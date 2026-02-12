Plan to refactor codebase on how we approach creation of singularity/apptainer containers.

We want to not create them directly from docker images, but rather first rely
on functionality in https://github.com/datalad/datalad-container/pull/277
(skopeo branch of the https://github.com/yarikoptic/datalad-container/ fork) to
initiate OCI container locally using `datalad containers-add oci:docker://...`
under `images-oci/` subdataset, under similar path (e.g.
repronim/repronim-reproin--0.13.1.oci for
images/repronim/repronim-reproin--0.13.1.sing in this one), registering it to
be ran with `{img_dspath}/scripts/oci_cmd run` which we are to provide as well.
E.g.
    datalad containers-add --url oci:docker://bids/aa:v0.2.0 -i bids/bids-aa--0.2.0.oci bids-aa

under images-oci// subdataset.

While generating such OCI image we need to ensure that either all produced
files are under annex with URL or directly in git (if text files), e.g.

   git annex find --not --in datalad --and --not --in web bids/bids-aa--0.2.0.oci

(could be under web directly or via datalad downloader!)

`scripts/oci_cmd` could be simple for now:

    #!/bin/bash

    apptainer "$@"

Then, after generation of OCI image, we would need to produce singularity SIF file using
(assuming that {image} would be the replacement with portion of path to image file like repronim/repronim-reproin--0.13.1)

    datalad run -m "Build SIF image for {image}.sif" --output images/{image}.sif scripts/oci_cmd build images/{image}.sif images-oci/{image}.oci/


After all that done and works, we would need to have a migration
functionality which would produce .sif to replace all images for which we had Singularity* files but without custom commands, rather just basic wrappers.  Full list could be obtained using

    git grep -l 'Automagically prepared' images

and files would look like

    ❯ head images/bids/Singularity.bids-aa--0.2.0
    #
    # Automagically prepared for ReproNim/containers distribution.
    # See http://github.com/ReproNim/containers for more info
    #
    Bootstrap: docker
    From: bids/aa:v0.2.0

so the goal would be to produce OCI image taking that "From:" as pointing to docker hub, in the above example (ran under images-oci/ subdataset). So the command to "containers-add" would be similar to above example:

    datalad containers-add --url oci:docker://bids/aa:v0.2.0 -i bids/bids-aa--0.2.0.oci bids-aa

and then verifying that all annex files are available from URLs:

   git annex find --not --in datalad --and --not --in web bids/bids-aa--0.2.0.oci

should come out empty. (so we need a generic helper function to be used here to reuse)

Original images, and corresponding recipes, like in this case
images/bids/Singularity.bids-aa--0.2.0 where "From:" was found, and the corresponding image images/bids/bids-aa--0.2.0.sing should be "git rm"ed and committed with an informative message. Path to the image within .datalad.config should be replaced to point to .sif instead of original .sing version.

While developing, try migration first on some simpler cases like

  images/bids/bids-validator--1.2.3.sing
  images/bids/bids-rshrf--1.0.0.sing

For migration, add an option to skip failing, and we would need some log file listing those which failed to convert.
