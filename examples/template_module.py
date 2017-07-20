from argschema import ArgSchemaParser,ArgSchema
from argschema.schemas import Schema
from argschema.fields import InputDir, NumpyArray, Boolean
import marshmallow as mm

class MyNestedParameters(Schema):
    name = mm.fields.Str(required=True,metadata={'description':'name of vector'})
    increment = mm.fields.Int(required=True,metadata={'description':'value to increment'})
    array = NumpyArray(required=True,metadata={'description':'array to increment'})
    output_path = InputDir(required=True,metadata={'description':'path to write result'})
    write_output = Boolean(required=False,default=True)

class MyParameters(ArgSchema):
    inc = mm.fields.Nested(MyNestedParameters)

class MyModule(ArgSchemaParser):
    def __init__(self,*args,**kwargs):
        super(MyModule,self).__init__(schema_type = MyParameters,*args,**kwargs)
        print self.args

if __name__ == '__main__':
    example_input={
        "inc":{
            "name":"example_output",
            "increment":5,
            "array":[0,2,5],
            "output_path":".",
            "write_output":True
        }
    }
    module = MyModule(input_data=example_input)
    module.run()

