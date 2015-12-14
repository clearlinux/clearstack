#
# Copyright (c) 2015 Intel Corporation
#
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
import sys
import io

from clearstack import shell as clearstack_shell


def shell(argstr):
    orig = sys.stdout
    clean_env = {}
    _old_env, os.environ = os.environ, clean_env.copy()
    try:
        sys.stdout = io.StringIO()
        _shell = clearstack_shell.ClearstackConfiguratorShell()
        _shell.main(argstr.split())
    except SystemExit:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        assert exc_value, 0
    finally:
        out = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = orig
        os.environ = _old_env
    return out
