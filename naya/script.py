import sys
from string import Template
from subprocess import Popen, PIPE, STDOUT


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

    def defaults(self, params=None, host=None):
        self.params = params
        self.host = host

    def run(self, cmd, capture):
        if capture:
            return cmd.wait(), cmd.stdout.read()

        stdout = ''
        while True:
            line = cmd.stdout.readline()
            if not line:
                break
            print(line.rstrip())
            stdout += line
        return cmd.wait(), stdout

    def __call__(self, command, capture=False, params=None, remote=False):
        self.code = self.stdout = None
        params = params or self.params

        if isinstance(command, (tuple, list)):
            command = ' && '.join(command)

        if params:
            command = Template(command).substitute(params)

        if remote:
            host = remote if isinstance(remote, basestring) else self.host
            command = command.replace('"', '\\"')
            command = 'ssh {0} "{1}"'.format(host, command)

        print('$ {0!s}'.format(command))

        cmd = Popen([command], stdout=PIPE, stderr=STDOUT, shell=True)
        try:
            code, stdout = self.run(cmd, capture)
        except KeyboardInterrupt:
            print('\nStopped.')
            sys.exit(1)

        self.code = code
        self.stdout = stdout and stdout.strip() or None
        if code != 0:
            print('Failed with code {0}.\n'.format(code))
            sys.exit(code)

        if capture:
            return self.stdout

sh = Shell()
