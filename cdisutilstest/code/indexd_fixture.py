import os
import time

import pytest
import requests
from indexd import get_app
from indexd.default_settings import settings

from indexclient.client import IndexClient


def wait_for_indexd_alive(port):
    url = 'http://localhost:{}'.format(port)
    try:
        requests.get(url)
    except requests.ConnectionError:
        return wait_for_indexd_alive(port)
    else:
        return


def wait_for_indexd_not_alive(port):
    url = 'http://localhost:{}'.format(port)
    try:
        requests.get(url)
    except requests.ConnectionError:
        return
    else:
        return wait_for_indexd_not_alive(port)


def run_indexd(port):
    app = get_app()
    app.run(host='localhost', port=port, debug=False)


def create_user(username, password, settings_key='auth'):
    driver = settings[settings_key]
    driver.add(username, password)
    return (username, password)

# TODO use tmpdir
def remove_sqlite_files():
    files = ['alias.sq3', 'index.sq3', 'auth.sq3']
    for f in files:
        if os.path.exists(f):
            os.remove(f)


class MockServer(object):
    def __init__(self, port, auth):
        self.port = port
        self.auth = auth
        self.baseurl = 'http://localhost:{}'.format(port)
