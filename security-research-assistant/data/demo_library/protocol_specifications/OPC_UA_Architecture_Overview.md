# OPC Unified Architecture (OPC UA) - Security Research Overview

**Document Classification:** OFFICIAL  
**Author:** ICS Security Research Team  
**Last Updated:** 2026-03-18  
**Revision:** 2.4  
**Applicable System:** AMS-500 Additive Manufacturing System  

---

## 1. Introduction

OPC Unified Architecture (OPC UA, IEC 62541) is the dominant machine-to-machine communication protocol in modern industrial automation. Unlike its predecessor OPC Classic (COM/DCOM-based, Windows-only), OPC UA is platform-independent, service-oriented, and provides built-in security primitives. It is increasingly deployed as the primary supervisory data-exchange layer in manufacturing execution systems, SCADA, and industrial IoT environments.

On the AMS-500 additive manufacturing system under assessment, OPC UA serves as the northbound interface between the Siemens S7-1500 PLC (firmware V21.9) and the supervisory HMI/MES layer. The PLC exposes process variables, alarms, and diagnostic data through an embedded OPC UA server (Siemens OPC UA S7-1500 CP module) on TCP port 4840. A secondary OPC UA server runs on the Windows-based HMI workstation, aggregating data from the PLC and the EtherCAT motion subsystem for upstream consumption by the plant historian and quality management system.

This document provides a protocol-level overview for ICS security researchers preparing to assess OPC UA deployments in operational technology environments.

---

## 2. Transport Protocols

OPC UA defines three transport protocol bindings, each with distinct security characteristics.

### 2.1 OPC UA TCP (opc.tcp://)

The native binary transport operates over TCP, typically on port 4840 (IANA-registered). Messages use the UA Binary encoding, which is compact and optimised for embedded devices with limited processing power. This is the transport used by the S7-1500's embedded OPC UA server on the AMS-500.

The connection sequence is:

1. **Hello/Acknowledge** -- The client sends a Hello message specifying buffer sizes and endpoint URL. The server responds with an Acknowledge containing negotiated parameters.
2. **OpenSecureChannel** -- Establishes a security context (see Section 5).
3. **CreateSession / ActivateSession** -- Application-layer authentication.
4. **Service requests** -- Browse, Read, Write, Call, Subscribe, etc.

Wire format: each message begins with a 4-byte message type indicator (`MSG`, `OPN`, `CLO`, `HEL`, `ACK`, `ERR`), followed by a chunk type byte (`F` for final, `C` for continuation, `A` for abort), a 4-byte message size, and the security header.

**Security note:** The binary encoding is not self-describing. Without a schema or NodeSet XML, intercepted traffic cannot be trivially decoded. However, tools such as Wireshark (with the OPC UA dissector) and the open-source `opcua-client-gui` can decode traffic given access to the endpoint's security policy.

### 2.2 HTTPS Transport

OPC UA can tunnel service requests over HTTPS (typically port 443 or 4443). Messages are encoded using either UA Binary or UA XML (SOAP). The HTTPS binding leverages TLS for transport security, making it suitable for traversing IT/OT network boundaries where firewalls and proxies are configured for HTTPS inspection.

The AMS-500 HMI workstation exposes an HTTPS-based OPC UA endpoint for the MES integration. During the initial assessment, this endpoint was found listening on TCP 4443 with a self-signed certificate issued to `CN=AMS500-HMI.local`.

### 2.3 WebSocket Transport (WSS)

Added in OPC UA 1.04, the WebSocket Secure transport (`opc.wss://`) allows browser-based clients and web dashboards to consume OPC UA services. This transport encapsulates UA Binary messages inside WebSocket frames, with TLS providing transport security.

The AMS-500 does not currently deploy WebSocket transport, but the HMI vendor's documentation references it as a planned feature in the next software update.

---

## 3. Message Types and Service Sets

OPC UA organises its functionality into Service Sets, each containing related request/response message pairs.

### 3.1 SecureChannel Services

| Message | Purpose |
|---------|---------|
| OpenSecureChannel | Establishes or renews a security context. Contains the client nonce, requested security token lifetime, and the security mode/policy. |
| CloseSecureChannel | Terminates the security context and invalidates the security token. |

The OpenSecureChannel request carries the client certificate (if MessageSecurityMode is Sign or SignAndEncrypt) and a client nonce used to derive symmetric keys. The server responds with a server nonce and a SecurityTokenId used to identify the channel in subsequent messages.

