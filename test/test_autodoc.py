from argschema.autodoc import process_schemas
import pytest
from test_first_test import SimpleExtension,ExampleRecursiveSchema,RecursiveSchema,MyShorterExtension
from fields.test_slice import SliceSchema
from argschema.argschema_parser import ArgSchemaParser
import argschema
from test_argschema_parser import MyParser
import rstcheck
import docutils.utils

def validate_rst_lines(lines,level = docutils.utils.Reporter.WARNING_LEVEL):
    """validates a set of lines that would make up an rst file
    using rstcheck
    
    Parameters
    ==========
    lines: list[str]
        a list of lines that would compose some restructuredText
    level: docutils.utils.Reporter.WARNING_LEVEL
        the reporting level to hold this to
    Returns
    =======
    None

    Raises
    ======
    AssertionError
        If the lines contain any errors above the  level
    """
    long_string  = "\n".join(lines)
    results = list(rstcheck.check(long_string, report_level = level))
    print(results)
    assert(len(results)==0)

def test_autodoc():
    lines = []
    process_schemas(None, 'class', 'SimpleExtension', SimpleExtension, None, lines)
    assert('   This schema is designed to be a schema_type for an ArgSchemaParser object' in lines)
    validate_rst_lines(lines)

def test_autodoc_nested():
    lines = []
    process_schemas(None, 'class', 'ExampleRecursiveSchema', ExampleRecursiveSchema, None, lines)
    nested_field=next(line for line in lines if 'RecursiveSchema`' in line)
    assert('dict' in nested_field)
    validate_rst_lines(lines)
    
def test_autodoc_slice():
    lines = []
    process_schemas(None, 'class', 'SliceSchema', SliceSchema, None, lines)
    slice_field=next(line for line in lines if 'argschema.fields.slice.Slice' in line)
    assert(('unicode' in slice_field) or ('str' in slice_field))
    validate_rst_lines(lines)

def test_autodoc_recursive_nested():
    lines = []
    process_schemas(None, 'class', 'RecursiveSchema', RecursiveSchema, None, lines)
    nested_field=next(line for line in lines if 'RecursiveSchema`,' in line)
    assert('list' in nested_field)
    validate_rst_lines(lines)
    
def test_autodoc_list():
    lines=[]
    process_schemas(None, 'class', 'MyShorterExtension', MyShorterExtension, None, lines)
    list_field=next(line for line in lines if 'List' in line)
    assert('int' in list_field)
    validate_rst_lines(lines)

def test_autodoc_argschemaparser():
    lines = []
    process_schemas(None, 'class', 'ArgSchemaParser', ArgSchemaParser, None, lines)
    assert('  This class takes a ArgSchema as an input to parse inputs' in lines)
    validate_rst_lines(lines)

def test_autodoc_myparser():
    lines = []
    process_schemas(None, 'class', 'MyParser', MyParser, None, lines)
    assert('  This class takes a ArgSchema as an input to parse inputs' in lines)
    default_line = next(line for line in lines if 'default schema of type' in line)
    assert ':class:`~test_argschema_parser.MySchema`' in default_line
    validate_rst_lines(lines)

class SchemaWithQuotedDescriptions(argschema.ArgSchema):
    a = argschema.fields.Int(required=True, description='something that is "quoted" is problematic')

def test_autodoc_quotes():
    lines = []
    process_schemas(None,'class','SchemaWithQuotedDescriptions',SchemaWithQuotedDescriptions,None,lines)
    validate_rst_lines(lines)
