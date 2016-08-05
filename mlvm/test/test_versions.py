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

import unittest
from tap import TAPTestRunner

from mlvm.versions import get_release_artifact, parse_artifact_from_file
from mlvm.versions import parse_version, serialize_version


class TestVersions(unittest.TestCase):

    def test_parse_version(self):
        self.assertEqual(
            parse_version('9.0'), 
            {'major': '9', 'minor': '0', 'patch': None}
        )
        self.assertEqual(
            parse_version('9.0-1'), 
            {'major': '9', 'minor': '0', 'patch': '1'}
        )
        self.assertEqual(
            parse_version('99.8-7'), 
            {'major': '99', 'minor': '8', 'patch': '7'}
        )
        self.assertEqual(
            parse_version('99.8-76543210'), 
            {'major': '99', 'minor': '8', 'patch': '76543210'}
        )
        self.assertEqual(
            parse_version('99.8-77.66'), 
            {'major': '99', 'minor': '8', 'patch': '77.66'}
        )
        self.assertEqual(
            parse_version('MarkLogic-RHEL6-9.0-20160801.x86_64.rpm'), 
            {'major': '9', 'minor': '0', 'patch': '20160801'}
        )
        self.assertEqual(
            parse_version('MarkLogic-RHEL7-9.0-20160803.x86_64.rpm'), 
            {'major': '9', 'minor': '0', 'patch': '20160803'}
        )
        self.assertEqual(
            parse_version('MarkLogic-9.0-20160805-x86_64.dmg'), 
            {'major': '9', 'minor': '0', 'patch': '20160805'}
        )
        self.assertEqual(
            parse_version('MarkLogic-9.0-20160806-amd64.msi'), 
            {'major': '9', 'minor': '0', 'patch': '20160806'}
        )
        self.assertEqual(
            parse_version('MarkLogic-RHEL6-7.0-6.4.x86_64.rpm'), 
            {'major': '7', 'minor': '0', 'patch': '6.4'}
        )
        self.assertEqual(
            parse_version('MarkLogic-RHEL7-7.0-8.4.x86_64.rpm'), 
            {'major': '7', 'minor': '0', 'patch': '8.4'}
        )
        self.assertEqual(
            parse_version('MarkLogic-7.0-9.4-x86_64.dmg'), 
            {'major': '7', 'minor': '0', 'patch': '9.4'}
        )
        self.assertEqual(
            parse_version('MarkLogic-7.0-10.4-amd64.msi'), 
            {'major': '7', 'minor': '0', 'patch': '10.4'}
        )
        with self.assertRaises(Exception):
            parse_version('asdf')
        with self.assertRaises(Exception):
            parse_version(None)

if __name__ == '__main__':
    unittest.main()