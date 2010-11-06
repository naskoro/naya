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
    '''
