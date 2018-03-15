import os
import time

import pytest
import requests
from multiprocessing import Process

from indexd import get_app
from indexd.default_settings import settings


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


def create_user(username, password):
    driver = settings['auth']
    driver.add(username, password)
    return (username, password)


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


@pytest.fixture(scope='session')
def indexd_server():
    port = 8001
    indexd = Process(target=run_indexd, args=[port])
    indexd.start()
    wait_for_indexd_alive(port)
    try:
        yield MockServer(port=port, auth=create_user('admin', 'admin'))
    except Exception:
        yield "Fail to setup indexd"
    finally:
        indexd.terminate()
        remove_sqlite_files()
        wait_for_indexd_not_alive(port)
