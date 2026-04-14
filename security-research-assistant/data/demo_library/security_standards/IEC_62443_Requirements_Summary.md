# IEC 62443 - Industrial Automation and Control Systems Security: Summary for ICS Assessors

**Document Classification:** OFFICIAL  
**Author:** ICS Security Research Team  
**Last Updated:** 2026-03-28  
**Revision:** 2.1  
**Applicable System:** AMS-500 Additive Manufacturing System  

---

## 1. Introduction

IEC 62443 (formerly ISA-99, also published as ISA/IEC 62443) is the primary international standard series for industrial automation and control system (IACS) cybersecurity. It provides a comprehensive framework addressing the entire lifecycle of industrial control system security -- from risk assessment and system architecture through to component-level requirements, maintenance, and patch management.

The standard series is organised into four groups:

| Group | Title | Parts | Audience |
|-------|-------|-------|----------|
| **1 - General** | Concepts, models, terminology | 1-1 to 1-5 | All stakeholders |
| **2 - Policies & Procedures** | Security management system for asset owners | 2-1 to 2-4 | Asset owners, operators |
| **3 - System** | System-level security requirements and security levels | 3-1 to 3-3 | System integrators, architects |
| **4 - Component** | Component-level security requirements | 4-1 to 4-2 | Product suppliers, developers |

For the AMS-500 security assessment, IEC 62443 provides the normative framework against which the system's security posture is evaluated. This document summarises the key concepts and requirements, then maps them to findings on the AMS-500.

---

## 2. Zones and Conduits Model

### 2.1 Concept

IEC 62443-3-2 defines the concept of **zones** and **conduits** as the foundation of IACS network architecture security.

**Zone:** A logical or physical grouping of assets that share common security requirements. Each zone has an assigned Security Level (SL). Assets within a zone should have a consistent trust level.

**Conduit:** A communication channel between zones that controls the flow of data. Conduits define the permitted communication paths and the security mechanisms applied to data crossing zone boundaries (firewalls, DMZs, data diodes, protocol converters).

### 2.2 AMS-500 Zone Decomposition

Based on the assessment, the AMS-500 system should be decomposed into the following zones:

| Zone ID | Name | Assets | Current SL | Target SL |
|---------|------|--------|------------|-----------|
| Z1 | Enterprise Network | MES, ERP, quality database | N/A (out of scope) | N/A |
| Z2 | Supervisory | HMI workstation, OPC UA aggregator, historian | SL1 (assessed) | SL3 |
| Z3 | Control | S7-1500 PLC, safety controller, I/O modules | SL1 (assessed) | SL3 |
| Z4 | Field Devices | EtherCAT drives, sensors, actuators | SL0 (assessed) | SL2 |
| Z5 | Auxiliary Systems | Powder management, gas handling, thermal cameras | SL0 (assessed) | SL2 |
| Z6 | Network Infrastructure | Hirschmann switches, cabling | SL1 (assessed) | SL3 |

**Current state:** The AMS-500 operates as a flat network with no zone segmentation. All devices share the same VLAN (10.10.20.0/24 and 10.10.30.0/24 bridged). There are no conduit-level controls. Any device on the network can communicate with any other device using any protocol.

---

## 3. Security Levels (SL)

IEC 62443 defines four Security Levels representing increasing levels of protection against different threat actor capabilities:

| Security Level | Description | Threat Actor Profile |
|----------------|-------------|---------------------|
| **SL1** | Protection against casual or coincidental violation | Unintentional errors, basic automated tools |
| **SL2** | Protection against intentional violation using simple means | Script kiddies, disgruntled insiders with limited skills |
| **SL3** | Protection against intentional violation using sophisticated means with moderate resources | Hacktivists, criminal groups, moderately skilled insiders |
| **SL4** | Protection against intentional violation using sophisticated means with extended resources and motivation | Nation-state actors, advanced persistent threats |

Each Security Level is assessed across three dimensions:

- **SL-T (Target):** The desired security level, determined by risk assessment.
- **SL-C (Capability):** The security level the system is capable of achieving based on its design and components.
- **SL-A (Achieved):** The security level actually achieved through implementation, configuration, and operational procedures.

**AMS-500 assessment:** Given the nature of the AMS-500 (additive manufacturing of potentially sensitive components for defence or critical infrastructure), the target security level should be **SL3** for the control and supervisory zones. The current achieved security level across all zones is assessed at **SL1** at best, with several foundational requirements failing entirely.

---

## 4. Foundational Requirements (FR)

IEC 62443-3-3 defines seven Foundational Requirements (FRs), each containing System Requirements (SRs) with optional Requirement Enhancements (REs). The SRs are the specific technical requirements that must be met to achieve each Security Level.

### 4.1 FR 1 - Identification and Authentication Control (IAC)

**Purpose:** Identify and authenticate all users (human, software, device) before granting access to the IACS.

| SR | Requirement | SL1 | SL2 | SL3 | SL4 | AMS-500 Status |
|----|-------------|-----|-----|-----|-----|----------------|
| 1.1 | Human user identification and authentication | X | X | X | X | PARTIAL -- HMI has local accounts but uses default credentials (admin/admin) |
| 1.2 | Software process and device identification and authentication | | X | X | X | FAIL -- No device authentication on EtherNet/IP or PROFINET |
| 1.3 | Account management | X | X | X | X | FAIL -- No account management process, no password policy, no account review |
| 1.4 | Identifier management | X | X | X | X | FAIL -- Default identifiers in use |
| 1.5 | Authenticator management | X | X | X | X | FAIL -- Passwords stored in plaintext, default passwords unchanged |
| 1.6 | Wireless access management | | X | X | X | N/A -- No wireless interfaces |
| 1.7 | Strength of password-based authentication | X | X | X | X | FAIL -- Default/trivial passwords (admin, AMS500plc, ams500op) |
| 1.8 | PKI certificates | | | X | X | FAIL -- Self-signed certificates, no CA, no revocation |
| 1.9 | Strength of public key-based authentication | | | X | X | FAIL -- 2048-bit RSA keys, global shared keys on PLC (CVE-2022-38465) |
| 1.10 | Authenticator feedback | X | X | X | X | PASS -- HMI masks password input |
| 1.11 | Unsuccessful login attempts | | X | X | X | FAIL -- No account lockout on HMI, PLC, or OPC UA |
| 1.12 | System use notification | | X | X | X | FAIL -- No login banner or terms of use |
| 1.13 | Access via untrusted networks | | | X | X | FAIL -- No DMZ, no additional authentication for remote access |

**FR 1 Overall Assessment: FAIL (SL1 not met)**

### 4.2 FR 2 - Use Control (UC)

**Purpose:** Enforce the assigned privileges of an authenticated user to control use of the IACS.

| SR | Requirement | SL1 | SL2 | SL3 | SL4 | AMS-500 Status |
|----|-------------|-----|-----|-----|-----|----------------|
| 2.1 | Authorisation enforcement | X | X | X | X | PARTIAL -- PLC has protection levels; no RBAC on HMI or OPC UA |
| 2.2 | Wireless use control | | X | X | X | N/A |
| 2.3 | Use control for portable/mobile devices | | X | X | X | FAIL -- Engineering laptops connect directly to OT network with no MAB or NAC |
| 2.4 | Mobile code | X | X | X | X | FAIL -- No application whitelisting on HMI workstation |
| 2.5 | Session lock | X | X | X | X | FAIL -- HMI workstation has no screen lock timeout |
| 2.6 | Remote session termination | | X | X | X | FAIL -- No mechanism to remotely terminate active sessions |
| 2.7 | Concurrent session control | | | X | X | FAIL -- Multiple simultaneous sessions allowed on all interfaces |
| 2.8 | Auditable events | X | X | X | X | PARTIAL -- PLC logs some events but no centralised audit log |
| 2.9 | Audit storage capacity | X | X | X | X | FAIL -- PLC diagnostic buffer is circular and limited to 3200 entries |
| 2.10 | Response to audit processing failures | | X | X | X | FAIL -- No alerting when audit logs are full or unavailable |
| 2.11 | Timestamps | X | X | X | X | PARTIAL -- PLC has NTP configured but HMI clock drifts (no NTP) |
| 2.12 | Non-repudiation | | | | X | FAIL -- No digital signatures on actions |

