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

import os
import logging

from mlvm.settings import HOME, SYSTEM, USER
import mlvm.filesystem as fs
import mlvm.commands.prepare as prepare

logger = logging.getLogger('mlvm')

def use(version):
    logger.info('Installing version %s', version)
    if prepare.is_prepared():
        if 'Darwin' == SYSTEM:
            version_dir = HOME + '/versions/' + version
            if not os.path.isdir(version_dir):
                raise Exception('%s does not exist', version_dir)

            current_dir = fs.ensure_directory(HOME + '/versions/.current')
            fs.clear_links(current_dir)

            """ Create links to top-level """
            for name in os.listdir(version_dir):
                logger.debug('Linking %s -> %s', version_dir + '/' + name, current_dir + '/' + os.path.basename(name))
                fs.symlink_force(version_dir + '/' + name, current_dir + '/' + os.path.basename(name))
        else:
            raise Exception('%s is not a supported platform', SYSTEM)  
    else:
        raise Exception('Is not prepared')  