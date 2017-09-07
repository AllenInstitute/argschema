from argschema.schemas import ArgSchema
import marshmallow as mm
from argschema.utils import get_description_from_field
from argschema.argschema_parser import ArgSchemaParser
import inspect

FIELD_TYPE_MAP = {v: k for k, v in mm.Schema.TYPE_MAPPING.items()}

def process_schemas(app, what, name, obj, options, lines):

    if what == "class":
        #pick out the ArgSchemaParser objects for documenting
        if issubclass(obj,ArgSchemaParser):
            #inspect the objects init function to find default schema
            (args,vargs,varkw,defaults)=inspect.getargspec(obj.__init__)
            #find where the schema_type is as a keyword argument
            schema_index = next(i for i,arg in enumerate(args) if arg=='schema_type')
            #use its default value to construct the string version of the classpath to the module
            def_schema = defaults[schema_index-1].__module__+'.'+defaults[schema_index-1].__name__
            #append to the documentation
            lines.append(".. note::")
            lines.append("  This class takes a ArgSchema as an input to parse inputs")
            lines.append("  , with a default schema of type :class:`{}`".format(def_schema))
            lines.append("")
        if issubclass(obj,ArgSchema):
            #add a special note to ArgSchema's
            lines.append("   This schema is designed to be a schema_type for an ArgSchemaParser object")
            lines.append("")
        if issubclass(obj,mm.Schema):
            #but document all mm.Schema's
            schema = obj()
            lines.append(".. note::")
            lines.append("")
            lines.append("  keys: (field_type \: raw_type) description")

            #loop over the declared fields for this schema
            for field_name, field in schema.declared_fields.items():
                #we will build up the documentation line for each field
                #start declaring the key as field_name like a parameter
                field_line = "    :%s: "%field_name
                try:
                    #get the set of types this field was derived from
                    if isinstance(field, mm.fields.List):
                        #if it's a list we want to do this for its container
                        base_types = inspect.getmro(type(field.container))
                    else:
                        base_types = inspect.getmro(type(field))
                  
                    #use these base_types to figure out the raw_json type for this field
                    if isinstance(field,mm.fields.Nested):
                        #if it's a nested field we should specify it as a dict, and link to the documentation 
                        #for that nested schema
                        if field.many == True:
                           raw_type = 'list[:class:`~{}`]'.format(type(field.schema).__name__)
                        else:
                           raw_type = 'dict(:class:`~{}`)'.format(type(field.schema).__name__)
                    else:
                        #otherwise we should be able to look it up in the FIELD_TYPE_MAP
                        try:
                            base_type=next(bt for bt in base_types if bt in FIELD_TYPE_MAP)
                            raw_type=FIELD_TYPE_MAP[base_type].__name__
                        except:
                            #if its not in the FIELD_TYPE_MAP, we aren't sure what type it is
                            #TODO handle this more elegantly/and/or patch up more use cases
                            raw_type = '?'
                    field_line += "(:class:`{}.{}` : {}) ".format(type(field).__module__,type(field).__name__,raw_type)
                except:
                    #in case this fails for some reason, note it as unknown
                    #TODO handle this more elegantly, identify and patch up such cases
                    field_line += " (unknown) "

                #get the description of this field and add it to documentation
                description = get_description_from_field(field)
                if description is not None:
                    field_line+=description
                else:
                    #if there is no description note that
                    field_line+="no description "
                if field.required:
                    #add a REQUIRED stamp to required fields
                    field_line += " REQUIRED "
                if field.default is not mm.missing:
                    #add in the default value if there is one
                    field_line += " (default = {})".format(field.default)
                #add this field line to the documentation
                lines.append(field_line)
            