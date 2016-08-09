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

# YUCK: <http://stackoverflow.com/a/6796536/563324>
with open(os.devnull, 'w') as devnull:
    _ = sys.stderr; sys.stderr = devnull
    from gmacpyutil import RunProcess # returns (stdout, stderr, returncode)
    sys.stderr = _

from mlvm.settings import HOME, SYSTEM

logger = logging.getLogger('mlvm')



def _run(go):
    if('Darwin' == SYSTEM):
        cmd = [HOME + '/versions/.current/StartupItems/MarkLogic/MarkLogic', go] 
        result = RunProcess(cmd)
        # if 0 != result[2]:
        #     raise Exception('{0} asdf'.format(result[1]))
    else:
        raise Exception('%s is not a supported platform', SYSTEM)

def start():
    return _run('start')

def stop():
    return _run('stop')

def ps():
    if('Darwin' == SYSTEM):
        cmd = ['pgrep', 'MarkLogic']
        result = RunProcess(cmd)
        print(result[0])
    else:
        raise Exception('{0} is not a supported platform'.format(SYSTEM))