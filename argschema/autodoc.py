from schemas import ArgSchema
import fields
import marshmallow as mm
from utils import get_description_from_field
from argschema_parser import ArgSchemaParser
import inspect

FIELD_TYPE_MAP = {v: k for k, v in mm.Schema.TYPE_MAPPING.items()}

def process_schemas(app, what, name, obj, options, lines):

    if what == "class":
        if issubclass(obj,ArgSchemaParser):
            lines.append("   This class takes a ArgSchema as an input to parse inputs")
            (args,vargs,varkw,defaults)=inspect.getargspec(obj.__init__)
            def_schema = defaults[1].__module__+'.'+defaults[1].__name__
            lines.append("   This class's default ArgSchema is of type :class:`{}`".format(def_schema))
            lines.append("")
        if issubclass(obj,ArgSchema):
            lines.append("   This schema is designed to be a schema_type for an ArgSchemaParser object")
            lines.append("")
        if issubclass(obj,mm.Schema):
            schema = obj()
            lines.append("Schema:")
            for field_name, field in schema.declared_fields.items():
                
                field_line = "  :%s: "%field_name
                try:
                    if isinstance(field, mm.fields.List):
                        base_types = inspect.getmro(type(field.container))
                    else:
                        base_types = inspect.getmro(type(field))
                  
                    if isinstance(field,mm.fields.Nested):
                        raw_type = 'dict(:class:`~{}`)'.format(type(field.schema).__name__)
                    else:
                        try:
                            base_type=next(bt for bt in base_types if bt in FIELD_TYPE_MAP)
                            raw_type=FIELD_TYPE_MAP[base_type].__name__
                        except:
                            raw_type = '?'
                    field_line += "(:class:`{}.{}` : {}) ".format(type(field).__module__,type(field).__name__,raw_type)
                except:
                    field_line += "fail "
                description = get_description_from_field(field)
                if description is not None:
                    field_line+=description
                else:
                    field_line+="no description "
                if field.required:
                    field_line += " REQUIRED "
                if field.default is not mm.missing:
                    field_line += " (default = {})".format(field.default)
                lines.append(field_line)
            