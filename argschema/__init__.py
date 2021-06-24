'''argschema: flexible definition, validation and setting of parameters'''
from argschema.fields import InputFile, InputDir, OutputFile # noQA:F401
from argschema.schemas import ArgSchema # noQA:F401
from argschema.argschema_parser import ArgSchemaParser # noQA:F401

__version__ = "2.0.2"

def main():  # pragma: no cover
    jm = ArgSchemaParser()
    print(jm.args)


if __name__ == "__main__":  # pragma: no cover
    main()
