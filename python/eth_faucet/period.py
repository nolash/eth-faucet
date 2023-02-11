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
from erc20_faucet import Faucet
from hexathon import add_0x

logg = logging.getLogger().getChild(__name__)

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class PeriodSimple(Faucet):

    __abi = None
    __bytecode = None
    __address = None

    @staticmethod
    def abi():
        if PeriodSimple.__abi == None:
            f = open(os.path.join(datadir, 'PeriodSimple.json'), 'r')
            PeriodSimple.__abi = json.load(f)
            f.close()
        return PeriodSimple.__abi


    @staticmethod
    def bytecode():
        if PeriodSimple.__bytecode == None:
            f = open(os.path.join(datadir, 'PeriodSimple.bin'))
            PeriodSimple.__bytecode = f.read()
            f.close()
        return PeriodSimple.__bytecode

    @staticmethod
    def gas(code=None):
        return 2000000


    # TODO: allow multiple overriders
    def constructor(self, sender_address):
        code = PeriodSimple.bytecode()
        enc = ABIContractEncoder()
        code += enc.get()
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.build(tx)


    def set_poker(self, contract_address, sender_address, poker_address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('setPeriodChecker')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(poker_address)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def set_period(self, contract_address, sender_address, period, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('setPeriod')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(threshold)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def set_balance_threshold(self, contract_address, sender_address, threshold, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('setBalanceThreshold')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(threshold)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx
