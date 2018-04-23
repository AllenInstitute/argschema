'''Module that contains the base class ArgSchemaParser which should be
subclassed when using this library
'''
import json
import logging
import copy
from . import schemas
from . import utils
from . import fields
import marshmallow as mm


def contains_non_default_schemas(schema, schema_list=[]):
    """returns True if this schema contains a schema which was not an instance of DefaultSchema

    Parameters
    ----------
    schema : marshmallow.Schema
        schema to check
    schema_list :
         (Default value = [])

    Returns
    -------
    bool
        does this schema only contain schemas which are subclassed from schemas.DefaultSchema

    """
    if not isinstance(schema, schemas.DefaultSchema):
        return True
    for k, v in schema.declared_fields.items():
        if isinstance(v, mm.fields.Nested):
            if type(v.schema) in schema_list:
                return False
            else:
                schema_list.append(type(v.schema))
                if contains_non_default_schemas(v.schema, schema_list):
                    return True
    return False


def is_recursive_schema(schema, schema_list=[]):
    """returns true if this schema contains recursive elements

    Parameters
    ----------
    schema : marshmallow.Schema
        schema to check
    schema_list :
         (Default value = [])

    Returns
    -------
    bool
        does this schema contain any recursively defined schemas

    """
    for k, v in schema.declared_fields.items():
        if isinstance(v, mm.fields.Nested):
            if type(v.schema) in schema_list:
                return True
            else:
                schema_list.append(type(v.schema))
                if is_recursive_schema(v.schema, schema_list):
                    return True
    return False


def fill_defaults(schema, args):
    """DEPRECATED, function to fill in default values from schema into args
    bug: goes into an infinite loop when there is a recursively defined schema

    Parameters
    ----------
    schema : marshmallow.Schema
        schema to get defaults from
    args :
        

    Returns
    -------
    dict
        dictionary with missing default values filled in

    """

    defaults = []

    # find all of the schema entries with default values
    schemata = [(schema, [])]
    while schemata:
        subschema, path = schemata.pop()
        for k, v in subschema.declared_fields.items():
            if isinstance(v, mm.fields.Nested):
                schemata.append((v.schema, path + [k]))
            elif v.default != mm.missing:
                defaults.append((path + [k], v.default))

    # put the default entries into the args dictionary
    args = copy.deepcopy(args)
    for path, val in defaults:
        d = args
        for path_item in path[:-1]:
            d = d.setdefault(path_item, {})
        if path[-1] not in d:
            d[path[-1]] = val
    return args


