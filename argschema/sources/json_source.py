from .source import FileSource, FileSink
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
    ConfigSchema = JsonInputConfigSchema

    def __init__(self,input_json=None):
        self.filepath = input_json
    def read_file(self,fp):
        return json.load(fp)

class JsonSink(FileSink):
    ConfigSchema = JsonOutputConfigSchema

    def __init__(self,output_json=None):
        self.filepath = output_json
    
    def write_file(self,fp,d):
        json.dump(d,fp)
