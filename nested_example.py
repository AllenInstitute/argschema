import argschema


class MyNest(argschema.schemas.DefaultSchema):
    a = argschema.fields.Int(load_default=1)
    b = argschema.fields.Int(load_default=2)


class MySchemaFill(argschema.ArgSchema):
    nest = argschema.fields.Nested(
        MyNest,
        required=False,
        load_default={},
        metadata={"description": "nested schema that fills in defaults"},
    )


class MySchema(argschema.ArgSchema):
    nest = argschema.fields.Nested(
        MyNest,
        required=False,
        metadata={"description": "nested schema that does not always fill defaults"},
    )


mod = argschema.ArgSchemaParser(schema_type=MySchema)
print("MySchema")
print(mod.args)
mod2 = argschema.ArgSchemaParser(schema_type=MySchemaFill)
print("MySchemaFill")
print(mod2.args)
