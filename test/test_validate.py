from argschema import validate
import pytest
from argschema.fields import NumpyArray
import marshmallow as mm
import numpy as np


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
])
def test_shape_call_invalid(validation_shape, input_array):
    validator = validate.Shape(validation_shape)
    with pytest.raises(mm.ValidationError):
        validator(input_array)


@pytest.mark.parametrize("validation_shape,input_array", [
    ((2, 2), np.empty((2,2))),
    ((5, 5, 3), np.empty((100,))),
])
def test_shape_call(validation_shape, input_array):
    validator = validate.Shape(validation_shape)
    assert(validator(input_array) == (validation_shape == input_array.shape))
