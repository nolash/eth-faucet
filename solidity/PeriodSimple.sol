pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract PeriodSimple {

	address public owner;
	address public poker;
	uint256 public period;
	uint256 public balanceThreshold;
	mapping (address => uint256) public lastUsed;

	event PeriodChange(uint256 _value);
	event BalanceThresholdChange(uint256 _value);

	constructor() {
		owner = msg.sender;
		poker = owner;
	}

	function setPeriod(uint256 _period) public {
		require(owner == msg.sender, 'ERR_NOT_OWNER');
		period = _period;
		emit PeriodChange(_period);
	}

	function setPoker(address _poker) public {
		require(msg.sender == owner);
		poker = _poker;
	}

	function setBalanceThreshold(uint256 _threshold) public {
		require(msg.sender == owner);
		balanceThreshold = _threshold;
		emit BalanceThresholdChange(_threshold);
	}

	function next(address _subject) external view returns(uint256) {
		return lastUsed[_subject] + period;
	}
	
	function check(address _subject) external view returns(bool) {
		if (balanceThreshold > 0 && _subject.balance >= balanceThreshold) {
			return false;
		}
		if (lastUsed[_subject] == 0) {
			return true;
		}
		return block.timestamp > this.next(_subject);
	}

	function poke(address _subject) external returns(bool) {
		require(msg.sender == owner || msg.sender == poker, 'ERR_ACCESS');
		if (!this.check(_subject)) {
			return false;
		}
		lastUsed[_subject] = block.timestamp;
		return true;
	}
}
