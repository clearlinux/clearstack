#
# Copyright (c) 2015 Intel Corporation
#
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

import os

import paramiko

from clearstack.controller import Controller
from clearstack.common import util
from clearstack.common.util import LOG
from clearstack.common.singleton import Singleton


@Singleton
class SshHandler(object):
    def __init__(self):
        conf = Controller.get().CONF
        path = os.path.expanduser(
            conf['CONFIG_PRIVATE_SSH_KEY'])
        path = os.path.realpath(path)
        self.ssh_private_key = path
        self.ssh_user = "root"

    def connect(self, user, key_file, host):
        ''' Creates a connection to the host using SSH key '''
        private_key = paramiko.RSAKey.from_private_key_file(key_file)
        connection = paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connection.connect(hostname=host, username=user, pkey=private_key,
                           timeout=1000)
        return connection

    def run_command(self, connection, command):
        try:
            stdin, stdout, stderr = connection.exec_command(command)
            while not stdout.channel.exit_status_ready():
                pass
        except Exception as e:
            raise e

        ''' if stderr is not empty then something fail '''
        error = stderr.read()
        if error:
            raise Exception(error.decode('utf-8'))

        return stdin, stdout, stderr

    def transfer_file(self, file, dest_path, ip):
        try:
            connection = self.connect(self.ssh_user, self.ssh_private_key, ip)
            sftp = connection.open_sftp()
        except paramiko.ssh_exception.SSHException:
            raise Exception("cannot send {0} to {1}, please check"
                            " your ssh connection".format(file, ip))

        if os.path.isdir(file):
            parent_dir = "/".join(file.split('/')[:-1])
            try:
                sftp.mkdir(dest_path)
            except IOError:
                pass
            for dirpath, dirnames, filenames in os.walk(file):
                remote_path = dest_path + dirpath.split(parent_dir)[1]
                try:
                    sftp.mkdir(remote_path)
                except:
                    LOG.info("clearstack: Directory {0} is already created"
                             "in remote host".format(remote_path))
                for filename in filenames:
                    local_path = os.path.join(dirpath, filename)
                    remote_filepath = os.path.join(remote_path, filename)
                    sftp.put(local_path, remote_filepath)
        else:
            filename = file.split('/')[-1]
            sftp.put(file, "{0}/{1}".format(dest_path, filename))

        connection.close()

    def test_python_in_host(self, host, connection):
        try:
            stdin, stdout, stderr = self.run_command(connection,
                                                     'python3 --version')
        except:
            raise Exception("cannot run python3 in {0},"
                            " please install python3".format(host))

    def test_hosts(self, _hosts):
        hosts = set(_hosts)
        connection = None
        conf = Controller.get().CONF

        util.remove_localhost(hosts)

        if not conf['CONFIG_PRIVATE_SSH_KEY'] and hosts:
            raise Exception("CONFIG_PRIVATE_SSH_KEY: missing private key")

        for host in hosts:
            try:
                connection = self.connect(self.ssh_user, self.ssh_private_key,
                                          host)
                self.test_python_in_host(host, connection)
            except Exception as e:
                raise Exception("host {0}: {1}".format(host, str(e)))
            finally:
                if connection:
                    connection.close()

    def run_recipe(self, recipe_file, host):
        connection = None
        interpreter = "python3"
        if recipe_file.endswith('.sh'):
            interpreter = "bash -f"

        try:
            connection = self.connect(self.ssh_user, self.ssh_private_key,
                                      host)
            cmd = "source /root/.bashrc 2> /dev/null;" \
                  "source /usr/share/defaults/etc/profile 2> /dev/null;" \
                  "{0} {1}".format(interpreter, recipe_file)
            stdin, stdout, stderr = self.run_command(connection, cmd)
        except Exception as e:
            LOG.error("clearstack: an error has occurred in {0},"
                      " please check logs for more information"
                      .format(host))
            raise e
        finally:
            if connection:
                connection.close()

    def get_logs(self, _hosts):
        hosts = set(_hosts)
        basename = os.path.splitext(util.LOG_FILE)[0]
        connection = None

        util.remove_localhost(hosts)

        for host in hosts:
            new_name = "{0}-{1}.log".format(basename, host)
            try:
                connection = self.connect(self.ssh_user, self.ssh_private_key,
                                          host)
                sftp = connection.open_sftp()
                sftp.get(util.HOST_LOG_FILE, new_name)
            except:
                LOG.warning("clearstack: cannot get log file from {0}".format(
                    host))
            finally:
                if connection:
                    connection.close()
