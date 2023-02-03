pragma solidity >0.8.0;

// SPDX-License-Identifier: GPL-3.0-or-later

contract EthFacuet {

	address public owner;
	address public registry;
	uint256 public value;
	uint256 public period;

	mapping (address => uint256) public lastUsed;

	event FaucetUsed(address indexed _recipient, address indexed _token, uint256 _value);
	event FaucetFail(address indexed _recipient, address indexed _token, uint256 _value);
	event FaucetAmountChange(uint256 _value);

	constructor(address _registry, uint256 periodMinutes) {
		registry = _registry;
		period = periodMinutes;
		owner = msg.sender;
	}

	function setValue(uint256 _v) public returns(uint256) {
		require(msg.sender == owner, 'ERR_NOT_OWNER');
		value = _v;
		emit FaucetAmountChange(value);
		return value;
	}

	function checkPeriod(address _recipient) private view returns(bool) {
		if (lastUsed[_recipient] == 0) {
			return true;
		}
		require(block.timestamp > lastUsed[_recipient] + period);
		return true;
	}

	function checkRegistry(address _recipient) private returns(bool) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = registry.call(abi.encodeWithSignature("have(address)", _recipient));
		if (!_ok) {
			emit FaucetFail(_recipient, address(0), value);
			revert('ERR_TRANSFER');
		}
			
		emit FaucetUsed(_recipient, address(0), value);
		return true;
	}

	function check(address _recipient) private returns(bool) {
		if (period > 0) {
			checkPeriod(_recipient);
		}
		if (registry != address(0)) {
			checkRegistry(_recipient);
		}
		return true;
	}


	function get() public returns(uint256) {
		check(msg.sender);
		payable(msg.sender).transfer(value);
		return value;
	}

	function to(address _recipient) public returns(uint256) {
		check(_recipient);
		payable(_recipient).transfer(value);
		return value;
	}

	receive () payable external {
	}
}
