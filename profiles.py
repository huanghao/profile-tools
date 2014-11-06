#!/usr/bin/env python
import os
import sys
import glob
import argparse

import yaml

ROOT = os.path.expanduser('~/.my-profiles')

CONTEXT = {
    '__HOME__': os.path.expanduser('~'),
    }

def sub(name):
    if name.startswith('__'):
        hide = '.' + name[2:]
        return CONTEXT.get(name, hide)
    return name


def walk(profile):
    top = os.path.join(ROOT, 'profiles', profile)
    for dirpath, dirnames, filenames in os.walk(top):
        parts = dirpath[len(top)+1:].split(os.path.sep)
        parts = (sub(i) for i in parts)
        path = os.path.sep.join(parts)

        for filename in filenames:
            name = sub(filename)
            yield os.path.join(path, name)


def load(profile):
    filename = os.path.join(ROOT, 'profiles', profile + '.yml')
    with open(filename) as file:
        return yaml.load(file)


def current_profile_name():
    current = os.path.join(ROOT, 'current')
    if os.path.exists(current):
        return open(current).read().strip()


def list_cmd(args):
    current = current_profile_name()
    found = False
    pattern = os.path.join(ROOT, 'profiles', '*.yml')
    for filename in glob.glob(pattern):
        name = os.path.splitext(os.path.basename(filename))[0]
        if name == current:
            print '*', name
            found = True
        else:
            print ' ', name

    if not found:
        print '* (detached)'


def st_cmd(args):
    current = current_profile_name()
    if not current:
        print >> sys.stderr, "Invalid current pofile"
    manifest = load(current)
    print manifest


def parse_args():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(title='subcommands')

    list_p = sp.add_parser('list', help='list all available profiles')
    list_p.set_defaults(func=list_cmd)

    st_p = sp.add_parser('st', help='show status of current profile')
    st_p.set_defaults(func=st_cmd)

    return p.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
