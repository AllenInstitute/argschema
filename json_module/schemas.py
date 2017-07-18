import marshmallow as mm
from .fields import OptionList, InputFile, OutputFile
from .loglevel import LogLevel
import logging


class ModuleParameters(mm.Schema):
    '''The base marshmallow schema used by JsonModule to identify input and
    output json files
    and the log_level
    '''
    input_json = InputFile(
        metadata={'description': "file path of input json file"})
    output_json = OutputFile(
        metadata={'description': "file path to output json file"})
    log_level = LogLevel()

