# Firewall Rules Audit - AMS-500 Network

**Document ID:** AMS-FW-AUDIT-001 Rev.A  
**Classification:** COMPANY CONFIDENTIAL  
**Auditor:** K. Okonkwo, ICS Security Team  
**Audit Date:** 2025-10-15  
**Firewall:** FortiGate 60F (FW-AMS-01), FortiOS 7.4.3  
**Audit Scope:** All inter-zone policies for the AMS-500 manufacturing cell  

---

## 1. Executive Summary

This document presents the findings of a firewall rule audit conducted on FortiGate 60F (FW-AMS-01) protecting the AMS-500 additive manufacturing system. The audit evaluated all inter-zone traffic policies against IEC 62443-3-3 requirements for Security Level 2 (SL-2) and the site OT security policy (POL-OT-SEC-003 Rev.2).

**Overall Assessment: FAIL**

The firewall configuration contains several critical and high-risk findings that undermine the intended zone-based security model. The most significant issues are:

- **Overly permissive rules** between the DMZ and Control zones that effectively allow unrestricted access from engineering workstations to all control network devices.
- **No application-layer inspection** for industrial protocols (Modbus TCP, OPC-UA), allowing unrestricted function codes and service calls.
- **Default-allow policies** between the Control and Field zones, negating the purpose of zone separation.
- **Management services** (VNC, SNMP) accessible across zone boundaries without adequate controls.

**Findings Summary:**

| Severity | Count |
|----------|-------|
| Critical | 3 |
| High | 5 |
| Medium | 4 |
| Low | 3 |
| Informational | 2 |
| **Total** | **17** |

---

## 2. Firewall Rule Table

The following rules are configured on FW-AMS-01. Rules are evaluated in order; first match applies. The final implicit rule is deny-all (not shown).

| Rule ID | Name | Source Zone | Source Address | Dest Zone | Dest Address | Service / Port | Protocol | Action | Log | Schedule | Status |
|---------|------|------------|---------------|-----------|-------------|---------------|----------|--------|-----|----------|--------|
| 1 | Corporate-to-RAS | WAN | 10.0.0.0/8 | DMZ | 10.10.10.30 | HTTPS (443) | TCP | ALLOW | Yes | Always | Enabled |
| 2 | DMZ-to-OPC-UA | DMZ | 10.10.10.0/24 | Control | 10.10.20.10 | TCP/4840 | TCP | ALLOW | Yes | Always | Enabled |
| 3 | DMZ-to-Modbus | DMZ | 10.10.10.0/24 | Control | 10.10.20.10 | TCP/502 | TCP | ALLOW | Yes | Always | Enabled |
| 4 | DMZ-to-HMI-Web | DMZ | 10.10.10.0/24 | Control | 10.10.20.50 | HTTP (80), HTTPS (443) | TCP | ALLOW | Yes | Always | Enabled |
| 5 | DMZ-to-HMI-VNC | DMZ | 10.10.10.0/24 | Control | 10.10.20.50 | TCP/5900 | TCP | ALLOW | No | Always | Enabled |
| 6 | DMZ-to-Control-SSH | DMZ | 10.10.10.20-21 | Control | 10.10.20.0/24 | SSH (22) | TCP | ALLOW | Yes | Always | Enabled |
| 7 | DMZ-to-SCADA-Web | DMZ | 10.10.10.0/24 | Control | 10.10.20.60 | HTTPS (443) | TCP | ALLOW | Yes | Always | Enabled |
| 8 | ENG-to-Control-All | DMZ | 10.10.10.20-21 | Control | 10.10.20.0/24 | ALL | ALL | ALLOW | No | Always | Enabled |
| 9 | Control-to-DMZ-SMB | Control | 10.10.20.50 | DMZ | 10.10.10.40 | SMB (445) | TCP | ALLOW | Yes | Always | Enabled |
| 10 | Control-to-DMZ-Syslog | Control | 10.10.20.0/24 | DMZ | 10.10.10.10 | UDP/514 | UDP | ALLOW | No | Always | Enabled |
| 11 | Control-to-DMZ-NTP | Control | 10.10.20.0/24 | DMZ | 10.10.10.10 | NTP (123) | UDP | ALLOW | No | Always | Enabled |
| 12 | Control-to-Field-All | Control | 10.10.20.0/24 | Field | 10.10.30.0/24 | ALL | ALL | ALLOW | No | Always | Enabled |
| 13 | Field-to-Control-Reply | Field | 10.10.30.0/24 | Control | 10.10.20.0/24 | ALL (established) | ALL | ALLOW | No | Always | Enabled |
| 14 | MGMT-Switch-Access | MGMT | 10.10.99.1 | MGMT | 10.10.99.0/24 | SSH (22), SNMP (161), HTTPS (443) | TCP/UDP | ALLOW | Yes | Always | Enabled |
| 15 | MGMT-to-All-SNMP | MGMT | 10.10.99.0/24 | DMZ, Control | 10.10.10.0/24, 10.10.20.0/24 | SNMP (161,162) | UDP | ALLOW | No | Always | Enabled |
| 16 | Historian-to-PLC-OPCUA | DMZ | 10.10.10.10 | Control | 10.10.20.10 | TCP/4840 | TCP | ALLOW | Yes | Always | Enabled |
| 17 | DMZ-to-Field-Block | DMZ | 10.10.10.0/24 | Field | 10.10.30.0/24 | ALL | ALL | DENY | Yes | Always | Enabled |
| 18 | Field-to-DMZ-Block | Field | 10.10.30.0/24 | DMZ | 10.10.10.0/24 | ALL | ALL | DENY | Yes | Always | Enabled |

