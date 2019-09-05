from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_simple_smart_contract.processor.handler import Simple_Smart_contract_TransactionHandler

def main():
    processor = TransactionProcessor(url='tcp://127.0.0.1:4004')

    handler = Simple_Smart_contract_TransactionHandler()

    processor.start()