**FR 2 Overall Assessment: FAIL (SL1 not met)**

### 4.3 FR 3 - System Integrity (SI)

**Purpose:** Ensure the integrity of the IACS to prevent unauthorised manipulation.

| SR | Requirement | SL1 | SL2 | SL3 | SL4 | AMS-500 Status |
|----|-------------|-----|-----|-----|-----|----------------|
| 3.1 | Communication integrity | | X | X | X | FAIL -- No integrity protection on EtherNet/IP, Modbus TCP; S7CommPlus has HMAC but key is compromisable |
| 3.2 | Malicious code protection | X | X | X | X | FAIL -- No antivirus or application whitelisting on HMI workstation |
| 3.3 | Security functionality verification | X | X | X | X | FAIL -- No regular verification of security configuration |
| 3.4 | Software and information integrity | X | X | X | X | FAIL -- No code signing on PLC programmes, no file integrity monitoring on HMI |
| 3.5 | Input validation | X | X | X | X | PARTIAL -- PLC validates some input ranges; HMI web server has input validation vulnerabilities (CVE-2023-46283) |
| 3.6 | Deterministic output | X | X | X | X | PASS -- PLC outputs go to defined safe state on CPU fault |
| 3.7 | Error handling | X | X | X | X | PARTIAL -- PLC error handling is adequate; HMI error messages reveal internal paths |
| 3.8 | Session integrity | | X | X | X | PARTIAL -- S7CommPlus has session integrity; OPC UA depends on security policy selection |
| 3.9 | Protection of audit information | | X | X | X | FAIL -- PLC diagnostic buffer can be cleared by any authenticated user |

**FR 3 Overall Assessment: FAIL (SL1 partially met)**

### 4.4 FR 4 - Data Confidentiality (DC)

**Purpose:** Ensure the confidentiality of information on communication channels and in data repositories.

| SR | Requirement | SL1 | SL2 | SL3 | SL4 | AMS-500 Status |
|----|-------------|-----|-----|-----|-----|----------------|
| 4.1 | Information confidentiality | | X | X | X | FAIL -- EtherNet/IP, Modbus TCP, PROFINET in cleartext |
| 4.2 | Information persistence | | X | X | X | FAIL -- No secure erasure of recipe data or process logs |
| 4.3 | Use of cryptography | | | X | X | FAIL -- Compromised cryptographic keys on PLC (CVE-2022-38465) |

**FR 4 Overall Assessment: FAIL (SL2 not met)**

### 4.5 FR 5 - Restricted Data Flow (RDF)

**Purpose:** Segment the IACS into zones and control data flow through conduits.

| SR | Requirement | SL1 | SL2 | SL3 | SL4 | AMS-500 Status |
|----|-------------|-----|-----|-----|-----|----------------|
| 5.1 | Network segmentation | X | X | X | X | FAIL -- Flat network, no zone segmentation |
| 5.2 | Zone boundary protection | | X | X | X | FAIL -- No firewalls between zones |
| 5.3 | General-purpose person-to-person communication restrictions | | X | X | X | FAIL -- HMI workstation has unrestricted internet access (via enterprise VLAN bridge) |
| 5.4 | Application partitioning | | | X | X | FAIL -- Single HMI workstation hosts all supervisory applications |

**FR 5 Overall Assessment: FAIL (SL1 not met)**

### 4.6 FR 6 - Timely Response to Events (TRE)

