import pytest
from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import NumpyArray
import marshmallow as mm
import numpy as np

numpy_array_test = {
    'a': [[1, 2],
          [3, 4]]
}


class NumpyFileuint16(ArgSchema):
    a = NumpyArray(
        dtype='uint16', required=True, metadata={
            'decription': 'list of lists representing numpy array'})


def test_numpy():
    mod = ArgSchemaParser(
        input_data=numpy_array_test, schema=NumpyFileuint16, args=[])
    assert mod.args['a'].shape == (2, 2)
    assert mod.args['a'].dtype == 'uint16'


def test_bad_shape():
    bad_shape = {
        'a': [[1, 2], [3]]
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=bad_shape, schema=NumpyFileuint16, args=[])


def test_bad_data():
    bad_shape = {
        'a': [['a', 'b']]
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=bad_shape, schema=NumpyFileuint16, args=[])


def test_serialize():
    schema = NumpyFileuint16()
    object_dict = {
        'a': np.array([1, 2])
    }
    (json_dict, errors) = schema.dump(object_dict)
    assert(len(errors) == 0)
    assert(type(json_dict['a']) == list)
    assert(json_dict['a'] == object_dict['a'].tolist())
