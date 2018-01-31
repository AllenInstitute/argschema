import yaml
from .source import FileSource,FileSink
import argschema
import marshmallow as mm

class YamlInputConfigSchema(mm.Schema):
    input_yaml = argschema.fields.InputFile(required=True, 
        description = 'filepath to input yaml')

class YamlOutputConfigSchema(mm.Schema):
    output_yaml = argschema.fields.OutputFile(required=True, 
        description = 'filepath to save output yaml')

class YamlSource(FileSource):
    ConfigSchema = YamlInputConfigSchema
    
    def __init__(self,input_yaml=None):
        self.filepath = input_yaml

    def read_file(self,fp):
        return yaml.load(fp)

class YamlSink(FileSink):
    ConfigSchema = YamlOutputConfigSchema

    def __init__(self,output_yaml=None):
        self.filepath = output_yaml

    def write_file(self,fp,d):
        yaml.dump(d,fp,default_flow_style=False)