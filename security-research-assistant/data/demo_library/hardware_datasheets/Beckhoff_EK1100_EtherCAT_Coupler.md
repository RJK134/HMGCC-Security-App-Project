# Beckhoff EK1100 EtherCAT Coupler -- Technical Datasheet

**Order Number:** EK1100  
**Product Family:** EtherCAT Bus Coupler  
**Document Type:** Technical Datasheet  
**Revision:** 2025-04  
**Source:** Beckhoff Automation GmbH & Co. KG, Verl, Germany

---

## 1. Product Description

The Beckhoff EK1100 is an EtherCAT bus coupler that provides the interface between an EtherCAT network (100BASE-TX Ethernet) and the Beckhoff EtherCAT Terminal (E-bus) system. The EK1100 converts the EtherCAT protocol frames received via standard Ethernet into the E-bus signal format used by EtherCAT terminals (ELxxxx series), and vice versa.

The coupler is the first device in an EtherCAT terminal station. It receives EtherCAT frames from the upstream EtherCAT master or previous EtherCAT device on its upper RJ-45 port (IN) and forwards them to downstream devices on its lower RJ-45 port (OUT), while simultaneously distributing data to the attached E-bus terminals. This daisy-chain topology eliminates the need for additional network switches in the EtherCAT segment.

In the AMS-500 additive manufacturing system, the EK1100 serves as the bridge between the PLC's PROFINET/EtherCAT gateway (Beckhoff EL6692) and the EtherCAT servo drives (AX5206, AX5203, AX5103) and I/O terminals that control the motion axes and field-level I/O.

### 1.1 Key Features

- EtherCAT bus coupler for EtherCAT Terminal system (E-bus)
- Two RJ-45 ports for EtherCAT daisy-chain topology (IN / OUT)
- Automatic detection of connected EtherCAT terminals
- EtherCAT Distributed Clock (DC) support
- Hot Connect group support for modular machine designs
- Comprehensive LED diagnostics (Run, Error, Link/Activity)
- DIN rail mounting (35 mm, EN 60715)
- Compact form factor (bus terminal housing)
- Firmware update via EtherCAT (FoE -- File over EtherCAT)

---

## 2. EtherCAT Specifications

### 2.1 Network Interface

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| EtherCAT standard               | IEC 61158, IEC 61784                   |
| Physical layer                   | 100BASE-TX (IEEE 802.3u)              |
| Connector type                   | 2x RJ-45 (upper = IN, lower = OUT)    |
| Cable type                       | Cat 5e minimum (Cat 6a recommended)   |
| Maximum cable length (per segment)| 100 m (Ethernet standard)             |
| Data rate                        | 100 Mbps (full duplex)                 |
| EtherCAT frame processing       | Hardware-based (ASIC), processing on the fly |
| Frame processing delay           | < 1 us (per coupler)                   |
| Maximum EtherCAT frame size      | 1518 bytes (standard Ethernet frame)   |
| EtherCAT addressing              | Auto-Increment, Station Alias, Logical addressing |

### 2.2 EtherCAT Protocol Features

| Feature                          | Support                                |
|----------------------------------|----------------------------------------|
| Distributed Clock (DC)          | Yes (can be DC reference clock)        |
| DC jitter                        | < 1 us                                 |
| Mailbox protocols                | CoE (CANopen over EtherCAT), EoE (Ethernet over EtherCAT), FoE (File over EtherCAT) |
| CoE (CANopen over EtherCAT)     | SDO access to terminal parameters      |
| EoE (Ethernet over EtherCAT)    | Tunnelling of standard Ethernet frames |
| FoE (File over EtherCAT)        | Firmware update capability             |
| Hot Connect                      | Supported (as group head)              |
| Slave Information Interface (SII)| EEPROM-based, auto-read at startup    |
| EtherCAT State Machine          | Init, Pre-Operational, Safe-Operational, Operational |

### 2.3 E-bus Interface (Backplane)

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| E-bus type                       | EtherCAT Terminal bus (E-bus)          |
| Maximum terminals per station    | 65,535 (theoretical); practical limit ~255 |
| Maximum E-bus current (supplied) | 2000 mA (from internal power supply)   |
| E-bus power source               | From coupler's 24 VDC supply           |
| E-bus voltage                    | 5 VDC (internal, regulated)            |
| E-bus data rate                  | 100 Mbps                               |
| E-bus termination                | Automatic (via last terminal or end cap)|

### 2.4 Supported Terminal Types

The EK1100 supports all Beckhoff EtherCAT terminals (ELxxxx series), including but not limited to:

