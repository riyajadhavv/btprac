# ==========================================
# ASSIGNMENT 9: AI-Powered Threat Detection
# Run this entire cell in Google Colab
# ==========================================
#
# pip install scikit-learn pandas

import hashlib
import json
import time
import pandas as pd
from sklearn.ensemble import IsolationForest

print("==========================================")
print(" 1. LOG GENERATION & SCHEMA DEFINITION")
print("==========================================")
# Schema: timestamp, event_type, source_ip, failed_attempts
raw_logs = [
    {"timestamp": time.time(), "event_type": "login", "source_ip": "192.168.1.10", "failed_attempts": 0},
    {"timestamp": time.time(), "event_type": "login", "source_ip": "192.168.1.11", "failed_attempts": 1},
    {"timestamp": time.time(), "event_type": "data_transfer", "source_ip": "192.168.1.12", "failed_attempts": 0},
    # ANOMALY: Brute force login attempt
    {"timestamp": time.time(), "event_type": "login", "source_ip": "10.0.0.99", "failed_attempts": 45},
    {"timestamp": time.time(), "event_type": "login", "source_ip": "192.168.1.14", "failed_attempts": 0}
]
print(f"Generated {len(raw_logs)} logs.\n")


print("==========================================")
print(" 2. CRYPTOGRAPHIC HASHING & BLOCKCHAIN")
print("==========================================")
def hash_log(log_entry):
    """Creates a SHA-256 hash of a log dictionary."""
    log_string = json.dumps(log_entry, sort_keys=True).encode()
    return hashlib.sha256(log_string).hexdigest()

blockchain_ledger = [] # Simulating our immutable on-chain storage

for log in raw_logs:
    log_hash = hash_log(log)
    blockchain_ledger.append(log_hash)
    print(f"Stored Hash: {log_hash[:15]}... | IP: {log['source_ip']}")


print("\n==========================================")
print(" 3. VERIFICATION & TAMPER DETECTION")
print("==========================================")
def verify_logs(logs, ledger):
    for i, log in enumerate(logs):
        if hash_log(log) != ledger[i]:
            print(f" [ALERT] Tampering detected at index {i}!")
            return False
    print(" [SUCCESS] All off-chain logs match on-chain hashes. Data is pristine.")
    return True

print("Checking original logs:")
verify_logs(raw_logs, blockchain_ledger)

print("\nSimulating a Hacker Altering a Log (Changing failed attempts to 0)...")
raw_logs[3]["failed_attempts"] = 0
verify_logs(raw_logs, blockchain_ledger)

# Revert the tamper so we can train our AI properly
raw_logs[3]["failed_attempts"] = 45


print("\n==========================================")
print(" 4. AI-POWERED THREAT DETECTION (Isolation Forest)")
print("==========================================")
# Convert logs to a pandas DataFrame for the AI
df = pd.DataFrame(raw_logs)

# Map string event types to numbers so the AI can process them
df['event_type_encoded'] = df['event_type'].astype('category').cat.codes

# Features for the AI to analyze
features = df[['event_type_encoded', 'failed_attempts']]

# Initialize and train the Isolation Forest model
# Contamination is the expected percentage of anomalies
model = IsolationForest(contamination=0.2, random_state=42)
df['anomaly_score'] = model.fit_predict(features)

# -1 means anomaly, 1 means normal
for index, row in df.iterrows():
    if row['anomaly_score'] == -1:
        status = " THREAT DETECTED (Anomaly)"
    else:
        status = " Normal"

    print(f"IP: {row['source_ip']:<15} | Fails: {row['failed_attempts']:<2} | Status: {status}")