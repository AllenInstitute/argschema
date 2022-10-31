import pytest
from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import NumpyArray
from argschema.utils import dump
import marshmallow as mm
import numpy as np

numpy_array_test = {
    'a': [[1, 2],
          [3, 4]]
}


class NumpyFileuint16(ArgSchema):
    a = NumpyArray(
        dtype='uint16', required=True,
        metadata = {'description':'list of lists representing a uint16 numpy array'})


def test_numpy():
    mod = ArgSchemaParser(
        input_data=numpy_array_test, schema_type=NumpyFileuint16, args=[])
    assert mod.args['a'].shape == (2, 2)
    assert mod.args['a'].dtype == 'uint16'


def test_bad_shape():
    bad_shape = {
        'a': [[1, 2], [3]]
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(  # noQA: F841
            input_data=bad_shape, schema_type=NumpyFileuint16, args=[])


def test_bad_data():
    bad_shape = {
        'a': [['a', 'b']]
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(  # noQA: F841
            input_data=bad_shape, schema_type=NumpyFileuint16, args=[])


def test_serialize():
    schema = NumpyFileuint16()
    object_dict = {
        'a': np.array([1, 2])
    }
    json_dict = dump(schema, object_dict)
    assert(type(json_dict['a']) == list)
    assert(json_dict['a'] == object_dict['a'].tolist())
