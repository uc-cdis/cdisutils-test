"""
Module for mocking and testing of the
"""

from os import path, sys
from urllib.parse import urlparse, urlencode
import json


class RequestMocker(object):
    def __init__(self, files):
        self.files = files

    def fake_request(self, method, url, auth, data, verify):
        """
        Allows us to mock the calls to the REST API
        The url will be used as path to the resource file
        From there, if necessary, the appropriate response data
        will be collected from a different entry in the json file
        """
        parsed_url = urlparse(url)
        resource_file = parsed_url.path.split("1.0/")[-1]
        resource_file = resource_file.split(".")[0]
        if data:
            params = urlencode(data)
        else:
            params = parsed_url.query
        resp_dict = self.files[resource_file]
        if params:
            parsed_data = frozenset(params.split("&"))  # ignore param order
            response = Response(
                int(resp_dict[parsed_data]["status_code"]),
                json.dumps(resp_dict[parsed_data]["text"]),
            )
        else:
            response = Response(
                int(resp_dict["status_code"]), json.dumps(resp_dict["text"])
            )
        return response

    def fake_request_only_failure(self, method, url, auth, data, verify):
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
