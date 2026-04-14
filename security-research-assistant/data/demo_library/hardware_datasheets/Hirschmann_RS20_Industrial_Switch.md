# Hirschmann RS20-0800T1T1SDAEHC Industrial Managed Switch -- Technical Datasheet

**Order Number:** RS20-0800T1T1SDAEHC  
**Product Family:** RSPE / RS20 Managed Industrial Ethernet Switches  
**Document Type:** Technical Datasheet  
**Revision:** 2025-03  
**Source:** Hirschmann (a Belden brand), Neckartenzlingen, Germany

---

## 1. Product Description

The Hirschmann RS20-0800T1T1SDAEHC is an entry-level managed industrial Ethernet switch designed for automation networks, industrial control systems, and harsh environment applications. It provides 8 Fast Ethernet copper ports and 2 SFP slots for fibre optic uplinks, with full Layer 2 management capabilities including VLANs, Quality of Service (QoS), Rapid Spanning Tree, port security, and SNMP-based monitoring.

The RS20 series is designed for DIN rail mounting in industrial control cabinets and complies with relevant IEC, EN, and UL standards for use in industrial and marine environments. The switch supports operating temperatures from -40 to +70 degrees C, making it suitable for non-climate-controlled installations.

In the AMS-500 additive manufacturing system, the RS20-0800T1T1SDAEHC provides network switching for all three VLANs (Control, Motion, Management) and acts as the central network infrastructure component within the machine's control cabinet.

### 1.1 Product Designation Breakdown

```
RS20 - 0800 T 1 T 1 S D A E H C
  |     |    | |  | | | | | | | |
  |     |    | |  | | | | | | | +-- C = Conformally coated
  |     |    | |  | | | | | | +---- H = Horizontal mounting
  |     |    | |  | | | | | +------ E = Enhanced features (ext. temp)
  |     |    | |  | | | | +-------- A = Auto-negotiation
  |     |    | |  | | | +---------- D = DIN rail mounting
  |     |    | |  | | +------------ S = Managed switch
  |     |    | |  | +-------------- 1 = 1x SFP slot (upper)
  |     |    | |  +---------------- T = Twisted pair (100BASE-TX)
  |     |    | +------------------- 1 = 1x SFP slot (lower)
  |     |    +--------------------- T = Twisted pair (100BASE-TX)
  |     +-------------------------- 0800 = 8 copper ports
  +-------------------------------- RS20 = Product family
```

---

## 2. Port Specifications

### 2.1 Copper Ports (10/100BASE-TX)

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Number of copper ports           | 8                                      |
| Connector type                   | RJ-45, shielded, with integrated LEDs |
| Speed                            | 10/100 Mbps (auto-negotiation)         |
| Duplex                           | Half/Full duplex (auto-negotiation)    |
| Auto MDI/MDI-X                   | Yes (automatic crossover detection)    |
| Cable type                       | Cat 5e minimum, shielded (STP/FTP)    |
| Maximum cable length             | 100 m (per IEEE 802.3)                |
| PoE (Power over Ethernet)        | Not supported                          |

### 2.2 SFP Slots (100BASE-FX / 1000BASE-SX/LX)

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Number of SFP slots              | 2 (combo with ports 9 and 10)         |
| Supported SFP modules            | 100BASE-FX, 1000BASE-SX, 1000BASE-LX |
| Connector type (SFP)             | LC duplex (module-dependent)           |
| Fibre type                       | Multimode (50/125 or 62.5/125 um) or single-mode (9/125 um) |
| Maximum distance (multimode)     | Up to 2 km (100BASE-FX) / 550 m (1000BASE-SX) |
| Maximum distance (single-mode)   | Up to 30 km (1000BASE-LX)             |

### 2.3 Compatible SFP Modules (Hirschmann)

