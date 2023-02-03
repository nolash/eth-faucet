pragma solidity >0.8.0;

// SPDX-License-Identifier: GPL-3.0-or-later

contract PeriodSimple {

	address public owner;
	address public poker;
	uint256 public period;
	mapping (address => uint256) public lastUsed;

	event PeriodChange(uint256 _value);

	constructor() {
		owner = msg.sender;
		poker = owner;
	}

	function setPeriod(uint256 _period) public {
		require(owner == msg.sender, 'ERR_NOT_OWNER');
		period = _period;
	}

	function setPoker(address _poker) public {
		require(msg.sender == owner);
		poker = _poker;
	}

	function check(address _subject) public view returns(bool) {
		if (lastUsed[_subject] == 0) {
			return true;
		}
		return block.timestamp > lastUsed[_subject] + period;
	}

	function poke(address _subject) public {
		require(msg.sender == owner || msg.sender == poker, 'ERR_ACCESS');
		require(check(_subject), 'ERR_PREMATURE');
		lastUsed[_subject] = block.timestamp;
	}
}