#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
# Author: Julio Montes <julio.montes@intel.com>
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

import calendar
import configparser
import datetime
import os
import binascii
import time
import shutil

from clearstack import controller
from clearstack.ssh import SshHandler
from clearstack.controller import Controller
from clearstack.common import util


__now = datetime.datetime.now()
__recipes_directory = "/tmp/clearstack-{0}-{1}-{2}-{3}/".format(
    __now.year, __now.month, __now.day, calendar.timegm(time.gmtime()))


def arg(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def run_recipe(recipe_file, recipe_src, hosts):
    recipes_dir = __recipes_directory
    if not os.path.isdir(recipes_dir):
        os.makedirs(recipes_dir)

    if controller.DEBUG and recipe_file.endswith('.py'):
        recipe_src = "from common import util\n" + \
                     "util.setup_debugging(True)\n\n" + \
                     recipe_src

    recipe_file = os.path.join(recipes_dir, recipe_file)
    with open(recipe_file, "w") as f:
        f.write(recipe_src)

    _run_recipe_in_hosts(recipe_file, recipes_dir, hosts)
    return True


def _run_recipe_local(recipe_file):
    if recipe_file.endswith('.py'):
        util.run_command("python3 {0}".format(recipe_file))
    else:
        util.run_command("bash -f {0}".format(recipe_file))


def _run_recipe_in_hosts(recipe_file, recipes_dir, _hosts):
    hosts = set(_hosts)
    ssh = SshHandler.get()

    if util.has_localhost(hosts):
        _run_recipe_local(recipe_file)
        util.remove_localhost(hosts)

    for host in hosts:
        try:
            ssh.transfer_file(recipe_file, recipes_dir, host)
            ssh.run_recipe(recipe_file, host)
        except Exception as e:
            raise e


def get_all_hosts():
    conf = Controller.get().CONF
    hosts = set()
    hosts.update(set(conf["CONFIG_COMPUTE_HOSTS"].split(",")))
    hosts.add(conf["CONFIG_CONTROLLER_HOST"])
    hosts.add(conf["CONFIG_AMQP_HOST"])
    hosts.add(conf["CONFIG_MARIADB_HOST"])
    hosts.add(conf["CONFIG_MONGODB_HOST"])

    return hosts


def generate_conf_file(conf_file):
    """ create defaults.conf file """
    conf = Controller.get().CONF
    config_file = configparser.RawConfigParser()
    config_file.optionxform = str
    dir_name = os.path.dirname(conf_file)

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    config_file.add_section("general")
    for key in conf.keys():
        config_file.set("general", key, '{0}'.format(conf[key]))

    with open(conf_file, 'w') as f:
        config_file.write(f)


def copy_resources():
    _copy_resources_to_hosts(get_all_hosts())
    return True


def _copy_resources_local():
    resources_dir = os.path.dirname(os.path.realpath(__file__))
    modules_src = "{0}/modules".format(resources_dir)
    common_src = "{0}/common".format(resources_dir)

    modules_dst = "{0}/modules".format(__recipes_directory)
    common_dst = "{0}/common".format(__recipes_directory)
    conf_file = "{0}/defaults.conf".format(__recipes_directory)

    generate_conf_file(conf_file)
    shutil.copytree(modules_src, modules_dst)
    shutil.copytree(common_src, common_dst)


def _copy_resources_to_hosts(_hosts):
    try:
        SshHandler.get().test_hosts(_hosts)
    except Exception as e:
        raise e

    hosts = set(_hosts)
    ssh = SshHandler.get()
    resources_dir = os.path.dirname(os.path.realpath(__file__))
    modules_dir = "{0}/modules".format(resources_dir)
    common_dir = "{0}/common".format(resources_dir)
    conf_file = "{0}/defaults.conf".format(__recipes_directory)

    if util.has_localhost(hosts):
        _copy_resources_local()

    util.remove_localhost(hosts)

    if not os.path.isfile(conf_file):
        generate_conf_file(conf_file)

    """ Copy modules and conf to hosts """
    for host in hosts:
        try:
            ssh.transfer_file(modules_dir, __recipes_directory, host)
            ssh.transfer_file(common_dir, __recipes_directory, host)
            ssh.transfer_file(conf_file, __recipes_directory, host)
        except Exception as e:
            raise e

    return True


def get_logs():
    SshHandler.get().get_logs(get_all_hosts())


def get_template(template):
    directory = "{0}/{1}".format(os.path.dirname(
        os.path.realpath(__file__)), "templates")
    if not template.endswith(".sh"):
        template = template + ".py"
    template = os.path.join(directory, template)
    source = "\n{0} {1} {0}\n".format("#" * 5, template)
    with open(template, 'r') as f:
        source += f.read()
        source += "\n{0}\n".format("#" * 60)
        return source

    raise Exception("cannot load {0} template".format(template))


def generate_random_pw():
    return binascii.b2a_hex(os.urandom(10)).decode("utf-8")


def generate_ssh_keys(output):
    util.run_command("ssh-keygen -b 4096 -f {0} -a 500 -N ''"
                     .format(output))


def setup_debugging(debug):
    controller.DEBUG = debug
    util.setup_debugging(debug, is_remote_host=False)
