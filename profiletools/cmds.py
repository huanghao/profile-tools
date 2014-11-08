from profiletools.loader import (
    ProfileLoader, current_profile_name, set_current_profile_name,
    BadProfile, ProfileNotFound)


def list_cmd(args):
    loader = ProfileLoader(args.profile_root)
    try:
        current = current_profile_name(args.target_root)
    except ProfileNotFound:
        current = '(not found)'
    else:
        try:
            loader.get(current)
        except BadProfile:
            current = '(unmanaged)'

    found = False
    for name in loader.names():
        if name == current:
            print '*', name
            found = True
        else:
            print ' ', name

    if not found:
        print '*', current

    print 'use "%s apply" to apply a profile.'


def st_cmd(args):
    print '#FIXME: current file should move to some place inside target_root'


def apply_cmd(args):
    loader = ProfileLoader(args.profile_root)
    profile = loader.get(args.profile_name)

    for mod in profile.settings['files']:
        mod.apply(args)

    set_current_profile_name(args.target_root, args.profile_name)
