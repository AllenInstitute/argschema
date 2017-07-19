import pytest
from argschema import ArgSchemaParser
from argschema.fields import LogLevel
import marshmallow as mm

def test_option_list():
    input_data = {
        'log_level':'WARNING'
    }
    mod = ArgSchemaParser(
        input_data=input_data, args=[])

def test_bad_option():
    input_data = {
        'log_level':'NOTALEVEL'
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=input_data, args=[])

