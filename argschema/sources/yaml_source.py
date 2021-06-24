import yaml
from argschema.sources.source import ConfigurableSource, ConfigurableSink
import argschema
import marshmallow as mm


class YamlInputConfigSchema(mm.Schema):
    input_yaml = argschema.fields.InputFile(required=True,
        description='filepath to input yaml')


class YamlOutputConfigSchema(mm.Schema):
    output_yaml = argschema.fields.OutputFile(required=True,
        description='filepath to save output yaml')


class YamlSource(ConfigurableSource):
    """ A configurable source which reads values from a yaml. Expects 
        --input_yaml
    to be specified.
    """
    ConfigSchema = YamlInputConfigSchema

    def get_dict(self):
        with open(self.config["input_yaml"], 'r') as fp:
            return yaml.load(fp, Loader=yaml.FullLoader)


class YamlSink(ConfigurableSink):
    """ A configurable sink which writes values to a yaml. Expects 
        --output_yaml
    to be specified.
    """
    ConfigSchema = YamlOutputConfigSchema

    def put_dict(self, data):
        with open(self.config["output_yaml"], 'w') as fp:
            yaml.dump(data, fp, default_flow_style=False)
