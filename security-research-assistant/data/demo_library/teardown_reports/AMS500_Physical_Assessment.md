# AMS-500 Additive Manufacturing System -- Physical Tear-Down Assessment

**Project:** AMS-500 Security Assessment  
**Document ID:** TD-AMS500-001  
**Classification:** OFFICIAL  
**Assessor:** [REDACTED]  
**Date:** 2026-03-18  
**Location:** Lab 3, Building 7  
**Serial Number:** AMS-5-2024-00147  

---

## 1. Executive Summary

Physical tear-down assessment of a production AMS-500 additive manufacturing system, serial AMS-5-2024-00147, manufactured Q3 2024. The unit was received powered down and disconnected from all external services. This report documents the physical inspection, component identification, and initial observations relevant to a security evaluation of the system's hardware architecture.

The AMS-500 is a powder-bed fusion additive manufacturing system designed for metallic parts production. It uses a single-mode fibre laser for selective melting and is marketed for aerospace and defence component manufacturing. The system was acquired through normal procurement channels and is representative of units deployed in operational environments.

---

## 2. External Inspection

### 2.1 Chassis and Enclosure

The outer enclosure is formed from folded 2mm 304 stainless steel sheet panels, powder-coated RAL 7035 light grey. Overall dimensions approximately 2200mm (W) x 1400mm (D) x 2100mm (H), estimated weight 1800 kg including powder handling subsystem. The unit sits on four M16 levelling feet with anti-vibration rubber pads.

