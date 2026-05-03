// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HelloWorld {
    string public message;

    constructor() {
        message = "Hello World";
    }

    function get() public view returns (string memory) {
        return message;
    }

    function set(string memory newMessage) public {
        message = newMessage;
    }
}