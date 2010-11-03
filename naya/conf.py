import re


class Config(dict):
    separator = ':'

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.is_valid(self)

    def is_valid(self, data):
        regex = '[^a-z_]'
        for key, value in data.items():
            if not isinstance(key, basestring) or re.search(regex, key):
                raise KeyError(
                    'All keys must be string and match regex[%r]' % regex
                )
            if isinstance(value, dict):
                self.is_valid(value)

    def get(self, name, default=None):
        try:
            value = self[name]
        except KeyError:
            value = default
        return value

    def __getitem__(self, name):
        if name.find(self.separator) != -1:
            index = name.index(self.separator)
            value = self.__getitem__(name[:index])
            if isinstance(value, dict):
                return value[name[index + 1:]]
            raise KeyError
        value = super(Config, self).__getitem__(name)
        if value is None:
            raise KeyError
        if isinstance(value, dict):
            value = Config(value)
        return value

    def __setitem__(self, name, value):
        if name.find(self.separator) != -1:
            index = name.index(self.separator)
            key = name[:index]
            if not key in self or not isinstance(self[key], dict):
                super(Config, self).__setitem__(key, Config())
            new = self[key]
            new[name[index + 1:]] = value
            super(Config, self).__setitem__(key, new)
            return

        if name in self and isinstance(self[name], dict) and isinstance(value, dict):
            self[name].update(value)
            return

        super(Config, self).__setitem__(name, value)

    def update(self, data):
        self.is_valid(data)
        for key, value in data.items():
            if not key in self or not isinstance(value, dict):
                self[key] = value
                continue

            new = self[key]
            new.update(value)
            super(Config, self).__setitem__(key, new)

