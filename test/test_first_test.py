import pytest
from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import InputFile, OutputFile, NumpyArray
import os
import json
import logging
import marshmallow as mm


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
    a = mm.fields.Str(metadata={'description': 'a string'})
    b = mm.fields.Int(metadata={'description': 'an integer'})
    c = mm.fields.Int(metadata={'description': 'an integer'}, default=10)
    d = mm.fields.List(mm.fields.Int,
                       metadata={'description': 'a list of integers'})


class SimpleExtension(ArgSchema):
    test = mm.fields.Nested(MyExtension)


class BasicInputFile(ArgSchema):
    input_file = InputFile(required=True,
                           metadata={'description': 'a simple file'})


class BasicOutputFile(ArgSchema):
    output_file = OutputFile(required=True,
                             metadata={'decription': 'a simple output file'})


input_file_example = {
    'input_file': 'relative.file'
}

output_file_example = {
    'output_file': 'output.file'
}

enoent_outfile_example = {
    'output_file': os.path.join('path', 'to', 'output.file')
}


def test_relative_file_input():
    with open(input_file_example['input_file'], 'w') as fp:
        fp.write("test")
    mod = ArgSchemaParser(
        input_data=input_file_example, schema_type=BasicInputFile, args=[])
    os.remove(input_file_example['input_file'])


def test_relative_file_input_failed():
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=input_file_example, schema_type=BasicInputFile, args=[])


def test_access_inputfile_failed():
    with open(input_file_example['input_file'], 'w') as fp:
        fp.write('test')
    os.chmod(input_file_example['input_file'], 0222)
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=input_file_example, schema_type=BasicInputFile, args=[])
    os.remove(input_file_example['input_file'])


def test_enoent_outputfile_failed():
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=enoent_outfile_example,
            schema_type=BasicOutputFile, args=[])


def test_output_file_relative():
    mod = ArgSchemaParser(
        input_data=output_file_example, schema_type=BasicOutputFile, args=[])


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


def test_output_path(tmpdir):
    file_ = tmpdir.join('testoutput.json')
    args = ['--output_json', str(file_)]
    mod = ArgSchemaParser(args=args)


def test_output_path_cannot_write():
    with pytest.raises(mm.ValidationError):
        file_ = '/etc/notok/notalocation.json'
        args = ['--output_json', str(file_)]
        mod = ArgSchemaParser(args=args)


def test_output_path_noapath():
    with pytest.raises(mm.ValidationError):
        file_ = '@/afa\\//'
        args = ['--output_json', str(file_)]
        mod = ArgSchemaParser(args=args)


def test_simple_extension_write_overwrite(simple_extension_file):
    args = ['--input_json', str(simple_extension_file), '--test.b', '5']
    mod = ArgSchemaParser(schema_type=SimpleExtension, args=args)
    assert mod.args['test']['b'] == 5


def test_simple_extension_write_overwrite_list(simple_extension_file):
    args = ['--input_json', str(simple_extension_file),
            '--test.d', '6', '7', '8', '9']
    mod = ArgSchemaParser(schema_type=SimpleExtension, args=args)
    assert len(mod.args['test']['d']) == 4


numpy_array_test = {
    'a': [[1, 2],
          [3, 4]]
}


class NumpyFileuint16(ArgSchema):
    a = NumpyArray(
        dtype='uint16', required=True, metadata={
            'decription': 'list of lists representing numpy array'})


def test_numpy():
    mod = ArgSchemaParser(
        input_data=numpy_array_test, schema_type=NumpyFileuint16, args=[])
    assert mod.args['a'].shape == (2, 2)
    assert mod.args['a'].dtype == 'uint16'
