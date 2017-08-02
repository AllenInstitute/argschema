User Guide
=====================================

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
    >>> mod = ArgSchemaParser(input_data=d,schema=MySchema)
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
    >>> mod = ArgSchemaParser(input_data=d,schema=MySchema)
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
:class:`~argschema.fields` contains all the built-in marshmallow fields, 
but also some useful custom ones, 
such as :class:`~argschema.fields.InputFile`, 
:class:`~argschema.fields.OutputFile`, 
:class:`~argschema.fields.InputDir` that validate that the paths exist and have the proper
permissions to allow files to be read or written.

Other fields, such as :class:`~argschema.fields.NumpyArray` will deserialize ordered lists of lists
directly into a numpy array of your choosing.

Finally, an important Field to know is :class:`~argschema.fields.Nested`, which allows you to define
heirarchical nested structures.  Note, that if you use Nested schemas, your Nested schemas should
subclass :class:`~argschema.schemas.DefaultSchema` in order that they properly fill in default values,
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

Installation
------------
install via source code

::

    $ python setup.py install

or pip

::

    $ pip install argschema


.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`