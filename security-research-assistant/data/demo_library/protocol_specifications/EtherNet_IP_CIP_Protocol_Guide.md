# EtherNet/IP and Common Industrial Protocol (CIP) - Protocol Guide for ICS Security Researchers

**Document Classification:** OFFICIAL  
**Author:** ICS Security Research Team  
**Last Updated:** 2026-03-22  
**Revision:** 1.7  
**Applicable System:** AMS-500 Additive Manufacturing System  

---

## 1. Protocol Overview

EtherNet/IP (Ethernet Industrial Protocol) is an industrial application-layer protocol that carries the Common Industrial Protocol (CIP) over standard Ethernet and TCP/IP infrastructure. Developed by Rockwell Automation and now managed by ODVA (Open DeviceNet Vendors Association), EtherNet/IP is one of the most widely deployed industrial Ethernet protocols alongside PROFINET and EtherCAT.

CIP is the common application layer shared by EtherNet/IP, DeviceNet, ControlNet, and CompoNet. It provides a unified object-oriented framework for industrial automation -- device configuration, real-time I/O data exchange, diagnostics, and network management all use the same CIP service model regardless of the underlying transport.

On the AMS-500 additive manufacturing system, EtherNet/IP is used for communication between the supervisory layer and several auxiliary subsystems: the powder management unit, the inert gas handling system, and the thermal monitoring cameras. These devices are connected via a Hirschmann RS20 managed switch on the auxiliary subsystem VLAN (10.10.30.0/24).

---

## 2. Transport Layer

EtherNet/IP uses standard TCP/IP and UDP/IP transport over Ethernet (IEEE 802.3).

### 2.1 TCP Port 44818 (AF12h)

Explicit messaging (unconnected and connected) uses TCP port 44818. This includes:

- **Encapsulation messages** -- Session registration, unregistration, list identity, list services.
- **Connected explicit messages** -- Forward Open, Forward Close, and connected data transfers for configuration and diagnostics.
- **Unconnected messages** -- SendRRData (Send Request/Reply Data) for request-response transactions.

TCP provides reliable, ordered delivery for non-time-critical messages such as device configuration, parameter reads/writes, and diagnostic queries.

### 2.2 UDP Port 2222 (08AEh)

Implicit messaging (real-time I/O data) uses UDP port 2222. Implicit messages are time-critical and use connectionless UDP for minimum latency. The data payload is defined by the connection's I/O assembly configuration, not by individual service requests.

Implicit connections are established via a Forward Open request over TCP, which negotiates the Requested Packet Interval (RPI), connection type (point-to-point or multicast), and assembly instance mappings. Once established, I/O data flows over UDP at the configured interval.

**AMS-500 observation:** The powder management controller (Allen-Bradley Micro850) produces implicit I/O data at a 100ms RPI on UDP 2222 multicast address 239.192.1.1. The thermal camera controller uses a 500ms RPI. All implicit traffic is unencrypted and unauthenticated.

### 2.3 Encapsulation Header

All EtherNet/IP messages (both TCP and UDP) begin with a 24-byte encapsulation header:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 2 | Command | Encapsulation command code |
| 2 | 2 | Length | Data length (bytes after header) |
| 4 | 4 | Session Handle | Assigned by target on RegisterSession |
| 8 | 4 | Status | 0 = success |
| 12 | 8 | Sender Context | Echoed back by target |
| 20 | 4 | Options | 0 for all current commands |

Key encapsulation commands:

| Code | Command | Transport |
|------|---------|-----------|
| 0x0001 | ListIdentity | TCP (broadcast via UDP also common) |
| 0x0004 | ListServices | TCP |
| 0x0063 | ListInterfaces | TCP |
| 0x0065 | RegisterSession | TCP |
| 0x0066 | UnregisterSession | TCP |
| 0x006F | SendRRData | TCP (explicit messaging) |
| 0x0070 | SendUnitData | TCP (connected explicit messaging) |

---

## 3. Common Industrial Protocol (CIP) Object Model

