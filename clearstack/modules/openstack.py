#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
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

from common import util
from common.swupd import Client as swupd_client
from common.util import LOG
from modules.conf import CONF
from modules.conf import ENV


class OpenStackService:
    _env = ""
    _internal_url = ""
    _admin_url = ""
    _region = ""
    _user = ""
    _controller = CONF["CONFIG_CONTROLLER_HOST"]
    _password = ""

    def __init__(self):
        if not self._env:
            self._env = ENV
        if not self._user:
            self._user = self._name
        if not self._password:
            self._password = CONF['CONFIG_%s_KS_PW' % self._name.upper()]
        if not self._internal_url:
            self._internal_url = self._public_url
        if not self._admin_url:
            self._admin_url = self._public_url
        if not self._region:
            self._region = CONF['CONFIG_KEYSTONE_REGION']

    def install(self, bundle=None):
        bundle = bundle or self._bundle
        swupd_client.install(bundle)

    def start_server(self, services=None):
        services = services or self._services
        LOG.debug("Starting services")
        util.run_command("systemctl enable %s" % " ".join(services))
        for service in services:
            if service.endswith(".socket"):
                util.run_command("systemctl stop %s" %
                                 service.replace(".socket", ".service"))
            util.run_command("systemctl restart %s" % service)

    def create_service(self, name=None, description=None, type=None):
        name = name or self._name
        description = description or self._description
        type = type or self._type
        LOG.debug("setting up %s service" % name)
        try:
            """ test if service already exists """
            util.run_command("openstack service show %s" % name,
                             environ=self._env)
        except:
            util.run_command("openstack service create %s"
                             " --name %s --description \"%s\""
                             % (type, name, description),
                             environ=self._env)

    def create_endpoint(self, publicurl=None,
                        internalurl=None,
                        adminurl=None,
                        region=None,
                        type=None):
        publicurl = publicurl or self._public_url
        internalurl = internalurl or self._internal_url
        adminurl = adminurl or self._admin_url
        region = region or self._region
        type = type or self._type

        LOG.debug("creating endpoint")
        """ test if endpoint already exists """
        out, err = util.run_command("openstack endpoint list | grep %s"
                                    % self._name, environ=self._env)
        if not out:
            cmd = ("openstack endpoint create --region {0} {1}"
                   .format(region, type))
            util.run_command(cmd + " public {0}".format(publicurl),
                             environ=self._env)
            util.run_command(cmd + " internal {0}".format(internalurl),
                             environ=self._env)
            util.run_command(cmd + " admin {0}".format(adminurl),
                             environ=self._env)

    def create_role(self, role):
        LOG.debug("setting up %s role" % role)
        try:
            util.run_command("openstack role show %s" % role,
                             environ=self._env)
        except:
            util.run_command("openstack role create %s" % role,
                             environ=self._env)

    def add_role(self, user, role, project="service", domain="default"):
            # openstack role add: error: argument --project: not allowed with
            # argument --domain
            cmd = "openstack role add --user {0} {1}".format(user, role)
            if domain != "default":
                cmd += " --domain %s" % domain
            else:
                cmd += " --project %s" % project
            util.run_command(cmd, environ=self._env)

    def create_user(self, user=None, password=None, domain="default",
                    project="service", role="admin"):
        user = user or self._user
        password = password or self._password
        LOG.debug("setting up %s user" % user)
        try:
            """ test if user already exists """
            util.run_command("openstack user show %s" % user,
                             environ=self._env)
        except:
            util.run_command("openstack user create --domain {0}"
                             " --password={1}"
                             " --email {2}@example.com {2}"
                             .format(domain, password, user),
                             environ=self._env, debug=False)
            self.add_role(user, role, project, domain)

    def create_domain(self, domain, description):
        LOG.debug("setting up %s domain" % domain)
        try:
            """ test if domain already exists """
            util.run_command("openstack domain show %s" % domain,
                             environ=self._env)
        except:
            util.run_command("openstack domain create --description \"%s\" %s"
                             % (description, domain),
                             environ=self._env, debug=False)

    def config_debug(self, configfile):
        if util.str2bool(CONF['CONFIG_DEBUG_MODE']):
            config = "[DEFAULT]\n" + \
                     "debug=True\n" + \
                     "verbose=True\n"
            util.write_config(configfile, config)

    def config_database(self, configfile):
        dbpass = CONF['CONFIG_%s_DB_PW' % self._name.upper()]
        dbhost = CONF['CONFIG_MARIADB_HOST']
        config = ("[database]\n"
                  "connection=mysql://{0}:{1}@{2}/{0}"
                  .format(self._name, dbpass, dbhost))
        util.write_config(configfile, config)

    def config_rabbitmq(self, configfile):
        rabbit_host = CONF['CONFIG_AMQP_HOST']
        rabbit_password = CONF['CONFIG_AMQP_AUTH_PASSWORD']
        rabbit_user = CONF['CONFIG_AMQP_AUTH_USER']
        config = \
            "[DEFAULT]\n" + \
            "rpc_backend=rabbit\n" + \
            "[oslo_messaging_rabbit]\n" + \
            "rabbit_host=%s\n" % rabbit_host + \
            "rabbit_userid=%s\n" % rabbit_user + \
            "rabbit_password=%s\n" % rabbit_password + \
            "send_single_reply=True"
        util.write_config(configfile, config)

    def config_auth(self, configfile, section='keystone_authtoken'):
        config = ("[{0}]\n"
                  "auth_uri=http://{1}:5000\n"
                  "auth_url=http://{1}:35357\n"
                  "auth_plugin=password\n"
                  "project_domain_id=default\n"
                  "user_domain_id=default\n"
                  "project_name=service\n"
                  "username={2}\n"
                  "password={3}"
                  .format(section, self._controller, self._name,
                          self._password))
        util.write_config(configfile, config)
