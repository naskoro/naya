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


    def defaults(self, capture=False, params=None, host=None):
        self.capture = capture
        self.params = params
        self.host = host

    def __call__(self, command, capture=False, params=None, remote=False):
        self.stdout = self.cmd =  self.code = None

        capture = capture if capture != None else self.capture
        params = params if params != None else self.params
        host = None
        if remote:
            host = remote if isinstance(remote, basestring) else self.host

        if isinstance(command, (tuple, list)):
            command = ' && '.join(command)

        command = Template(command).substitute(params or {})

        if host:
            command = command.replace('"', '\\"')
            command = 'ssh {0} "{1}"'.format(host, command)

        print '$ {0!s}'.format(command)

        self.cmd = Popen([command], stdout=PIPE , stderr=STDOUT, shell=True)
        try:
            if not capture:
                self.stdout = ''
                while True:
                    line = self.cmd.stdout.readline()
                    if not line:
                        break
                    print line,
                    self.stdout += line
                self.stdout = self.stdout.strip() or None

            self.cmd.wait()
        except KeyboardInterrupt:
            print >> sys.stderr, '\nStopped.'

        self.code = code = self.cmd.returncode
        if code != 0:
            print 'FAIL with code %r.\n' % code
            sys.exit(code)
        return self.stdout

sh = Shell()
