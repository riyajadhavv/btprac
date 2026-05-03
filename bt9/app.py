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
print("\nVerification:\n", df[["timestamp", "verify"]])

# 🔹 AI MODEL (Anomaly Detection)
# Convert status to numeric
df["status_num"] = df["status"].apply(lambda x: 1 if x == "failed" else 0)

model = IsolationForest(contamination=0.3)
df["anomaly"] = model.fit_predict(df[["status_num"]])

print("\nAnomaly Detection:\n", df[["timestamp", "event", "status", "anomaly"]])