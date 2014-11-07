import os
import glob

import yaml


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

    def current(self):
        current = os.path.join(self.root, 'current')
        if os.path.exists(current):
            with open(current) as file:
                name = file.readline()
            return self.get(name.rstrip())
        raise ValueError("Can't find current profile name")


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

        with open(self.conf) as file:
            data = yaml.load(file)

        if 'from' in data:
            baseattrs = {'from': data['from']}
        else:
            baseattrs = {}

        files = []
        for each in data.get('files', ()):
            if len(each) != 1:
                raise ValueError("Invalid module conf: %s" % each)
            name, val = each.items()[0]
            attrs = parse_attrs(val)
            files.append(create_module(name, self, attrs, baseattrs))
        data['files'] = files
        return data

    def __str__(self):
        return 'Profile(%s)' % self.settings['name']
