import pytest
from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import OptionList
import numpy as np
import marshmallow as mm


class OptionSchema(ArgSchema):
    a = OptionList([1, 2, 3], required=True, metadata={
        'decription': 'a slice object'})


def test_option_list():
    input_data = {
        'a': 1
    }
    mod = ArgSchemaParser(
        input_data=input_data, schema_type=OptionSchema, args=[])


def test_bad_option():
    input_data = {
        'a': 4
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=input_data, schema_type=OptionSchema, args=[])
