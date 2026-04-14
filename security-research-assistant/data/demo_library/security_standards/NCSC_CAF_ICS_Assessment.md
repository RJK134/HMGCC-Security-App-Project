# NCSC Cyber Assessment Framework (CAF) - Applied Assessment of AMS-500

**Document Classification:** OFFICIAL  
**Author:** ICS Security Research Team  
**Last Updated:** 2026-04-02  
**Revision:** 1.5  
**Applicable System:** AMS-500 Additive Manufacturing System  
**CAF Version:** 3.2 (2024)  

---

## 1. Introduction

The UK National Cyber Security Centre (NCSC) Cyber Assessment Framework (CAF) provides a systematic approach to assessing the cyber resilience of organisations operating essential services and related systems. Originally developed for operators of essential services (OES) under the NIS Regulations 2018, the CAF has broader applicability as a general-purpose cyber security assessment framework.

This document applies the CAF to the AMS-500 additive manufacturing system operated as part of a critical manufacturing capability. The assessment evaluates the system against the four top-level objectives and their constituent principles, identifying gaps against the indicators of good practice (IGPs).

The CAF uses a three-tier rating system for each contributing outcome:

- **Achieved** -- The outcome is fully met and evidenced.
- **Partially Achieved** -- Some elements are in place but significant gaps remain.
- **Not Achieved** -- The outcome is not met or evidence is absent.

---

## 2. Objective A: Managing Security Risk

Objective A addresses the governance, risk management, and organisational structures needed to manage cyber security risk.

### A1. Governance

**Principle:** The organisation has appropriate management policies and processes in place to govern its approach to the security of network and information systems.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| A1.a | Board-level accountability for cyber security | No identified board-level owner for OT/ICS security. IT security is managed separately with no remit over OT. | Not Achieved |
| A1.b | Organisational structure supports cyber security | No dedicated OT security role. The AMS-500 is managed by the manufacturing engineering team with no security input. | Not Achieved |
| A1.c | Cyber security policies appropriate to the organisation | IT security policies exist but do not cover OT/ICS systems. No OT-specific security policy. | Not Achieved |

### A2. Risk Management

**Principle:** The organisation takes appropriate steps to identify, assess, and understand security risks to network and information systems that support essential services.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| A2.a | Risk management process covers cyber security | No formal risk assessment has been conducted for the AMS-500 or its OT network. The manufacturing risk register covers physical safety (laser hazards, powder handling) but not cyber security. | Not Achieved |
| A2.b | Risk assessment identifies key assets and dependencies | No OT asset inventory. The AMS-500 system diagram dates from the original installation (2023) and has not been updated since commissioning. Network architecture is undocumented. | Not Achieved |
| A2.c | Risk management informs security decisions | No evidence that security configuration decisions are risk-informed. Default configurations were accepted without assessment. | Not Achieved |

### A3. Asset Management

**Principle:** The organisation determines and actively manages all assets that are critical to the essential service.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| A3.a | Asset management covers all relevant assets | No comprehensive OT asset register. Individual device IP addresses and firmware versions are not tracked. Discovery scan during this assessment identified 4 devices not present in any documentation. | Not Achieved |
| A3.b | Asset management supports risk assessment | No linkage between asset management and risk assessment. | Not Achieved |

### A4. Supply Chain

**Principle:** The organisation understands and manages security risks to network and information systems that arise from dependencies on external suppliers.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| A4.a | Supply chain risk understanding | No assessment of supply chain risk. The AMS-500 vendor has remote support access via a VPN connection that is left permanently active -- the vendor can access the HMI workstation and PLC at any time. No monitoring of vendor access. | Not Achieved |
| A4.b | Supply chain security requirements | No security requirements in the AMS-500 procurement contract. The maintenance agreement does not reference cyber security obligations. | Not Achieved |

**Objective A Overall: Not Achieved -- No governance, risk management, or asset management processes exist for the AMS-500 OT environment.**

---

## 3. Objective B: Protecting Against Cyber Attack

Objective B addresses the technical and procedural security controls that protect networks and information systems.

### B1. Service Protection Policies and Processes

**Principle:** The organisation defines, implements, communicates, and enforces security policies and processes.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| B1.a | Policy and process development | No OT-specific security policies. No change management process for PLC programme modifications. | Not Achieved |
| B1.b | Policy and process implementation | N/A (no policies to implement). | Not Achieved |

### B2. Identity and Access Management

**Principle:** The organisation controls access to its networks and information systems through user identity management and authentication.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| B2.a | Identity verification and access management | Default credentials in use across the system: HMI admin/admin, PLC password AMS500plc, OPC UA admin/admin. No user identity management process. Shared accounts used by all operators. | Not Achieved |
| B2.b | Privileged user management | No distinction between operator and administrator access. All users have the same admin account credentials. The PLC engineering password is known to all manufacturing engineers. | Not Achieved |
| B2.c | Authentication and access control | No multi-factor authentication. No account lockout. No session timeout on HMI workstation. OPC UA server accepts anonymous connections. | Not Achieved |

