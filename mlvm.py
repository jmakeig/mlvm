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


def get_release_artifact(major, minor, patch, system=platform.system()):
    if 'Darwin' == system:
      return 'MarkLogic-' + major + '.' + minor + '-' + patch + '-x86_64.dmg'
    raise Exception('Not yet implemented')

def promptCredentials(realm):
    """ Callback to prompt for username and password """
    user = raw_input('Username for ' + realm + ': ') # TODO: Validation
    password = getpass.getpass('Password for ' + user + ' on ' + realm + ': ')
    return {'user': user, 'password': password}

def get_download_itr(major, minor, patch, is_nightly=False, onAuth=promptCredentials):
    major = str(int(major)) # 8
    minor = str(int(minor)) # 0
    patch = str(patch) # 5.5 or 20160731
        
    if is_nightly:
      # https://root.marklogic.com/nightly/builds/macosx-64/osx-intel64-80-build.marklogic.com/b8_0/pkgs.20160731/MarkLogic-8.0-20160731-x86_64.dmg
      ROOT_URL = 'https://root.marklogic.com'
      # TODO: Platform-specific
      auth = onAuth(ROOT_URL)
      url = ROOT_URL+ '/nightly/builds/macosx-64/osx-intel64-' + major + minor + '-build.marklogic.com/HEAD/pkgs.' + patch + '/' + get_release_artifact(major, minor, patch)
      logger.debug(url)
      return requests.get(url, auth=HTTPDigestAuth(auth.get('user'), auth.get('password')), stream=True).iter_content
    else:
      DMC_URL = 'https://developer.marklogic.com'
      auth = onAuth(DMC_URL)
      session = requests.Session()
      response = session.post(DMC_URL + '/login', data={'email': auth.get('user'), 'password': auth.get('password')})
      # TODO: Handle non-200 response
      # > 200 OK
      # > {"status":"ok","name":"Justin Makeig"}
      response = session.post(DMC_URL + '/get-download-url', data={'download': '/download/binaries/' + major + '.' + minor + '/' + get_release_artifact(major, minor, patch)}) # '/download/binaries/8.0/MarkLogic-8.0-5.5-x86_64.dmg'
      # TODO: Handle non-200 response
      # > 200 OK
      # > {"status":"ok","path":"/download/binaries/8.0/MarkLogic-8.0-5.5-x86_64.dmg?t=*************/&email=whoami%40example.com"}
      path = response.json().get('path')
      logger.debug(DMC_URL + path)
      return session.get(DMC_URL + path, stream=True).iter_content


def download_file(itr, local_filename = 'MarkLogic.dmg', total_size=None, onProgress=None):
    """ Given a response iterator, write chunks to a file. """
    chunk_size=1024 * 5
    running = 0
    with open(local_filename, 'wb') as f:
        for chunk in itr(chunk_size=chunk_size): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                running += chunk_size
                if onProgress is not None:
                    onProgress(running, total_size)
    return local_filename

def show_progress(amt, total, stream=None):
    logger.debug(str(amt) + ' of ' + str(total))

def install_package(package_path):
    logger.debug(package_path)

def parse_version(version):
    """ Parses a string, such as `'9.0-20160731'` or `'8.0-5.5'` into a 
        dictionary with keys, `major`, `minor`, and `patch`. """
    version = str(version)
    mm_patch = version.split('-')
    mm = mm_patch[0]
    patch = None
    if len(mm_patch) > 1:
        patch = mm_patch[1]
    mm_tokens = mm.split('.')
    major = int(mm_tokens[0])
    minor = None
    if len(mm_tokens) > 1:
        minor = int(mm_tokens[1])
    return {'major': major, 'minor': minor, 'patch': patch}

def ensure_directory(path):
    """ If a directory doesn’t exist at the path create it. """    
    if not os.path.isdir(path):
      logger.warn('Creating ' + path + ' becuase it does not yet exist')
      os.makedirs(path)
    return path

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
    HOME = os.getenv('MLVM_HOME', '~/.mlvm')
    logger.debug('HOME ' + HOME)
    SYSTEM = platform.system() # 'Darwin'
    logger.debug('SYSTEM ' + SYSTEM)
    
    ensure_directory(HOME)

    if arguments.get('install'):
        version = parse_version(arguments.get('<version>')) # TODO: Allow of the form, 9, 9.0, 9.0-20160731
        package = None
        if arguments.get('--today'):
            if version.get('patch') is not None:
              raise Exception('You must not specify a patch release with the --today option')
            today = datetime.date.today()
            nightly = today.strftime('%Y%m%d')
            package = download_file(
                get_download_itr(
                    version.get('major'), 
                    version.get('minor'), 
                    nightly, 
                    is_nightly=True
                ), 
                local_filename = ensure_directory(HOME + '/downloads') + '/MarkLogic.dmg', 
                onProgress=show_progress
            )
        elif arguments.get('--local'):
            debug.error('local')
        else:
            logger.debug(version)
            package = download_file(
                get_download_itr(
                    version.get('major'),
                    version.get('minor'),
                    version.get('patch')
                ),
                local_filename = ensure_directory(HOME + '/downloads') + '/MarkLogic.dmg',
                onProgress=show_progress
            )

        install_package(package)            
