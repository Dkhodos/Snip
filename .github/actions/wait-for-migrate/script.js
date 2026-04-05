// @ts-check
/** @param {import('@actions/github-script').AsyncFunctionArguments & { pollInterval: number, timeout: number }} args */
export default async ({ github, context, core, pollInterval, timeout }) => {
  const owner = context.repo.owner;
  const repo = context.repo.repo;
  const sha = context.sha;
  const workflowName = 'Migrate';

  const { data: { workflow_runs: runs } } = await github.rest.actions.listWorkflowRunsForRepo({
    owner, repo, head_sha: sha, event: 'push',
  });
  const migrateRun = runs.find(r => r.name === workflowName);

  if (!migrateRun) {
    core.info('No Migrate run found for this commit — skipping wait.');
    return;
  }

  core.info(`Found Migrate run #${migrateRun.run_number} (${migrateRun.status})`);
  const start = Date.now();

  while (true) {
    const { data: run } = await github.rest.actions.getWorkflowRun({
      owner, repo, run_id: migrateRun.id,
    });

    if (run.status === 'completed') {
      if (run.conclusion === 'success') {
        core.info('Migrate succeeded — proceeding with deploy.');
        return;
      }
      core.setFailed(`Migrate finished with conclusion: ${run.conclusion}`);
      return;
    }

    if (Date.now() - start > timeout) {
      core.setFailed('Timed out waiting for Migrate (10 min).');
      return;
    }

    core.info(`Migrate still ${run.status} — waiting ${pollInterval / 1000}s...`);
    await new Promise(r => setTimeout(r, pollInterval));
  }
};
