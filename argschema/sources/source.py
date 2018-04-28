import json
import marshmallow as mm

class Source(object):
    InputConfigSchema = None
    OutputConfigSchema = None

    def __init__(self):
        pass

    def get_dict(self):
        pass
    
    def put_dict(self,d):
        pass

    @staticmethod
    def get_config(Schema,d):
        schema = Schema()
        result,errors = schema.load(d)
        if len(errors)>0:
            raise mm.ValidationError(json.dumps(errors, indent=2))
        return result

class FileSource(Source):

    def __init__(self,filepath):
        self.filepath = filepath

    def get_dict(self):
        with open(self.filepath,'r') as fp:
            d = self.read_file(fp)
        return d
    
    def put_dict(self,d):
        with open(self.filepath,'w') as fp:
            self.write_file(fp,d)

    def read_file(self,fp):
        pass

    def write_file(self,fp,d):
        pass

