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

from common.util import LOG
from common import util
from modules.conf import CONF
from modules.mariadb import MariaDB

conf = CONF
mariadb = MariaDB.get()
mariadb_user = CONF["CONFIG_MARIADB_USER"]
mariadb_pw = CONF["CONFIG_MARIADB_PW"]

if util.str2bool(conf['CONFIG_MARIADB_INSTALL']):
    mariadb.install()
    mariadb.configure()
    mariadb.start_server()
    mariadb.secure_installation(mariadb_user, mariadb_pw)

databases = ['keystone', 'glance', 'nova', 'neutron', 'heat']

for database in databases:
    if database == 'keystone' or util.str2bool(conf['CONFIG_%s_INSTALL'
                                               % database.upper()]):
        LOG.info("Setting up mariadb for %s" % database)
        password = CONF['CONFIG_%s_DB_PW' % database.upper()]
        mariadb.setup_database(database, database, password)