class ArgSchemaParser(object):
    """The main class you should sub-class to write your own argschema module.
    Takes input_data, reference to a input_json and the command line inputs and parses out the parameters
    and validates them against the schema_type specified.

    To subclass this and make a new schema be default, simply override the default_schema and default_output_schema
    attributes of this class.

    Parameters
    ----------
    input_data : dict or None
        dictionary parameters instead of --input_json
    schema_type : schemas.ArgSchema
        the schema to use to validate the parameters
    output_schema_type : marshmallow.Schema
        the schema to use to validate the output_json, used by self.output
    args : list or None
        command line arguments passed to the module, if None use argparse to parse the command line, set to [] if you want to bypass command line parsing
    logger_name : str
        name of logger from the logging module you want to instantiate 'argschema'

    Raises
    -------
    marshmallow.ValidationError
        If the combination of input_json, input_data and command line arguments do not pass
        the validation of the schema

    """
    default_schema = schemas.ArgSchema
    default_output_schema = None

    def __init__(self,
                 input_data=None,  # dictionary input as option instead of --input_json
                 schema_type=None,  # schema for parsing arguments
                 output_schema_type = None, # schema for parsing output_json
                 args=None,
                 logger_name=__name__):
        
        if schema_type is None:
            schema_type = self.default_schema
        if output_schema_type is None:
            output_schema_type = self.default_output_schema

        self.schema = schema_type()
        self.logger = self.initialize_logger(logger_name,'WARNING')
        self.logger.debug('input_data is {}'.format(input_data))

        # convert schema to argparse object
        p = utils.schema_argparser(self.schema)
        argsobj = p.parse_args(args)
        argsdict = utils.args_to_dict(argsobj, self.schema)
        self.logger.debug('argsdict is {}'.format(argsdict))

        if argsobj.input_json is not None:
            fields.files.validate_input_path(argsobj.input_json)
            with open(argsobj.input_json, 'r') as j:
                jsonargs = json.load(j)
        else:
            jsonargs = input_data if input_data else {}

        # merge the command line dictionary into the input json
        args = utils.smart_merge(jsonargs, argsdict)
        self.logger.debug('args after merge {}'.format(args))

        # validate with load!
        result = self.load_schema_with_defaults(self.schema, args)

        self.args = result
        self.output_schema_type = output_schema_type
        self.logger = self.initialize_logger(
            logger_name, self.args.get('log_level'))

    def get_output_json(self,d):
        """method for getting the output_json pushed through validation
        if validation exists
        Parameters
        ----------
        d:dict
            output dictionary to output 

        Returns
        -------
        dict
            validated and serialized version of the dictionary
        
        Raises
        ------
        marshmallow.ValidationError
            If any of the output dictionary doesn't meet the output schema
        """
        if self.output_schema_type is not None:
            schema = self.output_schema_type()
            output_json = utils.dump(schema,d)
        else:
            self.logger.warning("output_schema_type is not defined,\
                                 the output won't be validated")
            output_json = d
        
        return output_json

    def output(self,d,output_path=None,**json_dump_options):
        """method for outputing dictionary to the output_json file path after
        validating it through the output_schema_type

        Parameters
        ----------
        d:dict
            output dictionary to output 
        output_path: str
            path to save to output file, optional (with default to self.mod['output_json'] location)
        **json_dump_options :
            will be passed through to json.dump
         
        Raises
        ------
        marshmallow.ValidationError
            If any of the output dictionary doesn't meet the output schema
        """
        if output_path is None:
            output_path = self.args['output_json']
        
        output_json = self.get_output_json(d)
        with open(output_path,'w') as fp:
            json.dump(output_json,fp,**json_dump_options)

    def load_schema_with_defaults(self  ,schema, args):
        """method for deserializing the arguments dictionary (args)
        given the schema (schema) making sure that the default values have
        been filled in.

        Parameters
        ----------
        args : dict
            a dictionary of input arguments
        schema :
            

        Returns
        -------
        dict
            a deserialized dictionary of the parameters converted through marshmallow
        
        Raises
        ------
        marshmallow.ValidationError
            If this schema contains nested schemas that don't subclass argschema.DefaultSchema
            because these won't work with loading defaults.

        """
        is_recursive = is_recursive_schema(schema)
        is_non_default = contains_non_default_schemas(schema)
        if (not is_recursive) and is_non_default:
            # throw a warning
            self.logger.warning("""DEPRECATED:You are using a Schema which contains 
            a Schema which is not subclassed from argschema.DefaultSchema, 
            default values will not work correctly in this case, 
            this use is deprecated, and future versions will not fill in default 
            values when you use non-DefaultSchema subclasses""")
            args = fill_defaults(schema, args)
        if is_recursive and is_non_default:
            raise mm.ValidationError(
                'Recursive schemas need to subclass argschema.DefaultSchema else defaults will not work')

        # load the dictionary via the schema
        result = utils.load(schema, args)

        return result

    @staticmethod
    def initialize_logger(name, log_level):
        """initializes the logger to a level with a name
        logger = initialize_logger(name, log_level)

        Parameters
        ----------
        name : str
            name of the logger
        log_level :
            

        Returns
        -------
        logging.Logger
            a logger set with the name and level specified

        """
        level = logging.getLevelName(log_level)

        logging.basicConfig()
        logger = logging.getLogger(name)
        logger.setLevel(level=level)
        return logger
