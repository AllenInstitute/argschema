import argschema
from argschema.sources.json_source import JsonSource
from test_classes import MySchema
import json
import pytest

class MyParser(argschema.ArgSchemaParser):
    default_schema = MySchema

@pytest.fixture(scope='module')
def test_input_file(tmpdir_factory):
    file_in = tmpdir_factory.mktemp('test').join('test_input_json.json')
    input_data = {
        'a':5,
        'nest':{
            'one':7,
            'two':False
        }
    }
    with open(str(file_in),'w') as fp:
        json.dump(input_data, fp)
    return str(file_in)

def test_json_source_input_data(test_input_file):
    mod = MyParser(
        input_sources=JsonSource(), 
        input_data={"input_json": test_input_file},
        args=[]
    )

# def test_json_source(test_input_file):
#     source = JsonSource(input_json=test_input_file)
#     mod = MyParser(input_sources= source, args=)

def test_json_source_command(test_input_file):
    mod = MyParser(args = ['--input_json',test_input_file])