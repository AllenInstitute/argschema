import yaml
from argschema.sources.source import ArgSource, ArgSink
import argschema
import marshmallow as mm


class YamlInputConfigSchema(mm.Schema):
    input_yaml = argschema.fields.InputFile(required=True,
        description='filepath to input yaml')


class YamlOutputConfigSchema(mm.Schema):
    output_yaml = argschema.fields.OutputFile(required=True,
        description='filepath to save output yaml')


class YamlSource(ArgSource):
    ConfigSchema = YamlInputConfigSchema

    def get_dict(self):
        with open(self.config["input_yaml"], 'r') as fp:
            return yaml.load(fp)


class YamlSink(ArgSink):
    ConfigSchema = YamlOutputConfigSchema

    def put_dict(self, d):
        with open(self.config["output_yaml"], 'w') as fp:
            yaml.dump(d, fp, default_flow_style=False)
