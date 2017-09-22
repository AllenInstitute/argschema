import argschema
import marshmallow as mm

class NestedSchema(argschema.schemas.DefaultSchema):
    aint = argschema.fields.Int(required=False, default =5, description="a integer")
    bstr = argschema.fields.Str(required=True, 
                                validate=mm.validate.OneOf(["a","b","c"]),
                                description = "a string")
    cstr = argschema.fields.Str(required=True, 
                            validate=mm.validate.ContainsOnly(["true","false","maybe"]),
                            description = "a list of whether statements are true/false/maybe")                        

class MySchema(argschema.ArgSchema):
    """my set of parameters"""
    nest = argschema.fields.Nested(NestedSchema, required=True, description="nested schema")
    topint = argschema.fields.Int(required=True,description="a top integer")
    topintb = argschema.fields.Int(default=5,required=False,description="a top integer b")
    topintc = argschema.fields.Int(required=True,description="a top integer c")
    topintd = argschema.fields.Int(default=7,required=False,description="a top integer d")

if __name__ == '__main__':
    mod = argschema.ArgSchemaParser(schema_type=MySchema)

    # $ python test_schema.py  -h
    # usage: test_schema.py [-h] [--nest.cstr NEST.CSTR] [--nest.bstr NEST.BSTR]
    #                     [--nest.aint NEST.AINT] [--topintc TOPINTC]
    #                     [--topint TOPINT] [--input_json INPUT_JSON]
    #                     [--output_json OUTPUT_JSON] [--log_level LOG_LEVEL]
    #                     [--topintb TOPINTB] [--topintd TOPINTD]

    # optional arguments:
    # -h, --help            show this help message and exit

    # nest:
    # nested schema

    # --nest.cstr NEST.CSTR
    #                         a list of whether statements are true/false/maybe
    #                         (REQUIRED) (constrained list) (valid options are
    #                         ['true', 'false', 'maybe'])
    # --nest.bstr NEST.BSTR
    #                         a string (REQUIRED) (valid options are ['a', 'b',
    #                         'c'])
    # --nest.aint NEST.AINT
    #                         a integer (default=5)

    # MySchema:
    # my set of parameters

    # --topintc TOPINTC     a top integer c (REQUIRED)
    # --topint TOPINT       a top integer (REQUIRED)
    # --input_json INPUT_JSON
    #                         file path of input json file
    # --output_json OUTPUT_JSON
    #                         file path to output json file
    # --log_level LOG_LEVEL
    #                         set the logging level of the module (default=ERROR)
    # --topintb TOPINTB     a top integer b (default=5)
    # --topintd TOPINTD     a top integer d (default=7)