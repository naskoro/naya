import os
import sys


def get_package_path(name):
    """Returns the path to a package or cwd if that cannot be found."""
    try:
        return os.path.abspath(os.path.dirname(sys.modules[name].__file__))
    except (KeyError, AttributeError):
        return os.getcwd()


class DictByDot(object):
    def __init__(self, data={}):
        self._data = data

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        res = self._data[name]
        if isinstance(res, dict):
            res = DictByDot(res)
        return res

    def __setattribute__(self, name, value):
        if name.startswith('_'):
            object.__setattribute__(self, name, value)
        self._data[name] = value
