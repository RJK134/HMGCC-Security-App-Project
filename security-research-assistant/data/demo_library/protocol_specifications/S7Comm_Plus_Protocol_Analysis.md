# S7CommPlus Protocol Analysis - Reverse Engineering Notes for ICS Security Researchers

**Document Classification:** OFFICIAL  
**Author:** ICS Security Research Team  
**Last Updated:** 2026-03-25  
**Revision:** 1.3  
**Applicable System:** AMS-500 Additive Manufacturing System (Siemens S7-1500 PLC, FW V21.9)  

---

## 1. Background

S7CommPlus (also referred to as S7Comm-Plus or S7-1500 protocol) is the proprietary communication protocol used by Siemens S7-1200 (firmware >= V4.0) and S7-1500 PLCs. It replaces the legacy S7Comm protocol used by S7-300 and S7-400 series controllers.

Unlike the legacy S7Comm protocol, which has been extensively documented by the security research community and lacks any cryptographic protection, S7CommPlus introduces integrity verification and anti-replay mechanisms. However, these protections have been the subject of significant security research, and several weaknesses have been identified, particularly on older firmware versions.

This document records protocol-level findings from analysis of S7CommPlus traffic on the AMS-500 system's Siemens S7-1500 CPU 1516-3 PN/DP (firmware version V21.9, hardware version 6ES7516-3AN02-0AB0).

---

## 2. Transport Layer

### 2.1 ISO on TCP (RFC 1006)

S7CommPlus operates over ISO on TCP, encapsulating ISO 8073 (COTP - Connection-Oriented Transport Protocol) within TCP connections on **port 102**.

The protocol stack from bottom to top:

```
TCP (port 102)
  └── TPKT (RFC 1006) -- 4-byte header: version (0x03), reserved (0x00), length (2 bytes)
       └── COTP (ISO 8073) -- Connection Request (CR), Connection Confirm (CC), Data Transfer (DT)
            └── S7CommPlus PDU
```

### 2.2 COTP Connection Establishment

Before any S7CommPlus exchange, a COTP connection is established:

1. **CR (Connection Request)** -- Client sends COTP CR with source reference, destination reference (0x0000), and TPDU size parameter. The `src-tsap` and `dst-tsap` fields encode the rack and slot of the target CPU.
2. **CC (Connection Confirm)** -- Server responds with COTP CC, confirming the connection and returning a source reference.

For S7-1500 PLCs, the dst-tsap is typically `0x0102` (rack 0, slot 1), though the slot number may vary in multi-CPU configurations.

### 2.3 Traffic Characteristics

On the AMS-500 network, S7CommPlus traffic on port 102 was observed between:

- TIA Portal engineering workstation (10.10.20.10) and PLC (10.10.20.1) -- programme download, monitoring.
- HMI panel (10.10.20.5) and PLC (10.10.20.1) -- process data read, alarm subscription.
- OPC UA server (internal on PLC) and PLC CPU -- internal communication, not visible on network.

---

## 3. S7CommPlus PDU Structure

S7CommPlus PDUs are carried within COTP Data Transfer (DT) frames. The PDU structure differs significantly from legacy S7Comm.

### 3.1 Protocol Identification

The first byte of the S7CommPlus payload is the protocol ID:

| Value | Protocol |
|-------|----------|
| 0x32 | S7Comm (legacy, S7-300/400) |
| 0x72 | S7CommPlus (S7-1200/1500) |

All traffic to the AMS-500's S7-1500 uses protocol ID `0x72`.

### 3.2 PDU Header

The S7CommPlus header following the protocol ID byte:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 1 | Protocol ID | 0x72 |
| 1 | 1 | PDU Type | See Section 3.3 |
| 2 | 2 | Data Length | Length of remaining data |
| 4 | 2 | Sequence Number | Monotonically increasing per session |
| 6 | var | Integrity Part | Session-dependent integrity data |

### 3.3 PDU Types

