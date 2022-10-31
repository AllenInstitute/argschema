"""module that contains argschema functions for converting
marshmallow schemas to argparse and merging dictionaries from both systems
"""
import logging
import warnings
import ast
import argparse
from operator import add
import json
import marshmallow as mm
from argschema import fields
import collections

# explicit type mappings for field types that need them (default str)
FIELD_TYPE_MAP = {
    fields.Boolean: ast.literal_eval,
    fields.List: ast.literal_eval,
    fields.NumpyArray: ast.literal_eval,
}


def prune_dict_with_none(d):
    """function to remove all dictionaries from a nested dictionary
    when all the values of a particular dictionary are None

    Parameters
    ----------
    d: dictionary to prune

    Returns
    -------
    dict
        pruned dictionary
    """
    if all([d[key] is None for key in d.keys()]):
        return {}
    else:
        keys = [key for key in d.keys() if type(d[key]) == dict]
        for key in keys:
            pruned = prune_dict_with_none(d[key])
            if pruned == {}:
                d.pop(key)
    return d


def get_type_from_field(field):
    """Get type casting for command line argument from marshmallow.Field

    Parameters
    ----------
    field : marshmallow.Field
        Field class from input schema

    Returns
    -------
    callable
        Function to call to cast argument to
    """
    if isinstance(field, fields.List) and not field.metadata.get(
        "cli_as_single_argument", False
    ):
        return list
    else:
        return FIELD_TYPE_MAP.get(type(field), str)


def cli_error_dict(arg_path, field_type, index=0):
    """Constuct a nested dictionary containing a casting error message

    Matches the format of errors generated by schema.dump.

    Parameters
    ----------
    arg_path : string
        List of nested keys
    field_type : string
        Name of the marshmallow.Field type
    index : int
        Index into arg_path for recursion

    Returns
    -------
    dict
        Dictionary representing argument path, containing error.
    """
    if index == len(arg_path) - 1:
        return {
            arg_path[index]: [
                "Command-line argument can't cast to {}".format(field_type)
            ]
        }
    else:
        return {arg_path[index]: cli_error_dict(arg_path, field_type, index + 1)}


def args_to_dict(argsobj, schema=None):
    """function to convert namespace returned by argsparse into a nested dictionary

    Parameters
    ----------
    argsobj : argparse.Namespace
        Namespace object returned by standard argparse.parse function
    schema : marshmallow.Schema
        Optional schema which will be used to cast fields via `FIELD_TYPE_MAP`


    Returns
    -------
    dict
        dictionary of namespace values where nesting elements uses '.' to denote nesting of keys

    """
    d = {}
    argsdict = vars(argsobj)
    errors = {}
    field_def = None
    for field in argsdict.keys():
        current_schema = schema
        parts = field.split(".")
        root = d
        for i in range(len(parts)):
            if current_schema is not None:
                if current_schema.only and parts[i] not in current_schema.only:
                    field_def = None
                else:
                    field_def = current_schema.fields[parts[i]]
                if isinstance(field_def, fields.Nested):
                    current_schema = field_def.schema
            if i == (len(parts) - 1):
                value = argsdict.get(field)
                if value is not None:
                    try:
                        value = get_type_from_field(field_def)(value)
                    except ValueError:
                        typename = field_def.__class__.__name__
                        errors.update(cli_error_dict(parts, typename))
                root[parts[i]] = value
            else:
                if parts[i] not in root.keys():
                    root[parts[i]] = {}
                root = root[parts[i]]
    if errors:
        raise mm.ValidationError(json.dumps(errors, indent=2))
    return prune_dict_with_none(d)


