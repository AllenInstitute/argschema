import marshmallow as mm
from .fields import OptionList, InputFile, OutputFile


class ArgSchema(mm.Schema):
    '''The base marshmallow schema used by ArgSchemaParser to identify input and
    output json files
    and the log_level
    '''
    input_json = InputFile(
        metadata={'description': "file path of input json file"})
    output_json = OutputFile(
        metadata={'description': "file path to output json file"})
    log_level = OptionList(
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='ERROR', metadata={
            'description': "set the logging level of the module"})
