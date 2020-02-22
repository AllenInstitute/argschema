import requests
import mock
from argschema.sources.url_source import UrlSource
from argschema import ArgSchemaParser


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://localhost:88/test.json':
        return MockResponse({
            'a': 7,
            'nest': {
                'one': 7,
                'two': False
            }
        }, 200)
    return MockResponse(None, 404)


@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_url_parser_get_dict(mock_get):
    source = UrlSource()
    source.load_config({
        "input_host": "localhost",
        "input_port": 88,
        "input_url": "test.json",
    })

    obtained = source.get_dict()
    assert obtained["a"] == 7