### B3. Data Security

**Principle:** The organisation protects stored and electronically transmitted data.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| B3.a | Data in transit protection | All industrial protocols (Modbus TCP, EtherNet/IP, PROFINET) operate in cleartext. OPC UA configured to accept SecurityPolicy None. S7CommPlus encryption undermined by CVE-2022-38465. | Not Achieved |
| B3.b | Data at rest protection | Recipe data and process logs stored on the HMI workstation without encryption. PLC programme blocks are not encrypted (compromised global key). No disk encryption on the HMI workstation. | Not Achieved |
| B3.c | Data sanitisation | No data sanitisation procedures. Recipe data from previous builds remains on the system indefinitely. No secure deletion capability. | Not Achieved |

### B4. System Security

**Principle:** The organisation manages and maintains the security of network and information systems.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| B4.a | Secure design | The AMS-500 was designed and installed with no security architecture. Flat network, no segmentation, no defence-in-depth. | Not Achieved |
| B4.b | Secure configuration | Default configurations on all devices. HMI workstation runs unnecessary services (IIS on port 80, RDP on port 3389, Telnet on port 23). PLC web server enabled with default configuration. Hirschmann switches use factory default credentials (admin/private). | Not Achieved |
| B4.c | Secure management | Engineering workstation connects directly to the OT network. TIA Portal project files stored on the engineering workstation without access controls. No separation between engineering and operational access. | Not Achieved |
| B4.d | Vulnerability management | No vulnerability management process for OT systems. No tracking of CVEs affecting installed devices. The S7-1500 has 4 unpatched critical vulnerabilities (see vulnerability advisory). No patch management process -- firmware has not been updated since installation. | Not Achieved |

### B5. Resilience

**Principle:** The organisation builds resilience against cyber attack.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| B5.a | Resilience preparation | No business continuity plan for cyber incidents affecting the AMS-500. No documented recovery procedures. | Not Achieved |
| B5.b | Design for resilience | No redundancy in the control system. Single PLC, single HMI, single network path. Failure of any component halts production. | Not Achieved |
| B5.c | Backups | No regular backup of PLC programmes, HMI configuration, or switch configurations. The only copy of the PLC programme is on the engineering workstation (last saved 2024-06-15, over 20 months ago). | Not Achieved |

### B6. Staff Awareness and Training

**Principle:** Staff are trained to manage the security of network and information systems.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| B6.a | Cyber security training | Manufacturing operators have received no cyber security training. Engineers rely on generic IT security awareness training that does not cover OT-specific risks. | Not Achieved |
| B6.b | Cyber security culture | No evidence of security culture in the OT environment. USB drives are routinely used to transfer files to the HMI workstation. Personal devices are connected to the OT network for convenience. | Not Achieved |

**Objective B Overall: Not Achieved -- Fundamental security controls are absent across all B-series principles.**

---

## 4. Objective C: Detecting Cyber Security Events

Objective C addresses the capability to detect potential security incidents affecting network and information systems.

### C1. Security Monitoring

**Principle:** The organisation monitors the security status of its networks and information systems.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| C1.a | Monitoring coverage | No network monitoring on the OT network. No IDS/IPS. No SIEM integration. No netflow collection. The Hirschmann switches support port mirroring (SPAN) but this is not configured. | Not Achieved |
| C1.b | Securing monitoring logs | No logs to secure -- logging is not implemented. The PLC diagnostic buffer is the only source of operational event data and is limited to 3200 circular entries with no external backup. | Not Achieved |
| C1.c | Generating alerts | No alerting capability for security events. The only alerts are process alarms (temperature, pressure, laser faults) displayed on the HMI -- these are operational, not security, alerts. | Not Achieved |

### C2. Proactive Security Event Discovery

**Principle:** The organisation detects, within its networks and information systems, activity indicative of potential security incidents.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| C2.a | System abnormality detection | No baseline of normal network behaviour exists. No mechanism to detect abnormal traffic, new devices, or unexpected connections. | Not Achieved |
| C2.b | Attack detection | No attack detection capability. Common ICS attack patterns (port scanning, PLC stop/start, programme download, Modbus write to sensitive registers) would not be detected. | Not Achieved |

**Objective C Overall: Not Achieved -- No detection capability exists. The AMS-500 is effectively blind to security events.**

---

## 5. Objective D: Minimising the Impact of Cyber Security Incidents

Objective D addresses the capability to minimise the impact of cyber security incidents.

### D1. Response and Recovery Planning