**Attack surface:** If the security policy is `None` (no signing, no encryption), the entire channel operates in cleartext. An attacker on the network can read and modify all subsequent messages. On the AMS-500, the PLC's OPC UA server was observed accepting connections with SecurityPolicy `None` alongside the configured policy `Basic256Sha256`, meaning a downgrade attack is possible.

### 3.2 Session Services

| Message | Purpose |
|---------|---------|
| CreateSession | Requests a new application-layer session. Client provides application description and a session nonce. |
| ActivateSession | Authenticates the user (see Section 5.2). A session can be activated multiple times to change user identity. |
| CloseSession | Terminates the session and releases server resources. |

Sessions are bound to SecureChannels but can be transferred between channels (session portability). This has security implications: if an attacker can obtain a valid session token and authentication token, they can bind the session to their own SecureChannel.

### 3.3 View Services (Browse / BrowseNext)

The Browse service enumerates the server's address space. Starting from a known node (typically the Root folder, NodeId `i=84`, or the Objects folder, `i=85`), a client recursively discovers all exposed objects, variables, methods, and their relationships.

**Security implication:** On the AMS-500, unauthenticated Browse access reveals the full PLC tag namespace, including internal variable names such as `AMS500.Laser.PowerSetpoint`, `AMS500.Motion.AxisX.Position`, `AMS500.Safety.EStopState`, and `AMS500.Recipe.ActiveRecipeID`. This leaks significant operational intelligence about the manufacturing process.

### 3.4 Attribute Services (Read / Write)

| Message | Purpose |
|---------|---------|
| Read | Reads one or more attributes of one or more nodes (value, data type, timestamp, status code). |
| Write | Writes one or more values. Server validates against the data type and access level. |

Read and Write are the most frequently used services in supervisory data exchange. On the AMS-500, the Write service is used by the MES to push recipe parameters to the PLC (e.g., laser power, scan speed, layer thickness).

**Critical finding:** During testing, it was confirmed that the OPC UA server on the AMS-500 PLC allows Write access to process-critical variables (including `AMS500.Laser.PowerSetpoint` and `AMS500.Motion.FeedRate`) when authenticated with the default `admin` account. No write confirmation or operator approval workflow exists at the OPC UA layer.

### 3.5 Subscription and MonitoredItem Services

The Subscription model allows clients to receive asynchronous notifications when monitored values change, rather than polling. The client creates a Subscription with a publishing interval, then adds MonitoredItems to it.

| Message | Purpose |
|---------|---------|
| CreateSubscription | Creates a subscription context with publishing parameters. |
| CreateMonitoredItems | Adds nodes to the subscription with sampling intervals, filters, and queue sizes. |
| Publish | Client sends Publish requests; server responds with notifications when data changes. |
| Republish | Re-requests a missed notification sequence number. |

Subscriptions maintain state on the server. A large number of subscriptions with aggressive sampling intervals can exhaust server resources -- this is a viable denial-of-service vector against embedded OPC UA servers with limited memory.

### 3.6 Method Services (Call)

The Call service invokes methods defined in the server's address space. On the AMS-500, exposed methods include `StartBuild()`, `PauseBuild()`, `AbortBuild()`, and `LoadRecipe(RecipeID)`. These methods have significant operational impact and should be protected with role-based access control.

---

## 4. Address Space Structure

The OPC UA address space is a directed graph of nodes connected by references. Every item in the server is represented as a node with a unique NodeId.

### 4.1 Node Classes

| Node Class | Description | AMS-500 Examples |
|------------|-------------|------------------|
| **Object** | Represents a physical or logical entity. | `AMS500`, `Laser`, `BuildChamber`, `MotionSystem` |
| **Variable** | Holds a value with a data type. | `LaserPower` (Float, W), `ChamberTemp` (Float, degC), `BuildProgress` (UInt16, %) |
| **Method** | An invocable operation on an object. | `StartBuild()`, `LoadRecipe(UInt32)` |
| **ObjectType** | Defines the structure of an Object (template). | `AdditiveManufacturingMachineType` |
| **VariableType** | Defines the structure of a Variable. | `ProcessParameterType` |
| **ReferenceType** | Defines semantic relationships between nodes. | `HasComponent`, `Organizes`, `HasProperty` |
| **DataType** | Defines a data type used by Variables. | `RecipeParameterStruct` |
| **View** | A subset of the address space for a particular perspective. | `OperatorView`, `MaintenanceView` |

### 4.2 Namespace Structure

