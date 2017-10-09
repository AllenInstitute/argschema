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
        Tuple specifying the required shape

    Raises
    ------
    ValueError
        If the provided shape is not a valid tuple of integers
    marshmallow.ValidationError
        If the value being validated does not have a shape attribute
    """

    def __init__(self, shape=None):
        try:
            self.shape = tuple(shape)
        except TypeError:
            raise ValueError("{} is not a valid shape".format(shape))
        if not all(isinstance(item, int) for item in self.shape):
            raise ValueError("{} is not a valid shape".format(shape))
        self.error = "Array shape is not {}".format(self.shape)

    def __call__(self, value):
        try:
            valid = (value.shape == self.shape)
        except AttributeError:
            raise mm.ValidationError("{} is not a valid array, does not have "
                                     "attribute `shape`.".format(value))
        if not valid:
            raise mm.ValidationError("Array shape {} does not match required "
                                     "shape {}.".format(value.shape,
                                     self.shape))
        return valid

