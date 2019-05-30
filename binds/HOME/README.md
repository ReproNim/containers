This is a "sanitized" HOME directory to be used during containerized
execution, so that there is no side-effects from having some tools
and "data" to leak into the computing environment. All necessary for
computation paths should be explicitly bind mounted.

If .gitconfig (ignored by git by default) will be created if does not
yet exists or misses those configuration entries, with user.name and 
user.email configuration items for git.  Their values will be taken
from the git's configuration in host environment/dataset. 
If you would like to hardcode/use some other - just create and populate
that file manually.  You can also keep it under git in your fork of
this repository - just adjust .gitignore.