def merge_value(a, b, key, func=add):
    """attempt to merge these dictionaries using function defined by
    func (default to add) raise an exception if this fails

    Parameters
    ----------
    a : dict
        one dictionary
    b : dict
        second dictionary
    key : key
        key to merge dictionary values on
    func : function(x
        function that merges two values of this key
        Returns (Default value = add)
    func : a[key]
        merged version of values (Default value = add)

    Returns
    -------
    value

    """
    try:
        return func(a[key], b[key])
    except ValueError:
        raise Exception(
            "Cannot merge this key {},\
         for values {} and {} of types {} and {}".format(
                key, a[key], b[key], type(a[key]), type(b[key])
            )
        )


def smart_merge(a, b, path=None, merge_keys=None, overwrite_with_none=False):
    """updates dictionary a with values in dictionary b
    being careful not to write things with None, and performing a merge on merge_keys

    Parameters
    ----------
    a : dict
        dictionary to perform update on
    b : dict
        dictionary to perform update with
    path : list
        list of nested keys traversed so far (used for recursion) (Default value = None)
    merge_keys : list
        list of keys to do merging on (default None)
    overwrite_with_none :
         (Default value = False)

    Returns
    -------
    dict
        a dictionary that is a updated with b's values

    """
    a = {} if a is None else a
    b = {} if b is None else b
    path = [] if path is None else path

    # simplifies code to have empty list rather than None
    # might allow some crazy dynamic merging in future
    if merge_keys is None:
        merge_keys = []

    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                # recursively merge these leafs
                smart_merge(a[key], b[key], path + [str(key)], merge_keys)
            elif a[key] == b[key]:
                pass  # same leaf value, so don't bother
            elif b[key] is None:
                if overwrite_with_none:
                    a[key] = b[key]
            else:
                # in this case we are potentially overwriting a's value with b's
                # determine if we should try to merge
                if key in merge_keys:
                    # attempt to merge leafs
                    a[key] = merge_value(a, b, key)
                else:  # otherwise replace leafs
                    a[key] = b[key]
        else:  # there is no corresponding leaf in a
            if b[key] is None:
                if overwrite_with_none:
                    a[key] = b[key]
            else:
                if isinstance(b[key], dict):
                    a[key] = {}
                    smart_merge(a[key], b[key], path + [str(key)], merge_keys)
                else:
                    # otherwise replace entire leaf with b
                    a[key] = b[key]
    return a


def get_description_from_field(field):
    """get the description for this marshmallow field

    Parameters
    ----------
    field : marshmallow.fields.field
        field to get description

    Returns
    -------
    str
        description string (or None)
    """
    # look for description
    if "description" in field.metadata:
        desc = field.metadata.get("description")
    # also look to see if description was added in metadata
    else:
        md = field.metadata.get("metadata", {})
        if "description" in md:
            desc = md["description"]
        else:
            desc = None
    return desc


