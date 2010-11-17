#!/usr/bin/env python
from naya.script import sh
from werkzeug.script import run


def action_pep8(target='.'):
    '''Run pep8.'''
    sh('pep8 --ignore=E202 %s' % target)


def action_clean(mask=''):
    '''Clean useless files.'''
    masks = [mask] if mask else ['*.pyc', '*.pyo', '*~', '*.orig']
    command = ('find . -name "%s" -exec rm -f {} +' % mask for mask in masks)
    sh('\n'.join(command))


def action_test(target='', clean=False, failed=('f', False),
                with_coverage=('c', False), cover_package=('p', 'naya')):
    '''Run tests.'''
    if clean:
        command = ['nosetests']
    else:
        command = ['nosetests -v --with-doctest']

    if failed:
        command.append('--failed')
    if with_coverage:
        command.append('--with-coverage --cover-tests')
    if cover_package:
        command.append('--cover-package={0}'.format(cover_package))

    command.append('--with-id')

    if target:
        command.append(target)

    sh(' '.join(command))


if __name__ == '__main__':
    run()
