from .fields import InputFile, InputDir, OutputFile, OptionList
from .schemas import ModuleParameters
from .json_module import JsonModule

def main():
    jm = JsonModule()
    print jm.args

if __name__ == "__main__": main()