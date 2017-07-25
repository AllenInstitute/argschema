'''argschema: flexible definition, validation and setting of parameters'''
from .fields import InputFile, InputDir, OutputFile, OptionList
from .schemas import ArgSchema
from .argschema_parser import ArgSchemaParser
from .deprecated import JsonModule, ModuleParameters


def main():  # pragma: no cover
    jm = ArgSchemaParser()
    print(jm.args)


if __name__ == "__main__":  # pragma: no cover
    main()
