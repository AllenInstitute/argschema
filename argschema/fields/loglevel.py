'''marshmallow fields related to setting logging levels'''
import logging
import marshmallow as mm


class LogLevel(mm.fields.Str):
    """LogLevel is a field type that provides a setting for the loglevel of
    python.logging.  This class will both validate the input and also *set* the
    input globally.  In simple scenarios, a module will not have to do any
    manipulation of loglevel.
    """

    options = ['FATAL', 'CRITICAL', 'ERROR',
               'WARN', 'WARNING', 'INFO', 'DEBUG']

    def __init__(self, **kwargs):
        kwargs['metadata'] = kwargs.get(
            'metadata', {'description': 'set log level'})
        kwargs['default'] = kwargs.get('default', 'WARN')
        super(LogLevel, self).__init__(**kwargs)

    def _validate(self, value):
        """

        Parameters
        ----------
        value : str
            value to validate

        """
        if (not hasattr(logging, value) or
                type(getattr(logging, value)) is not int):
            raise mm.ValidationError(
                    '{} is not a valid loglevel; try one of {}'.format(
                        value, LogLevel.options))

        # Would prefer this to be an argparse.Action subclass, but not yet sure how to implement this way
        logging.getLogger().setLevel(value)
