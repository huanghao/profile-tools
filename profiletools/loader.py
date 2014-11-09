import os
import glob

import yaml

from profiletools.path import esc, sub


class ProfileNotFound(Exception):
    pass


class BadProfile(Exception):
    pass


def current_profile_filename(target_root):
    return os.path.join(
        target_root,
        os.path.expanduser('~').lstrip(os.path.sep),
        '.my-current-profile-name')


def current_profile_name(target_root):
    current = current_profile_filename(target_root)
    try:
        with open(current) as file:
            return file.readline().rstrip()
    except Exception as err:
        raise ProfileNotFound(err)


def set_current_profile_name(target_root, name):
    current = current_profile_filename(target_root)
    with open(current, 'w') as file:
        file.write(name)


class ProfileLoader(object):

    def __init__(self, root):
        self.root = root

    def get(self, name):
        return Profile(
            name,
            os.path.join(self.root, 'profiles', name),
            os.path.join(self.root, 'profiles', name + '.yml')
            )

    def names(self):
        pattern = os.path.join(self.root, 'profiles', '*.yml')
        return (os.path.splitext(os.path.basename(i))[0]
                for i in glob.glob(pattern))


class Profile(object):
    """
    Profile YAML example::

    name: Mac
    description: MacBook Air
    from: base
    files:
      - copy: path=~/bin/*
      - copy: path=~/.emacs
      - patch: path=~/.ssh/config
      - file: path=/tmp/a
    """
    def __init__(self, name, path, conf):
        self.name = name
        self.path = path
        self.conf = conf
        self.settings = self.load()

    def load(self):
        from profiletools.modules import create_module, parse_attrs

        try:
            with open(self.conf) as file:
                data = yaml.load(file)
        except Exception as err:
            raise BadProfile(err)

        files = []
        for each in data.get('files', ()):
            if len(each) != 1:
                raise ValueError("Invalid module conf: %s" % each)
            name, val = each.items()[0]
            attrs = parse_attrs(val)
            files.append(create_module(name, self, attrs))
        data['files'] = files
        return data

    def __str__(self):
        return 'Profile(%s)' % self.settings['name']

    def walk(self, top):
        """
        walk(profile.path, '~') yields (relative, absolute) pairs like this:

        ~/.emacs, {profile.path}/__HOME__/.emacs
        """
        root = os.path.expanduser(self.path)
        top = os.path.join(root, esc(top).lstrip(os.path.sep))
        for dirname, dirnames, filenames in os.walk(top):
            for filename in filenames:
                src = os.path.join(dirname, filename)
                rel = sub(src[len(root)+1:])
                yield rel, src
