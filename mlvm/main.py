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

logger = logging.getLogger('mlvm')
logger.setLevel(logging.DEBUG)
#log = logging.FileHandler('mlvm.log')
log = logging.StreamHandler()
log.setLevel(logging.DEBUG)
log.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logger.addHandler(log)



from settings import HOME, SYSTEM

# TODO: Add error handling to make sure `prepare` has been called for 
#       all of the commands that need it

def route_command(arguments):
    if arguments.get('install'):
        from mlvm.commands.install import install  
        install(arguments) # TODO: Pass decouple arguments         
    elif arguments.get('prepare'):
        from mlvm.commands.prepare import prepare
        prepare()
    elif arguments.get('use'):
        from mlvm.commands.use import use
        use(arguments.get('<version>'))
    elif arguments.get('list'):
        from mlvm.commands.list import list
        list(sys.stdout)
    elif arguments.get('start'):
        from mlvm.commands.run import start
        start()
    elif arguments.get('stop'):
        from mlvm.commands.run import stop
        stop()
    elif arguments.get('ps'):
        from mlvm.commands.run import ps
        ps()
    elif arguments.get('init'):
        from mlvm.commands.init import init
        init(arguments.get('--host'), arguments.get('--rename'))
        