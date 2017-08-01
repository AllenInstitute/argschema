'''module that contains argschema functions for converting
marshmallow schemas to argparse and merging dictionaries from both systems
'''
import logging
import argparse
from operator import add
import inspect
import marshmallow as mm
import collections
FIELD_TYPE_MAP = {v: k for k, v in mm.Schema.TYPE_MAPPING.items()}


def args_to_dict(argsobj):
    """function to convert namespace returned by argsparse into a nested dictionary

    Parameters
    ----------
    argsobj : argparse.Namespace
        Namespace object returned by standard argparse.parse function


    Returns
    -------
    dict
        dictionary of namespace values where nesting elements uses '.' to denote nesting of keys

    """
    d = {}
    argsdict = vars(argsobj)
    for field in argsdict.keys():
        parts = field.split('.')
        root = d
        for i in range(len(parts)):
            if i == (len(parts) - 1):
                root[parts[i]] = argsdict.get(field)
            else:
                if parts[i] not in root.keys():
                    root[parts[i]] = {}
                root = root[parts[i]]
    return d


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

    """
    try:
        return func(a[key], b[key])
    except:
        raise Exception("Cannot merge this key {},\
         for values {} and {} of types {} and {}".format
                        (key, a[key], b[key], type(a[key]), type(b[key])))


def do_join(a, b, key, merge_keys=None):
    """determine if we should/can attempt to merge a[key],b[key]
    if merge_keys is not specified, then no

    Parameters
    ----------
    a :

    b :

    key :

    merge_keys :
         (Default value = None)

    Returns
    -------

    """
    if merge_keys is None:
        return False
    # only consider if key is in merge_keys
    return key in merge_keys


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
                if do_join(a, b, key, merge_keys):
                    # attempt to merge leafs
                    a[key] = merge_value(a, b, key)
                else:  # otherwise replace leafs
                    a[key] = b[key]
        else:  # there is no corresponding leaf in a
            if b[key] is None:
                if overwrite_with_none:
                    a[key] = b[key]
            else:
                # otherwise replace entire leaf with b
                a[key] = b[key]
    return a


def build_schema_arguments(schema, arguments=None, path=None):
    """given a jsonschema, create a dictionary of argparse arguments (recursive function)

    Parameters
    ----------
    path :
        list or None (Default value = None)
    schema :
        marshmallow schema with metadata['description'] filled in with help values
    arguments :
        (Default value = None)

    Returns
    -------
    collections.OrderedDict
        OrderedDict of dictionaries with kwargs to build argparse arguments

    """
    path = [] if path is None else path
    arguments = collections.OrderedDict() if arguments is None else arguments

    for field_name, field in schema.declared_fields.items():
        if isinstance(field, mm.fields.Nested):
            if field.many:
                logging.warning("many=True not supported from argparse")
            else:
                build_schema_arguments(field.schema,
                                       arguments,
                                       path + [field_name])
        else:
            # it's not an object, so build the argument
            arg = {}
            arg_name = '--' + '.'.join(path + [field_name])

            md = field.metadata.get('metadata', {})
            if 'description' in md:
                arg['help'] = md['description']
            #also look to see if description was added a kwarg
            else:
                if 'description' in field.metadata:
                    arg['help'] = field.metadata.get('description')

            field_type = type(field)
            if isinstance(field, mm.fields.List):
                arg['nargs'] = '*'
                container_type = type(field.container)

                parent_classes = inspect.getmro(container_type)[1:]

                # recurse to up the class tree to find out if this is a supported type
                while (container_type not in FIELD_TYPE_MAP and
                       len(parent_classes)):
                    container_type = parent_classes[0]
                    parent_classes = parent_classes[1:]

                if container_type in FIELD_TYPE_MAP:
                    arg['type'] = FIELD_TYPE_MAP[container_type]
                else:
                    logging.warning("List contains unsupported type: %s" % str(
                        type(field.container)))
            elif type(field) in FIELD_TYPE_MAP:
                # it's a simple type, apply the mapping
                arg['type'] = FIELD_TYPE_MAP[field_type]

            # if field.default != mm.missing:
            #    arg['default'] = field.default

            arguments[arg_name] = arg

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

    arguments = build_schema_arguments(schema)

    parser = argparse.ArgumentParser()

    for arg_name, arg in arguments.items():
        parser.add_argument(arg_name, **arg)
    return parser