---

## 3. Findings

### Finding F-001: Engineering Workstations Have Unrestricted Access to Control Network

**Severity: CRITICAL**  
**Rule:** #8 (ENG-to-Control-All)  
**IEC 62443 Ref:** SR 5.1 (Network segmentation)  

**Description:**  
Rule 8 allows ALL traffic from engineering workstations (10.10.10.20-21) to the entire control network (10.10.20.0/24). This rule overrides the more specific rules 2-7, effectively granting unrestricted access from the DMZ to every device on the control network on every port and protocol.

**Impact:**  
A compromised engineering workstation provides full, unrestricted network access to all PLCs, the safety PLC, the HMI, SCADA server, laser controller, gas analyser, chiller, and cameras. This negates the purpose of the DMZ/Control zone boundary.

**Evidence:**  
Port scan from ENG-WS-01 (10.10.10.20) shows all 65535 TCP ports reachable on PLC (10.10.20.10), including PROFINET diagnostic ports (34962-34964), Siemens proprietary ports (102/TCP for S7comm), and the web server (80, 443).

**Recommendation:**  
Remove Rule 8 entirely. Create specific rules for each required engineering access path:
- TIA Portal to PLC: TCP/102 (S7comm), TCP/4840 (OPC-UA), TCP/443 (Web)
- TIA Portal to Safety PLC: TCP/102, TCP/443
- File transfer to SCADA: TCP/445 (SMB), restricted to specific shares

Apply a time-based schedule limiting engineering access to working hours (07:00-19:00 Mon-Fri) or require explicit enable by security team.

---

### Finding F-002: Modbus TCP With No Application-Layer Filtering

**Severity: CRITICAL**  
**Rule:** #3 (DMZ-to-Modbus), #12 (Control-to-Field-All)  
**IEC 62443 Ref:** SR 3.5 (Input validation)  

**Description:**  
Modbus TCP (port 502) is permitted from the entire DMZ subnet to the PLC, and from the entire control network to the field network, with no restriction on Modbus function codes. The FortiGate 60F supports Modbus application-layer inspection via its IPS engine, but this feature is not enabled.

**Impact:**  
Any host in the DMZ or control network can issue Modbus write commands (Function Code 6: Write Single Register, Function Code 16: Write Multiple Registers) to the PLC. Because Modbus TCP has no authentication, this allows modification of safety-critical setpoints including:
- HR40100: Laser power setpoint (0-500W)
- HR40102: O2 threshold (affects laser interlock)
- HR40103: Build start command
- HR40107: Fault reset command

A deliberately crafted Modbus write to HR40100 could increase laser power to maximum (500W) while simultaneously raising the O2 threshold via HR40102, defeating the safety interlock.

**Recommendation:**  
1. Enable FortiGate IPS with Modbus application-layer inspection.
2. Configure policy to allow only Function Codes 3 (Read Holding Registers) and 4 (Read Input Registers) from SCADA and HMI.
3. Allow Function Code 6 and 16 (write) only from engineering workstations, only during scheduled maintenance windows, and only to registers HR40100-HR40120.
4. Log all Modbus write operations with source IP and register addresses.

---

### Finding F-003: Default-Allow Between Control and Field Zones

**Severity: CRITICAL**  
**Rule:** #12 (Control-to-Field-All)  
**IEC 62443 Ref:** SR 5.1 (Network segmentation)  

