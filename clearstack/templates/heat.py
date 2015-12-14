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

from common import util
from modules.heat import Heat


heat = Heat.get()
config_file = "/etc/heat/heat.conf"

heat.install()
heat.create_user()
heat.create_service(name='heat', description='OpenStack Orchestration',
                    type='orchestration')
heat.create_service(name='heat-cfn', description='OpenStack Orchestration',
                    type='cloudformation')
heat.create_endpoint()
publicurl = "http://%s:8000/v1" % heat._controller
heat.create_endpoint(publicurl=publicurl, internalurl=publicurl,
                     adminurl=publicurl, type='cloudformation')
heat.create_domain(heat.domain_name, 'Stack projects and users')
heat.create_user(user=heat.domain_admin, password=heat.domain_admin_pw,
                 domain=heat.domain_name)
heat.create_role('heat_stack_owner')
heat.create_role('heat_stack_user')

heat.config_database(config_file)
heat.config_rabbitmq(config_file)
heat.config_auth(config_file)
heat.config_domain(config_file)

util.run_command("systemctl restart update-triggers.target")
heat.sync_database()
heat.start_server()
