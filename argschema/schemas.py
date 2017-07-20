import marshmallow as mm
from .fields import LogLevel, InputFile, OutputFile


class DefaultSchema(mm.Schema):
    """Schema class with support for making fields default to
    values defined by that field's arguments.
    """

    @mm.pre_load
    def make_object(self, in_data):
        for name, field in self.fields.items():
            if name not in in_data:
                if field.default is not None:
                    in_data[name] = field.default
        return in_data


class ArgSchema(DefaultSchema):
    """The base marshmallow schema used by ArgSchemaParser to identify
    input and output json files
    and the log_level
    """

    input_json = InputFile(
        metadata={'description': "file path of input json file"})
    output_json = OutputFile(
        metadata={'description': "file path to output json file"})
    log_level = LogLevel(
        default='ERROR', metadata={
            'description': "set the logging level of the module"})
