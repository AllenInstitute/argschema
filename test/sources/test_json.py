import json

import pytest

from argschema.sources import json_source


def test_json_source_get_dict(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("test_json_source").join("inp.json"))

    with open(path, "w") as jf:
        json.dump({"a": 12}, jf)

    source = json_source.JsonSource()
    source.load_config({"input_json": path})

    assert source.get_dict()["a"] == 12

def test_json_sink_put_dict(tmpdir_factory):
    path = str(tmpdir_factory.mktemp("test_json_source").join("out.json"))

    sink = json_source.JsonSink()
    sink.load_config({"output_json": path})
    sink.put_dict({"a": 13})
    
    with open(path, "r") as jf:
        assert json.load(jf)["a"] == 13