#!/bin/bash

set -eu

generate() {
	[ "$1" == singularity ] && add_entry=' "$@"' || add_entry=''
	ndversion=1.0.1
    # Thought to use conda-forge for this, but feedstock is not maintained:
    #  https://github.com/conda-forge/psychopy-feedstock/issues/64
    #   --miniconda version=py312_24.5.0-0 conda_install="conda-forge::psychopy conda-forge::qrcode" \
    # Had to go with 3.11 due to https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
    # Need extra -dev libraries etc to install/build wxpython
    # Gave up on native psychopy installation "myself" - decided to use the script!
    # sudo needed for the psychopy-installer script: https://github.com/wieluk/psychopy_linux_installer/issues/11
    # Surprise! cannot just ln -s python3 since then it would not have correct sys.path!
	docker run --rm repronim/neurodocker:$ndversion generate "$1" \
		--base-image=neurodebian:bookworm \
		--pkg-manager=apt \
		--install build-essential pkg-config git \
          sudo \
          libgtk-3-dev libwxgtk3.2-dev libwxgtk-media3.2-dev libwxgtk-webview3.2-dev libcanberra-gtk3-module \
          libusb-1.0-0-dev portaudio19-dev libasound2-dev \
          vim wget strace time ncdu gnupg curl procps pigz less tree python3 python3-pip \
        --run "git clone https://github.com/wieluk/psychopy_linux_installer/ /opt/psychopy-installer; cd /opt/psychopy-installer; git checkout 21b1ac36ee648e00cc3b68fd402c1e826270dad6" \
		--run "/opt/psychopy-installer/psychopy_linux_installer.sh --install_dir=/opt/psychopy --psychopy_version=2024.1.4 --bids_version=2023.2.0 --python_version=3.10.14 --wxpython_version=4.2.1 -v -f" \
        --run "/opt/psychopy/psychopy_*/bin/pip install qrcode" \
        --run "bash -c 'ln -s /opt/psychopy/psychopy_*/bin/psychopy /usr/local/bin/'" \
        --run "bash -c 'b=\$(ls /opt/psychopy/psychopy_*/bin/python3); echo -e \"#!/bin/sh\n\$b \\\"\\\$@\\\"\" >| /usr/local/bin/python3; chmod a+x /usr/local/bin/python3'" \
        --entrypoint python3
#       --user=reproin \
}

generate docker > Dockerfile
generate singularity > Singularity
