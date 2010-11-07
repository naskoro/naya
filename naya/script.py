import sys
from subprocess import Popen, PIPE


def make_shell(init_func=None, banner=None, use_bpython=True):
    """
    Returns an action callback that spawns a new interactive
    python shell.
    """
    if banner is None:
        banner = 'Interactive Werkzeug Shell'
    if init_func is None:
        init_func = dict

    def action(bpython=use_bpython):
        """Start a new interactive python session."""
        namespace = init_func()

        if use_bpython:
            try:
                import bpython
            except ImportError:
                pass
            else:
                bpython.embed(locals_=namespace, banner=banner)
                return

        from code import interact
        interact(banner, local=namespace)
    return action


def sh(command, capture=False, host=None, params=None, exit=False):
    if isinstance(command, (tuple, list)):
        command = ' && '.join(command)

    if params:
        command = command.format(**params)

    if host:
        command = command.replace('"', '\\"')
        command = 'ssh {0} "{1}"'.format(host, command)

    print '$ {0!s}'.format(command)

    stdout = stderr = not capture and PIPE or None

    cmd = Popen([command], stdout=stdout, stderr=stderr, shell=True)
    try:
        stdout, stderr = cmd.communicate()
        code = cmd.returncode

        out = stdout and [stdout] or []
        out += stderr and [stderr] or []
        out += cmd.returncode != 0 and ['FAIL with code %r.\n' % code] or []
        if out:
            print '\n\n'.join(out)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nStopped."
        sys.exit(1)
    if code != 0 or exit:
        sys.exit(code)
