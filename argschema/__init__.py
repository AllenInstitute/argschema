'''argschema: flexible definition, validation and setting of parameters'''
from .fields import InputFile, InputDir, OutputFile, OptionList # noQA:F401
from .schemas import ArgSchema # noQA:F401
from .argschema_parser import ArgSchemaParser # noQA:F401
from .deprecated import JsonModule, ModuleParameters # noQA:F401


def main():  # pragma: no cover
    jm = ArgSchemaParser()
    print(jm.args)


if __name__ == "__main__":  # pragma: no cover
    main()
