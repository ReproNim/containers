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

- retaining clear and unambigous association between data, code, and
  computing environments using git/git-annex/DataLad;
- executing in "sanitized" containerized environments:  no `$HOME` or
  system-wide `/tmp` is bind-mounted inside the containers, no
  environment variables from the host system made available inside.

All images are "registered" within the dataset for execution using
[datalad containers-run], so it is trivial to list available
containers:

    TODO

and execute

    TODO


# A typical workflow


    TODO
	datalad create study
	cd study
	# Install containers collection:
	datalad install -d . http://github.com/ReproNim/containers
	# Populate with input data:
	datalad install -d . -s ///labs/haxby/raiders data/bids
	# Create a new output dataset
	datalad create -d . data/fmriprep
	#
	# Execute desired preprocessing while creating a provenance record
	# in git history
	datalad containers-run containers/bids-fmriprep \
		--input	data/bids \
		--output data/fmriprep \
		data/bids {outputs} participant



[git-annex]: http://git-annex.branchable.com
[DataLad]: http://datalad.org
[datalad containers-run]: http://docs.datalad.org/projects/container/en/latest/generated/man/datalad-containers-run.html
[Singularity Hub]: https://singularity-hub.org
[Singularity Hub Collection]: https://www.singularity-hub.org/collections/2761
