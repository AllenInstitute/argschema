from .source import FileSource
import json
import marshmallow as mm
import argschema

class JsonInputConfigSchema(mm.Schema):
    input_json = argschema.fields.InputFile(required=True,
        description = 'filepath to input_json')

class JsonOutputConfigSchema(mm.Schema):
    output_json = argschema.fields.OutputFile(required=True,
        description = 'filepath to save output_json')

class JsonSource(FileSource):
    InputConfigSchema = JsonInputConfigSchema
    OutputConfigSchema = JsonOutputConfigSchema
    def __init__(self,input_json=None, output_json=None):
        if input_json is not None:
            self.filepath = input_json
        if output_json is not None:
            self.filepath = output_json

    def read_file(self,fp):
        return json.load(fp)
    
    def write_file(self,fp,d):
        json.dump(d,fp)
