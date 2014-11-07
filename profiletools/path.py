"""
There are three types of pathes:

- *real* path in the file system
  /home/alice/.emacs
  /chroot/home/alice/.emacs

- *relative* path to inside a target-root
  ~/.emacs
  ~/.ssh/.config

- *escaped* path inside a profile-root
  __HOME__/__emacs
  __HOME__/__ssh/__config

Use these functions to convert between them:

- sub: escaped -> relative
- esc: relative -> escaped
"""
import os


def esc(path):
    if '~' in path:
        path = path.replace('~', '__HOME__')

    parts = path.split(os.path.sep)
    return os.path.sep.join(
        ('__' + p[1:])
        if p.startswith('.')
        else p
        for p in parts)


def sub(path):
    def _t(p):
        if p == '__HOME__':
            return '~'
        elif p.startswith('__'):
            return '.' + p[2:]
        else:
            return p

    parts = path.split(os.path.sep)
    return os.path.sep.join(_t(p) for p in parts)


def walk(profile):
    top = os.path.join(ROOT, 'profiles', profile)
    for dirpath, dirnames, filenames in os.walk(top):
        path = dirpath[len(top)+1:]
        for filename in filenames:
            name = os.path.join(path, filename)
            yield name, sub(name)
