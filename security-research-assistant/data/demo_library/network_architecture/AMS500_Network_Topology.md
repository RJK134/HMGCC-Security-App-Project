# AMS-500 Network Topology and Architecture

**Document ID:** AMS-NET-001 Rev.D  
**Classification:** COMPANY CONFIDENTIAL  
**Author:** R. Thornton, OT Network Engineering  
**Reviewed:** K. Okonkwo, ICS Security  
**Date:** 2025-10-22  
**Applies to:** AMS-500 Installation at Building 7, Cell 3  

---

## 1. Overview

This document describes the network topology of the AMS-500 additive manufacturing system as deployed at the Building 7 manufacturing cell. The network is segmented into three zones aligned with the Purdue Enterprise Reference Architecture (ISA-95) and IEC 62443 zone/conduit model.

The AMS-500 system interconnects approximately 18 networked devices across three VLANs, utilising a combination of Ethernet/IP, PROFINET, EtherCAT, OPC-UA, and Modbus TCP protocols. Network traffic is managed by industrial-grade Cisco IE switches with a Fortinet FortiGate 60F firewall providing inter-zone traffic filtering.

**Key concern:** The current deployment was configured for rapid commissioning and does not yet meet IEC 62443 SL-2 requirements. Several findings from the most recent audit (AMS-SEC-2025-Q3) remain open. See Section 8 for a summary.

---

## 2. Network Zones

### Zone 1: IT / OT Demilitarised Zone (DMZ)

**Purpose:** Provides controlled connectivity between the corporate IT network and the OT control network. Hosts data historians, reporting servers, and remote access infrastructure.

- **VLAN:** 10
- **Subnet:** 10.10.10.0/24
- **Gateway:** 10.10.10.1 (FortiGate inside interface)
- **ISA-95 Level:** 3 / 3.5

### Zone 2: Control Network

**Purpose:** Carries supervisory traffic between the PLC, HMI, engineering workstations, and SCADA server. All OPC-UA, Modbus TCP, and PROFINET controller-level communications reside here.

- **VLAN:** 20
- **Subnet:** 10.10.20.0/24
- **Gateway:** 10.10.20.1 (FortiGate OT interface)
- **ISA-95 Level:** 2

### Zone 3: Field Network

**Purpose:** Dedicated to real-time fieldbus communications. EtherCAT motion bus and PROFINET IO are isolated on this segment. No IP-routable traffic should traverse this zone.

- **VLAN:** 30
- **Subnet:** 10.10.30.0/24 (PROFINET devices) / Non-IP (EtherCAT)
- **Gateway:** None (no routing to/from this zone)
- **ISA-95 Level:** 0 / 1

---

## 3. Network Diagram

