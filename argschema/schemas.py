import marshmallow as mm
from .fields import LogLevel, InputFile, OutputFile


class DefaultSchema(mm.Schema):
    """mm.Schema class with support for making fields default to
    values defined by that field's arguments.
    """

    @mm.pre_load
    def make_object(self, in_data):
        """marshmallow.pre_load decorated function for applying defaults on deserialation

        Parameters
        ----------
        in_data :
            

        Returns
        -------
        dict
            a dictionary with default values applied

        """
        for name, field in self.fields.items():
            if name not in in_data:
                if field.default is not mm.missing:
                    in_data[name] = field.default
        return in_data


class ArgSchema(DefaultSchema):
    """The base marshmallow schema used by ArgSchemaParser to identify
    input_json and output_json files and the log_level
    """

    input_json = InputFile(
        description= "file path of input json file")
    
    output_json = OutputFile(
        description= "file path to output json file")
    log_level = LogLevel(
        default='ERROR',
        description="set the logging level of the module")
