User Guide
=====================================
Installation
------------
install via source code

::

    $ python setup.py install

or pip

::

    $ pip install argschema

Your First Module
------------------

.. literalinclude:: ../../examples/mymodule.py
    :caption: mymodule.py

running this code produces 

.. code-block:: bash

    $ python mymodule.py
    {'a': 42, 'log_level': u'ERROR'}
    $ python mymodule.py --a 2
    {'a': 2, 'log_level': u'ERROR'}
    $ python mymodule.py --a 2 --log_level WARNING
    {'a': 2, 'log_level': u'WARNING'}
    WARNING:argschema.argschema_parser:this program does nothing useful
    $ python mymodule.py -h
    usage: mymodule.py [-h] [--a A] [--output_json OUTPUT_JSON]
                    [--log_level LOG_LEVEL] [--input_json INPUT_JSON]

    optional arguments:
    -h, --help            show this help message and exit
    --a A                 my first parameter
    --output_json OUTPUT_JSON
                            file path to output json file
    --log_level LOG_LEVEL
                            set the logging level of the module
    --input_json INPUT_JSON
                            file path of input json file

Great you are thinking, that is basically argparse, congratulations! 

But there is more.. you can also give your module a dictionary in an interactive session

::

    >>> from argschema import ArgSchemaParser
    >>> from mymodule import MySchema
    >>> d = {'a':5}
    >>> mod = ArgSchemaParser(input_data=d,schema_type=MySchema)
    >>> print(mod.args)
    {'a': 5, 'log_level': u'ERROR'}


or you write out a json file and pass it the path on the command line

.. literalinclude:: ../../examples/myinput.json
    :caption: myinput.json

.. code-block:: bash

    $ python mymodule.py --input_json myinput.json
    {'a': 99, 'log_level': u'ERROR', 'input_json': u'myinput.json'}

or override a parameter if you want

.. code-block:: bash

    $ python mymodule.py --input_json myinput.json --a 100
    {'a': 100, 'log_level': u'ERROR', 'input_json': u'myinput.json'}

plus, no matter how you give it parameters, they will always be validated,
before any of your code runs.

Whether from the command line

.. code-block:: bash

    $ python mymodule.py --input_json myinput.json --a 5!
    usage: mymodule.py [-h] [--a A] [--output_json OUTPUT_JSON]
                    [--log_level LOG_LEVEL] [--input_json INPUT_JSON]
    mymodule.py: error: argument --a: invalid int value: '5!'

or from a dictionary
::

    >>> from argschema import ArgSchemaParser
    >>> from mymodule import MySchema
    >>> d={'a':'hello'}
    >>> mod = ArgSchemaParser(input_data=d,schema_type=MySchema)
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/Users/forrestcollman/argschema/argschema/argschema_parser.py", line 159, in __init__
            raise mm.ValidationError(json.dumps(result.errors, indent=2))
        marshmallow.exceptions.ValidationError: {
        "a": [
            "Not a valid integer."
        ]
        }