CIP models everything as objects with classes, instances, and attributes. Every device on an EtherNet/IP network implements a set of required and optional CIP objects.

### 3.1 Identity Object (Class 0x01)

Every CIP device must implement the Identity Object. It provides device identification:

| Attribute | ID | Data Type | AMS-500 Powder Controller |
|-----------|----|-----------|---------------------------|
| Vendor ID | 1 | UINT | 1 (Rockwell Automation) |
| Device Type | 2 | UINT | 14 (Programmable Logic Controller) |
| Product Code | 3 | UINT | 55 (Micro850) |
| Revision | 4 | STRUCT | 20.013 |
| Status | 5 | WORD | 0x0030 (configured, minor fault) |
| Serial Number | 6 | UDINT | 0x7A3F21B5 |
| Product Name | 7 | STRING | "2080-LC50-48AWB" |

**Security note:** The Identity Object is readable without authentication by any device on the network. The ListIdentity encapsulation command (0x0001) can be broadcast to discover all EtherNet/IP devices. This is the foundation for asset inventory tools like `nmap` scripts (`enip-info`) and Shodan's EtherNet/IP fingerprinting.

### 3.2 Message Router (Class 0x02)

The Message Router directs incoming CIP requests to the appropriate object. It maintains a routing table mapping Class IDs to object implementations. The Message Router is not directly attacked, but it processes all incoming requests -- if it can be overloaded or confused, all CIP services are affected.

### 3.3 Assembly Object (Class 0x04)

Assembly Objects aggregate data from multiple attributes into a single block for efficient I/O exchange. They define the data layout for implicit messaging.

| Assembly Type | Purpose | Direction |
|---------------|---------|-----------|
| Input Assembly | Data produced by the device (sensor readings, status) | Target to Originator |
| Output Assembly | Data consumed by the device (commands, setpoints) | Originator to Target |
| Configuration Assembly | One-time configuration data sent at connection open | Originator to Target |

On the AMS-500 powder controller, the input assembly (Instance 100) contains:

```
Bytes 0-3:   Powder hopper level (REAL, %)
Bytes 4-7:   Powder flow rate (REAL, g/min)
Bytes 8-11:  Sieve motor current (REAL, A)
Byte 12:     System status (USINT, bitmask)
Byte 13:     Fault code (USINT)
```

The output assembly (Instance 101) contains:

```
Bytes 0-3:   Powder feed rate setpoint (REAL, g/min)
Byte 4:      Sieve enable (BOOL)
Byte 5:      Hopper refill command (BOOL)
Bytes 6-7:   Reserved
```

**Critical finding:** The output assembly accepts commands from any originator that establishes a valid CIP connection. There is no authentication, authorisation, or source verification. An attacker who can send packets to the powder controller on UDP 2222 can manipulate powder feed rate setpoints and issue hopper refill commands.

### 3.4 Connection Manager (Class 0x06)

The Connection Manager handles connection establishment and teardown. The key services are:

- **Forward Open (0x54)** -- Establishes a CIP connection (implicit I/O or explicit messaging). Specifies RPI, connection type, timeout multiplier, and transport class/trigger.
- **Forward Close (0x4E)** -- Tears down an existing connection.
- **Unconnected Send (0x52)** -- Routes a single CIP request to a device via an intermediate router without establishing a persistent connection.

The Forward Open request is the most important message in EtherNet/IP from a security perspective. It specifies:

- Connection serial number and originator info (used for connection tracking).
- Requested Packet Interval (RPI) in microseconds.
- Network connection parameters (connection size, type, priority, redundant owner).
- Connection path (route to the target object, including port and link segments).

**Attack vector:** An attacker can issue a Forward Open to establish an implicit I/O connection with the same connection parameters as the legitimate controller, but with the "redundant owner" flag set. If the target accepts the connection, the attacker can inject I/O data alongside the legitimate controller. On devices that accept multiple owners, this results in non-deterministic control behaviour.

