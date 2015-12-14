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


class Argument(object):
    def __init__(self, cmd_option, description,
                 conf_name, default_value, validators=[],
                 options=None):
        self.cmd_option = cmd_option
        self.description = description
        self.conf_name = conf_name
        self.default_value = default_value
        self.validators = validators
        self.option_list = options

    def validate(self, option):
        for validator in self.validators:
            try:
                validator(option)
            except ValueError as e:
                raise ValueError("{0}: {1}".format(self.conf_name, str(e)))
