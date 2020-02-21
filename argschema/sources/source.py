import abc
from typing import Dict

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


def d_contains_any_fields(schema, d):
    """function to test if a dictionary contains any elements of a schema

    Parameters
    ----------
    schema: marshmallow.Schema
        a marshmallow schema to test d with
    d: dict
        the dictionary to test whether it contains any elements of a schema

    Returns
    -------
    bool:
        True/False whether d contains any elements of a schema. If a schema contains no elements, returns True
    """

    if len(schema.declared_fields) == 0:
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

    def __init__(self, **kwargs):
        """Configurable source

        Parameters
        ----------
        **kwargs: dict
            a set of keyword arguments which will be validated by this classes ConfigSchema
            which will define the set of fields that are allowed (and their defaults)
        """
        self.schema = self.ConfigSchema()
        self.config = {}

    def load_config(self, candidate: Dict):
        """
        """

        if candidate is None:
            raise NotConfiguredSourceError("No data was provided")

        if not d_contains_any_fields(self.schema, candidate):
            raise NotConfiguredSourceError(
                "This source is not present in \n {}".format(candidate))

        try:
            self.config = self.schema.load(candidate, unknown=mm.EXCLUDE)
        except mm.ValidationError as e:
            raise MisconfiguredSourceError(
                "Source incorrectly configured\n {}".format(e))       


class ArgSource(ConfigurableSource):
    def get_dict(self):
        """method that must be implemented to enable an ArgSource to return a dictionary"""


class ArgSink(ConfigurableSource):
    def put_dict(self, d):
        """method that must be implemented to enable an ArgSink to write a dictionary

        Parameters
        ----------
        d: dict
            the dictionary to write
        """
