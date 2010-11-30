def test_sh():
    '''
    NOTICE: Need Doctest for test_script.test_sh;

    >>> from subprocess import Popen
    >>> from naya.script import sh
    >>> sh('cd ~')
    $ cd ~
    >>> sh.stdout
    >>> sh.code
    0
    >>> isinstance(sh.cmd, Popen)
    True
    >>> sh(('cd ~', 'cd /'))
    $ cd ~ && cd /
    >>> sh('echo "test"')
    $ echo "test"
    test
    'test'
    >>> sh(('echo "test"', 'echo "test"'))
    $ echo "test" && echo "test"
    test
    test
    'test\\ntest'
    >>> sh(('echo "test"', 'cd __'))
    Traceback (most recent call last):
        ...
    SystemExit: 2
    >>> sh.stdout
    "test\\ncd: 1: can't cd to __"
    >>> sh.code
    2
    >>> sh('echo $answer', params={'answer':'42'})
    $ echo 42
    42
    '42'
    >>> sh('echo "$answer"', params={'answer': 42})
    $ echo "42"
    42
    '42'
    >>> sh('echo 42', remote='localhost')
    $ ssh localhost "echo 42"
    42
    '42'
    >>> sh('echo "42"', remote='localhost')
    $ ssh localhost "echo \\"42\\""
    42
    '42'
    >>> sh.defaults(params={'answer': '42'}, host='localhost')
    >>> sh('echo $answer')
    $ echo 42
    42
    '42'
    >>> sh('echo $answer', remote=True)
    $ ssh localhost "echo 42"
    42
    '42'
    >>> sh('echo $answer', params={'answer': 'not 42'})
    $ echo not 42
    not 42
    'not 42'
    >>> sh('echo $answer', capture=True)
    $ echo 42
    >>> sh.defaults(capture=True)
    >>> sh('echo 42', capture=False)
    $ echo 42
    42
    '42'
    '''
