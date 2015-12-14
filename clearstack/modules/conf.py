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

import os
import configparser


_conf_file = "{0}/../defaults.conf".format(os.path.dirname(__file__))
_config = configparser.RawConfigParser()
_config.optionxform = str
_config.read(_conf_file)

CONF = dict(_config['general'])

ENV = {"OS_PROJECT_DOMAIN_ID": "default",
       "OS_USER_DOMAIN_ID": "default",
       "OS_PROJECT_NAME": "admin",
       "OS_USERNAME": "admin",
       "OS_PASSWORD": "{0}".format(CONF['CONFIG_KEYSTONE_ADMIN_PW']),
       "OS_TENANT_NAME": "admin",
       "OS_AUTH_URL": "http://{0}:35357/v3"
       .format(CONF['CONFIG_CONTROLLER_HOST']),
       "OS_IDENTITY_API_VERSION": "3",
       "OS_IMAGE_API_VERSION": "2"}
