from argschema.autodoc import process_schemas
import pytest
from test_first_test import SimpleExtension,ExampleRecursiveSchema,RecursiveSchema,MyShorterExtension
from fields.test_slice import SliceSchema
from argschema.argschema_parser import ArgSchemaParser

def test_autodoc():
    lines = []
    process_schemas(None, 'class', 'SimpleExtension', SimpleExtension, None, lines)
    assert('   This schema is designed to be a schema_type for an ArgSchemaParser object' in lines)
    
def test_autodoc_nested():
    lines = []
    process_schemas(None, 'class', 'ExampleRecursiveSchema', ExampleRecursiveSchema, None, lines)
    nested_field=next(line for line in lines if 'Nested' in line)
    assert('~RecursiveSchema' in nested_field)
    assert('dict' in nested_field)

def test_autodoc_slice():
    lines = []
    process_schemas(None, 'class', 'SliceSchema', SliceSchema, None, lines)
    slice_field=next(line for line in lines if 'argschema.fields.slice.Slice' in line)
    assert('?' in slice_field)

def test_autodoc_recursive_nested():
    lines = []
    process_schemas(None, 'class', 'RecursiveSchema', RecursiveSchema, None, lines)
    nested_field=next(line for line in lines if 'Nested' in line)
    assert('~RecursiveSchema' in nested_field)
    assert('list' in nested_field)
    
def test_autodoc_list():
    lines=[]
    process_schemas(None, 'class', 'MyShorterExtension', MyShorterExtension, None, lines)
    list_field=next(line for line in lines if 'List' in line)
    assert('d' in list_field)
    assert('List` : int' in list_field)

def test_autodoc_argschemaparser():
    lines = []
    process_schemas(None, 'class', 'ArgSchemaParser', ArgSchemaParser, None, lines)
    assert('  This class takes a ArgSchema as an input to parse inputs' in lines)