The AMS-500 OPC UA server exposes three namespaces:

- **Namespace 0** (`http://opcfoundation.org/UA/`) -- Standard OPC UA nodes.
- **Namespace 1** (`urn:siemens:s7-1500:opcua`) -- Siemens PLC-specific extensions.
- **Namespace 2** (`http://ams500.vendor.local/ua/`) -- AMS-500 application-specific nodes.

Namespace 2 contains the full process model: build chamber sensors, laser subsystem, motion axes, recipe management, and alarm conditions.

---

## 5. Security Model

### 5.1 Application-Layer Security (SecureChannel)

OPC UA security operates at two layers. The transport layer (SecureChannel) provides message-level security using X.509 certificates.

**MessageSecurityMode** options:

- `None` -- No signing or encryption. Traffic is cleartext.
- `Sign` -- Messages are signed but not encrypted. Integrity is protected; confidentiality is not.
- `SignAndEncrypt` -- Messages are both signed and encrypted. Recommended for production.

**SecurityPolicy** defines the cryptographic algorithms:

| Policy URI | Algorithms | Status |
|-----------|------------|--------|
| `None` | None | Insecure, must be disabled |
| `Basic128Rsa15` | AES-128-CBC, RSA-PKCS1.5, SHA-1 | Deprecated (SHA-1) |
| `Basic256` | AES-256-CBC, RSA-OAEP, SHA-1 | Deprecated (SHA-1) |
| `Basic256Sha256` | AES-256-CBC, RSA-OAEP, SHA-256 | Current minimum recommended |
| `Aes128_Sha256_RsaOaep` | AES-128-CBC, RSA-OAEP, SHA-256 | Acceptable |
| `Aes256_Sha256_RsaPss` | AES-256-CBC, RSA-PSS, SHA-256 | Best available |

**AMS-500 finding:** The PLC's OPC UA server advertises both `None` and `Basic256Sha256` security policies. The `None` policy must be disabled to prevent downgrade attacks. The server's application certificate uses a 2048-bit RSA key, which is acceptable but should be upgraded to 4096-bit or ECC P-384 at the next maintenance window.

### 5.2 User Authentication

After the SecureChannel is established, the user authenticates via the ActivateSession service. OPC UA supports several identity token types:

- **Anonymous** -- No user credentials. The server assigns a default role.
- **UserName/Password** -- Cleartext username and password (encrypted by the SecureChannel).
- **X.509 Certificate** -- Client presents a user certificate.
- **IssuedToken** -- Token from an external authority (e.g., Kerberos, JWT).

**AMS-500 finding:** Anonymous access is enabled on the PLC's OPC UA server. When connecting anonymously, the client receives read access to most of the address space, including process variables and alarm data. Two user accounts were identified: `admin` (password: `admin`) and `operator` (password: `ams500op`). Both have been in use since the system was commissioned and have never been changed.

### 5.3 Certificate Management

OPC UA relies on a trust-list model for certificate validation. Each application (client and server) maintains:

- A **Trust List** containing certificates of trusted peers and CA certificates.
- A **Rejected List** of certificates that have been presented but not yet trusted.
- An **Issuer List** of CA certificates used to validate certificate chains.

The S7-1500 PLC's certificate store is managed via the TIA Portal (Siemens engineering tool). On the AMS-500, the trust list was found to contain a wildcard entry that trusts any certificate signed by the factory-default Siemens CA -- this effectively disables mutual authentication.

---

## 6. Session Management

OPC UA sessions have configurable timeout and keep-alive parameters:

- **RequestedSessionTimeout** -- Maximum time (milliseconds) the server keeps the session alive without activity. Default on S7-1500: 30,000 ms (30 seconds).
- **RevisedSessionTimeout** -- The actual timeout the server assigns (may differ from requested).
- **MaxResponseMessageSize** -- Maximum size of a single response. Prevents memory exhaustion.

Sessions are identified by a `SessionId` (NodeId) and an `AuthenticationToken` (opaque byte string). The AuthenticationToken is included in every service request and acts as a session cookie.

**Security note:** The AuthenticationToken is transmitted in every message. If the SecurityPolicy is `None`, this token is visible to any network observer and can be used to hijack the session. Even with `Sign` mode, the token is visible (signing provides integrity, not confidentiality).

---

## 7. Known Attack Vectors

### 7.1 Denial of Service

