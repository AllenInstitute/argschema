import argparse
import logging

import marshmallow as mm

class LogLevelAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(values)

class LogLevel(mm.fields.Field):
    '''LogLevel is a field type that provides a setting for the loglevel of
    python.logging.  This class will both validate the input and also *set* the
    input globally.  In simple scenarios, a module will not have to do any
    manipulation of loglevel.'''

    options = ['FATAL', 'CRITICAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG']

    def __init__(self, *args, **kwargs):
        super(LogLevel, self).__init__(metadata={'description': 'set log level'}, default='WARN')

    def _serialize(self, value, attr, obj):
        return value;

    def _validate(self, value):
        if not hasattr(logging, value) or type(getattr(logging, value)) is not int:
            raise mm.ValidationError(
                    '{} is not a valid loglevel; try one of {}'.format(value, LogLevel.options))
        logging.getLogger().setLevel(value)