**Description:**  
Rule 12 permits ALL traffic from the control network to the field network without any protocol or port restriction. This means any device on the control network can communicate with any field device using any protocol.

**Impact:**  
The field network hosts the EtherCAT master (BeagleBone Black), PROFINET IO racks, and the Modbus RTU-TCP gateway. Unrestricted access from the control zone means:
- The SCADA server or cameras (which should have no business communicating with field devices) can reach the EtherCAT master.
- The HMI's VNC server, if compromised, provides a pivot point into the field network.
- SSH access to the BeagleBone Black (10.10.30.20) is possible from any control network device.

**Recommendation:**  
Replace Rule 12 with specific allow rules:
- PLC (10.10.20.10-12) to Field (10.10.30.0/24): PROFINET (ethertype 0x8892), Modbus TCP (502)
- No other control network devices should access the field network directly.
- Block SSH from the control network to the field network; require management VLAN for switch/BBB administration.

---

### Finding F-004: VNC Accessible From DMZ Without Additional Authentication

**Severity: HIGH**  
**Rule:** #5 (DMZ-to-HMI-VNC)  
**IEC 62443 Ref:** SR 1.1 (Human user identification and authentication)  

**Description:**  
VNC port 5900 on the HMI (10.10.20.50) is accessible from the entire DMZ subnet. The VNC server uses an 8-character DES-encrypted password ("ams500") which can be brute-forced in seconds. VNC provides full desktop access to the HMI, including the ability to operate the machine, modify setpoints, and access the HMI's local configuration including stored OPC-UA connection parameters.

**Impact:**  
An attacker with access to any DMZ host can gain full interactive control of the HMI within seconds. From the HMI, they can operate the AMS-500 machine through the legitimate operator interface, making malicious actions indistinguishable from normal operator activity.

**Evidence:**  
VNC connection successfully established from ENG-WS-01 using the password "ams500". Full desktop access confirmed, including ability to start builds, modify setpoints, and access configuration menus.

**Recommendation:**  
1. Disable VNC on the HMI or restrict to localhost only.
2. If remote HMI access is required, route through the Tosibox VPN gateway (RAS-01) with multi-factor authentication.
3. If VNC must remain, change to a strong password, enable TLS encryption, and restrict source to a single jump host.

---

### Finding F-005: OPC-UA Accessible With No Authentication

**Severity: HIGH**  
**Rule:** #2 (DMZ-to-OPC-UA), #16 (Historian-to-PLC-OPCUA)  
**IEC 62443 Ref:** SR 1.1, SR 3.1 (Communication integrity)  

**Description:**  
OPC-UA port 4840 is accessible from the DMZ and the OPC-UA server is configured with SecurityPolicy=None and Anonymous authentication. See `OPC_UA_Server_Configuration.md` for full details.

**Impact:**  
Any host in the DMZ can read all process data, write setpoints, issue commands (build start, fault reset), and access 72 hours of historical data. The unencrypted connection also allows passive eavesdropping and man-in-the-middle attacks.

**Recommendation:**  
1. Restrict Rule 2 source to HIST-01 (10.10.10.10) only. Remove the /24 source.
2. Enable OPC-UA security as per the implementation plan in `OPC_UA_Server_Configuration.md`.
3. Remove Rule 16 as it is redundant with Rule 2 (Rule 2 already covers HIST-01's access; Rule 16 was likely added because Rule 2's broad source mask was not understood).

---

### Finding F-006: No Logging on Several Critical Rules

**Severity: HIGH**  
**Rule:** #5, #8, #10, #11, #12, #13, #15  
**IEC 62443 Ref:** SR 6.1 (Audit log accessibility), SR 6.2 (Continuous monitoring)  

**Description:**  
Seven rules, including the most permissive rules (8 and 12), have logging disabled. This means traffic matched by these rules generates no firewall log entries, eliminating visibility into potentially malicious activity.

**Impact:**  
Without logging on Rule 8, there is no record of engineering workstation access to the control network. Without logging on Rule 12, there is no record of control-to-field traffic. An attacker or insider could exploit these paths without generating any firewall alerts or forensic evidence.

**Recommendation:**  
Enable logging on all rules. At minimum, enable logging on rules 5, 8, 12, and 15. Configure log forwarding to the historian/syslog server (10.10.10.10) and implement a 90-day log retention policy.

---

### Finding F-007: HTTP Permitted to HMI Alongside HTTPS

