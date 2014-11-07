import os
import glob
import inspect
import logging
from shutil import copyfile

from profiletools.loader import ProfileLoader
from profiletools.path import esc, sub


log = logging.getLogger(__name__)



def patch(origin, patch):
    cmd = 'patch %s %s' % (origin, patch)
    return os.system(cmd)



class Module(object):

    def __init__(self, profile, attrs, base=None):
        self.profile = profile
        if not base:
            base = {}
        self.attrs = dict(base, **attrs)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__,
            ', '.join(['%s=%s' % (k,v) for k,v in self.attrs.items()]))

    def apply(self, _args):
        """
        Apply this module
        """
        raise NotImplementError


class Copy(Module):
    """
    Copy from another profile. Example::

    copy: path=~/bin/*

    copy: path=~/bin/* from=base
    """

    def apply(self, args):
        print '>>>', self
        #FIXME: copy: path=~/bin/* from=home
        base = ProfileLoader(args.profile_root).get(self.attrs['from'])

        path = os.path.join(
            base.path,
            esc(self.attrs['path']).lstrip(os.path.sep))
        i = 0
        for src in glob.glob(path):
            i += 1
            rel = src.replace(base.path, '').lstrip(os.path.sep)
            to = os.path.join(
                os.path.expanduser(args.target_root),
                os.path.expanduser(sub(rel)).lstrip(os.path.sep))
            copyfile(src, to)
            log.debug('%s -> %s', src, to)

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

        copyfile(src, to)
        log.debug('%s -> %s', src, to)

        patch(to, pat)
        log.debug('patch %s < %s', to, pat)


class File(Module):
    """
    A file from current profile being applied. Example:

    file: path=~/some.file
    """
    def apply(self, args):
        print '>>>', self
        #FIXME: refactor the same code block in Copy.apply
        path = os.path.join(
            self.profile.path,
            esc(self.attrs['path'].lstrip(os.path.sep)))
        i = 0
        for src in glob.glob(path):
            i += 1
            rel = src.replace(self.profile.path, '').lstrip(os.path.sep)
            to = os.path.join(
                os.path.expanduser(args.target_root),
                os.path.expanduser(sub(rel)).lstrip(os.path.sep))
            copyfile(src, to)
            log.debug('%s -> %s', src, to)

        print i, 'file(s) copied'


def all_modules():
    return {k.lower(): v
            for k, v in globals().items()
            if inspect.isclass(v) and issubclass(v, Module)}
            
MODULES = all_modules()


def parse_attrs(value):
    #FIXME: deal with whitespaces, enclosed by double quotes
    return dict([i.split('=', 1) for i in value.split()])


def create_module(name, profile, attrs, baseattrs):
    cls = MODULES.get(name)
    if not cls:
        raise ValueError("Invalid module name: %s" % name)
    return cls(profile, attrs, baseattrs)
