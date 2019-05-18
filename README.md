# ReproNim/containers - containerized environments for reproducible neuroimaging

This repository provides a [DataLad] dataset (git/git-annex
repository) with a collection of popular computational tools provided
within ready to use containerized environments.  At the moment it
provides only [Singularity] images.  Versions of all images are tracked using
[git-annex] with content of the images provided from a dedicated
[Singularity Hub Collection] or other original collections.

The main purpose is to be able to include this repository as a
subdataset within larger study (super)datasets to facilitate rapid and
reproducible computation, while

- adhering to [YODA principles] and retaining clear and unambiguous
  association between data, code, and computing environments using
  git/git-annex/DataLad;
- executing in "sanitized" containerized environments:  no `$HOME` or
  system-wide `/tmp` is bind-mounted inside the containers, no
  environment variables from the host system made available inside.

All images are "registered" within the dataset for execution using
[datalad containers-run], so it is trivial to list available
containers:

    $> datalad containers-list
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-validator--1.2.3.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-freesurfer--6.0.1-5.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-fmriprep--1.3.2.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-magetbrain--0.3.sing (file)
	...
    containers(ok): /home/yoh/proj/repronim/containers/images/repronim/repronim-reproin--0.5.4.sing (file)
    action summary:
      containers (ok: 21)


and execute either via `datalad containers-run` (which would also take care
about getting them first if not present):

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

See [WiP PR #9](https://github.com/ReproNim/containers/pull/9) to
establish "reproducible interactive sessions" with the help of that script.

# Conventions

## Container image files

Singularity image files have `.sing` extension.  Since we are providing
a custom filename to store the file at, we cannot guess the format of
the container (e.g., either it is 
[.sif](https://www.sylabs.io/2018/03/sif-containing-your-containers/)),
so we just use uniform `.sing` extension.

# A typical workflow

Here is an outline of a simple analysis workflow, where we will adhere to
[YODA] principles where each component should contain all necessary for its
"reproduction" history and components

	# Create fmriprep'ed dataset
	datalad create -d data/raiders-fmriprep
	cd data/raiders-fmriprep
	# Install our containers collection:
	datalad install -d . http://github.com/ReproNim/containers
	# Populate with input data:
	datalad install -d . -s ///labs/haxby/raiders sourcedata
	# Execute desired preprocessing while creating a provenance record
	# in git history
	datalad containers-run \
		-n containers/bids-fmriprep \
		--input	sourcedata \
		--output . \
		{inputs} {outputs} participant

and now you have a dataset which has a git record on how these data
was created, and could be redone later in time (by anyone) using [datalad rerun].
You can even now [datalad uninstall] sourcedata and even containers 
sub-datasets to save space - they will be retreavable at those exact versions later 
on if you need to extend or redo your analysis.  

Note: ATM aforementioned example awaits DataLad and datalad-containers releases to
function as expected.

	# TODO: WiP https://github.com/datalad/datalad-container/pull/76
	#       to be able to run that helper script we provide here
	# TODO: use of {inputs} is awaiting release of datalad and -containers
	#       https://github.com/datalad/datalad-container/pull/60
	
# Installation

It is a DataLad dataset, so you can either just [git clone] or [datalad install] it.
You will need to have [git annex] available to retrieve any images. And you will 
need DataLad and [datalad-container] extension installed for [datalad container-run].
Since Singularity is Linux-only application, it will be "functional" only on 
Linux. There is a [WiP #3](https://github.com/ReproNim/containers/issues/3) to 
establish seamless execution of those Singularity images on systems which 
supports [Docker].

## Environment variables

A few environment variables (in addition to those consulted by datalad
and datalad-container) are considered in the scripts of this
repository:

### `SINGULARITY_CMD`

The default command (as "hardcoded" in [.datalad/config][]) is `run`
so running the container executes its default "entry point".  Setting
`SINGULARITY_CMD=exec` makes it possible to run an alternative command
in them (e.g. `bash` for interactive sessions)::

    SINGULARITY_CMD=exec datalad containers-run --explicit -n repronim-reproin bash

and then have `datalad` record any of the introduced changes.  Such
runs will not be reproducible but at least clearly annotated in what
environment corresponding actions were taken.

[git-annex]: http://git-annex.branchable.com
[DataLad]: http://datalad.org
[datalad containers-run]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-containers-run.html
[datalad get]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-get.html
[datalad run]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-run.html
[datalad rerun]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-rerun.html
[datalad uninstall]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-uninstall.html

[YODA principles]: https://github.com/myyoda/poster/blob/master/ohbm2018.pdf

[Singularity]: https://www.sylabs.io/singularity/
[Singularity Hub]: https://singularity-hub.org
[Singularity Hub Collection]: https://www.singularity-hub.org/collections/2761
