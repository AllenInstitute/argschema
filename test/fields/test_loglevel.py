import pytest
from argschema import ArgSchemaParser
import marshmallow as mm


def test_option_list():
    input_data = {
        'log_level': 'WARNING'
    }
    ArgSchemaParser(
        input_data=input_data, args=[])


def test_bad_option():
    input_data = {
        'log_level': 'NOTALEVEL'
    }
    with pytest.raises(mm.ValidationError):
        ArgSchemaParser(
            input_data=input_data, args=[])
