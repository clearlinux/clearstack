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
import sys

from common import util
from common.singleton import Singleton
from common.swupd import Client as swupd_client
from common.util import LOG


@Singleton
class Rabbitmq:
    def __init__(self):
        hostname, stderr = util.run_command("hostname")
        util.write_in_file_ine("/etc/hosts", "127.0.0.1 {0}"
                               .format(str(hostname.decode("utf-8")[:-1])))

    def user_exists(self, user):
        stdout = None
        stderr = None
        try:
            LOG.debug("Checking if rabbitmq user '{0}' exists".format(user))
            stdout, stderr = util.run_command("rabbitmqctl list_users"
                                              " | grep {0}".format(user))
        except:
            pass

        if not stdout:
            LOG.debug("rabbitmq user '{0}' does not exists".format(user))
            return False

        LOG.debug("rabbitmq user '{0}' does exists".format(user))
        return True

    def install(self):
        swupd_client.install("message-broker-rabbitmq")

    def enable_server(self):
        enabled = util.service_enabled("rabbitmq-server.service")
        if not enabled:
            util.run_command("systemctl enable rabbitmq-server")

    def start_server(self):
        LOG.debug("enabling rabbitmq-server service")
        self.enable_server()
        status = util.service_status("rabbitmq-server.service")
        LOG.debug("rabbitmq-server status: " + status)
        if status == "active":
            LOG.debug("rabbitmq-server service is already running")
            return
        elif status == "inactive" or status == "unknown":
            LOG.debug("starting rabbitmq-server service")
            util.run_command("systemctl restart rabbitmq-server")
        elif status == "failed":
            # try to re-run the service, catch the error if fails again
            try:
                LOG.debug("rabbitmq-server failed to start previously. "
                          "Trying to start service...")
                util.run_command("systemctl restart rabbitmq-server")
            except:
                LOG.debug("rabbitmq-server.service failed to start."
                          "Try 'rm -rf /var/lib/rabbitmq/*' and re-run"
                          "clearstack")
                sys.exit(1)
        else:
            LOG.debug("Error: rabbitmq-server service status"
                      " '{0}' unknown... Exiting clearstack".format(status))
            sys.exit(1)

    def add_user(self, auth_user, auth_pw):
        """ todo: what we do with guest """
        LOG.debug("adding rabbitmq user '{0}'".format(auth_user))
        if not self.user_exists(auth_user):
            util.run_command("rabbitmqctl add_user {0} {1}"
                             .format(auth_user, auth_pw), debug=False)

    def delete_user(self, user):
        LOG.debug("deleting rabbitmq user '{0}'".format(user))
        util.run_command("rabbitmqctl delete_user {1}"
                         .format(user))

    def set_permissions(self, auth_user, permissions):
        LOG.debug("setting rabbitmq permissions for "
                  "user '{0}'".format(auth_user))
        util.run_command("rabbitmqctl set_permissions {0} {1}"
                         .format(auth_user, permissions))