---

## 4. Explicit vs. Implicit Messaging

### 4.1 Explicit Messaging

Explicit messages carry full CIP routing information (service code, class, instance, attribute) in every packet. They are request-response transactions used for:

- Configuration: reading and writing device parameters.
- Diagnostics: querying fault logs, status registers.
- Firmware update: uploading new firmware via the File Object.

CIP service codes used in explicit messaging:

| Code | Service | Description |
|------|---------|-------------|
| 0x01 | Get_Attribute_All | Read all attributes of an instance |
| 0x0E | Get_Attribute_Single | Read one attribute |
| 0x03 | Get_Attribute_List | Read multiple specified attributes |
| 0x10 | Set_Attribute_Single | Write one attribute |
| 0x4B | Execute | Invoke a service-specific operation |
| 0x4C | Reset | Reset the device (Type 0: power cycle, Type 1: factory reset) |

**Security note:** The Reset service (0x4C) with Type 1 (factory reset) will erase all configuration and return the device to factory defaults, including resetting IP addresses and erasing any custom programming. This service is available without authentication on most EtherNet/IP devices.

### 4.2 Implicit Messaging

Implicit messages carry only the I/O data payload -- no CIP routing headers. The interpretation of the data is defined by the connection's assembly configuration (established during Forward Open). This makes implicit messages extremely compact and fast, but also means:

- No per-message authentication or integrity checking.
- No service code or addressing in the payload -- data is position-dependent.
- An attacker who knows the assembly layout can craft valid I/O messages.

---

## 5. Security Limitations

EtherNet/IP and CIP were designed in the late 1990s for closed, trusted networks. The protocol has fundamental security limitations.

### 5.1 No Native Encryption

All EtherNet/IP traffic -- both explicit and implicit -- is transmitted in cleartext. There is no provision for encryption in the protocol specification. All CIP service requests, responses, I/O data, device identities, and configuration parameters are visible to any device on the network segment.

### 5.2 No Native Authentication

CIP does not authenticate the source of messages. Any device that can reach the target's TCP port 44818 or UDP port 2222 can issue any CIP service request, including:

- Reading all device parameters.
- Writing configuration parameters.
- Issuing factory reset commands.
- Establishing I/O connections and sending control data.

### 5.3 No Integrity Protection

Messages do not include message authentication codes (MACs) or digital signatures. There is no way to detect in-transit modification of messages. An attacker performing a man-in-the-middle attack can alter I/O data values, service request parameters, or response data.

### 5.4 CIP Security (Recent Addition)

ODVA introduced CIP Security in 2015 (EtherNet/IP specification, Volume 8) to address these gaps. CIP Security provides:

- **TLS/DTLS** for transport encryption and authentication.
- **Device authentication** via X.509 certificates.
- **Secure session establishment** for both explicit and implicit messaging.

However, CIP Security adoption is extremely limited. As of 2026, very few fielded devices support it. None of the EtherNet/IP devices on the AMS-500 support CIP Security. The Micro850 controllers do not have firmware support for CIP Security and are not expected to receive it.

---

## 6. Wireshark Capture Analysis Tips

### 6.1 Capture Filters

```
# Capture all EtherNet/IP traffic
tcp port 44818 or udp port 2222

# Capture only implicit I/O traffic
udp port 2222

# Capture only explicit messaging
tcp port 44818
```

### 6.2 Display Filters

```
# All EtherNet/IP
enip

# CIP layer
cip

# Specific CIP services
cip.service == 0x54          # Forward Open
cip.service == 0x4e          # Forward Close
cip.service == 0x52          # Unconnected Send
cip.service == 0x10          # Set_Attribute_Single (writes)
cip.service == 0x4c          # Reset (dangerous!)

# ListIdentity responses (device enumeration)
enip.command == 0x0063

# Filter by specific device IP
ip.addr == 10.10.30.50 && enip
```

### 6.3 Decoding Tips

