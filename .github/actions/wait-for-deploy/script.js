// @ts-check
/** @param {import('@actions/github-script').AsyncFunctionArguments & { pollInterval: number, timeout: number, onFailure: string }} args */
export default async ({ github, context, core, pollInterval, timeout, onFailure = 'skip' }) => {
  /** @param {string} message */
  const handleFailure = (message) => {
    if (onFailure === 'fail') {
      core.setFailed(message);
    } else {
      core.warning(`${message} (skipping — set on-failure: fail to block)`);
    }
  };
  const deployWorkflows = [
    'Dashboard Frontend CI',
    'Dashboard Backend CI',
    'Redirect Service CI',
    'Click Worker CI',
  ];

  const owner = context.repo.owner;
  const repo = context.repo.repo;

  // For workflow_run events the relevant SHA is on the triggering run, not context.sha
  const sha = context.payload.workflow_run?.head_sha ?? context.sha;

  const { data: { workflow_runs: runs } } = await github.rest.actions.listWorkflowRunsForRepo({
    owner, repo, head_sha: sha, event: 'push',
  });

  const deployRuns = runs.filter(r => deployWorkflows.includes(r.name));

  if (deployRuns.length === 0) {
    core.info('No deploy workflow runs found for this commit — skipping wait.');
    return;
  }

  core.info(`Found ${deployRuns.length} deploy run(s): ${deployRuns.map(r => r.name).join(', ')}`);

  const start = Date.now();
  const pending = new Set(deployRuns.map(r => r.id));

  while (pending.size > 0) {
    if (Date.now() - start > timeout) {
      handleFailure(`Timed out waiting for deploy workflows (${timeout / 1000}s).`);
      return;
    }

    for (const runId of [...pending]) {
      const { data: run } = await github.rest.actions.getWorkflowRun({
        owner, repo, run_id: runId,
      });

      if (run.status === 'completed') {
        pending.delete(runId);
        if (run.conclusion !== 'success') {
          handleFailure(`${run.name} finished with conclusion: ${run.conclusion}`);
          return;
        }
        core.info(`${run.name} succeeded.`);
      } else {
        core.info(`${run.name} still ${run.status} — waiting ${pollInterval / 1000}s...`);
      }
    }

    if (pending.size > 0) {
      await new Promise(r => setTimeout(r, pollInterval));
    }
  }

  core.info('All deploy workflows succeeded — proceeding.');
};
