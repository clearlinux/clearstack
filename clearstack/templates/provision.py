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

from modules.glance import Glance
from modules.neutron import Neutron
from modules.nova import Nova
from modules.conf import CONF
from common import util

glance = Glance.get()
nova = Nova.get()
neutron = Neutron.get()

if util.str2bool(CONF['CONFIG_PROVISION_DEMO']):
    name = CONF['CONFIG_PROVISION_IMAGE_NAME']
    format = CONF['CONFIG_PROVISION_IMAGE_FORMAT']
    url = CONF['CONFIG_PROVISION_IMAGE_URL']
    glance.create_image(name, format, url, public=True)
    floating_range = CONF['CONFIG_PROVISION_DEMO_FLOATRANGE']
    neutron.create_network('private', '10.0.0.0/24', public=False)
    neutron.create_network('public', floating_range, public=True)
    neutron.create_router('router', gw='public', interfaces=['private'])
