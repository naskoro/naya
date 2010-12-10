from . import NayaBit as _NayaBit, Naya as _Naya
from .jinja import JinjaModuleMixin, JinjaMixin


class NayaBit(_NayaBit, JinjaModuleMixin):
    pass


class Naya(_Naya, JinjaModuleMixin, JinjaMixin):
    module_class = NayaBit
