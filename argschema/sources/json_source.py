from .source import ArgSource, ArgSink
import json
import marshmallow as mm
import argschema

class JsonInputConfigSchema(mm.Schema):
    input_json = argschema.fields.InputFile(required=True,
        description = 'filepath to input_json')

class JsonOutputConfigSchema(mm.Schema):
    output_json = argschema.fields.OutputFile(required=True,
        description = 'filepath to save output_json')

class JsonSource(ArgSource):
    ConfigSchema = JsonInputConfigSchema
    
    def get_dict(self):
        with open(self.input_json,'r') as fp:
            return json.load(fp)

class JsonSink(ArgSink):
    ConfigSchema = JsonOutputConfigSchema

    def put_dict(self,d):
        with open(self.output_json,'w') as fp:
            json.dump(d,fp)

