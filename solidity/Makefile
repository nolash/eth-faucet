SOLC = /usr/bin/solc

all:
	$(SOLC) --bin EthFaucet.sol --evm-version byzantium | awk 'NR>3' > EthFaucet.bin
	$(SOLC) --abi EthFaucet.sol --evm-version byzantium | awk 'NR>3' > EthFaucet.json
	$(SOLC) --metadata EthFaucet.sol --evm-version byzantium | awk 'NR>3' > EthFaucet.metadata.json
	$(SOLC) --bin PeriodSimple.sol --evm-version byzantium | awk 'NR>3' > PeriodSimple.bin
	$(SOLC) --abi PeriodSimple.sol --evm-version byzantium | awk 'NR==4' > PeriodSimple.json
	$(SOLC) --metadata PeriodSimple.sol --evm-version byzantium | awk 'NR==4' > PeriodSimple.metadata.json
	truncate -s -1 EthFaucet.bin
	truncate -s -1 PeriodSimple.bin

install: all
	cp -v *.json ../python/eth_faucet/data/
	cp -v *.bin ../python/eth_faucet/data/