```
                         CORPORATE NETWORK
                         (10.0.0.0/8)
                              |
                              | Gi0/0 (WAN)
                     +--------+--------+
                     |  FortiGate 60F  |
                     |  10.10.10.1     |
                     |  (FW-AMS-01)    |
                     +---+----+----+---+
                         |    |    |
           Gi0/1 (DMZ)  |    |    | Gi0/3 (MGMT)
          10.10.10.1/24  |    |    | 10.10.99.1/24
                         |    |
                         |    | Gi0/2 (OT)
                         |    | 10.10.20.1/24
                         |    |
     ZONE 1: DMZ         |    |          ZONE 2: CONTROL
     VLAN 10              |    |          VLAN 20
  +-----------------------+    +---------------------------+
  |                                                        |
  | Cisco IE-4010 (SW-DMZ-01)    Cisco IE-4010 (SW-CTL-01)|
  | 10.10.10.2                   10.10.20.2                |
  |                                                        |
  | Port  Device              IP            Port  Device              IP
  | ----  ------              --            ----  ------              --
  | Gi1   FortiGate Gi0/1    10.10.10.1    Gi1   FortiGate Gi0/2    10.10.20.1
  | Gi2   Historian Server    10.10.10.10   Gi2   S7-1500 PLC (PN1) 10.10.20.10
  | Gi3   Engineering WS 1   10.10.10.20   Gi3   S7-1500 PLC (PN2) 10.10.20.11
  | Gi4   Engineering WS 2   10.10.10.21   Gi4   HMI Panel          10.10.20.50
  | Gi5   Remote Access GW   10.10.10.30   Gi5   SCADA Server       10.10.20.60
  | Gi6   Backup NAS          10.10.10.40   Gi6   Safety PLC (F-CPU) 10.10.20.12
  | Gi7   (unused)                          Gi7   Laser Controller   10.10.20.70
  | Gi8   (unused)                          Gi8   Gas Analyser       10.10.20.71
  |                                         Gi9   Chiller Unit       10.10.20.72
  |                                         Gi10  MPC Camera Server  10.10.20.80
  |                                         Gi11  Powder Bed Camera  10.10.20.81
  |                                         Gi12  -> SW-FIELD-01     (trunk)
  |                                                                    |
  +--------------------------------------------------------+-----------+
                                                           |
                                              ZONE 3: FIELD NETWORK
                                              VLAN 30 + EtherCAT
                                                           |
                                              Cisco IE-2000 (SW-FIELD-01)
                                              10.10.30.2
                                                           |
                                              Port  Device              IP
                                              ----  ------              --
                                              Fa1   PROFINET IO (ET200SP-1) 10.10.30.10
                                              Fa2   PROFINET IO (ET200SP-2) 10.10.30.11
                                              Fa3   PROFINET IO (ET200SP-3) 10.10.30.12
                                              Fa4   EtherCAT Master (BBB)   10.10.30.20
                                              Fa5   (EtherCAT - non-IP)     N/A
                                              Fa6   (EtherCAT - non-IP)     N/A
                                              Fa7   Modbus RTU Gateway      10.10.30.30
                                              Fa8   -> SW-CTL-01 Gi12       (trunk)

  EtherCAT Segment (daisy-chain from BBB port eth1):
  +------------+     +------------+     +------------+
  | AX5206     |---->| AX5106     |---->| AX5103     |
  | Z-Axis     |     | X-Recoater |     | Doser      |
  | Slave 1    |     | Slave 2    |     | Slave 3    |
  +------------+     +------------+     +------------+

  Management VLAN 99 (out-of-band):
  10.10.99.0/24
  - FortiGate MGMT: 10.10.99.1
  - SW-DMZ-01 MGMT: 10.10.99.2
  - SW-CTL-01 MGMT: 10.10.99.3
  - SW-FIELD-01 MGMT: 10.10.99.4
```

---

## 4. Device Inventory

| Device | Hostname | IP Address | MAC Address | Zone | ISA-95 Level | Purpose |
|--------|----------|------------|-------------|------|-------------|---------|
| FortiGate 60F | FW-AMS-01 | 10.10.10.1 / 10.10.20.1 / 10.10.99.1 | 00:09:0F:AA:11:01 | All | 3.5 | Inter-zone firewall |
| Cisco IE-4010 | SW-DMZ-01 | 10.10.10.2 / 10.10.99.2 | 00:1B:54:C2:30:01 | DMZ | 3 | DMZ switch |
| Cisco IE-4010 | SW-CTL-01 | 10.10.20.2 / 10.10.99.3 | 00:1B:54:C2:30:02 | Control | 2 | Control network switch |
| Cisco IE-2000 | SW-FIELD-01 | 10.10.30.2 / 10.10.99.4 | 00:1B:54:D1:40:01 | Field | 1 | Field network switch |
| Dell PowerEdge T350 | HIST-01 | 10.10.10.10 | D4:AE:52:81:AA:10 | DMZ | 3 | Historian / data archive |
| Dell Precision 5570 | ENG-WS-01 | 10.10.10.20 | D4:AE:52:81:BB:20 | DMZ | 3 | TIA Portal engineering |
| Dell Precision 5570 | ENG-WS-02 | 10.10.10.21 | D4:AE:52:81:BB:21 | DMZ | 3 | CAM / recipe development |
| Tosibox Lock 500 | RAS-01 | 10.10.10.30 | 00:1A:4D:55:CC:30 | DMZ | 3.5 | Vendor remote access |
| Synology DS920+ | NAS-01 | 10.10.10.40 | 00:11:32:AA:DD:40 | DMZ | 3 | Backup / data archive |
| Siemens S7-1515SP PC2 | PLC-AMS-01 | 10.10.20.10 (PN1), 10.10.20.11 (PN2) | 00:1B:1B:A4:3C:10 | Control | 2 | Main process PLC |
| Siemens F-CPU 1516F | PLC-SAFETY-01 | 10.10.20.12 | 00:1B:1B:A4:3C:12 | Control | 2 | Safety PLC (PROFIsafe) |
| Siemens IPC477E | HMI-01 | 10.10.20.50 | 00:1B:1B:A4:3C:7E | Control | 2 | Operator HMI panel |
| Dell Precision 3460 | SCADA-01 | 10.10.20.60 | D4:AE:52:81:CC:60 | Control | 2 | WinCC SCADA server |
| IPG Photonics YLR-500 | LASER-01 | 10.10.20.70 | 00:50:C2:FF:01:70 | Control | 1 | Fibre laser controller |
| Servomex MiniMP 5200 | GAS-01 | 10.10.20.71 | 00:50:C2:FF:02:71 | Control | 1 | O2 / moisture analyser |
| SMC Thermo-chiller | CHILL-01 | 10.10.20.72 | 00:50:C2:FF:03:72 | Control | 1 | Laser chiller unit |
| Basler ace 2 | CAM-MPC-01 | 10.10.20.80 | 00:30:53:AA:01:80 | Control | 1 | Melt pool camera |
| Basler ace 2 | CAM-PB-01 | 10.10.20.81 | 00:30:53:AA:02:81 | Control | 1 | Powder bed camera |
| BeagleBone Black Ind. | ECAT-MASTER | 10.10.30.20 | 1C:BA:8C:EE:01:20 | Field | 1 | EtherCAT master |
| Siemens ET200SP | IO-01 | 10.10.30.10 | 00:1B:1B:B5:01:10 | Field | 0 | Distributed I/O rack 1 |
| Siemens ET200SP | IO-02 | 10.10.30.11 | 00:1B:1B:B5:01:11 | Field | 0 | Distributed I/O rack 2 |
| Siemens ET200SP | IO-03 | 10.10.30.12 | 00:1B:1B:B5:01:12 | Field | 0 | Distributed I/O rack 3 |
| Moxa MGate 3170 | MBUS-GW-01 | 10.10.30.30 | 00:90:E8:CC:01:30 | Field | 0 | Modbus RTU-TCP gateway |

