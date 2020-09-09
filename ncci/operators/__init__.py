"""operators -- define operators for obmixer and h2mixer input

    - 09/08/20 (pjf): Created, migrating from operators.py
"""
import deprecated as __deprecated

from . import ob, tb

################################################################
# import from tb but mark as deprecated
################################################################
import importlib as __importlib
__tb_module = __importlib.import_module('.tb', __name__)

# is there an __all__?  if so respect it
if "__all__" in __tb_module.__dict__:
    __names = __tb_module.__dict__["__all__"]
else:
    # otherwise we import all names that don't begin with _
    __names = [x for x in __tb_module.__dict__ if not x.startswith("_")]

# decorate the items as they get pulled into the namespace
globals().update({
    k: __deprecated.deprecated(getattr(__tb_module, k), action="always", reason="use tb namespace")
    for k in __names
    })