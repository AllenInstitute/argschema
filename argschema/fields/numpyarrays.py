'''marshmallow fields related to reading in numpy arrays'''
import numpy as np
import marshmallow as mm


class NumpyArray(mm.fields.List):
    '''NumpyArray is a marshmallow.fields.Str List subclass
    NumpyArray(dtype=None,*args,**kwargs)
    which will convert any numpy compatible set of lists into a
    numpy array after deserialization and convert it back to a list when
    serializing, if dtype is given (as a numpy.dtype)
    the array will be converted to the type, otherwise numpy will decide
    what type it should be.
    '''
    def __init__(self, dtype=None, *args, **kwargs):
        self.dtype = dtype
        super(NumpyArray, self).__init__(mm.fields.Field, *args, **kwargs)

    def _deserialize(self, value, attr, obj):
        mylist = super(NumpyArray, self)._serialize(value, attr, obj)
        try:
            return np.array(mylist, dtype=self.dtype)
        except ValueError as e:
            raise mm.ValidationError(
                'Cannot create numpy array with type {} from data.'.format(
                    self.dtype))

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return mm.fields.List._serialize(self, value.tolist(), attr, obj)