| Order Number     | Type           | Wavelength | Distance | Fibre      |
|------------------|----------------|------------|----------|------------|
| M-FAST SFP-SM/LC | 100BASE-FX SM  | 1310 nm    | 30 km    | Single-mode|
| M-FAST SFP-MM/LC | 100BASE-FX MM  | 1310 nm    | 2 km     | Multimode  |
| M-SFP-SX/LC      | 1000BASE-SX MM | 850 nm     | 550 m    | Multimode  |
| M-SFP-LX/LC      | 1000BASE-LX SM | 1310 nm    | 10 km    | Single-mode|

---

## 3. Switching Specifications

### 3.1 Performance

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Switching fabric capacity        | 5.6 Gbps (wire-speed, non-blocking)   |
| Forwarding rate                  | 4.17 Mpps (64-byte frames)            |
| MAC address table size           | 8192 entries                           |
| MAC address learning             | Automatic (IEEE 802.1D)               |
| MAC address aging time           | Configurable: 10 - 630 seconds (default: 300) |
| Jumbo frame support              | Up to 1632 bytes (extended frame)      |
| Packet buffer                    | 1 MB (shared across all ports)         |
| Latency (store-and-forward)      | < 7 us (64-byte frame, 100 Mbps)      |
| Latency (cut-through)            | Not supported (store-and-forward only) |

### 3.2 VLAN Support

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| VLAN standard                    | IEEE 802.1Q                            |
| Maximum VLANs                    | 256 (VLAN ID 1-4094)                  |
| Port-based VLAN (PVID)           | Supported                              |
| Tagged VLAN                      | Supported                              |
| VLAN trunking                    | Supported (802.1Q tagged ports)        |
| Voice VLAN                       | Supported                              |
| Guest VLAN                       | Supported (802.1X integration)         |
| GVRP (VLAN registration protocol)| Supported                             |
| Management VLAN                  | Configurable                           |
| Default VLAN                     | VLAN 1 (all ports, untagged)           |

### 3.3 Spanning Tree

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| STP (IEEE 802.1D)               | Supported                              |
| RSTP (IEEE 802.1w)              | Supported (default enabled)            |
| MSTP (IEEE 802.1s)              | Supported (up to 16 instances)         |
| Ring redundancy (MRP)            | Supported (IEC 62439-2, client + manager) |
| Ring recovery time (MRP)         | < 200 ms (manager), < 500 ms (client) |
| Hirschmann Hiper-Ring            | Supported (< 300 ms recovery)          |

### 3.4 Quality of Service (QoS)

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| QoS queues per port              | 4 (mapped to IEEE 802.1p priorities)  |
| Scheduling algorithm             | Strict priority and/or WRR (weighted round robin) |
| 802.1p priority tagging          | Supported                              |
| DSCP-based classification        | Supported                              |
| Port-based priority              | Supported                              |
| Rate limiting (per port)         | Ingress and egress, 64 kbps granularity|
| Storm control (broadcast)        | Configurable per port, threshold-based |

---

## 4. Management and Configuration

### 4.1 Management Interfaces

| Interface            | Protocol/Method     | Port     | Default State |
|---------------------|---------------------|----------|---------------|
| Web interface (GUI) | HTTP                | TCP 80   | Enabled       |
| Web interface (GUI) | HTTPS (TLS 1.2)    | TCP 443  | Enabled       |
| CLI (Telnet)        | Telnet              | TCP 23   | Enabled       |
| CLI (SSH)           | SSH v2              | TCP 22   | Enabled       |
| Serial console      | RS-232 (RJ11)      | N/A      | Always active |
| SNMP                | SNMP v1/v2c/v3     | UDP 161  | Enabled       |
| SNMP Traps          | SNMP v1/v2c/v3     | UDP 162  | Configurable  |
| HiDiscovery         | Hirschmann L2 protocol| Broadcast| Enabled     |
| Configuration file  | TFTP / SCP          | Various  | Enabled       |

### 4.2 Default Credentials

| Access Method       | Username | Default Password |
|--------------------|----------|------------------|
| Web / CLI / SSH    | admin    | private          |
| Web / CLI / SSH    | user     | public           |
| SNMP v1/v2c Read   | --       | public (community string)   |
| SNMP v1/v2c Write  | --       | private (community string)  |

