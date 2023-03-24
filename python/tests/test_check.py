# standard imports
import os
import unittest
import logging

# external imports
from chainlib.connection import RPCConnection
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address
from chainlib.eth.gas import balance
from chainlib.eth.gas import Gas
from chainlib.eth.gas import OverrideGasOracle

# local import
from eth_faucet import EthFaucet
from eth_faucet.unittest import TestFaucetFullBase

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestFaucet(TestFaucetFullBase):

    def test_check_registry(self):
        c = EthFaucet(self.chain_spec)
        o = c.check(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 1)

        o = c.check(self.address, self.accounts[2], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 0)


    def test_check_period_time(self):
        self.set_period(100)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)

        o = c.check(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 1)

        (tx_hash_hex, o) = c.gimme(self.address, self.accounts[1])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = c.check(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 0)


    def test_check_period_balance(self):
        o = balance(self.accounts[1])
        r = self.conn.do(o)
        prebalance = int(r, 16)

        c = EthFaucet(self.chain_spec)
        o = c.check(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 1)

        self.set_threshold(prebalance + 1)

        o = c.check(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 1)

        self.set_threshold(prebalance)

        o = c.check(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), 0)


if __name__ == '__main__':
    unittest.main()
