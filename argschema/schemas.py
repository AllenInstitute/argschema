from pydantic import BaseModel, Field, FilePath
from pydantic.main import ModelMetaclass
from typing import get_origin
from enum import Enum
import logging
import argparse
from .fields import OutputFile

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class ArgSchema(BaseModel):
    input_json: FilePath = Field('input.json', description='zee inputs')
    output_json: OutputFile = Field('output.json', description='zee outputs')
    log_level: LogLevel = Field(logging.ERROR, description='zee log level')

    @classmethod
    def from_args(cls, a):
        arg_data = vars(a)
        with open(arg_data['input_json'],'r') as f:
            input_data = json.load(f)

        input_data['input_json'] = arg_data['input_json']
        input_data['output_json'] = arg_data['output_json']
        input_data['log_level'] = arg_data['log_level']
        
        return populate_schema_from_data(cls, input_data, arg_data)

    @classmethod
    def argument_parser(cls, *args, **kwargs):
        parser = argparse.ArgumentParser(*args, **kwargs)
        add_arguments_from_schema(parser, cls)
        return parser 

def populate_schema_from_data(schema, input_data, arg_data):
    xdata = {}

    for field_name, field in schema.__fields__.items():
        if isinstance(field.outer_type_, ModelMetaclass):
            sub_input_data = input_data[field_name]
            sub_arg_data = { k.replace(f'{field_name}.',''):v for k,v in arg_data.items() if k.startswith(field_name)}
            xdata[field_name] = populate_schema_from_data(field.type_, sub_input_data, sub_arg_data)
        else:
            arg_value = arg_data.get(field_name, None)
            xdata[field_name] = input_data[field_name] if arg_value is None else arg_value
    
    return schema(**xdata)

def add_arguments_from_schema(parser, schema, parent_prefix=''):
    for field_name, field in schema.__fields__.items():
        fn = field_name.replace('_','-')
        
        if isinstance(field.outer_type_, ModelMetaclass):
            add_arguments_from_schema(parser, field.outer_type_, parent_prefix=f'{parent_prefix}{fn}.')
        elif get_origin(field.outer_type_) is list:
            parser.add_argument(f'--{parent_prefix}{fn}', nargs='+', type=field.type_, default=field.default, help=field.field_info.description)
        else:
            parser.add_argument(f'--{parent_prefix}{fn}', type=field.type_, default=field.default, help=field.field_info.description)   