**Principle:** The organisation plans and prepares to respond to and recover from cyber security incidents.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| D1.a | Response plan | No incident response plan for cyber security incidents affecting the AMS-500 or OT systems. The organisation has an IT incident response plan, but it does not cover OT systems and the IT security team has no authority or access to the OT environment. | Not Achieved |
| D1.b | Recovery plan | No recovery plan. No documented procedure for restoring the AMS-500 from a known-good state. No recovery time objective (RTO) or recovery point objective (RPO) defined. | Not Achieved |
| D1.c | Testing and exercising | No cyber security exercises involving the AMS-500. No tabletop exercises for OT incident scenarios. | Not Achieved |

### D2. Lessons Learned

**Principle:** The organisation learns from incidents and improves.

| Indicator | Description | Assessment | Rating |
|-----------|-------------|------------|--------|
| D2.a | Incident review process | No formal incident review process for OT cyber security events. Previous operational incidents (a PLC fault in September 2025 caused by a corrupted data block) were treated as hardware/software issues with no consideration of cyber security implications. | Not Achieved |
| D2.b | Using lessons learned | N/A (no incident review process to generate lessons). | Not Achieved |

**Objective D Overall: Not Achieved -- No incident response or recovery capability exists for cyber security events.**

---

## 6. Consolidated Gap Analysis

### Critical Findings (Immediate Action Required)

| Ref | Finding | CAF Principle | Impact |
|-----|---------|---------------|--------|
| GAP-01 | No network segmentation or firewall between OT and enterprise networks | B4.a | Compromise of any enterprise system provides direct access to PLC and manufacturing process |
| GAP-02 | Default credentials on all devices (HMI, PLC, switches, OPC UA) | B2.a, B2.c | Any network-adjacent attacker or insider can gain full control of the manufacturing system |
| GAP-03 | No security monitoring or detection capability | C1.a, C2.a, C2.b | Attacks will not be detected; dwell time is effectively unlimited |
| GAP-04 | No incident response plan or recovery capability | D1.a, D1.b | No ability to respond to or recover from a cyber incident |
| GAP-05 | Permanently active vendor VPN with no access controls | A4.a, B2.b | Third-party has unmonitored, unrestricted access to the entire OT network |

### High Findings (Address Within 3 Months)

| Ref | Finding | CAF Principle | Impact |
|-----|---------|---------------|--------|
| GAP-06 | No patch management for OT systems | B4.d | Known critical vulnerabilities remain unpatched indefinitely |
| GAP-07 | No PLC programme backup or integrity verification | B5.c, B4.b | Cannot detect programme modification or recover from corruption |
| GAP-08 | No OT asset inventory | A3.a | Unknown devices on network; cannot assess or manage what is not inventoried |
| GAP-09 | No OT security governance or accountability | A1.a, A1.b | No one is responsible for OT security; decisions are ad-hoc |
| GAP-10 | Cleartext industrial protocols with no compensating controls | B3.a | Process data, commands, and credentials visible to any network observer |

### Medium Findings (Address Within 6 Months)

| Ref | Finding | CAF Principle | Impact |
|-----|---------|---------------|--------|
| GAP-11 | No OT security training for operators or engineers | B6.a | Staff unable to recognise or respond to security events |
| GAP-12 | No secure data handling for recipes and process data | B3.b, B3.c | Sensitive manufacturing data unprotected |
| GAP-13 | No change management for PLC programmes | B1.a | Unauthorised modifications not tracked or controlled |

---

## 7. Recommended Priority Actions

1. **Immediate (0-4 weeks):**
   - Change all default credentials across all devices.
   - Disable the vendor VPN or restrict it to scheduled, monitored maintenance windows.
   - Disable unnecessary services on the HMI workstation (IIS, RDP, Telnet).
   - Disable OPC UA anonymous access and SecurityPolicy None.
   - Take a full backup of PLC programmes and HMI configuration as a known-good baseline.

2. **Short-term (1-3 months):**
   - Implement network segmentation using the Hirschmann switches' VLAN capability and deploy an industrial firewall between OT and enterprise networks.
   - Deploy ICS network monitoring (port mirror from Hirschmann switch to a monitoring appliance).
   - Establish a basic OT asset inventory.
   - Assign OT security accountability to a named individual.
   - Develop an OT incident response plan, even if initial version is basic.

3. **Medium-term (3-6 months):**
   - Upgrade S7-1500 firmware to V3.0.1+ to address CVE-2022-38465.
   - Implement a patch management process for OT systems.
   - Deploy application whitelisting on the HMI workstation.
   - Conduct OT security awareness training for manufacturing staff.
   - Establish a regular PLC programme integrity verification process.
   - Conduct a formal risk assessment in line with IEC 62443-3-2.

---

## 8. References

- NCSC, "Cyber Assessment Framework" v3.2 (2024)
- NCSC, "Secure Design Principles for SCADA/ICS Systems" (2022)
- NCSC, "OT Security: Overview" (2023)
- NIS Regulations 2018 (UK)
- NCSC, "Supply Chain Security Guidance" (2023)
- CPNI, "Protecting Industrial Control Systems" (2021)

---

*This document is part of the AMS-500 security assessment working library. Do not distribute outside the assessment team.*
