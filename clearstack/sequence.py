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

from clearstack.common.util import LOG


class Sequence:
    def __init__(self, desc, function, args=None):
        self.description = desc
        self.function = function
        self.function_args = args

    def run(self):
        LOG.info(self.description)
        if self.function_args:
            if not self.function(*self.function_args):
                raise Exception("error running {0}({1})"
                                .format(self.function.__name__,
                                        self.function_args))
        else:
            if not self.function():
                raise Exception("error running {0}"
                                .format(self.function.__name__))
