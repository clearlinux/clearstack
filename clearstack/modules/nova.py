#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
# Author: Julio Montes <julio.montes@intel.com>
# Author: Obed Munoz <obed.n.munoz@intel.com>
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

from modules.openstack import OpenStackService
from modules.ceilometer import Ceilometer
from modules.conf import CONF
from common import util
from common.util import LOG
from common.singleton import Singleton


@Singleton
class Nova(OpenStackService):
    _name = "nova"
    _bundle = "openstack-compute-controller"
    _services = ["nova-cert", "nova-consoleauth", "nova-scheduler",
                 "nova-conductor", "nova-novncproxy"]
    if CONF['CONFIG_HTTP_SERVICE'] == 'nginx':
        _services.extend(["nginx", "uwsgi@nova-api.socket",
                          "uwsgi@nova-metadata.socket"])
    elif CONF['CONFIG_HTTP_SERVICE'] == 'apache2':
        _services.append("httpd")
    else:
        _services.append("nova-api")
    _type = "compute"
    _description = "OpenStack Compute"
    _password = CONF['CONFIG_NOVA_KS_PW']
    _public_url = ("http://{0}:8774/v2/%\(tenant_id\)s"
                   .format(CONF['CONFIG_CONTROLLER_HOST']))

    def install_compute(self):
        self.install("openstack-compute")

    def sync_database(self):
        LOG.debug("syncing database")
        util.run_command("su -s /bin/sh -c \"nova-manage db sync\" nova")

    def ceilometer_enable(self, configfile):
        ceilometer = Ceilometer.get()
        ceilometer_cfg = "/etc/ceilometer/ceilometer.conf"

        ceilometer.install()
        ceilometer.config_rabbitmq(ceilometer_cfg)
        ceilometer.config_auth(ceilometer_cfg)
        ceilometer.config_service_credentials(ceilometer_cfg)

        config = ("[DEFAULT]\n"
                  "instance_usage_audit = True\n"
                  "instance_usage_audit_period = hour\n"
                  "notify_on_state_change = vm_and_task_state\n"
                  "notification_driver = messagingv2\n")
        util.write_config(configfile, config)
        self.start_server(['ceilometer-agent-compute.service'])