**Severity: HIGH**  
**Rule:** #4 (DMZ-to-HMI-Web)  
**IEC 62443 Ref:** SR 3.1 (Communication integrity)  

**Description:**  
Rule 4 permits both HTTP (80) and HTTPS (443) to the HMI web server. The HMI does not redirect HTTP to HTTPS. Authentication credentials (username/password) submitted via the HTTP login page are transmitted in cleartext.

**Impact:**  
Credentials can be captured by passive network monitoring or ARP spoofing on the DMZ network. The HMI admin credentials, if captured, grant full administrative access to the HMI including user management and configuration changes.

**Recommendation:**  
1. Remove port 80 from Rule 4. Allow only HTTPS (443).
2. Configure the HMI web server to redirect HTTP to HTTPS (see `hmi_webserver_config.xml`).
3. Deploy a CA-signed certificate to eliminate browser warnings that train operators to ignore security errors.

---

### Finding F-008: SMB Traffic Uses Potentially Legacy Protocol

**Severity: HIGH**  
**Rule:** #9 (Control-to-DMZ-SMB)  
**IEC 62443 Ref:** SR 3.1 (Communication integrity)  

**Description:**  
The HMI archives data logs to the NAS (10.10.10.40) via SMB on port 445. Packet capture reveals SMBv1 negotiation attempts alongside SMBv2/v3. The NAS (Synology DS920+) has SMBv1 enabled for compatibility. SMB credentials are stored in plaintext in the HMI configuration file.

**Impact:**  
SMBv1 is vulnerable to multiple well-known attacks (EternalBlue/MS17-010, relay attacks). The stored plaintext credentials ("ams_data" / "D@taL0g2024!") in the HMI config file (hmi_webserver_config.xml) provide lateral movement capability if the HMI is compromised.

**Recommendation:**  
1. Disable SMBv1 on the NAS. Enforce SMBv3 with encryption.
2. Create a dedicated service account with write-only access to the archive share.
3. Store SMB credentials in the HMI's encrypted credential store rather than plaintext XML.
4. Consider replacing SMB with a push-based mechanism (syslog, SFTP) that does not require stored credentials on the HMI.

---

### Finding F-009: SNMP v2c With Default Community Strings

**Severity: MEDIUM**  
**Rule:** #15 (MGMT-to-All-SNMP)  
**IEC 62443 Ref:** SR 1.1 (Identification and authentication)  

**Description:**  
SNMP v2c is used for network monitoring with community strings "public" (read) and "private" (read-write). These are the factory default values and are the first strings attempted by any network scanning tool.

**Impact:**  
The "private" community string provides read-write SNMP access to all switches, allowing an attacker to modify switch configurations, disable ports, alter VLAN assignments, or disable spanning tree. This could be used to bridge the field network directly to the DMZ, bypassing the firewall entirely.

**Recommendation:**  
1. Migrate to SNMPv3 with authentication (SHA) and encryption (AES-128).
2. If SNMPv2c must be retained temporarily, change community strings to non-default values.
3. Restrict SNMP write access to the firewall management IP (10.10.99.1) only.

---

### Finding F-010: Syslog Transmitted Unencrypted

**Severity: MEDIUM**  
**Rule:** #10 (Control-to-DMZ-Syslog)  
**IEC 62443 Ref:** SR 3.1 (Communication integrity), SR 6.1 (Audit log accessibility)  

**Description:**  
Syslog messages from all control network devices are sent to the historian (10.10.10.10) via UDP/514 without encryption or authentication. Syslog over UDP is also unreliable (no delivery confirmation).

**Impact:**  
Syslog messages can be intercepted, modified, or suppressed by an attacker on the network. An attacker could inject false log entries or suppress alerts to cover their tracks.

**Recommendation:**  
1. Migrate to syslog over TLS (TCP/6514) per RFC 5425.
2. If the historian does not support TLS syslog, use TCP/514 at minimum for reliable delivery.
3. Implement log integrity verification (hash chaining or signed timestamps).

---

### Finding F-011: NTP Without Authentication

**Severity: MEDIUM**  
**Rule:** #11 (Control-to-DMZ-NTP)  
**IEC 62443 Ref:** SR 3.1 (Communication integrity)  

**Description:**  
NTP synchronisation occurs between the control network and the historian server without NTP authentication (symmetric key or NTS). The PLC acts as the NTP master for the control and field networks.

**Impact:**  
An attacker who can inject or modify NTP packets could shift the time on the PLC and all downstream devices. This affects:
- Alarm timestamps (forensic accuracy)
- Build process timing (layer exposure calculations)
- Certificate validity checks (if OPC-UA security is later enabled)
- Log correlation between zones

