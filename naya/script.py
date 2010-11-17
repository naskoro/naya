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


class Shell(object):
    def __init__(self, *args, **kwargs):
        self.defaults(*args, **kwargs)

        self.stdout = None
        self.stderr = None
        self.code = None

    def defaults(self, capture=False, host=None, params=None):
        self.params = params
        self.host = host
        self.capture = capture

    def __call__(self, command, capture=False, host=None, params=None):
        capture = capture if capture != None else self.capture
        host = host if host != None else self.host
        params = params if params != None else self.params

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
            stdout = stdout.strip() if stdout else None
            stderr = stderr.strip() if stderr else None

            self.stdout, self.stderr = stdout, stderr
            self.code = code = cmd.returncode
            self.cmd = cmd

            out = stdout and [stdout] or []
            out += stderr and [stderr] or []
            if code != 0:
                out += ['FAIL with code %r.\n' % code]
            if out:
                print '\n\n'.join(out)
        except KeyboardInterrupt:
            print >> sys.stderr, "\nStopped."
            sys.exit(1)
        if code != 0:
            sys.exit(code)
        return stdout

sh = Shell()
