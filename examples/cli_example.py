from argschema import ArgSchema, ArgSchemaParser
from argschema.fields import List, NumpyArray, Bool, Int, Nested, Str
from argschema.schemas import DefaultSchema


class MyNestedSchema(DefaultSchema):
    a = Int(default=42, description= "my first parameter")
    b = Bool(default=True, description="my boolean")


class MySchema(ArgSchema):
    array = NumpyArray(default=[[1, 2, 3],[4, 5, 6]], dtype="uint8",
                       description="my example array")
    string_list = List(List(Str),
                       default=[["hello", "world"], ["lists!"]],
                       cli_as_single_argument=True,
                       description="list of lists of strings")
    int_list = List(Int, default=[1, 2, 3],
                    cli_as_single_argument=True,
                    description="list of ints")
    nested = Nested(MyNestedSchema, required=True)


if __name__ == '__main__':
    mod = ArgSchemaParser(schema_type=MySchema)
    print(mod.args)
