#pip install eth-tester[py-evm]
# pip install py-solc-x web3 python-dotenv

import sys
from web3 import Web3
from eth_tester import EthereumTester
from web3.providers.eth_tester import EthereumTesterProvider
from solcx import install_solc, compile_source

# 1. SETUP ENVIRONMENT
eth_tester = EthereumTester()
w3 = Web3(EthereumTesterProvider(eth_tester))
deployer = w3.eth.accounts[0]

def setup_blockchain():
    print("Initializing Blockchain & Compiling...")
    install_solc("0.8.0")
    source = '''
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;
    contract SimpleStorage {
        uint256 private data;
        function setData(uint256 _data) public { data = _data; }
        function getData() public view returns (uint256) { return data; }
    }
    '''
    compiled = compile_source(source, solc_version="0.8.0")
    _, interface = compiled.popitem()
    
    # Deployment - ADDED 'gas' here to avoid eth_estimateGas error
    contract = w3.eth.contract(abi=interface['abi'], bytecode=interface['bin'])
    tx_hash = contract.constructor().transact({
        'from': deployer,
        'gas': 1000000  # Manual gas limit
    })
    address = w3.eth.wait_for_transaction_receipt(tx_hash).contractAddress
    print(f"Contract deployed at: {address}")
    return w3.eth.contract(address=address, abi=interface['abi'])

def main():
    storage = setup_blockchain()
    
    while True:
        print("\n--- DApp Menu ---")
        print("1. Write (setData)")
        print("2. Read (getData)")
        print("3. Exit")
        choice = input("Select an option (1-3): ")

        if choice == '1':
            try:
                val = int(input("Enter an integer to store on-chain: "))
                print("Sending transaction...")
                # Write Operation - ADDED 'gas' here as well
                tx_hash = storage.functions.setData(val).transact({
                    'from': deployer,
                    'gas': 500000  # Manual gas limit
                })
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"✔️ Success! Hash: {tx_hash.hex()}")
            except ValueError:
                print("⚠️ Error: Please enter a valid whole number.")
            except Exception as e:
                print(f"⚠️ Transaction failed: {e}")

        elif choice == '2':
            value = storage.functions.getData().call()
            print(f"📖 Current Blockchain Value: {value}")

        elif choice == '3':
            print("Exiting DApp...")
            break
        else:
            print("Invalid selection, try again.")

if __name__ == "__main__":
    main()