---

## 5. Protocol Matrix

| Protocol | Transport | Port(s) | Source Zone | Destination Zone | Devices | Encrypted | Authenticated |
|----------|-----------|---------|-------------|-----------------|---------|-----------|--------------|
| OPC-UA | TCP | 4840 | DMZ, Control | Control | PLC, Historian, SCADA | **No** (policy=None) | **No** (Anonymous) |
| Modbus TCP | TCP | 502 | Control | Control, Field | PLC, HMI, SCADA, Gateway | **No** | **No** |
| PROFINET IO | Ethernet (L2) | N/A | Control, Field | Field | PLC, ET200SP | **No** | **No** |
| PROFINET CBA | TCP | 34962-34964 | Control | Control | PLC, SCADA | **No** | **No** |
| EtherCAT | Ethernet (L2) | N/A | Field | Field | BBB, Servo drives | **No** | **No** |
| HTTP/HTTPS | TCP | 80, 443 | DMZ, Control | Control | HMI, Engineering WS | Partial (HTTPS) | Basic (passwords) |
| VNC | TCP | 5900 | DMZ, Control | Control | HMI | **No** | DES password |
| SSH | TCP | 22 | DMZ | Control, Field | Engineering WS, BBB | **Yes** | Key/password |
| SMB | TCP | 445 | Control | DMZ | HMI, NAS | **No** (SMBv1 seen) | NTLM |
| NTP | UDP | 123 | All | Control | PLC (NTP master) | **No** | **No** |
| SNMP | UDP | 161, 162 | Management | All switches | Switches, Firewall | **No** (v2c) | Community string |
| Syslog | UDP | 514 | All | DMZ | All devices, Historian | **No** | **No** |
| GigE Vision | UDP | 3956 | Control | Control | Cameras | **No** | **No** |

---

## 6. Switch Port Assignments

### SW-DMZ-01 (Cisco IE-4010-4S8P, VLAN 10)

| Port | Speed | VLAN | Device | Notes |
|------|-------|------|--------|-------|
| Gi1/1 | 1G | Trunk (10,99) | FW-AMS-01 Gi0/1 | Uplink to firewall |
| Gi1/2 | 1G | 10 | HIST-01 | Data historian |
| Gi1/3 | 1G | 10 | ENG-WS-01 | Engineering workstation |
| Gi1/4 | 1G | 10 | ENG-WS-02 | Engineering workstation |
| Gi1/5 | 1G | 10 | RAS-01 | Remote access gateway |
| Gi1/6 | 1G | 10 | NAS-01 | Backup NAS |
| Gi1/7 | 1G | 10 | (unused) | Port disabled |
| Gi1/8 | 1G | 10 | (unused) | Port disabled |

### SW-CTL-01 (Cisco IE-4010-16S12P, VLAN 20)

