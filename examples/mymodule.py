import argschema

class MySchema(argschema.ArgSchema):
    a = argschema.fields.Int(default = 42, 
                            metadata = {'description':'my first parameter'})

class MyModule(argschema.ArgSchemaParser):
    def __init__(self, *args, **kwargs):
        super(MyModule, self).__init__(
            schema_type=MySchema, *args, **kwargs)
    def run(self):
        print(self.args)
        self.logger.warning('this program does nothing useful')

if __name__ == '__main__':
    mod = MyModule()
    mod.run()
    