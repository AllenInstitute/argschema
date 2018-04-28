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
        result = self.get_config(self.ConfigSchema, kwargs)
        self.__dict__.update(result)

    @staticmethod
    def get_config(ConfigSchema, d):
        """A static method to get the proper validated configuration keyword arguments/dictionary
        of a Configurable source from a dictionary

        Parameters
        ----------
        ConfigSchema: marshmallow.Schema
            a marshmallow schema that defines the configuration schema for this ConfigurableSource
        d: dict
            a dictionary that might contain a proper configuration of this schema

        Returns
        -------
        dict
            a dictionary of configuration values that has been properly deserialized and validated by
            ConfigSchema
        Raises
        ------
        NotConfiguredSourceError
            if the configation dictionary does not contain a configuration for this source
        MisconfiguredSourceError
            if the configuration dictionary contains a configuration but it is invalid
        """
        schema = ConfigSchema()
        if not d_contains_any_fields(schema, d):
            raise NotConfiguredSourceError(
                "This source is not present in \n {}".format(d))
        else:
            result, errors = schema.load(d)
            if len(errors) > 0:
                raise MisconfiguredSourceError(
                    "Source incorrectly configured\n {}".format(errors))
            else:
                return result


class ArgSource(ConfigurableSource):
    def get_dict(self):
        """method that must be implemented to enable an ArgSource to return a dictionary"""
        pass


def get_input_from_config(ArgSource, config_d):
    """function to return the input dictionary from an ArgSource, given a configuration dictionary

    Parameters
    ----------
    ArgSource: class(ArgSource)
        The ArgSource class subclass that you want to get input from
    config_d: a dictionary that might contain a configuration for this source

    Returns
    -------
    dict
        a dictionary returned by ArgSource.get_dict() after validating configuration
        and instantiating an ArgSource instance

    Raises
    ------
    NotConfiguredSourceError
        if the configation dictionary does not contain a configuration for this source
    MisconfiguredSourceError
        if the configuration dictionary contains a configuration but it is invalid
    """
    if config_d is not None:
        input_config_d = ArgSource.get_config(ArgSource.ConfigSchema, config_d)
        input_source = ArgSource(**input_config_d)
        input_data = input_source.get_dict()
        return input_data
    else:
        raise NotConfiguredSourceError('No dictionary provided')


class ArgSink(ConfigurableSource):
    def put_dict(self, d):
        """method that must be implemented to enable an ArgSink to write a dictionary

        Parameters
        ----------
        d: dict
            the dictionary to write
        """
        pass
