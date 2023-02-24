# ReproNim/containers - containerized environments for reproducible neuroimaging

[![Travis tests status](https://secure.travis-ci.org/ReproNim/containers.png?branch=master)](https://travis-ci.org/ReproNim/containers)
[![Additional tests](https://github.com/ReproNim/containers/workflows/Additional%20tests/badge.svg)](https://github.com/ReproNim/containers/actions?query=workflow%3A%22Additional+tests%22)

This repository provides a [DataLad] dataset (git/git-annex
repository) with a collection of popular computational tools provided
within ready to use containerized environments.  At the moment it
provides only [Singularity] images.  Versions of all images are tracked using
[git-annex] with content of the images provided from a dedicated
[Singularity Hub Collection] and http://datasets.datalad.org (AKA `///` of
DataLad) or other original collections.

The aims for this project is

- to be able to include this repository as a
  subdataset within larger study (super)datasets to facilitate rapid and
  reproducible computation, while
  adhering to [YODA principles] and retaining clear and unambiguous
  association between data, code, and computing environments using
  git/git-annex/DataLad;
- to assist with containers execution in "sanitized" environments:  no `$HOME` or
  system-wide `/tmp` is bind-mounted inside the containers, no
  environment variables from the host system made available inside;
- make Singularity images transparently usable on non-Linux (OSX) systems via
  [Docker].

![ReproNim/containers as a YODA building block](https://raw.githubusercontent.com/ReproNim/containers-artwork/master/repronim-containers-yoda_30dpi.png)

All images are "registered" within the dataset for execution using
[datalad containers-run], so it is trivial to list available
containers:

```shell
$> datalad containers-list
arg-test -> scripts/tests/arg-test.simg
bids-aa -> images/bids/bids-aa--0.2.0.sing
bids-afni-proc -> images/bids/bids-afni-proc--0.0.2.sing
bids-antscorticalthickness -> images/bids/bids-antscorticalthickness--2.2.0-1.sing
bids-baracus -> images/bids/bids-baracus--1.1.2.sing
bids-brainiak-srm -> images/bids/bids-brainiak-srm--latest.sing
...  many more to list them all ...
```

and execute either via `datalad containers-run` (which would also take care
about getting them first if not present):

```shell
$> datalad containers-run -n bids-validator -- --help
[INFO   ] Making sure inputs are available (this may take some time)
[INFO   ] == Command start (output follows) =====
Usage: bids-validator <dataset_directory> [options]

Options:
  --help, -h            Show help                                      [boolean]
  --version, -v         Show version number                            [boolean]
  --ignoreWarnings      Disregard non-critical issues                  [boolean]
  --ignoreNiftiHeaders  Disregard NIfTI header content during validation
                                                                       [boolean]
  --verbose             Log more extensive information about issues    [boolean]
  --json                Output results as JSON                         [boolean]
  --config, -c          Optional configuration file. See
                        https://github.com/bids-standard/bids-validator for more
                        info

This tool checks if a dataset in a given directory is compatible with the Brain
Imaging Data Structure specification. To learn more about Brain Imaging Data
Structure visit http://bids.neuroimaging.io
[INFO   ] == Command exit (modification check follows) =====
action summary:
  get (notneeded: 1)
  save (notneeded: 1)
```

or first getting them using [datalad get] and then either using
`singularity` `run` or `exec` directly, or (recommended) via
[scripts/singularity_cmd](). That is the helper which is used by
`containers-run` (see [.datalad/config]()).

## [scripts/singularity_cmd]()

Singularity execution by default is optimized for convenience and not for reproducibility.
This helper script assists in making singularity execution reproducible by

- disabling passing environment variables inside your containerized environment
- creating temporary `/tmp` directory for the environment, so there is no
  interaction with file paths outside of the current directory (which should
  ideally be a DataLad dataset)
- using custom and nearly empty [binds/HOME]() HOME directory, so there is
  no possible leakage of locally user-level installed Python and other modules
  to affect your computation

The [binds/HOME]() also provides a custom minimalistic [.bashrc](binds/HOME/.bashrc) file
with e.g. a customized prompt to inform you about which image you are in ATM for use
in interactive sessions:

    $> scripts/singularity_cmd exec images/repronim/repronim-reproin--0.5.4.sing bash
    singularity:repronim-reproin--0.5.4 > yoh@hopa:/home/yoh/proj/repronim/containers$ heudiconv --version
    0.5.4

### Singularity via Docker

On non-Linux systems, or if `REPRONIM_USE_DOCKER` environment variable is set to a non-empty value,
[scripts/singularity_cmd]() will use [Docker] shim image (in privileged mode) to run
singularity within it.  All necessary paths will be bind mounted as with a regular direct execution using
singularity.

### Interactive sessions

See [WiP PR #9](https://github.com/ReproNim/containers/pull/9) to
establish "reproducible interactive sessions" with the help of that script.

# Conventions

## Container image files

Singularity image files have `.sing` extension.  Since we are providing
a custom filename to store the file at, we cannot guess the format of
the container (e.g., either it is
[.sif](https://www.sylabs.io/2018/03/sif-containing-your-containers/)),
so we just use uniform `.sing` extension.

# A typical YODA workflow

Lets summarize YODA principles as a possible workflow:

- create a new dataset which would contain results and everything needed
    to obtain them
- install/add subdatasets(code, other datasets, containers)
- perform the analysis using **only** materials available within the reach of this dataset.


Let's assume that our goal is to do Quality Control of an MRI dataset
(which is available as DataLad dataset ds000003). We will create a new
dataset with the output of the QC results (as analyzed by mriqc
BIDS-App). mriqc is provided by the ReproNim/containers dataset of
containers. Below, we execute a simple analysis workflow which
adheres to YODA principles and we **end up with a dataset that contains
all components necessary a history of how it was achieved.**

This would help to guarantee reproducibility in the future because all the
materials would be *reachable* within that dataset.


## Runnable script

For advanced users who are comfortable with DataLad, the following
script may give you everything you need.

<details>
<summary>The version of the script with all commands explained</summary>

```shell
#!/bin/sh
(  # so it could be just copy pasted or used as a script
PS4='> '; set -xeu  # to see what we are doing and exit upon error
# Work in some temporary directory
cd $(mktemp -d ${TMPDIR:-/tmp}/repro-XXXXXXX)
# Create a dataset to contain mriqc output
datalad create -d ds000003-qc -c text2git
cd ds000003-qc
# Install our containers collection:
datalad install -d . ///repronim/containers
# (optionally) Freeze container of interest to the specific version desired
# to facilitate reproducibility of some older results
datalad run -m "Downgrade/Freeze mriqc container version" \
    containers/scripts/freeze_versions bids-mriqc=0.16.0
# Install input data:
datalad install -d . -s https://github.com/ReproNim/ds000003-demo sourcedata
# Setup git to ignore workdir to be used by pipelines
echo "workdir/" > .gitignore && datalad save -m "Ignore workdir" .gitignore
# Execute desired preprocessing while creating a provenance record
# in git history
datalad containers-run \
        -n containers/bids-mriqc \
        --input sourcedata \
        --output . \
        '{inputs}' '{outputs}' participant group -w workdir
)

```
</details>

## Walkthrough

For users who are new to these components, we will walk through how
these components are used together in a typical YODA workflow.
the steps

```bash
mkdir ~/my-experiments
cd ~/my-experiments
datalad create -d ds000003-qc -c text2git
cd ds000003-qc
```

Datalad has created a new directory for our results, `ds000003-qc`.
According to YODA principles, this dataset should also contain our input
data, code, and anything else we need to run the analysis.

Install the input dataset:

```bash
datalad install -d . -s https://github.com/ReproNim/ds000003-demo sourcedata
```

Next we install the `ReproNim/containers` collection.

```bash
datalad install -d . ///repronim/containers
```

Now let's take a look at what we have.

```bash
/ds000003-qc # The root dataset contains everything
 |--/sourcedata # we call it source, but it is actually ds000003-demo
 |--/containers # repronim/containers, this is where our non-custom code lives
```

`freeze_versions` is an optional step that will record and "freeze" the
version of the container used. Even if the `///containers` dataset is
upgraded with a newer version of our container, we are "pinned" to the
container we explicitly determined. Note: To switch version of the container
(e.g., to upgrade to a new one), rerun `freeze_versions` script with the version
specified.

Note: `freeze_versions` adds a change to the `///repronim/containers`
dataset.  Therefore, it is important to ensure that your clone of
`///repronim/containers` is publicly available. Reproducers will use
this clone and inherit your changes to `.datalad/config`, including the
frozen versions.


```bash
datalad run -m "Downgrade/Freeze mriqc container version" \
    containers/scripts/freeze_versions bids-mriqc=0.16.0
```

When we run the bids-mriqc container, it will need a working directory
for intermediate files. These are not helpful to commit, so we will
tell `git` (and `datalad`) to ignore the whole directory.

```bash
echo "workdir/" > .gitignore && datalad save -m "Ignore workdir" .gitignore
```

Now we use `datalad containers-run` to perform the analysis.

**_NOTE:_** mriqc is memory intensive, so we are restricting to a single
participant. OOM (Out of Memory) situations cause a `NodeExecutionError`
with an `Error 137`.

```bash
datalad containers-run \
        --container-name containers/bids-mriqc \
        --input sourcedata \
        --output . \
        '{inputs}' '{outputs}' participant --participant-label sub-02 -w workdir
```

If everything worked as expected, we will now see our new analysis, and
a commit message of how it was obtained! All of this is contained within
a single (nested) dataset with a complete record of how all the data was
obtained.

```shell
(git) .../ds000003-qc[master] $ git show --quiet
commit 5f0fbcbfe84bb8aa32c4400a0838bc41ff1c88e0 (HEAD -> master)
Author: Yaroslav Halchenko <debian@onerussian.com>
Date:   Sat Aug 31 05:29:31 2019 -0400

[DATALAD RUNCMD] containers/scripts/singularity_cmd run c...

=== Do not change lines below ===
{
 "chain": [],
 "cmd": "containers/scripts/singularity_cmd run containers/images/bids/bids-mriqc--0.15.1.sing '{inputs}' '{outputs}' participant group",
 "dsid": "f367440c-cbcf-11e9-9ad2-002590f97d84",
 "exit": 0,
 "extra_inputs": [
  "containers/images/bids/bids-mriqc--0.15.1.sing"
 ],
 "inputs": [
  "sourcedata"
 ],
 "outputs": [
  "."
 ],
 "pwd": "."
}
^^^ Do not change lines above ^^^
```

This record could later be reused (by anyone) using [datalad rerun] to rerun
this computation using exactly the same version(s) of input data and the
singularity container. You can even now [datalad uninstall] sourcedata and even containers
sub-datasets to save space - they will be retrievable at those exact versions later
on if you need to extend or redo your analysis.

#### Notes:

- aforementioned example requires DataLad >= 0.11.5 and datalad-containers >= 0.4.0;
- for more eleborate example with use of [reproman] to parallelize execution on
  remote resources, see [ReproNim/reproman PR#438](https://github.com/ReproNim/reproman/pull/438);
- a copy of the dataset is made available from [`///repronim/ds000003-qc`](http://datasets.datalad.org/?dir=/repronim/ds000003-qc)
  and [https://github.com/ReproNim/ds000003-qc]().


# Installation

It is a DataLad dataset, so you can either just [git clone] or [datalad install] it.
You will need to have [git-annex] available to retrieve any images. And you will
need DataLad and [datalad-container] extension installed for [datalad containers-run].
Since Singularity is Linux-only application, it will be "functional" only on
Linux. On OSX (and possibly Windows), if you have Docker installed, singularity
images will be executed through the provided docker shim image.

## Environment variables

A few environment variables (in addition to those consulted by datalad
and datalad-container) are considered in the scripts of this
repository:

### `SINGULARITY_CMD`

The default command (as "hardcoded" in [.datalad/config]()) is `run`
so running the container executes its default "entry point".  Setting
`SINGULARITY_CMD=exec` makes it possible to run an alternative command
in them (e.g. `bash` for interactive sessions)::

    SINGULARITY_CMD=exec datalad containers-run --explicit -n repronim-reproin bash

and then have `datalad` record any of the introduced changes.  Such
runs will not be reproducible but at least clearly annotated in what
environment corresponding actions were taken.

# Acknowledgements

## Grants

Development of this project and [datalad-container] extension was supported by the ReproNim project
([NIH 1P41EB019936-01A1](https://projectreporter.nih.gov/project_info_description.cfm?projectnumber=1P41EB019936-01A1)).
DataLad development was supported by a US-German collaboration in computational neuroscience (CRCNS) "DataGit: converging catalogues, warehouses, and deployment logistics into a federated 'data distribution'" (Halchenko/Hanke), co-funded by the US National Science Foundation ([NSF 1429999](https://www.nsf.gov/awardsearch/showAward?AWD_ID=1429999)) and the German Federal Ministry of Education and Research (BMBF 01GQ1411). Additional support is provided by the German federal state of Saxony-Anhalt and the European Regional Development Fund, Project: Center for Behavioral Brain Sciences, Imaging Platform.

## Copyrighted works

All container images are collections of various projects governed by the
corresponding copyrights/licenses.  Some are not completely FOSS and might
require additional license(s) to be obtained and provided (e.g. FreeSurfer
license for `fmriprep`).

### `artwork/repronim-containers-yoda_*`

Based on the artwork Copyright 2018-2019 Michael Hanke, from
[myyoda/poster](https://github.com/myyoda/poster), distributed under [CC BY](https://creativecommons.org/licenses/by/4.0/).

[git-annex]: http://git-annex.branchable.com
[DataLad]: http://datalad.org
[datalad-container]: http://docs.datalad.org/projects/container
[datalad containers-run]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-containers-run.html
[datalad get]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-get.html
[datalad run]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-run.html
[datalad rerun]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-rerun.html
[datalad install]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-install.html
[datalad uninstall]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-uninstall.html

[git clone]: https://git-scm.com/docs/git-clone

[Docker]: http://docker.com
[reproman]: http://reproman.repronim.org

[YODA principles]: https://github.com/myyoda/poster/blob/master/ohbm2018.pdf

[Singularity]: https://www.sylabs.io/singularity/
[Singularity Hub]: https://singularity-hub.org
[Singularity Hub Collection]: https://www.singularity-hub.org/collections/2761