| Type | Name | Direction | Purpose |
|------|------|-----------|---------|
| 0x01 | Request | Client -> PLC | Service request from engineering tool or HMI |
| 0x02 | Response | PLC -> Client | Response to a request |
| 0x03 | Notification | PLC -> Client | Asynchronous event (alarm, status change) |
| 0x04 | Keep-Alive | Bidirectional | Session keep-alive |

### 3.4 Function Codes (Opcode)

Within S7CommPlus requests and responses, the function code specifies the operation:

| Code | Function | Description | Security Relevance |
|------|----------|-------------|-------------------|
| 0x04B0 | SetMultiVariables | Write values to PLC memory | Direct process manipulation |
| 0x04A0 | GetMultiVariables | Read values from PLC memory | Process data exfiltration |
| 0x04CA | SetVariable | Write a single variable | Direct process manipulation |
| 0x04BA | GetVariable | Read a single variable | Data exfiltration |
| 0x0456 | BeginDownload | Start block download to PLC | Programme modification |
| 0x0457 | Download | Transfer block data | Programme modification |
| 0x0458 | EndDownload | Finalise block download | Programme modification |
| 0x044C | StartUpload | Start block upload from PLC | Programme extraction |
| 0x044D | Upload | Transfer block data from PLC | IP theft |
| 0x044E | EndUpload | Finalise block upload | IP theft |
| 0x0428 | PLCStop | Transition PLC to STOP mode | Denial of service |
| 0x0429 | PLCStart | Transition PLC to RUN mode | Restart after attack |
| 0x04F0 | Explore | Browse PLC symbol table | Reconnaissance |
| 0x0480 | CreateObject | Create a software object in PLC | Persistent modification |
| 0x0482 | DeleteObject | Delete a software object | Programme destruction |

---

## 4. Session Establishment and Anti-Replay Mechanism

### 4.1 Session Handshake

S7CommPlus session establishment (after COTP connection) involves a multi-step handshake:

1. **Client Hello** -- Client sends an initial request containing its protocol version, supported features, and a client challenge (random nonce).
2. **Server Hello** -- PLC responds with its protocol version, supported features, server challenge (random nonce), and public key information.
3. **Key Exchange** -- Client and server perform a key exchange (ECDH on firmware >= V2.0) to derive symmetric session keys.
4. **Authentication** -- Client proves knowledge of a password or certificate to gain access at a specific protection level.

### 4.2 Protection Levels

S7-1500 PLCs support configurable protection levels:

| Level | Name | Access | AMS-500 Config |
|-------|------|--------|----------------|
| 1 | No protection | Full access without password | No |
| 2 | Write protection | Read without password; write requires password | No |
| 3 | Read/Write protection | Both read and write require password | Yes (configured) |
| 4 | Full protection | No access without TIA Portal certificate | No |

**AMS-500 finding:** The PLC is configured at Protection Level 3, but the password (`AMS500plc`) was found documented in a plaintext configuration file on the engineering workstation at `C:\TIA_Projects\AMS500\connection_config.ini`. Additionally, the HMI panel stores the PLC password in its WinCC configuration, which is accessible to any user with access to the HMI's filesystem.

### 4.3 Integrity Mechanism

Starting with S7-1500 firmware V2.0, S7CommPlus includes an integrity mechanism to detect message modification and replay:

- Each message includes a **session key-derived HMAC** (SHA-256 based) computed over the PDU payload and a per-message counter.
- The counter is derived from the session sequence number and a session-specific offset negotiated during the key exchange.
- Messages with incorrect HMACs or out-of-sequence counters are rejected.

This mechanism is significantly stronger than the legacy S7Comm protocol, which used no integrity protection whatsoever.

### 4.4 Known Weaknesses

Despite the improvements, several weaknesses have been documented:

**4.4.1 Firmware < V2.0: No Integrity Protection**

