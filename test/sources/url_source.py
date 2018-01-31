from argschema.sources import ArgSource, ArgSink
from argschema.schemas import DefaultSchema
from argschema.fields import Str,Int
from argschema import ArgSchemaParser
from test_classes import MySchema
import requests
try:
    from urllib.parse import urlunparse 
except:
    from urlparse import urlunparse

class UrlSourceConfig(DefaultSchema):
    input_host = Str(required=True, description="host of url")
    input_port = Int(required=False, default=None, description="port of url")
    input_url = Str(required=True, description="location on host of input")
    input_protocol = Str(required=False, default='http', description="url protocol to use")

class UrlSource(ArgSource):
    ConfigSchema = UrlSourceConfig

    def get_dict(self):
        if self.input_port is None:
            netloc = self.input_host
        else:
            netloc = "{}:{}".format(self.input_host,self.input_port)
        url = urlunparse((self.input_protocol,netloc,self.input_url,None,None,None))                             
        response = requests.get(url)
        return response.json()


class UrlArgSchemaParser(ArgSchemaParser):
    default_configurable_sources = [UrlSource]
    default_schema = MySchema
