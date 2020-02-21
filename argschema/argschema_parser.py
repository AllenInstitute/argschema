'''Module that contains the base class ArgSchemaParser which should be
subclassed when using this library
'''
from typing import List, Sequence, Dict, Optional, Union
import logging
from . import schemas
from . import utils
import marshmallow as mm
from .sources.json_source import JsonSource, JsonSink
from .sources.yaml_source import YamlSource, YamlSink
from .sources.source import (
    ArgSource,
    ArgSink,
    NotConfiguredSourceError, 
    MultipleConfiguredSourceError, 
)


class ArgSchemaParser(object):
    """The main class you should sub-class to write your own argschema module.
    Takes input_data, reference to a input_json and the command line inputs and parses out the parameters
    and validates them against the schema_type specified.

    To subclass this and make a new schema be default, simply override the default_schema and default_output_schema
    attributes of this class.

    Parameters
    ----------
    input_data : dict or None
        dictionary parameters to fall back on if not source is given or configured via command line
    schema_type : schemas.ArgSchema
        the schema to use to validate the parameters
    output_schema_type : marshmallow.Schema
        the schema to use to validate the output, used by self.output
    input_sources : Sequence[argschema.sources.source.ConfigurableSource]
        Each of these will be considered 
    output_sinks : Sequence[argschema.sources.source.ConfigurableSource]
        a generic sink to write output dictionary to
    args : list or None
        command line arguments passed to the module, if None use argparse to parse the command line,
        set to [] if you want to bypass command line parsing
    logger_name : str
        name of logger from the logging module you want to instantiate default ('argschema')

    Raises
    -------
    marshmallow.ValidationError
        If the combination of input_json, input_data and command line arguments do not pass
        the validation of the schema

    """
    default_schema = schemas.ArgSchema
    default_output_schema = None
    default_sources = (JsonSource,)
    default_sinks = (JsonSink,)

    @property
    def input_sources(self) -> List[ArgSource]:
        if not hasattr(self, "_input_sources"):
            self._input_sources = []
        return self._input_sources

    @property
    def output_sinks(self) -> List[ArgSource]:
        if not hasattr(self, "_output_sinks"):
            self._output_sinks = []
        return self._output_sinks

    @property
    def io_schemas(self) -> List[mm.Schema]:
        if not hasattr(self, "_io_schemas"):
            self._io_schemas = []
        return self._io_schemas

    @io_schemas.setter
    def io_schemas(self, schemas: List[mm.Schema]):
        self._io_schemas = schemas

    def __init__(self,
                 input_data=None,  # dictionary input as option instead of --input_json
                 schema_type=None,  # schema for parsing arguments
                 output_schema_type=None,  # schema for parsing output_json
                 args=None,
                 input_sources=None,
                 output_sinks=None,
                 logger_name=__name__):

        if schema_type is None:
            schema_type = self.default_schema
        if output_schema_type is None:
            output_schema_type = self.default_output_schema

        self.schema = schema_type()
        self.logger = self.initialize_logger(logger_name, 'WARNING')
        self.logger.debug('input_data is {}'.format(input_data))

        self.register_sources(input_sources)
        self.register_sinks(output_sinks)

        argsdict = self.parse_command_line(args)
        resolved_args = self.resolve_inputs(input_data, argsdict)

        self.output_sink = self.__get_output_sink_from_config(resolved_args)
        self.args = self.load_schema_with_defaults(self.schema, resolved_args)

        self.output_schema_type = output_schema_type
        self.logger = self.initialize_logger(
            logger_name, self.args.get('log_level'))

    def register_sources(
        self, 
        sources: Union[None, Sequence[ArgSource], ArgSource]
    ):
        """consolidate a list of the input and output source command line 
        configuration schemas
        """

        if isinstance(sources, (ArgSource, type)):
            sources = [sources]
        elif sources is None:
            sources = self.default_sources


        for source in sources:
            if isinstance(source, type):
                source = source()
            self.io_schemas.append(source.schema)
            self.input_sources.append(source)

    def register_sinks(
        self, 
        sinks: Union[None, Sequence[ArgSink], ArgSink]
    ):
        """
        """

        if isinstance(sinks, (ArgSink, type)):
            sinks = [sinks]
        elif sinks is None:
            sinks = self.default_sinks

        for sink in sinks:
            if isinstance(sink, type):
                sink = sink()
            self.io_schemas.append(sink.schema)
            self.output_sinks.append(sink)

    def parse_command_line(self, args: Optional[List]):
        """ build a command line parser from the input schemas and 
        configurations
        """
        parser = utils.schema_argparser(self.schema, self.io_schemas)
        argsobj = parser.parse_args(args)
        argsdict = utils.args_to_dict(argsobj, [self.schema] + self.io_schemas)
        self.logger.debug('argsdict is {}'.format(argsdict))
        return argsdict

    def resolve_inputs(self, input_data: Dict, argsdict: Dict) -> Dict:
        """ Resolve input source by checking candidate sources against 
        constructor and command line arguments
        """

        config_data = self.__get_input_data_from_config(input_data)
        if config_data is not None:
            input_data = config_data

        config_data = self.__get_input_data_from_config(
            utils.smart_merge({}, argsdict))
        if config_data is not None:
            input_data = config_data

        args = utils.smart_merge(input_data, argsdict)
        self.logger.debug('args after merge {}'.format(args))

        return args

    def __get_output_sink_from_config(self, d):
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
        for sink in self.output_sinks:
            try:
                sink.load_config(d)
                
                if output_set:
                    raise MultipleConfiguredSourceError(
                        "more then one OutputSink configuration present in {}".format(d))
                output_sink = sink
                output_set = True
            except NotConfiguredSourceError:
                pass
        return output_sink

    def __get_input_data_from_config(self, d):
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
        for source in self.input_sources:
            try:
                source.load_config(d)
                input_data = source.get_dict()
                if input_set:
                    raise MultipleConfiguredSourceError(
                        "more then one InputSource configuration present in {}".format(d))
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
            errors = schema.validate(d)
            if len(errors)>0:
                raise(mm.ValidationError(errors))
            output_json = utils.dump(schema, d)
        else:
            self.logger.warning("output_schema_type is not defined,\
                                 the output won't be validated")
            output_json = d

        return output_json

    def output(self, d, sink=None):
        """method for outputing dictionary to the output_json file path after
        validating it through the output_schema_type

        Parameters
        ----------
        d:dict
            output dictionary to output
        sink: argschema.sources.source.ArgSink
            output_sink to output to (optional default to self.output_source)

        Raises
        ------
        marshmallow.ValidationError
            If any of the output dictionary doesn't meet the output schema
        """

        output_d = self.get_output_json(d)
        if sink is not None:
            sink.put_dict(output_d)
        else:
            self.output_sink.put_dict(output_d)

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
    default_sources = [YamlSource]
    default_sinks = [YamlSink]
