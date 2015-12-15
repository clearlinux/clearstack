#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
# Author: Julio Montes <julio.montes@intel.com>
# Author: Obed Munoz <obed.n.munoz@intel.com>
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

from clearstack.argument import Argument
from clearstack.controller import Controller
from clearstack import validators
from clearstack import utils
from clearstack.common import util


def validate_ssh_key(ssh_key):
    hosts = utils.get_all_hosts()
    util.remove_localhost(hosts)
    if len(hosts) != 0:
        validators.file(ssh_key)


def init_config():
    home = os.getenv('HOME')
    if home is None:
        home = "/root"
    conf = {
        "GENERAL": [
            Argument("debug-mode",
                     "Set to 'y' if you want to run"
                     " OpenStack services in debug mode",
                     "CONFIG_DEBUG_MODE",
                     "n",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("ssh-private-key",
                     "Path to the private SSH key file",
                     "CONFIG_PRIVATE_SSH_KEY",
                     "",
                     validators=[validate_ssh_key]),
            Argument("controller-host",
                     "IP address or hostname of the server on which "
                     " to install OpenStack services specific to"
                     " controller role such as API servers",
                     "CONFIG_CONTROLLER_HOST",
                     util.get_ip(),
                     validators=[validators.ip_or_hostname]),
            Argument("clean-controller-host",
                     "Set 'y' if you would like Clearstack to "
                     "clean up controller host",
                     "CONFIG_CLEAN_CONTROLLER_HOST",
                     "y",
                     validators=[validators.y_or_n]),
            Argument("compute-hosts",
                     "List of IP addresses or hostnames of the server on which"
                     " to install the Nova compute service",
                     "CONFIG_COMPUTE_HOSTS",
                     util.get_ip(),
                     validators=[validators.ip_or_hostname]),
            Argument("clean-compute-hosts",
                     "Set 'y' if you would like Clearstack to "
                     "clean up compute hosts",
                     "CONFIG_CLEAN_COMPUTE_HOSTS",
                     "y",
                     validators=[validators.y_or_n]),
            Argument("mariadb-install",
                     "Set 'y' if you would like Clearstack to install MariaDB",
                     "CONFIG_MARIADB_INSTALL",
                     "y",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("mongodb-install",
                     "Set 'y' if you would like Clearstack to install MongoDB",
                     "CONFIG_MONGODB_INSTALL",
                     "y",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("http-service",
                     "Set 'apache2' or 'nginx' as HTTP Service for Horizon, "
                     "Keystone and Nova API web services",
                     "CONFIG_HTTP_SERVICE",
                     "nginx",
                     options=['nginx', 'apache2'],
                     validators=[validators.not_empty]),
            Argument("glance-install ",
                     "Set 'y' if you would like Clearstack to install"
                     " Openstack image (glance)",
                     "CONFIG_GLANCE_INSTALL",
                     "y",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("nova-install ",
                     "Set 'y' if you would like Clearstack to install"
                     " Openstack compute (nova)",
                     "CONFIG_NOVA_INSTALL",
                     "y",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("horizon-install",
                     "Set 'y' if you would like Clearstack to install"
                     " OpenStack dashboard (horizon)",
                     "CONFIG_HORIZON_INSTALL",
                     "y",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("neutron-install",
                     "Set 'y' if you would like Clearstack to install"
                     " OpenStack Networking (neutron)",
                     "CONFIG_NEUTRON_INSTALL",
                     "y",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("ceilometer-install",
                     "Set 'y' if you would like Clearstack to install"
                     " OpenStack Telemetry (ceilometer)",
                     "CONFIG_CEILOMETER_INSTALL",
                     "y",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("heat-install",
                     "Set 'y' if you would like Clearstack to install"
                     " OpenStack Orchestration (heat)",
                     "CONFIG_HEAT_INSTALL",
                     "n",
                     options=['y', 'n'],
                     validators=[validators.y_or_n]),
            Argument("swift-install",
                     "Set 'y' if you would like Clearstack to install"
                     " OpenStack Object Storage (swift)",
                     "CONFIG_SWIFT_INSTALL",
                     "n",
                     options=['y', 'n'],
                     validators=[validators.y_or_n])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    Controller.get().add_sequence("Setting up controller host",
                                  setup_controller)
    Controller.get().add_sequence("Setting up compute hosts",
                                  setup_computes)


def setup_controller():
    conf = Controller.get().CONF
    if util.str2bool(conf['CONFIG_CLEAN_CONTROLLER_HOST']):
        try:
            utils.run_recipe("{0}".format("controller_cleanup.sh"),
                             utils.get_template("controller_cleanup.sh"),
                             [conf["CONFIG_CONTROLLER_HOST"]])
        except:
            pass

    template = "pre_controller.sh"
    recipe = utils.get_template(template)
    return utils.run_recipe("{0}".format(template), recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])


def setup_computes():
    conf = Controller.get().CONF
    if util.str2bool(conf['CONFIG_CLEAN_COMPUTE_HOSTS']):
        try:
            utils.run_recipe("{0}".format("compute_cleanup.sh"),
                             utils.get_template("compute_cleanup.sh"),
                             conf["CONFIG_COMPUTE_HOSTS"].split(','))
        except:
            pass

    template = "pre_compute.sh"
    recipe = utils.get_template(template)
    return utils.run_recipe("{0}".format(template), recipe,
                            conf["CONFIG_COMPUTE_HOSTS"].split(','))
