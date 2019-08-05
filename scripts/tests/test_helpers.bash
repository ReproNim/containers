# Messaging
debug () {
	[ -z "$DEBUG_BATS" ] || echo "  DEBUG: $@" >&3
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

assert_clean_exit () {
	assert_equal "$status" 0
}

