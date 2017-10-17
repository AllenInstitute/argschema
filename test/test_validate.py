from argschema import validate, ArgSchemaParser, ArgSchema
from argschema.fields import *
from marshmallow.fields import *
import pytest
import marshmallow as mm
import numpy as np


class MySchema(ArgSchema):
    a = NumpyArray(dtype='float', description='Test input array schema',
                   validate=validate.Shape((2,2)))
    b = NumpyArray(dtype='float', description='Test array',
                   validate=validate.Shape((2, None)))


@pytest.mark.parametrize("invalid_shape", [
    None,
    "notavalidshape",
    [1, 2, [3, 4]],
])
def test_shape_init_invalid(invalid_shape):
    with pytest.raises(ValueError):
        validator = validate.Shape(invalid_shape)


@pytest.mark.parametrize("input_shape,expected", [
    ([100, 5], (100, 5)),
    ((20, 20, 30, 80), (20, 20, 30, 80)),
    ([50], (50,)),
    ((2, None, 3), (2, None, 3)),
])
def test_shape_init(input_shape, expected):
    validator = validate.Shape(input_shape)
    assert(validator.shape == expected)


@pytest.mark.parametrize("validation_shape,input_array", [
    ((2, 2), "notanarray"),
    ((5, 5, 3), 6),
    ((3, 3), [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    ((2, 2), np.empty((2,3))),
])
def test_shape_call_invalid(validation_shape, input_array):
    validator = validate.Shape(validation_shape)
    with pytest.raises(mm.ValidationError):
        validator(input_array)


@pytest.mark.parametrize("validation_shape,input_array", [
    ((2, 2), np.empty((2,2))),
    ((2, 3, None), np.empty((2, 3, 5)))
])
def test_shape_call(validation_shape, input_array):
    validator = validate.Shape(validation_shape)
    assert(validator(input_array))


@pytest.mark.parametrize("input_dict,raises", [
    ({"a": [[1, 2], [3, 4]]}, False),
    ({"b": [[1, 2, 3, 4], [5, 6, 7, 8]]}, False),
    ({"a": [[1, 2, 3], [4, 5, 6]]}, True),
    ({"b": [[1, 2], [3, 4], [5, 6]]}, True),
])
def test_parser_validation(input_dict,raises):
    if raises:
        with pytest.raises(mm.ValidationError):
            p = ArgSchemaParser(input_data=input_dict, schema_type=MySchema)
    else:
        p = ArgSchemaParser(input_data=input_dict, schema_type=MySchema)
