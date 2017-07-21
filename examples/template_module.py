from argschema import ArgSchemaParser,ArgSchema
from argschema.fields import InputDir, NumpyArray, Boolean
import marshmallow as mm
import numpy as np

class MyOutputParams(mm.Schema):
    name = mm.fields.Str(required=True,metadata={'description':'name of vector'})
    inc_array = NumpyArray(dtype=np.int,required=True,metadata={'description':'incremented array'})

class MyNestedParameters(mm.Schema):
    name = mm.fields.Str(required=True,metadata={'description':'name of vector'})
    increment = mm.fields.Int(required=True,metadata={'description':'value to increment'})
    array = NumpyArray(dtype=np.int,required=True,metadata={'description':'array to increment'})
    output_path = InputDir(required=True,metadata={'description':'path to write result'})
    write_output = Boolean(required=False,default=True)

class MyParameters(ArgSchema):
    inc = mm.fields.Nested(MyNestedParameters)

class MyModule(ArgSchemaParser):
    def __init__(self,*args,**kwargs):
        super(MyModule,self).__init__(schema_type = MyParameters,*args,**kwargs)

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
    mod = MyModule(input_data=example_input)
    inc_params=mod.args['inc']
    inc_array = inc_params['array']+inc_params['increment']
    output = {
        'name':inc_params['name'],
        'inc_array':inc_array
    }
    if inc_params['write_output']:
        out_schema = MyOutputParams()
        print out_schema.dump(output)

