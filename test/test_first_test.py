import pytest
import os
import json
import logging
import marshmallow as mm
from argschema import ArgSchemaParser, ArgSchema


def test_bad_path():
    with pytest.raises(mm.ValidationError):
        example = {
            "input_json": "a bad path",
            "output_json": "another example",
            "log_level": "DEBUG"}
        jm = ArgSchemaParser(input_data=example, args=[])


def test_simple_example(tmpdir):
    file_in = tmpdir.join('test_input_json.json')
    file_in.write('nonesense')

    file_out = tmpdir.join('test_output.json')

    example = {
        "input_json": str(file_in),
        "output_json": str(file_out),
        "log_level": "CRITICAL"}
    jm = ArgSchemaParser(input_data=example, args=[])

    assert jm.args['log_level'] == 'CRITICAL'


def test_log_catch():
    with pytest.raises(mm.ValidationError):
        example = {"log_level": "NOTACHOICE"}
        jm = ArgSchemaParser(input_data=example, args=[])
        print(jm.args)


class MyExtension(mm.Schema):
    a = mm.fields.Str(metadata={'description': 'a string'},required=True)
    b = mm.fields.Int(metadata={'description': 'an integer'})
    c = mm.fields.Int(metadata={'description': 'an integer'}, default=10)
    d = mm.fields.List(mm.fields.Int,
                       metadata={'description': 'a list of integers'})


class SimpleExtension(ArgSchema):
    test = mm.fields.Nested(MyExtension)


def test_simple_extension_required():
    with pytest.raises(mm.ValidationError):
        example1 = {}
        mod = ArgSchemaParser(
            input_data=example1, schema_type=SimpleExtension, args=[])


SimpleExtension_example_invalid = {
    'test':
    {
        'a': 5,
        'b': 1,
        'd': ['a', 2, 3]
    }
}

SimpleExtension_example_valid = {
    'test':
        {
            'a': "hello",
            'b': 1,
            'd': [1, 5, 4]
        }
}


@pytest.fixture(scope='module')
def simple_extension_file(tmpdir_factory):
    file_ = tmpdir_factory.mktemp('test').join('testinput.json')
    file_.write(json.dumps(SimpleExtension_example_valid))
    return file_


def test_simple_extension_fail():
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=SimpleExtension_example_invalid,
            schema_type=SimpleExtension, args=[])


def test_simple_extension_pass():
    mod = ArgSchemaParser(
        input_data=SimpleExtension_example_valid,
        schema_type=SimpleExtension, args=[])
    assert mod.args['test']['a'] == 'hello'
    assert mod.args['test']['b'] == 1
    assert len(mod.args['test']['d']) == 3


def test_simple_extension_write_pass(simple_extension_file):
    args = ['--input_json', str(simple_extension_file)]
    mod = ArgSchemaParser(schema_type=SimpleExtension, args=args)
    assert mod.args['test']['a'] == 'hello'
    assert mod.args['test']['b'] == 1
    assert len(mod.args['test']['d']) == 3
    assert mod.logger.getEffectiveLevel() == logging.ERROR


def test_simple_extension_write_debug_level(simple_extension_file):
    args = ['--input_json', str(simple_extension_file), '--log_level', 'DEBUG']
    mod = ArgSchemaParser(schema_type=SimpleExtension, args=args)
    assert mod.logger.getEffectiveLevel() == logging.DEBUG


def test_simple_extension_write_overwrite(simple_extension_file):
    args = ['--input_json', str(simple_extension_file), '--test.b', '5']
    mod = ArgSchemaParser(schema_type=SimpleExtension, args=args)
    assert mod.args['test']['b'] == 5


def test_simple_extension_write_overwrite_list(simple_extension_file):
    args = ['--input_json', str(simple_extension_file),
            '--test.d', '6', '7', '8', '9']
    mod = ArgSchemaParser(schema_type=SimpleExtension, args=args)
    mod.run()
    assert len(mod.args['test']['d']) == 4

def test_bad_input_json_argparse():
    args = ['--input_json', 'not_a_file.json']
    with pytest.raises(mm.ValidationError): 
        mod = ArgSchemaParser(schema_type=SimpleExtension, args=args)
