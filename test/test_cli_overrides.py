import pytest
import os
from decimal import Decimal
import datetime
import uuid
import numpy as np
import marshmallow as mm
from argschema import fields, ArgSchema, ArgSchemaParser
from argschema.schemas import DefaultSchema


@pytest.fixture(scope="module")
def inputdir(tmpdir_factory):
    return tmpdir_factory.mktemp("input")


@pytest.fixture(scope="module")
def inputfile(inputdir):
    inputfile = inputdir.join("inputfile.file")
    with open(str(inputfile), "w") as f:
        f.write("")
    return inputfile


@pytest.fixture(scope="module")
def outputdir(tmpdir_factory):
    return tmpdir_factory.mktemp("output")


@pytest.fixture(scope="module")
def outputfile(outputdir):
    return outputdir.join("outputfile.file")


@pytest.fixture
def test_data(inputdir, inputfile, outputdir, outputfile):
    # Function, Method, Constant, FormattedString aren't included
    # Field is not tested, should use mm.fields.Raw instead
    data = {
        "boolean": True,
        "date": "1776-07-04",
        "datetime": "1997-08-29T02:14:00-05:00",
        "decimal": 2.7,
        "dict": {"some_data": 5, "some_other_data": "hello"},
        "email": "anemail@example.com",
        "float": 3.14159,
        "inputdir": str(inputdir),
        "inputfile": str(inputfile),
        "integer": 10,
        "list": [300, 200, 800, 1000],
        "list_deprecated": [300, 200, 800, 1000],
        "localdatetime": "0001-01-01T00:00:00",
        "log_level": "ERROR",
        "nested": {"a": 1, "b": False},
        "number": 5.5,
        "numpyarray": [[1, 2], [3, 4]],
        "outputdir": str(outputdir),
        "outputfile": str(outputfile),
        "raw": "{1,2,3}",
        "slice": ":-1",
        "string": "Four score and seven years ago",
        "time": "05:00:00",
        "timedelta": "945890400",
        "url": "http://www.example.com",
        "uuid": "f4a1c5ee-c214-4a2b-9e62-e4ba6beb771b"
    }
    return data


@pytest.fixture
def deprecated_data():
    data = {
        "list_deprecated": [300, 200, 800, 1000],
    }
    return data



class MyNestedSchema(DefaultSchema):
    a = fields.Int(required=True)
    b = fields.Boolean(required=True)


class MySchema(ArgSchema):
    boolean = fields.Boolean(required=True)
    date = fields.Date(required=True)
    datetime = fields.DateTime(required=True)
    decimal = fields.Decimal(requied=True)
    dict = fields.Dict(required=True)
    email = fields.Email(required=True)
    float = fields.Float(required=True)
    inputdir = fields.InputDir(required=True)
    inputfile = fields.InputFile(required=True)
    integer = fields.Int(required=True)
    list = fields.List(fields.Int, required=True, cli_as_single_argument=True)
    localdatetime = fields.LocalDateTime(required=True)
    nested = fields.Nested(MyNestedSchema, required=True)
    number = fields.Number(required=True)
    numpyarray = fields.NumpyArray(dtype="uint8", required=True)
    outputdir = fields.OutputDir(required=True)
    outputfile = fields.OutputFile(required=True)
    raw = fields.Raw(required=True)
    slice = fields.Slice(required=True)
    string = fields.Str(required=True)
    time = fields.Time(required=True)
    timedelta = fields.TimeDelta(required=True)
    url = fields.URL(required=True)
    uuid = fields.UUID(required=True)


class MyDeprecatedSchema(ArgSchema):
    list_deprecated = fields.List(fields.Int, required=True)


def test_unexpected_input(test_data):
    with pytest.raises(SystemExit):
        ArgSchemaParser(test_data, schema_type=MySchema,
                        args=["--notanarg", "something"])


def test_no_deprecation(test_data):
    with pytest.warns(None) as record:
        ArgSchemaParser(test_data, schema_type=MySchema,
                        args=[])
    assert(len(record) == 0)


def test_override_boolean(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--boolean", "False"])
    assert(not mod.args["boolean"])
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--boolean", "invalid"])


def test_override_date(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--date", "1977-05-04"])
    assert(mod.args["date"] == datetime.date(1977, 5, 4))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--date", "invalid"])


def test_override_datetime(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--datetime", "1977-05-04T00:00:00"])
    assert(mod.args["datetime"] == datetime.datetime(1977, 5, 4, 0, 0, 0))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--datetime", "invalid"])


def test_override_decimal(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--decimal", "1.23456789"])
    assert(mod.args["decimal"] == Decimal("1.23456789"))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--decimal", "invalid"])


def test_override_dict(test_data):
    with pytest.raises(SystemExit):
        ArgSchemaParser(test_data, schema_type=MySchema,
                        args=["--dict", "{'a': 600, 'b': 'hello'}"])


def test_override_email(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--email", "batman@batcave.org"])
    assert(mod.args["email"] == "batman@batcave.org")
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--email", "invalid"])


def test_override_float(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--float", "1.23456789"])
    assert(abs(mod.args["float"] - 1.23456789) < 1e-10)
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--float", "invalid"])


def test_override_inputdir(test_data, tmpdir_factory):
    input2 = tmpdir_factory.mktemp("input2")
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--inputdir", str(input2)])
    assert(mod.args["inputdir"] == str(input2))
    assert(os.path.exists(mod.args["inputdir"]) and
           os.path.isdir(mod.args["inputdir"]))


def test_override_inputfile(test_data, tmpdir_factory):
    input2 = tmpdir_factory.mktemp("input3").join("input2.file")
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--inputfile", str(input2)])
    with open(str(input2), "w") as f:
        f.write("")
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--inputfile", str(input2)])
    assert(mod.args["inputfile"] == str(input2))
    assert(os.path.exists(mod.args["inputfile"]) and
           os.path.isfile(mod.args["inputfile"]))


def test_override_integer(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--integer", "1000"])
    assert(mod.args["integer"] == 1000)
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--integer", "invalid"])


def test_override_list(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--list", "[1000,3000]"])
    assert(mod.args["list"] == [1000, 3000])
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--list", "invalid"])


def test_override_list_deprecated(deprecated_data):
    with pytest.warns(FutureWarning):
        mod = ArgSchemaParser(deprecated_data, schema_type=MyDeprecatedSchema,
                              args=["--list_deprecated", "1000", "3000"])
        assert(mod.args["list_deprecated"] == [1000, 3000])
        with pytest.raises(mm.ValidationError):
            mod = ArgSchemaParser(deprecated_data,
                                  schema_type=MyDeprecatedSchema,
                                  args=["--list_deprecated", "[1000,3000]"])


def test_override_localdatetime(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--localdatetime", "1977-05-04T00:00:00"])
    assert(mod.args["localdatetime"] == datetime.datetime(1977, 5, 4, 0, 0, 0))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--localdatetime", "invalid"])


def test_override_log_level(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--log_level", "CRITICAL"])
    assert(mod.args["log_level"] == "CRITICAL")
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--log_level", "invalid"])


def test_override_nested(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--nested.a", "-55"])
    assert(mod.args["nested"]["a"] == -55)
    with pytest.raises(SystemExit):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--nested", "something"])
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--nested.a", "invalid"])
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--nested.b", "foo"])
    with pytest.raises(SystemExit):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--nested.c", "foo"])


def test_override_number(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--number", "10"])
    assert(mod.args["number"] == 10)
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--number", "invalid"])


def test_override_numpyarray(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--numpyarray", "[[4,3],[2,1]]"])
    assert(np.all(mod.args["numpyarray"] == np.array([[4, 3], [2, 1]])))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--numpyarray", "invalid"])


def test_override_outputdir(test_data, tmpdir_factory):
    output2 = tmpdir_factory.mktemp("output2")
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--outputdir", str(output2)])
    assert(mod.args["outputdir"] == str(output2))
    assert(os.path.exists(mod.args["outputdir"]) and
           os.path.isdir(mod.args["outputdir"]))


def test_override_outputfile(test_data, tmpdir_factory):
    output2 = tmpdir_factory.mktemp("output3").join("output2.file")
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--outputfile", str(output2)])
    assert(mod.args["outputfile"] == str(output2))
    assert(os.path.isdir(os.path.dirname(mod.args["outputfile"])))


def test_override_raw(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--raw", "this!{could}be$anything"])
    assert(mod.args["raw"] == "this!{could}be$anything")


def test_override_slice(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--slice", "800:3:9000"])
    assert(mod.args["slice"] == slice(800, 3, 9000))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--slice", "invalid"])


def test_override_string(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--string", "I am not a crook"])
    assert(mod.args["string"] == "I am not a crook")


def test_override_time(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--time", "11:11:00"])
    assert(mod.args["time"] == datetime.time(11, 11, 0))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--time", "invalid"])


def test_override_timedelta(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--timedelta", "0"])
    assert(mod.args["timedelta"] == datetime.timedelta(0))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--timedelta", "invalid"])


def test_override_url(test_data):
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--url", "http://www.alleninstitute.org"])
    assert(mod.args["url"] == "http://www.alleninstitute.org")
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--url", "invalid"])


def test_override_uuid(test_data):
    val = "1a66e457-4d0f-474a-bb4e-bee91e61e084"
    mod = ArgSchemaParser(test_data, schema_type=MySchema,
                          args=["--uuid", val])
    assert(mod.args["uuid"] == uuid.UUID(val))
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(test_data, schema_type=MySchema,
                              args=["--uuid", "invalid"])