**Recommendation:**  
1. Enable NTP symmetric key authentication between the PLC and the historian.
2. Consider deploying a dedicated GPS-disciplined NTP server on the management network as a stratum-1 source.

---

### Finding F-012: No IDS/IPS on OT Interfaces

**Severity: MEDIUM**  
**Rule:** Global (not rule-specific)  
**IEC 62443 Ref:** SR 6.2 (Continuous monitoring)  

**Description:**  
The FortiGate 60F supports IPS with OT protocol signatures (including Modbus, OPC-UA, S7comm, EtherNet/IP). The IPS engine is enabled on the WAN interface but disabled on the DMZ, Control, and Field interfaces due to concerns about added latency affecting PROFINET cycle times.

**Impact:**  
No detection of protocol anomalies, known exploit signatures, or policy violations on inter-zone OT traffic.

**Recommendation:**  
1. Enable IPS in monitor-only mode (detect, do not block) on the DMZ-to-Control and Control-to-Field policies.
2. Measure latency impact before enabling blocking mode. PROFINET traffic is Layer 2 and does not traverse the firewall, so IPS on the firewall should not impact PROFINET timing.
3. Configure OT-specific IPS signatures for Modbus write function codes, S7comm CPU stop commands, and OPC-UA security policy downgrade attempts.

---

### Finding F-013: Firewall Admin Interface on Same Network as Data Traffic

**Severity: LOW**  
**Rule:** #14 (MGMT-Switch-Access)  
**IEC 62443 Ref:** SR 5.1 (Network segmentation)  

**Description:**  
The firewall management interface is on VLAN 99 (10.10.99.0/24), which is properly separated from data VLANs. However, the management VLAN is trunked across the same physical switch infrastructure as the data VLANs. A VLAN hopping attack (double-tagging) on the Cisco IE-4010 could potentially reach the management VLAN.

**Recommendation:**  
1. Verify that the native VLAN on all trunk ports is set to an unused VLAN (not 1, not 99).
2. Enable VLAN access lists (VACLs) on the switches to restrict inter-VLAN traffic at the switch level.
3. Consider a physically separate management switch for the most critical scenario.

---

### Finding F-014: No Egress Filtering From OT Zones

**Severity: LOW**  
**Rule:** Global  
**IEC 62443 Ref:** SR 5.2 (Zone boundary protection)  

**Description:**  
There are no rules restricting outbound traffic from the control or field zones to the WAN (corporate network). While the implicit deny-all blocks undefined traffic, there is no explicit egress policy documenting what should and should not leave the OT environment.

**Recommendation:**  
1. Add explicit deny rules for Control/Field to WAN with logging enabled.
2. Document the intended zero-egress policy for the OT zones.
3. Alert on any WAN-destined traffic from OT zones as it would indicate either misconfiguration or compromise.

---

### Finding F-015: Firewall Rule Comments Missing or Inaccurate

**Severity: LOW**  
**Rule:** Multiple  

**Description:**  
Several rules lack descriptive comments. Rule 8 is named "ENG-to-Control-All" which accurately describes its function but provides no justification for why ALL traffic is permitted. Rule 16 duplicates Rule 2's coverage without explanation.

**Recommendation:**  
1. Add comments to all rules documenting the business justification, the requester, and the approval reference.
2. Conduct a quarterly rule review to identify and remove redundant, shadowed, or obsolete rules.

---

### Finding F-016: No Rate Limiting on Modbus TCP

**Severity: INFORMATIONAL**  
**Rule:** #3 (DMZ-to-Modbus)  

**Description:**  
No connection rate limiting or concurrent session limits are configured for Modbus TCP traffic. A single host could open hundreds of simultaneous Modbus connections to the PLC.

**Recommendation:**  
Configure DoS protection policy limiting Modbus TCP connections per source IP to 5 concurrent sessions and 10 new connections per second.

---

### Finding F-017: Rule Ordering Creates Redundancy

**Severity: INFORMATIONAL**  
**Rule:** #2, #3, #4, #5, #7 vs #8  

**Description:**  
Rules 2-7 define specific permitted traffic from the DMZ to the control network. However, Rule 8 permits ALL traffic from engineering workstations (10.10.10.20-21) to the entire control network. Since the engineering workstations are within 10.10.10.0/24, Rule 8 makes Rules 2, 3, 4, 5, and 7 redundant for those specific source hosts.

