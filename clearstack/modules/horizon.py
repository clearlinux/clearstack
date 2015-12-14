#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
# Author: Julio Montes <julio.montes@intel.com>
# Author: Obed Muñoz <obed.n.munoz@intel.com>
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

from modules.openstack import OpenStackService
from modules.conf import CONF
from common.singleton import Singleton


@Singleton
class Horizon(OpenStackService):
    _name = "horizon"
    _bundle = "openstack-dashboard"
    if CONF['CONFIG_HTTP_SERVICE'] == 'nginx':
        _services = ["nginx", "uwsgi@horizon.socket"]
    elif CONF['CONFIG_HTTP_SERVICE'] == 'apache2':
        _services = ["httpd"]
    # These are needed by OpenStackService but not used by horizon
    _type = ""
    _public_url = ""
    _description = ""
    _password = True
