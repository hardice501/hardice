#!/usr/bin/python
#
# Copyright 2017 Intel Corporation
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
import hashlib
import logging
import binascii
import random
import string
import cbor

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

import sawtooth_sdk.protobuf.batch_pb2 as batch_pb2
import sawtooth_sdk.protobuf.transaction_pb2 as transaction_pb2

from sawtooth_voting_test3.processor.handler import make_voting_test3_address

LOGGER = logging.getLogger(__name__)


class Voting_Test3Payload:
    def __init__(self, verb, name, value):
        self._verb = verb
        self._name = name
        self._value = value
        self._cbor = None
        self._sha512 = None

    def to_hash(self):
        return {
            'Verb': self._verb,
            'Name': self._name,
            'Value': self._value
        }

    def to_cbor(self):
        if self._cbor is None:
            self._cbor = cbor.dumps(self.to_hash(), sort_keys=True)
        return self._cbor

    def sha512(self):
        if self._sha512 is None:
            self._sha512 = hashlib.sha512(self.to_cbor()).hexdigest()
        return self._sha512


def create_voting_test3_transaction(verb, name, value, deps, signer):
    payload = Voting_Test3Payload(
        verb=verb, name=name, value=value)

    # The prefix should eventually be looked up from the
    # validator's namespace registry.
    addr = make_voting_test3_address(name)

    header = transaction_pb2.TransactionHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        family_name='voting_test3',
        family_version='1.0',
        inputs=[addr],
        outputs=[addr],
        dependencies=deps,
        payload_sha512=payload.sha512(),
        batcher_public_key=signer.get_public_key().as_hex(),
        nonce=hex(random.randint(0, 2**64)))

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    transaction = transaction_pb2.Transaction(
        header=header_bytes,
        payload=payload.to_cbor(),
        header_signature=signature)

    return transaction


def create_batch(transactions, signer):
    transaction_signatures = [t.header_signature for t in transactions]

    header = batch_pb2.BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=transaction_signatures)

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    batch = batch_pb2.Batch(
        header=header_bytes,
        transactions=transactions,
        header_signature=signature)

    return batch


def generate_word():
    return ''.join([random.choice(string.ascii_letters) for _ in range(0, 6)])


def generate_word_list(count):
    if os.path.isfile('/usr/share/dict/words'):
        with open('/usr/share/dict/words', 'r') as fd:
            return {x.strip(): None for x in fd.readlines()[0:count]}
    else:
        return {generate_word(): None for _ in range(0, count)}


def do_populate(batches, keys):
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    crypto_factory = CryptoFactory(context)
    signer = crypto_factory.new_signer(private_key)

    total_txn_count = 0
    txns = []
    for i in range(0, len(keys)):
        name = list(keys)[i]
        txn = create_voting_test3_transaction(
            verb='init',
            name=name,
            value=random.randint(9000, 100000),
            deps=[],
            signer=signer)
        total_txn_count += 1
        txns.append(txn)
        # Establish the signature of the txn associated with the word
        # so we can create good dependencies later
        keys[name] = txn.header_signature

    batch = create_batch(
        transactions=txns,
        signer=signer)

    batches.append(batch)


def do_generate(args, batches, keys):
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    crypto_factory = CryptoFactory(context)
    signer = crypto_factory.new_signer(private_key)

    start = time.time()
    total_txn_count = 0
    for i in range(0, args.count):
        txns = []
        for _ in range(0, random.randint(1, args.max_batch_size)):
            name = random.choice(list(keys))
            txn = create_voting_test3_transaction(
                verb=random.choice(['inc', 'dec']),
                name=name,
                value=random.randint(1, 10),
                deps=[keys[name]],
                signer=signer)
            total_txn_count += 1
            txns.append(txn)

        batch = create_batch(
            transactions=txns,
            signer=signer)

        batches.append(batch)

        if i % 100 == 0 and i != 0:
            stop = time.time()

            txn_count = 0
            for batch in batches[-100:]:
                txn_count += len(batch.transactions)

            fmt = 'batches {}, batch/sec: {:.2f}, txns: {}, txns/sec: {:.2f}'
            print(fmt.format(
                str(i),
                100 / (stop - start),
                str(total_txn_count),
                txn_count / (stop - start)))
            start = stop


def write_batch_file(args, batches):
    batch_list = batch_pb2.BatchList(batches=batches)
    print("Writing to {}...".format(args.output))
    with open(args.output, "wb") as fd:
        fd.write(batch_list.SerializeToString())


def do_create_batch(args):
    batches = []
    keys = generate_word_list(args.key_count)
    do_populate(batches, keys)
    do_generate(args, batches, keys)
    write_batch_file(args, batches)


def add_create_batch_parser(subparsers, parent_parser):

    epilog = '''
    details:
     create sample batch(es) of voting_test3 transactions.
     populates state with voting_test3 key/value pairs
     then generates batches with inc and dec transactions.
    '''

    parser = subparsers.add_parser(
        'create_batch',
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog)

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='location of output file',
        default='batches.voting_test3',
        metavar='')

    parser.add_argument(
        '-c', '--count',
        type=int,
        help='number of batches modifying random keys',
        default=1,
        metavar='')

    parser.add_argument(
        '-B', '--max-batch-size',
        type=int,
        help='max transactions per batch',
        default=10,
        metavar='')

    parser.add_argument(
        '-K', '--key-count',
        type=int,
        help='number of keys to set initially',
        default=1,
        metavar='')
