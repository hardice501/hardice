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
        header = transaction.header
        signer = header.signer_public_key

        ssc_payload = 
