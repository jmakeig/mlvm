#!/usr/bin/env python
# coding=utf-8

"""MarkLogic Version Manager

Usage:
  mlvm list [--remote] [--verbose | --debug]
  mlvm use <version> [--verbose | --debug]
  mlvm install <version> [--alias <name>] [--today | --yesterday] [--upgrade] [--verbose | --debug]
  mlvm install --local <package> [--alias <name>] [--upgrade] [--verbose | --debug]
  mlvm remove [<version> | --all] [--verbose | --debug]
  mlvm rename <version> <name> [--alias] [--verbose | --debug]
  mlvm init [<host>] [--verbose | --debug]
  mlvm start [--verbose | --debug]
  mlvm stop [--verbose | --debug]
  mlvm eval <input> [--sjs | --xqy]
  mlvm ps
  
Options:
  -h --help     This screen
  --remote      Include remote versions as well
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
  --debug       Developer debugging information
  
Some other text:
  Here is some more text


"""

from docopt import docopt
import logging
import os
import platform
import subprocess
import getpass
#import tempfile
#import uuid
import re
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
      return 'MarkLogic-' + major + '.' + minor + '-' + patch + '-x86_64'
    raise Exception('Not yet implemented')
    
def parse_artifact_from_file(file):
    pattern = 'MarkLogic-(?:RHEL\d-)?\d{1,2}\.\d-(?:(?:\d{8})|(?:\d{1,2}\.\d{1,2}))[\.\-](?:x86_|amd)64'
    match = re.findall(pattern, file)
    if len(match) == 1:
        return match[0]
    raise Exception(artifact + ' does not match a MarkLogic version')

def promptCredentials(realm):
    """ Callback to prompt for username and password """
    user = raw_input('Username for ' + realm + ': ') # TODO: Validation
    password = getpass.getpass('Password for ' + user + ' on ' + realm + ': ')
    return {'user': user, 'password': password}

def get_download_itr(major, minor, patch, is_nightly=False, onAuth=promptCredentials):
    #major = str(int(major)) # 8
    #minor = str(int(minor)) # 0
    #patch = str(patch) # 5.5 or 20160731
        
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
        response = session.post(DMC_URL + '/get-download-url', data={'download': '/download/binaries/' + major + '.' + minor + '/' + get_release_artifact(major, minor, patch) + '.dmg'}) # FIXME: Platform-specific
        # TODO: Handle non-200 response
        # > 200 OK
        # > {"status":"ok","path":"/download/binaries/8.0/MarkLogic-8.0-5.5-x86_64.dmg?t=*************/&email=whoami%40example.com"}
        logger.debug(response.status_code)
        if 200 != response.status_code:
            raise Exception(response.text) # TODO: Better exceptions?
        path = response.json().get('path')
        logger.debug(DMC_URL + path)
        return session.get(DMC_URL + path, stream=True).iter_content

def download_file(itr, local_filename, total_size=None, onProgress=None):
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

def install_package(path, artifact, alias=None, system=platform.system()):
    logger.info('Installing ' + alias + ' from ' + path + ' with artifact ' + artifact)
    if alias is None:
        alias = artifact
    if not os.path.isfile(path):
        raise Exception(path + ' does not exist')
    if 'Darwin' == system:
        #mount_point = tempfile.gettempdir() + '/' + str(uuid.uuid4())
        #mount_point = ensure_directory(HOME + '/temp') + '/' + str(uuid.uuid4())
        #logger.debug(mount_point)
        #subprocess.call(["hdiutil", "attach", path, "-mountpoint", mount_point, "-verbose"]) #, "-nobrowse", "-quiet"])
        try:
            from gmacpyutil import macdisk
            img = macdisk.Image(path)
            disk = img.Attach()
        
            from gmacpyutil import RunProcess
            cmd = ['tar', 'xfz', '/Volumes/MarkLogic/' + artifact + '.pkg/Contents/Archive.pax.gz', 
                '-C', ensure_directory(HOME + '/versions/' + alias)]
            result = RunProcess(cmd)
            logger.debug(result)
            if 0 != result[2]:
                raise Exception(result[1])
            ensure_directory(HOME + '/versions/' + alias + '/Support/Data')
            os.chmod(HOME + '/versions/' + alias + '/StartupItems/MarkLogic/MarkLogic', 0775) # TODO: +x, not hard-coded
        finally:
            logger.debug('Detaching disk image')
            img.Detach(force=True)
    else:
        raise Exception('Support for ' + system + ' is not yet implemented')
      

def parse_version(version):
    """ Parses a string, such as `'9.0-20160731'` or `'8.0-5.5'` into a 
        dictionary with keys, `major`, `minor`, and `patch`. """
        
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
    pattern = '(?:MarkLogic-(?:RHEL\d-)?)?(\d{1,2}\.\d-(?:(?:\d{8})|(?:\d{1,2}\.\d{1,2})))(?:[\.\-](?:x86_|amd)64)?'
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

def ensure_directory(path):
    """ If a directory doesn’t exist at the path create it. """    
    if not os.path.isdir(path):
      logger.debug('Creating ' + path + ' becuase it does not yet exist')
      os.makedirs(path)
    return path

if __name__ == '__main__':
    arguments = docopt(__doc__, version='2.0.0')
    #logger.debug(arguments)
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
        package = arguments.get('<package>')
        artifact = None
        alias = arguments.get('<name>')
        if arguments.get('--local'):
            artifact = parse_artifact_from_file(package)
            if alias is None:
                alias = serialize_version(parse_version(artifact))
        else:
            version = parse_version(arguments.get('<version>'))
            if arguments.get('--today'):
                if version.get('patch') is not None:
                  raise Exception('You must not specify a patch release with the --today option')
                today = datetime.date.today()
                nightly = today.strftime('%Y%m%d')
                artifact = get_release_artifact(version.get('major'), version.get('minor'), nightly)
                dest = ensure_directory(HOME + '/downloads') + '/' + artifact + '.dmg'
                package = download_file(
                    get_download_itr(
                        version.get('major'), 
                        version.get('minor'), 
                        nightly, 
                        is_nightly=True
                    ), 
                    local_filename = dest, 
                    onProgress=show_progress
                )
            else:
                artifact = get_release_artifact(version.get('major'), version.get('minor'), version.get('patch'))
                dest = ensure_directory(HOME + '/downloads') + '/' + artifact + '.dmg'
                package = download_file(
                    get_download_itr(
                        version.get('major'),
                        version.get('minor'),
                        version.get('patch')
                    ),
                    local_filename = dest,
                    onProgress=show_progress
                )

        install_package(package, artifact, alias=alias)            
    elif arguments.get('use'):
        raise Exception('use isn’t implemented yet')
        #         rm ~/Library/MarkLogic ~/Library/Application\ Support/MarkLogic ~/Library/PreferencePanes/MarkLogic.prefPane
        #         rm $SOURCE/versions/.current/MarkLogic $SOURCE/versions/.current/MarkLogic/StartupParameters.plist
        #         vdir=$(versiondir $1)
        #         ln -s $vdir/MarkLogic ~/Library/MarkLogic
        #         ln -s $vdir/Support ~/Library/Application\ Support/MarkLogic
        #         ln -s $vdir/PreferencePanes/MarkLogic.prefPane ~/Library/PreferencePanes/MarkLogic.prefPane
        #         # current version links for startup commands
        #         ln -s $vdir/StartupItems/MarkLogic/MarkLogic $SOURCE/versions/.current/MarkLogic
        #         ln -s $vdir/StartupItems/MarkLogic/StartupParameters.plist $SOURCE/versions/.current/StartupParameters.plist    