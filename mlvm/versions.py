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

"""
Utilities for working with MarkLogic version and artifact names.
"""

import platform
import re

def get_release_artifact(major, minor, patch, system=platform.system()):
    if 'Darwin' == system:
      return 'MarkLogic-' + major + '.' + minor + '-' + patch + '-x86_64'
    raise Exception('Not yet implemented')
    
def parse_artifact_from_file(file):
    pattern = 'MarkLogic-(?:RHEL\d-)?\d{1,2}\.\d-(?:(?:\d{8})|(?:\d{1,2}\.\d{1,2}))[\.\-](?:x86_|amd)64'
    match = re.findall(pattern, file)
    if len(match) == 1:
        return match[0]
    raise Exception(artifact + ' does not match a MarkLogic version')

def parse_version(version):
    """ Parses a string, such as `'9.0-20160731'` or `'8.0-5.5'` into a 
        dictionary with keys, `major`, `minor`, and `patch`. """
    
    # 9.0-1
    # 10.0-5.5
    #
    # MarkLogic-RHEL6-9.0-20160801.x86_64.rpm
    # MarkLogic-RHEL7-9.0-20160801.x86_64.rpm
    # MarkLogic-9.0-20160801-x86_64.dmg
    # MarkLogic-9.0-20160801-amd64.msi
    # 
    # MarkLogic-RHEL6-7.0-6.4.x86_64.rpm
    # MarkLogic-RHEL7-7.0-6.4.x86_64.rpm
    # MarkLogic-7.0-6.4-x86_64.dmg
    # MarkLogic-7.0-6.4-amd64.msi
    
    version = str(version)
    pattern = '(?:MarkLogic-(?:RHEL\d-)?)?(\d{1,2}\.\d(?:-(?:(?:\d{8})|(?:\d{1,2}(?:\.\d{1,2})?)))?)(?:[\.\-](?:x86_|amd)64)?'
    match = re.findall(pattern, version)
    if 1 != len(match):
        raise Exception(version + ' doesn’t match a MarkLogic artifact')
    mm_patch = match[0].split('-')
    mm = mm_patch[0]
    patch = None
    if len(mm_patch) > 1:
        patch = mm_patch[1]
    mm_tokens = mm.split('.')
    major = int(mm_tokens[0])
    minor = None
    if len(mm_tokens) > 1:
        minor = int(mm_tokens[1])
    return {'major': str(major), 'minor': str(minor), 'patch': patch}

def serialize_version(version):
    major = version.get('major')
    minor = version.get('minor')
    patch = version.get('patch')
    
    result = major
    if minor is not None:
        result = result + '.' + minor
    if patch is not None:
        result = result + '-' + patch
    return result