**Purpose:** Respond to security violations by notifying the appropriate authority and taking corrective action.

| SR | Requirement | SL1 | SL2 | SL3 | SL4 | AMS-500 Status |
|----|-------------|-----|-----|-----|-----|----------------|
| 6.1 | Audit log accessibility | X | X | X | X | PARTIAL -- PLC diagnostic buffer accessible via TIA Portal only |
| 6.2 | Continuous monitoring | | | X | X | FAIL -- No network monitoring, no SIEM, no IDS |

**FR 6 Overall Assessment: FAIL (SL1 partially met)**

### 4.7 FR 7 - Resource Availability (RA)

**Purpose:** Ensure the availability of the IACS against denial-of-service attacks and equipment failures.

| SR | Requirement | SL1 | SL2 | SL3 | SL4 | AMS-500 Status |
|----|-------------|-----|-----|-----|-----|----------------|
| 7.1 | DoS protection | X | X | X | X | FAIL -- No rate limiting, connection limits exploitable |
| 7.2 | Resource management | X | X | X | X | PARTIAL -- PLC has watchdog and memory monitoring; no resource management on HMI |
| 7.3 | Control system backup | X | X | X | X | FAIL -- No regular backup of PLC programmes or HMI configuration |
| 7.4 | Control system recovery and reconstitution | X | X | X | X | FAIL -- No documented recovery procedure, no tested restore process |
| 7.5 | Emergency power | X | X | X | X | PASS -- UPS installed with 15-minute runtime |
| 7.6 | Network and security configuration settings | X | X | X | X | FAIL -- No documented baseline, no configuration management |
| 7.7 | Least functionality | X | X | X | X | FAIL -- Unnecessary services running on HMI (IIS, RDP, Telnet) |

**FR 7 Overall Assessment: FAIL (SL1 not met)**

---

## 5. Component Requirements (CR) - Key Items

IEC 62443-4-2 defines Component Requirements (CRs) that map to the System Requirements. For the AMS-500 assessment, the most relevant component-level findings are:

### CR 1.1 - Human User Identification and Authentication
**S7-1500 PLC:** Implements password-based access control at three protection levels, but the cryptographic implementation is compromised (CVE-2022-38465 on firmware < V3.0.1).

### CR 1.2 - Software Process and Device Identification
**EtherNet/IP devices:** No device authentication capability. Any device on the network can communicate with any other.
**PROFINET devices:** PROFINET does not natively authenticate devices. Device substitution is possible.

### CR 2.1 - Authorisation Enforcement
**OPC UA server:** Supports role-based access control but is misconfigured -- anonymous access grants read permissions, default admin account grants full access.

### CR 3.4 - Software and Information Integrity
**S7-1500 PLC (FW V21.9):** No programme code signing. Downloaded programmes are executed without verification of origin or integrity.

### CR 4.1 - Information Confidentiality
**Modbus TCP:** All register reads/writes are in cleartext with no encryption option.
**PROFINET:** All cyclic I/O data is in cleartext.

### CR 7.1 - Denial of Service Protection
**S7-1500 PLC:** Limited to 32 COTP connections and 20 OPC UA sessions. Susceptible to connection exhaustion.

---

## 6. Maturity Levels

IEC 62443-2-4 defines maturity levels for security practices of service providers (system integrators):

| Level | Description | AMS-500 Integrator Assessment |
|-------|-------------|-------------------------------|
| **ML1 - Initial** | Security practices are ad-hoc, undocumented | Current state |
| **ML2 - Managed** | Security practices are documented and repeatable | Not achieved |
| **ML3 - Defined** | Organisation-wide security standards and processes | Not achieved |
| **ML4 - Improving** | Metrics-driven continuous improvement | Not achieved |

The system integrator who deployed the AMS-500 operates at **ML1**. Security configuration was performed on an ad-hoc basis during commissioning with no documentation, no security testing, and no formal handover of security responsibilities to the asset owner.

