'''marshmallow fields related to setting logging levels'''
import logging
import marshmallow as mm

class LogLevel(mm.fields.Str):
    '''LogLevel is a field type that provides a setting for the loglevel of
    python.logging.  This class will both validate the input and also *set* the
    input globally.  In simple scenarios, a module will not have to do any
    manipulation of loglevel.
    '''

    options = { s: getattr(logging, s) for s in 
                ['FATAL', 'CRITICAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG'] }

    def __init__(self, **kwargs):
        kwargs['metadata'] = kwargs.get('metadata', {
            'description': 'set log level: {}'.format(LogLevel.options.keys())
            })
        kwargs['default'] = kwargs.get('default', 'WARN')
        super(LogLevel, self).__init__(**kwargs)

    def _deserialize(self, value, attr, obj):
        if value in LogLevel.options:
            level = LogLevel.options[value]
            logging.getLogger().setLevel(level)
            return level
        try:
            level = int(value)
            logging.getLogger().setLevel(level)
            return level
        except ValueError:
            raise mm.ValidationError(
                    '{} is not a valid loglevel; try one of {}, or an integer'.format(
                        value, LogLevel.options.keys()))

    @staticmethod
    def initialize(name, level):
        """initializes the logger with a name
        logger = LogLevel.initialize(name)
        
        Args:
           name (str):  name of the logger
        Returns:
            logging.Logger: a logger set with the name specified
        """
        logging.basicConfig()
        logger = logging.getLogger(name)
        logger.setLevel(level)
        return logger


