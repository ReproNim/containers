if [ ! -z "$PS1" ]; then
    # include a marker into PS1 that we are in the singularity image
    # Since we are using git-annex for images, SINGULARITY_NAME would
    # carry the dereferenced filename - git-annex key which is not
    # that useful to see, so we just add [SING] marker
    if ! echo "$PS1" | grep -q SINGULARITY_NAME; then
       export PS1="${SINGULARITY_NAME:+[SING]}$PS1"
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
