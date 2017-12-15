import argschema
from argschema.sources.json_source import JsonSource
from argschema.sources.yaml_source import YamlSource
from test_argschema_parser import MyParser
import json

def test_json_source(tmpdir):
    file_in = tmpdir.join('test_input_json.json')
    input_data = {
        'a':5,
        'nest':{
            'one':7,
            'two':False
        }
    }
    json.dump(input_data,file_in)
    mod = MyParser(input_source= JsonSource(str(file_in)), args=[])

    