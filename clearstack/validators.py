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

import ipaddress
import os
import socket


def y_or_n(value):
    if not value.lower() in ("n", "y"):
        raise ValueError("please set 'y' or 'n'")


def ip_or_hostname(value):
    for v in value.split(","):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            socket.gethostbyname(v)


def cidr(value):
    ip = ipaddress.ip_network(value)
    if not ip:
        raise ValueError("Invalid cidr")


def file(value):
    value = os.path.expanduser(value)
    if not os.path.exists(value):
        raise ValueError("file {0} not found".format(value))


def not_empty(value):
    if not value.strip():
        raise ValueError("empty value")


def digit(value):
    if not value.isdigit():
        raise ValueError("{0} is not a digit".format(value))
