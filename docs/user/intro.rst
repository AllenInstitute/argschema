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

.. command-output:: python mymodule.py
    :cwd: /../examples/ 

.. command-output:: python mymodule.py --a 2
    :cwd: /../examples/ 

.. command-output:: python mymodule.py --a 2 --log_level WARNING
    :cwd: /../examples/ 

.. command-output:: python mymodule.py -h
    :cwd: /../examples/ 

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

.. command-output:: python mymodule.py --input_json myinput.json
    :cwd: /../examples/ 

or override a parameter if you want

.. command-output:: python mymodule.py --input_json myinput.json --a 100
    :cwd: /../examples/ 

plus, no matter how you give it parameters, they will always be validated,
before any of your code runs.

Whether from the command line

.. command-output:: python mymodule.py --input_json ../examples/myinput.json --a 5!
    :cwd: /../examples/

or from a dictionary
::

    >>> from argschema import ArgSchemaParser
    >>> from mymodule import MySchema
    >>> d={'a':'hello'}
    >>> mod = ArgSchemaParser(input_data=d,schema_type=MySchema,args=[])
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

Another common question about :class:`~argschema.fields.Nested` is how you specify that 
you want it not to be required, but want it filled in with whatever default values exist 
in the schema it references.  Or alternatively, that you want it not required, and you only 
want the default values used if there is any reference in the input dictionary. The key 
to this distinction is including default={} (which will cause defaults of the subschemas to be 
filled in) vs leaving default unspecified, which will only trigger the subschema defaults if the 
original input contains any references to elements of that subschema. 

This example illustrates the difference in the approaches

.. literalinclude:: ../../examples/nested_example.py
    :caption: nested_example.py

.. command-output:: python nested_example.py
    :cwd: /../examples

.. command-output:: python nested_example.py --nest.a 4
    :cwd: /../examples

One important use case for :class:`~argschema.fields.Nested`, is where you want 
your json to have a list of dictionaries.  You might be tempted to use the field 
:class:`~argschema.fields.List`, with a field_type of :class:`~argschema.fields.Dict`, 
however you should use :class:`~argschema.fields.Nested` with `many=True`.

The template_module example shows how you might combine these features
to define a more complex parameter structure.

.. literalinclude:: ../../examples/template_module.py
    :caption: template_module.py

so now if run the example commands found in run_template.sh

.. literalinclude:: ../../examples/input.json
    :caption: input.json

.. command-output:: python template_module.py 
      --output_json output_command.json  
      --inc.name from_command 
      --inc.increment 2
    :cwd: /../examples

.. command-output:: python template_module.py 
      --input_json input.json 
      --output_json output_fromjson.json
    :cwd: /../examples

.. command-output:: python template_module.py 
    :cwd: /../examples


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


We can explore some typical examples of command line usage with the following script:

.. literalinclude:: ../../examples/cli_example.py
    :caption: cli_example.py

.. command-output:: python cli_example.py --help
    :cwd: /../examples
    
We can set some values and observe the output:

.. command-output:: python cli_example.py --nested.b 0 --string_list "[['foo','bar'],['baz','buz']]"
    :cwd: /../examples

If we try to set a field in a way the parser can't cast the variable (for
example, having an invalid literal) we will see a casting validation error:

.. command-output:: python cli_example.py --array [1,foo,3]
    :cwd: /../examples
    
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
and :method:`argschema.ArgSchemaParser.output` will output the dictionary however that :class:`argschema.sources.ArgSink` specifies it should.

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