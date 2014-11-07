from profiletools.loader import ProfileLoader


def list_cmd(args):
    loader = ProfileLoader(args.profile_root)
    try:
        current = loader.current()
    except ValueError: #FIXME: specific exception need
        current = None

    found = False
    for name in loader.names():
        if current and name == current.name:
            print '*', name
            found = True
        else:
            print ' ', name

    if not found:
        print '* (unmanaged)'

    print '\nuse "%s apply" to apply a profile.'


def st_cmd(args):
    print '#FIXME: current file should move to some place inside target_root'


def apply_cmd(args):
    loader = ProfileLoader(args.profile_root)
    profile = loader.get(args.profile_name)

    for mod in profile.settings['files']:
        mod.apply(args)
