'''sub-module for custom marshmallow fields of general utility'''
from marshmallow.fields import *
from marshmallow.fields import __all__
from .files import OutputFile, InputDir, InputFile
from .numpyarrays import NumpyArray
from .deprecated import OptionList
from .loglevel import LogLevel
from .slice import Slice

__all__ += ['OutputFile', 'InputDir', 'InputFile', 'NumpyArray', 'OptionList',
            'LogLevel', 'Slice']
