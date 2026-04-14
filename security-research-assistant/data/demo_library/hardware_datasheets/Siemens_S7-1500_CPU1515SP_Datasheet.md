# Siemens SIMATIC S7-1500 CPU 1515SP PC2 -- Technical Datasheet

**Order Number:** 6ES7 677-2AA41-0FL0  
**Product Family:** SIMATIC S7-1500 Software Controller  
**Document Type:** Technical Datasheet  
**Revision:** 2025-06  
**Source:** Siemens Digital Industries, Automation Products

---

> **NOTE:** This document is provided for reference in the context of the AMS-500 additive manufacturing system. For the most current specifications, consult the Siemens Industry Online Support portal (support.industry.siemens.com) and the official SIMATIC S7-1500 system manual (manual ID: A5E03461182).

---

## 1. Product Description

The SIMATIC S7-1500 CPU 1515SP PC2 (6ES7 677-2AA41-0FL0) is a combined industrial PC and software PLC in the compact ET 200SP form factor. It integrates a full-featured S7-1500 Software Controller with a Windows-based industrial PC, enabling simultaneous execution of PLC runtime and PC-based applications (SCADA, data logging, OPC-UA server, custom software) on a single hardware platform.

The CPU 1515SP PC2 is designed for mid-range to high-performance automation applications where the combination of deterministic PLC control and flexible PC-based computing is required. It is suitable for machine control, process automation, and IIoT edge computing applications.

### 1.1 Key Features

- Combined S7-1500 Software Controller and Industrial PC
- Intel Celeron 3965U dual-core processor at 2.2 GHz
- 2 GB DDR4 RAM (for PC applications), 100 MB PLC work memory
- Integrated PROFINET IO controller with 2-port switch (X1 P1 / X1 P2)
- Integrated OPC UA server (IEC 62541)
- Integrated web server (HTTPS)
- Failsafe capability (F-CPU) for safety applications up to SIL 2 / PL d
- TIA Portal V17 engineering (Update 6 or later required)
- ET 200SP backplane integration for distributed I/O

---

## 2. Processor and Memory Specifications

### 2.1 Processor

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Processor type               | Intel Celeron 3965U (Kaby Lake)            |
| Core count                   | 2 (dual-core)                              |
| Clock frequency              | 2.2 GHz                                   |
| Cache                        | 2 MB Intel Smart Cache                     |
| TDP (Thermal Design Power)   | 15 W                                       |
| Architecture                 | 64-bit (x86-64)                            |
| Process technology           | 14 nm                                      |

### 2.2 Memory

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| System RAM (PC applications)     | 2 GB DDR4-2133 (soldered, not expandable) |
| PLC work memory (user programme) | 100 MB                                 |
| PLC load memory (programme storage)| 2 GB (on internal CFast card)        |
| PLC retentive data memory        | 750 KB                                 |
| Data block memory                | Included in 100 MB work memory         |
| Number of data blocks            | max. 65535                              |
| Number of function blocks (FBs)  | max. 65535                              |
| Number of functions (FCs)        | max. 65535                              |
| Number of organisation blocks (OBs)| max. 255                              |
| Bit memory (M)                   | 32 KB                                  |
| Counter/Timer                    | IEC counters and timers (SW-based, no HW limit) |
| Process image input (PII)        | max. 32 KB                             |
| Process image output (PIQ)       | max. 32 KB                             |

### 2.3 PLC Performance

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Bit operation execution time     | 10 ns                                  |
| Word operation execution time    | 12 ns                                  |
| Fixed-point arithmetic (32-bit)  | 12 ns                                  |
| Floating-point arithmetic (64-bit)| 16 ns                                 |
| Minimum cycle time (OB1)         | 1 ms                                   |
| Typical cycle time (AMS-500 application)| 8-12 ms                         |
| Cyclic interrupt (OB35) minimum  | 500 us                                 |
| Number of OB priority classes    | 26                                     |

### 2.4 Storage

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Internal storage (OS + PC apps)  | 128 GB CFast card (industrial grade)   |
| SIMATIC Memory Card slot         | Yes (CFast Type I)                     |
| USB ports                        | 2x USB 3.0 Type A (front panel)       |

