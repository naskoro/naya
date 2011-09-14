from subprocess import Popen, PIPE, STDOUT

from naya.testing import aye


def test_shell():
    def check(cmd):
        cmd = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        stdout, stderr = cmd.communicate('print(42)\nquit()')
        aye('==', 0, cmd.returncode)
        aye('==', '42\n', stdout)

    check('./manage.py shell')
    check('./manage.py shell --no-bpython')

    cmd = Popen('./manage.py shell', shell=True,
        stdin=PIPE, stdout=PIPE, stderr=STDOUT
    )
    aye('is', None, cmd.terminate())


def test_sh():
    '''
    NOTICE: Need Doctest for test_script.test_sh;

    >>> from naya.script import sh
    >>> sh.defaults(capture=True)
    >>> sh('cd ~')
    $ cd ~
    >>> sh.stdout
    >>> sh.code
    0
    >>> sh(('cd ~', 'cd /'))
    $ cd ~ && cd /
    >>> sh('echo "test"')
    $ echo "test"
    'test'
    >>> sh(('echo "test"', 'echo "test"'))
    $ echo "test" && echo "test"
    'test\\ntest'
    >>> sh(('echo "test"', 'cd __'))
    Traceback (most recent call last):
        ...
    SystemExit: 2
    >>> sh.stdout
    "test\\n/bin/sh: 1: cd: can't cd to __"
    >>> sh(('echo "test"', 'cd __'), no_exit=True)
    $ echo "test" && cd __
    "test\\n/bin/sh: 1: cd: can't cd to __"
    >>> sh.code
    2
    >>> sh('echo $answer', params={'answer':'42'})
    $ echo 42
    '42'
    >>> sh('echo "$answer"', params={'answer': 42})
    $ echo "42"
    '42'
    >>> sh('echo 42', remote='localhost')
    $ ssh localhost "echo 42"
    '42'
    >>> sh('echo "42"', remote='localhost')
    $ ssh localhost "echo \\"42\\""
    '42'
    >>> sh.defaults(params={'answer': '42'}, host='localhost', capture=True)
    >>> sh('echo $answer')
    $ echo 42
    '42'
    >>> sh('echo $answer', remote=True)
    $ ssh localhost "echo 42"
    '42'
    >>> sh('echo $answer', params={'answer': 'not 42'})
    $ echo not 42
    'not 42'
    >>> sh('echo $answer', params={'42': 'is answer'})
    $ echo 42
    '42'
    >>> answer = sh('echo $answer', capture=True)
    $ echo 42
    >>> assert answer == '42'
    >>> sh('echo $answer', answer=42)
    Traceback (most recent call last):
    ...
    KeyError: "Unknown options: {'answer': 42}"
    >>> sh.defaults(answer=42)
    Traceback (most recent call last):
    ...
    KeyError: "Unknown options: {'answer': 42}"
    '''
