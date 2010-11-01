#!/usr/bin/env python
from naya import App
from werkzeug import run_simple


app = App(__name__)


@app.root.route('/')
def index(app):
    return 'Hello world!'


if __name__ == '__main__':
    run_simple('127.0.0.1', 5000, app)
