#!/bin/bash

set -eu

export PS4=+

datalad wtf -S datalad -S dependencies -S extensions

# verify that datalad-container is available in the environment
if ! datalad containers-run --help >/dev/null 2>&1; then
    echo "datalad-containers extension seems to be NA here"
    exit 1
fi

"$(dirname "$0")/create_singularities"
