# Messaging
debug () {
	[ -z "$DEBUG_BATS" ] || echo "	DEBUG: $@" >&3
}

debug_run () {
	debug "> lines=${lines[@]}"
	debug "> STATUS=$status"
}

fail_msg () {
	echo -e "FAIL: $@" >&3
}

fail () {
	fail_msg "$@"
	exit 1
}

error () {
	echo -e "ERROR: $@" >&3
	exit 2
}

# Assertion helpers

assert_equal () {
	if [ "$#" != 2 ]; then
		error "Got $# arguments to eq whenever expected 2"
	fi
	if [ "$1" != "$2" ]; then
		fail "Arguments are not equal.\n #1=<<$1>>\n #2=<<$2>>"
	fi
}

assert_python_re_match () {
	if ! python -c 'import re, sys; assert re.match(sys.argv[1], sys.argv[2], flags=re.DOTALL)' "$1" "$2"; then
		fail "<<$2>>\ndid not match\n<<$1>>"
	fi
}

assert_clean_exit () {
	assert_equal "$status" 0
}


# Misc helpers

pull_singularity_shim () {
	# make sure that we have our shim docker image so its pulling does not
	# leak into output of scripts/singularity_cmd
	if ! docker pull mjtravers/singularity-shim:latest; then
		skip "Failed to pull singularity shim"
	fi
}

skip_if_travis_osx() {
    if [ "$TRAVIS_OS_NAME" = osx ]
    then
        skip "$@"
    fi
}
