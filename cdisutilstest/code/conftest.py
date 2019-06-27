from multiprocessing import Process

import pytest

from .indexd_fixture import (IndexClient, MockServer, create_user, remove_sqlite_files, run_indexd, clear_database, setup_database, wait_for_indexd_alive, wait_for_indexd_not_alive)
# Note the . in front of indexd_fixtures for more information:
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3#16985066
# Basically the options are:
# 1) Use setuptools for this repo
# 2) Some terrible looking relative imports


@pytest.fixture(scope='session')
def indexd_server():
    """
    Starts the indexd server, and cleans up its mess.
    Most tests will use the client which stems from this
    server fixture.
    Runs once per test session.
    """
    port = 8001
    indexd = Process(target=run_indexd, args=[port])
    indexd.start()
    wait_for_indexd_alive(port)
    yield MockServer(port=port)
    indexd.terminate()
    wait_for_indexd_not_alive(port)


@pytest.fixture(scope='function')
def indexd_client(indexd_server):
    """
    Returns a IndexClient. This will delete any documents,
    aliases, or users made by this
    client after the test has completed.
    Currently the default user is the admin user
    Runs once per test.
    """
    setup_database()
    client = IndexClient(
        baseurl=indexd_server.baseurl, auth=create_user('admin', 'admin'))
    yield client
    clear_database()
