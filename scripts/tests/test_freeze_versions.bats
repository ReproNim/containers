#!/usr/bin/env bats
#
# This test uses the Bash Automated Testing System
# See: https://github.com/bats-core/bats-core
#
# Install instructions:
#   git clone https://github.com/bats-core/bats-core.git
#   cd bats-core
#   sudo ./install.sh /usr/local
#
# Several ways to run the test:
#   ./test_singularity_cmd.bats
#   bats test_freeze_versions.bats
#   bats .

load test_helpers

arg_test_img="$BATS_TEST_DIRNAME/arg-test.simg"
topdir="$BATS_TEST_DIRNAME/../.."
freeze_versions="$topdir/scripts/freeze_versions"

@test "fail to freeze nonexisting" {
	$freeze_versions neurodesk-romeo=0.999.9 && { echo "should have failed"; exit 1; } || :
}

@test "test freezing with extension" {
	$freeze_versions neurodesk-romeo=3.2.4.simg && git diff .datalad | grep "romeo--3.2.4.simg  # frozen" && git checkout .datalad
}

@test "partial specification" {
	# first I implemented that this would be possible and thought to promote it as a "feature"
	$freeze_versions neurodesk-slicer=4.11.2020 && { echo "should have failed"; git diff .datalad; git checkout .datalad; exit 1; } || :
	# we will have it available only when version to the . is specified, e.g. if someone wants to freeze to
	# specific major.minor so we will just automatically choose the one with some .PATCH if there is only 1
	$freeze_versions neurodesk-fmriprep=20.1 && git diff .datalad | grep "fmriprep--20.1.3.simg  # frozen" && git checkout .datalad

}
