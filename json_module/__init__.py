import jsonschema, os, logging, argparse
import tempfile
import json
import argparse
from marshmallow import Schema, fields, pprint
from marshmallow_enum import EnumField
from marshmallow_jsonschema import JSONSchema
from enum import Enum
import stat


def args_to_dict(argsobj):
    d = {}
    argsdict = vars(argsobj)
    for field in argsdict.keys():
        parts = field.split('.')
        root = d
        for i in range(len(parts)):
            if i == (len(parts)-1):
                root[parts[i]]=argsdict.get(field,None)
            else:
                if parts[i] not in root.keys():
                    root[parts[i]]={}
                root=root[parts[i]]
    return d

def merge_value(a,b,key):
    #attempt to merge these keys, first pass use simple addition
    #raise an exception if this fails
    try:
        return a[key]+b[key]
    except:
        raise Exception("Cannot merge this key {},\
         for values {} and {} of types {} and {}".format\
         (key,a[key],b[key],type(a[key]),type(b[key])))

def do_join(a,b,key,merge_keys):
    #determine if we should/can attempt to merge a[key],b[key]
    #if merge_keys is not specified, then no
    if merge_keys is None:
        return False
    #only consider if key is in merge_keys
    if key in merge_keys:
       return True
    else:
        return False


def smart_merge(a, b, path=None,merge_keys = None,overwrite_with_none=False):
    "merges dictionary b into dictionary a\
    being careful not to write things with None"
    if a is None:
        return b
    if b is None:
        return a
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                #recursively merge these leafs
                smart_merge(a[key], b[key], path + [str(key)],merge_keys)
            elif a[key] == b[key]: pass # same leaf value, so don't bother
            elif b[key] is None: #b dictionary has no entry for key
                if overwrite_with_none:
                    a[key]=b[key]
                else: pass #then don't alter a's
            else:
                #in this case we are potentially overwriting a's value with b's   
                #determine if we should try to merge     
                if do_join(a,b,key,merge_keys):
                    #attempt to merge leafs
                    a[key]=merge_value(a,b,key)
                else: #otherwise replace leafs
                    a[key]=b[key]
        else: #there is no corresponding leaf in a
            if b[key] is None:
                if overwrite_with_none:
                    a[key]=b[key]
                else: pass #don't do anything because b's leaf is None
            else:
                #otherwise replace entire leaf with b
                a[key] = b[key]
    return a

import py
class InputFile(fields.Str):
    def _serialize(self,value,attr,obj):
        return str(value)
    def _deserialize(self,value,attr,data):
         return self._validated(value)
    def _validated(self,value):
        print 'value',value
        p = py.path.local(value)

        if not os.path.isfile(value):
            self.fail('invalid')
        else:
            try:
                os.access(value,os.R_OK)    
            except IOError:
                self.fail('invalid')
        return p
    def _jsonschema_type_mapping(self):
        return {
            'type': 'string',
            'format':'input_path',
            'description':self.metadata['metadata']['description']
        }
class EnumField(EnumField):

    def _jsonschema_type_mapping(self):
        return {
            'type': 'string',
            'enum':[val.name for val in self.enum],
            'description':self.metadata['metadata']['description']
        }

