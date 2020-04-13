from argschema.sources import ConfigurableSource
from argschema.schemas import DefaultSchema
from argschema.fields import Str,Int
from argschema import ArgSchemaParser
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

class UrlSource(ConfigurableSource):
    """ A configurable source which obtains values by making a GET request, 
    expecting a JSON response.
    """
    ConfigSchema = UrlSourceConfig

    def get_dict(self):
        netloc = self.config["input_host"]
        if self.config["input_port"] is not None:
            netloc = "{}:{}".format(netloc, self.config["input_port"])

        url = urlunparse((
            self.config["input_protocol"], 
            netloc, 
            self.config["input_url"],
            None, None, None
        ))     
                        
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
