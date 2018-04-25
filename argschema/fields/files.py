'''marshmallow fields related to validating input and output file paths'''
import os
import marshmallow as mm
import tempfile
import errno


def validate_outpath(path):
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path) as tfile:
            tfile.write('0')
            tfile.close()
            
    except Exception as e:
        if isinstance(e, OSError):
            if e.errno == errno.ENOENT:
                raise mm.ValidationError(
                    "%s is not in a directory that exists" % path)
            elif e.errno == errno.EACCES:
                raise mm.ValidationError(
                    "%s does not appear you can write to path" % path)
            else:
                raise mm.ValidationError(
                    "Unknown OSError: {}".format(e.message))
        else:
            raise mm.ValidationError(
                "Unknown Exception: {}".format(e.message))


class OutputFile(mm.fields.Str):
    """OutputFile :class:`marshmallow.fields.Str` subclass which is a path to a
       file location that can be written to by the current user
       (presently tested by opening a temporary file to that
       location)

    Parameters
    ----------

    Returns
    -------

    """

    def _validate(self, value):
        """

        Parameters
        ----------
        value : str
            filepath to validate you can write to that location

        Returns
        -------
        None

        Raises
        ------
        marshmallow.ValidationError
            If os.path.dirname cannot be applied, or if directory does not exist, or if you cannot write to that directory,
            or writing a temporary file there produces any crazy exception
        """
        try:
            path = os.path.dirname(value)
        except Exception as e:  # pragma: no cover
            raise mm.ValidationError(
                "%s cannot be os.path.dirname-ed" % value)  # pragma: no cover
        validate_outpath(path)


class OutputDir(mm.fields.Str):
    """OutputDir is a :class:`marshmallow.fields.Str` subclass which is a path to
       a location where this module will write files.  Validation will check that 
       the directory exists and create the directory if it is not present,
       and will fail validation if the directory cannot be created or cannot be
       written to.

       Parameters
       ==========
       mode: str
          mode to create directory
       *args:
         smae as passed to marshmallow.fields.Str
       **kwargs:
         same as passed to marshmallow.fields.Str
    """

    def __init__(self, mode=None, *args, **kwargs):
        self.mode = mode
        super(OutputDir, self).__init__(*args, **kwargs)

    def _validate(self, value):
        if not os.path.isdir(value):
            try:
                os.makedirs(value)
                if self.mode is not None:
                    os.chmod(value, self.mode)
            except OSError as e:
                if e.errno == os.errno.EEXIST:
                    pass
                else:
                    raise mm.ValidationError(
                        "{} is not a directory and you cannot create it".format(
                            value)
                    )
        if self.mode is not None:
            try:
                assert((os.stat(value).st_mode & 0o777) == self.mode)
            except:
                raise mm.ValidationError(
                    "{} does not have the mode  ({}) that was specified ".format(
                        value, self.mode)
                )
        # use outputfile to test that a file in this location is a valid path
        validate_outpath(value)

def validate_input_path(value):
    if not os.path.isfile(value):
        raise mm.ValidationError("%s is not a file" % value)
    elif not os.access(value, os.R_OK):
        raise mm.ValidationError("%s is not readable" % value)

class InputDir(mm.fields.Str):
    """InputDir is  :class:`marshmallow.fields.Str` subclass which is a path to a
       a directory that exists and that the user can access
       (presently checked with os.access)
    """

    def _validate(self, value):
        if not os.path.isdir(value):
            raise mm.ValidationError("%s is not a directory")
        elif not os.access(value, os.R_OK):
            raise mm.ValidationError(
                "%s is not a readable directory" % value)


class InputFile(mm.fields.Str):
    """InputDile is a :class:`marshmallow.fields.Str` subclass which is a path to a
       file location which can be read by the user
       (presently passes os.path.isfile and os.access = R_OK)
    """

    def _validate(self, value):
        validate_input_path(value)
