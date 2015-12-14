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
        "HEAT": [
            Argument("heat-db-pw",
                     "Password for heat to access DB",
                     "CONFIG_HEAT_DB_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("heat-ks-pw",
                     "Password to use for Heat to"
                     " authenticate with Keystone",
                     "CONFIG_HEAT_KS_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("heat-domain",
                     "Name of the Identity domain for Orchestration.",
                     "CONFIG_HEAT_DOMAIN",
                     "heat",
                     validators=[validators.not_empty]),
            Argument("heat-domain-admin",
                     "Name of the Identity domain administrative user for "
                     "Orchestration.",
                     "CONFIG_HEAT_DOMAIN_ADMIN",
                     "heat_domain_admin",
                     validators=[validators.not_empty]),
            Argument("heat-domain-password",
                     "Password for the Identity domain administrative user "
                     "for Orchestration",
                     "CONFIG_HEAT_DOMAIN_PASSWORD",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    conf = controller.CONF
    if util.str2bool(conf['CONFIG_HEAT_INSTALL']):
        controller.add_sequence("Setting up heat", setup_heat)


def setup_heat():
    conf = Controller.get().CONF
    recipe = utils.get_template("heat")
    return utils.run_recipe("heat.py", recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])
