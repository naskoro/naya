import re


class Config(dict):
    separator = ':'

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.is_valid(self)

    def is_valid(self, data):
        regex = r'^$|^([a-z_][a-z_0-9]*$)'
        for key, value in data.items():
            if not isinstance(key, basestring) or not re.match(regex, key):
                raise KeyError(
                    'Keys must be a string and match %r, but contains key: %r'
                    % (regex, key)
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

        if self._update_item(name, value):
            return

        super(Config, self).__setitem__(name, value)

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def _update_item(self, name, value):
        if name in self and isinstance(self[name], dict):
            if isinstance(value, dict):
                new = self[name]
                new.update(value)
                super(Config, self).__setitem__(name, new)
                return True
        return False

    def update(self, data):
        self.is_valid(data)
        for key, value in data.items():
            if self._update_item(key, value):
                continue
            self[key] = value
