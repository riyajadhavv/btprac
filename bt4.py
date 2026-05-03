import hashlib
import json
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


# ---------------- WALLET ----------------
class Wallet:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

        # Address = hash of public key
        self.address = self.generate_address()

    def generate_address(self):
        pub_bytes = str(self.public_key).encode()
        return hashlib.sha256(pub_bytes).hexdigest()

    def sign(self, data):
        message = json.dumps(data).encode()
        return self.private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )


# ---------------- TRANSACTION ----------------
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender_address = sender.address
        self.receiver_address = receiver.address
        self.amount = amount
        self.timestamp = time.time()

        self.signature = None
        self.transaction_id = None

    def compute_hash(self):
        tx_data = f"{self.sender_address}{self.receiver_address}{self.amount}{self.timestamp}"
        return hashlib.sha256(tx_data.encode()).hexdigest()

    def sign_transaction(self, sender_wallet):
        self.transaction_id = self.compute_hash()
        self.signature = sender_wallet.sign({
            "sender": self.sender_address,
            "receiver": self.receiver_address,
            "amount": self.amount,
            "timestamp": self.timestamp
        })


# ---------------- SYSTEM ----------------
class TransactionSystem:
    def __init__(self):
        self.balances = {}
        self.used_transactions = set()

    def set_balance(self, address, amount):
        self.balances[address] = amount

    def verify_signature(self, tx, sender_public_key):
        message = json.dumps({
            "sender": tx.sender_address,
            "receiver": tx.receiver_address,
            "amount": tx.amount,
            "timestamp": tx.timestamp
        }).encode()

        try:
            sender_public_key.verify(
                tx.signature,
                message,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def process_transaction(self, tx, sender_public_key):
        
        # 1. Check signature
        if not self.verify_signature(tx, sender_public_key):
            return False, "Invalid Signature"

        # 2. Check duplicate transaction
        if tx.transaction_id in self.used_transactions:
            return False, "Double Spending Detected"

        # 3. Check balance
        sender_balance = self.balances.get(tx.sender_address, 0)
        if sender_balance < tx.amount:
            return False, "Insufficient Balance"

        # 4. Process transaction
        self.balances[tx.sender_address] -= tx.amount
        self.balances[tx.receiver_address] = self.balances.get(tx.receiver_address, 0) + tx.amount

        # Mark transaction as used
        self.used_transactions.add(tx.transaction_id)

        return True, "Transaction Successful"


# ---------------- TESTING ----------------

# Create wallets
walletA = Wallet()
walletB = Wallet()

# Create system
system = TransactionSystem()

# Set initial balance
system.set_balance(walletA.address, 100)
system.set_balance(walletB.address, 50)

print("Initial Balances:")
print("A:", system.balances[walletA.address])
print("B:", system.balances[walletB.address])


# ---------------- VALID TRANSACTION ----------------
tx1 = Transaction(walletA, walletB, 40)
tx1.sign_transaction(walletA)

result, msg = system.process_transaction(tx1, walletA.public_key)
print("\nVALID TRANSACTION:", msg)


# ---------------- DOUBLE SPENDING ----------------
# Try using same transaction again
result, msg = system.process_transaction(tx1, walletA.public_key)
print("DOUBLE SPENDING TEST:", msg)


# ---------------- TAMPER TEST ----------------
tx2 = Transaction(walletA, walletB, 20)
tx2.sign_transaction(walletA)

# Modify amount AFTER signing
tx2.amount = 999

result, msg = system.process_transaction(tx2, walletA.public_key)
print("TAMPERED TRANSACTION:", msg)


# ---------------- EDGE CASES ----------------

# Zero balance
tx3 = Transaction(walletA, walletB, 1000)
tx3.sign_transaction(walletA)

result, msg = system.process_transaction(tx3, walletA.public_key)
print("INSUFFICIENT BALANCE:", msg)


# Corrupted transaction ID
tx4 = Transaction(walletA, walletB, 10)
tx4.sign_transaction(walletA)
tx4.transaction_id = "fake_id"

result, msg = system.process_transaction(tx4, walletA.public_key)
print("CORRUPTED TX ID:", msg)