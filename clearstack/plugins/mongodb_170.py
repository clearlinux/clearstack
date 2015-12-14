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

from clearstack.controller import Controller
from clearstack.argument import Argument
from clearstack import utils
from clearstack import validators
from clearstack.common import util


def init_config():
    conf = {
        "MONGODB": [
            Argument("mongodb-host",
                     "The IP address or hostname of the MongoDB server",
                     "CONFIG_MONGODB_HOST",
                     util.get_ip(),
                     validators=[validators.ip_or_hostname])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    conf = controller.CONF
    if util.str2bool(conf['CONFIG_CEILOMETER_INSTALL']):
        controller.add_sequence("Setting up MongoDB", setup_mongodb)


def setup_mongodb():
    conf = Controller.get().CONF
    recipe = utils.get_template('mongodb')
    return utils.run_recipe("mongodb.py", recipe,
                            [conf["CONFIG_MONGODB_HOST"]])
