# AMS-500 Electrical Schematic Description

**Project:** AMS-500 Security Assessment  
**Document ID:** WD-AMS500-001  
**Classification:** OFFICIAL  
**Assessor:** [REDACTED]  
**Date:** 2026-03-25  
**Reference:** Derived from vendor schematic set AMS-500-EL-001 through AMS-500-EL-024  

---

## 1. Scope

This document provides a text description of the AMS-500 electrical schematic for use in security assessment context. The original schematics are 24 sheets in PDF format. This description covers the power distribution, PLC I/O wiring, network cabling, EtherCAT motion control, safety circuit, and sensor bus. Component references (e.g., -K1, -Q1) follow the vendor's naming convention from the original drawings.

---

## 2. Power Distribution (Sheets 1-3)

### 2.1 Incoming Supply

The AMS-500 is supplied by a 3-phase 400V 50Hz connection via a CEE 63A plug (IEC 60309, 3P+N+E). The supply enters through an IP68 cable gland on the rear panel and connects to the main incoming terminal block (-X0).

From -X0, supply is routed to:

- **-Q1:** Main circuit breaker, Siemens 5SY4332-7, 32A 3-pole. This is the master disconnect for the control cabinet. Lockout/tagout provision via a padlock hasp on the breaker handle.
- **-Q5:** Laser power supply breaker, 3-pole 30A, feeding the IPG YLR-1000 laser source directly. This is a separate feed from the main breaker, not downstream of -Q1. Both -Q1 and -Q5 are fed from -X0.
- **-Q6:** Chiller supply breaker, 3-pole 16A, feeding the laser cooling system.

An earth bus bar (-PE1) runs the full width of the cabinet, bonded to the cabinet frame with 10mm2 green/yellow conductor. All equipment earths terminate here.

### 2.2 24VDC Control Supply

Downstream of -Q1:

- **-Q2:** Auxiliary breaker, 2-pole 6A, feeds the primary 24VDC power supply.
- **-G1:** Siemens SITOP PSU8200 (6EP3334-8SB00-0AY0), 400VAC input, 24VDC 10A output. This supplies the PLC, I/O modules, communication gateway, HMI panel, and signal conditioning circuits.
- **-A1:** Phoenix Contact QUINT4-UPS/24DC/24DC/20, connected in series between -G1 and the PLC. Provides approximately 10 minutes of backup power for controlled shutdown on mains failure. The UPS has a battery status output (digital, 24VDC) wired to PLC digital input DI 0.0.

The 24VDC distribution bus is fused per branch:

| Fuse | Rating | Load |
|------|--------|------|
| -F1 | 4A | PLC CPU + signal modules |
| -F2 | 2A | Communication gateway module |
| -F3 | 2A | HMI panel |
| -F4 | 6A | Relay coils and solenoid valves |
| -F5 | 2A | Sensor power (24VDC sensor supply bus) |
| -F6 | 4A | Safety PLC and safety I/O |

All fuses are Siemens 5SG7 cylindrical fuse links in DIN-rail fuse holders.

### 2.3 Drive Power Supply

- **-Q3:** Auxiliary breaker, 2-pole 10A, feeds the servo drive DC bus power supply.
- **-G2:** Mean Well SDR-480-24, 24VDC 20A output. Dedicated supply for the Beckhoff AX5206 servo drives (the drives have internal DC-DC converters but require 24VDC logic supply and a separate 3-phase or DC bus supply for the power stage).

The servo power stage supply is taken from the 3-phase mains downstream of -Q1 via a separate breaker:
- **-Q4:** 3-pole 16A breaker feeding the AX5206 mains input terminals (L1, L2, L3). The drives regenerate through a shared DC bus with a braking resistor (-R1, 100 ohm 500W, mounted externally on the cabinet roof).

---

## 3. PLC I/O Wiring (Sheets 4-9)

### 3.1 CPU and Module Configuration

The Siemens S7-1516-3 PN/DP PLC is configured with the following module rack:

| Slot | Module | Order Number | Function |
|------|--------|--------------|----------|
| 0 | CPU 1516-3 PN/DP | 6ES7516-3AN02-0AB0 | Main processor |
| 1 | SM 1231 AI 8x13bit | 6ES7231-4HF32-0XB0 | Thermocouple inputs |
| 2 | SM 1231 AI 4x16bit | 6ES7231-5QD32-0XB0 | Pressure/analogue inputs |
| 3 | SM 1221 DI 16x24VDC | 6ES7221-1BH32-0XB0 | Digital inputs |
| 4 | SM 1222 DQ 16xRelay | 6ES7222-1HH32-0XB0 | Digital outputs |
| 5 | CM 1241 RS422/485 | 6ES7241-1CH32-0XB0 | Serial communication |

### 3.2 Analogue Inputs -- Thermocouples (SM 1231, Slot 1)

Eight Type K thermocouple inputs for build chamber thermal monitoring:

| Channel | Tag | Location | Range |
|---------|-----|----------|-------|
| AI 0 | TC-101 | Build plate centre | 0-500 C |
| AI 1 | TC-102 | Build plate edge N | 0-500 C |
| AI 2 | TC-103 | Build plate edge S | 0-500 C |
| AI 3 | TC-104 | Build plate edge E | 0-500 C |
| AI 4 | TC-105 | Build chamber gas inlet | 0-200 C |
| AI 5 | TC-106 | Build chamber gas outlet | 0-200 C |
| AI 6 | TC-107 | Powder hopper | 0-100 C |
| AI 7 | TC-108 | Laser optics housing | 0-80 C |

All thermocouples are 2-wire with cold-junction compensation handled internally by the SM 1231 module. Cable type: silicone-insulated Type K thermocouple extension wire, routed in a separate cable tray from power conductors for EMC reasons.

### 3.3 Analogue Inputs -- Pressure and General (SM 1231, Slot 2)

| Channel | Tag | Sensor | Signal | Range |
|---------|-----|--------|--------|-------|
| AI 0 | PT-201 | Chamber pressure | 4-20 mA | 0-2 bar abs |
| AI 1 | PT-202 | Gas supply pressure | 4-20 mA | 0-10 bar |
| AI 2 | OX-201 | Oxygen sensor | 0-10 V | 0-25% O2 |
| AI 3 | FT-201 | Gas flow rate | 4-20 mA | 0-200 l/min |

4-20 mA sensors are wired with 250 ohm precision shunt resistors at the module terminals to convert current to voltage. The SM 1231 4x16bit module is configured for 0-10V input on all channels.

### 3.4 Digital Inputs (SM 1221, Slot 3)

| Channel | Tag | Description | Type |
|---------|-----|-------------|------|
| DI 0.0 | UPS_OK | UPS battery status | NO contact |
| DI 0.1 | CHILLER_RUN | Chiller running feedback | NO contact |
| DI 0.2 | GAS_LOW | Inert gas low pressure alarm | NC contact |
| DI 0.3 | FILTER_DP | Gas filter differential pressure alarm | NC contact |
| DI 0.4 | HOPPER_FULL | Powder hopper level high | NO contact (capacitive prox) |
| DI 0.5 | HOPPER_LOW | Powder hopper level low | NO contact (capacitive prox) |
| DI 0.6 | RECOATER_HOME | Recoater blade home position | NO contact (inductive prox) |
| DI 0.7 | RECOATER_END | Recoater blade end position | NO contact (inductive prox) |
| DI 1.0 | BUILD_PLATE_LOCK | Build plate clamped confirmation | NO contact |
| DI 1.1 | OVERFLOW_BIN_FULL | Overflow powder bin full | NO contact (capacitive prox) |
| DI 1.2 | SIEVE_RUN | Powder sieve running feedback | NO contact |
| DI 1.3 | LASER_READY | Laser source ready signal | NO contact (from IPG) |
| DI 1.4 | SCANNER_READY | Scanner ready signal | NO contact (from SCANLAB) |
| DI 1.5 | DOOR_CLOSED | Build chamber door closed (non-safety) | NO contact |
| DI 1.6 | MAINT_MODE | Maintenance mode key switch | NO contact |
| DI 1.7 | SPARE | -- | -- |

