'''Module containing custom marshmallow fields that are useful for
defining schemas, including the base schema used by JsonModule
'''
import tempfile
import os
import errno
import marshmallow as mm
import numpy as np


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


class OutputFile(mm.fields.Str):
    '''OutputFile marshamallow.fields.Str subclass which is a path to a
       file location that can be written to by the current user
       (presently tested by opening a temporary file to that
       location)
    '''
    def _validate(self, value):
        try:
            path = os.path.dirname(value)
        except Exception as e:
            raise mm.ValidationError("%s cannot be os.path.dirname-ed" % value)
        try:
            with tempfile.TemporaryFile(mode='w', dir=path) as tfile:
                tfile.write('0')
        except Exception as e:
            if isinstance(e, OSError):
                if e.errno == errno.ENOENT:
                    raise mm.ValidationError(
                        "%s is not in a directory that exists" % value)
                elif e.errno == errno.EACCES:
                    raise mm.ValidationError(
                        "%s does not appear you can write to path" % value)
                else:
                    raise mm.ValidationError(
                        "Unknown OSError: {}".format(e.message))
            else:
                raise mm.ValidationError(
                    "Unknown Exception: {}".format(e.message))


class InputDir(mm.fields.Str):
    '''InputDir is  marshmallow.fields.Str subclass which is a path to a
       a directory that exists and that the user can access
       (presently checked with os.access)
    '''
    def _validate(self, value):
        if not os.path.isdir(value):
            raise mm.ValidationError("%s is not a directory")
        elif not os.access(value, os.R_OK):
            raise mm.ValidationError(
                "%s is not a readable directory" % value)


class InputFile(mm.fields.Str):
    '''InputDile is a marshmallow.fields.Str subclass which is a path to a
       file location which can be read by the user
       (presently passes os.path.isfile and os.access = R_OK)
    '''
    def _validate(self, value):
        if not os.path.isfile(value):
            raise mm.ValidationError("%s is not a file" % value)
        elif not os.access(value, os.R_OK):
            raise mm.ValidationError("%s is not readable" % value)


class OptionList(mm.fields.Field):
    '''OptionList is a marshmallow field which enforces that this field
       is one of a finite set of options.
       OptionList(options,*args,**kwargs) where options is a list of
       json compatible options which this option will be enforced to belong
    '''
    def __init__(self, options, *args, **kwargs):
        self.options = options
        super(OptionList, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        return value

    def _validate(self, value):
        if value not in self.options:
            raise mm.ValidationError("%s is not a valid option" % value)

        return value
