from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import NumpyArray, Boolean, Int, Str, Nested
from argschema.schemas import DefaultSchema
import numpy as np
import pprint as pp


# these are the core parameters for my module


class MyNestedParameters(DefaultSchema):
    name = Str(required=True, description='name of vector')
    increment = Int(required=True, description='value to increment')
    array = NumpyArray(dtype=np.float, required=True,
                       description='array to increment')
    write_output = Boolean(required=False, default=True)


# but i'm going to nest them inside a subsection called inc


class MyParameters(ArgSchema):
    inc = Nested(MyNestedParameters)


# this is another schema we will use to validate and deserialize our output
class MyOutputParams(DefaultSchema):
    name = Str(required=True, description='name of vector')
    inc_array = NumpyArray(dtype=np.float, required=True,
                           description='incremented array')


if __name__ == '__main__':

    # this defines a default dictionary that will be used if input_json is not specified
    example_input = {
        "inc": {
            "name": "from_dictionary",
            "increment": 5,
            "array": [0, 2, 5],

            "write_output": True
        },
        "output_json": "output_dictionary.json"
    }

    # here is my ArgSchemaParser that processes my inputs
    mod = ArgSchemaParser(input_data=example_input,
                          schema_type=MyParameters,
                          output_schema_type=MyOutputParams)

    # pull out the inc section of the parameters
    inc_params = mod.args['inc']

    # do my simple addition of the parameters
    inc_array = inc_params['array'] + inc_params['increment']

    # define the output dictionary
    output = {
        'name': inc_params['name'],
        'inc_array': inc_array
    }

    # if the parameters are set as such write the output
    if inc_params['write_output']:
        mod.output(output)

    pp.pprint(mod.args)
