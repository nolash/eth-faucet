pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract EthFaucet {

	// Implements ERC173
	address public owner;
	address public registry;
	address public periodChecker;

	// Implements Faucet
	address constant public token = address(0);

	// Implements Seal
	uint256 public sealState;

	uint256 amount;

	uint8 constant REGISTRY_STATE = 1;
	uint8 constant PERIODCHECKER_STATE = 2;
	uint8 constant VALUE_STATE = 4;
	// Implements Seal
	uint256 constant public maxSealState = 7;

	// Implements Faucet
	event Give(address indexed _recipient, address indexed _token, uint256 _amount);
	// Implements Faucet
	event FaucetAmountChange(uint256 _amount);

	// Implements Seal
	event SealStateChange(uint256 indexed _sealState, address _registry, address _periodChecker);

	constructor() {
		owner = msg.sender;
	}

	// Set the given seal bits.
	// Reverts if any bits are already set, if bit value is out of bounds.
	function seal(uint256 _state) public returns(uint256) {
		require(_state < 8, 'ERR_INVALID_STATE');
		require(_state & sealState == 0, 'ERR_ALREADY_LOCKED');
		sealState |= _state;
		emit SealStateChange(sealState, registry, periodChecker);
		return uint256(sealState);
	}

	// Change faucet amount.
	// Reverts if VALUE_STATE seal is set.
	function setAmount(uint256 _v) public returns(uint256) {
		require(msg.sender == owner, 'ERR_NOT_OWNER');
		require(sealState & VALUE_STATE == 0, 'ERR_SEALED');
		amount = _v;
		emit FaucetAmountChange(amount);
		return amount;
	}

	// Set period checker contract backend.
	// Reverts if PERIODCHECKER_STATE seal is set
	function setPeriodChecker(address _checker) public {
		require(msg.sender == owner, 'ERR_NOT_OWNER');
		require(sealState & PERIODCHECKER_STATE == 0, 'ERR_SEALED');
		periodChecker = _checker;
		emit SealStateChange(sealState, registry, periodChecker);
	}

	// Set accounts index (Access Control List - ACL) backend.
	// Reverts if REGISTRY_STATE seal is set
	function setRegistry(address _registry) public {
		require(msg.sender == owner, 'ERR_NOT_OWNER');
		require(sealState & REGISTRY_STATE == 0, 'ERR_SEALED');
		registry = _registry;
		emit SealStateChange(sealState, registry, periodChecker);
	}

	// Return true if period checker backend allows usage of the faucet.
	// Will always return true if period checker contract address has not been set.
	function checkPeriod(address _recipient) private returns(bool) {
		bool _ok;
		bytes memory _result;

		if (periodChecker == address(0)) {
			return true;
		}

		(_ok, _result) = periodChecker.call(abi.encodeWithSignature("check(address)", _recipient));
		if (!_ok) {
			revert('ERR_PERIOD_BACKEND');
		}
		return _result[31] == 0x01;
	}

	// Return true if recipient has been added to the ACL.
	// Will always return true if ACL contract address has not been set.
	function checkRegistry(address _recipient) private returns(bool) {
		bool _ok;
		bytes memory _result;

		if (registry == address(0)) {
			return true;
		}

		(_ok, _result) = registry.call(abi.encodeWithSignature("have(address)", _recipient));
		if (!_ok) {
			revert('ERR_REGISTRY_BACKEND');
		}
		return _result[31] == 0x01;
	}

	// Return false if contract does not have sufficient gas token balance to cover a single use.
	// Used as backend for check.
	function checkBalance() private view returns(bool) {
		return amount <= address(this).balance;
	}

	// Check if a faucet usage attempt would succeed for the given recipient in the current contract state.
	function check(address _recipient) public returns(bool) {
		if (!checkPeriod(_recipient)) {
			return false;
		}
		if (!checkRegistry(_recipient)) {
			return false;
		}
		return checkBalance();
	}

	// Execute a single faucet usage for recipient.
	function checkAndPoke(address _recipient) private returns(bool){
		bool _ok;
		bytes memory _result;

		if (!checkBalance()) {
			revert('ERR_INSUFFICIENT_BALANCE');
		}

		if (!checkRegistry(_recipient)) {
			revert('ERR_NOT_IN_WHITELIST');
		}

		if (periodChecker == address(0)) {
			return true;
		}

		(_ok, _result) = periodChecker.call(abi.encodeWithSignature("poke(address)", _recipient));
		if (!_ok) {
			revert('ERR_PERIOD_BACKEND');
		} 
		if (_result[31] == 0) {
			revert('ERR_PERIOD_CHECK');
		}
		return true;
	}

	// Implements Faucet
	function gimme() public returns(uint256) {
		require(checkAndPoke(msg.sender));
		payable(msg.sender).transfer(amount);
		emit Give(msg.sender, address(0), amount);
		return amount;
	}

	// Implements Faucet
	function giveTo(address _recipient) public returns(uint256) {
		require(checkAndPoke(_recipient));
		payable(_recipient).transfer(amount);
		emit Give(_recipient, address(0), amount);
		return amount;
	}

	// Implements Faucet
	function nextTime(address _subject) public returns(uint256) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = periodChecker.call(abi.encodeWithSignature("next(address)", _subject));
		if (!_ok) {
			revert('ERR_PERIOD_BACKEND_ERROR');
		}
		return uint256(bytes32(_result));
	}

	// Implements Faucet
	function nextBalance(address _subject) public returns(uint256) {
		bool _ok;
		bytes memory _result;

		(_ok, _result) = periodChecker.call(abi.encodeWithSignature("balanceThreshold()", _subject));
		if (!_ok) {
			revert('ERR_PERIOD_BACKEND_ERROR');
		}
		return uint256(bytes32(_result));

	}

	// Implements Faucet
	function tokenAmount() public view returns(uint256) {
		return amount;
	}

	receive () payable external {
	}

	// Implements ERC165
	function supportsInterface(bytes4 _sum) public pure returns (bool) {
		if (_sum == 0x01ffc9a7) { // ERC165
			return true;
		}
		if (_sum == 0x9493f8b2) { // ERC173
			return true;
		}
		if (_sum == 0x1a3ac634) { // Faucet
			return true;
		}
		if (_sum == 0x0d7491f8) { // Seal
			return true;
		}
		return false;
	}
}
