import pytest
import marshmallow as mm 
import argschema
import binascii
from pathlib import Path
from argschema import ArgSchema, ArgSchemaParser
from argschema.fields import ImageBatch

# Github user mathiasbynens maintains a cool repository of small files at
# https://github.com/mathiasbynens/small.git.  These binary encodings come from
# 'xxd -p tiff.tif', for example.

tinytiff = binascii.unhexlify((
    '4d4d002a0000000800070100000300000001000100000101000300000001'
    '000100000106000300000001000000000111000300000001000000000117'
    '00030000000100010000011a00050000000100000064011b000500000001'
    ))

invalid = binascii.unhexlify('0a0b0c0d1235')

class ImageTestSchema(ArgSchema):
    imageset = ImageBatch()

def test_valid_image_batch(tmpdir):
    batch = ['img1.tif', 'img2.tif', 'img3.tif']

    for name in batch:
        tmpdir.join(name).write(tinytiff)

    args = ArgSchemaParser(
            input_data = { 'imageset': tmpdir }, 
            schema_type = ImageTestSchema).args

    assert args['imageset'] == [Path(str(tmpdir.join(n))) for n in batch]

def test_invalid_image_batch(tmpdir):
    batch = ['img1', 'img2', 'img3']

    for name in batch:
        tmpdir.join(name).write(invalid)

    with pytest.raises(mm.ValidationError):
        ArgSchemaParser(
                input_data = { 'imageset': tmpdir }, 
                schema_type = ImageTestSchema)

