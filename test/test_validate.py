from argschema import validate, ArgSchemaParser, ArgSchema
from argschema.fields import NumpyArray
import pytest
import marshmallow as mm
import numpy as np


class MySchema(ArgSchema):
    a = NumpyArray(dtype='float', description='Test input array schema',
                   validate=validate.Shape((2,2)))


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
])
def test_shape_init(input_shape, expected):
    validator = validate.Shape(input_shape)
    assert(validator.shape == expected)


@pytest.mark.parametrize("validation_shape,input_array", [
    ((2, 2), "notanarray"),
    ((5, 5, 3), 6),
    ((3, 3), [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    ((2, 2), np.empty((2,3)))
])
def test_shape_call_invalid(validation_shape, input_array):
    validator = validate.Shape(validation_shape)
    with pytest.raises(mm.ValidationError):
        validator(input_array)


@pytest.mark.parametrize("validation_shape,input_array", [
    ((2, 2), np.empty((2,2))),
])
def test_shape_call(validation_shape, input_array):
    validator = validate.Shape(validation_shape)
    assert(validator(input_array))


def test_parser_validation():
    i1 = {"a": [[1, 2], [3, 4]]}
    p1 = ArgSchemaParser(input_data=i1, schema_type=MySchema)
    i2 = {"a": [[1, 2, 3], [4, 5, 6]]}
    with pytest.raises(mm.ValidationError):
        p2 = ArgSchemaParser(input_data=i2, schema_type=MySchema)
