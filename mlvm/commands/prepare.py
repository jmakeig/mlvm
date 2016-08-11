
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
logger = logging.getLogger('mlvm')

from mlvm.settings import HOME, SYSTEM, USER
import mlvm.filesystem as fs

from mlvm.exceptions import RootUserRequired, UnsupportedPlatform


# PATHS = {
#     'Darwin': {
#         'Lib': USER + '/Library',
#         'Sup': USER + '/Library/Application Support',
#         'Pref': USER + '/Library/PreferencePanes',
#         'Start': USER + '/Library/StartupItems'
#     }
# }

def is_prepared():
    if 'Darwin' == SYSTEM:
        return True # TODO
    else:
        raise UnsupportedPlatform('%s is not a supported platform', SYSTEM)

def ensure_sudo():
    try:
        real_user = os.environ['SUDO_USER']
    except Exception, err:
        raise RootUserRequired()
    
    import pwd
    return (
        pwd.getpwnam(real_user).pw_uid,
        pwd.getpwnam(real_user).pw_gid
    )

def prepare():
    if 'Darwin' == SYSTEM:
        real_user_id, real_group_id = ensure_sudo()

        # TODO: Extract me into a proper data structure
        LIBRARY = USER + '/Library'
        APPLICATION_SUPPORT = LIBRARY + '/Application Support'
        PREF_PANES = LIBRARY + '/PreferencePanes'
        STARTUP = LIBRARY + '/StartupItems'

        current_dir = fs.ensure_directory(HOME + '/versions/.current')
        os.lchown(current_dir, real_user_id, real_group_id)
        fs.clear_links(current_dir)

        # MarkLogic Server
        fs.symlink_force(current_dir + '/MarkLogic', LIBRARY + '/MarkLogic')
        os.lchown(LIBRARY + '/MarkLogic', real_user_id, real_group_id)
        # Application Support
        fs.symlink_force(current_dir + '/Support', APPLICATION_SUPPORT + '/MarkLogic')
        os.lchown(APPLICATION_SUPPORT + '/MarkLogic', real_user_id, real_group_id)
        # Preference Pane
        fs.symlink_force(current_dir + '/PreferencePanes/MarkLogic.prefPane', PREF_PANES + '/MarkLogic.prefPane')
        os.lchown(PREF_PANES + '/MarkLogic.prefPane', real_user_id, real_group_id)
        # Start Up
        fs.symlink_force(current_dir + '/StartupItems/MarkLogic', STARTUP + '/MarkLogic')
    else:
        raise Exception('%s is not a supported platform', SYSTEM)

def _unlink(path):
    if(os.path.islink(path)):
        os.unlink(path)

def remove():
    if 'Darwin' == SYSTEM:
        real_user_id, real_group_id = ensure_sudo()

        # TODO: Extract me into a proper data structure
        LIBRARY = USER + '/Library'
        APPLICATION_SUPPORT = LIBRARY + '/Application Support'
        PREF_PANES = LIBRARY + '/PreferencePanes'
        STARTUP = LIBRARY + '/StartupItems'

        logger.debug('Unlinking {0}'.format(LIBRARY + '/MarkLogic'))
        _unlink(LIBRARY + '/MarkLogic')
        logger.debug('Unlinking {0}'.format(APPLICATION_SUPPORT + '/MarkLogic'))
        _unlink(APPLICATION_SUPPORT + '/MarkLogic')
        logger.debug('Unlinking {0}'.format(PREF_PANES + '/MarkLogic.prefPane'))
        _unlink(PREF_PANES + '/MarkLogic.prefPane')
        logger.debug('Unlinking {0}'.format(STARTUP + '/MarkLogic'))
        _unlink(STARTUP + '/MarkLogic')

        current_dir = HOME + '/versions/.current'
        if os.path.isdir(current_dir):
            logger.debug('Clearing {0}'.format(current_dir))
            fs.clear_links(current_dir)

    else:
        raise UnsupportedPlatform('%s is not a supported platform', SYSTEM)