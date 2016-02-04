#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
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

from ipaddress import IPv4Network

from modules.keystone import Keystone
from modules.nova import Nova
from modules.openstack import OpenStackService
from modules.conf import CONF
from common import util
from common.util import LOG
from common.singleton import Singleton


metadata_password = CONF['CONFIG_NEUTRON_METADATA_PW']
tenant_network_types = CONF['CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES']
mechanism_drivers = CONF['CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS']
vni_ranges = CONF['CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES']
type_drivers = CONF['CONFIG_NEUTRON_ML2_TYPE_DRIVERS']
flat_networks = CONF['CONFIG_NEUTRON_ML2_FLAT_NETWORKS']


@Singleton
class Neutron(OpenStackService):
    _name = "neutron"
    _bundle = "openstack-network"
    _services = ["neutron-server", "neutron-linuxbridge-agent",
                 "neutron-dhcp-agent", "neutron-metadata-agent",
                 "neutron-l3-agent"]
    _type = "network"
    _description = "OpenStack Networking"
    _public_url = ("http://{0}:9696"
                   .format(CONF['CONFIG_CONTROLLER_HOST']))

    def sync_database(self):
        LOG.debug("populating neutron database")
        util.run_command('su -s /bin/sh -c "neutron-db-manage '
                         '--config-file /etc/neutron/neutron.conf '
                         '--config-file /etc/neutron/plugins/ml2/ml2_conf.ini '
                         'upgrade head" neutron')
        if util.str2bool(CONF['CONFIG_LBAAS_INSTALL']):
            util.run_command('su -s /bin/sh -c "neutron-db-manage '
                             '--service lbaas upgrade head"')

    def config_ml2_plugin(self):
        config = \
            "[DEFAULT]\n" + \
            "core_plugin = ml2\n" \
            "service_plugins = router\n" + \
            "allow_overlapping_ips = True\n"
        util.write_config("/etc/neutron/neutron.conf", config)
        config = \
            "[ml2]\n" + \
            "type_drivers = %s\n" % type_drivers + \
            "tenant_network_types = %s\n" % tenant_network_types + \
            "mechanism_drivers = %s\n" % mechanism_drivers + \
            "extension_drivers = port_security\n" + \
            "[ml2_type_flat]\n" + \
            "flat_networks = public\n" + \
            "[ml2_type_vxlan]\n" + \
            "vni_ranges = %s\n" % vni_ranges + \
            "[securitygroup]\n" + \
            "enable_ipset = True\n"
        util.write_config("/etc/neutron/plugins/ml2/ml2_conf.ini", config)
        util.link_file('/etc/neutron/plugins/ml2/ml2_conf.ini',
                       '/etc/neutron/plugin.ini')

    def config_linux_bridge_agent(self, local_ip, local_nic):
        config = \
            "[linux_bridge]\n" + \
            "physical_interface_mappings = public:%s\n" % local_nic + \
            "[vxlan]\n" + \
            "enable_vxlan = True\n" + \
            "local_ip = %s\n" % local_ip + \
            "l2_population = True\n" + \
            "[agent]\n" + \
            "prevent_arp_spoofing = True\n" + \
            "[securitygroup]\n" + \
            "enable_security_group = True\n" + \
            "firewall_driver = neutron.agent.linux.iptables_firewall." + \
            "IptablesFirewallDriver\n"
        util.write_config("/etc/neutron/plugins/ml2/linuxbridge_agent.ini",
                          config)

    def config_l3_agent(self, configfile):
        config = ("[DEFAULT]\n"
                  "interface_driver = "
                  "neutron.agent.linux.interface.BridgeInterfaceDriver\n"
                  "external_network_bridge = \n")
        util.write_config(configfile, config)

    def config_dhcp_agent(self, configfile):
        config = ("[DEFAULT]\n"
                  "interface_driver = "
                  "neutron.agent.linux.interface.BridgeInterfaceDriver\n"
                  "dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq\n"
                  "enable_isolated_metadata = True\n")
        util.write_config(configfile, config)

    def config_metadata_agent(self, configfile):
        config = \
            "[DEFAULT]\n" + \
            "auth_uri = http://%s:5000\n" % self._controller + \
            "auth_url = http://%s:35357\n" % self._controller + \
            "auth_region = %s\n" % self._region + \
            "auth_plugin = password\n" + \
            "project_domain_id = default\n" + \
            "user_domain_id = default\n" + \
            "project_name = service\n" + \
            "username = %s\n" % self._name + \
            "password = %s\n" % self._password + \
            "nova_metadata_ip = %s\n" % self._controller + \
            "metadata_proxy_shared_secret = %s\n" % metadata_password
        util.write_config(configfile, config)

    def config_nova(self, configfile):
        nova = Nova.get()
        config = ("[DEFAULT]\n"
                  "notify_nova_on_port_status_changes = True\n"
                  "notify_nova_on_port_data_changes = True\n"
                  "nova_url = http://{0}:8774/v2\n"
                  "[nova]\n"
                  "auth_url = http://{0}:35357\n"
                  "auth_plugin = password\n"
                  "project_domain_id = default\n"
                  "user_domain_id = default\n"
                  "region_name = {1}\n"
                  "project_name = service\n"
                  "username = nova\n"
                  "password = {2}\n"
                  .format(self._controller, self._region, nova._password))
        util.write_config(configfile, config)

    def config_neutron_on_nova(self, configfile):
        keystone = Keystone.get()
        config = \
            "[DEFAULT]\n" + \
            "network_api_class = nova.network.neutronv2.api.API\n" + \
            "security_group_api = neutron\n" + \
            "linuxnet_interface_driver = " + \
            "nova.network.linux_net.NeutronLinuxBridgeInterfaceDriver\n" + \
            "firewall_driver = nova.virt.firewall.NoopFirewallDriver\n" + \
            "[neutron]\n" + \
            "url = %s\n" % self._public_url + \
            "auth_url = %s\n" % keystone._admin_url + \
            "auth_plugin = password\n" + \
            "project_domain_id = default\n" + \
            "user_domain_id = default\n" + \
            "region_name = %s\n" % self._region + \
            "project_name = service\n" + \
            "username = neutron\n" + \
            "password = %s\n" % self._password + \
            "service_metadata_proxy = True\n" + \
            "metadata_proxy_shared_secret = %s\n" % metadata_password
        util.write_config(configfile, config)
        if CONF['CONFIG_HTTP_SERVICE'] == 'nginx':
            nova_api_services = ['uwsgi@nova-api.socket',
                                 'uwsgi@nova-metadata.socket']
        elif CONF['CONFIG_HTTP_SERVICE'] == 'apache2':
            nova_api_services = ['httpd']
        else:
            nova_api_services = ['nova-api']
        self.start_server(nova_api_services)

    def add_service_plugin(self, plugin):
        plugins = util.get_option('/etc/neutron/neutron.conf',
                                  'DEFAULT', 'service_plugins').split(',')
        if plugin not in plugins:
            plugins.append(plugin)
        config = ('[DEFAULT]\n'
                  "service_plugins = %s\n" % ','.join(plugins))
        util.write_config("/etc/neutron/neutron.conf", config)

    def config_lbaas(self):
        self.add_service_plugin('lbaas')
        config = ("[DEFAULT]\n"
                  "interface_driver = "
                  "neutron.agent.linux.interface.BridgeInterfaceDriver\n")
        util.write_config("/etc/neutron/lbaas_agent.ini", config)
        self._services += ['neutron-lbaas-agent']

    def config_vpnaas(self):
        self.add_service_plugin('vpnaas')
        driver = ("neutron_vpnaas.services.vpn.device_drivers.libreswan_ipsec"
                  ".LibreSwanDriver")
        config = "[vpnagent]\n" + \
                 "vpn_device_driver = %s\n" % driver
        util.write_config("/etc/neutron/vpnaas_agent.ini", config)
        self._services += ['ipsec', 'neutron-vpn-agent']

    def create_network(self, name, network, public=None):
        cidr = IPv4Network(network)
        cidr_e = cidr.exploded
        cidr_gw = (cidr.network_address + 1).exploded
        cidr_start = (cidr.network_address + 2).exploded
        cidr_end = (cidr.broadcast_address - 1).exploded
        try:
            LOG.debug("checking if network '{0}' exists".format(name))
            util.run_command("neutron net-show %s" % name,
                             environ=self._env)
        except:
            LOG.debug("creating network '{0}'".format(name))
            cmd = "neutron net-create %s" % name
            if public:
                cmd += (" --provider:physical_network public"
                        " --shared --provider:network_type flat")
            util.run_command(cmd, environ=self._env)
            cmd = ("neutron subnet-create %s %s --name %s"
                   " --gateway %s" % (name, cidr_e, name, cidr_gw))
            if public:
                cmd += (" --allocation-pool start=%s,end=%s"
                        % (cidr_start, cidr_end))
            util.run_command(cmd, environ=self._env)
            if public:
                util.run_command("neutron net-update %s --router:external"
                                 % name, environ=self._env)

    def create_router(self, router, gw, interfaces):
        try:
            LOG.debug("checking if router '{0}' exists".format(router))
            util.run_command("neutron router-show %s" % router,
                             environ=self._env)
        except:
            LOG.debug("creating router '{0}'".format(router))
            util.run_command("neutron router-create %s" % router,
                             environ=self._env)
            util.run_command("neutron router-gateway-set %s %s"
                             % (router, gw), environ=self._env)
            for i in interfaces:
                util.run_command("neutron router-interface-add %s %s"
                                 % (router, i), environ=self._env)

    def ceilometer_enable(self, configfile):
        LOG.debug("setting up rabbitmq configuration"
                  " in '{0}'".format(configfile))
        self.config_rabbitmq(configfile)
        config = ("[DEFAULT]\n"
                  "notification_driver = messagingv2\n")
        util.write_config(configfile, config)
