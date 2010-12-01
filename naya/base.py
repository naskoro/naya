from . import BaseModule, BaseApp
from .jinja import JinjaModuleMixin, JinjaMixin
from .shortcut import ShortcutMixin


class Module(BaseModule, JinjaModuleMixin):
    pass


class App(BaseApp, ShortcutMixin, JinjaModuleMixin, JinjaMixin):
    pass


