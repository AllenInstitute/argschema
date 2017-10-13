'''module for custom marshmallow validators'''
import numpy as np
from marshmallow.validate import Validator
import marshmallow as mm

__all__ = ['Shape']


class Shape(Validator):
    """Validator which succeeds if value.shape matches `shape`
    
    Parameters
    ----------
    shape : tuple
        Tuple specifying the required shape. If a value in the tuple is
        `None`, any length in that dimension is valid.

    Raises
    ------
    ValueError
        If the provided shape is not a valid tuple of integers and/or
        None types
    marshmallow.ValidationError
        If the value being validated does not have a shape attribute
    """

    def __init__(self, shape=None):
        try:
            self.shape = tuple(shape)
        except TypeError:
            raise ValueError("{} is not a valid shape".format(shape))
        if not all(isinstance(item, (int, type(None))) for item in self.shape):
            raise ValueError("{} is not a valid shape".format(shape))
        self.error = "Array shape is not {}".format(self.shape)

    def __call__(self, value):
        try:
            shape = value.shape
        except AttributeError:
            raise mm.ValidationError("{} is not a valid array, does not have "
                                     "attribute `shape`.".format(value))
        if len(shape) != len(self.shape):
            raise mm.ValidationError("Dimension mismatch: input shape {} does "
                                     "not match {}.".format(shape, self.shape))
        valid = all([a==b for a,b in zip(shape, self.shape) if b is not None])
        if not valid:
            raise mm.ValidationError("Array shape {} does not match required "
                                     "shape {}.".format(shape, self.shape))
        return valid

