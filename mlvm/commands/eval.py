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

import logging
from mlvm.settings import HOME, SYSTEM

logger = logging.getLogger('mlvm')

import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import HTTPError
from mlvm.multipart import read_multipart
from mlvm.cli import promptCredentials

def remote_eval(source, language='js', host='localhost', protocol='http', port=8000):
    #   cat <(echo 'javascript=') <(cat -) | curl http://localhost:8000/v1/eval \
    #   --digest -u admin:admin -X POST \
    #   -H 'Accept: multipart/mixed' \
    #   -H 'Content-Type: application/x-www-form-urlencoded' \
    #   -d @-
    credentials = promptCredentials('eval')
    auth = HTTPDigestAuth(credentials['user'], credentials['password'])
    boundary = 'ASDF123'
    headers = { 'Accept': 'multipart/mixed;boundary=' + boundary, 'Content-Type': 'application/x-www-form-urlencoded' }
    url = '{protocol}://{host}:{port}/v1/eval'.format(protocol=protocol, host=host, port=port)

    data = 'javascript=' + source
    try:
        response = requests.post(url, data, stream=True, headers=headers, auth=auth)
        parts = read_multipart(response.raw, boundary=boundary)
        for part in parts:
            logger.debug(part)
        response.raise_for_status()
    except HTTPError, err:
        raise err # What to do here?