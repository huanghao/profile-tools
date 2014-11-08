#!/usr/bin/env python
import os
import sys
import glob
import argparse
import logging
from fnmatch import fnmatch

import yaml

from profiletools.cmds import list_cmd, st_cmd, apply_cmd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--debug', action='store_true')
    p.add_argument('-y', '--yes')
    p.add_argument('-r', '--profile-root',
        default=os.path.expanduser('~/.my-profiles'),
        help='root path contains all profiles')
    p.add_argument('-t', '--target-root', default=os.path.sep,
        help='target root path, default is "/"')

    sp = p.add_subparsers(title='subcommands')

    list_p = sp.add_parser('list', help='list all available profiles')
    list_p.set_defaults(func=list_cmd)

    st_p = sp.add_parser('st', help='show status of current profile')
    st_p.set_defaults(func=st_cmd)

    apply_p = sp.add_parser('apply', help='apply profile')
    apply_p.set_defaults(func=apply_cmd)
    apply_p.add_argument('profile_name')

    return p.parse_args()


def main():
    args = parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    args.func(args)


if __name__ == '__main__':
    main()