class LoggingEnum(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    WARNING = logging.WARNING

class ModuleParameters(Schema):
    input_json = InputFile(metadata={'description':"file path of input json file"})
    output_json = fields.Str(metadata={'description':"file path to output json file"})
    log_level = EnumField(LoggingEnum,metadata={'description':"set the logging level of the module"})

class ParseError(Exception):
    pass

class JsonModule():

    def __init__(self,
        input=None, #dictionary input as option instead of --input_json
        schema = ModuleParameters, #schema for parsing arguments
        json_validator = jsonschema.Draft4Validator,
        args = None,
        logger_name = 'json_module'): 

        schema = schema()
        result = JSONSchema().dump(schema)
        myjsonschema = result.data

        print json.dumps(myjsonschema,indent=4)
        #validate the schema
        #json_validator.check_schema(schema)
        self.myjsonschema = result.data

        #setup a validator with custom format checking
        checker = jsonschema.FormatChecker()
        checker.checks('input_path')(validate_input_path)
        validator = json_validator(myjsonschema,format_checker=checker)

        #convert schema to argparse object
        p = schema_argparser(myjsonschema)

        #use that parseargs object to parse command line inputs
        argsobj=p.parse_args(args)
        
        #convert the command line object into command line dictionary
        argsdict = args_to_dict(argsobj)

        #if input_json is not provided, use input
        if argsobj.input_json is None:
            if input is None: #if input is not provided 
                jsonargs = {} #the the json inputs are empty
            else:
                jsonargs = input
        #otherwise read in the json file from path
        else: 
            with open(argsobj.input_json,'r') as fp:
                jsonargs = json.load(fp)

        #merge the command line dictionary into the inputJson
        args = smart_merge(jsonargs,argsdict)
        result = schema.load(args)
        if len(result.errors)>0:
            raise ParseError(result.errors)

        self.args = result.data
        print result.errors
        #validate the combined dictionary against the validator    
        #validator.validate(self.args)

        #set the log level and initialize logger
        #set the log level and initialize logger
        print "*********"
        print "hey forrest I don't know why 'log_level' doesn't exist in self.args"
        print self.args
        print "*********"
        self.logger = self.initialize_logger(logger_name, self.args.get('log_level',None))

    @staticmethod
    def add_to_schema(oldschema,newschema,merge_keys=['required']):
        #merges the old schema into the new schema
        #presently the newschema strictly replaces
        #keys in the oldschema except for keys found in merge_keys
        return smart_merge(oldschema,newschema,merge_keys)

    @staticmethod
    def initialize_logger(name, log_level_enum):
        if log_level_enum is None:
            log_level_enum = LoggingEnum.ERROR
        
        level = logging.getLevelName(log_level_enum.name)

        logging.basicConfig()
        logger = logging.getLogger(name)
        logger.setLevel(level=level)
        return logger

    def run(self):
        print "running! with args"
        print json.dumps(self.args,indent=4)


# mapping from jsonschema types to python types
# I wonder if this lives somewhere in jsonschema already?
# NOTE: 'array' is intentionally left out as a special case
PROP_TYPE_CLASSES = {
    "integer": int,
    "number": float,
    "boolean": bool
}    

def build_schema_arguments(schema, arguments=None, path=None):
    """ given a jsonschema, create a dictionary of argparse arguments"""
    path = [] if path is None else path
    arguments = {} if arguments is None else arguments

    schema_props = schema.get('properties',{})
    required_props = schema.get('required',[])
    for prop_name, prop_info in schema_props.iteritems():
        prop_type = prop_info.get('type')

        # if this schema property is an object, recurse down
        if prop_type == 'object':
            build_schema_arguments(prop_info,
                                   arguments,
                                   path + [ prop_name ])
        else:
            # it's not an object, so build the argument
            arg = {}
            arg_name = '--' + '.'.join(path + [prop_name])

            if 'description' in prop_info:
                arg['help'] = prop_info['description']

            if prop_type in PROP_TYPE_CLASSES:
                # it's a simple type, apply the mapping
                arg['type'] = PROP_TYPE_CLASSES[prop_type]
            elif prop_type == 'array':
                # it's an array type -- try to be smart
                arg['nargs'] = '+'

                # if the "items" section is an object, the "type" sub-item 
                # indicates that the array elements should all have a single type
                items = prop_info.get("items")
                if isinstance(items, dict):
                    item_type = items.get("type")
                    if item_type in PROP_TYPE_CLASSES:
                        arg['type'] = PROP_TYPE_CLASSES[item_type]
                elif isinstance(items, list):
                    # the "items" section can also be a list, but this
                    # isn't supported by argparse AFAICT
                    raise Exception("hetergenous array item types not supported")

            arguments[arg_name] = arg

    return arguments

        
def schema_argparser(schema):
    """ given a jsonschema, build an argparse.ArgumentParser """

    arguments = build_schema_arguments(schema)

    parser = argparse.ArgumentParser(schema.get('description'))
    for arg_name, arg in arguments.iteritems():
        parser.add_argument(arg_name, **arg)
    return parser


#@jsonschema.FormatChecker.cls_checks('input_path', raises=IOError)
def validate_input_path(entry):
    if not os.path.exists(entry):
        #return False
        raise IOError("input_path '%s' does not exist" % entry)

    return True

def main():
    class renderParameters(Schema):
        host = fields.Str(metadata={'description':'render host'},required=True)
        port = fields.Int(metadata={'description':'render port'},required=True)
        owner = fields.Str(metadata={'description':'render owner'},required=True)
        project = fields.Str(metadata={'description':'render project'},required=True)

    class parameterExtension(ModuleParameters):
        a = fields.Int(metadata={'description':'value for a'},required=True)
        b = fields.Int(metadata={'description':'value for b'},required=True)
        render = fields.Nested(renderParameters)
        
    input ={'a':5}
    jm = JsonModule(input=input,schema=parameterExtension)


if __name__ == "__main__": main()



