import os
import sys


class Register(object):
    NAME = 'register_name'
    INDEX = 'register_index'

    def __call__(self, name, index=10):
        def wrap(func):
            setattr(func, self.NAME, name)
            setattr(func, self.INDEX, index)
            return func
        return wrap

    def get(self, obj, name):
        funcs = []
        for attr in dir(obj):
            attr = getattr(obj, attr)
            if callable(attr) and hasattr(attr, self.NAME) \
            and getattr(attr, self.NAME) == name:
                funcs.insert(getattr(attr, self.INDEX), attr)
        return funcs

    def run(self, obj, name, callback=lambda x: x):
        for func in self.get(obj, name):
            callback(func())

register = Register()


def get_package_path(name):
    """Returns the path to a package or cwd if that cannot be found."""
    try:
        return os.path.abspath(os.path.dirname(sys.modules[name].__file__))
    except (KeyError, AttributeError):
        return os.getcwd()


def pformat(obj, verbose=False):
    """
    Prettyprint an object.  Either use the `pretty` library or the
    builtin `pprint`.
    """
    try:
        from pretty import pretty
        return pretty(obj, verbose=verbose)
    except ImportError:
        from pprint import pformat
        return pformat(obj)
