from multiprocessing import Process

import pytest

from indexd_fixture import (IndexClient, MockServer, create_user,
                            remove_sqlite_files, run_indexd,
                            wait_for_indexd_alive, wait_for_indexd_not_alive)


@pytest.fixture(scope='session')
def mock_server():
    port = 8001
    indexd = Process(target=run_indexd, args=[port])
    indexd.start()
    wait_for_indexd_alive(port)
    yield MockServer(port=port, auth=create_user('admin', 'admin'))
    indexd.terminate()
    remove_sqlite_files()
    wait_for_indexd_not_alive(port)

@pytest.fixture(scope='function')
def indexd_server(mock_server):
    # It is a misnomer this is returning a client
    client = IndexClient(
        baseurl=mock_server.baseurl, auth=mock_server.auth)
    yield client
    for doc in client.list():
        doc.delete()

@pytest.fixture(scope='function')
def indexd_client(indexd_server):
    return indexd_server