> **CRITICAL SECURITY WARNING:** The default credentials `admin/private`, `user/public`, and the SNMP community strings `public/private` are publicly documented in all Hirschmann product manuals and are known to automated scanning tools. Any device left with default credentials is considered compromised from a security perspective. **Change all credentials immediately upon installation.** Disable the `user` account if not required.

### 4.3 Operating System

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Operating system             | HiOS (Hirschmann Operating System)         |
| Current version              | HiOS V09.5.00                              |
| Previous versions            | V09.4.00, V09.3.00, V09.2.00, V09.1.00   |
| Configuration file format    | Binary (.cfg) or text-based (.cli)         |
| Configuration backup         | TFTP, SCP, USB (if equipped), web upload   |
| Firmware update method       | TFTP, SCP, web upload, CLI                 |

### 4.4 Web Interface Features

The web-based management interface (accessible via HTTPS on port 443) provides:

- Dashboard with port status, traffic statistics, and system information
- Port configuration (speed, duplex, flow control, description)
- VLAN management (create, delete, assign ports, PVID, tagging)
- Spanning tree configuration (RSTP, MSTP, MRP)
- QoS configuration (priority queues, rate limiting)
- Security settings (802.1X, port security, ACLs, user management)
- SNMP configuration (community strings, v3 users, trap receivers)
- Diagnostics (port statistics, cable diagnostics, event log, topology discovery)
- System maintenance (firmware update, configuration backup/restore, reboot)

### 4.5 Serial Console Access

| Parameter          | Setting       |
|-------------------|---------------|
| Connector          | RJ-11 (front panel) |
| Baud rate          | 9600          |
| Data bits          | 8             |
| Parity             | None          |
| Stop bits          | 1             |
| Flow control       | None          |

The serial console provides CLI access regardless of network connectivity and is the primary recovery method if the switch becomes unreachable via the network.

---

## 5. Security Features

### 5.1 Access Control

| Feature                          | Specification                          |
|----------------------------------|----------------------------------------|
| IEEE 802.1X                      | Supported (port-based network access control) |
| RADIUS authentication            | Supported (for 802.1X and management login) |
| TACACS+ authentication           | Supported (for management login)       |
| Port security (MAC limiting)     | Supported (max. 50 MAC addresses per port) |
| Port security action             | Disable port / send trap / none        |
| Access Control Lists (ACLs)      | IP-based ACLs, MAC-based ACLs (max. 128 rules) |
| DHCP snooping                    | Supported                              |
| Dynamic ARP Inspection (DAI)     | Supported                              |
| IP Source Guard                  | Supported                              |
| Management ACL                   | Restrict management access to specific IP addresses |

### 5.2 Encryption and Authentication

| Feature                          | Specification                          |
|----------------------------------|----------------------------------------|
| HTTPS (web interface)            | TLS 1.2, RSA 2048-bit keys             |
| SSH v2 (CLI)                     | RSA / ECDSA host keys, 2048+ bit       |
| SNMP v3                          | AuthPriv (SHA + AES-128 encryption)    |
| SCP (secure file transfer)       | Via SSH channel                        |
| SSL/TLS cipher suites            | AES-128-CBC, AES-256-CBC, AES-128-GCM |

### 5.3 SNMP Security

**SNMP v1/v2c (Community String Based):**

SNMP v1 and v2c use community strings as a form of authentication. These are transmitted in cleartext and provide no encryption.

| Community  | Default  | Access | Risk                                        |
|-----------|----------|--------|---------------------------------------------|
| Read      | `public` | GET, GETNEXT, GETBULK | Read switch configuration, port statistics, MAC tables, VLAN information |
| Write     | `private`| SET (all writable OIDs) | Modify switch configuration, change VLANs, disable ports, alter ACLs |

