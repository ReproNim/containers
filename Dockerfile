FROM alpine:3.21.3
ENV PATH="/usr/local/apptainer/bin:$PATH" \
    APPTAINER_TMPDIR="/tmp-apptainer"
RUN apk add --no-cache apptainer py3-pytest ca-certificates libseccomp squashfs-tools tzdata fuse2fs fuse-overlayfs squashfuse \
    python3 py3-pip git openssh-client git-annex curl bzip2 bash glab jq\
    && mkdir -p $APPTAINER_TMPDIR \
    && cp /usr/share/zoneinfo/UTC /etc/localtime \
    && apk del tzdata \
    && rm -rf /tmp/* /var/cache/apk/*

RUN pip install --break-system-packages --no-cache-dir datalad datalad-container ssh_agent_setup python-gitlab

WORKDIR /work