Fields
------
argschema uses marshmallow (http://marshmallow.readthedocs.io/)
under the hood to define the parameters schemas.  It comes with a basic set of fields
that you can use to define your schemas. One powerful feature of Marshmallow is that you
can define custom fields that do arbitrary validation.
:class:`argschema.fields` contains all the built-in marshmallow fields, 
but also some useful custom ones, 
such as :class:`argschema.fields.InputFile`, 
:class:`argschema.fields.OutputFile`, 
:class:`argschema.fields.InputDir` that validate that the paths exist and have the proper
permissions to allow files to be read or written.

Other fields, such as :class:`argschema.fields.NumpyArray` will deserialize ordered lists of lists
directly into a numpy array of your choosing.

Finally, an important Field to know is :class:`argschema.fields.Nested`, which allows you to define
heirarchical nested structures.  Note, that if you use Nested schemas, your Nested schemas should
subclass :class:`argschema.schemas.DefaultSchema` in order that they properly fill in default values,
as :class:`marshmallow.Schema` does not do that by itself.

The template_module example shows how you might combine these features
to define a more complex parameter structure.

.. literalinclude:: ../../examples/template_module.py
    :caption: template_module.py

so now if run the example commands found in run_template.sh

.. literalinclude:: ../../examples/input.json
    :caption: input.json

.. code-block:: bash

    $ python template_module.py \
        --output_json output_command.json \
        --inc.name from_command \
        --inc.increment 2
    {u'name': u'from_command', u'inc_array': [2.0, 4.0, 7.0]}
    $ python template_module.py \
        --input_json input.json \
        --output_json output_fromjson.json
    {u'name': u'from_json', u'inc_array': [4.0, 3.0, 2.0]}
    $ python template_module.py
    {u'name': u'from_dictionary', u'inc_array': [5.0, 7.0, 10.0]}


Command-Line Specification
--------------------------
As mentioned in the section `Your First Module`_, argschema supports
setting arguments at the command line, along with providing arguments
either in an input json or directly passing a dictionary as `input_data`.
Values passed at the command line will take precedence over those
passed to the parser or in the input json.

Arguments are specified with `--argument_name <value>`, where value is
passed by the shell. If there are spaces in the value, it will need to be
wrapped in quotes, and any special characters will need to be escaped
with \. Booleans are set with True or 1 for true and False or 0 for false.

An exception to this rule is list formatting. If a schema contains a
:class:`~marshmallow.fields.List` and does not set the
`cli_as_single_argument` keyword argument to True, lists will be parsed
as `--list_name <value1> <value2> ...`. In argschema 2.0 lists will be
parsed in the same way as other arguments, as it allows more flexibility
in list types and more clearly represents the intended data structure.

An example script showing old and new list settings:

.. literalinclude:: ../../examples/deprecated_example.py
    :caption: deprecated_example.py

Running this code can demonstrate the differences in command-line usage:

.. code-block:: bash

    $ python deprecated_example.py --help
    FutureWarning: '--list_old' is using old-style command-line syntax
    with each element as a separate argument. This will not be supported
    in argschema after 2.0. See http://argschema.readthedocs.io/en/master/user/intro.html#command-line-specification
    for details.
    warnings.warn(warn_msg, FutureWarning)
    usage: deprecated_example.py [-h] [--input_json INPUT_JSON]
                                 [--output_json OUTPUT_JSON]
                                 [--log_level LOG_LEVEL]
                                 [--list_old [LIST_OLD [LIST_OLD ...]]]
                                 [--list_new LIST_NEW]

    optional arguments:
      -h, --help            show this help message and exit

    MySchema:
      --input_json INPUT_JSON
                            file path of input json file
      --output_json OUTPUT_JSON
                            file path to output json file
      --log_level LOG_LEVEL
                            set the logging level of the module (default=ERROR)
      --list_old [LIST_OLD [LIST_OLD ...]]
                            float list with deprecated cli (default=[1.1, 2.2,
                            3.3])
      --list_new LIST_NEW   float list with supported cli (default=[4.4, 5.5,
                            6.6])
    $ python deprecated_example.py --list_old 9.1 8.2 7.3 --list_new [6.4,5.5,4.6]
    FutureWarning: '--list_old' is using old-style command-line syntax
    with each element as a separate argument. This will not be supported
    in argschema after 2.0. See http://argschema.readthedocs.io/en/master/user/intro.html#command-line-specification
    for details.
    warnings.warn(warn_msg, FutureWarning)
    {'log_level': 'ERROR', 'list_new': [6.4, 5.5, 4.6], 'list_old': [9.1, 8.2, 7.3]}

We can explore some typical examples of command line usage with the following script:

.. literalinclude:: ../../examples/cli_example.py
    :caption: cli_example.py

.. code-block:: bash

    $ python cli_example.py --help
    usage: cli_example.py [-h] [--input_json INPUT_JSON]
                          [--output_json OUTPUT_JSON] [--log_level LOG_LEVEL]
                          [--array ARRAY] [--string_list STRING_LIST]
                          [--int_list INT_LIST] [--nested.a NESTED.A]
                          [--nested.b NESTED.B]

    optional arguments:
      -h, --help            show this help message and exit

    MySchema:
      --input_json INPUT_JSON
                            file path of input json file
      --output_json OUTPUT_JSON
                            file path to output json file
      --log_level LOG_LEVEL
                            set the logging level of the module (default=ERROR)
      --array ARRAY         my example array (default=[[1, 2, 3], [4, 5, 6]])
      --string_list STRING_LIST
                            list of lists of strings (default=[['hello', 'world'],
                            ['lists!']])
      --int_list INT_LIST   list of ints (default=[1, 2, 3])

    nested:
      --nested.a NESTED.A   my first parameter (default=42)
      --nested.b NESTED.B   my boolean (default=True)

We can set some values and observe the output:

::

    $ python cli_example.py --nested.b 0 --string_list "[['foo','bar'],['baz','buz']]"
    {'int_list': [1, 2, 3], 'string_list': [['foo', 'bar'], ['baz', 'buz']], 'array': array([[1, 2, 3],
       [4, 5, 6]], dtype=uint8), 'log_level': 'ERROR', 'nested': {'a': 42, 'b': False}}

If we try to set a field in a way the parser can't cast the variable (for
example, having an invalid literal) we will see a casting validation error:

