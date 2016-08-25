# coding=utf-8

# Copyright 2016 MarkLogic Corporation
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import time
import logging

import json
import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import HTTPError

from mlvm.settings import HOME, SYSTEM
from mlvm.cli import promptCredentials

logger = logging.getLogger('mlvm')

credentials = { 'auth': None } # Module-scoped variables aren't writable. Their properties are, though. (Huh?)

def get_default_host_id(**kwargs):
    url = '{protocol}://{host}:{port}/manage/v2/hosts?group-id=Default'.format(**kwargs)
    headers = { 'Accept': 'application/json' }

    try:
        response = requests.get(url, headers=headers, auth=kwargs.get('auth'))
        response.raise_for_status()
    except HTTPError, err:
        raise err # What to do here?

    json = response.json()
    host_id = json.get('host-default-list').get('list-items').get('list-item')[0].get('idref')
    return host_id

def update_default_hostname(new_name, host='127.0.0.1', port=8002, protocol='http'):
    logger.info('Updating hostname')
    auth = HTTPDigestAuth(credentials['auth']['user'], credentials['auth']['password'])
    headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }
    host_id = get_default_host_id(protocol=protocol, host=host, port=port, auth=auth)
    url = '{protocol}://{host}:{port}/manage/v2/hosts/{host_id}/properties'.format(protocol=protocol, host=host, port=port, host_id=host_id)

    data = { "host-name": new_name }
    try:
        response = requests.put(url, data=json.dumps(data), headers=headers, auth=auth)
        response.raise_for_status()
    except HTTPError, err:
        raise err # What to do here?

def wait_for_restart(host):
    # TODO: Wait for server restart
    logger.debug('Sleeping…')
    time.sleep(10)

def bootstrap_init(host):
    logger.info('Enter the username and password for the admin user')
    credentials['auth'] = promptCredentials(host, verify=True)

    #http://"$HOST":8001/admin/v1/timestamp
    url = 'http://{host}:8001/admin/v1/init'.format(host=host)
    headers = { 'Content-Type': 'application/x-www-form-urlencoded'}
    logger.info('Initializing %s', host)
    try:
        response = requests.post(url, data='', headers=headers)
        response.raise_for_status()
    except HTTPError, err:
        raise err # What to do here?

    wait_for_restart(host)

    data = {'admin-username': credentials['auth']['user'], 'admin-password': credentials['auth']['password'], 'realm': 'public' }
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    url = 'http://{host}:8001/admin/v1/instance-admin'.format(host=host)
    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
    except HTTPError, err:
        raise err # What to do here?  

def init(host, new_name):
    if host is None:
        host = '127.0.0.1'
    bootstrap_init(host)

    wait_for_restart(host)
    if new_name is not None:
        update_default_hostname(new_name, host=host)