1. **Enable CIP I/O decoding:** In Wireshark, go to Edit > Preferences > Protocols > ENIP and enable "Dissect CIP I/O" to decode implicit message payloads.
2. **I/O data interpretation:** Without the assembly configuration (from the RSLogix/Studio 5000 project file), implicit I/O data appears as raw bytes. Export the controller's L5X/ACD project file to obtain the assembly mapping.
3. **Connection tracking:** Wireshark tracks Forward Open requests and maps them to subsequent I/O data streams. The Connection Serial Number and Originator Serial Number in the Forward Open response link to UDP data packets.
4. **Session handle tracking:** In TCP explicit messaging, the Session Handle from RegisterSession is included in all subsequent messages. Filter by session handle to isolate a specific client's traffic.
5. **CIP path decoding:** The CIP path in explicit messages uses encoded segments (port segment, link segment, logical segment). Wireshark decodes these, but understanding the path is essential for determining which device and object is being addressed.

### 6.4 Common Indicators of Compromise

- **Unexpected ListIdentity broadcasts** from non-engineering workstations (asset enumeration).
- **Forward Open from unknown IP addresses** (rogue controller or attacker establishing I/O connections).
- **Set_Attribute_Single (0x10) or Reset (0x4C) from unusual sources** (parameter manipulation or device disruption).
- **Multiple Forward Open requests in rapid succession** (connection exhaustion DoS).
- **I/O data from multiple sources to the same connection point** (injection attack).

---

## 7. AMS-500 Assessment Findings Summary

| Finding | Severity | Detail |
|---------|----------|--------|
| No encryption on any EtherNet/IP traffic | High | All process data, commands, and device parameters are cleartext |
| No authentication on CIP services | Critical | Any network-adjacent device can read/write parameters and issue resets |
| Implicit I/O accepts commands from any originator | Critical | Powder feed rate setpoint can be manipulated remotely |
| Factory reset available without authorisation | High | Service code 0x4C Type 1 erases all configuration |
| Device enumeration via ListIdentity | Medium | Full asset inventory available to any network participant |
| No CIP Security support on fielded devices | High | Cannot be remediated without hardware replacement |
| Multicast I/O data visible to all VLAN members | Medium | Process data leakage across the auxiliary subsystem VLAN |

---

## 8. Mitigation Recommendations

1. **Network segmentation:** Isolate EtherNet/IP devices on dedicated VLLANs with firewall rules restricting access to TCP 44818 and UDP 2222 from only authorised controllers and engineering workstations.
2. **Deploy industrial firewall/DPI:** Use an industrial-aware firewall (e.g., Hirschmann EAGLE, Fortinet FortiGate with OT signatures) that can inspect CIP traffic and block unauthorised service codes (especially 0x4C Reset and 0x10 Set_Attribute writes).
3. **Disable unnecessary CIP services:** If the device firmware supports it, disable the Reset service and restrict Set_Attribute access.
4. **Monitor for anomalous traffic:** Deploy ICS network monitoring (Claroty, Nozomi, Dragos) to detect unexpected CIP service requests, new connections, and I/O data from unauthorised sources.
5. **Physical access controls:** Since network-level authentication is absent, physical access to the EtherNet/IP network segments must be tightly controlled.
6. **Plan for CIP Security migration:** Evaluate whether future device replacements can include CIP Security-capable hardware.

---

## 9. References

- ODVA, "EtherNet/IP Specification" (CIP Vol 1-2, EtherNet/IP Vol 1-2)
- ODVA, "CIP Security" (EtherNet/IP Specification, Volume 8)
- CISA, "EtherNet/IP and CIP Security Assessment" (ICS-TIP-12-146-01B)
- Wireshark Foundation, "ENIP/CIP Protocol Dissector" documentation
- CVE-2012-6435 -- Rockwell Automation EtherNet/IP denial of service
- CVE-2022-1159 -- Rockwell Studio 5000 Logix Designer code injection

---

*This document is part of the AMS-500 security assessment working library. Do not distribute outside the assessment team.*
