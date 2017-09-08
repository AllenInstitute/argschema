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
    
    #simplifies code to have empty list rather than None
    #might allow some crazy dynamic merging in future
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
    #look for description
    if 'description' in field.metadata:
            desc = field.metadata.get('description')
    #also look to see if description was added in metadata
    else:
        md = field.metadata.get('metadata', {})
        if 'description' in md:
            desc = md['description']
        else:
            desc = None
    return desc
            
def build_schema_arguments(schema, arguments=None, path=None, description =None):
    """given a jsonschema, create a dictionary of argparse arguments,
    by navigating down the Nested schema tree. (recursive function) 

    Parameters
    ----------
    schema : marshamallow.schema.Schema
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
    #name this argument group by the path, or the schema class name if it's the root
    if len(path)==0:
        arggroup['title']=schema.__class__.__name__
    else:
        arggroup['title']='.'.join(path)
    arggroup['args']=collections.OrderedDict()
    #assume the description has been handed down
    arggroup['description']=description

    #sort the fields first by required, then by default values present or not
    for field_name, field in sorted(schema.declared_fields.items(),
                                    key= lambda x: 2*x[1].required+1*(x[1].default==mm.missing),
                                    reverse=True):
        #get this field's description
        desc = get_description_from_field(field)

        #if its nested, then we want to recusively follow this link
        if isinstance(field, mm.fields.Nested):
            if field.many:
                logging.warning("many=True not supported from argparse")
            else:
                build_schema_arguments(field.schema,
                                       arguments,
                                       path + [field_name],
                                       description = desc)
        else:
            # it's not nested then let's build the argument
            arg = {}
            arg_name = '--' + '.'.join(path + [field_name])
            if desc is not None:
                arg['help']=desc
            else:
                arg['help']=''

            #programatically add helpful notes to help string
            if field.default is not mm.missing:
                arg['help']+= " (default={})".format(field.default)
            if field.required:
                arg['help']+= " (REQUIRED)"
            for validator in field.validators:
                if isinstance(validator,mm.validate.ContainsOnly):
                    arg['help']+= " (constrained list)"
                if isinstance(validator,mm.validate.OneOf):
                    arg['help']+= " (valid options are {})".format(validator.choices)

            #catch lists to figure out desired type
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
            #otherwise look up the desired type in FIELD_TYPE_MAP
            elif type(field) in FIELD_TYPE_MAP:
                # it's a simple type, apply the mapping
                arg['type'] = FIELD_TYPE_MAP[field_type]

            #DON'T WANT TO USE DEFAULT VALUES AS ARGPARSE OVERRULES JSON
            # if field.default != mm.missing:
            #    arg['default'] = field.default

            #add this argument to the arggroup
            arggroup['args'][arg_name] = arg
    
    #tack on this arggroup to the list and return
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

    #build up a list of argument groups using recursive function
    #to traverse the tree, root node gets the description given by doc string
    #of the schema
    arguments = build_schema_arguments(schema,description=schema.__doc__)
    #make the root schema appeear first rather than last
    arguments = [arguments[-1]]+arguments[0:-1]

    parser = argparse.ArgumentParser()

    for arg_group in arguments:
        group=parser.add_argument_group(arg_group['title'],arg_group['description'])
        for arg_name,arg in arg_group['args'].items():
            group.add_argument(arg_name, **arg)
    return parser
