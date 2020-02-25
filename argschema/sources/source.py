import abc
from typing import Dict, Type

import marshmallow as mm


class ConfigurationError(mm.ValidationError):
    """Base Exception class for configurations"""
    pass


class MisconfigurationError(ConfigurationError):
    """Exception when a configuration was present in part but failed
    validation"""
    pass


class NonconfigurationError(ConfigurationError):
    """Exception when a configuration is simply completely missing"""
    pass


class MultipleConfigurationError(ConfigurationError):
    """Exception when there is more than one valid configuration"""
    pass


def d_contains_any_fields(schema: mm.Schema, data: Dict) -> bool:
    """function to test if a dictionary contains any elements of a schema

    Parameters
    ----------
    schema: marshmallow.Schema
        a marshmallow schema to test d with
    data: dict
        the dictionary to test whether it contains any elements of a schema

    Returns
    -------
    bool:
        True/False whether d contains any elements of a schema. If a schema 
        contains no elements, returns True
    """

    if len(schema.declared_fields) == 0:
        return True

    for field_name, field in schema.declared_fields.items():
        if field_name in data.keys():
            if data[field_name] is not None:
                return True

    return False



class Configurable(object):
    """Base class for sources and sinks of marshmallow-validatable 
    parameters.

    Parameters
    ----------
    **default_config : dict
        Optionally, attempt to load a config immediately upon construction

    Attributes
    ----------
    ConfigSchema : type(mm.Schema), class attribute
        Defines a schema for this Configurable's config.
    config : dict
        Stores for values loaded according to this instance's schema
    schema : mm.Schema
        An instance of this class's ConfigSchema. Used to validate potential
        configurations. 

    """

    ConfigSchema: Type[mm.Schema] = mm.Schema

    def __init__(self, **default_config: Dict):

        self.schema: mm.Schema = self.ConfigSchema()
        self.config: Dict = {}

        if default_config:
            self.load_config(default_config)

    def load_config(self, candidate: Dict):
        """Attempt to configure this object inplace using values in a candidate 
        dictionary.

        Parameters
        ----------
        candidate : dict
            Might satisfy (and will be loaded using) this object's schema.

        Raises
        ------
        NonconfigurationError : Indicates that the candidate was completely 
            inapplicable.
        MisconfigurationError : Indicates that the candidate did not adequetly 
            satisfy this configurable's schema.

        """

        if candidate is None:
            candidate = {}

        if not d_contains_any_fields(self.schema, candidate):
            raise NonconfigurationError(
                "This source is not present in \n {}".format(candidate))

        try:
            self.config = self.schema.load(candidate, unknown=mm.EXCLUDE)
        except mm.ValidationError as e:
            raise MisconfigurationError(
                "Source incorrectly configured\n {}".format(e))       


class ConfigurableSource(Configurable):
    def get_dict(self) -> Dict:
        """Produces a dictionary, potentially using information from this 
        source's config.

        Returns
        -------
        dict : Suitable for validatation by some external marshmallow schema.

        """
        raise NotImplementedError()


class ConfigurableSink(Configurable):
    def put_dict(self, data: Dict):
        """Writes a dictionary, potentially using information from this 
        sink's config.

        Parameters
        ----------
        dict : Will be written to some external sink.

        """
        raise NotImplementedError()
