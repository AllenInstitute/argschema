import json
import os

import pytest
import yaml

import argschema
from argschema.sources.json_source import JsonSource, JsonSink
from argschema.sources.yaml_source import YamlSource, YamlSink
from argschema.sources.source import MultipleConfigurationError


class MyNestedSchema(argschema.schemas.DefaultSchema):
    one = argschema.fields.Int(required=True,description="nested integer")
    two = argschema.fields.Boolean(required=True,description="a nested boolean")

class MySchema(argschema.ArgSchema):
    a = argschema.fields.Int(required=True,description="parameter a")
    b = argschema.fields.Str(required=False,default="my value",description="optional b string parameter")
    nest = argschema.fields.Nested(MyNestedSchema,description="a nested schema")

class MyOutputSchema(argschema.schemas.DefaultSchema):
    a = argschema.fields.Int(required=True,description="parameter a")
    b = argschema.fields.Str(required=False,default="my value",description="optional b string parameter")

class MyParser(argschema.ArgSchemaParser):
    default_schema = MySchema

@pytest.fixture(scope='module')
def json_inp(tmpdir_factory):
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

@pytest.fixture(scope='module')
def yaml_inp(tmpdir_factory):
    file_in = tmpdir_factory.mktemp('test').join('test_input_yaml.yaml')
    input_data = {
        'a':6,
        'nest':{
            'one':8,
            'two':False
        }
    }

    with open(str(file_in),'w') as fp:
        yaml.dump(input_data, fp)

    return str(file_in)


@pytest.mark.parametrize("inp_sources", [
    JsonSource(), [JsonSource()], JsonSource, [JsonSource]
])
def test_json_input_args(json_inp, inp_sources):
    parser = MyParser(
        input_sources=inp_sources, 
        args=["--input_json", 
        json_inp]
    )

    assert parser.args["a"] == 5

@pytest.mark.parametrize("inp_sources", [
    JsonSource(), [JsonSource()], JsonSource, [JsonSource]
])
def test_json_input_data(json_inp, inp_sources):
    parser = MyParser(
        input_sources=inp_sources, 
        input_data={"input_json":json_inp}, 
        args=[]
    )

    assert parser.args["a"] == 5

def test_multisource_arg(yaml_inp):
    parser = MyParser(
        input_sources=[JsonSource, YamlSource],
        args=["--input_yaml", yaml_inp]
    )
    assert parser.args["a"] == 6

def test_multisource_arg_conflict(json_inp, yaml_inp):
    with pytest.raises(MultipleConfigurationError):
        parser = MyParser(
            input_sources=[JsonSource, YamlSource],
            args=["--input_yaml", yaml_inp, "--input_json", json_inp]
        )

def test_multisink(yaml_inp):
    out_path = os.path.join(os.path.dirname(yaml_inp), "out.json")

    parser = MyParser(
        output_schema_type=MyOutputSchema,
        input_sources=YamlSource,
        output_sinks=[YamlSink, JsonSink],
        args=["--input_yaml", yaml_inp, "--output_json", out_path]
    )

    parser.output({"a": 12, "b": "16"})
    with open(out_path, "r") as out_file:
        obt = json.load(out_file)
        assert obt["a"] == 12

def test_multisink_conflicting(yaml_inp, json_inp):
    yaml_out = os.path.join(os.path.dirname(yaml_inp), "out.yaml")
    json_out = os.path.join(os.path.dirname(json_inp), "out.json")

    with pytest.raises(MultipleConfigurationError):
        parser = MyParser(
            output_schema_type=MyOutputSchema,
            input_sources=[YamlSource],
            output_sinks=[JsonSink, YamlSink],
            args=["--output_yaml", yaml_out, "--output_json", json_out]
        )
