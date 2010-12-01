#!/usr/bin/env python
from naya.script import make_shell
from werkzeug.script import make_runserver, run

from . import app


action_shell = make_shell(lambda: {'app': app})
action_run = make_runserver(
    lambda: app, use_reloader=True, use_debugger=True
)


if __name__ == '__main__':
    run()
