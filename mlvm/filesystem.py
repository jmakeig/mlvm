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
import errno
import logging

logger = logging.getLogger('mlvm')

def symlink_force(target, source):
    """ Creates or changes a symlink, linking `source` to `target`. Raises exception if `source` exists and is not a symlink."""
    try:
        os.symlink(target, source)
    except OSError, e:
        if e.errno == errno.EEXIST:
            if(os.path.islink(source)): # Only remove symlinks
                os.remove(source)
                os.symlink(target, source)
            else:
                raise Exception('File exists, but is not a symlink')
        else:
            raise e

def ensure_directory(path):
    """ If a directory doesn’t exist at the path create it. """    
    if not os.path.isdir(path):
      logger.debug('Creating ' + path + ' becuase it does not yet exist')
      os.makedirs(path)
    return path

def clear_links(path):
    """ Clear symlinks from a directory. If the directory contains anything other than symlinks throw an exception."""
    for name in os.listdir(path):
        link = path + '/' + name
        if(os.path.islink(link)):
            os.remove(link)
            logger.debug('Removing %s', link)
        else:
            raise Exception('%s is not a symlink', link)