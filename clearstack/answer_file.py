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

import os

import configparser

from clearstack.controller import Controller
from clearstack.common.util import LOG
from clearstack.common.singleton import Singleton


@Singleton
class AnswerFile:
    def generate(self, file, variables_cmd):
        with open(file, "w") as f:
            f.write("[general]\n\n")
            for group in Controller.get().get_all_groups():
                for argument in group.get_all_arguments():
                    f.write("# {0}\n".format(argument.description))
                    value = variables_cmd.get(argument.conf_name,
                                              argument.default_value)
                    f.write("{0}={1}\n\n".format(argument.conf_name, value))

    def read(self, file, variables_cmd):
        conf = Controller.get().CONF
        config = configparser.RawConfigParser()
        config.optionxform = str
        if not os.path.isfile(file):
            raise IOError("file {0} not found".format(file))

        """ Validate option in answer file"""
        config.read(file)
        if not config.has_section('general'):
            raise KeyError("answer file {0} doesn't have general"
                           " section".format(file))
        conf_file = dict(config['general'])
        conf_file.update(variables_cmd)  # override variables
        conf.update(conf_file)

        try:
            Controller.get().validate_groups(conf_file)
        except Exception as e:
            raise e

        all_args = Controller.get().get_all_arguments()
        for non_supported in (set(conf_file) - set(all_args)):
            LOG.warn("clearstack: variable {0} is not"
                     " supported yet".format(non_supported))
