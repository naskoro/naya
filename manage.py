#!/usr/bin/env python
from naya.script import sh
from werkzeug.script import run


SERVER_PARAMS = {
    'activate': 'source /root/.virtualenvs/pusto/bin/activate && which python',
    'naya_path': '/root/repos/naya'
}


def action_pep8(target='.'):
    '''Run pep8.'''
    sh('pep8 --ignore=E202 %s' % target)


def action_clean(mask=''):
    '''Clean useless files.'''
    masks = [mask] if mask else ['*.pyc', '*.pyo', '*~', '*.orig']
    command = ('find . -name "%s" -exec rm -f {} +' % mask for mask in masks)
    sh('\n'.join(command))


def action_test(target='', coverage=False):
    '''Run tests.'''
    command = ['nosetests -v --with-doctest']
    if coverage:
        command.append('--with-coverage --cover-tests --cover-package=naya')
    if target:
        command.append(target)

    sh(' '.join(command))


def action_deploy(host='yadro.org'):
    '''Deploy code on server.'''
    sh(('pwd', 'hg push'))
    sh((
        '{activate}', 'cd {naya_path}', 'hg up', 'pip install .'
    ), host=host, params=SERVER_PARAMS)


if __name__ == '__main__':
    run()
