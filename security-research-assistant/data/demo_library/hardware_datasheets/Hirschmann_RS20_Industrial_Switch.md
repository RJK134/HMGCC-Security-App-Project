# Hirschmann RS20-0800T2T Industrial Ethernet Switch — Technical Datasheet

## Product Overview

| Parameter | Value |
|-----------|-------|
| Order Number | RS20-0800T2T (943 434-029) |
| Manufacturer | Hirschmann (Belden) |
| Product Family | RAIL Switch RS20 |
| Function | Managed Layer 2 Industrial Ethernet Switch |
| Firmware Version | HiOS 7.1.04 (AMS-500 installed version) |
| Latest Firmware | HiOS 9.6.01 (not installed) |

## Description

The RS20-0800T2T is a managed industrial Ethernet switch designed for harsh industrial environments. It provides 8x 10/100BASE-TX ports and 2x 100BASE-FX SFP slots for fibre uplinks. In the AMS-500 installation, three RS20 switches provide network connectivity across the control, field, and management VLANs.

## Technical Specifications

### Ports and Performance

| Parameter | Specification |
|-----------|--------------|
| Copper Ports | 8x 10/100BASE-TX (RJ45) |
| Fibre Ports | 2x 100BASE-FX (SFP slots) |
| Switching Capacity | 2.0 Gbps |
| Forwarding Rate | 1.488 Mpps |
| MAC Address Table | 8,192 entries |
| VLAN Support | IEEE 802.1Q, up to 256 VLANs |
| Spanning Tree | RSTP (802.1w), MSTP (802.1s) |
| Link Aggregation | IEEE 802.3ad (2 groups) |
| Jumbo Frames | Up to 1,632 bytes |
| Latency | <7 us (store-and-forward) |

### Management Interfaces

| Interface | Port | Protocol | Default State |
|-----------|------|----------|---------------|
| Web Interface (HTTP) | TCP 80 | HTTP | **Enabled** |
| Web Interface (HTTPS) | TCP 443 | HTTPS (TLS 1.2) | Enabled |
| SSH | TCP 22 | SSHv2 | Enabled |
| Telnet | TCP 23 | Telnet (plaintext) | **Enabled** |
| SNMP v1 | UDP 161 | SNMP | **Enabled (community: public/private)** |
| SNMP v2c | UDP 161 | SNMP | **Enabled (community: public/private)** |
| SNMP v3 | UDP 161 | SNMP | Disabled |
| Serial Console | RS-232 (RJ11) | CLI, 9600 8N1 | Enabled |
| TFTP | UDP 69 | Configuration backup | Enabled on request |
| Syslog | UDP 514 | Event logging | Disabled |

**SECURITY WARNING:** Default installation has HTTP, Telnet, and SNMPv1/v2c enabled with default community strings. These should be disabled and replaced with HTTPS, SSH, and SNMPv3 in production environments.

### Default Credentials

| Service | Username | Password | Notes |
|---------|----------|----------|-------|
| Web/CLI Admin | admin | private | **Must be changed on first login** |
| Web/CLI User | user | public | Read-only access |
| SNMP Read | — | public | SNMPv1/v2c community string |
| SNMP Write | — | private | SNMPv1/v2c community string |

**AMS-500 Finding:** Default credentials are still active on all three RS20 switches in the installation. The admin password has not been changed from "private".

### Network Protocols

| Feature | Support |
|---------|---------|
| VLANs | 802.1Q, port-based, protocol-based |
| QoS | 802.1p, DSCP, 4 priority queues |
| Multicast | IGMP snooping v1/v2/v3 |
| Redundancy | RSTP, MRP (Media Redundancy Protocol) |
| Time Sync | IEEE 1588 PTP v2, SNTP |
| Port Security | MAC-based (up to 50 MACs per port) |
| Port Mirroring | 1 mirror destination port |
| ACLs | L2/L3/L4 access control lists (128 rules) |
| DHCP | Relay, snooping |
| LLDP | IEEE 802.1AB |

