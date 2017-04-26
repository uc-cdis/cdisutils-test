"""
Module for mocking and testing of the
"""

from os import path, sys
from urlparse import urlparse
import json
from urllib import urlencode

def fake_request(method, url, auth, data, verify):
    """
    Allows us to mock the calls to the REST API
    The url will be used as path to the resource file
    From there, if necessary, the appropriate response data
    will be collected from a different entry in the json file
    """
    parsed_url = urlparse(url)
    resource_file = parsed_url.path.split('1.0')[-1]
    if data != None:
        parsed_data = urlencode(data)
    else:
        parsed_data = None
    parsed_query = parsed_url.query
    file_path = './test/data/{request}'.format(request=resource_file)
    resource_file = path.normpath(file_path)
    with open(resource_file, 'r') as f:
        resp_dict = json.load(f)
    if parsed_data != None:
        response = Response(int(resp_dict[parsed_data]['status_code']), json.dumps(resp_dict[parsed_data]['text']))
    elif parsed_query != '':
        response = Response(int(resp_dict[parsed_query]['status_code']), json.dumps(resp_dict[parsed_query]['text']))
    else:
        response = Response(int(resp_dict['status_code']), json.dumps(resp_dict['text']))
    return response

def fake_request_only_failure(method, url, auth, data, verify):
    """                                                                                                                                                                                                            
    Used for functions without parameters, since those
    cannot be distinguished inside the file
    """ 
    return Response(404, json.dumps("Error"))

class Response(object):
    """
    Mocks a request response
    """
    def __init__(self, status_code=0, text=None):
        self.text = text
        self.status_code = status_code
