import pytest
from json_module import JsonModule, ModuleParameters,ParseError
import tempfile
import os
import json
import logging
from exceptions import IOError
from jsonschema import ValidationError
from marshmallow import Schema, fields, pprint

def test_bad_path():
    try:
        example = {
           "input_json":"a bad path",
           "output_json":"another example",
           "log_level":"DEBUG"}
        jm=JsonModule(input=example)
    except ParseError:
        assert True
        return
    assert False

def test_simple_example(tmpdir):
    file_in = tmpdir.join('test_input_json.json')
    file_in.write('nonesense')

    file_out = tmpdir.join('test_output.json')

    example = {
        "input_json":str(file_in),
        "output_json":str(file_out),
        "log_level":"ERROR"
    }
    jm=JsonModule(input=example)
    print jm.logger
    print jm.args

def test_log_catch():
    try:
        example = {
            "log_level":"NOTACHOICE"
        }
        jm = JsonModule(input=example)
    except ParseError:
        assert True
        return
    assert False

class TestExtension(Schema):
    a = fields.Str(metadata={'description':'a string'})
    b = fields.Int(metadata={'description':'an integer'})    
class SimpleExtension(ModuleParameters):
    test = fields.Nested(TestExtension)


def test_simple_extension_required():
    
    example1 = {}
    try:
        mod = JsonModule(input=example1,schema = SimpleExtension())
    except ParseError:
        assert True
        return 
    assert False

SimpleExtension_example_valid={
    'test':
        {
            'a':"hello",
            'b':1
        }
}

def test_simple_extension_pass(): 

    mod = JsonModule(input=SimpleExtension_example_valid,schema=SimpleExtension())
    assert mod.args['test']['a']=='hello'
    assert mod.args['test']['b']==1

def test_simple_extension_write_pass(tmpdir):
    file = tmpdir.join('testinput.json')
    file.write(json.dumps(SimpleExtension_example_valid))

    args = ['--input_json',str(file)]
    mod = JsonModule(schema=SimpleExtension(),args=args)    
    assert mod.args['test']['a']=='hello'
    assert mod.args['test']['b']==1
    assert mod.logger.getEffectiveLevel() == logging.ERROR

def test_simple_extension_write_debug_level(tmpdir):
    file = tmpdir.join('testinput.json')
    file.write(json.dumps(SimpleExtension_example_valid))
    args = ['--input_json',str(file),'--log_level','DEBUG']
    mod = JsonModule(schema=SimpleExtension(),args=args)
    assert mod.logger.getEffectiveLevel() == logging.DEBUG
