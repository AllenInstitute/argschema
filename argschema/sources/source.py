import json
import marshmallow as mm

class ConfigurableSourceError(mm.ValidationError):
    """Base Exception class for configurable sources"""
    pass

class MisconfiguredSourceError(ConfigurableSourceError):
    """Exception when a source configuration was present in part but failed
    validation"""
    pass

class NotConfiguredSourceError(ConfigurableSourceError):
    """Exception when the source configuration is simply completely missing"""
    pass

def d_contains_any_fields(schema,d):
    for field_name, field in schema.declared_fields.items():
        if field_name in d.keys():
            if d[field_name] is not None:
                return True        
    return False

class ConfigurableSource(object):
    ConfigSchema = None
    @staticmethod
    def get_config(Schema,d):
        schema = Schema()
        if not d_contains_any_fields(schema,d):
            raise NotConfiguredSourceError("This source is not present in \n" + json.dumps(d, indent=2))
        else:
            result,errors = schema.load(d)   
            if len(errors)>0:
                raise MisconfiguredSourceError("Source incorrectly configured\n" + json.dumps(errors, indent=2))
            else:
                return result

class ArgSource(ConfigurableSource):
    def get_dict(self):
        pass

class ArgSink(ConfigurableSource):
    def put_dict(self,d):
        pass

class FileSource(ArgSource):

    def get_dict(self):
        with open(self.filepath,'r') as fp:
            d = self.read_file(fp)
        return d

    def read_file(self,fp):
        pass

class FileSink(ArgSink):

    def write_file(self,fp,d):
        pass

    def put_dict(self,d):
        with open(self.filepath,'w') as fp:
            self.write_file(fp,d)