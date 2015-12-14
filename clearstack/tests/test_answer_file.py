#
# Copyright (c) 2015 Intel Corporation
#
# Author: Julio Montes <julio.montes@intel.com>
# Author: Victor Morales <victor.morales@intel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import mock
import testtools

from clearstack.answer_file import AnswerFile
from clearstack.argument import Argument
from clearstack.controller import Controller

conf = {'COMPONENT': [Argument('argument',
                               'description',
                               'CONFIG_ARGUMET',
                               'secure')]}

for group in conf:
    Controller.get().add_group(group, conf[group])


class AnswerFileTest(testtools.TestCase):
    def setUp(self):
        super(AnswerFileTest, self).setUp()

    def test_generate_file(self):
        m = mock.mock_open()
        filename = '/tmp/clearstack.answerfile'
        with mock.patch('clearstack.answer_file.open', m, create=True):
            AnswerFile.get().generate(filename, {})
        m.assert_called_once_with(filename, 'w')

    @mock.patch('os.path.isfile')
    def test_read_non_existing_file(self, mock_isfile):
        mock_isfile.side_effect = [False]
        filename = '/tmp/clearstack.answerfile'
        self.assertRaises(IOError, AnswerFile.get().read, filename, {})
