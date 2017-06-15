This module simplifies the development of modules that would like to define and check a particular set of input parameters, but be able to flexibly define those inputs in different ways in different contexts. 

It will allow you to 
Passing a command line argument to a location of a json_file which contains the input parameters
OR passing a json_dictionary directly into the module with the parameters defined
AND passing parameters via the command line, in a way that will override the examples given.

## What does it do
json_module defines two basic classes which every module should subclass, JsonModule and ModuleParameters. JsonModule takes ModuleParameters as an input which is simply an extension of the marshmallow Schema class.

JsonModule then takes that schema, and builds a argparse parser from the schema using a standard pattern to convert the schema.
Nested elements of the schema are specified with a "." 

so the json 
{
    "nested":{
        "a":5
    },
    "b":"a"
}
would map to the command line arguments
--nested.a 5 --b a

JsonModule then parses the command line arguments into a  dictionary using argparse, and then reformatting the dictionary to have the proper nested structure to match the schema it was provided.

Next, JsonModule reads either the input_data if it was passed, or takes the path of the input_json and reads that in as a dictionary.  

Given that input dictionary and the command line dictionary, JsonModule then merges the two dictionaries, where the command line dictionary takes precendence. 

Next, that dictionary is parsed and validated using marshmallow to convert the raw dictionary into the types defined by the marshmallow fields.

The resulting dictionary is then stored in self.args available for the module to user.

After that the module does some standard things, such as parsing the parameter args['log_level'] to configure a logging module at self.logger.

## How should I use it
subclass JsonModule and ModuleParameters using the pattern found in template_module.py to define your module parameters, defining default values if you want and help statements that will be displayed by argparse as help statements, and maybe provide some example parameters for someone who is trying to figure out how to user your module (which is also a good way to rapidly test your module as you are developing it)

Note the use of InputDir and InputFile, two example custom marshmallow validators that are included in JsonModule.
They will insure that these directory exist, or files exist before trying to run your module and provide errors to the user.
You can use the power of marshmallow to produce custom validators for any data type, 
and serialize/deserialize functions that will make loading complex parameters as python objects, such as numpy arrays of parameters.

For instance, this could allow you to have a parameter that is simply a string in json, but the deserialization routine loads uses that string to look something up in a database and return a numpy array, or have a string which is actually a filepath to an image file, and deserializes that as a numpy array.  This is the basic power of marshmallow.

## Why did we make this
You should consider using this module if this pattern seems familar to you.

You start building some code in an ipython notebook to play around with a new idea where you define some variables as you go that make your code work, you fiddle with things for awhile and eventually you get it to a point that works.  You then immediately want to use it over and over again, and are scrolling through your ipython notebook, changing variables, making copies of your notebook for different runs.  Several times you make mistakes typing in the exact filepath of some input file, and your notebook breaks on cell 53, but no big deal, you just fix the filename variable and rerun it. 

It's a mess, and you know you should migrate your code over to a module that you can call from other programs or notebooks.  You start collecting your input variables to the top of the notebook and make yourself a wrapper function that you can call.  However, now your mistake in filename typing is a disaster because the file doesn't exist, and your code doesn't check for the existence of the file until quite late. You start implementing some input validation checks to avoid this problem.

Now you start wanting to integrate this code with other things, including elements that aren't in python and so you want to have a command line module that executes the code, so you can use some other tool to stitch together a process that includes this code, like maybe some shell scripts.  You implement an argparse set of inputs and default values that make your python program a self-contained program, with some help documentation.  Along the way, you have to refactor the parsed argparse variables into your function

Now this module starts becoming useful enough that you want to integrate it into more complex modules.  You end up copying and pasting the argparse code over to the other module, and then 5 other modules.  Later you decide to change your original module a little bit, and you have a nightmare of code replace to fix up the other modules.. you kick yourself for not having thought this through more clearly.

Your code is now pretty useful, but its so useful you start running it on larger and larger jobs, and you want to deploy it on a cluster in your groups pipeline workflow.  Your pipeline framework needs to dynamically define and control the parameters, and so it would like to simply write all the inputs to a file and pass your program that file, rather than having to parse out the inputs into your argparse format.  Now you have to refactor your inputs again to deal with this new pattern, so you have to make a new version that works in this way. Now you have to redo validation to work in a different way, since you were using argparse to do it before. 

If you had only designed things from the beginning to allow for each of these use cases over the lifetime of your module.

This is what json_module is designed to do.

