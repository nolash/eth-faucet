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
from eth_faucet.unittest import TestFaucetBase

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestFaucet(TestFaucetBase):

    def test_basic(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
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


    def test_basic_funding(self):
        o = balance(self.accounts[2])
        r = self.conn.do(o)
        prebalance = int(r, 16)

        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
        
        o = balance(self.accounts[2])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), prebalance)

        (tx_hash, o) = c.set_amount(self.address, self.accounts[0], 1000)
        r = self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 0)

        contract_gas_oracle = OverrideGasOracle(limit=21055, conn=self.conn)
        cg = Gas(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=contract_gas_oracle)
        (tx_hash_hex, o) = cg.create(self.accounts[0], self.address, 1000)
        self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
        
        (tx_hash_hex, o) = c.give_to(self.address, self.accounts[0], self.accounts[2])
        self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        o = balance(self.accounts[2])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), prebalance + 1000)


    def test_basic_result(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)

        contract_gas_oracle = OverrideGasOracle(limit=21055, conn=self.conn)
        cg = Gas(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=contract_gas_oracle)
        (tx_hash_hex, o) = cg.create(self.accounts[0], self.address, 1000)
        self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash, o) = c.set_amount(self.address, self.accounts[0], 1000)
        r = self.conn.do(o)

        o = balance(self.accounts[1])
        r = self.conn.do(o)
        prebalance = int(r, 16)

        nonce_oracle = RPCNonceOracle(self.accounts[1], self.conn)
        gas_price = 1000000000
        gas_oracle = OverrideGasOracle(limit=100000, price=gas_price, conn=self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash_hex, o) = c.gimme(self.address, self.accounts[1])
        self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        cost = r['gas_used'] * gas_price
        self.assertEqual(r['status'], 1)

        o = balance(self.accounts[1])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), prebalance - cost + 1000)


    def test_payable_with_tx_data(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)

        o = balance(self.accounts[0])
        r = self.conn.do(o)
        prebalance = int(r, 16)

        gas_price = 1000000000
        contract_gas_oracle = OverrideGasOracle(limit=21055, price=gas_price, conn=self.conn)
        cg = Gas(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=contract_gas_oracle)
        (tx_hash_hex, o) = cg.create(self.accounts[0], self.address, 1000, data='0x0')
        self.conn.do(o)

        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        cost = r['gas_used'] * gas_price
        self.assertEqual(r['status'], 0)

        o = balance(self.accounts[0])
        r = self.conn.do(o)
        self.assertEqual(int(r, 16), prebalance - cost)



if __name__ == '__main__':
    unittest.main()
