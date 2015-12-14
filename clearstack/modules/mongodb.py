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

from common import util
from common.singleton import Singleton
from common.swupd import Client as swupd_client
from common.util import LOG


@Singleton
class MongoDB:
    def install(self):
        swupd_client.install("database-mongodb")

    def start_server(self):
        LOG.debug("starting services")
        util.run_command("systemctl enable mongodb")
        util.run_command("systemctl restart mongodb")
        count = 0
        while count < 10:
            try:
                util.run_command("mongo --host 127.0.0.1")
                return
            except:
                util.run_command("sleep 1")
                count += 1
        raise Exception("Failed to start mongodb service")

    def configure(self):
        config_file = "/etc/mongodb/mongod.conf"
        config = {'bind_ip': '0.0.0.0'}
        util.write_properties(config_file, config)

    def setup_database(self, database, user, password):
        cmd = ("mongo --host 127.0.0.1 --eval '"
               "db = db.getSiblingDB(\"%s\");"
               "db.createUser({user: \"%s\",pwd: \"%s\","
               "roles: [ \"readWrite\", \"dbAdmin\" ]})'"
               % (database, user, password))
        util.run_command(cmd)
