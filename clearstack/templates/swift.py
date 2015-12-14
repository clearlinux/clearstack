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
from modules.conf import CONF
from modules.swift import Swift


swift = Swift.get()
config_file = "/etc/swift/proxy-server.conf"

swift.install()
swift.create_user()
swift.create_service()
swift.create_endpoint()

swift.config_auth(config_file)
swift.config_memcache(config_file)
swift.config_hash('/etc/swift/swift.conf')

# Storage configuration
swift.parse_devices()
swift.prepare_devices()
swift.create_rings()
swift.config_rsync()
swift.config_storage_services()

if util.str2bool(CONF['CONFIG_CEILOMETER_INSTALL']):
    swift.ceilometer_enable(config_file)

util.run_command("systemctl restart update-triggers.target")

# Start controller services
swift.start_server()

# Start storage node services
services = ['rsyncd', 'swift-account', 'swift-account-auditor',
            'swift-account-reaper', 'swift-account-replicator',
            'swift-container', 'swift-container-auditor',
            'swift-container-replicator', 'swift-container-updater',
            'swift-object', 'swift-object-auditor',
            'swift-object-replicator', 'swift-object-updater']
swift.start_server(services)
