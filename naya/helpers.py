import os
import sys


class Register(object):
    SLUG = 'register_name'

    def __call__(self, name):
        def wrap(func):
            setattr(func, self.SLUG, name)
            return func
        return wrap

    def get_funcs(cls, obj, name):
        funcs = []
        for attr in dir(obj):
            attr = getattr(obj, attr)
            if hasattr(attr, cls.SLUG) and getattr(attr, cls.SLUG) == name:
                if callable(attr):
                    funcs.append(attr)
        return funcs

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