S7-1500 PLCs running firmware prior to V2.0 use a version of S7CommPlus without the HMAC integrity mechanism. On these devices, the "anti-replay" protection consists of a simple sequence number check that can be predicted and spoofed. These firmware versions are vulnerable to:

- Full session hijacking.
- Man-in-the-middle modification of read/write requests.
- Replay of recorded sessions.

**AMS-500 relevance:** The AMS-500's S7-1500 runs firmware V21.9, which includes the HMAC integrity mechanism. However, if the firmware is ever downgraded (e.g., during maintenance using an older TIA Portal version), the protections would be lost.

**4.4.2 Hardcoded Cryptographic Keys (CVE-2022-38465)**

Research by Claroty Team82 (published October 2022) revealed that S7-1200 and S7-1500 PLCs use a **global private key** embedded in the firmware for protecting configuration and programme passwords. This key is identical across all CPUs of the same type and firmware version. An attacker who extracts this key (via firmware dump) can:

- Decrypt PLC protection passwords offline.
- Derive session keys and forge authenticated messages.
- Bypass all protection levels without the legitimate password.

Siemens addressed this in firmware V3.0.1 by introducing individual per-device keys. The AMS-500's firmware V21.9 predates this fix and is vulnerable.

**4.4.3 Session Key Derivation Weakness**

On firmware versions between V2.0 and V2.9, the ECDH key exchange uses a static server key pair. While the client's ephemeral key provides some forward secrecy, the static server key means that an attacker who compromises the server private key (via the hardcoded key issue in CVE-2022-38465) can derive all past and future session keys for any recorded traffic.

**4.4.4 No Mutual Authentication by Default**

The default configuration authenticates the client to the server (password or certificate), but the client does not authenticate the server. This enables man-in-the-middle attacks where an attacker impersonates the PLC to the engineering workstation or HMI.

---

## 5. Comparison with Legacy S7Comm

| Feature | S7Comm (S7-300/400) | S7CommPlus (S7-1200/1500) |
|---------|---------------------|---------------------------|
| Protocol ID | 0x32 | 0x72 |
| Transport | ISO on TCP, port 102 | ISO on TCP, port 102 |
| Encryption | None | Session-key encrypted payload (FW >= V2.0) |
| Integrity | None | HMAC-SHA256 (FW >= V2.0) |
| Anti-replay | None | Sequence counter with session offset |
| Authentication | TSAP-level only (trivial) | Password or certificate per protection level |
| Programme protection | Password in cleartext within block header | Encrypted with global/individual key |
| Known attack tools | snap7, s7-brute, Metasploit modules, PLCInject | Limited (requires session key derivation) |
| Firmware extraction | Via upload function codes | Restricted by protection level |
| Session hijacking | Trivial (forge packets matching seq number) | Difficult (requires HMAC key) unless FW < V2.0 |

**Key difference for assessment:** Legacy S7Comm devices (S7-300, S7-400, and S7-1200 with firmware < V4.0) remain trivially exploitable using open-source tools. S7CommPlus on current firmware is substantially harder to attack at the protocol level, but the hardcoded key vulnerability (CVE-2022-38465) undermines the entire cryptographic model on firmware < V3.0.1.

---

## 6. Traffic Analysis with Wireshark

### 6.1 Capture Configuration

```
# Capture filter for S7CommPlus traffic
tcp port 102

# Display filter for S7CommPlus only (exclude S7Comm)
s7comm-plus

# Filter by specific function code (e.g., PLC Stop)
s7comm-plus.opcode == 0x0428

# Filter write operations
s7comm-plus.opcode == 0x04b0 || s7comm-plus.opcode == 0x04ca

# Filter programme download
s7comm-plus.opcode == 0x0456 || s7comm-plus.opcode == 0x0457 || s7comm-plus.opcode == 0x0458
```

### 6.2 Decoding Limitations

Wireshark's S7CommPlus dissector (as of version 4.2) provides partial decoding of the protocol. Key limitations:

