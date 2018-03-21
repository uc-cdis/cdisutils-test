import os
import time

import pytest
import requests
from indexd import get_app
from indexd.default_settings import settings

from indexclient.client import IndexClient
from indexd.index.drivers.alchemy import Base as index_base
from indexd.auth.drivers.alchemy import Base as auth_base
from indexd.alias.drivers.alchemy import Base as alias_base


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


def setup_database():
    index_base.metadata.create_all()
    alias_base.metadata.create_all()
    auth_base.metadata.create_all()


def clear_database():
    with settings['config']['INDEX']['driver'].session as session:
        for model in index_base.__subclasses__():
            session.query(model).delete()

    with settings['config']['ALIAS']['driver'].session as session:
        for model in alias_base.__subclasses__():
            session.query(model).delete()

    with settings['auth'].session as session:
        for model in auth_base.__subclasses__():
            session.query(model).delete()


class MockServer(object):
    def __init__(self, port):
        self.port = port
        self.baseurl = 'http://localhost:{}'.format(port)
