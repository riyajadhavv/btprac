# Cybersecurity & Infrastructure Assignments

---

## Assignment 7: Deploying Public Key Infrastructure Based Identity

### Objectives
* To design and deploy a hierarchical Public Key Infrastructure (PKI) using a Root and Intermediate Certificate Authority (CA).
* To generate, sign, and manage X.509 end-entity certificates for both client and server identities.
* To demonstrate certificate-based authentication and identity validation through a mutual TLS (mTLS) simulation.
* To implement and document the certificate lifecycle, including issuance, renewal, and revocation mechanisms.
* To analyze the security risks associated with misconfigured PKI and define strategies for private key protection.

### Theory

**Public Key Infrastructure (PKI)**
PKI is a comprehensive framework of roles, policies, hardware, and software required to create, manage, distribute, use, store, and revoke digital certificates. It uses public-key cryptography to secure communications and establish identity over untrusted networks.

**The Certificate Authority (CA) Hierarchy**
A robust PKI relies on a Chain of Trust to delegate security:
* **Root CA:** The ultimate trust anchor in a PKI. It issues a self-signed certificate. Because its compromise would invalidate the entire system, it is typically kept offline in a highly secure environment.
* **Intermediate CA:** A subordinate authority whose certificate is signed by the Root CA. It acts as a proxy to issue end-entity certificates, protecting the Root CA from direct exposure to the network.

**Certificate-Based Authentication (Mutual TLS)**
Standard TLS (HTTPS) only authenticates the server to the client. In highly secure infrastructures, mutual TLS (mTLS) is used. In this model, the server presents its certificate to the client, and the client also presents its certificate to the server. Both parties use the PKI Chain of Trust to verify each other's identities before exchanging data.

### Practical Deployment (Ubuntu / Linux / WSL)

Run these commands in a single folder on your computer to generate your PKI environment.

**1. Deploy the Root CA**
We generate a private key and a self-signed Root certificate valid for 10 years.
```bash
# Generate Root CA Private Key and Certificate
openssl req -x509 -newkey rsa:4096 -days 3650 -nodes \
  -keyout rootCA.key -out rootCA.crt \
  -subj "/C=US/O=MyLab/CN=LabRootCA" \
  -addext "basicConstraints=critical,CA:TRUE"
```

**2. Configure the Intermediate CA**
We generate a key, create a Certificate Signing Request (CSR), and have the Root CA sign it.
```bash
# Generate Intermediate CA Private Key and CSR
openssl req -newkey rsa:4096 -nodes \
  -keyout intCA.key -out intCA.csr \
  -subj "/C=US/O=MyLab/CN=LabIntermediateCA"

# Root CA signs the Intermediate CA CSR
openssl x509 -req -in intCA.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial \
  -out intCA.crt -days 1825 \
  -extfile <(echo -e "basicConstraints=critical,CA:TRUE\nkeyUsage=critical,keyCertSign,cRLSign")
```

**3. Generate End-Entity Certificates (Server & Client)**
The Intermediate CA will issue one certificate for a web server, and one for a client user.
```bash
# Web Server: Key, CSR, and Certificate
openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj "/C=US/O=MyLab/CN=localhost"
openssl x509 -req -in server.csr -CA intCA.crt -CAkey intCA.key -CAcreateserial -out server.crt -days 365

# Client: Key, CSR, and Certificate
openssl req -newkey rsa:2048 -nodes -keyout client.key -out client.csr -subj "/C=US/O=MyLab/CN=LabClient"
openssl x509 -req -in client.csr -CA intCA.crt -CAkey intCA.key -CAcreateserial -out client.crt -days 365
```

**4. Demonstration & Validation (mTLS)**
To demonstrate certificate-based authentication and show how identity is validated, we will set up a quick secure web server that requires a client certificate.

*Step 1: Start the HTTPS Server*
Open a terminal and start a built-in OpenSSL web server that requires client authentication:
```bash
# This tells the server to use the server cert/key, but also ask the client for a cert trusted by our PKI
openssl s_server -accept 4433 -cert server.crt -key server.key -CAfile intCA.crt -Verify 1
```

*Step 2: Connect with the Client*
Open a second terminal window and use curl to connect to the server, providing the client certificate:
```bash
# We pass the client cert/key to prove who we are, and the rootCA to verify the server
curl -v --cacert rootCA.crt --cert client.crt --key client.key https://localhost:4433
```

### Conclusion
In this assignment, a fully functional Public Key Infrastructure was successfully designed and deployed within a simulated environment. By establishing a Root CA and an Intermediate CA, a secure Chain of Trust was created to issue valid certificates for a web server and a client. The practical deployment successfully demonstrated certificate-based mutual authentication, proving that both entities could reliably verify each other's cryptographic identities.

---