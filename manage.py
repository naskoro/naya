#!/usr/bin/env python
from naya.script import sh, make_shell
from werkzeug.script import run


def action_clean(mask=''):
    '''Clean useless files.'''
    masks = [mask] if mask else ['*.pyc', '*.pyo', '*~', '*.orig']
    command = ('find . -name "%s" -exec rm -f {} +' % mask for mask in masks)
    sh('\n'.join(command))


def action_code(target='.'):
    '''Check code style'''
    sh('pep8 --ignore=E202 %s' % target, no_exit=True)
    sh('pyflakes %s' % target, no_exit=True)
    sh('git diff | grep -5 print', no_exit=True)


def action_test(target='', base=False, rm=False, failed=('f', False),
                with_coverage=('c', False), cover_package=('p', 'naya')):
    '''Run tests.'''
    if rm:
        sh('rm .noseids .coverage')
    if base:
        command = ['nosetests']
    else:
        command = ['nosetests -v --with-doctest']

    if failed:
        command.append('--failed')
    if with_coverage:
        command.append('--with-coverage --cover-tests')
        if cover_package:
            command.append('--cover-package=%s' % cover_package)

    command.append('--with-id')

    if target:
        command.append(target)

    sh(' '.join(command))


action_shell = make_shell()


if __name__ == '__main__':
    run()
