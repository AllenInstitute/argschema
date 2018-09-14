import argschema


class MySchema(argschema.ArgSchema):
    a = argschema.fields.Int(default=42, description='my first parameter')


if __name__ == '__main__':
    mod = argschema.ArgSchemaParser(schema_type=MySchema)
    mod.logger.warn("this module does nothing useful")
    print(mod.args)
