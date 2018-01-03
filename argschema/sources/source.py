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

class MultipleConfiguredSourceError(ConfigurableSourceError):
    """Exception when there is more than one validly configured Source configured"""
    pass

def d_contains_any_fields(schema,d):
    if len(schema.declared_fields)==0:
        return True
    for field_name, field in schema.declared_fields.items():
        if field_name in d.keys():
            if d[field_name] is not None:
                return True        
    return False

class ConfigSourceSchema(mm.Schema):
    pass

class ConfigurableSource(object):
    ConfigSchema = ConfigSourceSchema
    def __init__(self,**kwargs):
        """Configurable source 

        Parameters
        ----------
        **kwargs: dict
            a set of keyword arguments which will be validated by this classes ConfigSchema
            which will define the set of fields that are allowed (and their defaults)
        """
        schema = self.ConfigSchema()
        result = self.get_config(self.ConfigSchema,kwargs)
        self.__dict__.update(result)
            
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

def get_input_from_config(ArgSource, config_d):
    if config_d is not None:
        input_config_d = ArgSource.get_config(ArgSource.ConfigSchema, config_d)
        input_source = ArgSource(**input_config_d)
        input_data = input_source.get_dict()
        return input_data
    else:
        raise NotConfiguredSourceError('No dictionary provided')

class ArgSink(ConfigurableSource):
    def put_dict(self,d):
        pass