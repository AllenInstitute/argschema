'''__init__.py file for the argschema module'''
from .fields import InputFile, InputDir, OutputFile, OptionList
from .schemas import ArgSchema
from .argschema_parser import ArgSchemaParser
from .deprecated import JsonModule, ModuleParameters


def main():  # pragma: no cover
    jm = ArgSchemaParser()
    print(jm.args)


if __name__ == "__main__":  # pragma: no cover
    main()
