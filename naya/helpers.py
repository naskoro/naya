import os
import sys


class Mark(object):
    NAME = '_mark_name_'
    INDEX = '_mark_index_'

    def __init__(self, name):
        self.name = name

    def __call__(self, index=10):
        def wrap(func):
            setattr(func, self.NAME, self.name)
            setattr(func, self.INDEX, index)
            return func
        return wrap

    def of(self, obj):
        funcs = []
        for attr in dir(obj):
            attr = getattr(obj, attr)
            if callable(attr) and hasattr(attr, self.NAME) \
            and getattr(attr, self.NAME) == self.name:
                funcs.insert(getattr(attr, self.INDEX), attr)
        return funcs

    def run(self, obj, callback=lambda x: x):
        for func in self.of(obj):
            callback(func())


class Marker(object):
    def __init__(self):
        self._marks = {}

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        marks = self._marks
        if name not in marks:
            marks[name] = Mark(name)
        return marks[name]


marker = Marker()


def get_package_path(name):
    """Returns the path to a package or cwd if that cannot be found."""
    try:
        return os.path.abspath(os.path.dirname(sys.modules[name].__file__))
    except (KeyError, AttributeError):
        return os.getcwd()
