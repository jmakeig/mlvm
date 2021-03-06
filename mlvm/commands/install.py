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
import datetime

from mlvm.settings import HOME, SYSTEM, USER
import mlvm.filesystem as fs
import mlvm.cli as cli
import mlvm.versions as versions

logger = logging.getLogger('mlvm')

""" `True` to bypass the actual download for testing. 
Assumes you’ve already got the artifact downloaded to the downloads folder. """
BYPASS_REMOTE = False # Make sure not to check this in as True

def get_download_itr(major, minor, patch, is_nightly = False, onAuth = cli.promptCredentials):
    import requests
    from requests.auth import HTTPDigestAuth

    if BYPASS_REMOTE:
        return 'BYPASS_REMOTE'

    if is_nightly:
        # https://root.marklogic.com/nightly/builds/macosx-64/osx-intel64-80-build.marklogic.com/b8_0/pkgs.20160731/MarkLogic-8.0-20160731-x86_64.dmg
        ROOT_URL = 'https://root.marklogic.com'
        # TODO: Platform-specific
        auth = onAuth(ROOT_URL)
        # FIXME: Cross-platform
        url = ROOT_URL+ '/nightly/builds/macosx-64/osx-intel64-' + major + minor + '-build.marklogic.com/HEAD/pkgs.' + patch + '/' + versions.get_release_artifact(major, minor, patch) + '.dmg'
        logger.debug(url)
        response = requests.get(url, auth = HTTPDigestAuth(auth.get('user'), auth.get('password')), stream = True)
        response.raise_for_status()
        return response.iter_content
    else:
        DMC_URL = 'https://developer.marklogic.com'
        auth = onAuth(DMC_URL)
        session = requests.Session()
        response = session.post(DMC_URL + '/login', data={'email': auth.get('user'), 'password': auth.get('password')})
        response.raise_for_status()
        # TODO: Handle non-200 response
        # > 200 OK
        # > {"status":"ok","name":"Justin Makeig"}
        response = session.post(DMC_URL + '/get-download-url', data={'download': '/download/binaries/' + major + '.' + minor + '/' + versions.get_release_artifact(major, minor, patch) + '.dmg'}) # FIXME: Platform-specific
        response.raise_for_status()
        # TODO: Handle non-200 response
        # > 200 OK
        # > {"status":"ok","path":"/download/binaries/8.0/MarkLogic-8.0-5.5-x86_64.dmg?t=*************/&email=whoami%40example.com"}
        path = response.json().get('path')
        logger.debug(DMC_URL + path)
        return session.get(DMC_URL + path, stream=True).iter_content

def download_file(itr, local_filename, total_size = None, onProgress = None):
    """ Given a response iterator, write chunks to a file. """

    if BYPASS_REMOTE:
        return local_filename
    
    chunk_size = 1024 * 5
    running = 0
    with open(local_filename, 'wb') as f:
        for chunk in itr(chunk_size=chunk_size): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                running += chunk_size
                if onProgress is not None:
                    onProgress(running, total_size)
    return local_filename

def install_package(path, artifact, alias=None, system = SYSTEM):
    if alias is None:
        alias = artifact
    if not os.path.isfile(path):
        raise Exception(path + ' does not exist')
    
    logger.info('Installing %s from %s with artifact %s', alias, path, artifact)
    
    if 'Darwin' == system:
        try:
            from gmacpyutil import macdisk
            
            img = macdisk.Image(path)
            disk = img.Attach()
            
            from gmacpyutil import RunProcess # returns (stdout, stderr, returncode)

            # pax.gz doesn’t seem to be properly supported by Python’s tar library
            cmd = ['tar', 'xfz', '/Volumes/MarkLogic/' + artifact + '.pkg/Contents/Archive.pax.gz', 
                '-C', fs.ensure_directory(HOME + '/versions/' + alias)] 
            result = RunProcess(cmd)
            logger.debug(result)
            if 0 != result[2]:
                raise Exception(result[1])
            fs.ensure_directory(HOME + '/versions/' + alias + '/Support/Data')
            os.chmod(HOME + '/versions/' + alias + '/StartupItems/MarkLogic/MarkLogic', 0755) # TODO: +x, not hard-coded
        finally:
            logger.debug('Detaching disk image')
            img.Detach(force=True)
    else:
        raise Exception('Support for ' + system + ' is not yet implemented')

# mlvm install <version> [--alias=<name>] [--today | --yesterday] [--upgrade] [--verbose | --debug]
# mlvm install --local=<package> [--alias <name>] [--upgrade] [--verbose | --debug]
#
# args = {
#     'version': None, 
#     'nightly': 'TODAY|YESTERDAY',
##########################################
#     'local': None,
##########################################
#     'upgrade': False,
#     'alias': None,
# }



def install(arguments):
    fs.ensure_directory(HOME)

    package = arguments.get('--local')
    artifact = None
    alias = arguments.get('<name>')
    if arguments.get('--local'):
        artifact = versions.parse_artifact_from_file(package)
        if alias is None:
            alias = versions.serialize_version(versions.parse_version(artifact))
    else:
        version = versions.parse_version(arguments.get('<version>'))
        if arguments.get('--nightly'):
            if version.get('patch') is None:
                version['patch'] = datetime.date.today().strftime('%Y%m%d')
            artifact = versions.get_release_artifact(version.get('major'), version.get('minor'), version['patch'])
            alias = versions.serialize_version(versions.parse_version(artifact))
            # FIXME: Cross-platform
            dest = fs.ensure_directory(HOME + '/downloads') + '/' + artifact + '.dmg'
            package = download_file(
                get_download_itr(
                    version.get('major'), 
                    version.get('minor'), 
                    version.get('patch'), 
                    is_nightly=True
                ), 
                local_filename = dest, 
                onProgress=cli.show_progress
            )
        else:
            artifact = versions.get_release_artifact(version.get('major'), version.get('minor'), version.get('patch'))
            # FIXME: Cross-platform
            dest = fs.ensure_directory(HOME + '/downloads') + '/' + artifact + '.dmg'
            package = download_file(
                get_download_itr(
                    version.get('major'),
                    version.get('minor'),
                    version.get('patch')
                ),
                local_filename = dest,
                onProgress=cli.show_progress
            )
    install_package(package, artifact, alias=alias)   
