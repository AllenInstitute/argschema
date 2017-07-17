import argparse

import marshmallow as mm

class Slice(mm.fields.Field):
    '''Slice is a field type that supports a range or slice argument for
    selecting some subset of a larger dataset.  The syntax is identical to
    numpy slicing. Examples: "10:20", "40", ":30", "10:2:40"'''

    def __init__(self, *args, **kwargs):
        super(Slice, self).__init__(metadata={'description': 'slice the dataset'}, default=slice(None))

    def _deserialize(self, value, attr, obj):
        args = tuple([int(c) if c else None for c in value.split(':')])
        return slice(*args)

