#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
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
from modules.neutron import Neutron
from common import util


neutron = Neutron.get()
config_file = "/etc/neutron/neutron.conf"
ip_list = CONF['CONFIG_CONTROLLER_HOST'].split(',')
local_ip = util.find_my_ip_from_config(ip_list)
local_nic = util.get_nic(local_ip)

# Install neutron controller
neutron.install()
neutron.create_user()
neutron.create_service()
neutron.create_endpoint()

# Configure neutron controller
neutron.config_debug(config_file)
neutron.config_database(config_file)
neutron.config_rabbitmq(config_file)
neutron.config_auth(config_file)

neutron.config_nova(config_file)
neutron.config_ml2_plugin()
neutron.config_linux_bridge_agent(local_ip, local_nic)
neutron.config_l3_agent("/etc/neutron/l3_agent.ini")
neutron.config_dhcp_agent("/etc/neutron/dhcp_agent.ini")
neutron.config_metadata_agent("/etc/neutron/metadata_agent.ini")
neutron.config_neutron_on_nova("/etc/nova/nova.conf")

if util.str2bool(CONF['CONFIG_CEILOMETER_INSTALL']):
    neutron.ceilometer_enable(config_file)

if util.str2bool(CONF['CONFIG_LBAAS_INSTALL']):
    neutron.install('openstack-lbaas')
    neutron.config_lbaas()

if util.str2bool(CONF['CONFIG_VPNAAS_INSTALL']):
    neutron.install('openstack-vpnaas')
    neutron.config_vpnaas()

util.run_command("systemctl restart update-triggers.target")
neutron.sync_database()
neutron.start_server()
