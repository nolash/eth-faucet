# eth-faucet

A faucet implementation for ETH gas tokens, implementing the [CIC Faucet](https://git.grassecon.net/cicnet/cic-contracts#faucet) interface.


## Setup

Firstly, the faucet contract must be funded before use. It can be funded simply by sending gas tokens to it as a normal transaction.

Secondly, the amount of gas tokens to emit must be changed using the `setAmount()` method. Only the contract "owner" or a "writer" (see below) may change the amount. The amount can be changed again at any time, until sealed.


## Usage

To receive gas tokens from the faucet, the method `giveTo(address)` or `gimme()` is used. The latter will send gas tokens to the address that signed the transaction.


## Restricting accounts

Usage of the faucet may be restricted by which addresses can request gas tokens from it.

The list must be provided by a contract implementing the [CIC ACL](https://git.grassecon.net/cicnet/cic-contracts#acl) interface. The contract to use is defined using the `setRegistry()` method.


## Restricting usage frequency

Usage of the faucet may also be restricted by time delay. 

The usage control must be provided by a smart contract implementing the [CIC Throttle](https://git.grassecon.net/cicnet/cic-contracts#throttle) interface. The contract to use is defined using the `setPeriodChecker()` method.


### Example usage frequency controller

The `PeriodSimple` contract provided by this repository demonstrates an implementation of the usage frequency restriction.

Only a single address has access to call the `poke(address)` method. This address is typically the contract providing the resource, and is defined by calling the `setPoker(address)` method.

The number of seconds that must pass between each usage can be set using `setPeriod()`

Using `setBalanceThreshold()` a maximum balance can be defined, to disallow use for addresses holding higher balances. (Note that this does not provide any real protection against agents, for example non-custioal wallets, that can forward the gas tokens at will).


## Sealing the contracts

The faucet contract implements the [CIC Seal](https://git.grassecon.net/cicnet/cic-contracts#seal) interface to enable sealing the parameters defining its behavior.

The parameters that can be sealed are:

- *Registry*, blocking the use of the `setRegistry()` method.
- *Period checker*, blocking the use of the `setPeriodChecker()` method.
- *Value*, blocking the use of the `setAmount()` method.

The PeriodSimple contract does not implement the seal, but may discard ownedship through the [EIP173](https://eips.ethereum.org/EIPS/eip-173) interface, after which no parameters changing behavior can be modified.
