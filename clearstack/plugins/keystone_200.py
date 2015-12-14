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

import uuid

from clearstack.controller import Controller
from clearstack.argument import Argument
from clearstack import utils
from clearstack import validators


def init_config():
    conf = {
        "KEYSTONE": [
            Argument("keystone-db-pw",
                     "Password for keystone to access DB",
                     "CONFIG_KEYSTONE_DB_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("keystone-admin-token",
                     "The token to use for the Keystone service api",
                     "CONFIG_KEYSTONE_ADMIN_TOKEN",
                     uuid.uuid4().hex,
                     validators=[validators.not_empty]),
            Argument("keystone-admin-pw",
                     "The password to use for the Keystone admin user",
                     "CONFIG_KEYSTONE_ADMIN_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("keystone-demo-pw",
                     "The password to use for the Keystone demo user",
                     "CONFIG_KEYSTONE_DEMO_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("keystone-region",
                     "Region name",
                     "CONFIG_KEYSTONE_REGION",
                     "RegionOne",
                     validators=[validators.not_empty])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    Controller.get().add_sequence("Setting up keystone", setup_keystone)


def setup_keystone():
    conf = Controller.get().CONF
    recipe = utils.get_template('keystone')
    return utils.run_recipe("keystone.py", recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])
