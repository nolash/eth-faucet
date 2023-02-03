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
