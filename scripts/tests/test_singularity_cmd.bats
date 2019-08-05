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
#   bats test_singularity_cmd.bats
#   bats .

load test_helpers

arg_test_img="$BATS_TEST_DIRNAME/arg-test.simg"
topdir="$BATS_TEST_DIRNAME/../.."

cd "$BATS_TEST_DIRNAME"
git annex get "$arg_test_img"


@test "verifying arguments passed to singularity_cmd Docker shim" {
	pull_singularity_shim

	cd "$topdir"
    export REPRONIM_USE_DOCKER=1
    run scripts/singularity_cmd \
        exec "$arg_test_img" /singularity "foo bar" blah 45.5 /dir "bar;" "foo&" '${foo}'

    debug_run

    assert_clean_exit
    assert_equal "${lines[0]}"  'arg #1=<foo bar>'
    assert_equal "${lines[1]}"  'arg #2=<blah>'
    assert_equal "${lines[2]}"  'arg #3=<45.5>'
    assert_equal "${lines[3]}"  'arg #4=</dir>'
    assert_equal "${lines[4]}"  'arg #5=<bar;>'
    assert_equal "${lines[5]}"  'arg #6=<foo&>'
    assert_equal "${lines[6]}"  'arg #7=<${foo}>'
}

@test "verifying ability to singularity exec under /tmp/subdir" {
	subdir=/tmp/$(mktemp -t "s i.XXXXXX" -u | sed -e 's,.*/,,g')
	mkdir -p "$subdir"
	echo "content" > "$subdir/file"
	debug "subdir: $subdir"

	cd "$subdir"
	# Our arg_test image has no /etc/localtime so singularity might complain
	# about inability to bind mount that one
	#  \S* to swallow ANSI coloring
	target_out=( '(\S*WARNING:\S* skipping mount of /etc/localtime: no such file or directory\n)?/tmp'
"$subdir"
"$subdir/file"
/var/tmp
content )

	# export REPRONIM_USE_DOCKER=1
	if [ -n "${REPRONIM_USE_DOCKER:-}" ]; then
		pull_singularity_shim
	fi
	run "$topdir/scripts/singularity_cmd" exec "$arg_test_img" sh -c "find /tmp /var/tmp && cat \"$subdir/file\""

	debug_run

	assert_clean_exit
	assert_python_re_match "${target_out[*]}" "${lines[*]}"
	rm -rf "$subdir"  # cleanup
}
