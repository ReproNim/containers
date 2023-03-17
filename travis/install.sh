#!/bin/bash

set -ev

git clone https://github.com/matthew-brett/multibuild ~/multibuild
# shellcheck disable=SC1090
source ~/multibuild/osx_utils.sh

if [ "$TRAVIS_OS_NAME" = linux ]
then
    # So we get all backports etc
    bash <(wget -q -O- http://neuro.debian.net/_files/neurodebian-travis.sh)
    sudo apt-get update -qq
    sudo apt-get install eatmydata  # to speedup some installations
    sudo eatmydata apt-get install singularity-container shellcheck bats git-annex-standalone
else
    # osx
    HOMEBREW_NO_AUTO_UPDATE=1 brew install shellcheck
    HOMEBREW_NO_AUTO_UPDATE=1 brew install git-annex
    git clone https://github.com/sstephenson/bats.git ~/bats
    ( cd ~/bats ; sudo ./install.sh /usr/local )
    sudo cp travis/dummy_docker /usr/local/bin/docker
fi

git fetch origin git-annex
git remote add --fetch datalad.datasets.org http://datasets.datalad.org/repronim/containers/.git
git annex upgrade  # we need v7 for the unlocked test img

exit 0