> **VULNERABILITY NOTE:** With the default `private` write community string, an attacker with Layer 2 or Layer 3 access to the switch management interface can:
> - Change VLAN port assignments (potentially bridging segmented networks)
> - Disable or enable ports (denial of service)
> - Modify port mirroring (traffic interception)
> - Change management credentials
> - Upload a modified configuration file
> - Modify QoS rules (traffic manipulation)
>
> This is not a vulnerability in the product -- it is an expected consequence of using factory default credentials. Operators MUST change these values.

**SNMP v3 (Recommended):**

SNMP v3 provides authentication (MD5 or SHA) and encryption (DES or AES-128). It should be used instead of v1/v2c in all security-sensitive deployments.

| Parameter            | Specification                                |
|---------------------|----------------------------------------------|
| Security levels     | noAuthNoPriv, authNoPriv, authPriv            |
| Authentication      | MD5, SHA (SHA recommended)                    |
| Encryption          | DES, AES-128 (AES-128 recommended)           |
| Max. SNMPv3 users   | 20                                            |
| Engine ID           | Auto-generated from MAC address               |

### 5.4 Useful SNMP OIDs

| OID                              | Description                    |
|----------------------------------|--------------------------------|
| 1.3.6.1.2.1.1.1.0               | System description             |
| 1.3.6.1.2.1.1.3.0               | System uptime                  |
| 1.3.6.1.2.1.1.5.0               | System name                    |
| 1.3.6.1.2.1.2.2.1.10            | Interface octets in            |
| 1.3.6.1.2.1.2.2.1.16            | Interface octets out           |
| 1.3.6.1.2.1.2.2.1.14            | Interface input errors         |
| 1.3.6.1.2.1.2.2.1.20            | Interface output errors        |
| 1.3.6.1.2.1.17.4.3.1.1          | MAC address table (bridge MIB) |
| 1.3.6.1.4.1.248.14.2.1.2.1.3    | Hirschmann port link status    |
| 1.3.6.1.4.1.248.14.2.1.2.1.9    | Hirschmann port speed          |

---

## 6. Firmware and Known Vulnerabilities

### 6.1 Firmware (HiOS) Versions

| Version    | Release Date | Key Changes                                      |
|------------|-------------|--------------------------------------------------|
| V09.5.00   | 2025-01-15  | TLS 1.3 support, security hardening              |
| V09.4.00   | 2024-07-20  | Fixed SSH key exchange vulnerability              |
| V09.3.00   | 2024-02-10  | Added TACACS+ support, improved RSTP performance  |
| V09.2.00   | 2023-08-05  | Fixed SNMP buffer overflow (CVE-2023-36641)       |
| V09.1.00   | 2023-03-01  | Added DHCP snooping, IP Source Guard              |
| V09.0.00   | 2022-09-15  | Major release: HiOS platform migration            |
| V08.7.00   | 2022-04-01  | Security patches for older platform               |

### 6.2 Known Vulnerabilities in Older Firmware

The following vulnerabilities have been identified in older HiOS firmware versions. Operators running firmware older than V09.5.00 should upgrade immediately.

| CVE ID              | Affected FW    | Fixed FW   | CVSS  | Description                                     |
|---------------------|----------------|------------|-------|-------------------------------------------------|
| CVE-2023-36641      | < V09.2.00     | V09.2.00   | 7.5   | SNMP buffer overflow allowing remote code execution via crafted SNMP v1/v2c GET request |
| CVE-2023-28390      | < V09.2.00     | V09.2.00   | 6.1   | Cross-site scripting (XSS) in web management interface, allows session hijacking |
| CVE-2024-10123      | < V09.4.00     | V09.4.00   | 8.1   | SSH key exchange vulnerability allowing man-in-the-middle attack against SSH management sessions |
| CVE-2022-34825      | < V09.0.00     | V09.0.00   | 9.8   | Hard-coded cryptographic key in firmware, allows decryption of configuration file backups |
| CVE-2022-29561      | < V08.7.00     | V08.7.00   | 7.2   | Authentication bypass in web interface via crafted HTTP request, allows admin access without credentials |

