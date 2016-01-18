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

from modules.keystone import Keystone
from modules.openstack import OpenStackService
from modules.conf import CONF
from common import util
from common.singleton import Singleton


@Singleton
class Ceilometer(OpenStackService):
    _name = "ceilometer"
    _bundle = "openstack-telemetry"
    _services = ["ceilometer-agent-central", "ceilometer-agent-notification",
                 "ceilometer-api", "ceilometer-collector",
                 "ceilometer-alarm-evaluator", "ceilometer-alarm-notifier"]
    _type = "metering"
    _description = "OpenStack Telemetry Service"
    _public_url = "http://{0}:8777".format(CONF['CONFIG_CONTROLLER_HOST'])

    def config_database(self, configfile):
        dbpass = CONF['CONFIG_%s_DB_PW' % self._name.upper()]
        dbhost = CONF['CONFIG_MONGODB_HOST']
        config = ("[database]\n"
                  "connection=mongodb://{0}:{1}@{2}:27017/{0}"
                  .format(self._name, dbpass, dbhost))
        util.write_config(configfile, config)

    def config_service_credentials(self, configfile):
        keystone = Keystone.get()
        config = \
            "[service_credentials]\n" + \
            "os_auth_url = %s\n" % keystone._admin_url + \
            "os_username = %s\n" % self._name + \
            "os_tenant_name = service\n" + \
            "os_password = %s\n" % self._password + \
            "os_endpoint_type = internalURL\n" + \
            "os_region_name = %s\n" % self._region
        util.write_config(configfile, config)
