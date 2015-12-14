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
from clearstack.controller import Controller
from clearstack.common import util


def init_config():
    conf = {}

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    conf = controller.CONF
    if util.str2bool(conf['CONFIG_HORIZON_INSTALL']):
        controller.add_sequence("Setting up horizon", setup_horizon)


def setup_horizon():
    template = "horizon"
    conf = Controller.get().CONF
    recipe = utils.get_template(template)
    return utils.run_recipe("{0}.py".format(template), recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])
