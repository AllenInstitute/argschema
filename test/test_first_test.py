import pytest
from json_module import JsonModule
import tempfile
import os
import json
import logging
from exceptions import IOError
from jsonschema import ValidationError

def test_bad_path():
    try:
        example = {
           "input_json":"a bad path",
           "output_json":"another example",
           "log_level":"DEBUG"}
        jm=JsonModule(input=example)
    except IOError:
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
    except ValidationError:
        assert True
        return
    assert False

class SimpleExtension(JsonModule):
    
        def __init__(self,input=None,schema_extension=None,*args,**kwargs):
            schema = {
                "description":"a generic module ex",
                "properties":{
                    "test":{
                        "type":"object",
                        "title":"test Parameters",
                        "description":"This specifies parameters for connecting to test",
                        "properties":{
                            "a":{
                                "type":"string",
                                "description":"a string"
                                },
                            "b":{
                                "type":"integer",
                                "description":"an integer"
                                }              
                        },
                        "required": [ "a" ]                
                    }
                }
            }
            schema=self.add_to_schema(schema,schema_extension)
            JsonModule.__init__(self,*args,input=input,schema_extension=schema,**kwargs)
            #self.render = renderapi.render.connect(**self.args['render'])

def test_simple_extension_required():
    
    example1 = {}
    try:
        mod = SimpleExtension(example1)
    except ValidationError:
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

    mod = SimpleExtension(input=SimpleExtension_example_valid)
    assert mod.args['test']['a']=='hello'
    assert mod.args['test']['b']==1

def test_simple_extension_write_pass(tmpdir):
    file = tmpdir.join('testinput.json')
    file.write(json.dumps(SimpleExtension_example_valid))

    args = ['--input_json',str(file)]
    mod = SimpleExtension(args=args)
    assert mod.args['test']['a']=='hello'
    assert mod.args['test']['b']==1
    assert mod.logger.getEffectiveLevel() == logging.ERROR

def test_simple_extension_write_debug_level(tmpdir):
    file = tmpdir.join('testinput.json')
    file.write(json.dumps(SimpleExtension_example_valid))

    args = ['--input_json',str(file),'--log_level','DEBUG']
    mod = SimpleExtension(args=args)
    assert mod.args['log_level']=='DEBUG'
