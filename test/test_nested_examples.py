import argschema
import marshmallow as mm


class MyNested(argschema.schemas.DefaultSchema):
    a = argschema.fields.Int(required=True)
    b = argschema.fields.Str(required=True)
    c = argschema.fields.Str(required=False,default='c')

class MySchema(argschema.ArgSchema):
    nested = argschema.fields.Nested(MyNested, only=['a', 'b'],
        required=False, default=mm.missing)

def test_nested_example():
    mod = argschema.ArgSchemaParser(schema_type=MySchema,
                                     args = [])
    assert(not 'nested' in mod.args.keys())

def test_nested_marshmallow_example():
    schema = MySchema()
    argschema.utils.load(schema, {})
