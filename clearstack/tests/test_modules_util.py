#
# Copyright (c) 2015 Intel Corporation
#
# Author: Julio Montes <julio.montes@intel.com>
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

import testtools

from clearstack.common import util


class ModulesUtilTest(testtools.TestCase):
    def setUp(self):
        super(ModulesUtilTest, self).setUp()

    # # Test if run_command is hidden debug logs
    # def test_0000_run_command(self):
    #     util.setup_debugging(True, False)
    #     util.run_command("echo", debug=False)
    #     logging.StreamHandler().close()
    #     self.assertEqual("echo" in open(self.log_file).read(), False)

    # # Test if run_command is showing debug logs
    # def test_0001_run_command(self):
    #     util.setup_debugging(True, False)
    #     util.run_command("echo")
    #     logging.StreamHandler().close()
    #     self.assertEqual("echo" in open(self.log_file).read(), True)

    # Test command not found
    def test_0002_run_command(self):
        self.assertRaises(Exception, util.run_command, "inexistente")

    # Test simple command
    def test_0003_run_command(self):
        try:
            util.run_command("echo")
        except Exception:
            self.fail()
