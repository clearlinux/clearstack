#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
# Author: Julio Montes <julio.montes@intel.com>
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

import os

from modules.openstack import OpenStackService
from modules.conf import CONF
from common import util
from common.util import LOG
from common.singleton import Singleton


@Singleton
class Glance(OpenStackService):
    _name = "glance"
    _bundle = "openstack-image"
    _services = ["glance-api", "glance-registry"]
    _type = "image"
    _description = "OpenStack Image"
    _public_url = "http://{0}:9292".format(CONF['CONFIG_CONTROLLER_HOST'])

    def sync_database(self):
        LOG.debug("populating glance database")
        util.run_command("su -s /bin/sh -c"
                         " \"glance-manage db_sync\" glance")

    def create_image(self, name, format, url, public=False):
        try:
            LOG.debug("checking if image '{0}' exists".format(name))
            util.run_command("openstack image show %s" % name,
                             environ=self._env)
        except:
            LOG.debug("creating image '{0}'".format(name))
            command = ("openstack image create --disk-format %s %s"
                       % (format, name))
            if os.path.isfile(url):
                command += " --file %s" % url
            else:
                command += " --location %s" % url
            if public:
                command += " --public"
            util.run_command(command, environ=self._env)

    def ceilometer_enable(self, configfile):
        LOG.debug("setting up rabbitmq configuration"
                  " in '{0}'".format(configfile))
        self.config_rabbitmq(configfile)
        config = ("[DEFAULT]\n"
                  "notification_driver = messagingv2\n")
        util.write_config(configfile, config)
