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

import os
import shutil

from common import util
from commmon.util import LOG
from modules.openstack import OpenStackService
from modules.conf import CONF
from common.singleton import Singleton


@Singleton
class Swift(OpenStackService):
    _name = "swift"
    _bundle = "openstack-object-storage"
    _services = ["swift-proxy", "memcached"]
    _type = "object-store"
    _description = "OpenStack Object Storage"
    _public_url = ("http://{0}:8080/v1/AUTH_%\(tenant_id\)s"
                   .format(CONF['CONFIG_CONTROLLER_HOST']))
    _admin_url = "http://{0}:8080/v1".format(CONF['CONFIG_CONTROLLER_HOST'])

    _devices = []

    def ceilometer_enable(self, configfile):
        pass

    def config_auth(self, configfile):
        confdir = os.path.dirname(configfile)
        if not os.path.isdir(confdir):
            os.makedirs(confdir)
        shutil.copy('/usr/share/defaults/swift/proxy-server.conf', confdir)
        OpenStackService.config_auth(self, configfile,
                                     section='filter:authtoken')
        config = ("[pipeline:main]\n"
                  "pipeline = catch_errors gatekeeper healthcheck "
                  "proxy-logging cache container_sync bulk ratelimit "
                  "authtoken keystoneauth container-quotas account-quotas "
                  "slo dlo versioned_writes proxy-logging proxy-server\n"
                  "[filter:authtoken]\n"
                  "paste.filter_factory = "
                  "keystonemiddleware.auth_token:filter_factory\n"
                  "delay_auth_decision = True\n"
                  "[app:proxy-server]\n"
                  "use = egg:swift#proxy\n"
                  "account_autocreate = True\n"
                  "[filter:keystoneauth]\n"
                  "use = egg:swift#keystoneauth\n"
                  "operator_roles = admin,user\n")
        util.write_config(configfile, config)

    def config_memcache(self, configfile):
        config = ("[filter:cache]\n"
                  "use = egg:swift#memcache\n"
                  "memcache_servers = 127.0.0.1:11211")
        util.write_config(configfile, config)

    def config_hash(self, configfile):
        suffix = CONF['CONFIG_SWIFT_HASH']
        config = ("[swift-hash]\n"
                  "swift_hash_path_suffix = {0}").format(suffix)
        util.write_config(configfile, config)

    def parse_devices(self):

        def create_loopback(name, size):
            # Remove the file if exists
            if os.path.isfile(name):
                os.remove(name)
            # Create an empty file
            with open(name, 'wb') as f:
                f.seek(1024 * 1024 * 1024 * size - 1)
                f.write(b"\0")
            LOG.("formatting '{0}' as XFS".format(name))
            util.run_command("mkfs.xfs %s" % name)

        devs = CONF['CONFIG_SWIFT_STORAGES']
        if devs:
            devs = devs.split(',')
            devs = [x.strip() for x in devs]
            device_number = 0
            num_zones = int(CONF["CONFIG_SWIFT_STORAGE_ZONES"])
            for dev in devs:
                device_number += 1
                zone = (device_number % num_zones) + 1
                self._devices.append({'device': dev, 'zone': zone,
                                      'name': 'device%s' % device_number})
        else:
            # Setup loopdevice
            filename = '/srv/loopback-device'
            filesize = int(CONF['CONFIG_SWIFT_STORAGE_SIZE'])
            create_loopback(filename, filesize)
            self._devices.append({'device': filename, 'zone': 1,
                                  'name': 'loopback'})

    def prepare_devices(self):
        # Avoid adding duplicate entries in fstab
        mounted_devices = []
        if os.path.isfile('/etc/fstab'):
            with open('/etc/fstab', 'r') as f:
                for l in f:
                    mounted_devices.append(l.split()[0].strip())

        # Add each device to fstab if not already added
        fstab = ""
        for device in self._devices:
            # Format the device with xfs filesystem
            util.ensure_directory('/srv/node/%s' % device['name'])

            # Ensure the device is mounted
            if device['device'] not in mounted_devices:
                fstab += ("{0} /srv/node/{1} xfs noatime,nodiratime,nobarrier,"
                          "logbufs=8 0 2\n").format(device['device'],
                                                    device['name'])
        with open('/etc/fstab', 'a') as f:
            f.write(fstab)

        util.run_command('mount -a')
        # Change ownership of /srv to swift
        util.run_command("chown -R swift:swift /srv")

    def create_rings(self):
        replicas = CONF['CONFIG_SWIFT_STORAGE_REPLICAS']
        ip = util.get_ip()
        for ringtype, port in [('object', '6000'),
                               ('container', '6001'),
                               ('account', 6002)]:
            LOG.debug("creating '{0}' ring with {1} "
                      "replicas".format(ringtype, replicas))
            cmd = ("swift-ring-builder {0}.builder create 10 {1} 1"
                   .format(ringtype, replicas))
            util.run_command(cmd)
            for device in self._devices:
                LOG.debug("adding '{0}' storage node on ring "
                          "'{1}'".format(device['name'], ringtype))
                cmd = ("swift-ring-builder %s.builder add --region 1 "
                       "--zone %s --ip %s --port %s --device %s --weight 100"
                       % (ringtype, device['zone'], ip, port, device['name']))
                util.run_command(cmd)
            LOG.debug("rebalancing ring '{0}'".format(ringtype))
            cmd = "swift-ring-builder {0}.builder rebalance".format(ringtype)
            util.run_command(cmd)
            if os.path.isfile("/etc/swift/%s.ring.gz" % ringtype):
                os.remove("/etc/swift/%s.ring.gz" % ringtype)
            shutil.move("%s.ring.gz" % ringtype, "/etc/swift")

    def config_storage_services(self):
        confdir = '/etc/swift/'
        shutil.copy('/usr/share/defaults/swift/account-server.conf', confdir)
        shutil.copy('/usr/share/defaults/swift/container-server.conf', confdir)
        shutil.copy('/usr/share/defaults/swift/object-server.conf', confdir)
        shutil.copy('/usr/share/defaults/swift/container-reconciler.conf',
                    confdir)
        shutil.copy('/usr/share/defaults/swift/object-expirer.conf', confdir)
        for type in ['account', 'container', 'object']:
            conf = ("[DEFAULT]\n"
                    "bind_ip = 0.0.0.0\n"
                    "devices = /srv/node\n"
                    "[pipeline:main]\n"
                    "pipeline = healthcheck recon {0}-server\n"
                    "[filter:recon]\n"
                    "recon_cache_path = /var/cache/swift\n").format(type)
            util.write_config('/etc/swift/%s-server.conf' % type, conf)

    def config_rsync(self):
        config = """
uid = swift
gid = swift
log file = /var/log/rsyncd.log
pid file = /var/run/rsyncd.pid
address = {0}

[account]
max connections = 2
path = /srv/node/
read only = false
lock file = /var/lock/account.lock

[container]
max connections = 2
path = /srv/node/
read only = false
lock file = /var/lock/container.lock

[object]
max connections = 2
path = /srv/node/
read only = false
lock file = /var/lock/object.lock
""".format(util.get_ip())
        with open('/etc/rsyncd.conf', 'w') as f:
            f.write(config)
