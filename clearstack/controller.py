#
# Copyright (c) 2015 Intel Corporation
#
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

from clearstack.group import Group
from clearstack.sequence import Sequence
from clearstack.common.singleton import Singleton

DEBUG = False


@Singleton
class Controller:
    CONF = {}
    _plugins = []
    _groups = []
    _sequences = []

    def add_sequence(self, desc, function, args=None):
        self._sequences.append(Sequence(desc, function, args))

    def run_all_sequences(self):
        for seq in self._sequences:
            try:
                seq.run()
            except Exception as e:
                raise e

    def add_plugin(self, plugin):
        self._plugins.append(plugin)

    def get_all_plugins(self):
        return self._plugins

    def add_group(self, name, args):
        self._groups.append(Group(name, args))

    def get_all_groups(self):
        return self._groups

    def get_all_arguments(self):
        """Get a list of the configuration argument loaded"""
        arguments = []
        for group in self._groups:
            arguments.extend([argument.conf_name
                              for argument in group.get_all_arguments()])
        return arguments

    def remove_argument(self, group_name, conf_name):
        for group in self._groups:
            if group.group_name == group_name:
                for arg in group.arguments:
                    if arg.conf_name == conf_name:
                        group.arguments.remove(arg)
                        return True
        return False

    def remove_validators(self, conf_names):
        for group in self._groups:
            for arg in group.arguments:
                if arg.conf_name in conf_names:
                    arg.validators.clear()

    def validate_groups(self, conf_values):
        """ Load validation functions, in order to check
        the values in the answer file """
        arguments = {}
        for group in self._groups:
            for arg in group.get_all_arguments():
                try:
                    arg.validate(conf_values[arg.conf_name])
                except Exception as e:
                    raise Exception("{0}: {1}".format(arg.conf_name, str(e)))
        return arguments
