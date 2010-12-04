from . import BaseModule, App as BaseApp
from .jinja import JinjaModuleMixin, JinjaMixin


class Module(BaseModule, JinjaModuleMixin):
    pass


class App(BaseApp, JinjaModuleMixin, JinjaMixin):
    pass
