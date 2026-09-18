# Changelog

## 1.20260903.0 (2026-09-03)

751 commits since 0.20250527.0.

**POTENTIALLY BREAKING**: Newly built Singularity images now use the `.sif`
extension instead of `.sing`. Workflows that hard-code `.sing` paths will need
updating. Legacy containers without runscripts have been rebuilt as `.sif`.
The MAJOR version was bumped to 1 to signal this change.

### New and updated containers

- ~345 new NeuroDesk images added and registered
- ~156 new BIDS-Apps and ReproNim container images, including new versions
  of fmriprep (25.x), xcp-d (26.x), aslprep (26.x), qsiprep (26.x),
  smriprep (0.17–0.20), qsirecon (26.x), nibabies (25.x), mriqc (24.x),
  hippunfold (1.5.x), heudiconv (1.4–1.5), bids-validator (2.x–3.x),
  reprostim (0.7.x), petprep (0.0.x), simbids (0.0.x), cvrmap (4.x), rshrf
  (1.7.x), fmripost-aroma (0.0.x), fmripost-phase/rapidtide (main)

### Infrastructure / scripts

- `create_singularities` now uses PEP 723 inline script metadata so it can
  run directly via `uv run` without a separate install step; added `uv` and
  `git-annex` to declared dependencies
- Added retry logic for `singularity pull` failures (#158)
- Scripts refactored to use `singularity pull` instead of `singularity build`
- NeuroDesk URL base switched from CloudFront to `workers.dev`; arm64
  NeuroDesk images tracked in the registry without DataLad registration
- Improved error messages when parsing NeuroDesk image list entries; added
  deduplication of `(name, version)` entries to prevent URL flip-flopping
- Added `--pdb` CLI option for post-mortem debugging on exceptions
- git-annex branch commits now labelled via `annex.commitmessage`
- Fixed typing CI: bumped runner Python 3.8 → 3.13, pinned mypy target to 3.10
- bids-validator: workaround for deno runtime location change
- qsiprep: ignore keras config to avoid crashes (#157)

---

## 0.20250527.0 (2025-05-27)

- Added many new versions of BIDS-Apps and NeuroDesk images
- `scripts/freeze_versions` was rewritten in Python
- `scripts/*` received many tune-ups to robustify operation and add additional
  testing

---

## 0.20240201.0 (2024-02-01)

- Added NeuroDesk images
- Added many new versions of BIDS-Apps
- `scripts/freeze_versions` was rewritten in Python
- `scripts/singularity_exec` got better handling to pass git config variables
  inside, and added passing `annex.pidlock` and `git safe.directory`

---

## 0.20230525.0 (2023-05-25)

Current state was 0.3-716-g417bbbe — a large number of changes since 0.3 (2020).

- Switched to date-based release scheme (MAJOR=0, MINOR=YYYYMMDD)
- `scripts/create_singularities` was rewritten in Python and placed on a
  cron job
- Added NeuroDesk Singularity containers (not mirrored from
  datasets.datalad.org)
- Over 250 new containers added overall
- All scripts and documentation are codespelled
- `scripts/freeze_versions` can now freeze into a super-dataset to avoid
  modifying the original ReproNim/containers dataset
- Replaced `shub://` URLs with explicit direct URLs to `datasets.datalad.org`,
  removing the dependency on the DataLad git-annex special remote

---

## 0.3 (2020-01-22)

- Large number of new containers or new versions added
- `singularity_cmd` enhanced with ability to fall back to Docker when
  Singularity is unavailable
- `create_singularities` updated to account for changes in Singularity Hub API
  and behavior
- `freeze_versions` helper created to assist with freezing container versions
  for `datalad-container` use

---

## 0.2 (2019-05-20)

- Extended README.md with examples
- New container: `simple_workflow`

---

## 0.1 (2019-05-15)

Initial collection of containers.
