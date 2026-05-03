import hashlib
import time

# ---------------- BLOCK CLASS ----------------
class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()


# ---------------- BLOCKCHAIN CLASS ----------------
class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.difficulty = difficulty
        self.create_genesis_block()

    # Hardcoded genesis block
    def create_genesis_block(self):
        genesis = Block(0, time.time(), "Genesis Block", "0")
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    def get_latest_block(self):
        return self.chain[-1]

    # Proof of Work
    def proof_of_work(self, block):
        target = '0' * self.difficulty
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block.hash

    def add_block(self, data):
        prev_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=prev_block.hash
        )
        self.proof_of_work(new_block)
        self.chain.append(new_block)


# ---------------- VALIDATION FUNCTION ----------------
def validate_blockchain(blockchain):
    
    if len(blockchain.chain) == 0:
        return False, "Blockchain is empty"

    # Check Genesis Block
    genesis = blockchain.chain[0]
    if genesis.hash != genesis.compute_hash():
        return False, "Genesis block hash mismatch"

    # Validate rest of the chain
    for i in range(1, len(blockchain.chain)):
        current = blockchain.chain[i]
        previous = blockchain.chain[i-1]

        # 1. Hash check
        if current.hash != current.compute_hash():
            return False, f"Block {i} hash mismatch"

        # 2. Linkage check
        if current.previous_hash != previous.hash:
            return False, f"Block {i} linkage error"

        # 3. Proof of Work check
        if not current.hash.startswith('0' * blockchain.difficulty):
            return False, f"Block {i} PoW invalid"

        # 4. Timestamp check
        if current.timestamp > time.time():
            return False, f"Block {i} has future timestamp"

    return True, "Blockchain is valid"


# ---------------- TESTING ----------------

# Create blockchain
bc = Blockchain(difficulty=2)

bc.add_block("Transaction 1: Riya pays 50")
bc.add_block("Transaction 2: Riya pays 30")

# VALID CASE
result, message = validate_blockchain(bc)
print("VALID TEST:", result, "-", message)


# ---------------- TAMPERING TESTS ----------------

# 1. Modify data (Hash failure)
bc.chain[1].data = "Tampered Data"

result, message = validate_blockchain(bc)
print("DATA TAMPER TEST:", result, "-", message)


# Fix it back
bc.chain[1].data = "Transaction 1: Riya pays 50"
bc.chain[1].hash = bc.chain[1].compute_hash()


# 2. Modify linkage
bc.chain[2].previous_hash = "fake_hash"

result, message = validate_blockchain(bc)
print("LINKAGE TAMPER TEST:", result, "-", message)


# ---------------- EDGE CASES ----------------

# Empty chain
empty_bc = Blockchain()
empty_bc.chain = []
print(validate_blockchain(empty_bc))

# Single block
single_bc = Blockchain()
print(validate_blockchain(single_bc))