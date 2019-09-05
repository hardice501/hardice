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

from sawtooth_sdk.processor.handler import TransactionHandler


class Simple_Smart_contract_TransactionHandler(TransactionHandler):
    """
    TransactionHandler is the Abstract Base Class that defines the business
    logic for a new transaction family.

    The family_name, family_versions, and namespaces properties are
    used by the processor to route processing requests to the handler.
    """

    @property
    def family_name(self):
        return 'ssc'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    @property
    def apply(self, transaction, context):
        """
        Apply is the single method where all the business logic for a
        transaction family is defined. The method will be called by the
        transaction processor upon receiving a TpProcessRequest that the
        handler understands and will pass in the TpProcessRequest and an
        initialized instance of the Context type.
        """
