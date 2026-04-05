// @ts-check
import { execSync } from 'node:child_process';

/** @param {{ core: import('@actions/core'), service: string, region: string, keep: number }} args */
export default async ({ core, service, region, keep }) => {
  let output;
  try {
    output = execSync(
      `gcloud run revisions list --service="${service}" --region="${region}" --sort-by="~creationTimestamp" --format="value(name)"`,
      { encoding: 'utf-8' },
    ).trim();
  } catch (error) {
    core.warning(`Failed to list revisions for ${service}: ${error}`);
    return;
  }

  if (!output) {
    core.info(`No revisions found for ${service}`);
    return;
  }

  const revisions = output.split('\n');
  const toDelete = revisions.slice(keep);

  if (toDelete.length === 0) {
    core.info(`${service}: ${revisions.length} revision(s), keeping ${keep} — nothing to prune`);
    return;
  }

  core.info(`${service}: pruning ${toDelete.length} old revision(s), keeping ${keep}`);

  for (const rev of toDelete) {
    try {
      execSync(`gcloud run revisions delete "${rev}" --region="${region}" --quiet`, {
        encoding: 'utf-8',
      });
      core.info(`  Deleted: ${rev}`);
    } catch (error) {
      core.warning(`  Failed to delete ${rev}: ${error}`);
    }
  }
};
