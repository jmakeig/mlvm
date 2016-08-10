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
import getpass

logger = logging.getLogger('mlvm')

def promptCredentials(realm, verify=False):
    """ Callback to prompt for username and password """
    user = raw_input('Username for ' + realm + ': ') # TODO: Validation
    password = getpass.getpass('Password for ' + user + ' on ' + realm + ': ')
    if verify:
        password2 = getpass.getpass('Verify password: ')
        if password2 != password:
            raise Exception('The passwords do not match')

    return {'user': user, 'password': password}

def show_progress(amt, total, stream = None):
    logger.debug(str(amt) + ' of ' + str(total))