**Digital I/O:**

| Terminal       | Description                              | Channels |
|----------------|------------------------------------------|----------|
| EL1008         | 8-channel digital input, 24 VDC, 3 ms    | 8 DI     |
| EL1018         | 8-channel digital input, 24 VDC, 10 us   | 8 DI     |
| EL1809         | 16-channel digital input, 24 VDC, 3 ms   | 16 DI    |
| EL2008         | 8-channel digital output, 24 VDC, 0.5 A  | 8 DQ     |
| EL2798         | 8-channel digital output, 24 VDC, relay   | 8 DQ     |
| EL2809         | 16-channel digital output, 24 VDC, 0.5 A | 16 DQ    |

**Analogue I/O:**

| Terminal       | Description                              | Channels |
|----------------|------------------------------------------|----------|
| EL3064         | 4-channel analogue input, 0-10 V, 12-bit | 4 AI     |
| EL3154         | 4-channel analogue input, 4-20 mA, 16-bit| 4 AI     |
| EL3314         | 4-channel thermocouple input (K, J, etc.) | 4 AI     |
| EL4004         | 4-channel analogue output, 0-10 V, 12-bit| 4 AQ     |
| EL4034         | 4-channel analogue output, +/-10 V, 16-bit| 4 AQ    |
| EL4134         | 4-channel analogue output, -10..+10 V, 16-bit| 4 AQ  |

**Special / Communication:**

| Terminal       | Description                              |
|----------------|------------------------------------------|
| EL6692         | EtherCAT bridge (PROFINET to EtherCAT)   |
| EL6695         | EtherCAT bridge (PTP time sync)          |
| EL6021         | Serial interface, RS-422/RS-485          |
| EL6751         | CANopen master terminal                  |
| EL6631         | PROFINET IO device terminal              |

**Servo Drives (AX5000 series):** The AX5000 series servo drives are standalone EtherCAT devices connected in the daisy chain via RJ-45 ports, not via the E-bus backplane. They appear after the EK1100 OUT port in the EtherCAT topology.

---

## 3. Distributed Clock (DC) Configuration

### 3.1 DC Overview

The EK1100 supports EtherCAT Distributed Clocks, which provide high-precision time synchronisation across all EtherCAT devices in the network. DC ensures that output events (servo commands, digital outputs) occur simultaneously across all devices, regardless of their position in the daisy chain.

### 3.2 DC Configuration Parameters

| Parameter                        | Specification / Setting                |
|----------------------------------|----------------------------------------|
| DC support                       | Yes                                    |
| DC reference clock capability    | Yes (can act as reference clock)       |
| DC clock resolution              | 1 ns (internal)                        |
| DC clock accuracy (free-running) | +/- 10 ppm (approximately +/- 0.86 s/day) |
| DC synchronisation accuracy      | < 100 ns (after drift compensation)    |
| DC Sync0 / Sync1 signals        | Supported                              |
| SYNC output (physical)           | Not available (internal signal only)    |

### 3.3 Recommended DC Configuration (for AMS-500)

In the AMS-500 system, the EK1100 is configured as the DC reference clock (first device in the EtherCAT chain with DC capability). All downstream devices synchronise to the EK1100's clock.

**TwinCAT / TIA Portal Configuration:**

- DC operating mode: DC-Synchron (with SYNC0)
- Cycle time: 1000 us (1 ms)
- SYNC0 cycle time: 1000 us
- Shift time: 0 us
- DC reference clock: EK1100 (automatic selection)

---

## 4. Diagnostic LEDs

### 4.1 LED Layout (Front Panel)

```
+-------------------+
|  [  RUN  ] green  |  EtherCAT Run LED
|  [  ERR  ] red    |  EtherCAT Error LED
|                   |
|  [LINK/ACT] green |  Upper port (IN) link and activity
|  ====[RJ-45]====  |  Upper port (IN)
|                   |
|  [LINK/ACT] green |  Lower port (OUT) link and activity
|  ====[RJ-45]====  |  Lower port (OUT)
|                   |
|  [POWER ] green   |  24 VDC supply OK
+-------------------+
```

### 4.2 LED Interpretation

**RUN LED (Green):**

| State                | Meaning                                     |
|----------------------|---------------------------------------------|
| Off                  | Init state (no EtherCAT communication)      |
| Blinking (1 Hz)      | Pre-Operational state                       |
| Single flash (200ms) | Safe-Operational state                      |
| On (steady)          | Operational state (normal operation)        |

**ERR LED (Red):**