**Recommendation:**  
After removing Rule 8 (as per Finding F-001), Rules 2-7 will correctly define the permitted traffic. No action needed beyond addressing F-001.

---

## 4. Risk Summary Matrix

| Finding | Severity | CVSS-like Score | Exploitability | Remediation Effort | Priority |
|---------|----------|----------------|---------------|-------------------|----------|
| F-001 | Critical | 9.1 | Easy (any DMZ host) | Low (rule change) | P1 - Immediate |
| F-002 | Critical | 8.8 | Easy (Modbus write tool) | Medium (enable IPS) | P1 - Immediate |
| F-003 | Critical | 8.5 | Easy (any control host) | Low (rule change) | P1 - Immediate |
| F-004 | High | 8.1 | Easy (VNC brute-force) | Low (disable VNC) | P1 - Within 1 week |
| F-005 | High | 7.8 | Easy (OPC-UA client) | Medium (see OPCUA doc) | P2 - Within 2 weeks |
| F-006 | High | 7.5 | N/A (detection gap) | Low (enable logging) | P1 - Immediate |
| F-007 | High | 7.2 | Medium (MITM required) | Low (rule change) | P2 - Within 2 weeks |
| F-008 | High | 7.0 | Medium (network access) | Medium (config changes) | P2 - Within 2 weeks |
| F-009 | Medium | 6.5 | Easy (default creds) | Low (change strings) | P2 - Within 2 weeks |
| F-010 | Medium | 5.3 | Medium (MITM required) | Medium (TLS syslog) | P3 - Within 30 days |
| F-011 | Medium | 5.0 | Medium (NTP spoofing) | Low (enable auth) | P3 - Within 30 days |
| F-012 | Medium | 5.0 | N/A (detection gap) | Medium (enable IPS) | P3 - Within 30 days |
| F-013 | Low | 3.7 | Difficult (VLAN hop) | Low (config tweak) | P4 - Within 90 days |
| F-014 | Low | 3.5 | N/A (policy gap) | Low (add deny rules) | P4 - Within 90 days |
| F-015 | Low | 2.0 | N/A (documentation) | Low (add comments) | P4 - Within 90 days |
| F-016 | Info | 2.0 | Medium (DoS) | Low (rate limit) | P4 - Within 90 days |
| F-017 | Info | 1.0 | N/A (redundancy) | Low (rule cleanup) | Resolved by F-001 |

---

## 5. Remediation Timeline

### Immediate (within 48 hours)
- **F-001:** Remove Rule 8. Replace with specific engineering access rules.
- **F-003:** Replace Rule 12 with PLC-only access to field network.
- **F-006:** Enable logging on all rules.

### Within 1 week
- **F-004:** Disable VNC or restrict access to VPN gateway.
- **F-002:** Enable Modbus application-layer inspection (monitor mode initially).

### Within 2 weeks
- **F-005:** Restrict OPC-UA source addresses; begin OPC-UA security hardening.
- **F-007:** Remove HTTP from HMI firewall rule; enable HTTPS redirect.
- **F-008:** Disable SMBv1 on NAS; rotate SMB credentials.
- **F-009:** Change SNMP community strings; plan SNMPv3 migration.

### Within 30 days
- **F-010:** Deploy syslog over TLS.
- **F-011:** Enable NTP authentication.
- **F-012:** Enable IPS in monitor mode on OT interfaces.

### Within 90 days
- **F-013:** Verify VLAN security on trunk ports.
- **F-014:** Implement explicit egress deny rules with alerting.
- **F-015:** Complete rule documentation and establish quarterly review process.
- **F-016:** Configure Modbus connection rate limiting.

---

## 6. Appendix: Test Methodology

The audit was conducted using the following approach:

1. **Configuration review:** FortiGate configuration exported via `exec backup config` and analysed offline.
2. **Active testing:** Port scans (Nmap) and protocol-specific tests (Metasploit Modbus modules, UaExpert OPC-UA client) conducted from the DMZ (ENG-WS-01) and control network (SCADA-01) during a scheduled maintenance window.
3. **Traffic analysis:** 4-hour packet capture on SW-CTL-01 SPAN port during normal build operation, analysed with Wireshark and Zeek.
4. **Policy comparison:** Rules compared against the approved network security design document (AMS-NET-001 Rev.C) and IEC 62443-3-3 SL-2 requirements.

All testing was conducted with written authorisation from the Plant Manager and OT Security Lead. No production builds were interrupted during the audit.
