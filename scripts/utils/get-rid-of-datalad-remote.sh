#!/bin/zsh
# the goal is to transfer handling of all URLs directly to web remote and not datalad
# one which initially was needed for handling shub:// urls.

# disable autoenabling of datalad remote
git annex enableremote datalad autoenable=false

# For those which are in shub:// resolve urls directly to the images
# Had to use zsh  since in bash this cmds changes not visible outside of the loop
cmds=''; 
git annex find --not --in web --in datalad | \
    while read f; do 
    shub=$(git annex whereis $f | sed -n -e '/shub:/s,.*shub://,,gp'); key=$(readlink $f | xargs basename); url=$(curl --silent https://singularity-hub.org/api/container/$shub | jq .image | sed -e 's,",,g'); cmds+="git annex registerurl $key $url;"; done

# We need to run registerurl after we "disable" datalad remote so it does not claim them
git remote remove datalad

eval $cmds

git checkout git-annex

# move neurodesk ones 
web=00000000-0000-0000-0000-000000000001; 
git grep -l :https://objectstorage | grep '\.web$' | while read f; do 
    grep -q "$web" ${f//.web/} || sed -i -e "1i1675747460.124574642s 1 $web" ${f//.web/}; 
    # transfer them from being handled directly by web remote, thus not to have : prefix
    sed -i -e "s,:https://objectstorage,https://objectstorage,g" $f ; 
done

git commit -m 'Moved all URLs for neurodesk to regular web remote' -a
git checkout master
git log -p git-annex