| State                | Meaning                                     |
|----------------------|---------------------------------------------|
| Off                  | No error                                    |
| Blinking (1 Hz)      | Configuration error (invalid or mismatched) |
| Single flash (200ms) | Local error detected                        |
| On (steady)          | Application watchdog timeout / fatal error  |
| Flickering (fast)    | EEPROM checksum error or hardware fault     |

**LINK/ACT LED (Green, per port):**

| State                | Meaning                                     |
|----------------------|---------------------------------------------|
| Off                  | No Ethernet link detected                   |
| On (steady)          | Link established, no activity               |
| Blinking/Flickering  | Link established, data traffic active       |

**POWER LED (Green):**

| State                | Meaning                                     |
|----------------------|---------------------------------------------|
| Off                  | No 24 VDC supply                            |
| On (steady)          | 24 VDC supply present and within tolerance  |

### 4.3 Diagnostic Troubleshooting

| Symptom                          | Probable Cause                          | Action                                  |
|----------------------------------|-----------------------------------------|-----------------------------------------|
| RUN off, ERR off                 | No power or no EtherCAT traffic         | Check 24 VDC supply, check Ethernet cable to IN port |
| RUN blinking, ERR off            | Stuck in Pre-Op state                   | Check master configuration matches actual terminal configuration |
| RUN off, ERR blinking            | Configuration mismatch                  | Scan EtherCAT topology in TwinCAT/TIA Portal, compare with project |
| RUN off, ERR steady on           | Watchdog timeout                        | Check EtherCAT master is running, check cable integrity |
| LINK/ACT off (IN port)           | No Ethernet link on upstream connection | Check cable, check upstream device port status |
| LINK/ACT off (OUT port)          | No downstream device or cable fault     | Check cable to next device; OK if this is the last device in chain |

---

## 5. Configuration via TwinCAT

### 5.1 Device Identification

| Parameter                | Value                                      |
|--------------------------|----------------------------------------------|
| EtherCAT Vendor ID       | 0x00000002 (Beckhoff)                       |
| EtherCAT Product Code    | 0x044C2C52                                  |
| EtherCAT Revision        | 0x00120000                                  |
| EtherCAT Serial Number   | (unique per device, read from EEPROM)        |
| ESI file                 | Beckhoff EK1100.xml (included in TwinCAT)    |

### 5.2 TwinCAT Configuration Steps

1. Open TwinCAT XAE (Engineering) or TwinCAT 3.
2. Right-click on "I/O > Devices" and select "Scan Devices" or "Add New Item > EtherCAT Master".
3. The EK1100 and all attached terminals will be auto-detected during a bus scan.
4. Verify that the scanned topology matches the expected configuration.
5. Assign the EK1100 as the DC reference clock (right-click > Advanced Settings > Distributed Clock > Reference Clock: Yes).
6. Configure individual terminal parameters via CoE (CANopen over EtherCAT) SDO access if needed.
7. Activate the configuration and transition to Operational state.

### 5.3 Configuration via TIA Portal (with Beckhoff ESI files)

When the EK1100 is used with a Siemens S7-1500 PLC via the EL6692 PROFINET-to-EtherCAT bridge:

1. Import the Beckhoff ESI (EtherCAT Slave Information) files into TIA Portal:
   - File location: Beckhoff website or TwinCAT installation directory
   - Import path: TIA Portal > Options > Manage General Station Description Files (GSD) > Install
2. Add the EL6692 as a PROFINET IO device in the S7-1500 project.
3. Configure the EtherCAT sub-network under the EL6692 device.
4. Add the EK1100 as the first device in the EtherCAT chain.
5. Add subsequent terminals and drives in the correct topology order.
6. Map EtherCAT process data to PLC tags.

---

## 6. Firmware

### 6.1 Firmware Information

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Firmware type                | EtherCAT Slave Controller (ESC) firmware   |
| Current firmware version     | V01.13                                     |
| Firmware update method       | FoE (File over EtherCAT) via TwinCAT       |
| Firmware file format         | .efw (Beckhoff EtherCAT firmware)          |
| Firmware rollback            | Supported (load previous version via FoE)  |

### 6.2 Firmware Update Procedure

1. Download the firmware update file from the Beckhoff website (requires login).
2. Open TwinCAT and connect to the EtherCAT master.
3. Right-click on the EK1100 device in the I/O tree.
4. Select "Online > Firmware Update via FoE".
5. Browse to the .efw file and initiate the update.
6. The EK1100 will restart automatically after the update.
7. Verify the new firmware version in the device's Online tab.

> **WARNING:** Do not power off the EK1100 during a firmware update. Interrupted firmware writes can result in a non-functional device that requires factory service.

