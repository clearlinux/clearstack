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

from clearstack import utils
from clearstack import validators
from clearstack.controller import Controller
from clearstack.argument import Argument
from clearstack.common import util


def init_config():
    conf = {
        "NEUTRON": [
            Argument("neutron-ks-pw",
                     "Password to use for OpenStack Networking (neutron) to"
                     " authenticate with the Identity service.",
                     "CONFIG_NEUTRON_KS_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("neutron-db-pw",
                     "The password to use for OpenStack Networking to access "
                     "the database.",
                     "CONFIG_NEUTRON_DB_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            # Argument('neutron-l3-ext-bridge',
            #          'The name of the Open vSwitch bridge (or empty for '
            #          'linuxbridge) for the OpenStack Networking L3 agent to '
            #          'use for external traffic',
            #          'CONFIG_NEUTRON_L3_EXT_BRIDGE',
            #          'br-ex',
            #          validators=[validators.not_empty]),
            Argument('neutron-metadata-pw',
                     'Password for the OpenStack Networking metadata agent',
                     'CONFIG_NEUTRON_METADATA_PW',
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument('neutron-lbaas-install',
                     "Specify 'y' to install OpenStack Networking's "
                     "Load-Balancing-as-a-Service (LBaaS)",
                     "CONFIG_LBAAS_INSTALL",
                     'n',
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument('neutron-vpnass-install',
                     "Specify 'y' to install OpenStack Networking's "
                     "VPN-as-a-Service (VPNaaS)",
                     "CONFIG_VPNAAS_INSTALL",
                     'n',
                     options=['y', 'n'],
                     validators=[validators.y_or_n])
        ],
        # "NEUTRON_OVS_AGENT": [
        #     Argument("neutron-ovs-bridge-mappings",
        #              "Comma-separated list of bridge mappings for the "
        #              "OpenStack Networking Open vSwitch plugin. Each tuple "
        #              "in the list must be in he format "
        #              " <physical_network>:<ovs_bridge>",
        #              "CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS",
        #              "external:br-ex"),
        #     Argument("neutron-ovs-bridge-interfaces",
        #              "Comma-separated list of colon-separated Open vSwitch"
        #              " <bridge>:<interface> pairs.",
        #              "CONFIG_NEUTRON_OVS_BRIDGE_IFACES",
        #              "br-ex:%s" % util.get_net_interface())
        # ],
        "NEUTRON_LINUXBRIDGE_AGENT": [
            Argument("neutron-linuxbridge-physical-interface-mappings",
                     "Colon separated linuxbridge <bridge>:<interface> pairs",
                     "CONFIG_NEUTRON_LINUXBRIDGE_IFACES",
                     "public:%s" % util.get_net_interface())
        ],
        "NEUTRON_ML2_PLUGIN": [
            Argument("neutron-ml2-type-drivers",
                     "Comma-separated list of network-type driver entry "
                     "points to be loaded from the neutron.ml2.type_drivers "
                     "namespace",
                     "CONFIG_NEUTRON_ML2_TYPE_DRIVERS",
                     "flat,vlan,vxlan",
                     options=['local', 'flat', 'vlan', 'gre', 'vxlan'],
                     validators=[validators.not_empty]),
            Argument("neutron-ml2-tenant-network-types",
                     "Comma-separated, ordered list of network types to "
                     "allocate as tenant networks",
                     "CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES",
                     "vxlan",
                     options=['local', 'vlan', 'gre', 'vxlan'],
                     validators=[validators.not_empty]),
            Argument("neutron-ml2-mechanism-drivers",
                     "Comma-separated, ordered list of network types to "
                     "allocate as tenant networks",
                     "CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS",
                     "linuxbridge,l2population",
                     options=['openvswitch', 'linuxbridge'],
                     validators=[validators.not_empty]),
            Argument("neutron-ml2-flat-networks",
                     "Comma-separated list of physical_network names with "
                     "wich flat networks can be created.",
                     "CONFIG_NEUTRON_ML2_FLAT_NETWORKS",
                     "public",
                     validators=[validators.not_empty]),
            Argument("neutron-ml2-tunnel-id-ranges",
                     "Comma-separated list of <tun_min>:<tun_max> tuples "
                     "enumerating ranges of GRE tunnel IDs that are available "
                     "for tenant-network allocation.",
                     "CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES",
                     "1:1000",
                     validators=[validators.not_empty]),
            Argument("neutron-l2-agent",
                     "Name of the L2 agent to be used with OpenStack "
                     "Networking",
                     "CONFIG_NEUTRON_L2_AGENT",
                     "linuxbridge",
                     options=['openvswitch', 'linuxbridge'],
                     validators=[validators.not_empty])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    conf = controller.CONF
    if util.str2bool(conf['CONFIG_NEUTRON_INSTALL']):
        controller.add_sequence("Setting up neutron controller",
                                setup_controller)
        controller.add_sequence("Setting up neutron on computes nodes",
                                setup_compute_nodes)


def setup_controller():
    conf = Controller.get().CONF
    recipe = utils.get_template('neutron')
    return utils.run_recipe("neutron.py", recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])


def setup_compute_nodes():
    conf = Controller.get().CONF
    recipe = utils.get_template('neutron_compute')
    return utils.run_recipe("neutron_compute.py", recipe,
                            conf["CONFIG_COMPUTE_HOSTS"].split(','))
