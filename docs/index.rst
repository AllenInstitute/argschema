.. argschema documentation master file, created by
   sphinx-quickstart on Fri Jul 21 18:01:44 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

argschema documentation
=====================================
This python module enables python programs to specify and validate their input parameters via a schema,
 while allowing those parameters to be passed into it in different ways in different contexts. 

In particular it will allow you to 

1) Specify an input_json file which contains the parameters via the command line
2) OR pass a dictionary directly into the module with the parameters defined
3) AND/OR pass individual parameters via the command line, in a way that will override the input_json or the dictionary given.

In all cases, it will merge these different parameters into a single dictionary and then validate that the parameters against your schema.

The User Guide
--------------

This part of the documentation, which is mostly prose, begins with some
background information about Requests, then focuses on step-by-step
instructions for getting the most out of Requests.

.. toctree::
   :maxdepth: 2

   user/intro

API
---
.. toctree::
   :maxdepth: 2

   api/argschema


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



Support/Contribute
------------------
We are planning on occasional updating this tool with no fixed schedule. 
Community involvement is encouraged through both issues and pull requests.  
Please make pull requests against the dev branch, as we will test changes there before merging into master.

- Issue Tracker: github.com/AllenInstitute/argschema/issues
- Source Code: github.com/AllenInstitute/argschema



License
-------

The project is licensed under the BSD license.