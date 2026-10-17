# Roadmap: unattended updates

## Current state (option C, in use)

`update.sh` runs on the owner's PC through the Windows task `SepitaDatasetUpdate` (daily 20:00).
It downloads the SEPA dump, builds the CSVs, publishes the `datos` release and reloads Supabase.
It only runs while the PC is on (`StartWhenAvailable` catches up missed runs).

## Why it cannot run in the cloud as-is (verified 2026-10-17)

- `datos.produccion.gob.ar` answers **403** to GitHub-hosted runners (API, dataset page and zip).
- The daily dump is **324 MB** (~92 s to download) and takes ~6 min of CPU to process.
  It is a zip of zips, so it cannot be streamed. Supabase Edge Functions (memory and
  wall-time limits) cannot do it. Their limits come from Supabase docs, not re-verified.

## Planned: option B, always-on VM

Run `update.sh` on a free always-on VM (e.g. Oracle Cloud Free Tier, Ubuntu).

1. **Gate: test the IP first.** From the VM: `curl -sI https://datos.produccion.gob.ar/api/3/action/package_show?id=sepa-precios`.
   Only continue on `HTTP/2 200`. A datacenter IP may be blocked just like GitHub's.
2. Install `python3`, `git`, `gh`, `postgresql-client`; `gh auth login`.
3. Clone the repo and create `.env` from `.env.example` (use the Supabase connection string).
4. Schedule with cron, e.g. `0 20 * * * /path/to/update.sh >> /path/to/update.log 2>&1`
   (mind the VM timezone: ART is UTC-3).
5. Disable the Windows task `SepitaDatasetUpdate` to avoid two writers.

If the VM IP is blocked: try another provider, or keep option C.

## Rejected for now

- **Supabase pulls the release CSVs (pg_cron + Edge Function):** only moves the 7 MB load; the
  heavy build would still run on the PC.
