# Contributing to ReproNim/containers

## Adding a container

Images are not added by hand. `scripts/create_singularities` pulls them, saves them, and registers them with datalad-container; your job is to teach that script about the image, then run it.

### 1. Teach the script about the image

Most images come from a group in `scripts/create_singularities`: `bids-apps`, `neurodesk`, `repronim`, `brainiak`, `neuronets`, `poldrack`.

`bids-apps` is discovered automatically — the script scrapes the `dh:` entries of [bids-website's `apps.yml`](https://github.com/bids-standard/bids-website/blob/main/data/tools/apps.yml), so a BIDS App listed there needs no change here at all. Everything else is an explicit call in `main()`:

```python
if should_build('repronim', 'repronim/reprostim'):
    builder.generate_singularity_for_docker_image("repronim/reprostim")
```

The first argument to `should_build` is the group; the second lets `--image-groups` select this image on its own. `generate_singularity_for_docker_image` takes the Docker Hub id and:

- `family=` — the collection the image is filed under, i.e. the `images/<family>/` subdirectory and the `<family>-<name>` registration. **It defaults to the Docker Hub namespace**, which is usually not what you want: `pennlinc/simbids` without `family="bids"` would land in `images/pennlinc/` as `pennlinc-simbids`.
- `version_regex=` — restrict which tags are considered, e.g. pinning an LTS line.
- `familysuf=` — a suffix for the registered name, e.g. `20-2` for a maintained older series.

Versions are not pinned. The script queries Docker Hub, discards tags ending in a prerelease marker (`…a1`, `…b2`, `…rc1`) or containing `master`, keeps those beginning with a version number — optionally prefixed `v`, `version-`, or `release-` — and takes the highest. The prefix is stripped for the filename, so `docker://bids/rshrf:v1.7.0` becomes `bids-rshrf--1.7.0`. A new upstream release is picked up by the next run.

### 2. Run it

```
scripts/create_singularities -i <group-or-image>
```

Without arguments it considers everything, which is what the cron job does. `--push` runs `git pull` and then `datalad push --data=auto` to share the result. Add `--no-singularity-check` to skip the "singularity is too old" guard.

`-i` selects a group, or an individual image that has its own explicit call. It cannot select one of the auto-discovered `bids-apps`, since those are reached only by building the whole group. To narrow to one of those, name it positionally instead — that filter applies to every image the run considers:

```
scripts/create_singularities nipreps/fmriprep
```

A successful add produces **two commits**:

```
Adding image for bids-cvrmap--4.3.1 from docker://arovai/cvrmap:4.3.1
[DATALAD] Configure containerized environment 'bids-cvrmap'
```

The first saves `images/<family>/<family>-<name>--<version>.sif`. The second is `datalad containers-add` recording the image in `.datalad/config` — a new `[datalad "containers.<family>-<name>"]` stanza for a new container, or an updated `image =` line for a new version of an existing one.

Underscores in the name become dashes, since datalad does not allow `_` in container names: `pennlinc/xcp_d` is registered as `bids-xcp-d`.

NeuroDesk images take a different path: they are downloaded from published URLs and registered with `git annex registerurl`, they use the `.simg` extension, and only the newest version of each is registered as a container.

### 3. Verify

```
datalad containers-list
datalad containers-run -n <family>-<name> -- --help
```

The second matters more than the first — a registered container that cannot execute is not done.

## Who can add an image

**Image commits cannot arrive by pull request.** `scripts/tests/test_repo_state.bats` fails if any annexed file is available neither from the web nor from our `datasets.datalad.org` remote. A `.sif` built on your own machine is in neither, so a PR carrying one fails CI no matter how correct it is.

So the work splits:

- **Anyone** can PR the `scripts/create_singularities` change that teaches the script about a new image, along with any doc updates.
- **A maintainer with push access to `datasets.datalad.org`** then runs the script, which produces the two commits above and pushes the image content.

If you are contributing a new container, open a PR with just the script change and say in the description that the image itself needs a maintainer run.

## Using a container you added

```
datalad containers-run -n <family>-<name> -- <args>
```

Downstream datasets that include this repository as a subdataset can freeze a container to a specific version with `scripts/freeze_versions`, so that upgrading the subdataset does not silently change which image a workflow runs:

```
scripts/freeze_versions bids-mriqc=0.15.0
```

See the README for the full workflow.
