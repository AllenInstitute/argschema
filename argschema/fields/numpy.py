'''marshmallow fields related to reading in numpy arrays'''
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
        super(NumpyArray, self).__init__(*args, **kwargs)

    def _deserialize(self, value, attr, obj):
        mylist = super(NumpyArray, self)._serialize(value, attr, obj)
        if self.dtype is not None:
            myarray = np.array(mylist, dtype=self.dtype)
        else:
            myarray = np.array(mylist)
        return myarray

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return mm.fields.List._serialize(self, value.tolist(), attr, obj)