---

## 3. Operating System and Runtime

### 3.1 PC Operating System

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Operating system             | Windows 10 IoT Enterprise LTSC 2021 (64-bit) |
| Windows activation           | Pre-activated (OEM license)                |
| Windows Update               | Manual only (WSUS compatible)              |
| .NET Framework               | 4.8 (pre-installed)                        |

### 3.2 PLC Runtime

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| PLC runtime                  | SIMATIC S7-1500 Software Controller V21.9  |
| Safety runtime               | F-Runtime for fail-safe operation           |
| Runtime license              | Pre-installed (included with hardware)     |
| Firmware version (current)   | V21.9 (as of 2025-06)                     |
| Firmware update method        | TIA Portal download or SIMATIC Automation Tool |
| Previous firmware versions   | V21.8, V21.7, V21.6, V3.0, V2.9          |

### 3.3 Engineering Software

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Required engineering tool    | TIA Portal V17 (Update 6 or later)        |
| STEP 7 Safety (F-CPU)       | STEP 7 Safety V17 (additional license)     |
| Compatibility                | Also accessible from TIA Portal V18, V19  |

---

## 4. Communication Interfaces

### 4.1 PROFINET IO

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| PROFINET ports                   | 2-port integrated switch (X1 P1, X1 P2)|
| Connector type                   | RJ-45, shielded                        |
| Speed                            | 10/100/1000 Mbps (auto-negotiation)    |
| PROFINET role                    | IO Controller                          |
| PROFINET IO devices (max)        | 128                                    |
| PROFINET send clock              | 250 us / 500 us / 1 ms / 2 ms / 4 ms  |
| PROFINET IRT (Isochronous Real-Time)| Supported                           |
| LLDP                             | Supported (IEEE 802.1AB)               |
| Media Redundancy Protocol (MRP)  | Supported (client and manager)         |
| PROFINET Shared Device           | Supported                              |
| S7 Communication                 | Supported (ISO-on-TCP, port 102)       |
| Open IE Communication            | TCP/IP, UDP/IP, ISO-on-TCP             |

