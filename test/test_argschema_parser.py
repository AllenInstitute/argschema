import argschema
import pytest


class MyNestedSchema(argschema.schemas.DefaultSchema):
    one = argschema.fields.Int(required=True,description="nested integer")
    two = argschema.fields.Boolean(required=True,description="a nested boolean")

class MySchema(argschema.ArgSchema):
    a = argschema.fields.Int(required=True,description="parameter a")
    b = argschema.fields.Str(required=False,default="my value",description="optional b string parameter")
    nest = argschema.fields.Nested(MyNestedSchema,description="a nested schema")

class MyParser(argschema.ArgSchemaParser):
    default_schema = MySchema

def test_my_parser():
    input_data = {
        'a':5,
        'nest':{
            'one':7,
            'two':False
        }
    }
    mod = MyParser(input_data = input_data, args=[])

class MyNestedSchemaWithDefaults(argschema.schemas.DefaultSchema):
    one = argschema.fields.Int(default=1,
        description="nested integer")
    two = argschema.fields.Boolean(default=True,
        description="a nested boolean")

class MySchema2(argschema.ArgSchema):
    a = argschema.fields.Int(required=True,description="parameter a")
    b = argschema.fields.Str(required=False,default="my value",description="optional b string parameter")
    nest = argschema.fields.Nested(MyNestedSchemaWithDefaults,description="a nested schema")


def test_my_default_nested_parser():
    input_data = {
        'a':5
    }
    mod = argschema.ArgSchemaParser(input_data = input_data, 
                                    schema_type=MySchema2,
                                    args=None)


@pytest.mark.parametrize("default,args,expected", [
    (True, ["--nest.two", "False"], False),
    (True, ["--nest.two", "0"], False),
    (True, ["--nest.two", "'f'"], False),
    (False, ["--nest.two", "True"], True),
    (False, ["--nest.two", "1"], True)
])
def test_boolean_command_line(default, args, expected):
    input_data = {
        'a':5,
        'nest':{
            'one':7,
            'two':default
        }
    }
    mod = MyParser(input_data=input_data, args=args)
    assert(isinstance(mod.args['nest']['two'], bool))
    assert(mod.args['nest']['two'] == expected)


def test_bad_cli_input():
    input_data = {
        'a':5,
        'nest':{
            'one':7,
            'two':True
        }
    }
    with pytest.raises(SystemExit):
        mod = MyParser(input_data=input_data, args=["--nest.two", "notabool"])
