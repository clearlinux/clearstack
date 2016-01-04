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

"""Command-line interface to configure Clearstack."""

from __future__ import print_function

import argparse
import sys

import clearstack
from clearstack.answer_file import AnswerFile
from clearstack import run_setup
from clearstack import utils
from clearstack.common.util import LOG


class ClearstackConfiguratorShell(object):

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='clearstack',
            description=__doc__.strip(),
            epilog='See "clearstack help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=argparse.HelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h',
                            '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=clearstack.__version__,
                            help="Shows the client version and exits.")

        parser.add_argument('-d',
                            '--debug',
                            action='store_true',
                            help="Enable debug mode in clearstack")

        parser.add_argument('--gen-answer-file',
                            action='store',
                            dest='gen_answer_file',
                            help='Generate an answer file')

        parser.add_argument('--answer-file',
                            action='store',
                            dest='answer_file',
                            help='Read answer file')

        parser.add_argument('--gen-keys',
                            action='store',
                            dest='gen_keys',
                            help='Generate ssh keys')

        return parser

    def main(self, argv):
        self.parser = self.get_base_parser()
        run_setup.add_arguments(self.parser)
        (options, args) = self.parser.parse_known_args(argv)
        utils.setup_debugging(options.debug)

        LOG.debug('Starting clearstack')

        if not argv or options.help:
            self.do_help(options)
            return 0

        if options.gen_keys:
            LOG.debug('generating ssh keys')
            utils.generate_ssh_keys(options.gen_keys)

        # todo: fix
        # if options.allinone:
        #     LOG.debug('testing root access')
        #     if os.geteuid() != 0:
        #         LOG.error("clearstack: error: you need to have root access")
        #         sys.exit(1)

        """ Save user's variables, used to read/write answerfile """
        variables_cmd = {k: v for (k, v) in options.__dict__.items()
                         if v is not None and k.startswith("CONFIG_")}

        ansfile = AnswerFile.get()
        if options.gen_answer_file:
            LOG.debug('generating answer file')
            ansfile.generate(options.gen_answer_file, variables_cmd)

        if options.answer_file:
            try:
                LOG.debug('Reading answer file')
                ansfile.read(options.answer_file, variables_cmd)
                LOG.debug('Running all sequences')
                run_setup.run_all_sequences()
            except Exception as e:
                LOG.error("clearstack: {0}".format(str(e)))
                sys.exit(1)
            LOG.debug('Generating admin-openrc')
            run_setup.generate_admin_openrc()

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help='Display help for <subcommand>.')
    def do_help(self, args):
        self.parser.print_help()


def main():
    try:
        ClearstackConfiguratorShell().main(sys.argv[1:])
    except KeyboardInterrupt:
        print("... terminating clearstack", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
