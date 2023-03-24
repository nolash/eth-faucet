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
from chainlib.eth.contract import ABIContractEncoder
from chainlib.eth.tx import TxFactory
from chainlib.eth.contract import ABIContractType
from chainlib.eth.block import block_by_number
from eth_accounts_index.registry import AccountRegistry

# local import
from eth_faucet import EthFaucet
from eth_faucet.period import PeriodSimple

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, '..', 'data')


class TestFaucetBase(EthTesterCase):

    def setUp(self):
        super(TestFaucetBase, self).setUp()
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.constructor(self.accounts[0])
        r = self.conn.do(o)
        
        o = receipt(r)
        r = self.conn.do(o)
        self.address = to_checksum_address(r['contract_address'])
        logg.debug('faucet contract {}'.format(self.address))


class TestFaucetRegistryBase(TestFaucetBase):

    def setUpRegistry(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = AccountRegistry(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.constructor(self.accounts[0])
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        r = self.conn.do(o)
        o = receipt(r)
        r = self.conn.do(o)
        self.registry_address = to_checksum_address(r['contract_address'])

        (tx_hash_hex, o) = c.add_writer(self.registry_address, self.accounts[0], self.accounts[0])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        (tx_hash_hex, o) = c.add(self.registry_address, self.accounts[0], self.accounts[1])
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.set_registry(self.address, self.accounts[0], self.registry_address)
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)


    def setUp(self):
        super(TestFaucetRegistryBase, self).setUp()
        self.setUpRegistry()


class TestFaucetPeriodBase(TestFaucetBase):

    def setUpPeriod(self):
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = PeriodSimple(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.constructor(self.accounts[0])
        r = self.conn.do(o)

        f = open(os.path.join(datadir, 'PeriodSimple.bin'))
        period_store_bytecode = f.read()
        f.close()
        enc = ABIContractEncoder()
        code = enc.get()

        c = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        tx = c.template(self.accounts[0], None, use_nonce=True)
        tx = c.set_code(tx, period_store_bytecode)
        (tx_hash_hex, o) =  c.build(tx)
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
        self.period_store_address = r['contract_address']

        o = block_by_number(r['block_number'])
        r = self.conn.do(o)

        try:
            self.start_time = int(r['timestamp'], 16)
        except TypeError:
            self.start_time = int(r['timestamp'])

        c = EthFaucet(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.set_period_checker(self.address, self.accounts[0], self.period_store_address)
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        enc = ABIContractEncoder()
        enc.method('setPoker')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(self.address)
        data = enc.get()
        tx = c.template(self.accounts[0], self.period_store_address, use_nonce=True)
        tx = c.set_code(tx, data)
        (tx_hash_hex, o) = c.finalize(tx)
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        self.period = 0
        self.threshold = 0


    def setUp(self):
        super(TestFaucetPeriodBase, self).setUp()
        self.setUpPeriod()


    def set_period(self, period):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        enc = ABIContractEncoder()
        enc.method('setPeriod')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(period)
        data = enc.get()
        tx = c.template(self.accounts[0], self.period_store_address, use_nonce=True)
        tx = c.set_code(tx, data)
        (tx_hash_hex, o) = c.finalize(tx)
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)
        self.period = period


    def set_threshold(self, threshold):
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.conn)
        c = TxFactory(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        enc = ABIContractEncoder()
        enc.method('setBalanceThreshold')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(threshold)
        data = enc.get()
        tx = c.template(self.accounts[0], self.period_store_address, use_nonce=True)
        tx = c.set_code(tx, data)
        (tx_hash_hex, o) = c.finalize(tx)
        self.conn.do(o)
        o = receipt(tx_hash_hex)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)

        self.threshold = threshold


class TestFaucetFullBase(TestFaucetRegistryBase, TestFaucetPeriodBase):

    def setUp(self):
        super(TestFaucetFullBase, self).setUp()
        self.setUpPeriod()
