from argschema import ArgSchemaParser, ArgSchema
from argschema.schemas import DefaultSchema
from argschema.fields import Str,Int,NumpyArray
import json
import numpy as np
import pytest
import marshmallow as mm
import os

class MyOutputSchema(DefaultSchema):
    a = Str(required=True, description="a simple string")
    b = Int(default = 5 , description ="a default integer")
    M = NumpyArray(required=True, description="a numpy array of answers")

def test_output(tmpdir):
    file_out = tmpdir.join('test_output.json')
    input_parameters = {
        'output_json':str(file_out)
    }
    mod = ArgSchemaParser(input_data = input_parameters,
                          output_schema_type = MyOutputSchema,
                          args=[])
    M=[[5,5],[7,2]]
    Mnp = np.array(M)
    output = {
        "a":"example",
        "M":Mnp  
    }
    expected_output = {
        "a":"example",
        "b":5,
        "M":M
    }
    mod.output(output)
    with open(str(file_out),'r') as fp:
        actual_output = json.load(fp)
    assert actual_output == expected_output
    

def test_output_unvalidated(tmpdir):
    file_out = tmpdir.join('test_output_unvalidated.json')
    input_parameters = {
        'output_json':str(file_out)
    }
    mod = ArgSchemaParser(input_data = input_parameters,
                          args=[])

    output = {
        "a":"example",
    }
    mod.output(output)
    with open(str(file_out),'r') as fp:
        actual_output = json.load(fp)
    assert actual_output == output

def test_bad_output(tmpdir):
    file_out = tmpdir.join('test_output_bad.json')
    input_parameters = {
        'output_json':str(file_out)
    }
    mod = ArgSchemaParser(input_data = input_parameters,
                          output_schema_type = MyOutputSchema,
                          args=[])
    M=[[5,5],[7,2]]
    Mnp = np.array(M)
    output = {
        "a":"example",
        "b":"not a number",
        "M":Mnp  
    }

    with pytest.raises(mm.ValidationError):
        mod.output(output)

def test_alt_output(tmpdir):
    file_out = tmpdir.join('test_output.json')
    file_out_2 = tmpdir.join('test_output_2.json')
    input_parameters = {
        'output_json':str(file_out)
    }
    mod = ArgSchemaParser(input_data = input_parameters,
                          output_schema_type = MyOutputSchema,
                          args=[])
    M=[[5,5],[7,2]]
    Mnp = np.array(M)
    output = {
        "a":"example",
        "M":Mnp  
    }
    expected_output = {
        "a":"example",
        "b":5,
        "M":M
    }
    mod.output(output,str(file_out_2))
    with open(str(file_out_2),'r') as fp:
        actual_output = json.load(fp)
    assert actual_output == expected_output

def test_tmp_output_cleanput(tmpdir):
    file_out = tmpdir.join('test_output.json')
    input_parameters = {
        'output_json':str(file_out)
    }
    mod = ArgSchemaParser(input_data = input_parameters,
                          output_schema_type = MyOutputSchema,
                          args=[])
    files = os.listdir(str(tmpdir))
    assert len(files)==0