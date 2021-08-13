#!/bin/bash

set -eu

export PS4=+

datalad wtf -S datalad -S dependencies -S extensions

$(dirname $0)/create_singularities
