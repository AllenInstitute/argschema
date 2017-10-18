'''sub-module for custom marshmallow fields of general utility'''
from marshmallow.fields import *
from marshmallow.fields import __all__ as __mmall__
from .files import OutputFile, InputDir, InputFile, OutputDir
from .numpyarrays import NumpyArray
from .deprecated import OptionList
from .loglevel import LogLevel
from .slice import Slice

__all__ = __mmall__ + ['OutputFile', 'InputDir', 'InputFile', 'OutputDir',
                       'NumpyArray', 'OptionList','LogLevel', 'Slice']

# Python 2 subpackage (not module) * imports break if items in __all__
# are unicode.
__all__ = list(map(str, __all__))