- **Subscription flooding:** Create thousands of MonitoredItems with minimum sampling intervals. The S7-1500 embedded server has limited memory (approximately 1 MB allocated to OPC UA connections); exceeding this causes the server to reject new connections and may degrade PLC cycle time.
- **Connection exhaustion:** The S7-1500 supports a maximum of 20 concurrent OPC UA sessions. An attacker can consume all slots with idle connections, locking out legitimate clients.
- **Large Browse request:** Requesting Browse with `maxReferencesPerNode=0` (unlimited) on a large address space forces the server to serialise the entire namespace in a single response.

### 7.2 Certificate Theft and Impersonation

If an attacker obtains the private key of a trusted OPC UA client application certificate, they can establish an authenticated SecureChannel and access the server as that application. On the AMS-500, the HMI workstation stores its OPC UA client certificate and private key in a PFX file at `C:\ProgramData\AMS500\Certificates\client.pfx` with no password protection.

### 7.3 Node Enumeration and Intelligence Gathering

Even with Anonymous access, the Browse service exposes the full address space structure, revealing:

- Internal variable naming conventions (process parameters, safety interlocks, alarm thresholds).
- System architecture (which subsystems exist, how they are interconnected).
- Firmware and software version information (exposed as properties on the Server object).
- Network configuration (endpoint URLs reveal hostnames and IP addresses).

This information significantly reduces the reconnaissance effort required for a targeted attack.

### 7.4 Write Abuse

If Write access is available (through compromised credentials or misconfigured access control), an attacker can:

- Modify process parameters (laser power, scan speed) to produce defective parts or damage the machine.
- Change safety thresholds to suppress alarms.
- Overwrite recipe data to sabotage future builds.
- Call methods such as `AbortBuild()` to disrupt production.

On the AMS-500, the combination of default credentials and write-capable OPC UA access represents a critical risk. An attacker on the OT network segment can modify manufacturing parameters through the OPC UA interface without any additional exploitation.

### 7.5 Downgrade Attack

When a server advertises both `None` and a secure SecurityPolicy, a man-in-the-middle attacker can modify the GetEndpoints response to remove the secure policy options, forcing the client to connect with `None`. The client must be configured to reject `None` connections, and the server should not advertise `None` in production.

### 7.6 Replay Attacks on Signed-Only Channels

When using `Sign` mode without encryption, the message payloads are visible. Although the signature prevents modification, an attacker can record and replay entire messages. OPC UA includes sequence numbers and timestamps to mitigate replay, but the protection is limited to a single session -- replayed messages from a different session context will be rejected, but messages within the same session's sequence window may be accepted if the attacker can predict or manipulate sequence numbers.

---

## 8. Assessment Recommendations for AMS-500

1. **Disable SecurityPolicy `None`** on both the PLC and HMI OPC UA servers.
2. **Disable Anonymous access** -- require username/password authentication at minimum; certificate-based authentication is preferred.
3. **Change all default credentials** (`admin`/`admin`, `operator`/`ams500op`) and implement a password policy.
4. **Protect the HMI client certificate** -- set a strong password on the PFX file and restrict filesystem permissions.
5. **Review the PLC trust list** -- remove the wildcard Siemens CA trust entry and explicitly trust only required client certificates.
6. **Implement role-based access control** -- separate read-only monitoring roles from write-capable operator and engineering roles.
7. **Restrict Method access** -- `StartBuild()`, `AbortBuild()`, and `LoadRecipe()` should require elevated privileges and should log all invocations.
8. **Deploy network segmentation** -- the OPC UA server port (4840) should only be accessible from the designated HMI/MES VLAN.
9. **Monitor OPC UA traffic** -- deploy an ICS-aware network monitoring tool (e.g., Claroty, Nozomi Networks, or Dragos) that can decode OPC UA and alert on anomalous Browse, Write, or Call operations.
10. **Upgrade the PLC application certificate** to use a 4096-bit RSA key or ECC P-384 curve.

---

## 9. References

- IEC 62541 (Parts 1-14) -- OPC Unified Architecture
- OPC Foundation, "OPC UA Security Analysis" (2020)
- Siemens Product Note: "Configuring OPC UA on S7-1500" (2024)
- Biham, E. and Neumann, S., "OPC-UA Security Analysis" (BSI, 2017)
- CVE-2022-29862 -- OPC UA .NET Stack Denial of Service
- CVE-2023-27321 -- OPC UA .NET Standard Stack Infinite Loop

---

*This document is part of the AMS-500 security assessment working library. Do not distribute outside the assessment team.*
