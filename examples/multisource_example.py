"""This example shows you how to register multiple input sources for your executable, which users can then select from dynamically when running it. This feature makes your code a bit more flexible about the format of the input parameters.

There is a similar feature (not shown here) for specifying output sinks. It follows the same pattern.

Usage
-----
# you can load parameters from a yaml ...
$ python examples/multisource_example.py --input_yaml examples/multisource_example.yaml
{'a_subschema': {'an_int': 13}, 'log_level': 'ERROR', 'a_float': 16.7}

# ... or from an input json ...
$ python examples/multisource_example.py --input_json examples/multisource_example.json
{'a_float': 15.5, 'a_subschema': {'an_int': 12}, 'log_level': 'ERROR'}

# ... but not both
$ python examples/multisource_example.py --input_json examples/multisource_example.json --input_yaml examples/multisource_example.yaml
argschema.sources.source.MultipleConfigurationError: more then one InputSource configuration present in {'input_json': 'examples/multisource_example.json', 'input_yaml': 'examples/multisource_example.yaml'}

# command line parameters still override sourced ones
$ python examples/multisource_example.py --input_json examples/multisource_example.json --a_float 13.1
{'a_float': 13.1, 'a_subschema': {'an_int': 12}, 'log_level': 'ERROR'}

"""

import argschema

class SubSchema(argschema.schemas.DefaultSchema):
    an_int = argschema.fields.Int()

class MySchema(argschema.ArgSchema):
    a_subschema = argschema.fields.Nested(SubSchema)
    a_float = argschema.fields.Float()


def main():

    parser = argschema.ArgSchemaParser(
        schema_type=MySchema,
        input_sources=[ # each source provided here will be checked against command-line arguments
            argschema.sources.json_source.JsonSource, # ArgschemaParser includes this source by default
            argschema.sources.yaml_source.YamlSource
        ]
    )

    print(parser.args)

if __name__ == "__main__":
    main()