| Port | Speed | VLAN | Device | Notes |
|------|-------|------|--------|-------|
| Gi1/1 | 1G | Trunk (20,99) | FW-AMS-01 Gi0/2 | Uplink to firewall |
| Gi1/2 | 1G | 20 | PLC-AMS-01 (PN1) | PLC port 1 - OPC-UA, Modbus |
| Gi1/3 | 1G | 20 | PLC-AMS-01 (PN2) | PLC port 2 - PROFINET controller |
| Gi1/4 | 1G | 20 | HMI-01 | Operator panel |
| Gi1/5 | 1G | 20 | SCADA-01 | WinCC SCADA |
| Gi1/6 | 1G | 20 | PLC-SAFETY-01 | Safety PLC |
| Gi1/7 | 100M | 20 | LASER-01 | Laser controller |
| Gi1/8 | 100M | 20 | GAS-01 | O2 analyser |
| Gi1/9 | 100M | 20 | CHILL-01 | Chiller unit |
| Gi1/10 | 1G | 20 | CAM-MPC-01 | Melt pool camera (GigE Vision) |
| Gi1/11 | 1G | 20 | CAM-PB-01 | Powder bed camera (GigE Vision) |
| Gi1/12 | 1G | Trunk (20,30,99) | SW-FIELD-01 Fa8 | Downlink to field switch |

### SW-FIELD-01 (Cisco IE-2000-8TC-G-E, VLAN 30)

| Port | Speed | VLAN | Device | Notes |
|------|-------|------|--------|-------|
| Fa1 | 100M | 30 | IO-01 (ET200SP) | Digital I/O - safety sensors |
| Fa2 | 100M | 30 | IO-02 (ET200SP) | Analogue I/O - process sensors |
| Fa3 | 100M | 30 | IO-03 (ET200SP) | Mixed I/O - powder handling |
| Fa4 | 100M | 30 | ECAT-MASTER (eth0) | BBB management port |
| Fa5 | - | - | (reserved) | Future expansion |
| Fa6 | - | - | (reserved) | Future expansion |
| Fa7 | 100M | 30 | MBUS-GW-01 | Modbus RTU-TCP gateway |
| Gi1 | 1G | Trunk (20,30,99) | SW-CTL-01 Gi1/12 | Uplink to control switch |

Note: EtherCAT runs on a dedicated port (eth1) on the BeagleBone Black, directly daisy-chained to the three Beckhoff servo drives. This is a separate physical segment from the switched Ethernet infrastructure.

---

## 7. Traffic Flow Analysis

### 7.1 Normal Build Operation

During a typical build cycle, the following traffic patterns are observed:

**High-frequency (< 10ms cycle):**
- PROFINET IO: PLC <-> ET200SP racks. Layer 2 frames, ~150 bytes every 4ms. Three IO connections totalling approximately 300 Kbps sustained.
- EtherCAT: BBB <-> Servo drives. Layer 2 frames, ~120 bytes every 1ms. Approximately 960 Kbps sustained on the dedicated EtherCAT segment.

**Medium-frequency (100ms - 1s):**
- OPC-UA: PLC -> SCADA/Historian. Subscription updates at 500ms interval. Approximately 40 monitored items producing ~20 Kbps.
- Modbus TCP: HMI -> PLC. Polling 50 holding registers at 1-second intervals. Approximately 5 Kbps per polling session.
- GigE Vision: Cameras -> CAM servers. Melt pool camera at 1000 fps producing approximately 80 Mbps during active lasing. Powder bed camera captures a single 5MP frame after each recoat (~10 MB per image, one per layer).

**Low-frequency (> 1s):**
- SMB: HMI -> NAS. Data log archive every 60 minutes. Burst of approximately 10-50 MB.
- NTP: All devices -> PLC. Time synchronisation every 60 seconds.
- SNMP: Switches/FW -> Historian. Polling every 300 seconds.
- Syslog: All devices -> Historian. Event-driven, typically 1-5 messages per minute during normal operation.

### 7.2 Bandwidth Requirements

| Segment | Typical Load | Peak Load | Interface Capacity | Utilisation |
|---------|-------------|-----------|-------------------|-------------|
| DMZ uplink | 5 Mbps | 100 Mbps (data archive) | 1 Gbps | < 10% |
| Control backbone | 120 Mbps | 200 Mbps (dual camera) | 1 Gbps | 12-20% |
| Field (PROFINET) | 500 Kbps | 1 Mbps | 100 Mbps | < 1% |
| Field (EtherCAT) | 960 Kbps | 1 Mbps | 100 Mbps | ~1% |

The GigE Vision camera traffic is the dominant bandwidth consumer. If both cameras operate simultaneously during quality inspection phases, the control network backbone reaches approximately 200 Mbps. This has not caused PROFINET jitter issues due to VLAN separation and switch QoS configuration, but it should be monitored.

