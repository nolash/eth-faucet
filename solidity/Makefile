SOLC = /usr/bin/solc

all:
	$(SOLC) --bin EthFaucet.sol --evm-version byzantium | awk 'NR>3' > EthFaucet.bin
	truncate -s -1 EthFaucet.bin
	$(SOLC) --abi EthFaucet.sol --evm-version byzantium | awk 'NR>3' > EthFaucet.json
	$(SOLC) --bin PeriodSimple.sol --evm-version byzantium | awk 'NR>3' > PeriodSimple.bin
	truncate -s -1 PeriodSimple.bin
	$(SOLC) --abi PeriodSimple.sol --evm-version byzantium | awk 'NR==4' > PeriodSimple.json

install: all
	cp -v *{json,bin} ../python/eth_faucet/data/

