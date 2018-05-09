import hashlib
import os
import random

import time
import uuid

import pytest
import requests
from indexd import get_app
from indexd.default_settings import settings

from indexclient.client import IndexClient, Document
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


def create_random_index(index_client, did=None, version=None, hashes=None):
    """
    Shorthand for creating new index entries for test purposes.
    Note:
        Expects index client v1.5.2 and above
    Args:
        index_client (indexclient.client.IndexClient): pytest fixture for index_client
        passed from actual test functions
        did (str): if specified it will be used as document did, else allows indexd to create one
        version (str): version of the index being added
        hashes (dict): hashes to store on the index, if not specified a random one is created
    Returns:
        indexclient.client.Document: the document just created
    """

    did = str(uuid.uuid4()) if did is None else did

    if not hashes:
        md5_hasher = hashlib.md5()
        md5_hasher.update(did.encode("utf-8"))
        hashes = {'md5': md5_hasher.hexdigest()}

    doc = index_client.create(
        did=did,
        hashes=hashes,
        size=random.randint(10, 1000),
        version=version if version else "",
        acl=["a", "b"],
        file_name="{}_warning_huge_file.svs".format(did),
        urls=["s3://super-safe.com/{}_warning_huge_file.svs".format(did)],
        urls_metadata={"s3://super-safe.com/{}_warning_huge_file.svs".format(did): {"a", "b"}}
    )

    return doc


def create_random_index_version(index_client, did, version_did=None, version=None):
    """
    Shorthand for creating a dummy version of an existing index, use wisely as it does not assume any versioning
    scheme and null versions are allowed
    Args:
        index_client (IndexClient): pytest fixture for index_client
        passed from actual test functions
        did (str): existing member did
        version_did (str): did for the version to be created
        version (str): version number for the version to be created
    Returns:
        Document: the document just created
    """
    md5_hasher = hashlib.md5()
    md5_hasher.update(did.encode("utf-8"))
    file_name = did

    data = {}
    if version_did:
        data["did"] = version_did
        file_name += version_did
        md5_hasher.update(version_did.encode("utf-8"))

    data["acl"] = ["ax", "bx"]
    data["size"] = random.randint(10, 1000)
    data["hashes"] = {"md5": md5_hasher.hexdigest()}
    data["urls"] = ["s3://super-safe.com/{}_warning_huge_file.svs".format(file_name)]
    data["form"] = "object"
    data["file_name"] = "{}_warning_huge_file.svs".format(file_name)
    data["urls_metadata"] = {"s3://super-safe.com/{}_warning_huge_file.svs".format(did): {"a": "b"}}

    if version:
        data["version"] = version

    return index_client.add_version(did, Document(None, None, data))
