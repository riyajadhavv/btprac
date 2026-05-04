# pip install scikit-learn pandas
import hashlib
import pandas as pd
from sklearn.ensemble import IsolationForest

# 🔹 Load logs
df = pd.read_csv("logs.csv")

# 🔹 Function to hash logs
def hash_log(row):
    log_string = str(row.values)
    return hashlib.sha256(log_string.encode()).hexdigest()

# 🔹 Create hashes
df["hash"] = df.apply(hash_log, axis=1)

# 🔹 Store hashes (simulate blockchain)
with open("hashes.txt", "w") as f:
    for h in df["hash"]:
        f.write(h + "\n")

print("Hashes stored on blockchain (simulated)")

# 🔹 VERIFY logs
with open("hashes.txt", "r") as f:
    stored_hashes = f.read().splitlines()

df["verify"] = df["hash"] == stored_hashes
print("\n🔍 Verification:\n", df[["timestamp", "verify"]])

# =========================
# IMPROVED AI MODEL
# =========================

# Convert status to numeric
df["status_num"] = df["status"].apply(lambda x: 1 if x == "failed" else 0)

# 🔹 Feature Engineering (IMPORTANT)
# Count failed attempts per user
df["fail_count"] = df.groupby("source")["status_num"].transform("sum")

# Encode event type
df["event_num"] = df["event"].apply(lambda x: 1 if x == "login" else 0)

# 🔹 Use multiple features
features = df[["status_num", "fail_count", "event_num"]]

# 🔹 Train model
model = IsolationForest(contamination=0.2, random_state=42)
df["anomaly"] = model.fit_predict(features)

# 🔹 Show all results
print("\nFull Results:\n", df[["timestamp", "event", "source", "status", "fail_count", "anomaly"]])

# 🔹 Highlight anomalies
print("\n Detected Anomalies:")
print(df[df["anomaly"] == -1][["timestamp", "event", "source", "status", "fail_count"]])