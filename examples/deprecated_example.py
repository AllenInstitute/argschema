from argschema import ArgSchema, ArgSchemaParser
from argschema.fields import List, Float


class MySchema(ArgSchema):
    list_old = List(
        Float,
        default=[1.1, 2.2, 3.3],
        metadata={"description": "float list with deprecated cli"},
    )
    list_new = List(
        Float,
        default=[4.4, 5.5, 6.6],
        metadata={
            "cli_as_single_argument": True,
            "description": "float list with supported cli",
        },
    )


if __name__ == "__main__":
    mod = ArgSchemaParser(schema_type=MySchema)
    print(mod.args)
