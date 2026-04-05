// @ts-check
/** @param {import('@actions/github-script').AsyncFunctionArguments & { pollInterval: number, timeout: number }} args */
export default async ({ github, context, core, pollInterval, timeout }) => {
  const owner = context.repo.owner;
  const repo = context.repo.repo;
  const sha = context.sha;
  const workflowName = 'Terraform CI';

  const { data: { workflow_runs: runs } } = await github.rest.actions.listWorkflowRunsForRepo({
    owner, repo, head_sha: sha, event: 'push',
  });
  const tfRun = runs.find(r => r.name === workflowName);

  if (!tfRun) {
    core.info('No Terraform CI run found for this commit — skipping wait.');
    return;
  }

  core.info(`Found Terraform CI run #${tfRun.run_number} (${tfRun.status})`);
  const start = Date.now();

  while (true) {
    const { data: run } = await github.rest.actions.getWorkflowRun({
      owner, repo, run_id: tfRun.id,
    });

    if (run.status === 'completed') {
      if (run.conclusion === 'success') {
        core.info('Terraform CI succeeded — proceeding with deploy.');
        return;
      }
      core.setFailed(`Terraform CI finished with conclusion: ${run.conclusion}`);
      return;
    }

    if (Date.now() - start > timeout) {
      core.setFailed('Timed out waiting for Terraform CI (10 min).');
      return;
    }

    core.info(`Terraform CI still ${run.status} — waiting ${pollInterval / 1000}s...`);
    await new Promise(r => setTimeout(r, pollInterval));
  }
};
