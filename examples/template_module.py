from argschema import ArgSchemaParser, ArgSchema
from argschema.schemas import DefaultSchema
from argschema.fields import OutputFile, NumpyArray, Boolean
import marshmallow as mm
import numpy as np
import json


class MyOutputParams(DefaultSchema):
    name = mm.fields.Str(required=True, metadata={
                         'description': 'name of vector'})
    inc_array = NumpyArray(dtype=np.float, required=True, metadata={
                           'description': 'incremented array'})


class MyNestedParameters(DefaultSchema):
    name = mm.fields.Str(required=True, metadata={
                         'description': 'name of vector'})
    increment = mm.fields.Int(required=True, metadata={
                              'description': 'value to increment'})
    array = NumpyArray(dtype=np.float, required=True, metadata={
                       'description': 'array to increment'})
    write_output = Boolean(required=False, default=True)


class MyParameters(ArgSchema):
    inc = mm.fields.Nested(MyNestedParameters)


class MyModule(ArgSchemaParser):
    def __init__(self, *args, **kwargs):
        super(MyModule, self).__init__(
            schema_type=MyParameters, *args, **kwargs)


if __name__ == '__main__':
    example_input = {
        "inc": {
            "name": "from_dictionary",
            "increment": 5,
            "array": [0, 2, 5],

            "write_output": True
        },
        "output_json": "output_dictionary.json"
    }
    mod = MyModule(input_data=example_input)
    inc_params = mod.args['inc']
    inc_array = inc_params['array'] + inc_params['increment']
    output = {
        'name': inc_params['name'],
        'inc_array': inc_array
    }
    if inc_params['write_output']:
        out_schema = MyOutputParams()
        out_json, errors = out_schema.dump(output)
        assert not errors
        print out_json
        with open(mod.args['output_json'], 'w') as fp:
            json.dump(out_json, fp)
