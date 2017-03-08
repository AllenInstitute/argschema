import pytest
from json_module import JsonModule, ModuleParameters
import tempfile
import os
import json
import logging
from exceptions import IOError
import marshmallow as mm

def test_bad_path():
    with pytest.raises(mm.ValidationError):
        example = {
           "input_json":"a bad path",
           "output_json":"another example",
           "log_level":"DEBUG"}
        jm=JsonModule(input_data=example,args=[])

def test_simple_example(tmpdir):
    file_in = tmpdir.join('test_input_json.json')
    file_in.write('nonesense')

    file_out = tmpdir.join('test_output.json')

    example = {
        "input_json":str(file_in),
        "output_json":str(file_out),
        "log_level":"CRITICAL"
    }
    jm=JsonModule(input_data=example,args=[])

    assert jm.args['log_level'] == 'CRITICAL'

def test_log_catch():
    with pytest.raises(mm.ValidationError):
        example = {
            "log_level":"NOTACHOICE"
        }
        jm = JsonModule(input_data=example,args=[])
        print jm.args


class TestExtension(mm.Schema):
    a = mm.fields.Str(metadata={'description':'a string'})
    b = mm.fields.Int(metadata={'description':'an integer'}) 
    c = mm.fields.Int(metadata={'description':'an integer'}, default=10) 

class SimpleExtension(ModuleParameters):
    test = mm.fields.Nested(TestExtension)


def test_simple_extension_required():
    with pytest.raises(mm.ValidationError):
        example1 = {}
        mod = JsonModule(input_data=example1,schema_type = SimpleExtension,args=[])
SimpleExtension_example_invalid={
    'test':
    {
        'a':5,
        'b':1
    }
}  
SimpleExtension_example_valid={
    'test':
        {
            'a':"hello",
            'b':1
        }
}
def test_simple_extension_fail():
    with pytest.raises(mm.ValidationError):
        mod = JsonModule(input_data=SimpleExtension_example_invalid,schema_type=SimpleExtension,args=[])

def test_simple_extension_pass(): 

    mod = JsonModule(input_data=SimpleExtension_example_valid,schema_type=SimpleExtension,args=[])
    assert mod.args['test']['a']=='hello'
    assert mod.args['test']['b']==1

def test_simple_extension_write_pass(tmpdir):
    file = tmpdir.join('testinput.json')
    file.write(json.dumps(SimpleExtension_example_valid))

    args = ['--input_json',str(file)]
    mod = JsonModule(schema_type=SimpleExtension,args=args)    
    assert mod.args['test']['a']=='hello'
    assert mod.args['test']['b']==1
    assert mod.logger.getEffectiveLevel() == logging.ERROR

def test_simple_extension_write_debug_level(tmpdir):
    file = tmpdir.join('testinput.json')
    file.write(json.dumps(SimpleExtension_example_valid))
    args = ['--input_json',str(file),'--log_level','DEBUG']
    mod = JsonModule(schema_type=SimpleExtension,args=args)
    assert mod.logger.getEffectiveLevel() == logging.DEBUG

def test_output_path(tmpdir):
    file = tmpdir.join('testoutput.json')
    args = ['--output_json',str(file)]
    mod = JsonModule(args=args)

def test_output_path_cannot_write():
    with pytest.raises(mm.ValidationError):
        file = '/etc/notok/notalocation.json'
        args = ['--output_json',str(file)]
        mod = JsonModule(args=args)

def test_output_path_noapath():
    with pytest.raises(mm.ValidationError):
        file = '@/afa\\//'
        args = ['--output_json',str(file)]
        mod = JsonModule(args=args)
