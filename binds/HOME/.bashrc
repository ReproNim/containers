if [ ! -z "$PS1" ]; then
    # include a marker into PS1 that we are in the singularity image
    # Since we are using git-annex for images, SINGULARITY_NAME would
    # carry the dereferenced filename - git-annex key which is not
    # that useful to see, so we just add [SING] marker
    if ! echo "$PS1" | grep -q SINGULARITY_NAME && [ ! -z "$SINGULARITY_NAME" ]; then
        # proposed in https://github.com/datalad/datalad-container/pull/84
        if [ ! -z "${DATALAD_CONTAINER_NAME:-}" ]; then
            _name="$DATALAD_CONTAINER_NAME"
        elif echo "$SINGULARITY_NAME" | grep -q '^MD5E-'; then
            # singularity < 3. dereferences symlinks -
            # annexed keys are too long/useless in this context, we shorten
            _name=$(echo ${SINGULARITY_NAME##*--} | cut -c 1-8)...
        else
            _name="$SINGULARITY_NAME"
        fi
        # strip our possible suffix
        _name="$(echo $_name | sed -e 's,.sing$,,g')"
        export PS1="singularity:$_name > $PS1"
    fi
fi

# USER variable might not be defined in sanitized environment
# but could be needed by some tools, e.g. FSL. See
# https://github.com/kaczmarj/neurodocker/pull/270
export USER="${USER:=`whoami`}"

# Bash history, although precious, could be a factor which is not
# common, so we might want to disable storing it altogether
#
# export HISTFILESIZE=0
#
# But for now keep it just ignored in .gitignore
