import argschema
from argschema.sources.yaml_source import YamlSource
from argschema.argschema_parser import ArgSchemaYamlParser
from test_classes import MySchema
import yaml
import pytest

class MyParser(ArgSchemaYamlParser):
    default_schema = MySchema

@pytest.fixture(scope='module')
def test_input_file(tmpdir_factory):
    file_in = tmpdir_factory.mktemp('test').join('test_input_yaml.yml')
    input_data = {
        'a':5,
        'nest':{
            'one':7,
            'two':False
        }
    }
    with open(str(file_in),'w') as fp:
        yaml.dump(input_data,fp,default_flow_style=False)
    return str(file_in)

def test_yaml_source(test_input_file):
    mod = MyParser(input_source= YamlSource(test_input_file), args=[])

def test_yaml_source_command(test_input_file):
    mod = MyParser(args = ['--input_yaml',test_input_file])