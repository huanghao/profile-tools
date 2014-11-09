import os
import glob
import time
import inspect
import shutil
import logging
import hashlib
import tempfile

from profiletools.loader import ProfileLoader
from profiletools.path import esc, sub


log = logging.getLogger(__name__)


class UnknownModule(Exception):
    pass


def is_the_same(file1, file2):
    st1 = os.stat(file1)
    st2 = os.stat(file2)
    # 0: st_mode - protection bits,
    # st_ino - inode number,
    # st_dev - device,
    # st_nlink - number of hard links,
    # st_uid - user id of owner,
    # st_gid - group id of owner,
    # 6: st_size - size of file, in bytes,
    # st_atime - time of most recent access,
    # st_mtime - time of most recent content modification,
    # st_ctime - platform dependent; time of most recent metadata change on Unix, or the time of creation on Windows)
    getkey = lambda st: st[6]
    key1 = getkey(st1)
    key2 = getkey(st2)
    if key1 != key2:
        return False

    hash1 = hashlib.md5(open(file1).read()).hexdigest()
    hash2 = hashlib.md5(open(file2).read()).hexdigest()
    if hash1 != hash2:
        print file1, file2
    return hash1 == hash2


#FIXME: harcord path here
BACKUP_PATH = os.path.expanduser('~/.my-profiles-backup')

def back_up(path):
    name = '%s_%s' % (time.time(), path.replace(os.path.sep, '_'))
    name = os.path.join(BACKUP_PATH, name)
    print 'backup', path, 'to', name
    os.rename(path, name)


def patch(origin, patch, to):
    fd, tmp = tempfile.mkstemp()
    os.close(fd)
    shutil.copyfile(origin, tmp)
    os.system('patch %s %s >/dev/null' % (tmp, patch))
    if need_change(tmp, to):
        os.rename(tmp, to)
        return True


def need_change(src, to):
    if os.path.islink(to):
        os.unlink(to)
    elif os.path.exists(to):
        if is_the_same(src, to):
            return False
        back_up(to)
    return True


def savecopy(src, to):
    if need_change(src, to):
        shutil.copy2(src, to)
        return True


class Module(object):

    def __init__(self, profile, attrs):
        self.profile = profile
        self.attrs = dict(attrs)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__,
            ', '.join(['%s=%s' % (k,v) for k,v in self.attrs.items()]))

    def apply(self, _args):
        """
        Apply this module
        """
        raise NotImplementError

    def find(self, profile_root, target_root):
        if 'from' in self.attrs:
            profile = ProfileLoader(
                profile_root).get(self.attrs['from'])
        else:
            profile = self.profile

        if 'exclude' in self.attrs:
            excludes = self.attrs['exclude'].split(',')
            def exclude(path):
                return any(path.startswith(ex) for ex in excludes)
        else:
            exclude = lambda _: False

        for rel, src in profile.walk(self.attrs['path']):
            if exclude and exclude(rel):
                continue
            to = os.path.join(
                os.path.expanduser(target_root),
                os.path.expanduser(sub(rel)).lstrip(os.path.sep))
            yield src, to



class Copy(Module):
    """
    Copy from another profile. Example::

    copy: path=~
    copy: path=~ from=base
    copy: path=~ exclude=~/bin,~/.ssh
    """

    def apply(self, args):
        print '>>>', self
        i = 0
        for src, to in self.find(args.profile_root, args.target_root):
            log.debug('%s -> %s', src, to)
            if savecopy(src, to):
                i += 1
        if i > 0:
            print i, 'file(s) copied'
        # TODO: check file exist and give choose
        # --yes to choose the default, normally means overwriting


class Patch(Module):
    """
    Patch based on a file from another profile. Example:

    patch: path=~/.ssh/config
    patch: path=~/.ssh/config from=base
    """
    def apply(self, args):
        print '>>>', self
        base = ProfileLoader(args.profile_root).get(self.attrs['from'])

        rel = esc(self.attrs['path']).lstrip(os.path.sep)
        src = os.path.join(base.path, rel)
        pat = os.path.join(self.profile.path, rel)
        to = os.path.join(
            os.path.expanduser(args.target_root),
            os.path.expanduser(sub(rel)).lstrip(os.path.sep))

        log.debug('path: %s < %s > %s', src, pat, to)
        if patch(src, pat, to):
            print '1 file patched'


def all_modules():
    return {k.lower(): v
            for k, v in globals().items()
            if inspect.isclass(v) and issubclass(v, Module)}
            
MODULES = all_modules()

def parse_attrs(value):
    #FIXME: deal with whitespaces, enclosed by double quotes
    return dict([i.split('=', 1) for i in value.split()])


def create_module(name, profile, attrs):
    cls = MODULES.get(name)
    if not cls:
        raise UnknownModule("Invalid module: %s" % name)
    return cls(profile, attrs)
