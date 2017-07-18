'''marshmallow fields related to validating input and output file paths'''
import os
import marshmallow as mm
import tempfile
import errno


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
