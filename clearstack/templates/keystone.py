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

from modules.conf import CONF
from modules.keystone import Keystone
from common import util

keystone = Keystone.get()
config_file = "/etc/keystone/keystone.conf"

keystone.install()
keystone.config_debug(config_file)
keystone.config_database(config_file)
keystone.config_admin_token(config_file)

util.run_command("systemctl restart update-triggers.target")
keystone.sync_database()
keystone.start_server()

keystone.create_service()
keystone.create_endpoint()
keystone.create_project("admin", "Admin Project")
keystone.create_role("admin")
keystone.create_user(user="admin", project="admin", role="admin")
keystone.create_project("service", "Service Project")
keystone.create_project("demo", "Demo Project")
keystone.create_role("user")
keystone.create_user(user="demo", project="demo", role="user",
                     password=CONF['CONFIG_KEYSTONE_DEMO_PW'])
util.delete_option(config_file, "DEFAULT", "admin_token")
keystone.start_server()
