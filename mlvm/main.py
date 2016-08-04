# coding=utf-8

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

################################################################################
from versions import get_release_artifact, parse_artifact_from_file, parse_version, serialize_version
################################################################################

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
        url = ROOT_URL+ '/nightly/builds/macosx-64/osx-intel64-' + major + minor + '-build.marklogic.com/HEAD/pkgs.' + patch + '/' + get_release_artifact(major, minor, patch) + '.dmg'
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
        try:
            from gmacpyutil import macdisk
            img = macdisk.Image(path)
            disk = img.Attach()
        
            from gmacpyutil import RunProcess
            # pax.gz doesn’t seem to be properly supported by Python’s tar library
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
      
def ensure_directory(path):
    """ If a directory doesn’t exist at the path create it. """    
    if not os.path.isdir(path):
      logger.debug('Creating ' + path + ' becuase it does not yet exist')
      os.makedirs(path)
    return path

from settings import HOME, SYSTEM

def route_command(arguments):     
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
        from mlvm.commands.use import use
        use()
        #         rm ~/Library/MarkLogic ~/Library/Application\ Support/MarkLogic ~/Library/PreferencePanes/MarkLogic.prefPane
        #         rm $SOURCE/versions/.current/MarkLogic $SOURCE/versions/.current/MarkLogic/StartupParameters.plist
        #         vdir=$(versiondir $1)
        #         ln -s $vdir/MarkLogic ~/Library/MarkLogic
        #         ln -s $vdir/Support ~/Library/Application\ Support/MarkLogic
        #         ln -s $vdir/PreferencePanes/MarkLogic.prefPane ~/Library/PreferencePanes/MarkLogic.prefPane
        #         # current version links for startup commands
        #         ln -s $vdir/StartupItems/MarkLogic/MarkLogic $SOURCE/versions/.current/MarkLogic
        #         ln -s $vdir/StartupItems/MarkLogic/StartupParameters.plist $SOURCE/versions/.current/StartupParameters.plist    