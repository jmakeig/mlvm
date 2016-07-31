#!/usr/bin/env python
# coding=utf-8

"""MarkLogic Version Manager

Usage:
  mlvm list
  mlvm use <version> [--verbose]
  mlvm install <version> [--alias <name>] [--today | --yesterday] [--upgrade] [--verbose]
  mlvm install --local <package> [--alias <name>] [--upgrade] [--verbose]
  mlvm remove [<version> | --all] [--verbose]
  mlvm rename <version> <name> [--verbose]
  mlvm init [<host>] [--verbose]
  mlvm start
  mlvm stop
  mlvm eval <input> [--sjs | --xqy]
  mlvm ps
  
Options:
  -h --help     This screen
  --version     The version
  -a --alias    A preferred name for the version
  --today       Today’s nightly (requires credentials)
  --yesterday   Yesterday’s nightly (requires credentials)
  -l --local    Install a package from a local file
  -u --upgrade  Upgrade an existing installation
  -a --all      Remove all versions
  --sjs         Evaluate Server-Side JavaScript
  --xqy         Evaluate XQuery
  -v --verbose  More detailed information
  
Some other text:
  Here is some more text


"""

from docopt import docopt
import logging
import os
import platform
import getpass
import requests
from requests.auth import HTTPDigestAuth
import datetime

logger = logging.getLogger('mlvm')
logger.setLevel(logging.DEBUG)
#log = logging.FileHandler('mlvm.log')
log = logging.StreamHandler()
log.setLevel(logging.DEBUG)
log.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
logger.addHandler(log)


def download_file(url, local_filename = 'MarkLogic.dmg', onProgress=None, auth=None):
    #local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True, auth=auth)
    logger.debug(r.headers) # TODO: Handle errors
    #logger.info(r.headers.get('Content-Length'))
    total_size = int(r.headers.get('Content-Length'))
    chunk_size=1024
    running = 0
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                running += chunk_size
                if onProgress is not None:
                    onProgress(running, total_size)
    return local_filename

def show_progress(amt, total):
    logger.debug(str(amt) + ' of ' + str(total))

def install_package(package_path):
    logger.debug(package_path)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='2.0.0')
    # logger.debug(arguments)
# {'--alias': False,
#  '--all': False,
#  '--local': False,
#  '--nightly': False,
#  '--sjs': False,
#  '--upgrade': False,
#  '--verbose': False,
#  '--xqy': False,
#  '<host>': None,
#  '<input>': None,
#  '<name>': None,
#  '<package>': None,
#  '<version>': '9.0',
#  'eval': False,
#  'init': False,
#  'install': True,
#  'list': False,
#  'ps': False,
#  'remove': False,
#  'rename': False,
#  'start': False,
#  'stop': False,
#  'use': False}
    HOME = os.getenv('MLVM_HOME', '~/.mlvm/versions')
    logger.debug('HOME ' + HOME)
    SYSTEM = platform.system() # 'Darwin'
    logger.debug('SYSTEM ' + SYSTEM)
    
    if not os.path.isdir(HOME):
        logger.warn('Creating ' + HOME + ' becuase it does not yet exist')
        os.makedirs(HOME)
        # TODO: Ensure .mlvm/versions exists

    if arguments.get('install'):
        url = 'https://developer.marklogic.com/download/binaries/8.0/MarkLogic-8.0-5.5-x86_64.dmg?t=GUp8vqR53O5ItrB.KCXEu0&email=jmakeig%40marklogic.com'
        version = None
        package = None
        if arguments.get('--today'):
            version = arguments.get('<version>') # TODO: Allow of the form, 9, 9.0, 9.0-20160731
            today = datetime.date.today()
            nightly = today.strftime('%Y%m%d')
            # TODO: Branch for platform
            url = 'https://root.marklogic.com/nightly/builds/macosx-64/osx-intel64-' + '90' + '-build.marklogic.com/HEAD/pkgs.' + nightly + '/MarkLogic-' + version + '-' + nightly + '-x86_64.dmg'
            user = raw_input('Username for root.marklogic.com: ') # TODO: Validation
            password = getpass.getpass('Password for ' + user + ' on root.marklogic.com: ')
            # TODO: Download package to $HOME/downloads
            package = download_file(url, local_filename='MarkLogic.dmg', auth=HTTPDigestAuth(user, password), onProgress=show_progress)
        elif arguments.get('--local'):
            debug.error('local')

        install_package(package)            
