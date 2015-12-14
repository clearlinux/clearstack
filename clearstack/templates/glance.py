#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
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

from common import util
from modules.conf import CONF
from modules.glance import Glance


glance = Glance.get()
config_files = ["/etc/glance/glance-api.conf"]
config_files.append("/etc/glance/glance-registry.conf")

glance.install()
glance.create_user()
glance.create_service()
glance.create_endpoint()

for config_file in config_files:
    glance.config_debug(config_file)
    glance.config_database(config_file)
    glance.config_auth(config_file)
    if util.str2bool(CONF['CONFIG_CEILOMETER_INSTALL']):
        glance.ceilometer_enable(config_file)

util.run_command("systemctl restart update-triggers.target")
glance.sync_database()
glance.start_server()
