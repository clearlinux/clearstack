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

from modules.nova import Nova
from modules.conf import CONF
from common import util


nova = Nova.get()
config_file = "/etc/nova/nova.conf"
my_ip = util.get_ip()

# Install nova controller
nova.install()
nova.create_user()
nova.create_service()
nova.create_endpoint()

# Configure nova controller
nova.config_debug(config_file)
nova.config_database(config_file)
nova.config_rabbitmq(config_file)
nova.config_auth(config_file)

# Setup vncproxy
config = \
    "[DEFAULT]\n" + \
    "my_ip=%s\n" % my_ip + \
    "[vnc]\n" + \
    "vncserver_listen=0.0.0.0\n" + \
    "vncserver_proxyclient_address=%s\n" % my_ip
util.write_config(config_file, config)

# Setup glance host
config = \
    "[glance]\n" + \
    "host=%s\n" % CONF['CONFIG_CONTROLLER_HOST']
util.write_config(config_file, config)

if CONF['CONFIG_HTTP_SERVICE'] == 'nginx':
    util.link_file('/usr/share/nginx/conf.d/nova-api.template',
                   '/etc/nginx/nova-api.conf')
else:
    util.link_file('/usr/share/defaults/httpd/conf.d/nova-api.template',
                   '/etc/httpd/conf.d/nova-api.conf')

util.run_command("systemctl restart update-triggers.target")
nova.sync_database()
nova.start_server()
