#!/usr/bin/env bats
#
# This test uses the Bash Automated Testing System
# See: https://github.com/bats-core/bats-core
#

load test_helpers

@test "verify that images are available either from web or our server" {
    unavail=$(git annex find --not --in web --and --not --in 71c620b5-997f-4849-bb30-c42dbb48a51e --and --not --metadata distribution-restrictions=no-longer)
	if [ -n "$unavail" ]; then
		fail "Following files are not available from the web or our datasets.datalad.org remote: $unavail"
	fi
}
