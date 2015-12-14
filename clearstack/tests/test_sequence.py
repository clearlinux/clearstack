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

from clearstack.sequence import Sequence


class SequenceTest(testtools.TestCase):
    def setUp(self):
        super(SequenceTest, self).setUp()

    def test_run(self):
        mock_function = mock.Mock(return_value=False)
        mock_function.__name__ = 'Bar'

        seq = Sequence('test', mock_function)
        self.assertRaises(Exception, seq.run)

        seq = Sequence('test', mock_function, ["subsequence"])
        self.assertRaises(Exception, seq.run)
