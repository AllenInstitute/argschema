'''marshmallow fields related to validating input and output file paths'''
import os
import tempfile
import errno
import sys
import uuid
import stat
import warnings


class WindowsNamedTemporaryFile():
    def __init__(self, dir=None, mode=None):
        self.filename = os.path.join(dir, str(uuid.uuid4()))
        self.mode = mode

    def __enter__(self):
        self.open_file = open(self.filename, self.mode)
        return self.open_file
    
    def __exit__(self, *args):
        self.open_file.close()
        os.remove(self.filename)


if sys.platform == "win32":
    NamedTemporaryFile = WindowsNamedTemporaryFile
else:
    NamedTemporaryFile = tempfile.NamedTemporaryFile


def validate_outpath(path):
    try:
        with NamedTemporaryFile(mode='w', dir=path) as tfile:
            tfile.write('0')
            tfile.close()

    except Exception as e:
        if isinstance(e, OSError):
            if e.errno == errno.ENOENT:
                raise ValueError(
                    "%s is not in a directory that exists" % path)
            elif e.errno == errno.EACCES:
                raise ValueError(
                    "%s does not appear you can write to path" % path)
            else:
                raise ValueError(
                    "Unknown OSError: {}".format(e.message))
        else:
            raise ValueError(
                "Unknown Exception: {}".format(e.message))


class OutputFile(str):
    """OutputFile :class:`str` subclass which is a path to a
       file location that can be written to by the current user
       (presently tested by opening a temporary file to that
       location)

    Parameters
    ----------

    Returns
    -------

    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value):
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
            raise ValueError(
                "%s cannot be os.path.dirname-ed" % value)  # pragma: no cover
        validate_outpath(path)

        return cls(value)

class OutputDirModeException(Exception):
    pass

class OutputDir(str):
    """OutputDir is a :class:`str` subclass which is a path to
       a location where this module will write files.  Validation will check that
       the directory exists and create the directory if it is not present,
       and will fail validation if the directory cannot be created or cannot be
       written to.

       Parameters
       ==========
       mode: str
          mode to create directory
    """

    def __new__(cls, value='', mode=None):
        obj = str.__new__(cls, value)
        obj.mode = mode

        if (mode is not None) & (sys.platform == "win32"):
            raise OutputDirModeException(
                "Setting mode of OutputDir supported only on posix systems")

        return obj

    def __class_getitem__(cls, mode):
        return lambda value: cls(value, mode=mode)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        # this gets called before pydantic attempts to typecast
        if not isinstance(value, cls):
            value = cls(value)
        
        mode = value.mode
        value = str(value)

        if not os.path.isdir(value):
            try:
                os.makedirs(value)
                if mode is not None:
                    os.chmod(value, mode)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
                else:
                    raise ValueError(
                        "{} is not a directory and you cannot create it".format(
                            value)
                    )
        if mode is not None:
            try:
                assert((os.stat(value).st_mode & 0o777) == mode)
            except AssertionError:
                raise ValueError(
                    "{} does not have the mode  ({}) that was specified ".format(
                        value, mode)
                )
            except os.error:
                raise ValueError(
                    "cannot get os.stat of {}".format(value)
                )

        # use outputfile to test that a file in this location is a valid path
        validate_outpath(value)

        return value


def validate_input_path(value):
    if not os.path.isfile(value):
        raise ValueError("%s is not a file" % value)
    else:
        try:
            with open(value) as f:  
                pass
        except Exception as value:
            raise ValueError("%s is not readable" % value)   

class InputDir(str):
    """InputDir is  :class:`marshmallow.fields.Str` subclass which is a path to a
       a directory that exists and that the user can access
       (presently checked with os.access)
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value):
        if not os.path.isdir(value):
            raise ValueError("%s is not a directory")

        if sys.platform == "win32":
            try:
                x = list(os.scandir(value))
            except PermissionError:
                raise ValueError(
                    "%s is not a readable directory" % value)
        else:
            if not os.access(value, os.R_OK):
                raise ValueError(
                    "%s is not a readable directory" % value)

        return cls(value)


class InputFile(str):
    """InputDile is a :class:`marshmallow.fields.Str` subclass which is a path to a
       file location which can be read by the user
       (presently passes os.path.isfile and os.access = R_OK)
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value):
        validate_input_path(value)
        return cls(value)
