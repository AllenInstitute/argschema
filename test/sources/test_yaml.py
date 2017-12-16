import argschema
from argschema.sources.yaml_source import YamlSource, YamlSink
from argschema.argschema_parser import ArgSchemaYamlParser
from test_classes import MySchema, MyOutputSchema
import yaml
import pytest


class MyParser(ArgSchemaYamlParser):
    default_schema = MySchema
    default_output_schema = MyOutputSchema


@pytest.fixture(scope='module')
def test_input_file(tmpdir_factory):
    file_in = tmpdir_factory.mktemp('test').join('test_input_yaml.yml')
    input_data = {
        'a': 5,
        'nest': {
            'one': 7,
            'two': False
        }
    }
    with open(str(file_in), 'w') as fp:
        yaml.dump(input_data, fp, default_flow_style=False)
    return str(file_in)


def test_yaml_source(test_input_file):
    mod = MyParser(input_source=YamlSource(test_input_file), args=[])


def test_yaml_source_command(test_input_file):
    mod = MyParser(args=['--input_yaml', test_input_file])


def test_yaml_sink(test_input_file, tmpdir):
    outfile = tmpdir.join('test_out.yml')
    output_data = {
        'a': 3
    }
    mod = MyParser(input_source=YamlSource(test_input_file),
                   output_sink=YamlSink(str(outfile)))
    mod.output(output_data)

    with open(str(outfile), 'r') as fp:
        d = yaml.load(fp)
    output_data['b'] = "my value"
    assert (output_data == d)