::

    $ python cli_example.py --array [1,foo,3]
    Traceback (most recent call last):
      File "cli_example.py", line 25, in <module>
        mod = ArgSchemaParser(schema_type=MySchema)
      ...
    marshmallow.exceptions.ValidationError: {
      "array": [
        "Command-line argument can't cast to NumpyArray"
      ]
    }

argschema does not support setting :class:`~marshmallow.fields.Dict` at the
command line.

Alternate Sources/Sinks
-----------------------
A json files are just one way that you might decide to store module parameter dictionaries or outputs. 
For example, yaml is another perfectly reasonable choice for storing nested key values stores. Argschema by default provides
json support because that is what we use most frequently at the Allen Institute, however we have generalized the concept
to allow ArgSchemaParser to plugin alternative "sources" and "sinks" of parameters.  

You can pass an ArgSchemaParser an :class:`argschema.sources.ArgSource` object which implements a get_dict method,
and :class:`argschema.ArgSchemaParser` will get its input parameters from that dictionary.

Similarly you can pass an :class:`argschema.sources.ArgSink` object which implements a put_dict method,
and :class:`argschema.ArgSchemaParser.output` will output the dictionary however that :class:`argschema.sources.ArgSink` specifies it should.

Finally, both :class:`argschema.sources.ArgSource` and :class:`argschema.sources.ArgSink` have a property called ConfigSchema,
which is a :class:`marshmallow.Schema` for how to deserialize the kwargs to it's init class.  
For example, the default :class:`argschema.sources.json_source.JsonSource.ConfigSchema` has one string field of 'input_json'. 
This is how :class:`argschema.ArgSchemaParser` is told what keys and values should be read to initialize the :class:`argschema.sources.ArgSource` 
or  :class:`argschema.sources.ArgSink`.  

So for example, if you wanted to define a :class:`argschema.sources.ArgSource` which loaded a dictionary from a particular host, port and url,
and a module which had a command line interface for setting that host port and url you could do so like this.

.. literalinclude:: ../../test/sources/url_source.py

so now a UrlArgSchemaParser would expect command line flags of --input_host, --input_port, --input_url, and will look to download the json
from an http location via requests, or an existing ArgSchemaParser module could be simply passed an UrlSource, even though the original module 
author didn't explicitly support passing parameters by http location, and the parameters will still be deserialized and validated all the same. 


Sphinx Documentation
--------------------
argschema comes with a autodocumentation feature for Sphnix which will help you automatically
add documentation of your Schemas and :class:`argschema.ArgSchemaParser` classes in your project. This is how the 
documentation of the :doc:`../tests/modules` suite included here was generated.

To configure sphinx to use this function, you must be using the sphnix autodoc module and add the following to your conf.py file

.. code-block:: python

    from argschema.autodoc import process_schemas

    def setup(app):
        app.connect('autodoc-process-docstring',process_schemas)




.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`