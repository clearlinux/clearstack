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

from clearstack import utils
from clearstack import validators
from clearstack.controller import Controller
from clearstack.argument import Argument
from clearstack.common import util


def init_config():
    conf = {
        "NOVA": [
            Argument("nova-db-pw",
                     "Password for nova to access DB",
                     "CONFIG_NOVA_DB_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("nova-ks-pw",
                     "Password to use for the Nova to"
                     " authenticate with Keystone",
                     "CONFIG_NOVA_KS_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    conf = controller.CONF
    if util.str2bool(conf['CONFIG_NOVA_INSTALL']):
        controller.add_sequence("Setting up nova controller",
                                setup_controller)
        controller.add_sequence("Setting up nova computes",
                                setup_computes)


def setup_controller():
    conf = Controller.get().CONF
    recipe = utils.get_template('nova')
    return utils.run_recipe("nova.py", recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])


def setup_computes():
    conf = Controller.get().CONF
    recipe = utils.get_template('nova_compute')
    return utils.run_recipe("nova_compute.py", recipe,
                            conf["CONFIG_COMPUTE_HOSTS"].split(','))