> **IMPORTANT:** CVE-2022-34825 (hard-coded cryptographic key) is particularly severe. In firmware versions prior to V09.0.00, the configuration file encryption key is identical across all RS20 devices. An attacker who obtains a configuration backup file (via SNMP, TFTP, or physical access) can decrypt it offline to extract all credentials, community strings, and network configuration. **Upgrade to V09.0.00 or later immediately** and rotate all credentials after upgrading.

### 6.3 Security Hardening Recommendations

1. **Upgrade firmware** to V09.5.00 (latest) or at minimum V09.4.00.
2. **Change default passwords** for admin and user accounts.
3. **Change SNMP community strings** or, preferably, disable SNMPv1/v2c and use SNMPv3.
4. **Disable Telnet** (port 23). Use SSH v2 exclusively.
5. **Disable HTTP** (port 80). Use HTTPS exclusively.
6. **Disable HiDiscovery** protocol if not needed (Layer 2 broadcast protocol that reveals device presence).
7. **Configure management ACL** to restrict management access to specific IP addresses.
8. **Enable port security** with MAC address limiting on all edge ports.
9. **Disable unused ports** to prevent unauthorised device connection.
10. **Enable 802.1X** on ports where dynamic device connections may occur.
11. **Configure SNMP trap receiver** to send alerts to a SIEM or monitoring system.
12. **Review event log** regularly for failed login attempts, port security violations, and topology changes.

---

## 7. Electrical Specifications

### 7.1 Power Supply

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Supply voltage                   | 12 - 45 VDC or 18 - 30 VAC           |
| Redundant power inputs           | 2 (DC input 1 and DC input 2)         |
| Typical power consumption        | 8 W (without SFP modules)              |
| Maximum power consumption        | 11 W (with 2x SFP modules)            |
| Inrush current                   | 3 A (< 1 ms)                          |
| Power connector                  | Removable terminal block (4-pin)       |
| Wire size                        | 0.14 - 2.5 mm^2 (AWG 26 - 14)        |
| Fuse recommendation (external)   | 2 A slow-blow per supply               |

### 7.2 Power Wiring (4-Pin Terminal Block)

```
+------+------+----------------------------------+
| Pin  | Label| Function                         |
+------+------+----------------------------------+
| 1    | V1+  | DC Supply 1 Positive (+)         |
| 2    | V1-  | DC Supply 1 Negative (-)         |
| 3    | V2+  | DC Supply 2 Positive (+) [redundant] |
| 4    | V2-  | DC Supply 2 Negative (-)         |
+------+------+----------------------------------+

NOTE: Both supplies are diode-isolated internally.
The switch operates from whichever supply provides
the higher voltage. If one supply fails, the switch
continues operating on the remaining supply without
interruption (bumpless transfer). A relay contact
signals power supply fault (see alarm contact below).
```

### 7.3 Signal Contact (Relay Output)

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Contact type                     | Floating relay contact (1x changeover) |
| Maximum switching voltage        | 60 VDC / 30 VAC                       |
| Maximum switching current        | 0.5 A                                  |
| Contact resistance               | < 100 mOhm                            |
| Configurable triggers            | Power supply fault, link loss, temperature alarm, ring redundancy error |
| Connector                        | 3-pin terminal block                   |

---

## 8. Environmental Specifications

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Operating temperature            | -40 to +70 degrees C                   |
| Storage temperature              | -40 to +85 degrees C                   |
| Relative humidity                | 10% to 95% (non-condensing)            |
| Vibration (IEC 60068-2-6)        | 5 Hz - 150 Hz: 3.5 mm / 1g            |
| Shock (IEC 60068-2-27)           | 15g, 11 ms, half-sine                  |
| Free fall (IEC 60068-2-32)       | 1 m (in packaging)                     |
| EMC immunity                     | EN 61000-6-2:2005 (industrial)         |
| EMC emissions                    | EN 61000-6-4:2007+A1:2011              |
| Protection rating                | IP30                                    |
| Pollution degree                 | 2                                       |
| MTBF                             | > 250,000 hours (at +25 degrees C)     |

