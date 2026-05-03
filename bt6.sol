// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TokenTransfer {
    string public name = "AssignmentToken";
    string public symbol = "ATK";
    uint256 public totalSupply;
    
    // Mapping to track balances of accounts
    mapping(address => uint256) public balances;

    // The constructor assigns all initial tokens to the contract deployer
    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply;
        balances[msg.sender] = _initialSupply;
    }

    /**
     * @dev Moves 'amount' tokens from the caller's account to 'recipient'.
     * Returns a boolean value indicating whether the operation succeeded.
     */
    function transfer(address recipient, uint256 amount) public returns (bool) {
        // Validation: Check if recipient is valid and sender has enough tokens
        require(recipient != address(0), "Transfer to the zero address");
        require(balances[msg.sender] >= amount, "Transfer failed: insufficient balance");

        // Update balances
        balances[msg.sender] -= amount;
        balances[recipient] += amount;

        return true;
    }

    // Helper function to check balance of a specific account
    function balanceOf(address account) public view returns (uint256) {
        return balances[account];
    }
}