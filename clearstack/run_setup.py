#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
# Author: Julio Montes <julio.montes@intel.com>
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

import re
import os

from importlib import import_module

from clearstack import utils
from clearstack.controller import Controller
from clearstack.common.util import LOG


def load_plugins():
    """ return if plugins already are loaded """
    if Controller.get().get_all_plugins():
        return

    path = "plugins"
    base_module = "clearstack.{0}".format(path)
    directory = "{0}/{1}".format(os.path.dirname(
        os.path.realpath(__file__)), path)
    rx_val = r'^[a-zA-Z]+_[0-9]{3}\.py$'
    files = [fd for fd in os.listdir(directory) if re.match(rx_val, fd)]
    for fd in sorted(files, key=_get_weight):
        plugin = import_module("{0}.{1}".format(base_module, fd.split(".")[0]))
        Controller.get().add_plugin(plugin)
        try:
            getattr(plugin, "init_config")()
        except AttributeError:
            LOG.debug("missing attribute: init_config in %s",
                      plugin.__file__)


def add_arguments(parser):
    load_plugins()
    for group in Controller.get().get_all_groups():
        for argument in group.get_all_arguments():
            parser.add_argument("--{0}".format(argument.cmd_option),
                                action="store",
                                dest=argument.conf_name,
                                help=argument.description,
                                choices=argument.option_list)


def load_sequences():
    load_plugins()
    for plugin in Controller.get().get_all_plugins():
        try:
            getattr(plugin, "init_sequences")()
        except AttributeError:
            LOG.debug("missing attribute: init_sequences in %s",
                      plugin.__file__)


def run_all_sequences():
    load_sequences()

    try:
        utils.copy_resources()
    except Exception as e:
        raise e

    try:
        Controller.get().run_all_sequences()
    except Exception as e:
        raise e
    finally:
        utils.get_logs()


def generate_admin_openrc():
    conf = Controller.get().CONF
    home = os.getenv('HOME')
    with open("{0}/admin-openrc.sh".format(home), "w") as f:
        f.write('export OS_PROJECT_DOMAIN_ID=default\n')
        f.write('export OS_USER_DOMAIN_ID=default\n')
        f.write('export OS_PROJECT_NAME=admin\n')
        f.write('export OS_USERNAME="admin"\n')
        f.write('export OS_TENANT_NAME="admin"\n')
        f.write('export OS_AUTH_URL=http://{0}:35357/v3\n'
                .format(conf['CONFIG_CONTROLLER_HOST']))
        f.write('export OS_REGION_NAME="{0}"\n'
                .format(conf['CONFIG_KEYSTONE_REGION']))
        f.write('export OS_PASSWORD={0}\n'
                .format(conf['CONFIG_KEYSTONE_ADMIN_PW']))
        f.write('export OS_IDENTITY_API_VERSION=3\n')


def _get_weight(item):
    tmp = item.split('_')[-1]
    tmp = tmp.split('.')[0]
    return tmp
