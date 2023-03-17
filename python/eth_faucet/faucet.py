# Author:	Louis Holbrook <dev@holbrook.no> 0826EDA1702D1E87C6E2875121D2E7BB88C2A746
# SPDX-License-Identifier:	GPL-3.0-or-later
# File-version: 1
# Description: Python interface to abi and bin files for faucet contracts

# standard imports
import logging
import json
import os

# external imports
from chainlib.eth.tx import TxFactory
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.contract import (
        abi_decode_single,
        ABIContractEncoder,
        ABIContractType,
        )
from chainlib.eth.tx import TxFormat
from chainlib.jsonrpc import JSONRPCRequest
from erc20_faucet import Faucet
from hexathon import add_0x

logg = logging.getLogger().getChild(__name__)

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class EthFaucet(Faucet):

    __abi = None
    __bytecode = None
    __address = None

    @staticmethod
    def abi():
        if EthFaucet.__abi == None:
            f = open(os.path.join(datadir, 'EthFaucet.json'), 'r')
            EthFaucet.__abi = json.load(f)
            f.close()
        return EthFaucet.__abi


    @staticmethod
    def bytecode():
        if EthFaucet.__bytecode == None:
            f = open(os.path.join(datadir, 'EthFaucet.bin'))
            EthFaucet.__bytecode = f.read()
            f.close()
        return EthFaucet.__bytecode

    @staticmethod
    def gas(code=None):
        return 2000000


    # TODO: allow multiple overriders
    def constructor(self, sender_address):
        code = EthFaucet.bytecode()
        enc = ABIContractEncoder()
        code += enc.get()
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.build(tx)


    def set_period_checker(self, contract_address, sender_address, checker_address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('setPeriodChecker')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(checker_address)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def set_registry(self, contract_address, sender_address, checker_address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('setRegistry')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(checker_address)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def check(self, contract_address, address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('check')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o

