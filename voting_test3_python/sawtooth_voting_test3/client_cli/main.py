# Copyright 2016, 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import argparse
import getpass
import logging
import os
import sys
import traceback
import pkg_resources
import binascii

from colorlog import ColoredFormatter

from sawtooth_voting_test3.client_cli.create_batch import add_create_batch_parser
from sawtooth_voting_test3.client_cli.create_batch import do_create_batch

from sawtooth_voting_test3.client_cli.voting_test3_workload import add_workload_parser
from sawtooth_voting_test3.client_cli.voting_test3_workload import do_workload

from sawtooth_voting_test3.client_cli.voting_client import Voting_Test3Client
from sawtooth_voting_test3.client_cli.exceptions import Voting_Test3CliException
from sawtooth_voting_test3.client_cli.exceptions import Voting_Test3ClientException


DISTRIBUTION_NAME = 'sawtooth-voting_test3'


DEFAULT_URL = 'http://127.0.0.1:8008'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    add_init_parser(subparsers, parent_parser)
    add_show_parser(subparsers, parent_parser)
    add_list_parser(subparsers, parent_parser)

    add_create_batch_parser(subparsers, parent_parser)
    add_workload_parser(subparsers, parent_parser)

    return parser


def add_init_parser(subparsers, parent_parser):
    message = 'Sends an voting_test3 transaction to set <name> to <value>.'

    parser = subparsers.add_parser(
        'init',
        parents=[parent_parser],
        description=message,
        help='Sets an voting_test3 value')

    parser.add_argument(
        'name',
        type=str,
        help='file name')

    parser.add_argument(
        '--path',
        type=str,
        help='file path')

    #parser.add_argument(
    #    'value',
    #    type=int,
    #    help='amount to set')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')

    parser.add_argument(
        '--keyfile',
        type=str,
        help="identify file containing user's private key")

    parser.add_argument(
        '--wait',
        nargs='?',
        const=sys.maxsize,
        type=int,
        help='set time, in seconds, to wait for transaction to commit')


def do_init(args):
    if(args.name is not None):
        if(args.path is None):
            fp = open("/home/ksj/test_sawtooth/Voting_Web_backup_20190909/{0}".format(args.name),'rb')
        else:
            fp = open("{0}{1}".format(args.path, args.name),'rb')
            
        dat = fp.read()

        if(args.name == 'CRS.dat'):
            scrs = 0
            fcrs = 1
            while(1):
                now = dat[scrs<<20:fcrs<<20]
                if(len(now) == 0):
                    break
                scrs += 1
                fcrs += 1

                #args.name, args.value, wait = str(binascii.hexlify(now)),scrs, args.wait
                names = args.name + "-{0}".format(scrs)
                print(names)
                args.value, wait = str(binascii.hexlify(now)), args.wait  
                client = _get_client(args)
                response = client.init(names, args.value, wait)
                print(response)
        else:
            args.name, args.value, wait = args.name, str(binascii.hexlify(dat)), args.wait
            client = _get_client(args)
            response = client.init(args.name, args.value, wait)
            print(response)

def add_show_parser(subparsers, parent_parser):
    message = 'Shows the value of the key <name>.'

    parser = subparsers.add_parser(
        'show',
        parents=[parent_parser],
        description=message,
        help='Displays the specified voting_test3 value')

    parser.add_argument(
        'name',
        type=str,
        help='name of key to show')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')


def do_show(args):
    name = args.name
    client = _get_client(args)
    value = client.show(name)
    print('{}: {}'.format(name, value))


def add_list_parser(subparsers, parent_parser):
    message = 'Shows the values of all keys in voting_test3 state.'

    parser = subparsers.add_parser(
        'list',
        parents=[parent_parser],
        description=message,
        help='Displays all voting_test3 values')

    parser.add_argument(
        '--url',
        type=str,
        help='specify URL of REST API')


def do_list(args):
    client = _get_client(args)
    results = client.list()
    for pair in results:
        names, address = pair
        for name in names.items():
            print('{}: {}'.format(name[0], address))


def _get_client(args):
    return Voting_Test3Client(
        url=DEFAULT_URL if args.url is None else args.url,
        keyfile=_get_keyfile(args))


def _get_keyfile(args):
    try:
        if args.keyfile is not None:
            return args.keyfile
    except AttributeError:
        return None

    real_user = getpass.getuser()
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, real_user)


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose
    setup_loggers(verbose_level=verbose_level)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'init':
        do_init(args)
    elif args.command == 'show':
        do_show(args)
    elif args.command == 'list':
        do_list(args)
    elif args.command == 'create_batch':
        do_create_batch(args)
    elif args.command == 'workload':
        do_workload(args)

    else:
        raise Voting_Test3CliException("invalid command: {}".format(args.command))


def main_wrapper():
    # pylint: disable=bare-except
    try:
        main()
    except (Voting_Test3CliException, Voting_Test3ClientException) as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as e:
        raise e
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
