import pytest
from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import Slice
import numpy as np
import marshmallow as mm


class SliceSchema(ArgSchema):
    a = Slice(required=True, metadata={
            'decription': 'a slice object'})


def test_slice():
    input_data = {
        'a': '5:7'
    }
    mod = ArgSchemaParser(
        input_data=input_data, schema_type=SliceSchema, args=[])
    assert type(mod.args['a']) == slice
    test = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert(test[mod.args['a']].shape == (2,))


def test_bad_slice():
    input_data = {
        'a': '5:7:8:9'
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=input_data, schema_type=SliceSchema, args=[])