All digital inputs are sinking type, 24VDC, with LED status indication on the module face.

### 3.5 Digital Outputs (SM 1222, Slot 4)

| Channel | Tag | Description | Type |
|---------|-----|-------------|------|
| DQ 0.0 | GAS_INLET_VALVE | Inert gas inlet solenoid | 24VDC relay, 2A |
| DQ 0.1 | GAS_OUTLET_VALVE | Inert gas outlet solenoid | 24VDC relay, 2A |
| DQ 0.2 | CHILLER_START | Chiller start command | 24VDC relay, 2A |
| DQ 0.3 | RECOATER_FWD | Recoater forward command | 24VDC relay, 2A |
| DQ 0.4 | RECOATER_REV | Recoater reverse command | 24VDC relay, 2A |
| DQ 0.5 | SIEVE_START | Powder sieve start | 24VDC relay, 2A |
| DQ 0.6 | BUILD_PLATE_CLAMP | Build plate clamp solenoid | 24VDC relay, 2A |
| DQ 0.7 | BEACON_GREEN | Status beacon green | 24VDC relay, 2A |
| DQ 1.0 | BEACON_AMBER | Status beacon amber | 24VDC relay, 2A |
| DQ 1.1 | BEACON_RED | Status beacon red | 24VDC relay, 2A |
| DQ 1.2 | EXTRACTION_FAN | Fume extraction fan | 24VDC relay via contactor -K3 |
| DQ 1.3 | HEATING_ENABLE | Build plate heater enable | 24VDC relay via SSR -K4 |
| DQ 1.4 | SPARE | -- | -- |
| DQ 1.5 | SPARE | -- | -- |
| DQ 1.6 | SPARE | -- | -- |
| DQ 1.7 | SPARE | -- | -- |

The relay module contacts are rated 2A/30VDC. Loads exceeding 2A (extraction fan motor, build plate heater) are driven via intermediate contactors or solid-state relays mounted on the bottom DIN rail.

---

## 4. EtherCAT Motion Control Network (Sheet 10-12)

### 4.1 Topology

The EtherCAT network is wired in a daisy-chain topology originating from the Hirschmann managed switch (via a dedicated VLAN port) and passing through the following devices in order:

```
Hirschmann RS20 Switch (Port 5, VLAN 10)
    |
    v
Beckhoff EK1100 EtherCAT Coupler
    |
    v
Beckhoff AX5206 Servo Drive #1 (X-axis recoater, Z-axis build platform)
    |
    v
Beckhoff AX5206 Servo Drive #2 (Powder handling axes 1 & 2)
    |
    v
Beckhoff AX5206 Servo Drive #3 (Auxiliary axes -- sieve, overflow)
    |
    v
Beckhoff EL1008 Digital Input Terminal (8x DI)
    |
    v
Beckhoff EL2008 Digital Output Terminal (8x DO)
    |
    v
Beckhoff EL3064 Analogue Input Terminal (4x AI, 0-10V)
    |
    v
Beckhoff EL4034 Analogue Output Terminal (4x AO, 0-10V)
    |
    v  (terminated -- last device, OUT port unused)
```

All cabling is Cat5e SF/UTP shielded, with M12 D-coded connectors at the servo drives and standard RJ-45 at the EL-series terminals. Cable lengths range from 0.5m (between adjacent terminals) to 3m (switch to EK1100 coupler). The total daisy-chain length is approximately 12m.

### 4.2 EtherCAT Coupler (EK1100)

The Beckhoff EK1100 coupler acts as the bridge between the Ethernet (PROFINET) side and the EtherCAT fieldbus. On the Ethernet side, it appears as a PROFINET IO-device to the S7-1500 PLC. On the EtherCAT side, it is the master device for the daisy-chain.

The EK1100 has two RJ-45 ports: IN (from switch) and OUT (to first slave). There is no configuration interface on the coupler itself -- it is configured via the PLC engineering tool (TIA Portal) through the PROFINET connection.

### 4.3 Servo Drives