### 6.3 Firmware Version History

| Version | Date       | Key Changes                                      |
|---------|------------|--------------------------------------------------|
| V01.13  | 2024-11-01 | Improved DC synchronisation stability             |
| V01.12  | 2024-05-15 | Fixed rare E-bus initialisation failure           |
| V01.11  | 2023-09-20 | EoE performance improvements                     |
| V01.10  | 2023-03-01 | Added Hot Connect group capability                |
| V01.09  | 2022-08-10 | Fixed EEPROM write timeout issue                 |

### 6.4 Security Considerations

| Concern                          | Detail                                 |
|----------------------------------|----------------------------------------|
| SEC-EK-001: No Authentication    | EtherCAT operates at Layer 2 with no authentication. Any device on the physical network can read and write all process data. The protocol has no concept of identity or access control. |
| SEC-EK-002: Unsigned Firmware    | FoE firmware updates carry no digital signature. Any EtherCAT master with network access can push arbitrary firmware to the EK1100. There is no signature verification mechanism. |
| SEC-EK-003: No Encryption        | All EtherCAT frames are transmitted in plaintext. Process data, configuration parameters, and firmware content are all visible to any device capable of monitoring the physical Ethernet segment. |
| SEC-EK-004: EEPROM Writable      | The Slave Information Interface (SII) EEPROM can be written to via EtherCAT SDO access. An attacker could modify device identity information, potentially causing misidentification during bus scans. |

**Recommended Mitigations:**

- Physical network isolation (dedicated cabling, no shared switch ports with untrusted devices)
- Port security on upstream managed switches (MAC address limiting)
- Regular firmware version audits (compare against known-good versions)
- Physical access controls to the control cabinet
- Network monitoring for unexpected EtherCAT traffic patterns
- Periodic EEPROM integrity verification (compare SII checksums)

---

## 7. Electrical Specifications

### 7.1 Power Supply

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Supply voltage (Us)              | 24 VDC (-15% / +20%), i.e., 20.4 - 28.8 VDC |
| Typical current consumption      | 190 mA (without E-bus load)            |
| Maximum current consumption      | 2200 mA (with maximum E-bus load)      |
| E-bus current output (max)       | 2000 mA at 5 VDC                       |
| Power dissipation (typical)      | 4.5 W (without E-bus load)             |
| Power connector                  | Spring-loaded terminal (top-mounted)   |
| Wire size                        | 0.08 - 2.5 mm^2 (AWG 28 - 14)         |
| Fuse recommendation              | 6.3 A slow-blow (external)             |

### 7.2 Electrical Isolation

| Isolation                        | Rating                                 |
|----------------------------------|----------------------------------------|
| EtherCAT (RJ-45) to E-bus       | Functional isolation                   |
| EtherCAT (RJ-45) to power supply| 1500 V (reinforced insulation)         |
| E-bus to power supply            | Functional isolation                   |

### 7.3 Power Wiring

```
+-------+------+---------------------------+
| Pin   | Label| Function                  |
+-------+------+---------------------------+
| 1 (L) | +24V | Power supply positive (+) |
| 2     | 0V   | Power supply negative (-) |
| 3 (L) | PE   | Protective Earth          |
+-------+------+---------------------------+

NOTE: The +24V and 0V connections are bridge-connected
internally to the E-bus power supply rail. All terminals
in the station receive their E-bus power from this supply.
Verify total E-bus current consumption does not exceed 2000 mA.
If it does, add an EL9410 E-bus power supply terminal
at the appropriate point in the terminal strip.
```

---

## 8. Mechanical Specifications

### 8.1 Dimensions

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Width                        | 57 mm                                      |
| Height                       | 100 mm                                     |
| Depth                        | 73 mm (including DIN rail clip)            |
| Weight                       | 135 g                                      |

### 8.2 Mounting

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Mounting method              | DIN rail, 35 mm (EN 60715), snap-on        |
| Mounting orientation         | Horizontal rail, terminals pointing upward |
| Minimum clearance (top)      | 30 mm (for wiring access)                  |
| Minimum clearance (bottom)   | 30 mm (for wiring access)                  |
| Minimum clearance (left)     | 0 mm (flush with adjacent terminals)       |

### 8.3 Wiring

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Terminal type                | Spring-loaded (cage-clamp)                 |
| Wire size (solid)            | 0.08 - 2.5 mm^2 (AWG 28 - 14)            |
| Wire size (stranded)         | 0.08 - 2.5 mm^2 (AWG 28 - 14)            |
| Wire size (with ferrule)     | 0.14 - 1.5 mm^2                           |
| Stripping length             | 8 - 9 mm                                  |

