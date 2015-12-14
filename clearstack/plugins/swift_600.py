#
# Copyright (c) 2015 Intel Corporation
#
# Author: Alberto Murillo <alberto.murillo.silva@intel.com>
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
import stat

from clearstack import utils
from clearstack import validators
from clearstack.controller import Controller
from clearstack.argument import Argument
from clearstack.common import util


def init_config():
    conf = {
        "SWIFT": [
            Argument("swift-ks-pw",
                     "Password to use for the Object Storage service to "
                     " authenticate with with the Identity service",
                     "CONFIG_SWIFT_KS_PW",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("swift-storages",
                     "Comma-separated list of devices to use as storage device"
                     " for Object Storage. e.g. /path/to/dev1,/path/to/dev2."
                     " Clearstack DOES NOT creare the file system, you must "
                     "format it with xfs. Leave blank to use a loop device",
                     "CONFIG_SWIFT_STORAGES",
                     '',
                     validators=[validate_storage]),
            Argument("swift-storage-zones",
                     "Number of Object Storage storage zones; this number "
                     "MUST be no larger than the number of configured "
                     "storage devices.",
                     "CONFIG_SWIFT_STORAGE_ZONES",
                     '1',
                     validators=[validators.digit]),
            Argument("swift-storage-replicas",
                     "Number of Object Storage storage replicas; this number "
                     "MUST be no larger than the number of configured "
                     "storage zones.",
                     "CONFIG_SWIFT_STORAGE_REPLICAS",
                     '1',
                     validators=[validators.digit]),
            Argument("swift-hash",
                     "Custom seed number to use for swift_hash_path_suffix in"
                     " /etc/swift/swift.conf. If you do not provide a value, "
                     "a seed number is automatically generated.",
                     "CONFIG_SWIFT_HASH",
                     utils.generate_random_pw(),
                     validators=[validators.not_empty]),
            Argument("swift-storage-size",
                     "Size of the Object Storage loopback file storage "
                     "device in GB",
                     "CONFIG_SWIFT_STORAGE_SIZE",
                     "2",
                     validators=[validators.digit]),
        ]
    }

    for group in conf:
        Controller.get().add_group(group, conf[group])


def init_sequences():
    controller = Controller.get()
    conf = controller.CONF
    if util.str2bool(conf['CONFIG_SWIFT_INSTALL']):
        controller.add_sequence("Setting up swift", setup_swift)


def setup_swift():
    conf = Controller.get().CONF
    recipe = utils.get_template("swift")
    return utils.run_recipe("swift.py", recipe,
                            [conf["CONFIG_CONTROLLER_HOST"]])


def validate_storage(value):
    if not value:
        return
    devices = value.split(',')
    for device in devices:
        mode = os.stat(device).st_mode
        if not stat.S_ISBLK(mode):
            raise ValueError("%s is not a block device" % device)