### 4.2 OPC UA Server

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| OPC UA specification             | IEC 62541 (Part 3-5, 8, 11, 13)       |
| Transport protocol               | OPC UA TCP Binary (opc.tcp://)         |
| Port                             | TCP 4840 (default, configurable)       |
| Maximum concurrent sessions       | 20                                     |
| Maximum monitored items           | 10000                                  |
| Minimum publishing interval       | 100 ms                                 |
| Security policies                 | None, Basic256Sha256, Aes128_Sha256_RsaOaep, Aes256_Sha256_RsaPss |
| Authentication                   | Anonymous, Username/Password, X.509 certificate |
| Information model                | S7-1500 data types, user-defined namespaces |
| Companion specifications         | OPC UA for Machinery (OPC 40001-1) partial |
| Data Access (DA)                 | Supported                              |
| Alarms and Conditions (AC)       | Supported                              |
| Historical Access (HA)           | Supported (limited to 10000 values)    |
| Method calls                     | Supported                              |
| GDS (Global Discovery Server)    | Push model supported                   |

### 4.3 Web Server

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Protocol                         | HTTPS (TLS 1.2, TLS 1.3)              |
| Port                             | TCP 443 (HTTPS only, HTTP disabled)    |
| Maximum concurrent connections   | 30                                     |
| Authentication                   | Username/Password (configurable levels)|
| Features                         | Diagnostic pages, module status, alarm buffer, communication diagnostics, user-defined pages (HTML/JS) |
| Certificate                      | Self-signed (auto-generated) or CA-signed (importable) |

### 4.4 Other Communication

| Interface          | Specification                                        |
|--------------------|------------------------------------------------------|
| S7 Communication   | ISO-on-TCP, port 102, max. 64 connections            |
| Open User Comm.    | TCP (max. 64), UDP (max. 64), ISO-on-TCP (max. 64)  |
| Modbus TCP         | Via library function blocks (MB_SERVER, MB_CLIENT)    |
| MQTT               | Via library function block (LMQTT_Client) -- V21.8+  |
| REST API           | Via user-defined web pages and function blocks        |

---

## 5. Safety (Fail-Safe) Functionality

### 5.1 Fail-Safe Specifications

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Safety Integrity Level           | SIL 2 (IEC 62061)                     |
| Performance Level                | PL d (EN ISO 13849-1)                 |
| Category                         | Cat. 3 (EN ISO 13849-1)               |
| Safety programme execution       | F-OB (Failsafe Organisation Block)    |
| F-programme cycle time (min)     | 10 ms                                  |
| F-programme cycle time (typical) | 50 ms                                  |
| F-signature                      | 32-bit CRC                             |
| PROFIsafe                        | Supported (F-I/O via PROFINET)         |
| Safety I/O modules (max)         | 128 F-modules                          |
| F-Runtime licence                | Included with CPU                      |
| F-Engineering licence            | STEP 7 Safety V17 (separate purchase)  |

### 5.2 Compatible Safety I/O Modules (ET 200SP)

| Order Number            | Description                    | Channels |
|------------------------|--------------------------------|----------|
| 6ES7 526-1BH00-0AB0   | F-DI 8x24VDC HF               | 8 DI     |
| 6ES7 526-2BF00-0AB0   | F-DQ 4x24VDC/2A PM            | 4 DQ     |
| 6ES7 536-6CF00-0AB0   | F-AI 2xU/I HS                 | 2 AI     |
| 6ES7 526-1BJ00-0AB0   | F-DI 4x24VDC HF (NAMUR)      | 4 DI     |

---

## 6. I/O Integration (ET 200SP Backplane)

### 6.1 Backplane Specifications

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Backplane bus                    | ET 200SP backplane (proprietary)       |
| Maximum I/O modules (per station)| 64                                    |
| Maximum I/O data (per station)   | 2 KB input + 2 KB output              |
| BaseUnit types                   | BU15-P16+A0+2D (with AUX terminals)   |
| Maximum station width            | Approximately 2 metres                 |
| Hot swapping                     | Not supported (station must be stopped)|

### 6.2 Compatible I/O Module Categories

- Digital Input modules (DI 2x, 4x, 8x, 16x -- 24VDC, 120/230VAC)
- Digital Output modules (DQ 2x, 4x, 8x, 16x -- 24VDC, relay)
- Analogue Input modules (AI 2x, 4x, 8x -- U, I, RTD, TC)
- Analogue Output modules (AQ 2x, 4x -- U, I)
- Technology modules (counter, position, motor starter)
- Communication modules (CM PtP RS232/422/485, CM CAN)
- Fail-safe I/O modules (F-DI, F-DQ, F-AI)

---

## 7. Electrical Specifications

### 7.1 Power Supply

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Supply voltage                   | 24 VDC (19.2 - 28.8 VDC, SELV/PELV)  |
| Typical current consumption      | 1.8 A (without I/O modules)           |
| Maximum current consumption      | 2.5 A (with loaded USB ports)          |
| Power consumption (typical)      | 43 W                                   |
| Power consumption (maximum)      | 60 W                                   |
| Power connector                  | 2-pin terminal block (front, removable)|
| Inrush current                   | 12 A (< 5 ms)                         |
| Battery backup                   | Maintenance-free (supercapacitor for retentive data, battery for RTC) |
| Battery type                     | CR2032 (for real-time clock, 5-year life) |
| Redundant power supply           | Not supported (use external redundant PSU) |

### 7.2 Electrical Isolation

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| PROFINET to backplane bus    | Functional isolation                       |
| PROFINET to 24 VDC supply   | Functional isolation                       |
| USB to system                | Functional isolation                       |

---

## 8. Environmental Specifications

### 8.1 Operating Conditions

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Operating temperature            | 0 to +50 degrees C (horizontal mount)  |
| Operating temperature            | 0 to +40 degrees C (vertical mount)    |
| Storage temperature              | -40 to +70 degrees C                   |
| Relative humidity                | 10% to 95% (non-condensing)            |
| Operating altitude               | Up to 2000 m (without derating)        |
| Operating altitude               | Up to 5000 m (with temperature derating)|
| Vibration (operation)            | 5-58 Hz: 0.35 mm amplitude; 58-150 Hz: 1g (per IEC 60068-2-6) |
| Shock (operation)                | 15g, 11 ms (per IEC 60068-2-27)       |
| EMC immunity                     | EN 61000-6-2:2005 (industrial)         |
| EMC emissions                    | EN 61000-6-4:2007+A1:2011              |
| Pollution degree                 | 2                                       |
| Protection rating                | IP20                                    |

### 8.2 Mounting

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Mounting method              | DIN rail (35 mm, EN 60715)                 |
| Mounting orientation         | Horizontal (preferred) or Vertical         |
| Minimum clearance (top/bottom)| 25 mm                                     |
| Minimum clearance (left/right)| 0 mm (flush mounting with adjacent modules)|

---

## 9. Physical Dimensions

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Width                        | 75 mm (4 BaseUnit widths)                  |
| Height                       | 117 mm                                     |
| Depth                        | 135 mm                                     |
| Weight                       | 520 g (without packaging)                  |

---

## 10. Firmware Information

### 10.1 Current Firmware

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Firmware version             | V21.9                                      |
| Release date                 | 2025-03-15                                 |
| Minimum TIA Portal version   | V17 Update 6                               |
| Key changes in V21.9         | OPC UA performance improvements, TLS 1.3 support for web server, bugfixes for F-Runtime timing |

### 10.2 Firmware Update Procedure

1. Download the firmware update package from Siemens Industry Online Support.
2. Open TIA Portal V17 and connect to the CPU via the management interface (192.168.10.20:102).
3. Navigate to Online & Diagnostics > Functions > Firmware Update.
4. Select the downloaded firmware file (.upd).
5. The CPU will restart during the update process. **Ensure no active build process is running.**
6. After restart, verify the firmware version via the CPU web server or TIA Portal Online.

> **WARNING:** Firmware updates require the CPU to restart, causing a temporary loss of process control. Schedule firmware updates during planned maintenance windows only. Verify firmware compatibility with your TIA Portal project version before updating.

---

## 11. Known Vulnerabilities and Security Advisories

The following Siemens Product CERT security advisories are relevant to the S7-1500 CPU family. Operators should review these advisories, assess applicability to their installation, and apply mitigations or updates as appropriate.

### 11.1 Relevant Security Advisories

| Advisory ID    | CVE(s)                 | Title                                          | Severity | Affected FW    | Fixed FW  |
|----------------|------------------------|------------------------------------------------|----------|----------------|-----------|
| SSA-838121     | CVE-2023-46283, CVE-2023-46284, CVE-2023-46285 | Multiple Vulnerabilities in SIMATIC S7-1500 CPU Web Server | High (CVSS 7.5) | < V21.9 | V21.9 |
| SSA-711309     | CVE-2023-44374         | Improper Validation of Integrity Check Value in S7-1500 CPU | Medium (CVSS 6.5) | < V21.8 | V21.8 |
| SSA-482757     | CVE-2023-25910         | Denial of Service in OPC UA Server of S7-1500 CPU | Medium (CVSS 5.3) | < V21.7 | V21.7 |
| SSA-566905     | CVE-2022-46144         | Denial of Service via Crafted S7 Communication Packets | High (CVSS 7.5) | < V21.6 | V21.6 |
| SSA-568427     | CVE-2022-38465         | Extracting Key Material from S7-1500 CPU Firmware | Critical (CVSS 9.8) | < V3.0 | V3.0+ (new HW) |
| SSA-198999     | CVE-2022-30137         | Privilege Escalation in S7-1500 CPU Web Server | High (CVSS 8.1) | < V2.9.6 | V2.9.6 |
| SSA-731239     | CVE-2021-37185, CVE-2021-37204, CVE-2021-37205 | Multiple PROFINET Vulnerabilities in S7-1500 CPU | High (CVSS 7.5) | < V2.9.4 | V2.9.4 |

### 11.2 Security Recommendations

Siemens recommends the following general security measures for all S7-1500 installations:

1. **Keep firmware up to date.** Apply the latest firmware version (currently V21.9) which addresses all known vulnerabilities listed above.

2. **Restrict network access.** Place the CPU behind a properly configured industrial firewall. Use VLANs to segment control traffic from management traffic.

3. **Disable unused services.** If OPC-UA, Modbus TCP, or the web server are not required, disable them to reduce the attack surface.

4. **Configure access protection.** Set PLC access level passwords (Full, HMI, Read) to prevent unauthorised programme modification.

5. **Enable OPC-UA security.** Use certificate-based authentication with the Basic256Sha256 or Aes128_Sha256_RsaOaep security policy. Disable the "None" security policy.

6. **Monitor for anomalies.** Use the CPU's diagnostic buffer, web server, and syslog capabilities to monitor for unexpected connections, failed authentication attempts, or abnormal CPU behaviour.

7. **Follow IEC 62443 principles.** Implement defence-in-depth, principle of least privilege, and security-by-design in the overall automation architecture.

> **NOTE ON CVE-2022-38465 (SSA-568427):** This critical vulnerability affects S7-1500 CPUs with hardware versions prior to V3.0. It allows extraction of the global private key used for CPU-to-CPU secure communication. CPUs with firmware V3.0 and later running on new hardware (V3.0-compatible hardware) use individual key material and are not affected. **The CPU 1515SP PC2 (6ES7 677-2AA41-0FL0) with firmware V21.9 uses new hardware and is not affected by CVE-2022-38465**, provided it was manufactured after 2023-01. Check the hardware version on the CPU rating plate.

---

## 12. Certifications and Approvals

| Certification                    | Standard / Regulation                  |
|----------------------------------|----------------------------------------|
| CE Marking                       | EU Machinery Directive, EMC Directive, LVD |
| UL Listed                        | UL 61010-2-201, CSA C22.2 No. 61010-2-201 |
| cULus                            | For use in Class I, Div. 2, Groups A-D |
| FM                               | Factory Mutual approved (Class I, Div. 2) |
| IECEx                            | IECEx CSA 14.0017X                    |
| ATEX                             | II 3 G Ex nA IIC T4 Gc               |
| KC (Korea)                       | KCC-REM-S57-S71500                    |
| RCM (Australia)                  | Compliant with EN 61000-6-4           |
| Marine (Class NK, GL, LR, BV)    | On request                            |
| Functional Safety                | SIL 2 (IEC 62061), PL d (ISO 13849-1)|

---

## 13. Ordering Information

| Order Number            | Description                                           | Price (List) |
|------------------------|-------------------------------------------------------|-------------|
| 6ES7 677-2AA41-0FL0   | CPU 1515SP PC2, 2GB RAM, 100MB work memory, Win10 IoT | On request  |
| 6ES7 954-8LF04-0AA0   | SIMATIC Memory Card, 24 MB (spare)                    | On request  |
| 6ES7 648-2AH60-0KA0   | CFast Card, 128 GB (spare)                            | On request  |
| 6ES7 677-2AA41-0FK0   | CPU 1515SP PC2 (Open Controller variant, no Windows)  | On request  |

### 13.1 Required Accessories

| Order Number            | Description                                    |
|------------------------|------------------------------------------------|
| 6ES7 193-6PA00-0AA0   | BaseUnit BU15-P16+A0+2D (required for mounting)|
| 6ES7 193-6BP00-0DA0   | BaseUnit BU20-P12+A0+2B (for I/O modules)     |
| 6ES7 197-1LA12-0XA0   | Server Module (bus termination, rightmost slot)|

---

## 14. Dimensional Drawing

```
         75 mm
     +----------+
     |   CPU    |
     |  1515SP  |   117 mm
     |   PC2    |
     |          |
     |  [X1 P1] |
     |  [X1 P2] |
     |  [USB x2]|
     +----------+
         |
     135 mm depth
     (including connectors)
```

Front panel indicators:
- RUN/STOP LED (green/amber)
- ERROR LED (red)
- MAINT LED (amber)
- PROFINET LINK/ACT LEDs (green, 2x)
- USB Activity LED (green)

---

**End of Document**

*Based on Siemens SIMATIC S7-1500 product documentation. Siemens and SIMATIC are registered trademarks of Siemens AG. All specifications subject to change without notice. Refer to official Siemens documentation for binding specifications.*