---

## 8. Firewall Rules Summary

The FortiGate 60F is configured with the following inter-zone policy. Detailed rule-by-rule analysis is in the companion document `Firewall_Rules_Audit.md`.

| Direction | Permitted Traffic | Status |
|-----------|------------------|--------|
| Corporate -> DMZ | HTTPS (443) to Remote Access GW only | OK |
| DMZ -> Control | OPC-UA (4840), Modbus (502), HTTPS (443), VNC (5900), SSH (22) | **OVERLY PERMISSIVE** |
| Control -> DMZ | SMB (445), Syslog (514), NTP (123) | Needs review |
| Control -> Field | PROFINET (all), Modbus (502) | **DEFAULT ALLOW** |
| Field -> Control | Reply traffic only | OK (stateful) |
| DMZ -> Field | **BLOCKED** | OK |
| Field -> DMZ | **BLOCKED** | OK |
| Management (99) | SSH (22), SNMP (161), HTTPS (443) from FW only | OK |

**Key findings from AMS-SEC-2025-Q3 audit:**

1. **DMZ to Control zone is too permissive.** Engineering workstations can reach all ports on all control network devices. Should be restricted to specific source-destination-port tuples.
2. **Modbus TCP (port 502) has no application-layer inspection.** Any Modbus function code is permitted, including write-multiple-registers (FC16) which can modify safety-critical setpoints.
3. **VNC (5900) is reachable from the DMZ.** The HMI panel's VNC server can be accessed from engineering workstations without traversing additional authentication.
4. **No IDS/IPS between zones.** The FortiGate has IPS capability but it is not enabled on the OT interfaces due to concerns about latency impact on PROFINET.
5. **SNMP v2c used on management VLAN.** Community string is "public" (read) and "private" (write). Should migrate to SNMPv3.

---

## 9. Recommendations

Based on the current topology and the AMS-SEC-2025-Q3 audit findings:

1. **Implement micro-segmentation** on the control network. The cameras, laser controller, gas analyser, and chiller should be on a separate VLAN (proposed VLAN 25) with firewall rules restricting them to communication with the PLC only.

2. **Enable OPC-UA security.** Transition from SecurityPolicy=None to Basic256Sha256 with SignAndEncrypt mode. Requires certificate deployment to PLC and all OPC-UA clients. See `OPC_UA_Server_Configuration.md` for implementation plan.

3. **Disable HTTP on the HMI.** Enforce HTTPS-only with a minimum of TLS 1.2. Replace the self-signed certificate with one issued from the site CA.

4. **Restrict Modbus TCP access.** Implement application-layer firewall rules that permit only read function codes (FC03, FC04) from the SCADA server and HMI. Write function codes (FC06, FC16) should be permitted only from the engineering workstations during maintenance windows.

5. **Disable VNC or wrap in VPN.** If remote HMI access is required, use the Tosibox VPN gateway with multi-factor authentication rather than exposing VNC directly.

6. **Deploy network monitoring.** Install a passive network tap on the control switch (SW-CTL-01 SPAN port) feeding a Security Onion or similar IDS for OT protocol anomaly detection.

7. **Upgrade SNMP to v3** on all managed switches and the firewall. Remove default community strings.

8. **Implement 802.1X port authentication** on unused switch ports. Currently, unused ports are administratively disabled but not authenticated.

---

## Appendix A: IP Address Allocation

| Subnet | VLAN | Range | Purpose |
|--------|------|-------|---------|
| 10.10.10.0/24 | 10 | .1 = GW, .2 = Switch, .10-.19 = Servers, .20-.29 = Workstations, .30-.39 = Infrastructure | DMZ |
| 10.10.20.0/24 | 20 | .1 = GW, .2 = Switch, .10-.19 = PLCs, .50-.59 = HMIs, .60-.69 = SCADA, .70-.79 = Instruments, .80-.89 = Cameras | Control |
| 10.10.30.0/24 | 30 | .1 = GW, .2 = Switch, .10-.19 = PROFINET IO, .20-.29 = EtherCAT, .30-.39 = Gateways | Field |
| 10.10.99.0/24 | 99 | .1 = FW, .2-.10 = Switches | Management (OOB) |

## Appendix B: Cable Schedule

All inter-switch links use Cat6A S/FTP cabling. Maximum run length in Cell 3 is 22 metres. EtherCAT segment uses dedicated Cat6A cables with industrial M12 connectors (X-coded). PROFINET uses Cat5e with RJ45 industrial connectors (IE FC RJ45 Plug 180).
