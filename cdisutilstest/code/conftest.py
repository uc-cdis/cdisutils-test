from multiprocessing import Process

import pytest

from indexd_fixture import (IndexClient, MockServer, create_user,
                            remove_sqlite_files, run_indexd,
                            wait_for_indexd_alive, wait_for_indexd_not_alive)


@pytest.fixture(scope='session')
def indexd_server():
    """
    Starts the indexd server, and cleans up its mess.
    Most tests will use the client which stems from this
    sever fixture. Runs once per test session.
    """
    port = 8001
    indexd = Process(target=run_indexd, args=[port])
    indexd.start()
    wait_for_indexd_alive(port)
    yield MockServer(port=port, auth=create_user('admin', 'admin'))
    indexd.terminate()
    remove_sqlite_files()
    wait_for_indexd_not_alive(port)

@pytest.fixture(scope='function')
def indexd_client(indexd_server):
    """
    Returns a IndexClient. This will delete any documents
    made by this client after the test has completed.
    Runs once per test.
    """
    client = IndexClient(
        baseurl=indexd_server.baseurl, auth=indexd_server.auth)
    yield client
    for doc in client.list():
        doc.delete()