---

## 9. Environmental Specifications

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Operating temperature            | 0 to +55 degrees C                     |
| Storage temperature              | -25 to +85 degrees C                   |
| Relative humidity                | 5% to 95% (non-condensing)             |
| Vibration resistance             | IEC 60068-2-6: 5g, 10-500 Hz           |
| Shock resistance                 | IEC 60068-2-27: 15g, 11 ms             |
| EMC immunity                     | EN 61000-6-2:2005                       |
| EMC emissions                    | EN 61000-6-4:2007+A1:2011              |
| Protection rating                | IP20                                    |
| Pollution degree                 | 2                                       |
| Operating altitude               | Up to 2000 m                            |

---

## 10. Certifications and Approvals

| Certification                    | Standard / Regulation                  |
|----------------------------------|----------------------------------------|
| CE Marking                       | EU EMC Directive 2014/30/EU, LVD 2014/35/EU |
| UL Listed                        | UL 61010-2-201                         |
| cULus                            | Class I, Division 2, Groups A-D        |
| EtherCAT Conformance             | ETG Conformance Test Tool certified    |
| RoHS                             | Directive 2011/65/EU                   |
| REACH                            | Compliant                              |

---

## 11. Ordering Information

| Order Number | Description                                    | Package |
|-------------|------------------------------------------------|---------|
| EK1100      | EtherCAT Bus Coupler (2x RJ-45, E-bus)        | 1 unit  |
| EK1101      | EtherCAT Bus Coupler (2x RJ-45, E-bus, with ID switch) | 1 unit |
| EK1110      | EtherCAT Extension (extends E-bus via 2nd RJ-45)| 1 unit |
| EK1122      | EtherCAT Junction (2 EtherCAT branches)        | 1 unit  |
| EL9410      | E-bus Power Supply terminal (2A additional)     | 1 unit  |
| EL9011      | End cap for E-bus terminal strip                | 1 unit  |
| ZB8801      | Bus end cap (10-pack)                           | 10 units|

---

## 12. Application Notes for the AMS-500

### 12.1 EtherCAT Topology in the AMS-500

```
[PROFINET / EtherCAT Gateway]
   EL6692
      |
      | (EtherCAT via RJ-45)
      |
   EK1100  <-- Bus Coupler (DC reference clock)
      |
      +-- [E-bus terminals]
      |      EL1008 (8x DI - limit switches, sensors)
      |      EL2008 (8x DQ - pneumatic valves, indicators)
      |      EL3064 (4x AI - analogue sensors)
      |
      | (EtherCAT via RJ-45 OUT port)
      |
   AX5206  <-- Servo Drive (Z-axis + X-axis)
      |
   AX5203  <-- Servo Drive (Y-axis)
      |
   AX5103  <-- Servo Drive (R-axis, sieve)
```

### 12.2 E-bus Current Budget

| Device    | E-bus Current (mA) | Running Total (mA) |
|-----------|--------------------|--------------------|
| EK1100    | +2000 (supply)     | 2000               |
| EL1008    | -100               | 1900               |
| EL2008    | -120               | 1780               |
| EL3064    | -180               | 1600               |

With 1600 mA remaining, there is ample headroom for additional E-bus terminals without requiring an EL9410 power supply terminal.

### 12.3 Commissioning Checklist

- [ ] Verify 24 VDC supply is connected and within specification (20.4 - 28.8 VDC)
- [ ] Verify POWER LED is green (steady)
- [ ] Connect EtherCAT cable from EL6692 or master to EK1100 IN port
- [ ] Verify LINK/ACT LED on IN port is green (steady or blinking)
- [ ] Connect downstream EtherCAT devices to EK1100 OUT port
- [ ] Verify LINK/ACT LED on OUT port is green (if downstream devices present)
- [ ] Perform EtherCAT bus scan in TwinCAT or TIA Portal
- [ ] Verify all expected devices are detected
- [ ] Configure Distributed Clock (EK1100 as reference)
- [ ] Transition to Operational state and verify RUN LED is steady green
- [ ] Verify ERR LED is off
- [ ] Run motion test on each axis to confirm communication integrity

---

**End of Document**

*Based on Beckhoff Automation product documentation. Beckhoff, TwinCAT, and EtherCAT are registered trademarks of Beckhoff Automation GmbH & Co. KG. EtherCAT is a patented technology, licensed by Beckhoff Automation GmbH. All specifications subject to change without notice.*
