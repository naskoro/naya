#!/usr/bin/env python
from naya import Naya
from werkzeug import run_simple


app = Naya(__name__)


@app.route('/')
def index(app):
    return 'Hello world!'


if __name__ == '__main__':
    run_simple('127.0.0.1', 5000, app)
