from argschema.autodoc import process_schemas
import pytest
from test_first_test import SimpleExtension,ExampleRecursiveSchema,RecursiveSchema,MyShorterExtension
from fields.test_slice import SliceSchema
from argschema.argschema_parser import ArgSchemaParser
import argschema
from test_argschema_parser import MyParser

def test_autodoc():
    lines = []
    process_schemas(None, 'class', 'SimpleExtension', SimpleExtension, None, lines)
    assert('   This schema is designed to be a schema_type for an ArgSchemaParser object' in lines)
    
def test_autodoc_nested():
    lines = []
    process_schemas(None, 'class', 'ExampleRecursiveSchema', ExampleRecursiveSchema, None, lines)
    nested_field=next(line for line in lines if 'RecursiveSchema`' in line)
    assert('dict' in nested_field)

def test_autodoc_slice():
    lines = []
    process_schemas(None, 'class', 'SliceSchema', SliceSchema, None, lines)
    slice_field=next(line for line in lines if 'argschema.fields.slice.Slice' in line)
    assert('str' in slice_field)

def test_autodoc_recursive_nested():
    lines = []
    process_schemas(None, 'class', 'RecursiveSchema', RecursiveSchema, None, lines)
    nested_field=next(line for line in lines if 'RecursiveSchema`,' in line)
    assert('list' in nested_field)
    
def test_autodoc_list():
    lines=[]
    process_schemas(None, 'class', 'MyShorterExtension', MyShorterExtension, None, lines)
    list_field=next(line for line in lines if 'List' in line)
    assert('int' in list_field)

def test_autodoc_argschemaparser():
    lines = []
    process_schemas(None, 'class', 'ArgSchemaParser', ArgSchemaParser, None, lines)
    assert('  This class takes a ArgSchema as an input to parse inputs' in lines)

def test_autodoc_myparser():
    lines = []
    process_schemas(None, 'class', 'MyParser', MyParser, None, lines)
    assert('  This class takes a ArgSchema as an input to parse inputs' in lines)
    default_line = next(line for line in lines if 'default schema of type' in line)
    assert ':class:`~test_argschema_parser.MySchema`' in default_line

class SchemaWithQuotedDescriptions(argschema.ArgSchema):
    a = argschema.fields.Int(required=True, description='something that is "quoted" is problematic')

def test_autodoc_quotes():
    input_data = {
        'a':5
    }
    mod = argschema.ArgSchemaParser(input_data = input_data,
                                    schema_type=SchemaWithQuotedDescriptions)
