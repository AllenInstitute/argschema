import pytest
from argschema import ArgSchema
from argschema.fields import OutputFile, OutputDir
from argschema.fields.files import OutputDirModeException
from pydantic import Field, FilePath, DirectoryPath
import os
import sys
from pathlib import Path
from stat import S_IREAD, S_IRGRP, S_IROTH
import stat

# OUTPUT FILE TESTS
class BasicOutputFile(ArgSchema):
    output_file: OutputFile = Field(..., description='a simple output file')


output_file_example = {
    'output_file': 'output.file'
}

enoent_outfile_example = {
    'output_file': os.path.join('path', 'to', 'output.file')
}


def test_outputfile_no_write(tmpdir):
    # this doesn't work in windows

    outdir = Path(tmpdir / 'cannot_write_here')
    outdir.mkdir(mode=S_IREAD)
    
    outfile = outdir / 'test'

    with pytest.raises(ValueError):
        BasicOutputFile(output_file=str(outfile))
    
    outdir.chmod(0o666)


def test_outputfile_not_a_path():
    with pytest.raises(ValueError):
        BasicOutputFile(output_file=10)
        

def test_enoent_outputfile_failed():
    with pytest.raises(ValueError):
        BasicOutputFile(**enoent_outfile_example)


def test_output_file_relative():
    BasicOutputFile(**output_file_example)


def test_output_path(tmpdir):
    file_ = tmpdir.join('testoutput.json')
    ArgSchema(output_json=str(file_))


def test_output_path_cannot_write():
    with pytest.raises(ValueError):
        ArgSchema(output_json='/etc/notok/notalocation.json')


def test_output_path_noapath():
    with pytest.raises(ValueError):
        ArgSchema(output_json='@/afa\\//')


class BasicOutputDir(ArgSchema):
    output_dir: OutputDir = Field(..., description="basic output dir")


def test_output_dir_basic(tmpdir):
    outdir = tmpdir.mkdir('mytmp')
    
    BasicOutputDir(output_dir=str(outdir))
    

def test_output_dir_bad_permission(tmpdir):
    outdir = tmpdir.mkdir('no_read')
    if sys.platform == "win32":
        sd = win32security.GetFileSecurity(str(outdir), win32security.DACL_SECURITY_INFORMATION)
        everyone, domain, type = win32security.LookupAccountName ("", "Everyone")
        dacl = win32security.ACL ()
        dacl.AddAccessAllowedAce (win32security.ACL_REVISION, con.FILE_GENERIC_WRITE, everyone)
        sd.SetSecurityDescriptorDacl (1, dacl, 0)
        win32security.SetFileSecurity (str(outdir), win32security.DACL_SECURITY_INFORMATION, sd)
    else:
        outdir.chmod(0o222)
        
    with pytest.raises(ValueError):
        BasicOutputDir(output_dir=outdir)


def test_output_dir_bad_location():
    with pytest.raises(ValueError):
        BasicOutputDir(output_dir='///\\\//\/')

# INPUT FILE TESTS


class BasicInputFile(ArgSchema):
    input_file: FilePath = Field(..., description='a simple file')


input_file_example = {
    'input_file': 'relative.file'
}


def test_relative_file_input():
    with open(input_file_example['input_file'], 'w') as fp:
        fp.write("test")

    BasicInputFile(**input_file_example)
    
    os.remove(input_file_example['input_file'])


def test_relative_file_input_failed():
    with pytest.raises(ValueError):
        BasicInputFile(**input_file_example)


def test_access_inputfile_failed():
    with open(input_file_example['input_file'], 'w') as fp:
        fp.write('test')

    if sys.platform == "win32":
        sd = win32security.GetFileSecurity(
                input_file_example['input_file'],
                win32security.DACL_SECURITY_INFORMATION)
        everyone, domain, type = win32security.LookupAccountName ("", "Everyone")
        dacl = win32security.ACL ()
        dacl.AddAccessAllowedAce (win32security.ACL_REVISION, con.FILE_GENERIC_WRITE, everyone)
        sd.SetSecurityDescriptorDacl (1, dacl, 0)
        win32security.SetFileSecurity (
                input_file_example['input_file'],
                win32security.DACL_SECURITY_INFORMATION, sd)
    else:
        os.chmod(input_file_example['input_file'], 0o222)

    with pytest.raises(ValueError):
        BasicInputFile(**input_file_example)
    os.remove(input_file_example['input_file'])


# INPUTDIR TESTS
class BasicInputDir(ArgSchema):
    input_dir: DirectoryPath = Field(description='a simple file')


def test_basic_inputdir(tmpdir):
    BasicInputDir(input_dir=str(tmpdir))

def test_bad_inputdir():
    with pytest.raises(ValueError):
        BasicInputDir(input_dir='not_a_dir')

@pytest.mark.skipif(sys.platform == "win32",
                    reason="can't get working after migrating from appveyor to"
                           "github-actions.")
def test_inputdir_no_access(tmpdir):
    input_dir = tmpdir.mkdir('no_access')
    if sys.platform == "win32":
        sd = win32security.GetFileSecurity(
                str(input_dir),
                win32security.DACL_SECURITY_INFORMATION)
        everyone, domain, type = win32security.LookupAccountName ("", "Everyone")
        dacl = win32security.ACL ()
        dacl.AddAccessAllowedAce (win32security.ACL_REVISION, con.FILE_GENERIC_WRITE, everyone)
        sd.SetSecurityDescriptorDacl (1, dacl, 0)
        win32security.SetFileSecurity (
                str(input_dir),
                win32security.DACL_SECURITY_INFORMATION, sd)
    else:
        input_dir.chmod(0o222)
        
    with pytest.raises(ValueError):
        BasicInputDir(input_dir=str(input_dir))