#!/usr/bin/env python
from fabric.api import local
from werkzeug.script import run


def action_pep8(target='.'):
    '''Run pep8.'''
    local('pep8 --ignore=E202 %s' % target, capture=False)


def action_clean(mask=''):
    '''Clean useless files.'''
    masks = [mask] if mask else ['*.pyc', '*.pyo', '*~', '*.orig']
    command = ('find . -name "%s" -exec rm -f {} +' % mask for mask in masks)
    local('\n'.join(command), capture=False)


def action_test(target='', coverage=True):
    '''Run tests.'''
    command = 'nosetests -v'
    if coverage:
        command = (
            '%s --cover-tests --with-coverage --cover-package=naya' % command
        )
    if target:
        command = '%s %s' % (command, target)

    local(command, capture=False)


if __name__ == '__main__':
    run()
