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

import sys

from common import util
from common.singleton import Singleton
from common.swupd import Client as swupd_client
from common.util import LOG
from modules.conf import CONF


@Singleton
class MariaDB:
    def install(self):
        swupd_client.install("database-mariadb")

    def start_server(self):
        LOG.debug("starting services")
        util.run_command("systemctl enable mariadb")
        util.run_command("systemctl restart mariadb")

    def configure(self):
        config_file = "/etc/mariadb/openstack.cnf"
        config = """
        [mysqld]
        default-storage-engine = innodb
        innodb_file_per_table
        collation-server = utf8_general_ci
        init-connect = 'SET NAMES utf8'
        character-set-server = utf8
        bind-address = 0.0.0.0
        """
        util.write_config(config_file, config)

    def secure_installation(self, user, password):
        LOG.debug("secure installation mariadb")
        try:
            """ test if mysql has a password """
            util.run_command("mysql -u{0} -e \"\"".format(user), debug=False)
            """ Secure the database service """
            util.run_command('mysqladmin -u root password "{0}"'
                             .format(password, debug=False))
            util.run_command('mysql -u root -p"{0}" -e "UPDATE mysql.user '
                             'SET Password=PASSWORD(\'{0}\') '
                             'WHERE User=\'root\'"'
                             .format(password, debug=False))
            util.run_command('mysql -u root -p"{0}" -e "DELETE FROM '
                             'mysql.user WHERE User=\'root\' AND Host '
                             ' NOT IN (\'localhost\', \'127.0.0.1\', '
                             '\'::1\')"'
                             .format(password, debug=False))
            util.run_command('mysql -u root -p"{0}" -e "DELETE FROM '
                             'mysql.user WHERE User=\'\'"'
                             .format(password, debug=False))
            util.run_command('mysql -u root -p"{0}" -e "DELETE FROM mysql.db '
                             'WHERE Db=\'test\' OR Db=\'test\_%\'"'
                             .format(password, debug=False))
            util.run_command('mysql -u root -p"{0}" -e '
                             '"FLUSH PRIVILEGES"'
                             .format(password, debug=False))
        except:
            pass

        try:
            """ verify the password """
            util.run_command("mysql -u{0} -p{1} -e \"\""
                             .format(user, password), debug=False)
        except:
            LOG.error("clearstack: cannot connect to mysql database,"
                      " the password is incorrect")
            return sys.exit(1)

    def setup_database(self, database, user, password, host):
        LOG.debug("setting up database")
        mariadb_user = CONF["CONFIG_MARIADB_USER"]
        mariadb_pw = CONF["CONFIG_MARIADB_PW"]
        util.run_command("mysql -u{0} -p{1} -e"
                         " \"CREATE DATABASE if not exists {2};\""
                         .format(mariadb_user, mariadb_pw, database),
                         debug=False)
        util.run_command("mysql -u{0} -p{1} -e"
                         " \"GRANT ALL PRIVILEGES ON {2}.* TO"
                         " '{3}'@'localhost' IDENTIFIED BY '{4}';\""
                         .format(mariadb_user, mariadb_pw, database, user,
                                 password), debug=False)
        util.run_command("mysql -u{0} -p{1} -e"
                         " \"GRANT ALL PRIVILEGES ON {2}.* TO '{3}'@'{4}'"
                         " IDENTIFIED BY '{5}';\""
                         .format(mariadb_user, mariadb_pw, database, user,
                                 host, password), debug=False)