- **Encrypted payloads** on firmware >= V2.0 cannot be decoded without the session key.
- **Object identifiers** in Explore and CreateObject responses use Siemens-internal numbering that is not publicly documented.
- **Variable addressing** in GetMultiVariables/SetMultiVariables uses a symbolic addressing scheme that requires the PLC's symbol table for interpretation.

### 6.3 What Can Be Observed in Encrypted Sessions

Even with encrypted payloads, traffic analysis reveals:

- **Connection timing** -- when engineering tools connect and disconnect.
- **Message sizes** -- large transfers (programme download) vs. small transfers (variable read).
- **Function code patterns** -- the opcode field is in the cleartext header on some firmware versions.
- **Session frequency** -- how often the HMI reads data (polling interval).

---

## 7. Attack Scenarios Against AMS-500

### 7.1 Credential Recovery

1. Obtain the global cryptographic key for S7-1500 CPU 1516 FW V21.9 (published in Claroty's research or extracted from firmware dump).
2. Capture the S7CommPlus session handshake between the TIA Portal workstation and the PLC.
3. Derive the session keys using the global key and the captured key exchange.
4. Decrypt the PLC protection password from the session authentication phase.
5. Use the recovered password to establish an authenticated session and gain full read/write access.

### 7.2 Programme Modification

1. Establish an authenticated session (using recovered credentials or the plaintext password from the configuration file).
2. Upload the current programme blocks (OB1, FB1-FB50, FC1-FC30, DB1-DB999) for analysis.
3. Modify target blocks (e.g., alter process parameters in DB100, add a backdoor in OB35).
4. Download the modified blocks to the PLC.
5. The PLC will execute the modified programme without any code-signing verification.

**Note:** S7-1500 firmware V21.9 does not support programme code signing. Code signing was introduced in firmware V3.0.1 for CPU types that support it. The AMS-500's CPU 1516-3 PN/DP does not support code signing even with updated firmware.

### 7.3 Denial of Service

1. Send a PLCStop (0x0428) command. On Protection Level 3, this requires the PLC password, but as noted, the password is recoverable.
2. Alternatively, flood port 102 with malformed COTP connection requests to exhaust the PLC's connection table (maximum 32 concurrent COTP connections on S7-1500).
3. Exploit CVE-2023-44373 (improper input validation) to crash the PLC web server, potentially affecting the CPU.

---

## 8. Recommendations for AMS-500

1. **Upgrade firmware to V3.0.1 or later** to obtain individual per-device cryptographic keys and eliminate the CVE-2022-38465 vulnerability. Verify hardware compatibility before upgrading.
2. **Change the PLC protection password** and remove all plaintext copies from the engineering workstation and HMI configuration files.
3. **Enable Protection Level 4** (full protection with TIA Portal certificates) if the operational workflow permits.
4. **Restrict TCP port 102 access** at the network firewall level to only the TIA Portal engineering workstation and HMI panel.
5. **Monitor S7CommPlus traffic** for unauthorised connections, programme download operations, and PLCStop commands.
6. **Implement network segmentation** between the PLC network (10.10.20.0/24) and other OT subnets.
7. **Conduct regular programme integrity checks** by uploading the PLC programme and comparing it against the authorised baseline stored offline.

---

## 9. References

- Biham, E. et al., "Rogue7: Rogue Engineering-Station Attacks on S7 Simatic PLCs" (Black Hat USA 2019)
- Claroty Team82, "Evil PLC Attack: Weaponizing PLCs" (2022)
- Claroty Team82, "Breaking the S7-1500 Cryptographic Keys" (CVE-2022-38465, October 2022)
- Siemens ProductCERT Advisory SSA-568427 (CVE-2022-38465)
- Wiens, K., "S7CommPlus Wireshark Dissector" (GitHub, 2023)
- Nozomi Networks, "S7Comm and S7CommPlus Protocol Guide" (2021)

---

*This document is part of the AMS-500 security assessment working library. Do not distribute outside the assessment team.*
