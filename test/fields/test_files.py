import pytest
from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import InputFile, OutputFile, InputDir, OutputDir
import marshmallow as mm
import os
import stat


# OUTPUT FILE TESTS
class BasicOutputFile(ArgSchema):
    output_file = OutputFile(required=True,
                             description='a simple output file')


output_file_example = {
    'output_file': 'output.file'
}

enoent_outfile_example = {
    'output_file': os.path.join('path', 'to', 'output.file')
}


def test_outputfile_no_write(tmpdir):
    outdir = tmpdir.mkdir('cannot_write_here')
    outdir.chmod(0o222)
    outfile = outdir.join('test')
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(input_data={'output_file': str(outfile)},
                              schema_type=BasicOutputFile)


def test_outputfile_not_a_path():
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(input_data={'output_file': 10},
                              schema_type=BasicOutputFile, args=[])


def test_enoent_outputfile_failed():
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=enoent_outfile_example,
            schema_type=BasicOutputFile, args=[])


def test_output_file_relative():
    mod = ArgSchemaParser(
        input_data=output_file_example, schema_type=BasicOutputFile, args=[])


def test_output_path(tmpdir):
    file_ = tmpdir.join('testoutput.json')
    args = ['--output_json', str(file_)]
    mod = ArgSchemaParser(args=args)


def test_output_path_cannot_write():
    with pytest.raises(mm.ValidationError):
        file_ = '/etc/notok/notalocation.json'
        args = ['--output_json', str(file_)]
        mod = ArgSchemaParser(args=args)


def test_output_path_noapath():
    with pytest.raises(mm.ValidationError):
        file_ = '@/afa\\//'
        args = ['--output_json', str(file_)]
        mod = ArgSchemaParser(args=args)


class BasicOutputDir(ArgSchema):
    output_dir = OutputDir(required=True, description="basic output dir")


def test_output_dir_basic(tmpdir):
    outdir = tmpdir.mkdir('mytmp')
    output_dir_example = {
        'output_dir': str(outdir)
    }
    mod = ArgSchemaParser(schema_type=BasicOutputDir,
                          input_data=output_dir_example,
                          args=[])


def test_output_dir_bad_permission(tmpdir):
    outdir = tmpdir.mkdir('no_write')
    outdir.chmod(0o222)
    output_dir_example = {
        'output_dir': outdir
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(schema_type=BasicOutputDir,
                              input_data=output_dir_example,
                              args=[])


def test_output_dir_bad_location():
    output_dir_example = {
        'output_dir': '///\\\//\/'
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(schema_type=BasicOutputDir,
                              input_data=output_dir_example,
                              args=[])


class ModeOutputDirSchema(ArgSchema):
    output_dir = OutputDir(required=True,
                           description="775 output directory",
                           mode=0o775)


def test_mode_output_osdir(tmpdir):
    outdir = tmpdir.join('mytmp')
    output_dir_example = {
        'output_dir': str(outdir)
    }
    mod = ArgSchemaParser(schema_type=ModeOutputDirSchema,
                          input_data=output_dir_example,
                          args=[])
    assert((os.stat(mod.args['output_dir']).st_mode & 0o777) == 0o775)


def test_failed_mode(tmpdir):
    outdir = tmpdir.join('mytmp_failed')
    os.makedirs(str(outdir))
    os.chmod(str(outdir), 0o777)
    output_dir_example = {
        'output_dir': str(outdir)
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(schema_type=ModeOutputDirSchema,
                              input_data=output_dir_example,
                              args=[])

# INPUT FILE TESTS


class BasicInputFile(ArgSchema):
    input_file = InputFile(required=True,
                           description='a simple file')


input_file_example = {
    'input_file': 'relative.file'
}


def test_relative_file_input():
    with open(input_file_example['input_file'], 'w') as fp:
        fp.write("test")
    mod = ArgSchemaParser(
        input_data=input_file_example, schema_type=BasicInputFile, args=[])
    os.remove(input_file_example['input_file'])


def test_relative_file_input_failed():
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=input_file_example, schema_type=BasicInputFile, args=[])


def test_access_inputfile_failed():
    with open(input_file_example['input_file'], 'w') as fp:
        fp.write('test')
    os.chmod(input_file_example['input_file'], 0o222)
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(
            input_data=input_file_example, schema_type=BasicInputFile, args=[])
    os.remove(input_file_example['input_file'])


# INPUTDIR TESTS
class BasicInputDir(ArgSchema):
    input_dir = InputDir(required=True,
                         description='a simple file')


def test_basic_inputdir(tmpdir):
    input_data = {
        'input_dir': str(tmpdir)
    }
    mod = ArgSchemaParser(input_data=input_data,
                          schema_type=BasicInputDir, args=[])


def test_bad_inputdir():
    input_data = {
        'input_dir': 'not_a_dir'
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(input_data=input_data,
                              schema_type=BasicInputDir, args=[])


def test_inputdir_no_access(tmpdir):
    input_dir = tmpdir.mkdir('no_access')
    input_dir.chmod(0o222)
    input_data = {
        'input_dir': str(input_dir)
    }
    with pytest.raises(mm.ValidationError):
        mod = ArgSchemaParser(input_data=input_data,
                              schema_type=BasicInputDir, args=[])
