# ReproNim/containers - containerized environments for reproducible neuroimaging

This repository provides a [DataLad] dataset (git/git-annex
repository) with a collection of popular computational tools provided
within ready to use containerized environments.  At the moment it
provides only [Singularity].  Versions of all images are tracked using
[git-annex] with content of the images provided from a dedicated
[Singularity Hub Collection].

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
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-mriqc--0.15.0.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-mrtrix3-connectome--0.4.1.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-broccoli--1.0.1.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-spm--0.0.15.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-cpac--1.1.0_14.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-aa--0.2.0.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-niak--latest.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-oppni--0.7.0-1.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-brainiak-srm--latest.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-tracula--6.0.0.beta-0.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-baracus--1.1.2.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-antscorticalthickness--2.2.0-1.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-dparsf--4.3.12.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-afni-proc--0.0.2.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-rshrf--1.0.0.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-example--0.0.7.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/bids/bids-magetbrain--0.3.sing (file)
    containers(ok): /home/yoh/proj/repronim/containers/images/repronim/repronim-reproin--0.5.4.sing (file)
    action summary:
      containers (ok: 21)


and execute

    

# Conventions

## Container image files

Singularity image files have `.sing` extension.  Since we are providing
a custom filename to store the file at, we cannot guess the format of
the container (e.g., either it is 
[.sif](https://www.sylabs.io/2018/03/sif-containing-your-containers/)),
so we just use uniform `.sing` extension.

# A typical workflow


    TODO
	datalad create study
	cd study
	# Install containers collection:
	datalad install -d . http://github.com/ReproNim/containers
	# Populate with input data:
	datalad install -d . -s ///labs/haxby/raiders data/bids
	# Create a new output dataset. TODO: --cfg fmriprep
	datalad create -d . data/fmriprep
	#
	# Execute desired preprocessing while creating a provenance record
	# in git history
	# TODO: WiP https://github.com/datalad/datalad-container/pull/76
	#       to be able to run that helper script we provide here
	# TODO: use of {inputs} is awaiting
	#       https://github.com/datalad/datalad-container/pull/60
	datalad containers-run \
		-n containers/bids-fmriprep \
		--input	data/bids \
		--output data/fmriprep \
		data/bids {outputs} participant


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
[YODA principles]: https://github.com/myyoda/poster/blob/master/ohbm2018.pdf

[Singularity]: https://www.sylabs.io/singularity/
[Singularity Hub]: https://singularity-hub.org
[Singularity Hub Collection]: https://www.singularity-hub.org/collections/2761
