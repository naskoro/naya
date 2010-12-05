from . import NayaBit as Module, Naya as App
from .jinja import JinjaModuleMixin, JinjaMixin


class NayaBit(Module, JinjaModuleMixin):
    pass


class Naya(App, JinjaModuleMixin, JinjaMixin):
    module_class = NayaBit
