def test_sh():
    '''
    FAIL: Need Doctest for test_script.test_sh;

    >>> from naya.script import sh
    >>> sh('cd ~')
    $ cd ~
    >>> sh(('cd ~', 'cd /'))
    $ cd ~ && cd /
    >>> sh('echo "test"')
    $ echo "test"
    test
    <BLANKLINE>
    >>> sh(('echo "test"', 'echo "test"'))
    $ echo "test" && echo "test"
    test
    test
    <BLANKLINE>
    >>> sh(('echo "test"', 'cd __'))
    Traceback (most recent call last):
        ...
    SystemExit: 2
    >>> sh('echo {answer}', params={'answer':'42'})
    $ echo 42
    42
    <BLANKLINE>
    >>> sh('echo "{answer}"', params={'answer': 42})
    $ echo "42"
    42
    <BLANKLINE>
    >>> sh('echo 42', host='localhost')
    $ ssh localhost "echo 42"
    42
    <BLANKLINE>
    >>> sh('echo "42"', host='localhost')
    $ ssh localhost "echo \\"42\\""
    42
    <BLANKLINE>
    '''
