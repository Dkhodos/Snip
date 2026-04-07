// @ts-check
import { execSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';

/**
 * @param {{ core: import('@actions/core'), job: string, region: string, projectId: string, timeout: number, pollInterval: number, summaryTitle: string }} args
 */
export default async ({ core, job, region, projectId, timeout, pollInterval, summaryTitle }) => {
  const sleep = (/** @type {number} */ ms) => new Promise(r => setTimeout(r, ms));

  /** @param {string} cmd */
  const gcloud = (cmd) => execSync(cmd, { encoding: 'utf-8' }).trim();

  /** @param {string} cmd */
  const gcloudSafe = (cmd) => {
    try {
      return gcloud(cmd);
    } catch {
      return '';
    }
  };

  // ── Launch job ──────────────────────────────────────────────────────
  gcloud(`gcloud run jobs execute "${job}" --region "${region}" --async`);

  const executionFull = gcloud(
    `gcloud run jobs executions list --job="${job}" --region="${region}" --limit=1 --sort-by="~createTime" --format="value(name)"`,
  );
  const executionShort = executionFull.split('/').pop();
  core.info(`▶ Execution started: ${executionShort}`);

  // ── Build log filter ────────────────────────────────────────────────
  const appLogFilter = [
    `resource.type="cloud_run_job"`,
    `resource.labels.job_name="${job}"`,
    `labels."run.googleapis.com/execution_name"="${executionShort}"`,
    `logName:("stdout" OR "stderr")`,
  ].join(' AND ');

  // ── Poll loop ───────────────────────────────────────────────────────
  let seenCount = 0;
  const start = Date.now();
  /** @type {'success' | 'failed' | 'timeout'} */
  let result;

  while (true) {
    const elapsed = (Date.now() - start) / 1000;
    if (elapsed > timeout) {
      core.error(`Timed out after ${timeout}s`);
      result = 'timeout';
      break;
    }

    // Stream new log lines
    const logs = gcloudSafe(
      `gcloud logging read '${appLogFilter}' --project="${projectId}" --limit=500 --freshness=15m --order=asc --format="value(timestamp, textPayload)"`,
    );
    const lines = logs ? logs.split('\n').filter(Boolean) : [];
    if (lines.length > seenCount) {
      for (const line of lines.slice(seenCount)) {
        core.info(line);
      }
      seenCount = lines.length;
    }

    // Check execution status
    const completed = gcloudSafe(
      `gcloud run jobs executions describe "${executionFull}" --region="${region}" --format="value(status.conditions.filter(type='Completed').map().extract(status).flatten())"`,
    );
    if (completed === 'True') {
      result = 'success';
      break;
    }

    const failed = gcloudSafe(
      `gcloud run jobs executions describe "${executionFull}" --region="${region}" --format="value(status.conditions.filter(type='Failed').map().extract(status).flatten())"`,
    );
    if (failed === 'True') {
      result = 'failed';
      break;
    }

    core.info(`⏳ Still running... (polling in ${pollInterval}s)`);
    await sleep(pollInterval * 1000);
  }

  const duration = Math.round((Date.now() - start) / 1000);

  // ── Fetch final application logs ────────────────────────────────────
  const finalLogs = gcloudSafe(
    `gcloud logging read '${appLogFilter}' --project="${projectId}" --limit=500 --freshness=15m --order=asc --format="value(textPayload)"`,
  );
  const logLines = finalLogs ? finalLogs.split('\n').filter(Boolean) : [];

  // ── Parse log content ───────────────────────────────────────────────
  const upgrades = logLines
    .filter(l => l.includes('Running upgrade'))
    .map(l => l.replace(/^.*Running upgrade\s*/, '').trim());

  const errors = logLines
    .filter(l => /\b(error|exception|traceback|fatal)\b/i.test(l));

  // ── Console URL ─────────────────────────────────────────────────────
  const consoleUrl = `https://console.cloud.google.com/run/jobs/executions/details/${region}/${executionShort}`;

  // ── Write GitHub Step Summary ───────────────────────────────────────
  const statusIcon = result === 'success' ? '✅ Success' : result === 'failed' ? '❌ Failed' : '⏱️ Timed out';
  const commitShort = process.env.GITHUB_SHA?.slice(0, 7) ?? 'unknown';

  const parts = [
    `## ${summaryTitle}`,
    '',
    '| | |',
    '| --- | --- |',
    `| **Status** | ${statusIcon} |`,
    `| **Job** | \`${job}\` |`,
    `| **Execution** | [\`${executionShort}\`](${consoleUrl}) |`,
    `| **Duration** | ${duration}s |`,
    `| **Commit** | \`${commitShort}\` |`,
  ];

  if (upgrades.length > 0) {
    parts.push(`| **Migrations** | ${upgrades.length} applied |`);
  } else if (result === 'success') {
    parts.push(`| **Migrations** | Already up to date |`);
  }

  parts.push('');

  // Migrations applied
  if (upgrades.length > 0) {
    parts.push('### Migrations Applied', '');
    for (const u of upgrades) {
      parts.push(`- \`${u}\``);
    }
    parts.push('');
  }

  // Errors (if any)
  if (errors.length > 0) {
    parts.push('### Errors', '', '```');
    for (const e of errors) {
      parts.push(e);
    }
    parts.push('```', '');
  }

  // Full logs in collapsible
  parts.push(
    '<details>',
    '<summary>Full Logs</summary>',
    '',
    '```',
    logLines.length > 0 ? logLines.join('\n') : '(no logs captured)',
    '```',
    '',
    '</details>',
    '',
  );

  const summaryFile = process.env.GITHUB_STEP_SUMMARY;
  if (summaryFile) {
    appendFileSync(summaryFile, parts.join('\n'));
  }

  if (result !== 'success') {
    core.setFailed(`Job ${result}: ${executionShort}`);
  }
};
