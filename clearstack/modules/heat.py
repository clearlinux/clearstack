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

import configparser

from modules.openstack import OpenStackService
from modules.conf import CONF
from common import util
from common.util import LOG
from common.singleton import Singleton


@Singleton
class Heat(OpenStackService):
    _name = "heat"
    _bundle = "openstack-orchestration"
    _services = ["heat-api", "heat-api-cfn", "heat-engine"]
    _type = "orchestration"
    _description = "OpenStack Orchestration"
    _public_url = ("http://{0}:8004/v1/%\(tenant_id\)s"
                   .format(CONF['CONFIG_CONTROLLER_HOST']))

    domain_admin = CONF['CONFIG_HEAT_DOMAIN_ADMIN']
    domain_admin_pw = CONF['CONFIG_HEAT_DOMAIN_PASSWORD']
    domain_name = CONF['CONFIG_HEAT_DOMAIN']

    def sync_database(self):
        LOG.debug("syncing database")
        util.run_command("su -s /bin/sh -c"
                         " \"heat-manage db_sync\" heat")

    def config_auth(self, configfile):
        OpenStackService.config_auth(self, configfile)
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(configfile)
        auth_uri = config['keystone_authtoken']['auth_uri']
        config['trustee'] = config['keystone_authtoken']
        if not config.has_section('clients_keystone'):
            config.add_section('clients_keystone')
        config['clients_keystone']['auth_uri'] = auth_uri
        if not config.has_section('ec2authtoken'):
            config.add_section('ec2authtoken')
        config['ec2authtoken']['auth_uri'] = auth_uri
        with open(configfile, 'w') as f:
            config.write(f)

    def config_domain(self, configfile):
        config = ("[DEFAULT]\n"
                  "heat_metadata_server_url = http://{0}:8000\n"
                  "heat_waitcondition_server_url = "
                  "http://{0}:8000/v1/waitcondition\n"
                  "stack_domain_admin = {1}\n"
                  "stack_domain_admin_password = {2}\n"
                  "stack_user_domain_name = {3}\n"
                  .format(self._controller, self.domain_admin,
                          self.domain_admin_pw, self.domain_name))
        util.write_config(configfile, config)
