#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
# Author: Julio Montes <julio.montes@intel.com>
# Author: Obed Munoz <obed.n.munoz@intel.com>
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
from common import util
from common.util import LOG
from common.singleton import Singleton


@Singleton
class Keystone(OpenStackService):
    _name = "keystone"
    _bundle = "openstack-identity"
    if CONF['CONFIG_HTTP_SERVICE'] == 'nginx':
        _services = ["memcached", "nginx", "uwsgi@keystone-admin.socket",
                     "uwsgi@keystone-public.socket"]
    elif CONF['CONFIG_HTTP_SERVICE'] == 'apache2':
        _services = ["memcached", "httpd"]
    else:
        _services = ["keystone"]
    _type = "identity"
    _description = "OpenStack Identity"
    _user = "admin"
    _password = CONF['CONFIG_KEYSTONE_ADMIN_PW']
    _public_url = "http://%s:5000/v3" % CONF['CONFIG_CONTROLLER_HOST']
    _internal_url = _public_url
    _admin_url = "http://%s:35357/v3" % CONF['CONFIG_CONTROLLER_HOST']
    _env = {"OS_TOKEN": CONF['CONFIG_KEYSTONE_ADMIN_TOKEN'],
            "OS_URL": "http://{0}:35357/v3"
            .format(CONF['CONFIG_CONTROLLER_HOST']),
            "OS_IDENTITY_API_VERSION": "3"}

    def sync_database(self):
        LOG.debug("syncing database")
        util.run_command("su -s /bin/sh -c"
                         " \"keystone-manage db_sync\" keystone")

    def create_project(self, project, description):
        LOG.debug("setting up %s project" % project)
        try:
            """ test if project already exists """
            util.run_command("openstack project show %s" % project,
                             environ=self._env)
        except:
            util.run_command("openstack project create --domain default"
                             " --description \"%s\" %s"
                             % (description, project), environ=self._env)

    def config_admin_token(self, configfile):
        config = \
            "[DEFAULT]\n" + \
            "admin_token=%s\n" % CONF['CONFIG_KEYSTONE_ADMIN_TOKEN']
        util.write_config(configfile, config)
