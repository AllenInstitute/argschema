import pytest
import yaml

from argschema.sources import yaml_source

def test_json_source_get_dict(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("test_yaml_source").join("inp.yaml"))

    with open(path, "w") as jf:
        yaml.dump({"a": 12}, jf)

    source = yaml_source.YamlSource()
    source.load_config({"input_yaml": path})

    assert source.get_dict()["a"] == 12

def test_json_sink_put_dict(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("test_yaml_source").join("out.yaml"))

    sink = yaml_source.YamlSink()
    sink.load_config({"output_yaml": path})
    sink.put_dict({"a": 13})
    
    with open(path, "r") as jf:
        assert yaml.load(jf)["a"] == 13