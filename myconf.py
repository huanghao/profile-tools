#!/usr/bin/env python
import os
import argparse
import logging

from profiletools.cmds import br_cmd, df_cmd, co_cmd, ci_cmd, push_cmd


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

    br = sp.add_parser('br', help='list all available profiles')
    br.set_defaults(func=br_cmd)

    df = sp.add_parser('df', help='show status of current profile')
    df.set_defaults(func=df_cmd)
    df.add_argument('-v', '--verbose', action='store_true')

    co = sp.add_parser('co', help='apply profile')
    co.set_defaults(func=co_cmd)
    co.add_argument('profile_name')
    # FIXME: check df before co

    ci = sp.add_parser('ci', help='commit changed')
    ci.set_defaults(func=ci_cmd)

    push = sp.add_parser('push', help='push committed changes to remote')
    push.set_defaults(func=push)

    return p.parse_args()


def main():
    args = parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    args.func(args)


if __name__ == '__main__':
    main()
