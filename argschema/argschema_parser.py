'''Module that contains the base class ArgSchemaParser which should be
subclassed when using this library
'''
import json
import logging
from . import schemas
from . import utils
from . import fields
import marshmallow as mm
from .sources.json_source import JsonSource, JsonSink
from .sources.yaml_source import YamlSource, YamlSink
from .sources.source import NotConfiguredSourceError, MultipleConfiguredSourceError


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
    output_sink : argschema.sources.source.Source
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
    default_configurable_sources = [ JsonSource ]
    default_configurable_sinks = [ JsonSink ]

    def __init__(self,
                 input_data=None,  # dictionary input as option instead of --input_json
                 schema_type=None,  # schema for parsing arguments
                 output_schema_type=None,  # schema for parsing output_json
                 args=None,
                 input_source=None,
                 output_sink=None,
                 logger_name=__name__):

        if schema_type is None:
            schema_type = self.default_schema
        if output_schema_type is None:
            output_schema_type = self.default_output_schema

        self.schema = schema_type()
        self.logger = self.initialize_logger(logger_name, 'WARNING')
        self.logger.debug('input_data is {}'.format(input_data))

        # convert schema to argparse object

        # consolidate a list of the input and output source
        # command line configuration schemas
        io_schemas = []
        for in_cfg in self.default_configurable_sources:
            io_schemas.append(in_cfg.ConfigSchema())
        for out_cfg in self.default_configurable_sinks:
            io_schemas.append(out_cfg.ConfigSchema())

        # build a command line parser from the input schemas and configurations
        p = utils.schema_argparser(self.schema, io_schemas)
        argsobj = p.parse_args(args)
        argsdict = utils.args_to_dict(argsobj, self.schema)
        self.logger.debug('argsdict is {}'.format(argsdict))

        # if you received an input_source, get the dictionary from there
        if input_source is not None:
            input_data = input_source.get_dict()
        else:  # see if the input_data itself contains an InputSource configuration use that
            config_data = self.__get_input_data_from_config(input_data)
            input_data = config_data if config_data is not None else input_data

        # check whether the command line arguments contain an input configuration and use that
        config_data = self.__get_input_data_from_config(argsdict)
        input_data = config_data if config_data is not None else input_data

        # merge the command line dictionary into the input json
        args = utils.smart_merge(input_data, argsdict)
        self.logger.debug('args after merge {}'.format(args))

        # if the output sink was not passed in, see if there is a configuration in the combined args
        if output_sink is None: 
            output_sink = self.__get_output_sink_from_config(args)     
        # save the output sink for later
        self.output_sink = output_sink

        # validate with load!
        result = self.load_schema_with_defaults(self.schema, args)

        self.args = result
        self.output_schema_type = output_schema_type
        self.logger = self.initialize_logger(
            logger_name, self.args.get('log_level'))

    def __get_output_sink_from_config(self,d):
        """private function to check for ArgSink configuration in a dictionary and return a configured ArgSink

        Parameters
        ----------
        d : dict
            dictionary to look for ArgSink Configuration parameters in
        
        Returns
        -------
        ArgSink
            A configured argsink

        Raises
        ------
        MultipleConfiguredSourceError
            If more than one Sink is configured
        """
        output_set = False
        output_sink = None
        for OutputSink in self.default_configurable_sinks:
                try: 
                    output_config_d = OutputSink.get_config(OutputSink.ConfigSchema,d)
                    if output_set:
                        raise MultipleConfiguredSourceError("more then one OutputSink configuration present in {}".format(d))
                    output_sink = OutputSink(**output_config_d)
                    output_set=True
                except NotConfiguredSourceError:
                    pass
        return output_sink
    
    def __get_input_data_from_config(self,d):
        """private function to check for ArgSource configurations in a dictionary
        and return the data if it exists

        Parameters
        ----------
        d : dict
            dictionary to look for InputSource configuration parameters in

        Returns
        -------
        dict or None
            dictionary of InputData if it found a valid configuration, None otherwise
        
        Raises
        ------
        MultipleConfiguredSourceError
            if more than one InputSource is configured
        """
        input_set = False
        input_data = None
        for InputSource in self.default_configurable_sources:
            try: 
                input_data = get_input(InputSource, d)
                if input_set:
                    raise MultipleConfiguredSourceError("more then one InputSource configuration present in {}".format(d))
                input_set = True
            except NotConfiguredSourceError as e:
                pass
        return input_data

    def get_output_json(self, d):
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
            output_json = utils.dump(schema, d)
        else:
            self.logger.warning("output_schema_type is not defined,\
                                 the output won't be validated")
            output_json = d

        return output_json

    def output(self, d, output_path=None, sink=None, **sink_options):
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
            self.output_sink.put_dict(output_d, **sink_options)

    def load_schema_with_defaults(self, schema, args):
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


class ArgSchemaYamlParser(ArgSchemaParser):
    input_config_map = [YamlSource]
    output_config_map = [YamlSink]