### Electrical

| Parameter | Specification |
|-----------|--------------|
| Power Supply | 12-45 V DC (redundant inputs on terminal block) |
| Power Consumption | Max. 7.3 W |
| PoE | Not supported |
| Relay Output | 1x signal contact (fault relay) |

### Environmental

| Parameter | Specification |
|-----------|--------------|
| Operating Temperature | -40 to +70 C |
| Storage Temperature | -40 to +85 C |
| Humidity | 10-95% non-condensing |
| Protection Rating | IP30 |
| Mounting | DIN rail (TS 35) |
| Dimensions (W x H x D) | 56 x 138 x 114 mm |
| Weight | 650 g |
| MTBF | >500,000 hours (MIL-HDBK-217F) |

## Known Vulnerabilities

### Applicable to Installed Firmware (HiOS 7.1.04)

| CVE | CVSS | Description | Remediation |
|-----|------|-------------|-------------|
| CVE-2021-9295 | 9.8 | Unauthenticated remote code execution via crafted HTTP request to web interface | Upgrade to HiOS 8.0+ |
| CVE-2020-9308 | 7.5 | Directory traversal via web interface allows reading arbitrary files | Upgrade to HiOS 7.2+ |
| CVE-2019-12263 | 5.3 | VxWorks TCP/IP stack vulnerability (URGENT/11) affects older firmware | Upgrade to HiOS 7.1.05+ |
| CVE-2018-10933 | 9.1 | libssh authentication bypass in SSH implementation | Upgrade to HiOS 7.1.02+ |

**AMS-500 Finding:** The installed firmware HiOS 7.1.04 is vulnerable to CVE-2021-9295 (RCE) and CVE-2020-9308 (directory traversal). These are critical findings requiring immediate firmware upgrade.

### Firmware Update Process

Firmware can be updated via:
1. Web interface (upload .bin file)
2. TFTP transfer
3. USB (via serial console bootstrap)
4. Hirschmann Industrial HiVision management software

**Security Note:** Firmware images are signed with RSA-2048 by Hirschmann. The switch verifies signatures before applying updates, preventing installation of tampered firmware.

## AMS-500 Installation Configuration

### Switch Assignments

| Switch | Hostname | IP Address | VLAN | Function |
|--------|----------|-----------|------|----------|
| SW-01 | AMS-CTRL-SW | 192.168.1.1 | VLAN 20 (Control) | PLC, HMI, engineering workstation |
| SW-02 | AMS-FIELD-SW | 192.168.2.1 | VLAN 30 (Field) | EtherCAT, Modbus devices, sensors |
| SW-03 | AMS-MGMT-SW | 192.168.99.1 | VLAN 99 (Management) | Switch management, NTP, syslog |

### Port Security Configuration (Current State)

Port security is **not configured** on any switch. All ports accept traffic from any MAC address. There is no 802.1X authentication configured.

### Recommendations

1. **CRITICAL:** Change default admin password on all three switches
2. **CRITICAL:** Upgrade firmware from HiOS 7.1.04 to HiOS 9.6.01
3. **HIGH:** Disable HTTP, Telnet, SNMPv1/v2c; enable HTTPS-only, SSH, SNMPv3
4. **HIGH:** Enable port security with MAC address whitelisting
5. **MEDIUM:** Configure ACLs to restrict inter-VLAN traffic
6. **MEDIUM:** Enable syslog forwarding to a centralised log server
7. **LOW:** Configure RSTP for loop prevention
8. **LOW:** Enable IEEE 1588 PTP for network time synchronisation

## Compliance

- CE, UL, CSA, ATEX (Zone 2), IECEx
- IEC 61850-3 (Substation hardened)
- IEEE 1613 (Power substation)
- EN 50121-4 (Railway)
- NEMA TS2 (Traffic control)
- DNV GL (Maritime)

---
*Source: Hirschmann (Belden). Reference: RS20 Family Technical Documentation, 2024.*
