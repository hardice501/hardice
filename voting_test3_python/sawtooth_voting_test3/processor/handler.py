# Copyright 2016 Intel Corporation
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

import logging
import hashlib

import cbor


from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError


LOGGER = logging.getLogger(__name__)

VALID_VERBS = 'init'

MIN_VALUE = 0
MAX_VALUE = 4294967295
MAX_NAME_LENGTH = 20

FAMILY_NAME = 'voting_test3'

VOTING_TEST3_ADDRESS_PREFIX = hashlib.sha512(
    FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]


def make_voting_test3_address(name):
    return VOTING_TEST3_ADDRESS_PREFIX + hashlib.sha512(
        name.encode('utf-8')).hexdigest()[-64:]


class Voting_Test3TransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [VOTING_TEST3_ADDRESS_PREFIX]

    def apply(self, transaction, context):
        verb, name, value = _unpack_transaction(transaction)

        state = _get_state_data(name, context)

        updated_state = _do_voting_test3(verb, name, value, state)

        _set_state_data(name, updated_state, context)


def _unpack_transaction(transaction):
    verb, name, value = _decode_transaction(transaction)

    _validate_verb(verb)
    _validate_name(name)
    _validate_value(value)

    return verb, name, value


def _decode_transaction(transaction):
    try:
        content = cbor.loads(transaction.payload)
    except:
        raise InvalidTransaction('Invalid payload serialization')

    try:
        verb = content['Verb']
    except AttributeError:
        raise InvalidTransaction('Verb is required')
    try:
        name = content['Name']
    except AttributeError:
        raise InvalidTransaction('Name is required')
    try:
        value = content['Value']
    except AttributeError:
        raise InvalidTransaction('Value is required')

    return verb, name, value


def _validate_verb(verb):
    print("VERB : {}".format(verb))
    if verb not in VALID_VERBS:
        raise InvalidTransaction('Verb must be "init"')


def _validate_name(name):
    pass
    #if not isinstance(name, str) or len(name) > MAX_NAME_LENGTH:
    #    raise InvalidTransaction(
    #        'Name must be a string of no more than {} characters'.format(
    #            MAX_NAME_LENGTH))


def _validate_value(value):
    pass
    #if not isinstance(value, int) or value < 0 or value > MAX_VALUE:
    #    raise InvalidTransaction(
    #        'Value must be an integer '
    #        'no less than {i} and no greater than {a}'.format(
    #            i=MIN_VALUE,
    #            a=MAX_VALUE))


def _get_state_data(name, context):
    address = make_voting_test3_address(name)

    state_entries = context.get_state([address])

    try:
        return cbor.loads(state_entries[0].data)
    except IndexError:
        return {}
    except:
        raise InternalError('Failed to load state data')


def _set_state_data(name, state, context):
    address = make_voting_test3_address(name)

    encoded = cbor.dumps(state)

    addresses = context.set_state({address: encoded})

    if not addresses:
        raise InternalError('State error')


def _do_voting_test3(verb, name, value, state):
    verbs = {
        'init': _do_init,
    }

    try:
        return verbs[verb](name, value, state)
    except KeyError:
        # This would be a programming error.
        raise InternalError('Unhandled verb: {}'.format(verb))


def _do_init(name, value, state):
    msg = 'Setting "{n}" to {v}'.format(n=name, v=value)
    LOGGER.debug(msg)

    if name in state:
        raise InvalidTransaction(
            'Verb is "init", but already exists: Name: {n}, Value {v}'.format(
                n=name,
                v=state[name]))

    updated = {k: v for k, v in state.items()}
    updated[name] = value

    return updated