Each AX5206 is a dual-axis servo drive. Motor connections use Beckhoff One Cable Technology (OCT) with encoder feedback embedded in the power cable. The drives accept motion commands from the EtherCAT bus (position, velocity, or torque mode, configured per-axis).

Motor feedback encoders are absolute single-turn (EnDat 2.2 protocol), providing 20-bit position resolution per revolution. The drives perform position loop closure locally at 8 kHz.

---

## 5. Safety Circuit (Sheets 13-16)

### 5.1 Safety PLC

The safety circuit is managed by a separate Siemens S7-1511F-1 PN safety PLC (F-CPU) in a small dedicated enclosure (-A2) mounted adjacent to the main control cabinet. This F-CPU has its own 24VDC supply from the main PSU via fuse -F6.

The safety PLC connects to the Hirschmann switch on a dedicated port (Port 4) and communicates with the main S7-1516 CPU via PROFIsafe over PROFINET.

Safety I/O modules:
- **F-DI 8x24VDC** (6ES7226-6BA32-0XB0): Safety-rated digital inputs
- **F-DQ 4x24VDC/2A** (6ES7226-6DA32-0XB0): Safety-rated digital outputs

### 5.2 E-Stop Chain

Two E-stop buttons are provided:
- **-S1:** Front panel, Siemens 3SU1150-0AB20-1CA0, red mushroom with yellow surround, twist-to-release.
- **-S2:** Rear service area, identical model.

Both are wired dual-channel (2x NC contacts each) to F-DI channels 3 and 4. The safety PLC runs cross-fault monitoring. Response time from E-stop activation to safety output de-energisation: < 50 ms (SIL 3 / PLe).

E-stop activation triggers:
1. Laser enable signal removed (laser emission stops immediately)
2. Servo drives safe-torque-off (STO) activated via the AX5206 STO input
3. Gas valves de-energised (fail-closed)
4. Red beacon activated

### 5.3 Guard Interlocks

The build chamber door interlock uses a Schmersal BNS 260-11/01ZG-ST-L magnetic safety switch with a coded actuator. Dual-channel wiring to F-DI channels 1 and 2.

Guard interlock behaviour:
- Door open during idle: laser and motion systems inhibited, gas inerting continues
- Door opened during build: immediate laser shutdown, servo STO, build aborted
- Door re-close: requires manual reset (reset button on operator panel) before resuming

### 5.4 Laser-Specific Safety

The laser safety circuit is described in TD-AMS500-004 section 5. In summary, the safety PLC controls two independent relay channels (-K1, -K2, Siemens 3SK1 series) that both must be energised for the laser enable signal to reach the IPG laser source. The safety logic requires simultaneous satisfaction of: key switch ON, door interlock closed, E-stop circuit healthy, laser source ready, and emission indicator functional.

---

## 6. Ethernet Network Cabling (Sheets 17-19)

### 6.1 Network Topology

The internal network uses a star topology centred on the Hirschmann RS20-0800T2T1SDAEHH06.0 managed switch:

| Port | Device | Cable | Length | VLAN |
|------|--------|-------|--------|------|
| 1 | S7-1516 PLC (PN X1 P1) | Cat6 S/FTP green | 0.5m | VLAN 1 (default) |
| 2 | Operator HMI (CP3915) | Cat6 S/FTP green | 2.0m | VLAN 1 |
| 3 | Communication gateway (ETH1) | Cat6 S/FTP green | 0.8m | VLAN 1 |
| 4 | Safety PLC (S7-1511F) | Cat6 S/FTP green | 1.2m | VLAN 1 |
| 5 | EtherCAT coupler (EK1100) | Cat5e SF/UTP green | 3.0m | VLAN 10 |
| 6 | Laser control unit MCB | Cat6 S/FTP green | 1.5m | VLAN 1 |
| 7 | Service port (rear panel) | Cat6 S/FTP grey | 4.0m | VLAN 20 |
| 8 | Empty | -- | -- | -- |

Note: The VLAN configuration was documented on an internal sticker reference "AMS-NET-002" but this document was not available at the time of assessment. The VLAN assignments above were determined by reading the switch configuration via the console port.

