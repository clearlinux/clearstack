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

import os
import socket
import subprocess
import configparser
import netifaces
import ipaddress
import logging
from errno import EACCES, EPERM, ENOENT

HOST_LOG_DIR = '/var/log/clearstack'
HOST_LOG_FILE = "{0}/clearstack.log".format(HOST_LOG_DIR)
LOG_DIR = '/var/log/clearstack'
if os.geteuid() != 0:
    LOG_DIR = '/tmp/log/clearstack'
LOG_FILE = "{0}/clearstack.log".format(LOG_DIR)
LOG = logging.getLogger("Clearstack")


def _print_error_message(self, e, file_name):
    # PermissionError
    if e.errno == EPERM or e.errno == EACCES:
        print("PermissionError error({0}): {1} for:\n{2}".format(e.errno,
              e.strerror, file_name))
    # FileNotFoundError
    elif e.errno == ENOENT:
        print("FileNotFoundError error({0}): {1} as:\n{2}".format(e.errno,
              e.strerror, file_name))
    elif IOError:
        print("I/O error({0}): {1} as:\n{2}".format(e.errno, e.strerror,
              file_name))
    elif OSError:
        print("OS error({0}): {1} as:\n{2}".format(e.errno, e.strerror,
              file_name))


def port_open(port):
    """Return True if given port is already open in localhost.
       Return False otherwise."""
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return (sck.connect_ex(('127.0.0.1', port)) == 0)


def service_status(service):
    """Return status of a given systemd service."""
    stdout, stderr = run_command("systemctl is-active " + str(service))
    return (stdout.strip().decode("utf-8"))


def setup_debugging(debug, is_remote_host=True):
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    try:
        logging.basicConfig(filename=LOG_FILE,
                            format='%(message)s',
                            level=logging.INFO)
    except (IOError, OSError) as e:
        _print_error_message(e, LOG_FILE)

    ''' paramiko detects all output as error (stderr)'''
    ''' if it is a remote host redirect output to log file '''
    if not is_remote_host:
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        LOG.addHandler(sh)

    if debug:
        LOG.setLevel(logging.DEBUG)


def run_command(command, stdin=None, environ=None, debug=True):
    """Returns (stdout, stderr), raises error on non-zero return code"""
    if environ is None:
        env = None
    else:
        env = os.environ.copy()
        env.update(environ)

    if debug:  # to avoid show passwords
        LOG.debug("command: %s", command)

    proc = subprocess.Popen(['bash', '-c', command],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE, env=env)
    stdout, stderr = proc.communicate()
    if proc.returncode and stderr:
        raise Exception("Error running: {0}\n{1}"
                        .format(command, stderr.decode("utf-8")))

    return stdout, stderr


def str2bool(value):
    return value.lower() in ("yes", "true", "t", "1", "y")


def write_config(file, data):
    directory = os.path.dirname(file)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    config = configparser.RawConfigParser(allow_no_value=True)
    if os.path.isfile(file):
        config.read(file)
    config.read_string(data)
    with open(file, 'w') as f:
        config.write(f)


def write_properties(file, data):
    directory = os.path.dirname(file)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    if os.path.isfile(file):
        with open(file, 'r') as f:
            for l in f.readlines():
                key, value = [x.strip() for x in l.split('=')]
                data[key] = value
    output = ""
    for key, value in data.items():
        output += "%s = %s\n" % (key, value)
    with open(file, 'w') as f:
        f.write(output)


def get_option(file, section, option):
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(file)
    return config[section][option]


def delete_option(file, section, option=None):
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(file)
    if option:
        config.remove_option(section, option)
    else:
        config.remove_section(section)
    with open(file, 'w') as f:
        config.write(f)


# write in file if not exist the line
def write_in_file_ine(file, data):
    with open(file, 'a+') as f:
        f.seek(0)
        if not any(data == x.rstrip('\r\n') for x in f):
            f.write(data + '\n')
            return True
    return False


def get_dns():
    with open('/etc/resolv.conf', 'r') as f:
        return [l.split(' ')[1].strip() for l in f.readlines()
                if l.startswith('nameserver')]


def get_netmask():
    interface = get_net_interface()
    mask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
    return ipaddress.IPv4Network('0.0.0.0/%s' % mask).prefixlen


def get_gateway():
    return netifaces.gateways()['default'][netifaces.AF_INET][0]


def get_net_interface():
    return (netifaces.gateways())['default'][netifaces.AF_INET][1]


def get_ips():
    ips = []
    for iface in netifaces.interfaces():
        try:
            for addr in netifaces.ifaddresses(iface)[netifaces.AF_INET]:
                ips.append(addr['addr'])
        except:
            pass
    return ips


def get_nic(ip):
    for iface in netifaces.interfaces():
        try:
            for addr in netifaces.ifaddresses(iface)[netifaces.AF_INET]:
                if addr['addr'] == ip:
                    return iface
        except:
            pass
    return None


def get_ip():
    interface = get_net_interface()
    return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']


def find_my_ip_from_config(config_ips):
    ip = set(get_ips()) & set(config_ips)
    return ip.pop()


def is_localhost(host):
    return (host == "localhost" or host == socket.gethostname()
            or host in get_ips())


def has_localhost(hosts):
    for host in hosts:
        if is_localhost(host):
            return True
    return False


def remove_localhost(hosts):
    for host in hosts.copy():
        if is_localhost(host):
            hosts.remove(host)


def ensure_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def link_file(source, target):
    dir = os.path.dirname(target)
    ensure_directory(dir)
    if os.path.exists(target):
        os.remove(target)
    os.symlink(source, target)
