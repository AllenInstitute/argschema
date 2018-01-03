import requests 
import mock
from url_source import UrlArgSchemaParser, UrlSource, MySchema
from argschema import ArgSchemaParser
# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://localhost:88/test.json':
        return MockResponse({
                                'a':7,
                                'nest':{
                                    'one':7,
                                    'two':False
                                }
                            }, 200)


    return MockResponse(None, 404)

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_url_parser(mock_get):
    input_source=UrlSource(input_host='localhost',input_port=88,input_url='test.json')
    mod = ArgSchemaParser(schema_type=MySchema, input_source=input_source, args = [])
    assert(mod.args['a']==7)

@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_url_parser_command_line(mock_get):
    mod = UrlArgSchemaParser(args = ['--input_host','localhost','--input_port','88','--input_url','test.json'])
    assert(mod.args['a']==7)
