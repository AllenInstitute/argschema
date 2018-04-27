'''sub-module for custom marshmallow fields of general utility'''
from marshmallow.fields import *  # noQA:F401
from marshmallow.fields import __all__ as __mmall__ # noQA:F401
from .files import OutputFile, InputDir, InputFile, OutputDir # noQA:F401
from .numpyarrays import NumpyArray # noQA:F401
from .deprecated import OptionList # noQA:F401
from .loglevel import LogLevel # noQA:F401
from .slice import Slice # noQA:F401

__all__ = __mmall__ + ['OutputFile', 'InputDir', 'InputFile', 'OutputDir',
                       'NumpyArray', 'OptionList', 'LogLevel', 'Slice']

# Python 2 subpackage (not module) * imports break if items in __all__
# are unicode.
__all__ = list(map(str, __all__))
