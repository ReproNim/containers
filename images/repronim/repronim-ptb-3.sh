#!/bin/bash

# TODO: ideally we should figure it out
v=3.0.15.20190401.dfsg1-1~nd100
v=$(echo $v | tr '~' '+')

neurodocker generate singularity \
   --base neurodebian:buster-non-free \
   --ndfreeze date=20190915 \
   --pkg-manager apt \
   --install {octave,matlab}-psychtoolbox-3{,-nonfree} octave-{image,optim,signal,statistics} strace gdb valgrind \
   >| Singularity.repronim-ptb-3--"$v"