---

## 9. Physical Dimensions and Mounting

### 9.1 Dimensions

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Width                        | 53 mm                                      |
| Height                       | 135 mm                                     |
| Depth                        | 115 mm (including DIN rail clip)           |
| Weight                       | 540 g (without SFP modules)               |

### 9.2 Mounting

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Mounting method              | DIN rail (35 mm, EN 60715)                 |
| Alternative mounting         | Wall mount (optional bracket)              |
| Mounting orientation         | Horizontal (vertical also supported)       |
| Minimum clearance (top/bottom)| 50 mm (for ventilation)                   |
| Minimum clearance (sides)    | 25 mm (for airflow)                        |

---

## 10. Port LED Indicators

### 10.1 Per-Port LEDs (Each Copper Port)

| LED     | State           | Meaning                                  |
|---------|-----------------|------------------------------------------|
| LINK    | Off             | No link                                  |
| LINK    | Green (steady)  | Link established                         |
| LINK    | Green (blinking)| Link established, data traffic           |
| SPEED   | Off             | 10 Mbps                                  |
| SPEED   | Green           | 100 Mbps                                 |

### 10.2 System LEDs

| LED     | State           | Meaning                                  |
|---------|-----------------|------------------------------------------|
| P1      | Green (steady)  | Power supply 1 present and OK            |
| P1      | Off             | Power supply 1 not present or below threshold |
| P2      | Green (steady)  | Power supply 2 present and OK            |
| P2      | Off             | Power supply 2 not present               |
| RM      | Off             | Ring manager not configured               |
| RM      | Green (steady)  | Ring manager active, ring closed (normal) |
| RM      | Red (steady)    | Ring manager active, ring open (fault)   |
| FAULT   | Off             | No alarms                                |
| FAULT   | Red (steady)    | Active alarm (check event log)           |

---

## 11. Certifications and Approvals

| Certification                    | Standard / Regulation                  |
|----------------------------------|----------------------------------------|
| CE Marking                       | EU EMC Directive, LVD, RoHS            |
| UL / cUL                        | UL 61010-2-201, CSA C22.2 No. 142     |
| Class I, Division 2              | Groups A, B, C, D (UL/FM)             |
| ATEX                             | II 3 G Ex nA IIC T4 Gc               |
| IECEx                            | IECEx UL 14.0001X                     |
| Marine approvals                 | GL, LR, BV, DNV, ABS, NK, CCS, RINA  |
| Railway (rolling stock)          | EN 50155:2007 (Tx -25..+70 degrees C) |
| NEMA                             | TS-2 (traffic control, optional)       |
| IEC 61850-3                      | Substation hardened (with conformal coating) |
| NEBS Level 3                     | GR-63-CORE, GR-1089-CORE (optional)   |

---

## 12. Ordering Information

| Order Number              | Description                                    |
|--------------------------|------------------------------------------------|
| RS20-0800T1T1SDAEHC      | 8x 100BASE-TX, 2x SFP, managed, -40..+70 degC, conformal coated |
| RS20-0800T1T1SDAEHH      | 8x 100BASE-TX, 2x SFP, managed, 0..+55 degC   |
| RS20-0800M2M2SDAEHC      | 8x 100BASE-TX, 2x 100BASE-FX MM (SC), managed  |
| RS20-0400T1T1SDAEHC      | 4x 100BASE-TX, 2x SFP, managed, -40..+70 degC  |
| DIN Rail Power Supply     | See Phoenix Contact QUINT POWER 2904602 (24 VDC, 20A) |

---

**End of Document**

*Based on Hirschmann (Belden) product documentation. Hirschmann, HiOS, and Hiper-Ring are registered trademarks of Belden Inc. All specifications subject to change without notice. Refer to official Hirschmann documentation for binding specifications.*