**Front face:** Large viewing window (250mm x 150mm, borosilicate with OD4+ laser-rated filter, wavelength marking 900-1100nm) set into the build chamber door. Door secured with two quarter-turn latches and a magnetic reed switch interlock (Schmersal BNS 260, wired to the safety PLC). Operator touch-panel display (15.6" capacitive, Beckhoff CP3915-0010) mounted at ergonomic height on an articulated arm. Below the display: emergency stop mushroom button (red/yellow, Siemens 3SU1150-0AB20-1CA0), key switch (two-position, maintained, labelled "LASER ENABLE"), and three indicator lights (POWER green, FAULT amber, LASER EMISSION red).

**Right side:** Service access panel secured with six M5 Torx T25 security screws (tamper-evident type with centre pin). Behind this panel: the main control cabinet. A second smaller panel below provides access to the powder recovery hopper.

**Rear face:** Main power entry (400V 3-phase, 63A, CEE plug IEC 60309). Compressed air inlet (6mm push-fit, 6 bar requirement label). Inert gas inlet (Swagelok 6mm, labelled "N2/Ar"). Two cable glands (M25, IP68) for external signal connections. Ventilation grille with filtered intake. Factory reset button recessed behind a breakable plastic cap, labelled "FACTORY RESET -- CAUTION: Restores all parameters to factory defaults. Press and hold 10s during boot."

**Left side:** Build chamber access panel (double-sealed, bolted with twelve M8 hex bolts). Powder loading port with hinged cover.

**Top:** Laser delivery optics housing (sealed unit, no user-serviceable parts labelling). Exhaust port for the recirculating gas filtration system.

### 2.2 Labels and Markings

**Compliance labels identified:**
- CE marking (Notified Body 0681)
- UKCA marking
- Laser Class 4 warning label per IEC 60825-1:2014 (yellow/black triangle)
- Electrical safety per IEC 61010-1
- EMC per IEC 61326-1

**Identification plate (riveted, rear panel):**
- Manufacturer: [Vendor redacted -- referred to as "AMS Vendor"]
- Model: AMS-500
- Serial: AMS-5-2024-00147
- Year of manufacture: 2024
- Supply: 400V 3ph 50Hz 45A
- Weight: 1780 kg
- IP rating: IP54

**Additional labels noted:**
- QC sticker with date stamp "2024-08-14" and inspector initials "MK"
- Firmware version label on inner control cabinet door: "v3.8.2-prod build 20240801"
- Calibration sticker (laser power): "Cal date 2024-08-12, next due 2025-08-12"

---

## 3. Control Cabinet Inspection

### 3.1 Cabinet Access

Removed the right-side service panel (six Torx T25 security screws). These are tamper-evident screws with a centre pin. Noted that the screws showed no visible evidence of prior removal. Behind the panel is a standard 600mm x 400mm x 200mm sheet-metal enclosure with its own hinged door, secured by a triangular lock (standard 7mm electrical cabinet key). Lock was keyed alike -- matches common Rittal cabinet keys. No tamper seals on the cabinet door itself.

[Photo reference: IMG_0341.jpg -- cabinet door open, overview shot]

### 3.2 Component Inventory

Opening the cabinet door reveals three 35mm DIN rails mounted horizontally:

**Top DIN rail (power distribution):**
- Main circuit breaker: Siemens 5SY4332-7 (32A, 3-pole)
- Auxiliary breaker 1: Siemens 5SY4206-7 (6A, 2-pole, labelled "CTRL 24V")
- Auxiliary breaker 2: Siemens 5SY4210-7 (10A, 2-pole, labelled "SERVO PWR")
- Power supply 1: Siemens SITOP PSU8200 6EP3334-8SB00-0AY0 (24VDC, 10A)
- Power supply 2: Mean Well SDR-480-24 (24VDC, 20A, labelled "DRIVE SUPPLY")
- UPS module: Phoenix Contact QUINT4-UPS/24DC/24DC/20 (for PLC backup, 20A)

**Middle DIN rail (PLC and I/O):**
- PLC CPU: Siemens S7-1516-3 PN/DP (6ES7516-3AN02-0AB0)
  - Firmware label on side: "V3.0.3"
  - Memory card slot visible (SIMATIC Memory Card, no card inserted at time of inspection -- slot empty)
  - PROFINET ports x2 (X1 P1, X1 P2), both with green link LEDs
  - PROFIBUS DP port (X2), 9-pin D-sub, no cable connected
  - USB port (Micro-B) on front panel under a rubber flap
  - Mode selector switch in RUN position
  - Status LEDs: RUN solid green, ERROR off, MAINT off
- Signal module 1: Siemens SM 1231 AI 8x13bit (6ES7231-4HF32-0XB0) -- analogue inputs (thermocouples)
- Signal module 2: Siemens SM 1231 AI 4x16bit (6ES7231-5QD32-0XB0) -- analogue inputs (pressure transducers)
- Signal module 3: Siemens SM 1221 DI 16x24VDC (6ES7221-1BH32-0XB0) -- digital inputs
- Signal module 4: Siemens SM 1222 DQ 16xRelay (6ES7222-1HH32-0XB0) -- digital outputs
- Communication module: Siemens CM 1241 RS422/485 (6ES7241-1CH32-0XB0) -- serial comms to legacy sensors
- Safety module: Siemens F-DI 8x24VDC (6ES7226-6BA32-0XB0) -- safety inputs
- Safety module: Siemens F-DQ 4x24VDC/2A (6ES7226-6DA32-0XB0) -- safety outputs

**Bottom DIN rail (relays and terminal blocks):**
- Relay block: 8x Finder 40.52 miniature relays (8A contacts) on 95.05 sockets
- Terminal strips: Weidmuller WDU 2.5 series, approximately 60 terminals
- Surge protection: Phoenix Contact VAL-MS 230/3+1 on incoming mains
- Ground bus bar: copper, 12 connections

[Photo reference: IMG_0348.jpg -- middle DIN rail close-up showing PLC and I/O modules]
[Photo reference: IMG_0352.jpg -- terminal strip labelling detail]

### 3.3 Network Infrastructure

A Hirschmann RS20-0800T2T1SDAEHH06.0 managed switch is mounted on the inside wall of the control cabinet (not on DIN rail -- bracket-mounted). Eight 100Mbit copper ports. Observed cable connections:

- Port 1: PLC PROFINET X1 P1 (green cable, labelled "PLC-PN1")
- Port 2: Operator HMI panel (green cable, labelled "HMI")
- Port 3: Communication gateway module (green cable, labelled "GW-ETH1")
- Port 4: Laser control unit (green cable, labelled "LASER-CTRL")
- Port 5: Beckhoff EtherCAT coupler (green cable, labelled "ECAT-GW")
- Port 6: Empty
- Port 7: External connection (routed through rear cable gland, labelled "SERVICE")
- Port 8: Empty

Switch has a console port (RS-232, RJ-45 pinout). Default IP label on underside: 192.168.1.1. A small sticker reads "VLAN config: see doc AMS-NET-002."

### 3.4 Communication Gateway Module

Separate PCB assembly mounted in a DIN-rail enclosure (Phoenix Contact ME-series housing). Dual RJ-45 Ethernet connectors on front. One 9-pin D-sub serial port (labelled RS-232/485 with a DIP switch bank for selection). Power LED, STATUS LED (blinking green), and FAULT LED (off). This module handles PROFINET-to-Modbus TCP/IP protocol translation. See separate report TD-AMS500-003 for detailed inspection.

---

## 4. Main Controller Board Identification

### 4.1 Board Location and Removal

The main controller board is housed in a separate sealed enclosure mounted above the control cabinet, behind the operator display arm. This enclosure is secured with four Phillips-head screws and a tamper-evident label across the seam (holographic sticker, serial 00294817, appeared intact). Removing the screws and breaking the tamper seal revealed a custom PCB, approximately 160mm x 100mm, 6-layer (estimated from edge view).

[Photo reference: IMG_0361.jpg -- tamper seal before removal]
[Photo reference: IMG_0365.jpg -- board top side overview]
[Photo reference: IMG_0368.jpg -- board bottom side]

### 4.2 Major ICs Identified (Top Side)

Reading component markings under magnification (10x loupe):

1. **Main processor:** STMicroelectronics STM32F407VGT6 -- ARM Cortex-M4, 168 MHz, 1MB Flash, 192KB SRAM, LQFP-100 package. Date code 2348 (week 48, 2023).

2. **SPI Flash:** Winbond W25Q128JVSIQ -- 128Mbit (16MB) SPI NOR flash, SOIC-8. This likely holds firmware image, configuration data, and possibly cryptographic material.

3. **Ethernet PHY:** Microchip LAN8742A-CZ -- 10/100 Ethernet transceiver, QFN-24. Connected to the STM32's RMII interface.

4. **CAN transceiver:** Microchip MCP2551-I/SN -- high-speed CAN bus transceiver, SOIC-8. CAN bus runs to the laser control subsystem.

5. **RS-485 transceiver:** Maxim MAX485ESA+ -- half-duplex RS-485/RS-422 transceiver, SOIC-8. Connected to the legacy sensor bus.

6. **Crypto IC:** Microchip ATECC608A-MAHDA-S -- secure element, UDFN-8. Likely used for firmware authentication or secure boot. Noted: this is the "A" variant without I2C address locking.

7. **Voltage regulators:** Two Texas Instruments TPS5430DDA (5V and 3.3V rails), plus a Microchip MCP1700-3302E (3.3V LDO, likely for the crypto IC).

8. **EEPROM:** Microchip 24LC256-I/SN -- 256Kbit I2C EEPROM, SOIC-8. Likely stores calibration data or machine-specific parameters.

9. **Crystal oscillators:** 8.000 MHz (main CPU HSE), 32.768 kHz (RTC), 25.000 MHz (Ethernet PHY).

### 4.3 Debug and Test Interfaces

**J12 -- UART header:** 4-pin 2.54mm header, unpopulated (through-hole pads). Silkscreen labels: GND, TX, RX, 3V3. Confirmed active UART at 115200 baud, 8N1 using a logic analyser during power-up. Outputs boot messages including firmware version, build timestamp, and memory test results. See section 6.

**J5 -- SWD header:** 10-pin 1.27mm header (ARM Cortex standard pinout), populated with pin header. Confirmed connectivity to STM32 SWD interface using a Segger J-Link. Device ID reads correctly. Note: Readout protection (RDP) is set to Level 1. This prevents direct flash read-out via SWD but does not prevent JTAG attachment for debugging with breakpoints.

**TP1-TP8:** Eight test points along the board edge. TP1 = 3.3V, TP2 = 5V, TP3 = GND, TP4 = CAN_H, TP5 = CAN_L, TP6 = SPI_CLK, TP7 = SPI_MOSI, TP8 = SPI_MISO.

**J8 -- SD card slot:** MicroSD card slot on the board edge. At time of inspection, a 4GB SanDisk Industrial MicroSD card was installed, labelled "AMS-FW-3.8.2". Card was imaged for later analysis (hash SHA-256: a7c3f2e8...[truncated]).

---

## 5. Physical Ports Summary

| Port | Location | Type | Status |
|------|----------|------|--------|
| USB Micro-B | PLC front panel | USB 2.0 | Accessible with cabinet door open |
| USB Micro-B | Main controller board (J3) | USB 2.0 | Requires tamper seal removal |
| PROFINET x2 | PLC X1 P1, P2 | RJ-45 Ethernet | Connected to network switch |
| PROFIBUS DP | PLC X2 | 9-pin D-sub | Unused/disconnected |
| RS-232/485 | Communication gateway | 9-pin D-sub | Selectable via DIP switch |
| Ethernet x2 | Communication gateway | RJ-45 | Connected (ETH1 to switch, ETH2 unused) |
| RS-232 console | Hirschmann switch | RJ-45 serial | Accessible with cabinet door open |
| Service Ethernet | Rear panel cable gland | RJ-45 | Routed to switch port 7 |
| SWD debug | Main controller J5 | 10-pin 1.27mm | Requires enclosure removal |
| UART debug | Main controller J12 | 4-pin 2.54mm | Requires enclosure removal |
| MicroSD | Main controller J8 | MicroSD slot | Requires enclosure removal |
| SIMATIC MC slot | PLC front panel | Proprietary | Slot empty at time of inspection |

---

## 6. Boot Process Observations

Connected to J12 UART (115200 8N1) and powered the unit from cold. Boot sequence captured (excerpt):

```
[0.000] AMS-500 Main Controller Bootloader v1.2.0
[0.002] Build: 2024-02-15T14:22:33Z
[0.003] Hardware Rev: C.2
[0.010] Memory test: 192KB SRAM ... PASS
[0.045] SPI Flash: W25Q128 detected, ID 0xEF4018
[0.048] ATECC608A: Device present, serial 01239ABC[...]
[0.051] Firmware signature verification ... OK
[0.089] Loading firmware image from SPI flash @ 0x00010000
[0.203] Firmware: AMS-500 v3.8.2 (build 20240801-rel)
[0.204] Copyright (c) 2024 [Vendor]
[0.250] Initialising peripherals...
[0.251]   UART0: 115200 8N1 (debug console)
[0.252]   CAN1: 500kbps, normal mode
[0.253]   SPI1: 10MHz, master
[0.254]   ETH0: LAN8742A link up, 100Mbps FD
[0.255]   I2C1: 400kHz, ATECC608A, 24LC256
[0.280] EEPROM: Machine serial AMS-5-2024-00147
[0.282] Loading calibration data ... OK (CRC32 match)
[0.300] Connecting to S7-1500 PLC via PROFINET...
[0.850] PROFINET: AR established, device OK
[1.200] System ready. Entering main loop.
```

Key observations:
- Bootloader performs firmware signature verification using the ATECC608A secure element
- The SPI flash base address 0x00010000 suggests a 64KB bootloader region at 0x00000000-0x0000FFFF
- Machine serial number is stored in the I2C EEPROM, not hardcoded
- CAN bus is initialised at 500 kbps -- this communicates with the laser control subsystem
- PROFINET connection to the PLC is established as an IO device

---

## 7. Tamper Evidence Summary

| Item | Type | Status |
|------|------|--------|
| Main controller enclosure | Holographic tamper seal | Intact prior to our inspection. Broken during tear-down. |
| Right service panel | Torx T25 security screws (x6) | No visible signs of prior removal. |
| Laser optics housing | "Warranty void" sticker + pentalobe screws | Intact. Not opened during this assessment. |
| Build chamber | Bolted panel (M8 hex x12) | Bolts had thread-locking compound, consistent with factory assembly. |
| PLC memory card slot | Rubber flap (no seal) | No tamper evidence. Card slot physically accessible. |
| Cabinet lock | Standard triangular key | Common key profile, no tamper evidence possible. |

---

## 8. Physical Access Risk Assessment

**Low barrier (cabinet key or no tool required):**
- PLC USB port
- PLC PROFINET ports
- Hirschmann switch console port
- SIMATIC memory card slot
- Communication gateway serial port
- Service Ethernet port (rear panel)
- Factory reset button (rear panel)

**Medium barrier (Torx security screwdriver required):**
- Main controller board and all debug interfaces
- MicroSD card containing firmware

**High barrier (specialist tools or destructive access):**
- Laser optics assembly (pentalobe screws, warranty seal)
- Build chamber sealed internals

---

## 9. Initial Findings of Security Relevance

1. The PLC memory card slot was empty. An attacker with brief physical access could insert a prepared SIMATIC Memory Card to alter PLC program or configuration.

2. The Hirschmann managed switch uses a standard RJ-45 console port accessible with the cabinet door open. Default credentials for this switch series are well-documented (admin/admin on Hirschmann Classic platform).

3. The main controller board has a populated SWD debug header. While RDP Level 1 is set, this does not prevent debugging -- only direct flash readout. A fault injection attack on the STM32F4 could potentially downgrade RDP to Level 0.

4. UART debug console is active and outputs detailed system information including firmware version and hardware configuration on every boot. No authentication is required for the debug console.

5. The service Ethernet port on the rear panel provides direct network access to the internal PROFINET segment with no apparent filtering.

6. The factory reset button on the rear panel is protected only by a breakable plastic cap. This could be used to restore default configurations, including any hardened network settings.

7. The communication gateway module has a TFTP server enabled by default (see TD-AMS500-003), which could allow firmware extraction or modification from the network.

---

**Next steps:** Detailed PCB analysis (TD-AMS500-002), communication gateway inspection (TD-AMS500-003), laser control subsystem assessment (TD-AMS500-004), network traffic capture and protocol analysis.

---

*Document version: 1.0 | Last updated: 2026-03-18*
