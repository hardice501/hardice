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

import hashlib
import logging
import cbor

from sawtooth_sdk.processor.handler import TransactionHandler


LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'ssc'

SSC_ADDRESS_PREFIX = hashlib.sha512(
    FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]

def make_ssc_address(tag):
    return INTKEY_ADDRESS_PREFIX + hashlib.sha512(
        tag.encode('utf-8')).hexdigest()[-64:]

class Simple_Smart_contract_TransactionHandler(TransactionHandler):

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [SSC_ADDRESS_PREFIX]

    @property
    def apply(self, transaction, context):
        verb, tag, data = _unpack_transaction(transaction)

        state = _get_state_data(tag, context)

        updated_state = _do_intkey(verb, tag, data, state)

        _set_state_data(tag, updated_state, context)


def _unpack_transaction(transaction):
    verb, tag, data = _decode_transaction(transaction)

    _validate_verb(verb)
    _validate_tag(tag)
    _validate_data(data)

    return verb, tag, data


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
        tag = content['Tag']
    except AttributeError:
        raise InvalidTransaction('Name is required')

    try:
        data = content['Data']
    except AttributeError:
        raise InvalidTransaction('Value is required')

    return verb, tag, data


def _validate_verb(verb):
    if verb not in VALID_VERBS:
        raise InvalidTransaction('Verb must be "set"')


def _validate_tag(tag):
    # if not isinstance(name, str) or len(name) > MAX_NAME_LENGTH:
    #     raise InvalidTransaction(
    #         'Name must be a string of no more than {} characters'.format(
    #             MAX_NAME_LENGTH))
    pass


def _validate_data(data):
    # if not isinstance(value, int) or value < 0 or value > MAX_VALUE:
    #     raise InvalidTransaction(
    #         'Value must be an integer '
    #         'no less than {i} and no greater than {a}'.format(
    #             i=MIN_VALUE,
    #             a=MAX_VALUE))
    pass


def _get_state_data(tag, context):
    address = make_ssc_address(tag)

    state_entries = context.get_state([address])

    try:
        return cbor.loads(state_entries[0].data)
    except IndexError:
        return {}
    except:
        raise InternalError('Failed to load state data')


def _set_state_data(tag, state, context):
    address = make_ssc_address(tag)

    encoded = cbor.dumps(state)

    addresses = context.set_state({address: encoded})

    if not addresses:
        raise InternalError('State error')


def _do_ssc(verb, tag, data, state):
    verbs = {
        'set': _do_set,
    }

    try:
        return verbs[verb](tag, data, state)
    except KeyError:
        # This would be a programming error.
        raise InternalError('Unhandled verb: {}'.format(verb))


def _do_set(tag, data, state):
    msg = 'Setting "{n}" to {v}'.format(n=tag, v=data)
    LOGGER.debug(msg)

    if tag in state:
        raise InvalidTransaction(
            'Verb is "set", but already exists: Tag: {n}, Data {v}'.format(
                n=tag,
                v=state[tag]))

    updated = {k: v for k, v in state.items()}
    updated[tag] = name

    return updated


def _do_inc(name, value, state):
    msg = 'Incrementing "{n}" by {v}'.format(n=name, v=value)
    LOGGER.debug(msg)

    if name not in state:
        raise InvalidTransaction(
            'Verb is "inc" but name "{}" not in state'.format(name))

    curr = state[name]
    incd = curr + value

    if incd > MAX_VALUE:
        raise InvalidTransaction(
            'Verb is "inc", but result would be greater than {}'.format(
                MAX_VALUE))

    updated = {k: v for k, v in state.items()}
    updated[name] = incd

    return updated


def _do_dec(name, value, state):
    msg = 'Decrementing "{n}" by {v}'.format(n=name, v=value)
    LOGGER.debug(msg)

    if name not in state:
        raise InvalidTransaction(
            'Verb is "dec" but name "{}" not in state'.format(name))

    curr = state[name]
    decd = curr - value

    if decd < MIN_VALUE:
        raise InvalidTransaction(
            'Verb is "dec", but result would be less than {}'.format(
                MIN_VALUE))

    updated = {k: v for k, v in state.items()}
    updated[name] = decd

    return updated