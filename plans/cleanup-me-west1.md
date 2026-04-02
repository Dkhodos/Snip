# Cleanup: me-west1 leftover resources

## Background
Region migration from `me-west1` to `europe-west1` completed on 2026-04-02.
A GCP-managed serverless address is blocking subnet deletion.

## Resources to delete

1. **Serverless address** (will auto-release eventually):
   ```bash
   gcloud compute addresses delete serverless-ipv4-1775156314960152753 --region=me-west1 --project=snip-491719
   ```

2. **Subnet** (blocked by the address above):
   ```bash
   gcloud compute networks subnets delete snip-subnet-pre-prod --region=me-west1 --project=snip-491719
   ```

## Status
- [ ] Serverless address released by GCP
- [ ] Subnet deleted
