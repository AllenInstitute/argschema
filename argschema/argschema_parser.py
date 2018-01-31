'''Module that contains the base class ArgSchemaParser which should be
subclassed when using this library
'''
import json
import logging
import copy
from . import schemas
from . import utils
import marshmallow as mm
from .sources.json_source import JsonSource, JsonSink
from .sources.yaml_source import YamlSource, YamlSink
from .sources.source import NotConfiguredSourceError

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


def get_input(Source,config_d):
    if config_d is not None:
        input_config_d = Source.get_config(Source.ConfigSchema,config_d)
        input_source = Source(**input_config_d)
        input_data = input_source.get_dict()
        return input_data
    else:
        raise NotConfiguredSourceError('No dictionary provided')
    

class ArgSchemaParser(object):
    """The main class you should sub-class to write your own argschema module.
    Takes input_data, reference to a input_json and the command line inputs and parses out the parameters
    and validates them against the schema_type specified.

    To subclass this and make a new schema be default, simply override the default_schema and default_output_schema
    attributes of this class.

    Parameters
    ----------
    input_data : dict or None
        dictionary parameters to fall back on if all source aren't present
    schema_type : schemas.ArgSchema
        the schema to use to validate the parameters
    output_schema_type : marshmallow.Schema
        the schema to use to validate the output_json, used by self.output
    input_source : argschema.sources.source.Source
        a generic source of a dictionary
    output_source : argschema.sources.source.Source
        a generic output to put output dictionary
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
    input_config_map = [ JsonSource ]
    output_config_map = [ JsonSink ]

    def __init__(self,
                 input_data=None,  # dictionary input as option instead of --input_json
                 schema_type=None,  # schema for parsing arguments
                 output_schema_type = None, # schema for parsing output_json
                 args=None,
                 input_source = None,
                 output_sink = None,
                 logger_name=__name__):
        
        if schema_type is None:
            schema_type = self.default_schema
        if output_schema_type is None:
            output_schema_type = self.default_output_schema
        
        self.schema = schema_type()
        self.logger = self.initialize_logger(logger_name,'WARNING')
        self.logger.debug('input_data is {}'.format(input_data))

        # convert schema to argparse object

        #consolidate a list of the input and output source
        #command line configuration schemas
        io_schemas = []
        for in_cfg in self.input_config_map:
            io_schemas.append(in_cfg.ConfigSchema())
        for out_cfg in self.output_config_map:
            io_schemas.append(out_cfg.ConfigSchema())

        #build a command line parser from the input schemas and configurations
        p = utils.schema_argparser(self.schema,io_schemas)
        argsobj = p.parse_args(args)
        argsdict = utils.args_to_dict(argsobj, self.schema)
        self.logger.debug('argsdict is {}'.format(argsdict))

        #if you received an input_source, get the dictionary from there
        if input_source is not None:
            input_data = input_source.get_dict()
        else: #see if the input_data itself contains an InputSource configuration use that
            for InputSource in self.input_config_map:
                try: 
                    input_data = get_input(InputSource,input_data)
                except NotConfiguredSourceError as e:
                    pass

        #loop over the set of input_configurations to see if the command line arguments
        # include a valid configuration for an input_source
        for InputSource in self.input_config_map:
            try:
                input_data = get_input(InputSource,argsdict)
            #if the command line argument dictionary doesn't contain a valid configuration
            #simply move on to the next one
            except NotConfiguredSourceError as e:
                pass

        # merge the command line dictionary into the input json
        args = utils.smart_merge(input_data, argsdict)
        self.logger.debug('args after merge {}'.format(args))

        # if the output source was not passed in, see if there is a configuration in the combined args
        if output_sink is None: 
            for OutputSink in self.output_config_map:
                try: 
                    output_config_d = OutputSink.get_config(OutputSink.ConfigSchema,args)
                    output_sink = OutputSink(**output_config_d)
                except NotConfiguredSourceError:
                    pass
        # save the output source for later
        self.output_sink = output_sink
        # validate with load!
        result = self.load_schema_with_defaults(self.schema, args)
        if len(result.errors) > 0:
            raise mm.ValidationError(json.dumps(result.errors, indent=2))

        self.schema_args = result
        self.args = result.data
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
            (output_json,errors)=schema.dump(d)
            if len(errors)>0:
                raise mm.ValidationError(json.dumps(errors))
        else:
            self.logger.warning("output_schema_type is not defined,\
                                 the output won't be validated")
            output_json = d
        
        return output_json

    def output(self,d,output_path=None,sink=None,**sink_options):
        """method for outputing dictionary to the output_json file path after
        validating it through the output_schema_type

        Parameters
        ----------
        d:dict
            output dictionary to output 
        sink: argschema.sources.source.ArgSink
            output_sink to output to (optional default to self.output_source)
        output_path: str
            path to save to output file, optional (with default to self.mod['output_json'] location)
        **sink_options :
            will be passed through to sink.put_dict
         
            (DEPRECATED path to save to output file, optional (with default to self.mod['output_json'] location)
        Raises
        ------
        marshmallow.ValidationError
            If any of the output dictionary doesn't meet the output schema
        """
        
        output_d = self.get_output_json(d)
        if output_path is not None:
            self.logger.warning('DEPRECATED, pass sink instead')
            sink = JsonSink(output_json=output_path)
        if sink is not None:
            sink.put_dict(output_d)
        else:
            self.output_sink.put_dict(output_d,**sink_options)

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
        result = schema.load(args)

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

class ArgSchemaYamlParser(ArgSchemaParser):
    input_config_map = [YamlSource]
    output_config_map = [YamlSink]