'''module for custom marshmallow validators'''
import numpy as np
from marshmallow.validate import Validator
import marshmallow as mm

__all__ = ['Shape']


class Shape(Validator):
    """Validate that an array has the correct shape.
    
    Parameters
    ----------
    shape : tuple
        Tuple specifying the required array shape.
    """

    def __init__(self, shape=None):
        try:
            self.shape = tuple(shape)
        except TypeError:
            raise ValueError("{} is not a valid shape".format(shape))
        if not all(isinstance(item, int) for item in self.shape):
            raise ValueError("{} is not a valid shape".format(shape))

    def __call__(self, value):
        try:
            shape = value.shape
        except AttributeError:
            raise mm.ValidationError("{} is not a valid array, does not have "
                                     "attribute `shape`.".format(value))
        return shape == self.shape
