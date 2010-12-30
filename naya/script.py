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

    def defaults(self, params={}, host=None, capture=False, remote=False):
        self.params = params
        self.host = host
        self.capture = capture
        self.remote = remote

    def __call__(self, command, **options):
        self.code = self.stdout = None

        params = options.pop('params', None)
        remote = options.pop('remote', self.remote)
        capture = options.pop('capture', self.capture)

        if options:
            raise KeyError('Unknown options: %r' % options)

        context = self.params.copy()
        if params:
            context.update(params)

        if isinstance(command, (tuple, list)):
            command = ' && '.join(command)

        if context:
            command = Template(command).substitute(context)

        if remote:
            host = remote if isinstance(remote, basestring) else self.host
            command = command.replace('"', '\\"')
            command = 'ssh {0} "{1}"'.format(host, command)

        print('$ {0!s}'.format(command))

        stdout = None
        if capture:
            stdout = PIPE
        cmd = Popen([command], stdout=stdout, stderr=STDOUT, shell=True)
        try:
            stdout, code = cmd.communicate()[0], cmd.returncode
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
