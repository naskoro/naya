import os
import sys


class Mark(object):
    MARK = '_mark_'
    DEFAULT_INDEX = 10

    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        def wrap(func):
            self.func_set(func, args=args, kwargs=kwargs)
            return func
        return wrap

    def index(self, index):
        def wrap(func):
            self.func_set(func, index=index)
            return func
        return wrap

    def func_set(self, func, **options_):
        marks = getattr(func, self.MARK, [])
        options = {
            'name': self.name,
            'index': self.DEFAULT_INDEX,
            'args': [],
            'kwargs': {}
        }
        options.update(options_)
        marks.append(options)
        setattr(func, self.MARK, marks)

    def func_get(self, func):
        marks = getattr(func, self.MARK, [])
        return [mark for mark in marks if mark['name'] == self.name]

    def of(self, obj):
        funcs = []
        for attr in dir(obj):
            attr = getattr(obj, attr)
            if not callable(attr):
                continue
            marks = self.func_get(attr)
            for mark in marks:
                index = mark['index']
                item = attr, mark['args'], mark['kwargs']
                funcs.append((index, item))
        funcs.sort(key=lambda item: item[0])
        funcs = [func[1] for func in funcs]
        return funcs

    def run(self, obj):
        for func, args, kwargs in self.of(obj):
            func(*args, **kwargs)


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


def package_path(name):
    """Returns the path to a package or cwd if that cannot be found."""
    try:
        return os.path.abspath(os.path.dirname(sys.modules[name].__file__))
    except (KeyError, AttributeError):
        return os.getcwd()
