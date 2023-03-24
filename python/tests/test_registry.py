# standard imports
import os
import unittest
import logging

# external imports
from chainlib.connection import RPCConnection
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.tx import receipt
from chainlib.eth.tx import TxFactory
from chainlib.eth.address import to_checksum_address
from chainlib.eth.gas import balance
from chainlib.eth.gas import Gas
from chainlib.eth.gas import OverrideGasOracle
from chainlib.eth.contract import ABIContractEncoder
from chainlib.eth.contract import ABIContractType
from chainlib.eth.block import block_by_number
from eth_accounts_index.registry import AccountRegistry

# local imports
from eth_faucet import EthFaucet
from eth_faucet.unittest import TestFaucetRegistryBase

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestFaucetRegistry(TestFaucetRegistryBase):

    def test_basic(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)

        nonce_oracle = RPCNonceOracle(self.accounts[2], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.gimme(self.address, self.accounts[1])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)


    def test_registry(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)

        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[1])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)


    def test_transparent(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        o = c.check(self.address, self.accounts[2], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 0)

        o = c.check(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 1)


if __name__ == '__main__':
    unittest.main()
