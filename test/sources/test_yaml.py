import argschema
from argschema.sources.yaml_source import YamlSource, YamlSink
from argschema.sources.json_source import JsonSource, JsonSink
from argschema.sources.source import MultipleConfiguredSourceError
from argschema.argschema_parser import ArgSchemaYamlParser
from test_classes import MySchema, MyOutputSchema
import yaml
import pytest
import json

class MyParser(ArgSchemaYamlParser):
    default_schema = MySchema
    default_output_schema = MyOutputSchema

class MyDualParser(MyParser):
    default_configurable_sources = [JsonSource, YamlSource]
    default_configurable_sinks = [JsonSink, YamlSink]

input_data = {
    'a': 5,
    'nest': {
        'one': 7,
        'two': False
    }
}

@pytest.fixture(scope='module')
def test_yaml_input_file(tmpdir_factory):
    file_in = tmpdir_factory.mktemp('test').join('test_input_yaml.yml')
   
    with open(str(file_in), 'w') as fp:
        yaml.dump(input_data, fp, default_flow_style=False)
    return str(file_in)

@pytest.fixture(scope='module')
def test_json_input_file(tmpdir_factory):
    file_in = tmpdir_factory.mktemp('test').join('test_input_json.json')
   
    with open(str(file_in), 'w') as fp:
        json.dump(input_data, fp)
    return str(file_in)


def test_yaml_source(test_yaml_input_file):
    mod = MyParser(input_source=YamlSource(test_yaml_input_file), args=[])


def test_yaml_source_command(test_yaml_input_file):
    mod = MyParser(args=['--input_yaml', test_yaml_input_file])


def test_yaml_sink(test_yaml_input_file, tmpdir):
    outfile = tmpdir.join('test_out.yml')
    output_data = {
        'a': 3
    }
    mod = MyParser(input_source=YamlSource(test_yaml_input_file),
                   output_sink=YamlSink(str(outfile)))
    mod.output(output_data)

    with open(str(outfile), 'r') as fp:
        d = yaml.load(fp)
    output_data['b'] = "my value"
    assert (output_data == d)

def test_dual_parser(test_json_input_file,test_yaml_input_file):

    mod = MyDualParser(args=['--input_yaml', test_yaml_input_file])
    assert mod.args['a']==5
    assert mod.args['nest']==input_data['nest']

    mod = MyDualParser(args=['--input_json', test_json_input_file])
    assert mod.args['a']==5
    assert mod.args['nest']==input_data['nest']

def test_dual_parser_fail(test_json_input_file,test_yaml_input_file):
    with pytest.raises(MultipleConfiguredSourceError):
        mod = MyDualParser(args=['--input_yaml', test_yaml_input_file, '--input_json', test_json_input_file])

def test_dual_parser_output_fail(test_json_input_file,tmpdir):
    test_json_output = str(tmpdir.join('output.yml'))
    test_yaml_output = str(tmpdir.join('output.json'))
    with pytest.raises(MultipleConfiguredSourceError):
        mod = MyDualParser(args=['--input_json', test_json_input_file,
            '--output_json',test_json_output,
            '--output_yaml',test_yaml_output])
            