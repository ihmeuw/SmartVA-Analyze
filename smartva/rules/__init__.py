def module_names():
    from os.path import dirname, basename, isfile
    import glob

    modules = glob.glob(dirname(__file__) + "/*.py")
    return [basename(f).replace('.py', '') for f in modules if isfile(f) and not basename(f).startswith('_')]


__all__ = module_names()

from . import *


def modules():
    return [globals().get(name) for name in __all__]
