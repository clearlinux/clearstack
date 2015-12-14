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

from modules.ceilometer import Ceilometer
from common import util


ceilometer = Ceilometer.get()
config_file = "/etc/ceilometer/ceilometer.conf"

ceilometer.install()
ceilometer.create_user()
ceilometer.create_service()
ceilometer.create_endpoint()

ceilometer.config_debug(config_file)
ceilometer.config_database(config_file)
ceilometer.config_rabbitmq(config_file)
ceilometer.config_auth(config_file)
ceilometer.config_service_credentials(config_file)

util.run_command("systemctl restart update-triggers.target")
ceilometer.start_server()
