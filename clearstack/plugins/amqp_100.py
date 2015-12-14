#
# Copyright (c) 2015 Intel Corporation
#
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
from clearstack.argument import Argument
from clearstack.controller import Controller
from clearstack.common import util


def init_config():
    conf = {
        "AMQP": [
            Argument("amqp-auth-user",
                     "User for amqp authentication",
                     "CONFIG_AMQP_AUTH_USER",
                     "amqp_user",
                     validators=[validators.not_empty]),
            Argument("amqp-auth-pw",
                     "Password for amqp user authentication",
                     "CONFIG_AMQP_AUTH_PASSWORD",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("amqp-host",
                     "The IP address or hostname of the server on which"
                     " to install the AMQP service",
                     "CONFIG_AMQP_HOST",
                     util.get_ip(),
                     validators=[validators.ip_or_hostname])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    Controller.get().add_sequence("Setting up rabbit", setup_rabbit)


def setup_rabbit():
    conf = Controller.get().CONF
    recipe = utils.get_template("rabbitmq")
    return utils.run_recipe("rabbitmq.py", recipe, [conf["CONFIG_AMQP_HOST"]])
