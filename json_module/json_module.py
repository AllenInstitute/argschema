import json
import logging
from . import schemas
import copy
from .utils import args_to_dict, smart_merge, schema_argparser
import marshmallow as mm

class JsonModule( object ):
    def __init__(self,
        input_data = None, #dictionary input as option instead of --input_json
        schema_type = schemas.ModuleParameters, #schema for parsing arguments
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
            for k,v in subschema.declared_fields.items():
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
        print("running! with args")
        print(json.dumps(self.args,indent=4))

