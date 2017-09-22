from argschema.schemas import ArgSchema
import marshmallow as mm
from argschema.utils import get_description_from_field
from argschema.argschema_parser import ArgSchemaParser
import inspect

FIELD_TYPE_MAP = {v: k for k, v in mm.Schema.TYPE_MAPPING.items()}


def process_schemas(app, what, name, obj, options, lines):
    """function designed to process a :mod:`sphinx.ext.autodoc`
    event as autodoc hook to alter docstring lines of
    argschema related classes, providing a table of parameters for schemas
    and links to the default schemas for ArgSchemaParser derived elements

    use in sphnix conf.py as follows

    ::

        from argschema.autodoc import process_schemas
        def setup(app):
            app.connect('autodoc-process-docstring',process_schemas)
    """

    if what == "class":
        # pick out the ArgSchemaParser objects for documenting
        if issubclass(obj, ArgSchemaParser):
            # inspect the objects init function to find default schema
            (args, vargs, varkw, defaults) = inspect.getargspec(obj.__init__)
            # find where the schema_type is as a keyword argument
            schema_index = next(i for i, arg in enumerate(
                args) if arg == 'schema_type')
            # use its default value to construct the string version of the classpath to the module
            def_schema = defaults[schema_index - 1]

            def_schema = def_schema or obj.default_schema
            if def_schema is not None:
                def_schema_name = def_schema.__module__ + '.' + def_schema.__name__
            def_schema_name = def_schema_name or 'None'

            # append to the documentation
            lines.append(".. note::")
            lines.append(
                "  This class takes a ArgSchema as an input to parse inputs")
            lines.append(
                "  , with a default schema of type :class:`~{}`".format(def_schema_name))
            lines.append("")
        if issubclass(obj, ArgSchema):
            # add a special note to ArgSchema's
            lines.append(
                "   This schema is designed to be a schema_type for an ArgSchemaParser object")
            lines.append("")
        if issubclass(obj, mm.Schema):
            # but document all mm.Schema's
            schema = obj()
            if len(schema.declared_fields) > 0:
                lines.append(".. csv-table:: %s" % obj.__name__)
                lines.append(
                    '   :header: "key", "description", "default","field_type","json_type"')
                lines.append('   :widths: 30, 80, 30, 30, 30')
                lines.append('')

                # #loop over the declared fields for this schema
                for field_name, field in schema.declared_fields.items():
                    # we will build up the documentation line for each field
                    # start declaring the key as field_name like a parameter
                    field_line = "    %s," % field_name

                    # get the description of this field and add it to documentation
                    description = get_description_from_field(field)

                    description = description or "no description"
                    description = description.replace('\"', "'")
                    field_line += '"%s",' % description

                    if field.default is not mm.missing:
                        # add in the default value if there is one
                        default = '"{}",'.format(field.default)
                        field_line += default
                    elif field.required:
                        field_line += '(REQUIRED),'
                    else:
                        field_line += "NA,"

                    # add this field line to the documentation
                    try:
                        # get the set of types this field was derived from
                        if isinstance(field, mm.fields.List):
                            # if it's a list we want to do this for its container
                            base_types = inspect.getmro(type(field.container))
                        else:
                            base_types = inspect.getmro(type(field))

                        field_type = type(field)
                        # use these base_types to figure out the raw_json type for this field
                        if isinstance(field, mm.fields.Nested):
                            # if it's a nested field we should specify it as a dict, and link to the documentation
                            # for that nested schema
                            # = type
                            #schema_type = type(field.schema)
                            field_type = type(field.schema)
                            #schema_class_name = schema_type.__module__ + "." + schema_type.__name__
                            if field.many == True:
                                raw_type = 'list'
                            else:
                                raw_type = 'dict'
                        else:
                            # otherwise we should be able to look it up in the FIELD_TYPE_MAP
                            try:
                                base_type = next(
                                    bt for bt in base_types if bt in FIELD_TYPE_MAP)
                                raw_type = FIELD_TYPE_MAP[base_type].__name__
                                # hack in marshmallow for py3 which things Str is type 'bytes'
                                if raw_type == 'bytes':
                                    raw_type = 'str'
                            except:
                                # if its not in the FIELD_TYPE_MAP, we aren't sure what type it is
                                # TODO handle this more elegantly/and/or patch up more use cases
                                raw_type = '?'
                        field_line += ":class:`~{}.{}`,{}".format(
                            field_type.__module__, field_type.__name__, raw_type)
                    except:
                        # in case this fails for some reason, note it as unknown
                        # TODO handle this more elegantly, identify and patch up such cases
                        field_line += "unknown,unknown"
                    lines.append(field_line)
                # lines.append(table_line)