def build_schema_arguments(schema, arguments=None, path=None, description=None):
    """given a jsonschema, create a dictionary of argparse arguments,
    by navigating down the Nested schema tree. (recursive function)

    Parameters
    ----------
    schema : marshmallow.Schema
        schema with field.description filled in with help values
    arguments : list or None
        list of argument group dictionaries to add to (see Returns) (Default value = None)
    path : list or None
        list of strings denoted where you are in the tree (Default value = None)
    description: str or None
        description for the argument group at this level of the tree

    Returns
    -------
    list
        List of argument group dictionaries, with keys ['title','description','args']
        which contain the arguments for argparse.  'args' is an OrderedDict of dictionaries
        with keys of the argument names with kwargs to build an argparse argument

    """
    path = [] if path is None else path
    arguments = [] if arguments is None else arguments
    arggroup = {}
    # name this argument group by the path, or the schema class name if it's the root
    if len(path) == 0:
        arggroup["title"] = schema.__class__.__name__
    else:
        arggroup["title"] = ".".join(path)
    arggroup["args"] = collections.OrderedDict()
    # assume the description has been handed down
    arggroup["description"] = description

    # sort the fields first by required, then by default values present or not
    for field_name, field in sorted(
        schema.declared_fields.items(),
        key=lambda x: 2 * x[1].required + 1 * (x[1].default == mm.missing),
        reverse=True,
    ):
        # get this field's description
        desc = get_description_from_field(field)

        # if its nested, then we want to recusively follow this link
        if isinstance(field, mm.fields.Nested):
            if field.many:
                logging.warning("many=True not supported from argparse")
            else:
                build_schema_arguments(
                    field.schema, arguments, path + [field_name], description=desc
                )
        elif isinstance(field, fields.Dict):
            logging.warning("setting Dict fields not supported from argparse")
        else:
            # it's not nested then let's build the argument
            arg = {}
            arg_name = "--" + ".".join(path + [field_name])
            if desc is not None:
                arg["help"] = desc
            else:
                arg["help"] = ""

            # programatically add helpful notes to help string
            if field.default is not mm.missing:
                arg["help"] += " (default={})".format(field.load_default)
            if field.required:
                arg["help"] += " (REQUIRED)"
            for validator in field.validators:
                if isinstance(validator, mm.validate.ContainsOnly):
                    arg["help"] += " (constrained list)"
                if isinstance(validator, mm.validate.OneOf):
                    arg["help"] += " (valid options are {})".format(validator.choices)

            if isinstance(field, mm.fields.List) and not field.metadata.get(
                "cli_as_single_argument", False
            ):
                warn_msg = (
                    "'{}' is using old-style command-line syntax with "
                    "each element as a separate argument. This will "
                    "not be supported in argschema after "
                    "2.0. See http://argschema.readthedocs.io/en/"
                    "master/user/intro.html#command-line-specification"
                    " for details."
                ).format(arg_name)
                warnings.warn(warn_msg, FutureWarning)
                arg["nargs"] = "*"

            # do type mapping after parsing so we can raise validation errors
            arg["type"] = str

            # DON'T WANT TO USE DEFAULT VALUES AS ARGPARSE OVERRULES JSON
            # if field.default != mm.missing:
            #    arg['default'] = field.default

            # add this argument to the arggroup
            arggroup["args"][arg_name] = arg

    # tack on this arggroup to the list and return
    arguments.append(arggroup)
    return arguments


def schema_argparser(schema):
    """given a jsonschema, build an argparse.ArgumentParser

    Parameters
    ----------
    schema : argschema.schemas.ArgSchema
        schema to build an argparser from

    Returns
    -------
    argparse.ArgumentParser
        the represents the schema

    """

    # build up a list of argument groups using recursive function
    # to traverse the tree, root node gets the description given by doc string
    # of the schema
    arguments = build_schema_arguments(schema, description=schema.__doc__)
    # make the root schema appeear first rather than last
    arguments = [arguments[-1]] + arguments[0:-1]

    parser = argparse.ArgumentParser()

    for arg_group in arguments:
        group = parser.add_argument_group(arg_group["title"], arg_group["description"])
        for arg_name, arg in arg_group["args"].items():
            group.add_argument(arg_name, **arg)
    return parser


def load(schema, d):
    """function to wrap marshmallow load to smooth
        differences from marshmallow 2 to 3

    Parameters
    ----------
    schema: marshmallow.Schema
        schema that you want to use to validate
    d: dict
        dictionary to validate and load

    Returns
    -------
    dict
        deserialized and validated dictionary

    Raises
    ------
    marshmallow.ValidationError
        if the dictionary does not conform to the schema
    """

    results = schema.load(d)

    return results


def dump(schema, d):
    """function to wrap marshmallow dump to smooth
        differences from marshmallow 2 to 3
    Parameters
    ----------
    schema: marshmallow.Schema
        schema that you want to use to validate and dump
    d: dict
        dictionary to validate and dump

    Returns
    -------
    dict
        serialized and validated dictionary

    Raises
    ------
    marshmallow.ValidationError
        if the dictionary does not conform to the schema
    """
    errors = schema.validate(d)
    if len(errors) > 0:
        raise mm.ValidationError(errors)

    return schema.dump(d)
