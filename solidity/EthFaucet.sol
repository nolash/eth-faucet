pragma solidity >0.8.0;

// SPDX-License-Identifier: GPL-3.0-or-later

contract EthFacuet {

	address public owner;
	address public registry;
	address public periodChecker;
	uint256 public sealState;
	uint256 amount;

	uint8 constant REGISTRY_STATE = 1;
	uint8 constant PERIODCHECKER_STATE = 2;
	uint8 constant VALUE_STATE = 4;
	uint256 constant public maxSealState = 7;

	event Give(address indexed _recipient, address indexed _token, uint256 _amount);
	event FaucetAmountChange(uint256 _amount);
	event SealStateChange(uint256 indexed _sealState, address _registry, address _periodChecker);
	event ImNotGassy();

	constructor() {
		owner = msg.sender;
	}

	function seal(uint256 _state) public returns(uint256) {
		require(_state < 8, 'ERR_INVALID_STATE');
		require(_state & sealState == 0, 'ERR_ALREADY_LOCKED');
		sealState |= _state;
		emit SealStateChange(sealState, registry, periodChecker);
		return uint256(sealState);
	}

	function setAmount(uint256 _v) public returns(uint256) {
		require(msg.sender == owner, 'ERR_NOT_OWNER');
		require(sealState & VALUE_STATE == 0, 'ERR_SEALED');
		amount = _v;
		emit FaucetAmountChange(amount);
		return amount;
	}

	function setPeriodChecker(address _checker) public {
		require(msg.sender == owner, 'ERR_NOT_OWNER');
		require(sealState & PERIODCHECKER_STATE == 0, 'ERR_SEALED');
		periodChecker = _checker;
		emit SealStateChange(sealState, registry, periodChecker);
	}

	function setRegistry(address _registry) public {
		require(msg.sender == owner, 'ERR_NOT_OWNER');
		require(sealState & REGISTRY_STATE == 0, 'ERR_SEALED');
		registry = _registry;
		emit SealStateChange(sealState, registry, periodChecker);
	}

	function checkPeriod(address _recipient) private returns(bool) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = periodChecker.call(abi.encodeWithSignature("check(address)", _recipient));
		if (!_ok) {
			revert('ERR_PERIOD_BACKEND_ERROR');
		}
		if (_result[31] == 0) {
			revert('ERR_PERIOD_CHECK');
		}

		(_ok, _result) = periodChecker.call(abi.encodeWithSignature("poke(address)", _recipient));
		if (!_ok) {
			revert('ERR_REGISTRY_BACKEND_ERROR');
		}
		return true;
	}

	function checkRegistry(address _recipient) private returns(bool) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = registry.call(abi.encodeWithSignature("have(address)", _recipient));
		if (!_ok) {
			revert('ERR_TRANSFER');
		}
		if (_result[31] == 0) {
			revert('ERR_REGISTRY_CHECK');
		}

		emit Give(_recipient, address(0), amount);
		return true;
	}

	function checkBalance() private {
		if (amount > address(this).balance) {
			emit ImNotGassy();
			revert('ERR_ITSNOTAGAS');
		}
	}

	function check(address _recipient) private returns(bool) {
		if (periodChecker != address(0)) {
			checkPeriod(_recipient);
		}
		if (registry != address(0)) {
			checkRegistry(_recipient);
		}
		checkBalance();
		return true;
	}

	function gimme() public returns(uint256) {
		require(check(msg.sender));
		payable(msg.sender).transfer(amount);
		return amount;
	}

	function giveTo(address _recipient) public returns(uint256) {
		require(check(_recipient));
		payable(_recipient).transfer(amount);
		return amount;
	}

	function nextTime(address _subject) public returns(uint256) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = periodChecker.call(abi.encodeWithSignature("next(address)", _subject));
		if (!_ok) {
			revert('ERR_PERIOD_BACKEND_ERROR');
		}
		return uint256(bytes32(_result));
	}

	function tokenAmount() public view returns(uint256) {
		return amount;
	}

	function token() public pure returns(address) {
		return address(0);
	}

	receive () payable external {
	}
}
