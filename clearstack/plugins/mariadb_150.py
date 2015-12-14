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

from clearstack.controller import Controller
from clearstack.argument import Argument
from clearstack import utils
from clearstack import validators
from clearstack.common import util


def init_config():
    conf = {
        "MARIADB": [
            Argument("mariadb-host",
                     "The IP address or hostname of the MariaDB server",
                     "CONFIG_MARIADB_HOST",
                     util.get_ip(),
                     validators=[validators.ip_or_hostname]),
            Argument("mariadb-user",
                     "User for mariadb authentication",
                     "CONFIG_MARIADB_USER",
                     "root",
                     validators=[validators.not_empty]),
            Argument("mariadb-pw",
                     "Password for mariadb user",
                     "CONFIG_MARIADB_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    controller.add_sequence("Setting up mariadb",
                            setup_mariadb, args=['mariadb'])


def setup_mariadb(template):
    conf = Controller.get().CONF
    recipe = utils.get_template(template)
    return utils.run_recipe("{0}.py".format(template), recipe,
                            [conf["CONFIG_MARIADB_HOST"]])
