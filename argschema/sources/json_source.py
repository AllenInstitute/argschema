from argschema.sources.source import ConfigurableSource, ConfigurableSink
import json
import marshmallow as mm
import argschema


class JsonInputConfigSchema(mm.Schema):
    input_json = argschema.fields.InputFile(required=True,
        description='filepath to input_json')


class JsonOutputConfigSchema(mm.Schema):
    output_json = argschema.fields.OutputFile(required=True,
        description='filepath to save output_json')
    output_json_indent = argschema.fields.Int(required=False,
        description='whether to indent options or not')


class JsonSource(ConfigurableSource):
    """ A configurable source which reads values from a json. Expects 
        --input_json
    to be specified.
    """

    ConfigSchema = JsonInputConfigSchema

    def get_dict(self):
        with open(self.config["input_json"], 'r') as fp:
            return json.load(fp,)


class JsonSink(ConfigurableSink):
    """ A configurable sink which writes values to a json. Expects 
        --output_json
    to be specified.
    """
    ConfigSchema = JsonOutputConfigSchema

    def put_dict(self, data):
        with open(self.config["output_json"], 'w') as fp:
            json.dump(
                data, fp, indent=self.config.get("output_json_indent", None))
