#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
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

import os

from common import util
from common.util import LOG


class Client():
    def install(bundle):
        if not os.path.isfile("/usr/share/clear/bundles/" + str(bundle)) and \
            not os.path.isfile("/usr/share/clear/bundles/"
                               "openstack-all-in-one"):
            LOG.info("Installing {0} bundle".format(bundle))
            cmd = "clr_bundle_add -V {0}".format(bundle)
            if(os.path.isfile("/bin/swupd")):
                cmd = "swupd bundle-add -V {0}".format(bundle)

            try:
                stdout, stderr = util.run_command(cmd)
                if stderr:
                    LOG.error("swupd bundle-add: {0}\n{1}"
                              .format(stdout, stderr))
            except Exception:
                LOG.error("clearstack: cannot install"
                          " {0} bundle".format(bundle))
