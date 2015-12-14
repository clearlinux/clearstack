#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
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

from clearstack import utils
from clearstack import validators
from clearstack.controller import Controller
from clearstack.argument import Argument
from clearstack.common import util


def init_config():
    conf = {
        "PROVISION_INIT": [
            Argument("provision-demo",
                     "Specify 'y' to provision for demo usage and testing."
                     " ['y', 'n']",
                     "CONFIG_PROVISION_DEMO",
                     "n",
                     options=['y', 'n'],
                     validators=[validators.y_or_n])
        ],
        "PROVISION_DEMO": [
            Argument("provision-demo-floatrange",
                     "CIDR network address for the floating IP subnet.",
                     "CONFIG_PROVISION_DEMO_FLOATRANGE",
                     "172.24.4.224/28",
                     validators=[validators.cidr]),
            Argument("privision-image-format",
                     'Format for the demo image (default "qcow2").',
                     "CONFIG_PROVISION_IMAGE_FORMAT",
                     "qcow2",
                     validators=[validators.not_empty]),
            Argument("provision-image-name",
                     'The name to be assigned to the demo image in Glance '
                     '(default "cirros")',
                     "CONFIG_PROVISION_IMAGE_NAME",
                     "cirros",
                     validators=[validators.not_empty]),
            Argument("provision-image-url",
                     'A URL or local file location for an image to download'
                     'and provision in Glance (defaults to a URL for a '
                     'recent "cirros" image).',
                     "CONFIG_PROVISION_IMAGE_URL",
                     'http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-'
                     'x86_64-disk.img',
                     validators=[validators.not_empty])
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    conf = controller.CONF
    if util.str2bool(conf['CONFIG_PROVISION_DEMO']):
        controller.add_sequence("Running provisioning",
                                setup_controller)


def setup_controller():
    conf = Controller.get().CONF
    templates = ['provision']
    recipe = ""
    for template in templates:
        recipe += utils.get_template(template)

    return utils.run_recipe("provision.py", recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])
