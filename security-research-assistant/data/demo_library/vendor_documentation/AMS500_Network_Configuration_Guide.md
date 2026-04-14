# AMS-500 Additive Manufacturing System -- Network Configuration Guide

**Document Number:** AMS-500-NET-001  
**Revision:** B  
**Date:** 2025-09-15  
**Classification:** COMMERCIAL IN CONFIDENCE  
**Manufacturer:** Meridian Advanced Manufacturing Systems Ltd.

---

> **NOTICE:** Incorrect network configuration can result in loss of process control, unintended machine operation, or exposure of the control system to unauthorised access. Network configuration should only be performed by qualified personnel with knowledge of industrial networking and OT security principles. Always follow your organisation's OT security policy.

---

## Table of Contents

1. [Network Architecture Overview](#1-network-architecture-overview)
2. [IP Addressing Scheme](#2-ip-addressing-scheme)
3. [VLAN Configuration](#3-vlan-configuration)
4. [Switch Configuration (Hirschmann RS20)](#4-switch-configuration-hirschmann-rs20)
5. [Firewall Rules Between Zones](#5-firewall-rules-between-zones)
6. [OPC-UA Certificate Management](#6-opc-ua-certificate-management)
7. [NTP Configuration](#7-ntp-configuration)
8. [SNMP Configuration](#8-snmp-configuration)
9. [Remote Access Configuration](#9-remote-access-configuration)
10. [Diagnostic Ports and Services](#10-diagnostic-ports-and-services)
11. [Security Hardening Checklist](#11-security-hardening-checklist)
12. [Network Troubleshooting](#12-network-troubleshooting)

---

## 1. Network Architecture Overview

The AMS-500 employs a defence-in-depth network architecture with three logically separated zones implemented via VLANs on a Hirschmann RS20-0800T1T1SDAEHC managed industrial Ethernet switch. This segmentation follows the principles of IEC 62443 (Industrial Automation and Control Systems Security) and the Purdue Model for network zone separation.

### 1.1 Network Topology Diagram

```
                        +-----------------------------------+
                        |        FACILITY NETWORK           |
                        |     (Customer infrastructure)     |
                        +----------------+------------------+
                                         |
                                    [FIREWALL]
                                    (Customer-provided)
                                         |
                        +----------------+------------------+
                        |   MANAGEMENT NETWORK (VLAN 30)    |
                        |      192.168.10.0/24              |
                        |                                   |
                        |  .1  Hirschmann RS20 (Mgmt IP)   |
                        |  .10 HMI (management interface)   |
                        |  .20 PLC (web server / diag)      |
                        +----------------+------------------+
                                         |
                        +================+==================+
                        |    HIRSCHMANN RS20-0800T1T1SDAEHC |
                        |    (Managed Industrial Switch)     |
                        |                                   |
                        |  Port 1-4: VLAN 10 (Control)      |
                        |  Port 5-6: VLAN 20 (Motion)       |
                        |  Port 7-8: VLAN 30 (Management)   |
                        +===+========+===========+==========+
                            |        |           |
              +-------------+--+  +--+---------+ +----------+
              | CONTROL NET    |  | MOTION NET | | MGMT NET |
              | VLAN 10        |  | VLAN 20    | | VLAN 30  |
              | 192.168.1.0/24 |  | 192.168.2.0| | 192.168.10.0|
              |                |  |   /24      | |    /24   |
              | .1  PLC (S7)   |  | .10 EK1100 | | .1  Switch|
              | .10 EK1100 gw  |  | .11 AX5206 | | .10 HMI  |
              | .20 HMI        |  | .12 AX5203 | | .20 PLC  |
              | .30 RTC6       |  | .13 AX5103 | |          |
              | .100 OPC-UA cl.|  |            | |          |
              +----------------+  +------------+ +----------+
```

### 1.2 Physical Connections

| Switch Port | Connected Device                  | Cable Type      | Speed/Duplex     | VLAN  |
|-------------|-----------------------------------|-----------------|------------------|-------|
| Port 1      | PLC CPU 1515SP PC2 (X1 P1)       | Cat 6a STP, 2m  | 100 Mbps / Full  | 10    |
| Port 2      | Beckhoff EK1100 (PROFINET port)   | Cat 6a STP, 3m  | 100 Mbps / Full  | 10    |
| Port 3      | HMI PanelView Plus 7 (LAN1)      | Cat 6a STP, 5m  | 100 Mbps / Full  | 10    |
| Port 4      | RTC6 Scanner Controller           | Cat 6a STP, 2m  | 100 Mbps / Full  | 10    |
| Port 5      | Beckhoff EK1100 (EtherCAT port)   | Cat 6a STP, 1m  | 100 Mbps / Full  | 20    |
| Port 6      | (Reserved for EtherCAT expansion) | --              | --               | 20    |
| Port 7      | HMI PanelView Plus 7 (LAN2)      | Cat 6a STP, 5m  | 100 Mbps / Full  | 30    |
| Port 8      | PLC CPU 1515SP PC2 (X1 P2)       | Cat 6a STP, 2m  | 100 Mbps / Full  | 30    |

> **NOTE:** The HMI has two network interface cards (LAN1 and LAN2). LAN1 connects to the control network (VLAN 10) for OPC-UA communication with the PLC. LAN2 connects to the management network (VLAN 30) for remote access, file transfer, and diagnostic purposes. These interfaces must NOT be bridged.

---

## 2. IP Addressing Scheme

### 2.1 Control Network (VLAN 10 -- 192.168.1.0/24)

This network carries all real-time control traffic including PROFINET IO, OPC-UA process data, and Modbus TCP.

| IP Address     | Subnet Mask     | Device                          | Interface    | Purpose                    |
|----------------|----------------|---------------------------------|-------------|----------------------------|
| 192.168.1.1    | 255.255.255.0  | Siemens S7-1500 CPU 1515SP PC2 | X1 P1       | PLC control interface      |
| 192.168.1.10   | 255.255.255.0  | Beckhoff EK1100 EtherCAT Coupler| PROFINET port| PROFINET IO device        |
| 192.168.1.20   | 255.255.255.0  | Allen-Bradley PanelView Plus 7 | LAN1        | HMI control interface      |
| 192.168.1.30   | 255.255.255.0  | Scanlab RTC6 Controller        | Ethernet     | Scanner control            |
| 192.168.1.100  | 255.255.255.0  | (Reserved: external OPC-UA client)| --        | SCADA / Historian          |
| 192.168.1.101  | 255.255.255.0  | (Reserved: external Modbus TCP client)| --    | Third-party integration    |
| 192.168.1.200  | 255.255.255.0  | (Reserved: engineering laptop)  | --          | Temporary commissioning    |
| 192.168.1.254  | 255.255.255.0  | Default gateway (if routed)     | --          | Not used in default config |

### 2.2 Motion Network (VLAN 20 -- 192.168.2.0/24)

This network is dedicated to EtherCAT motion control traffic. Although EtherCAT is a Layer 2 protocol and does not require IP addressing, the VLAN is configured for physical isolation and the EtherCAT coupler has an IP address for diagnostic purposes only.

| IP Address     | Subnet Mask     | Device                          | Purpose                |
|----------------|----------------|---------------------------------|------------------------|
| 192.168.2.10   | 255.255.255.0  | Beckhoff EK1100 (diagnostic IP) | EtherCAT diagnostics   |
| 192.168.2.11   | 255.255.255.0  | AX5206 Drive 1 (Z + X axes)    | Drive diagnostics      |
| 192.168.2.12   | 255.255.255.0  | AX5203 Drive 2 (Y axis)        | Drive diagnostics      |
| 192.168.2.13   | 255.255.255.0  | AX5103 Drive 3 (R axis)        | Drive diagnostics      |

> **IMPORTANT:** The motion network must be isolated from all other networks. EtherCAT real-time performance degrades significantly if non-EtherCAT traffic is present on the same physical segment. Do not connect any devices other than EtherCAT participants to VLAN 20.

### 2.3 Management Network (VLAN 30 -- 192.168.10.0/24)

This network provides access for diagnostics, configuration, firmware updates, and optional remote access.

| IP Address      | Subnet Mask     | Device                          | Purpose                    |
|-----------------|----------------|---------------------------------|----------------------------|
| 192.168.10.1    | 255.255.255.0  | Hirschmann RS20 (switch mgmt)   | Switch management          |
| 192.168.10.10   | 255.255.255.0  | Allen-Bradley PanelView Plus 7  | HMI remote access (LAN2)  |
| 192.168.10.20   | 255.255.255.0  | Siemens S7-1500 CPU 1515SP PC2  | PLC web server and diag    |
| 192.168.10.50   | 255.255.255.0  | (Reserved: syslog server)       | Centralised logging        |
| 192.168.10.51   | 255.255.255.0  | (Reserved: NTP server)          | Time synchronisation       |
| 192.168.10.100  | 255.255.255.0  | (Reserved: engineering workstation)| Configuration access     |
| 192.168.10.254  | 255.255.255.0  | Default gateway                 | Facility network uplink    |

### 2.4 DHCP

DHCP is **not used** on any AMS-500 network. All devices use static IP addresses. Using DHCP on the control or motion networks is unsupported and will result in unpredictable behaviour, particularly for PROFINET IO which requires deterministic name resolution.

---

## 3. VLAN Configuration

### 3.1 VLAN Definitions

| VLAN ID | Name              | Subnet           | Purpose                         | Tagged/Untagged |
|---------|-------------------|-------------------|---------------------------------|-----------------|
| 10      | AMS_CONTROL       | 192.168.1.0/24   | PROFINET, OPC-UA, Modbus TCP    | Untagged on P1-4|
| 20      | AMS_MOTION        | 192.168.2.0/24   | EtherCAT motion control         | Untagged on P5-6|
| 30      | AMS_MGMT          | 192.168.10.0/24  | Management, diagnostics, remote | Untagged on P7-8|

### 3.2 Port VLAN Membership (PVID Assignment)

| Port | PVID | Untagged VLAN | Tagged VLANs | Description            |
|------|------|---------------|--------------|------------------------|
| 1    | 10   | 10            | --           | PLC control            |
| 2    | 10   | 10            | --           | EK1100 PROFINET        |
| 3    | 10   | 10            | --           | HMI control            |
| 4    | 10   | 10            | --           | RTC6 scanner           |
| 5    | 20   | 20            | --           | EtherCAT segment       |
| 6    | 20   | 20            | --           | EtherCAT expansion     |
| 7    | 30   | 30            | --           | HMI management         |
| 8    | 30   | 30            | --           | PLC management         |

### 3.3 Inter-VLAN Routing

Inter-VLAN routing is **disabled** on the Hirschmann RS20 switch by default. The three VLANs are completely isolated at Layer 2 and Layer 3. If routing between VLAN 10 and VLAN 30 is required (for example, to allow a management workstation to access OPC-UA data), this must be implemented via an external firewall/router connected to both VLANs, with explicit allow rules.

> **SECURITY WARNING:** Enabling inter-VLAN routing without a firewall exposes the real-time control network to traffic from the management network. This is a significant security risk and can also degrade control network performance. Always use a stateful firewall for inter-VLAN traffic.

---

## 4. Switch Configuration (Hirschmann RS20)

### 4.1 Factory Default Credentials

| Access Method    | Username   | Default Password | Port     |
|------------------|-----------|------------------|----------|
| Web interface    | admin     | private          | 80 (HTTP), 443 (HTTPS) |
| CLI (SSH)        | admin     | private          | 22       |
| CLI (Telnet)     | admin     | private          | 23       |
| SNMP v1/v2c read | --        | public           | 161/UDP  |
| SNMP v1/v2c write| --        | private          | 161/UDP  |

> **CRITICAL SECURITY ACTION:** Change ALL default passwords and SNMP community strings immediately during commissioning. The factory default credentials are publicly documented and represent a known attack vector. Disable Telnet access (port 23) and use SSH exclusively. Disable HTTP and use HTTPS only.

### 4.2 Management Interface Configuration

Access the switch management interface by connecting a laptop to any port on VLAN 30 (ports 7 or 8), configuring the laptop with IP address 192.168.10.100/24, and navigating to https://192.168.10.1.

Alternatively, connect via serial console:
- Connector: RJ11 (front panel)
- Baud rate: 9600
- Data bits: 8
- Parity: None
- Stop bits: 1
- Flow control: None

### 4.3 Recommended Switch Configuration (CLI Commands)

```
! Hirschmann RS20 CLI Configuration
! AMS-500 Network Configuration
! Date: 2025-09-15

! --- System ---
system name AMS500-SW01
system location "Build Chamber Control Cabinet"
system contact "maintenance@facility.local"

! --- Management Interface ---
network parms 192.168.10.1 255.255.255.0 192.168.10.254
network protocol none

! --- Disable unused services ---
no telnet server
no http server
https server

! --- SSH Configuration ---
ssh server
ssh key rsa 4096

! --- VLAN Configuration ---
vlan database
  vlan 10 name AMS_CONTROL state enable
  vlan 20 name AMS_MOTION state enable
  vlan 30 name AMS_MGMT state enable
exit

! --- Port VLAN Assignment ---
interface 1/1
  vlan pvid 10
  vlan participation include 10
  vlan participation exclude 20,30
  no vlan tagging 10
  description "PLC_S7-1500_Control"
  spanning-tree portfast
exit

interface 1/2
  vlan pvid 10
  vlan participation include 10
  vlan participation exclude 20,30
  no vlan tagging 10
  description "EK1100_PROFINET"
  spanning-tree portfast
exit

interface 1/3
  vlan pvid 10
  vlan participation include 10
  vlan participation exclude 20,30
  no vlan tagging 10
  description "HMI_PanelView_Control"
  spanning-tree portfast
exit

interface 1/4
  vlan pvid 10
  vlan participation include 10
  vlan participation exclude 20,30
  no vlan tagging 10
  description "RTC6_Scanner"
  spanning-tree portfast
exit

interface 1/5
  vlan pvid 20
  vlan participation include 20
  vlan participation exclude 10,30
  no vlan tagging 20
  description "EtherCAT_Segment"
  spanning-tree portfast
exit

interface 1/6
  vlan pvid 20
  vlan participation include 20
  vlan participation exclude 10,30
  no vlan tagging 20
  description "EtherCAT_Expansion"
  spanning-tree portfast
exit

interface 1/7
  vlan pvid 30
  vlan participation include 30
  vlan participation exclude 10,20
  no vlan tagging 30
  description "HMI_Management"
  spanning-tree portfast
exit

interface 1/8
  vlan pvid 30
  vlan participation include 30
  vlan participation exclude 10,20
  no vlan tagging 30
  description "PLC_Management"
  spanning-tree portfast
exit

! --- Port Security ---
interface 1/1
  port-security max-mac-count 2
  port-security action shutdown
exit
interface 1/2
  port-security max-mac-count 2
  port-security action shutdown
exit

! --- SNMP (change community strings!) ---
snmp-server community "AMS500_RO_CHANGE_ME" ro
snmp-server community "AMS500_RW_CHANGE_ME" rw

! --- NTP ---
sntp client operation enable
sntp server primary 192.168.10.51
sntp client poll-interval 60

! --- Logging ---
logging host 192.168.10.50 severity informational
logging buffered severity informational
logging console severity warning

! --- Save configuration ---
copy system:running-config nvram:startup-config
```

### 4.4 Spanning Tree Configuration

Rapid Spanning Tree Protocol (RSTP, IEEE 802.1w) is enabled by default. All edge ports (connected to end devices) are configured with PortFast to minimise link-up time. The switch is configured as the root bridge for all VLANs with a bridge priority of 4096.

---

## 5. Firewall Rules Between Zones

If an external firewall is installed between the management network (VLAN 30) and the facility network, the following rules are recommended. Rules should be applied in order, with an implicit deny-all at the end.

### 5.1 Management Network to Facility Network (Outbound)

| Rule | Source           | Destination      | Protocol | Port     | Action | Description                    |
|------|------------------|------------------|----------|----------|--------|--------------------------------|
| 1    | 192.168.10.0/24 | NTP Server       | UDP      | 123      | Allow  | Time synchronisation           |
| 2    | 192.168.10.0/24 | Syslog Server    | UDP      | 514      | Allow  | Centralised logging            |
| 3    | 192.168.10.0/24 | DNS Server       | UDP      | 53       | Allow  | Name resolution (if required)  |
| 4    | 192.168.10.0/24 | Any              | Any      | Any      | Deny   | Block all other outbound       |

### 5.2 Facility Network to Management Network (Inbound)

| Rule | Source           | Destination       | Protocol | Port     | Action | Description                    |
|------|------------------|-------------------|----------|----------|--------|--------------------------------|
| 1    | Eng. Workstation | 192.168.10.1      | TCP      | 443      | Allow  | Switch HTTPS management        |
| 2    | Eng. Workstation | 192.168.10.1      | TCP      | 22       | Allow  | Switch SSH management          |
| 3    | Eng. Workstation | 192.168.10.10     | TCP      | 5900     | Allow  | HMI VNC (if enabled)           |
| 4    | Eng. Workstation | 192.168.10.20     | TCP      | 443      | Allow  | PLC web server                 |
| 5    | SCADA Server     | 192.168.10.20     | TCP      | 4840     | Allow  | OPC-UA (via mgmt interface)    |
| 6    | Monitoring       | 192.168.10.0/24   | UDP      | 161      | Allow  | SNMP polling                   |
| 7    | Any              | 192.168.10.0/24   | Any      | Any      | Deny   | Block all other inbound        |

### 5.3 Control Network Isolation

The control network (VLAN 10) should have NO direct routing path to the facility network. All access to control network services (OPC-UA, Modbus TCP) from outside the AMS-500 must traverse the management network and the PLC's secondary interface (192.168.10.20). This ensures that real-time control traffic is never disrupted by external network activity.

> **NOTE:** The S7-1500 CPU 1515SP PC2 has two Ethernet ports (X1 P1 and X1 P2). P1 is on the control network (192.168.1.1) and handles PROFINET IO and internal OPC-UA traffic. P2 is on the management network (192.168.10.20) and provides the web server, external OPC-UA access, and diagnostic services. These two interfaces are internally firewalled within the CPU -- traffic from the management interface cannot reach the control network backplane.

---

## 6. OPC-UA Certificate Management

### 6.1 Overview

The S7-1500 OPC-UA server uses X.509 certificates for client authentication and transport encryption. In the default configuration, a self-signed certificate is generated by the CPU on first boot. For production deployments, Meridian recommends replacing the self-signed certificate with a certificate signed by your organisation's PKI (Public Key Infrastructure).

### 6.2 Certificate Locations

| Certificate                | Location on CPU                          | Purpose                      |
|----------------------------|------------------------------------------|------------------------------|
| Server certificate         | /OPCUACertificates/own/certs/            | Server identity              |
| Server private key         | /OPCUACertificates/own/private/          | Server authentication        |
| Trusted client certificates| /OPCUACertificates/trusted/certs/        | Authorised client identities |
| Rejected certificates      | /OPCUACertificates/rejected/certs/       | Rejected connection attempts |

### 6.3 Generating a New Server Certificate

Using TIA Portal V17:

1. Open the project containing the S7-1500 configuration.
2. Navigate to the CPU properties > OPC UA > Server > Security.
3. Under "Server Certificate", click "Generate new certificate".
4. Set the following parameters:
   - Common Name (CN): `ams500-plc.local`
   - Organisation (O): `Your Organisation`
   - Validity period: 5 years (1826 days)
   - Key length: 2048 bits (minimum) or 4096 bits (recommended)
   - Signature algorithm: SHA-256
5. Download the configuration to the CPU.
6. Export the server certificate (.der or .pem) for distribution to OPC-UA clients.

### 6.4 Client Certificate Trust

To allow a new OPC-UA client to connect:

1. The client must present an X.509 application instance certificate during the OPC-UA handshake.
2. On first connection attempt, the client certificate will appear in the CPU's "Rejected" certificate store.
3. Using TIA Portal or the CPU's web server, move the client certificate from "Rejected" to "Trusted".
4. The client can now connect.

Alternatively, pre-load trusted client certificates via TIA Portal before deployment.

### 6.5 Security Policies

Configure the OPC-UA server to accept only secure connections:

| Security Policy               | Message Security Mode | Recommended |
|-------------------------------|----------------------|-------------|
| None                          | None                 | DISABLE     |
| Basic256Sha256                | Sign                 | Acceptable  |
| Basic256Sha256                | SignAndEncrypt        | RECOMMENDED |
| Aes128_Sha256_RsaOaep        | SignAndEncrypt        | RECOMMENDED |
| Aes256_Sha256_RsaPss         | SignAndEncrypt        | RECOMMENDED |

> **WARNING:** The "None" security policy transmits all data (including credentials) in cleartext. It must be disabled in any production or security-sensitive environment. This is a common finding in ICS security assessments.

### 6.6 OPC-UA Endpoint URLs

| Endpoint URL                                        | Interface         | Purpose          |
|-----------------------------------------------------|-------------------|------------------|
| `opc.tcp://192.168.1.1:4840`                       | Control (VLAN 10) | Internal HMI     |
| `opc.tcp://192.168.10.20:4840`                     | Mgmt (VLAN 30)    | External clients |

---

## 7. NTP Configuration

### 7.1 Importance of Time Synchronisation

Accurate time synchronisation is essential for:
- Correlating alarm and event timestamps across devices
- Build log integrity (layer timing records)
- Security audit trail accuracy
- Certificate validity checking (OPC-UA)

### 7.2 NTP Architecture

The AMS-500 supports a hierarchical time synchronisation model:

```
[Facility NTP Server (Stratum 1-2)] --> [AMS-500 NTP Reference]
     |
     +--> Hirschmann RS20 (SNTP client) --> 192.168.10.1
     +--> S7-1500 CPU (NTP client)      --> 192.168.1.1 / 192.168.10.20
     +--> HMI PanelView (NTP client)    --> 192.168.1.20 / 192.168.10.10
```

### 7.3 S7-1500 NTP Configuration (TIA Portal)

1. Open CPU properties > Time synchronisation.
2. Select "NTP" as the synchronisation method.
3. Configure NTP server: `192.168.10.51` (or your facility NTP server).
4. Update interval: 60 seconds.
5. Time zone: Set to facility local time zone (e.g., UTC+0 for UK).
6. Enable "Send system time to modules" to synchronise I/O module timestamps.

### 7.4 Hirschmann RS20 SNTP Configuration

The switch uses Simple NTP (SNTP). Configuration via CLI:

```
sntp client operation enable
sntp server primary 192.168.10.51
sntp server secondary 192.168.10.52
sntp client poll-interval 60
clock timezone GMT+0
```

### 7.5 HMI Time Synchronisation

The PanelView Plus 7 HMI synchronises its clock from the PLC via OPC-UA. No separate NTP configuration is required on the HMI if it is connected to the PLC. However, if the HMI is used as a standalone data source, configure the Windows NTP client:

```
w32tm /config /manualpeerlist:"192.168.10.51" /syncfromflags:manual /update
w32tm /resync
```

### 7.6 Offline Operation

In air-gapped deployments where no external NTP server is available, the S7-1500 CPU can act as the local time reference. Configure the CPU as the authoritative time source and all other devices to synchronise from it. Note that the S7-1500 internal clock has an accuracy of approximately +/- 2 seconds per day and will drift without periodic correction.

---

## 8. SNMP Configuration

### 8.1 SNMP Versions Supported

The Hirschmann RS20 supports:
- SNMP v1 (community-string authentication, no encryption)
- SNMP v2c (community-string authentication, no encryption)
- SNMP v3 (user-based authentication, optional encryption)

### 8.2 Factory Default SNMP Communities

| Community String | Access Level | Used By           |
|------------------|-------------|-------------------|
| `public`         | Read-Only   | SNMP GET/GETNEXT  |
| `private`        | Read-Write  | SNMP SET          |

> **CRITICAL SECURITY WARNING:** The default community strings `public` and `private` are universally known and documented. An attacker with network access to the switch management interface can read all switch configuration, interface statistics, VLAN information, MAC address tables, and routing entries using the `public` community. With the `private` community, an attacker can modify switch configuration, change VLAN assignments, disable ports, or modify access control lists. **Change these community strings immediately during commissioning.**

### 8.3 Recommended SNMP Configuration

For security-sensitive deployments, Meridian recommends:

1. **Disable SNMP v1 and v2c entirely.**
2. **Configure SNMP v3** with authentication (SHA) and encryption (AES-128):

```
! Disable SNMP v1/v2c
no snmp-server community "public"
no snmp-server community "private"

! Configure SNMP v3
snmp-server user "ams500_monitor" "AMS500_Monitoring" auth sha "YourAuthPassword" priv aes128 "YourPrivPassword"
snmp-server group "AMS500_Monitoring" v3 auth read "AMS500_ReadView"
snmp-server view "AMS500_ReadView" 1.3.6.1 included
```

3. Restrict SNMP access to specific management stations via ACL:

```
access-list 10 permit 192.168.10.100 0.0.0.0
snmp-server community "AMS500_RO_CHANGE_ME" ro 10
```

### 8.4 Useful SNMP OIDs

| OID                              | Description                    |
|----------------------------------|--------------------------------|
| 1.3.6.1.2.1.1.1.0               | System description             |
| 1.3.6.1.2.1.1.3.0               | System uptime                  |
| 1.3.6.1.2.1.2.2.1.10            | Interface octets in            |
| 1.3.6.1.2.1.2.2.1.16            | Interface octets out           |
| 1.3.6.1.2.1.2.2.1.14            | Interface input errors         |
| 1.3.6.1.2.1.2.2.1.20            | Interface output errors        |
| 1.3.6.1.2.1.17.4.3.1.1          | MAC address table (bridge MIB) |
| 1.3.6.1.4.1.248.14.2.1.2.1.3    | Hirschmann port link status    |
| 1.3.6.1.4.1.248.14.2.1.2.1.9    | Hirschmann port speed          |

---

## 9. Remote Access Configuration

### 9.1 VNC Remote Access to HMI

The Allen-Bradley PanelView Plus 7 HMI can be accessed remotely via VNC (Virtual Network Computing) over the management network.

| Parameter        | Setting                   |
|------------------|---------------------------|
| Protocol         | VNC (RFB protocol)        |
| Port             | TCP 5900                  |
| Default state    | **DISABLED**              |
| Authentication   | VNC password              |
| Encryption       | None (standard VNC)       |

**To enable VNC access:**

1. On the HMI touchscreen, navigate to: Settings > Network > Remote Access.
2. Set "VNC Server" to "Enabled".
3. Set a VNC password (minimum 8 characters).
4. The VNC server listens on 192.168.10.10:5900 (management network only).

> **SECURITY WARNINGS:**
> - Standard VNC does not encrypt traffic. All screen content and keyboard input (including passwords) are transmitted in cleartext. Use only on trusted, segmented networks.
> - Consider tunnelling VNC over SSH for additional security.
> - VNC provides full operator-level access to the HMI. A remote VNC user can start, stop, or modify builds.
> - Disable VNC when remote access is not actively required.

### 9.2 PLC Web Server

The S7-1500 CPU provides a built-in web server for diagnostics and basic configuration.

| Parameter        | Setting                           |
|------------------|-----------------------------------|
| Protocol         | HTTPS (TLS 1.2)                   |
| Port             | TCP 443                           |
| URL              | https://192.168.10.20             |
| Default state    | Enabled                           |
| Authentication   | Username/Password                 |
| Default username | admin                             |
| Default password | (set during TIA Portal download)  |

The web server provides:
- CPU diagnostic information (operating state, memory usage, cycle times)
- Module diagnostic status
- Communication diagnostic (PROFINET, OPC-UA connection status)
- Alarm buffer
- Certificate management
- Firmware version information
- User-defined web pages (custom diagnostic pages)

> **NOTE:** The S7-1500 web server supports only HTTPS. HTTP (port 80) is disabled and cannot be enabled. This is a security-positive design feature of the S7-1500 platform.

### 9.3 TIA Portal Remote Access

For PLC programming and configuration, Siemens TIA Portal V17 connects to the CPU via the management network (192.168.10.20). Access requires:

1. A valid TIA Portal V17 license (Update 6 or later)
2. Network connectivity to 192.168.10.20 on TCP port 102 (S7 Communication / ISO-on-TCP)
3. The CPU must have a configured "access level" that permits HMI + Programming access
4. A password for the configured access level

| Access Level | Permissions                                      | Default Password |
|-------------|--------------------------------------------------|------------------|
| Full access | Read/write PLC programme, diagnostics, firmware   | (set at commissioning) |
| HMI access  | Read process data, write HMI-tagged variables     | (set at commissioning) |
| Read access | Read process data only                            | None             |
| No access   | No online connection                              | --               |

---

## 10. Diagnostic Ports and Services

### 10.1 Active Network Services Summary

| Device         | IP Address      | Port  | Protocol | Service                  | Default State |
|----------------|----------------|-------|----------|--------------------------|---------------|
| PLC (S7-1500)  | 192.168.1.1    | 4840  | TCP      | OPC-UA server            | Enabled       |
| PLC (S7-1500)  | 192.168.1.1    | 502   | TCP      | Modbus TCP server        | Enabled       |
| PLC (S7-1500)  | 192.168.1.1    | 102   | TCP      | S7 Communication (TSAP)  | Enabled       |
| PLC (S7-1500)  | 192.168.10.20  | 443   | TCP      | HTTPS web server         | Enabled       |
| PLC (S7-1500)  | 192.168.10.20  | 4840  | TCP      | OPC-UA server (mgmt)     | Enabled       |
| PLC (S7-1500)  | 192.168.10.20  | 102   | TCP      | S7 Comm (programming)    | Enabled       |
| HMI (PV+7)     | 192.168.1.20   | 44818 | TCP      | EtherNet/IP (CIP)        | Enabled       |
| HMI (PV+7)     | 192.168.10.10  | 5900  | TCP      | VNC server               | **Disabled**  |
| HMI (PV+7)     | 192.168.10.10  | 80    | TCP      | HTTP (FactoryTalk diag)  | Enabled       |
| HMI (PV+7)     | 192.168.10.10  | 443   | TCP      | HTTPS (FactoryTalk diag) | Enabled       |
| Switch (RS20)  | 192.168.10.1   | 443   | TCP      | HTTPS management         | Enabled       |
| Switch (RS20)  | 192.168.10.1   | 22    | TCP      | SSH CLI                  | Enabled       |
| Switch (RS20)  | 192.168.10.1   | 80    | TCP      | HTTP management          | **Disable**   |
| Switch (RS20)  | 192.168.10.1   | 23    | TCP      | Telnet CLI               | **Disable**   |
| Switch (RS20)  | 192.168.10.1   | 161   | UDP      | SNMP                     | Enabled       |
| RTC6           | 192.168.1.30   | 50000 | TCP      | Scanner vector data      | Enabled       |

### 10.2 Port Scan Baseline

For security assessment purposes, the following is the expected result of a port scan against each device in its default (hardened) configuration. Any deviation from this baseline should be investigated.

**PLC (192.168.1.1):**
```
PORT     STATE  SERVICE
102/tcp  open   iso-tsap
502/tcp  open   modbus
4840/tcp open   opcua-tcp
```

**PLC (192.168.10.20):**
```
PORT     STATE  SERVICE
102/tcp  open   iso-tsap
443/tcp  open   https
4840/tcp open   opcua-tcp
```

**HMI (192.168.10.10):**
```
PORT     STATE  SERVICE
80/tcp   open   http
443/tcp  open   https
5900/tcp closed vnc (if disabled)
```

---

## 11. Security Hardening Checklist

Perform these actions during commissioning to secure the AMS-500 network:

- [ ] Change Hirschmann RS20 default password (admin/private)
- [ ] Change SNMP community strings from public/private to unique values
- [ ] Disable SNMP v1/v2c, enable SNMP v3 with authentication and encryption
- [ ] Disable Telnet on the Hirschmann RS20 (use SSH only)
- [ ] Disable HTTP on the Hirschmann RS20 (use HTTPS only)
- [ ] Change OPC-UA default credentials (opc_operator, opc_engineer)
- [ ] Configure OPC-UA certificate-based authentication
- [ ] Disable OPC-UA "None" security policy
- [ ] Set PLC access level passwords in TIA Portal
- [ ] Verify VNC is disabled on HMI (unless explicitly required)
- [ ] If VNC is enabled, set a strong password and restrict access via firewall
- [ ] Verify VLAN isolation -- no cross-VLAN traffic without firewall
- [ ] Configure port security on switch (MAC limiting)
- [ ] Disable unused switch ports
- [ ] Configure NTP for all devices
- [ ] Configure syslog forwarding to centralised log server
- [ ] Perform baseline port scan and document results
- [ ] Verify no default credentials remain on any device
- [ ] Review and restrict Modbus TCP write access (coils and holding registers)
- [ ] Document all IP addresses, credentials, and certificates in a secure asset register
- [ ] Apply latest firmware updates to all devices (PLC, HMI, switch, drives)

---

## 12. Network Troubleshooting

### 12.1 Common Issues

**Issue: HMI cannot connect to PLC via OPC-UA**

1. Verify the HMI is on the control network (192.168.1.20) and can ping 192.168.1.1.
2. Verify OPC-UA server is enabled on the PLC (TIA Portal > CPU properties > OPC UA).
3. Check OPC-UA security policy -- the HMI client must use a policy that the server accepts.
4. Check certificate trust -- the HMI's client certificate must be in the PLC's "Trusted" store.
5. Check the PLC diagnostic buffer for OPC-UA connection errors (web server > Diagnostics > OPC UA).

**Issue: External system cannot connect to Modbus TCP**

1. Verify the client is on the control network or can reach 192.168.1.1 via routing.
2. Verify Modbus TCP server is enabled in the PLC programme (MB_SERVER function block).
3. Check Unit ID -- the default is 1.
4. Check register addressing -- Modbus uses 0-based addressing internally; some clients use 1-based (40001 = address 0).
5. Check for firewall rules blocking TCP port 502.

**Issue: EtherCAT communication error**

1. Check physical connections on the EtherCAT segment (VLAN 20 ports).
2. Check EK1100 diagnostic LEDs: RUN (green = OK), ERR (red = error), LINK/ACT.
3. Use TwinCAT or TIA Portal EtherCAT diagnostics to check for CRC errors, working counter mismatches.
4. Verify EtherCAT is on VLAN 20 only -- any non-EtherCAT traffic on the segment will cause errors.
5. Check cable quality -- EtherCAT requires Cat 5e minimum, Cat 6a recommended for reliability.

**Issue: Switch management interface unreachable**

1. Verify laptop is on the management network (192.168.10.0/24).
2. Try serial console access (RJ11, 9600 baud) as a fallback.
3. If the switch has been factory reset, the management IP returns to 0.0.0.0. Use Hirschmann Discovery protocol (HiDiscovery tool) to find and reconfigure the switch.
4. Check that HTTPS is enabled and you are using https:// (not http://).

### 12.2 Diagnostic Tools

| Tool                        | Purpose                                    | Access                       |
|-----------------------------|--------------------------------------------|------------------------------|
| S7-1500 Web Server          | PLC diagnostics, alarm buffer, module status| https://192.168.10.20       |
| TIA Portal Online           | Full PLC programming and diagnostics       | TCP 102 to 192.168.10.20    |
| Hirschmann Web Manager      | Switch statistics, VLAN config, port status | https://192.168.10.1        |
| Hirschmann CLI (SSH)        | Advanced switch diagnostics                 | SSH to 192.168.10.1         |
| HiDiscovery                 | Hirschmann device discovery (Layer 2)       | Broadcast on VLAN 30        |
| Wireshark                   | Packet capture and protocol analysis       | Mirror port on switch        |
| nmap                        | Port scan and service identification        | From management network      |
| mbpoll                      | Modbus TCP testing utility                  | From control network         |
| UaExpert                    | OPC-UA client for testing                   | From control/mgmt network    |

### 12.3 Configuring a Mirror Port for Packet Capture

To enable packet capture on the Hirschmann RS20 for network troubleshooting:

```
! Mirror all traffic on port 1 (PLC control) to port 8 (monitoring)
monitor session 1 source interface 1/1 both
monitor session 1 destination interface 1/8
```

> **WARNING:** Enabling port mirroring on a production system can impact switch performance under high traffic conditions. Remove mirror configuration when troubleshooting is complete.

---

**End of Document**

*AMS-500-NET-001 Rev B -- Copyright 2025 Meridian Advanced Manufacturing Systems Ltd. All rights reserved.*
*Unauthorised reproduction or distribution of this document is prohibited.*
