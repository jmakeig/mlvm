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
import logging

from mlvm.settings import HOME, SYSTEM

logger = logging.getLogger('mlvm')

import mlvm.versions

def list(writer):
    versions_dir = HOME + '/versions'
    # for name in sorted(os.listdir(versions_dir)):
    #     if '.current' != name:
    #         writer.write('{version}'.format(**get_version_from_path(versions_dir + '/' + name)) + '\n')
    
    versions = [
            get_version_from_path(versions_dir + '/' + dir) 
        for dir in os.listdir(versions_dir) 
        if '.current' != dir
    ]
    
    print '\n'.join([
            display_version(ver) 
        for ver in sorted(versions, lambda x, y: cmp(
            x['alias'] if x['alias'] is not None else x['version'],
            y['alias'] if y['alias'] is not None else y['version']
        ))
    ])

def display_version(version):
    str = ''
    if version['is_current']:
        str = str + '* '
    else: 
        str = str + '  '

    if version['alias'] is not None:
        str = str + version['alias'] + ' -> '
    
    return str + version['version']

def get_versions(path):
    print(os.listdir(path))

def get_current_version():
    return 'asdf'

def get_version_from_path(path):
    version = os.path.basename(path)
    alias = None
    if os.path.islink(path):
        version = os.path.basename(os.path.realpath(path))
        alias = os.path.basename(path)
    
    return {
        'version': version,
        'alias': alias,
        'is_current': get_current_version() == version,
        'is_local': True
    }
   


# TODO: Figure out which one is current