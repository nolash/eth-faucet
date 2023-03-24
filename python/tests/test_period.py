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

# local imports
from eth_faucet import EthFaucet
from eth_faucet.period import PeriodSimple
from eth_faucet.unittest import TestFaucetPeriodBase

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, '..', 'eth_faucet', 'data')


class TestFaucetPeriod(TestFaucetPeriodBase):

    def test_period_basic(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[1])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        nonce_oracle = RPCNonceOracle(self.accounts[2], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.gimme(self.address, self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)


    def test_period(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        enc = ABIContractEncoder()
        enc.method('setPeriod')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(100)
        data = enc.get()
        tx = c.template(self.accounts[0], self.period_store_address, use_nonce=True)
        tx = c.set_code(tx, data)
        (tx_hash_hex, o) = c.finalize(tx)
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)

        self.backend.time_travel(self.start_time + 6000)

        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)


    def test_balance(self):
        o = balance(self.accounts[1])
        r = self.conn.do(o)
        prebalance = int(r, 16)

        self.set_threshold(prebalance / 2)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.gimme(self.address, self.accounts[1])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)

        self.set_threshold(prebalance)

        (tx_hash_hex, o) = c.gimme(self.address, self.accounts[1])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)


    def test_period_front(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        enc = ABIContractEncoder()
        enc.method('setPeriod')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(100)
        data = enc.get()
        tx = c.template(self.accounts[0], self.period_store_address, use_nonce=True)
        tx = c.set_code(tx, data)
        (tx_hash_hex, o) = c.finalize(tx)
        self.conn.do(o)
   
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.gimme(self.address, self.accounts[0])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        o = block_by_number(r['block_number'])
        r = self.conn.do(o)
        thistime = r['timestamp']

        o = c.next_time(self.address, self.accounts[0], sender_address=self.accounts[0])
        r = self.conn.do(o)
        nexttime = int(r, 16)
        self.assertEqual(nexttime, thistime+100)

        o = c.check(self.address, self.accounts[0], sender_address=self.accounts[0])
        r = self.conn.do(o)
        checked = int(r, 16)
        self.assertEqual(checked, 0)


if __name__ == '__main__':
    unittest.main()
