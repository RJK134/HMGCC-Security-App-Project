# Beckhoff EK1100 EtherCAT Coupler — Technical Datasheet

## Product Overview

| Parameter | Value |
|-----------|-------|
| Order Number | EK1100 |
| Manufacturer | Beckhoff Automation GmbH & Co. KG |
| Product Category | EtherCAT Bus Coupler |
| Function | Connects EtherCAT (100BASE-TX) to E-bus terminal segment |
| Firmware Version | v2.14 (AMS-500 installed version) |

## Description

The EK1100 is the head station for connecting Beckhoff EtherCAT Terminals (E-bus) to an EtherCAT network. It converts the 100BASE-TX Ethernet physical layer to the E-bus internal backplane, allowing up to 255 terminals per coupler segment. The coupler contains no user-programmable logic and acts as a transparent bridge between the EtherCAT master (S7-1500 PLC in this installation) and the downstream I/O terminals.

## Technical Specifications

### Communication

| Parameter | Specification |
|-----------|--------------|
| Fieldbus Protocol | EtherCAT (IEC 61158, IEC 61784) |
| Physical Layer (Upstream) | 100BASE-TX, 2x RJ45 (IN/OUT) |
| Physical Layer (Downstream) | E-bus (LVDS, proprietary backplane) |
| Data Rate | 100 Mbit/s full-duplex |
| Topology | Line, star (via junction), or ring (with redundancy) |
| Frame Processing | Processing on the fly — frames pass through in <1 us |
| Max Terminals per Coupler | 255 (limited by E-bus addressing) |
| Max E-bus Current | 2000 mA |

### Electrical

| Parameter | Specification |
|-----------|--------------|
| Power Supply Voltage (Us) | 24 V DC (-15%/+20%) |
| Power Dissipation | Typ. 2.1 W |
| Current Consumption (Us) | Typ. 90 mA |
| E-bus Output Current | Max. 2000 mA |
| Electrical Isolation | 500 V (system/field) |

### Physical

| Parameter | Specification |
|-----------|--------------|
| Dimensions (W x H x D) | 12 x 100 x 68 mm |
| Mounting | 35 mm DIN rail (EN 60715) |
| Weight | Approx. 55 g |
| Protection Rating | IP20 |
| Operating Temperature | 0 to +55 C |

### Diagnostic LEDs

| LED | Colour | Meaning |
|-----|--------|---------|
| Run | Green solid | EtherCAT communication active |
| Run | Green flashing | Pre-operational state |
| Err | Red solid | Local error (E-bus fault) |
| Err | Red flashing | Configuration error |
| Link/Act IN | Green | Link/activity on upstream port |
| Link/Act OUT | Green | Link/activity on downstream port |

## EtherCAT Configuration

### Device Identification

- Vendor ID: 0x00000002 (Beckhoff)
- Product Code: 0x044C2C52
- Revision: 0x00120000
- ESI File: Beckhoff EK1100.xml

### Distributed Clocks

Supports EtherCAT DC for sub-microsecond synchronisation. Oscillator accuracy: +/- 100 ppm. Time resolution: 1 ns.

### Firmware Update

Via FoE (File over EtherCAT) protocol. **Security Note:** FoE transfers are unauthenticated. Any EtherCAT master can push firmware. No signature verification.

## AMS-500 Installation

### Connected Terminals

| Position | Terminal | Function |
|----------|---------|----------|
| 1 | EL1809 | 16-channel digital input (sensors, interlocks) |
| 2 | EL2809 | 16-channel digital output (valves, relays) |
| 3 | EL3064 | 4-channel analogue input 0-10V (pressure) |
| 4 | EL3314 | 4-channel thermocouple (Type K, chamber temps) |
| 5 | EL4034 | 4-channel analogue output 0-10V (laser power) |
| 6 | EL6695 | EtherCAT bridge (PTP time sync) |
| 7 | EL9011 | End terminal (bus termination) |

## Security Considerations

### SEC-EK-001: No Authentication on EtherCAT
EtherCAT operates at Layer 2 with no authentication. Any device on the physical network can read/write all process data.

### SEC-EK-002: Firmware Updates Unsigned
FoE firmware updates have no digital signature verification.

### SEC-EK-003: No Encryption
All EtherCAT frames transmitted in plaintext.

### Mitigations
- Physical network isolation (dedicated cabling)
- Port security on upstream managed switches
- Regular firmware audits
- Physical access controls to cabinet

## Compliance
CE, UL, EtherCAT Conformance Tested, RoHS, REACH.

---
*Source: Beckhoff Automation. EK1100 Technical Documentation.*
