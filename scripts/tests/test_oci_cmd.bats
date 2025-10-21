#!/usr/bin/env bats
#emacs: -*- mode: shell-script; c-basic-offset: 4; tab-width: 4; indent-tabs-mode: t -*-
#ex: set sts=4 ts=4 sw=4 noet:
#
# Tests for scripts/oci_cmd wrapper
#

load test_helpers

topdir="$BATS_TEST_DIRNAME/../.."

@test "oci_cmd exists and is executable" {
	[ -x "$topdir/scripts/oci_cmd" ]
}

@test "oci_cmd --version passes through to apptainer" {
	# This test verifies that oci_cmd correctly forwards arguments to apptainer
	cd "$topdir"

	# Check if apptainer is available
	if ! command -v apptainer >/dev/null 2>&1; then
		skip "apptainer not available"
	fi

	myrun scripts/oci_cmd --version

	# Should succeed and output should contain "apptainer"
	assert_clean_exit
	assert_python_re_match "apptainer" "${lines[*]}"
}

@test "oci_cmd help passes through to apptainer" {
	cd "$topdir"

	# Check if apptainer is available
	if ! command -v apptainer >/dev/null 2>&1; then
		skip "apptainer not available"
	fi

	myrun scripts/oci_cmd help

	# Should succeed and output should contain apptainer help text
	assert_clean_exit
	# Check for "apptainer" in output as help command shows apptainer commands
	assert_python_re_match ".*apptainer.*" "${lines[*]}"
}

@test "oci_cmd with no arguments shows apptainer usage" {
	cd "$topdir"

	# Check if apptainer is available
	if ! command -v apptainer >/dev/null 2>&1; then
		skip "apptainer not available"
	fi

	# apptainer with no arguments typically shows usage and exits with non-zero
	run "$topdir/scripts/oci_cmd"

	# Should show usage information
	assert_python_re_match "Usage:" "${lines[*]}"
}