---

## 7. AMS-500 Gap Analysis Summary

### Critical Gaps (Must Address)

1. **No network segmentation** (FR5, SR 5.1-5.2) -- The flat network architecture is the single most significant finding. All zones share the same network, allowing lateral movement from any compromised device.
2. **Default and trivial credentials** (FR1, SR 1.5, 1.7) -- Default passwords on HMI, PLC, and OPC UA server.
3. **Compromised PLC cryptography** (FR4, SR 4.3) -- CVE-2022-38465 undermines all PLC access controls.
4. **No programme integrity verification** (FR3, SR 3.4) -- PLC programmes can be modified without detection.
5. **No backup or recovery process** (FR7, SR 7.3-7.4) -- No ability to recover from a cyber incident.

### High Gaps (Should Address)

6. **No security monitoring** (FR6, SR 6.2) -- No network monitoring, IDS, or SIEM for the OT environment.
7. **No malicious code protection** (FR3, SR 3.2) -- HMI workstation unprotected.
8. **Unencrypted protocols** (FR4, SR 4.1) -- Modbus TCP, EtherNet/IP, PROFINET all cleartext.
9. **No audit logging** (FR2, SR 2.8-2.10) -- Inadequate logging and no log protection.
10. **Unnecessary services** (FR7, SR 7.7) -- HMI workstation running IIS, RDP, Telnet.

### Medium Gaps (Consider Addressing)

11. **No login banners** (FR1, SR 1.12).
12. **No session management** (FR2, SR 2.5-2.7) -- No screen lock, no session limits.
13. **No NTP on all devices** (FR2, SR 2.11) -- Time synchronisation incomplete.

---

## 8. Remediation Roadmap

| Priority | Action | IEC 62443 Reference | Effort | Timeline |
|----------|--------|---------------------|--------|----------|
| P1 | Implement network segmentation with VLANs and industrial firewall | FR5 SR 5.1-5.2 | High | 4-6 weeks |
| P1 | Change all default credentials, implement password policy | FR1 SR 1.5, 1.7 | Low | 1 week |
| P1 | Upgrade S7-1500 firmware to V3.0.1+ | FR4 SR 4.3 | Medium | 2-3 weeks (requires test) |
| P1 | Establish PLC programme backup and integrity baseline | FR3 SR 3.4, FR7 SR 7.3 | Medium | 1-2 weeks |
| P2 | Deploy ICS network monitoring | FR6 SR 6.2 | High | 6-8 weeks |
| P2 | Install application whitelisting on HMI | FR3 SR 3.2 | Medium | 2-3 weeks |
| P2 | Disable OPC UA SecurityPolicy None and anonymous access | FR1 SR 1.1, FR3 SR 3.1 | Low | 1 day |
| P2 | Remove unnecessary services from HMI (IIS, RDP, Telnet) | FR7 SR 7.7 | Low | 1 day |
| P3 | Implement centralised audit logging (syslog) | FR2 SR 2.8-2.10 | Medium | 2-3 weeks |
| P3 | Deploy NTP across all devices | FR2 SR 2.11 | Low | 1 day |
| P3 | Document incident response procedure | FR6 SR 6.1 | Medium | 2 weeks |

---

## 9. References

- IEC 62443-1-1:2009 -- Concepts and models
- IEC 62443-2-1:2010 -- Establishing an IACS security management system
- IEC 62443-2-4:2015 -- Security program requirements for IACS service providers
- IEC 62443-3-2:2020 -- Security risk assessment for system design
- IEC 62443-3-3:2013 -- System security requirements and security levels
- IEC 62443-4-2:2019 -- Technical security requirements for IACS components
- NIST SP 800-82 Rev 3 -- Guide to Operational Technology Security (2023)
- Siemens, "Industrial Security for SIMATIC S7-1500" (2024)

---

*This document is part of the AMS-500 security assessment working library. Do not distribute outside the assessment team.*