### 6.2 IP Address Allocation (from switch ARP table and PROFINET discovery)

| Device | IP Address | Subnet | Notes |
|--------|-----------|--------|-------|
| S7-1516 PLC | 192.168.1.10 | /24 | PROFINET controller |
| HMI panel | 192.168.1.11 | /24 | Static |
| Comm gateway ETH1 | 192.168.1.20 | /24 | PROFINET device |
| Safety PLC | 192.168.1.30 | /24 | PROFIsafe device |
| EK1100 coupler | 192.168.1.40 | /24 | PROFINET device |
| Main controller board | 192.168.1.50 | /24 | PROFINET device |
| Hirschmann switch | 192.168.1.1 | /24 | Management interface |
| Service port | DHCP | /24 | DHCP served by switch |

Security observation: The service port (rear panel) is on VLAN 20 but DHCP is enabled on that VLAN, which means any device plugged into the rear service port will automatically receive an IP address. Inter-VLAN routing between VLAN 1 and VLAN 20 was found to be enabled on the switch, effectively allowing full access from the service port to all internal devices.

---

## 7. RS-485 Legacy Sensor Bus (Sheets 20-21)

### 7.1 Bus Configuration

The RS-485 sensor bus originates from the Siemens CM 1241 communication module in the PLC rack. It is a 2-wire half-duplex bus running at 9600 baud, 8N1.

Bus parameters:
- Cable: Belden 3105A (shielded twisted pair, RS-485 rated)
- Topology: multi-drop daisy-chain
- Termination: 120 ohm resistors at both ends (at the CM 1241 module and at the last sensor)
- Maximum cable length: 35m total (within spec for 9600 baud)
- Protocol: Modbus RTU

### 7.2 Device Addresses

| Address | Device | Location | Measurement |
|---------|--------|----------|-------------|
| 1 | Vaisala HMT330 | Build chamber | Humidity + temperature |
| 2 | Vaisala HMT330 | Powder storage | Humidity + temperature |
| 3 | Endress+Hauser Deltabar PMD75 | Gas inlet manifold | Differential pressure |
| 4 | Endress+Hauser Deltabar PMD75 | Gas outlet manifold | Differential pressure |
| 5 | Keyence FD-Q50C | Cooling water supply | Flow rate |
| 6 | Keyence FD-Q50C | Cooling water return | Flow rate |
| 7-16 | -- | Reserved | -- |

The Modbus RTU protocol has no authentication or encryption. Any device on the RS-485 bus can read from or write to any other device by transmitting valid Modbus frames. The bus is physically accessible at the terminal strip inside the control cabinet where individual sensor cables are terminated.

---

## 8. Security Observations from Schematic Review

1. **Flat PROFINET network.** The PLC, HMI, communication gateway, safety PLC, laser controller, and EtherCAT coupler are all on the same VLAN (VLAN 1). There is no segmentation between safety-critical and non-critical devices.

2. **Service port provides unrestricted internal access.** VLAN 20 (service port) has inter-VLAN routing to VLAN 1, with DHCP enabled. An attacker plugging into the rear service port gets full network access to all internal devices.

3. **Unauthenticated sensor bus.** The RS-485 Modbus RTU bus carries environmental sensor data with no authentication. Spoofed sensor readings (e.g., false oxygen concentration or temperature) could cause the PLC to make incorrect process decisions.

4. **Single point of power failure.** The UPS only protects the PLC. The communication gateway, switch, HMI, and safety PLC are on the same 24VDC bus but not behind the UPS. A brief mains interruption could cause the switch and gateway to reboot while the PLC remains running, potentially creating inconsistent states.

5. **Servo STO wiring is safety-rated.** The safe-torque-off function on the AX5206 drives is properly wired through the safety PLC -- this is a correct safety architecture. However, the motion command path (EtherCAT) has no security and could be used to command abnormal motion profiles while the safety system does not intervene (as long as the motion stays within the safe envelope monitored by the STO function).

---

*Document version: 1.0 | Last updated: 2026-03-25*
