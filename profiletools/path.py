"""
Two types of relative path:

- *quoted*
  __HOME__/.emacs
  __HOME__/.ssh/config

- *unquoted" (always not expanduser)
  ~/.emacs
  ~/.ssh/config

Two types of absoluate path:

- inside of profile-root
  {profile-root|expanduser}/{quoted}

- inside of target-root
  {target-root|expanduser}/{unquoted|expanduser}

Functions:

- esc: unquoted -> quoted
- sub: quoted -> unquoted
- pabs: (profile-root, unquoted) -> pabs
- tabs: (target-root, quoted) -> tabs
"""
import os


def esc(path):
    """relative -> escaped"""
    return path.replace('~', '__HOME__')


def sub(path):
    """escaped -> relative"""
    return path.replace('__HOME__', '~')
