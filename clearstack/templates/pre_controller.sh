#!/bin/bash
#
# Copyright (c) 2015 Intel Corporation
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

if [ -f /bin/swupd ];then
  if [ ! -f /usr/share/clear/bundles/openstack-configure ];then
    swupd bundle-add openstack-configure
  fi

  if [ ! -f /usr/share/clear/bundles/openstack-python-clients -a ! -f /usr/share/clear/bundles/openstack-all-in-one ];then
    swupd bundle-add openstack-python-clients
  fi
elif [ -f /bin/clr_bundle_add];then
  if [ ! -f /usr/share/clear/bundles/openstack-configure ];then
    clr_bundle_add openstack-configure
  fi

  if [ ! -f /usr/share/clear/bundles/openstack-python-clients -a ! -f /usr/share/clear/bundles/openstack-all-in-one ];then
    clr_bundle_add openstack-python-clients
  fi
fi
