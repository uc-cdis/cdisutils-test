"""
Functions for testing the validity of example files for a data dictionary.
Import and call these functions in the data dictionary's repo with correct 
parameters. 
Requires fixtures imported from gdcapi
"""

import json
import os
from gdcdatamodel import models as md
from flask import g
from collections import deque
import yaml

def put_program(client, program, data_dir, auth=None, role='admin'):
    path = '/v0/submission'
    headers = auth(path, 'put', role) if auth else None
    with open(os.path.join(data_dir, 'program.json'), 'r') as f:
        program = f.read()
    r = client.put(path, headers=headers, data=program)
    del g.user
    return r

def put_program_project(client, program, project, data_dir, auth=None, role='admin'):
    put_program(client, program, data_dir, auth=auth, role=role)
    path = '/v0/submission/' + program + '/'
    headers = auth(path, 'put', role) if auth else None
    with open(os.path.join(data_dir, 'project.json'), 'r') as f:
        project = f.read()
    r = client.put(path, headers=headers, data=project)
    assert r.status_code == 200, r.data
    del g.user
    return r

def put_entity_from_file(client, path, submitter, submission_path, data_dir,
                         validate=True):
    with open(os.path.join(data_dir, path), 'r') as f:
        entity = f.read()
    print "entity", entity
    r = client.put(submission_path, headers=submitter(submission_path, 'put'), data=entity)
    if validate:
        assert r.status_code == 200, r.data
    return r

def program_creation_endpoint_helper(client, pg_driver, submitter, program, data_dir):
    resp = put_program(client, program, data_dir, auth=submitter)
    assert resp.status_code == 200, resp.data
    print resp.data
    resp = client.get('/v0/submission/')
    assert resp.json['links'] == ['/v0/submission/' + program], resp.json

def project_creation_endpoint_helper(client, pg_driver, submitter, program, project, data_dir):
    resp = put_program_project(client, program, project, data_dir, auth=submitter)
    assert resp.status_code == 200
    resp = client.get('/v0/submission/' + program + '/')
    with pg_driver.session_scope():
        assert pg_driver.nodes(md.Project).count() == 1
        assert pg_driver.nodes(md.Project).path('programs')\
                                          .props(name=program)\
                                          .count() == 1
    assert resp.json['links'] == ['/v0/submission/' + program + '/' + project], resp.json

def put_entity_creation_valid_helper(client, pg_driver, submitter, program, project, data_dir, schema_path):

    put_program_project(client, program, project, data_dir, auth=submitter)

    entities = os.listdir(schema_path)
    entities = [entity for entity in entities if (not entity.startswith('_') and entity.endswith('.yaml') and entity != 'program.yaml' and entity != 'project.yaml' and entity != 'metaschema.yaml')]
    yamls = [yaml.load(open(os.path.join(schema_path, entity)).read()) for entity in entities]
    search_q = deque(['projects'])
    request_q = deque(['projects'])

    def check_all_parents_in_request_q(links):
        for link in links:
            if 'name' in link:
                if link['name'] not in request_q:
                    return False
            if 'subgroup' in link:
                for subgroup in link['subgroup']:
                    if subgroup['name'] not in request_q:
                        return False
        return True

    while len(search_q) != 0:
        parent = search_q.popleft()
        for i in range(len(yamls)):
            for j in range(len(yamls[i]['links'])):
                if 'name' in yamls[i]['links'][j] and yamls[i]['links'][j]['name'] == parent and yamls[i]['links'][j]['backref'] not in request_q and check_all_parents_in_request_q(yamls[i]['links']):
                    search_q.append(yamls[i]['links'][j]['backref'])
                    request_q.append(yamls[i]['links'][j]['backref'])
                if 'subgroup' in yamls[i]['links'][j]:
                    for subgroup in yamls[i]['links'][j]['subgroup']:
                        if subgroup['name'] == parent and subgroup['backref'] not in request_q and check_all_parents_in_request_q(yamls[i]['links']):
                            search_q.append(subgroup['backref'])
                            request_q.append(subgroup['backref'])

    request_q.remove('projects')
    
    print 'request_q: ', request_q

    singular_request_q = deque([])

    # map plural to singular
    for plural in request_q:
        for schema in yamls:
            if 'subgroup' in schema['links'][0]:
                if schema['links'][0]['subgroup'][0]['backref'] == plural:
                    singular_request_q.append(schema['id'])
                    break
            elif 'backref' in schema['links'][0]:
                if schema['links'][0]['backref'] == plural:
                    singular_request_q.append(schema['id'])
                    break

    for entity in singular_request_q:
        put_entity_from_file(client, entity+".json", submitter, 'v0/submission/' + program + '/' + project, data_dir)

def put_entity_creation_invalid_helper(client, pg_driver, submitter, program, project, data_dir, invalid_data_dir):
    put_program_project(client, program, project, data_dir, auth=submitter)
    invalid_jsons = os.listdir(invalid_data_dir)
    for invalid in invalid_jsons:
        r = put_entity_from_file(client, invalid, submitter, 'v0/submission/' + program + '/' + project, invalid_data_dir, validate=False)
        assert 500 > r.status_code >= 400
