import os, logging, argparse
import tempfile
import json
import argparse, copy
import marshmallow as mm

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

class OutputFile(mm.fields.Str):
    def _validate(self,value):
        try:
            path = os.path.split(value)[0]
        except:
            raise mm.ValidationError("%s cannot be os.path.split"%value)

        if not os.path.isdir(path):
            raise mm.ValidationError("%s is not in a directory that exists"%value)

        try:
            tfile = tempfile.TemporaryFile(mode='w',dir=path)
            tfile.write('0')
            tfile.close()
        except:
            raise mm.ValidationError("%s does not appear you can write to path"%value)


class InputDir(mm.fields.Str):
    def _validate(self,value):
        if not os.path.isdir(value):
            raise mm.ValidationError("%s is not a directory")
        else:
            try:
                os.access(value,os.R_OK)
            except:
                raise mm.ValidationError("%s is not a readable directory"%value)

class InputFile(mm.fields.Str):

    def _validate(self,value):
        if not os.path.isfile(value):
            raise mm.ValidationError("%s is not a file" % value)
        else:
            try:
                os.access(value,os.R_OK)    
            except IOError:
                raise mm.ValidationError("%s is not readable" % value)

class OptionList(mm.fields.Field):
    def __init__(self, options, *args, **kwargs):
        self.options = options
        super(OptionList, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        return value

    def _validate(self,  value):
        if value not in self.options:
            raise mm.ValidationError("%s is not a valid option" % value)

        return value

class ModuleParameters(mm.Schema):
    input_json = InputFile(metadata={'description':"file path of input json file"})
    output_json = OutputFile(metadata={'description':"file path to output json file"})
    log_level = OptionList([ 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' ],
                           metadata={'description':"set the logging level of the module"},
                           default='ERROR')

class JsonModule( object ):
    def __init__(self,
        input_data = None, #dictionary input as option instead of --input_json
        schema_type = ModuleParameters, #schema for parsing arguments
        args = None,
        logger_name = 'json_module'): 

        schema = schema_type()
        
        #convert schema to argparse object
        p = schema_argparser(schema)
        argsobj = p.parse_args(args)
        argsdict = args_to_dict(argsobj)

        if argsobj.input_json is not None:
            result = schema.load(argsdict)
            if 'input_json' in result.errors:
                raise mm.ValidationError(result.errors['input_json'])
            jsonargs = json.load(open(result.data['input_json'], 'r'))
        else:
            jsonargs = input_data if input_data else {}

        #merge the command line dictionary into the input json
        args = smart_merge(jsonargs, argsdict)

        # validate with load!
        result = self.load_schema_with_defaults(schema, args)

        if len(result.errors)>0:
            raise mm.ValidationError(json.dumps(result.errors, indent=2))

        self.schema_args = result
        self.args = result.data

        self.logger = self.initialize_logger(logger_name, self.args.get('log_level'))

    @staticmethod
    def load_schema_with_defaults(schema, args):
        defaults = []

        # find all of the schema entries with default values
        schemas = [ (schema, []) ]
        while schemas:
            subschema, path = schemas.pop()
            for k,v in subschema.declared_fields.iteritems():
                if isinstance(v, mm.fields.Nested):
                    schemas.append((v.schema, path + [ k ]))
                elif v.default != mm.missing:
                    defaults.append((path + [ k ], v.default))

        # put the default entries into the args dictionary
        args = copy.deepcopy(args)
        for path, val in defaults:
            d = args
            for path_item in path[:-1]:
                d = d.setdefault(path_item, {})
            if path[-1] not in d:
                d[path[-1]] = val

        # load the dictionary via the schema
        result = schema.load(args)

        return result

    @staticmethod
    def initialize_logger(name, log_level):
        level = logging.getLevelName(log_level)

        logging.basicConfig()
        logger = logging.getLogger(name)
        logger.setLevel(level=level)
        return logger

    def run(self):
        print "running! with args"
        print json.dumps(self.args,indent=4)

FIELD_TYPE_MAP = { v:k for k,v in mm.Schema.TYPE_MAPPING.iteritems()}

def build_schema_arguments(schema, arguments=None, path=None):
    """ given a jsonschema, create a dictionary of argparse arguments"""
    path = [] if path is None else path
    arguments = {} if arguments is None else arguments

    for field_name, field in schema.declared_fields.iteritems():
        if isinstance(field, mm.fields.Nested):
            build_schema_arguments(field.schema,
                                   arguments,
                                   path + [ field_name ])
        else:
            # it's not an object, so build the argument
            arg = {}
            arg_name = '--' + '.'.join(path + [field_name])

            md = field.metadata.get('metadata',{})
            if 'description' in md:
                arg['help'] = md['description']

            field_type = type(field)
            if isinstance(field_type, mm.fields.List):
                raise NotImplementedError("fields.List is not a supported type, YET")
            elif type(field) in FIELD_TYPE_MAP:
                # it's a simple type, apply the mapping
                arg['type'] = FIELD_TYPE_MAP[field_type]

            #if field.default != mm.missing:
            #    arg['default'] = field.default

            arguments[arg_name] = arg

    return arguments
        
def schema_argparser(schema):
    """ given a jsonschema, build an argparse.ArgumentParser """

    arguments = build_schema_arguments(schema)

    parser = argparse.ArgumentParser()
    
    for arg_name, arg in arguments.iteritems():
        parser.add_argument(arg_name, **arg)
    return parser


def main():
    jm = JsonModule()
    print jm.args

if __name__ == "__main__": main()



