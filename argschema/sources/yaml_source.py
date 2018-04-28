import yaml
from .source import FileSource

class YamlSource(FileSource):

    def read_file(self,fp):
        return yaml.load(fp)

    def write_file(self,fp,d):
        yaml.dump(d,fp)