import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


# ---------------- WALLET CLASS ----------------
class Wallet:
    def __init__(self):
        # Generate private key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # Generate public key
        self.public_key = self.private_key.public_key()

        # Create address (hash of public key)
        self.address = self.generate_address()

    def generate_address(self):
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return str(hash(public_bytes))

    # SIGN TRANSACTION
    def sign_transaction(self, transaction_data):
        message = json.dumps(transaction_data).encode()

        signature = self.private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature

    # VERIFY TRANSACTION
    def verify_transaction(self, transaction_data, signature, sender_public_key):
        message = json.dumps(transaction_data).encode()

        try:
            sender_public_key.verify(
                signature,
                message,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False


# ---------------- TRANSACTION ----------------
def create_transaction(sender, receiver, amount):
    return {
        "sender": sender.address,
        "receiver": receiver.address,
        "amount": amount
    }


# ---------------- TESTING ----------------

# Create wallets
wallet1 = Wallet()
wallet2 = Wallet()

print("Wallet 1 Address:", wallet1.address)
print("Wallet 2 Address:", wallet2.address)

# Create transaction
tx = create_transaction(wallet1, wallet2, 100)

# Sign transaction
signature = wallet1.sign_transaction(tx)

# Verify transaction (VALID)
is_valid = wallet1.verify_transaction(tx, signature, wallet1.public_key)
print("\nVALID TRANSACTION:", "Success" if is_valid else "Failure")


# ---------------- TAMPER TEST ----------------

# Modify transaction
tampered_tx = tx.copy()
tampered_tx["amount"] = 999

is_valid = wallet1.verify_transaction(tampered_tx, signature, wallet1.public_key)
print("TAMPERED TRANSACTION:", "Success" if is_valid else "Failure")


# ---------------- MULTIPLE WALLET TEST ----------------

wallet3 = Wallet()

tx2 = create_transaction(wallet2, wallet3, 50)
signature2 = wallet2.sign_transaction(tx2)

is_valid2 = wallet2.verify_transaction(tx2, signature2, wallet2.public_key)
print("MULTI-WALLET TEST:", "Success" if is_valid2 else "Failure")


# ---------------- EDGE CASES ----------------

# Empty transaction
empty_tx = {}
signature_empty = wallet1.sign_transaction(empty_tx)

print("EMPTY TX:", "Success" if wallet1.verify_transaction(empty_tx, signature_empty, wallet1.public_key) else "Failure")

# Invalid key test
fake_wallet = Wallet()
print("INVALID KEY TEST:", "Success" if wallet1.verify_transaction(tx, signature, fake_wallet.public_key) else "Failure")

# Corrupted signature
corrupt_signature = signature[:-1] + b'0'
print("CORRUPTED SIGNATURE:", "Success" if wallet1.verify_transaction(tx, corrupt_signature, wallet1.public_key) else "Failure")