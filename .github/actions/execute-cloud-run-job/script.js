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
  const logFilter = [
    `resource.type="cloud_run_job"`,
    `resource.labels.job_name="${job}"`,
    `labels."run.googleapis.com/execution_name"="${executionShort}"`,
    `logName:("stdout" OR "stderr" OR "varlog")`,
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
      `gcloud logging read '${logFilter}' --project="${projectId}" --limit=500 --freshness=15m --order=asc --format="value(timestamp, textPayload)"`,
    );
    const lines = logs ? logs.split('\n') : [];
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

  // ── Fetch final logs for summary ────────────────────────────────────
  const finalLogs = gcloudSafe(
    `gcloud logging read '${logFilter}' --project="${projectId}" --limit=500 --freshness=15m --order=asc --format="value(textPayload)"`,
  );

  // ── Write GitHub Step Summary ───────────────────────────────────────
  const statusIcon = result === 'success' ? '✅ Success' : result === 'failed' ? '❌ Failed' : '⏱️ Timed out';
  const commitShort = process.env.GITHUB_SHA?.slice(0, 7) ?? 'unknown';

  const summary = [
    `## ${summaryTitle}`,
    '',
    '| | |',
    '| --- | --- |',
    `| **Status** | ${statusIcon} |`,
    `| **Job** | \`${job}\` |`,
    `| **Execution** | \`${executionShort}\` |`,
    `| **Duration** | ${duration}s |`,
    `| **Commit** | \`${commitShort}\` |`,
    '',
    '<details>',
    '<summary>Logs</summary>',
    '',
    '```',
    finalLogs || '(no logs captured)',
    '```',
    '',
    '</details>',
    '',
  ].join('\n');

  const summaryFile = process.env.GITHUB_STEP_SUMMARY;
  if (summaryFile) {
    appendFileSync(summaryFile, summary);
  }

  if (result !== 'success') {
    core.setFailed(`Job ${result}: ${executionShort}`);
  }
};
