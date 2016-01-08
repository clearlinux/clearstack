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

from modules import clearlinux
from modules.nova import Nova
from modules.conf import CONF
from common import util


nova = Nova.get()
config_file = "/etc/nova/nova.conf"
services = ['libvirtd.socket', 'nova-compute']
ip_list = CONF['CONFIG_COMPUTE_HOSTS'].split(',')
my_ip = util.find_my_ip_from_config(ip_list)

if CONF['CONFIG_HTTP_SERVICE'] == 'nginx':
    services.extend(['nginx', 'uwsgi@nova-metadata.socket'])
elif CONF['CONFIG_HTTP_SERVICE'] == 'apache2':
    services.append('httpd')
else:
    services.append('nova-api-metadata')

nova.install_compute()
nova.config_debug(config_file)
nova.config_rabbitmq(config_file)
nova.config_auth(config_file)

# Setup vncproxy server
config = ("[DEFAULT]\n"
          "my_ip={0}\n"
          "[vnc]\n"
          "vnc_enabled=True\n"
          "vncserver_listen=0.0.0.0\n"
          "vncserver_proxyclient_address={0}\n"
          "novncproxy_base_url=http://{1}:6080/vnc_auto.html\n"
          .format(my_ip, CONF['CONFIG_CONTROLLER_HOST']))

# Setup glance host
config += ("[glance]\n"
           "host=%s\n") % CONF['CONFIG_CONTROLLER_HOST']

# Disable HW acceleration on unsupported HW
if not clearlinux.support_hw_acceleration():
    config += ("[libvirt]\n"
               "virt_type=qemu\n")

util.write_config(config_file, config)

if util.str2bool(CONF['CONFIG_CEILOMETER_INSTALL']):
    nova.ceilometer_enable(config_file)

util.run_command("systemctl restart update-triggers.target")
nova.start_server(services)
