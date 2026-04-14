# Phoenix Contact QUINT POWER Power Supply — Technical Datasheet

## Product Overview

| Parameter | Value |
|-----------|-------|
| Order Number | 2904602 |
| Type Designation | QUINT4-PS/1AC/24DC/20 |
| Manufacturer | Phoenix Contact GmbH & Co. KG |
| Product Family | QUINT POWER (4th generation) |
| Function | Primary-switched AC/DC power supply with SFB Technology |

## Description

The QUINT4-PS/1AC/24DC/20 is a DIN rail mounted power supply providing 24 VDC at 20 A (480 W) from a single-phase AC input. It features Phoenix Contact's patented SFB (Selective Fuse Breaking) Technology, which provides up to 6x nominal current for 15 ms to trip downstream circuit breakers in a fault condition, ensuring selective protection without oversizing the power supply.

In the AMS-500 installation, this PSU provides the primary 24 VDC supply for the PLC, I/O modules, HMI, and field instrumentation.

## Technical Specifications

### Input

| Parameter | Specification |
|-----------|--------------|
| Input Voltage Range | 100-240 V AC (85-264 V AC extended) |
| Frequency | 45-65 Hz |
| Input Current | 5.1 A at 120 V AC / 2.7 A at 230 V AC |
| Inrush Current | <20 A (at 230 V AC, cold start) |
| Power Factor | >0.98 (active PFC) |
| Input Fuse (recommended) | 10 A slow-blow (external) |
| Mains Connection | Push-in terminal block, max. 2.5 mm2 |

### Output

| Parameter | Specification |
|-----------|--------------|
| Output Voltage | 24 V DC (adjustable 18-29.5 V DC via front potentiometer) |
| Output Current | 20 A continuous |
| Output Power | 480 W continuous |
| SFB Current (boost) | 120 A for 15 ms (6x nominal) |
| Parallel Operation | Yes, with active current sharing |
| Redundancy | Via QUINT4-DIODE/1X40 oring module |
| Ripple and Noise | <50 mVpp |
| Voltage Accuracy | +/- 1% at nominal load |
| Dynamic Response | <1% overshoot at 50% load step |

### SFB Technology (Selective Fuse Breaking)

SFB Technology dynamically boosts output current to 6x nominal (120 A) for up to 15 ms when a short circuit is detected on a downstream branch. This ensures that the branch circuit breaker trips selectively without causing the main supply to sag or other branches to lose power.

| Parameter | Value |
|-----------|-------|
| SFB Current | 120 A (6x In) |
| SFB Duration | 15 ms |
| Trigger Condition | Output current exceeds 120% of nominal |
| Recovery Time | <100 ms |

### Efficiency

| Load | Efficiency |
|------|-----------|
| 25% | 91.5% |
| 50% | 93.2% |
| 75% | 93.8% |
| 100% | 93.5% |

### Protections

| Protection | Method |
|-----------|--------|
| Overcurrent | Current limiting with SFB boost |
| Overvoltage | Output clamp at 30 V DC |
| Short Circuit | Continuous, auto-recovery |
| Overtemperature | Thermal derating above 60 C, shutdown at 75 C |
| Input Surge | Varistor + gas discharge tube |
| Inrush Current | NTC limiter with bypass relay |

### Diagnostics

| Signal | Type | Description |
|--------|------|-------------|
| DC OK | Relay contact (NO/NC) | Output voltage within tolerance (>90% of set value) |
| DC OK | LED (green) | Output voltage OK |
| Overload | LED (yellow) | Output current >100% (thermal derating active) |
| Status | LED (green) | Mains present, PSU operational |

The DC OK relay contact is used in the AMS-500 for PLC monitoring (wired to S7-1500 DI, address %I0.7). The PLC monitors this contact and initiates an orderly shutdown of the laser and motion system if the power supply reports a fault.

### Physical

| Parameter | Specification |
|-----------|--------------|
| Dimensions (W x H x D) | 60 x 130 x 125 mm |
| Mounting | 35 mm DIN rail (EN 60715) |
| Weight | 750 g |
| Connection Method | Push-in terminal blocks |
| Wire Size | 0.2 - 6 mm2 (AWG 24 - 10) |
| Tightening Torque | 0.5 - 0.6 Nm |
| Protection Rating | IP20 |
| Cooling | Convection (no fan) |

### Environmental

| Parameter | Specification |
|-----------|--------------|
| Operating Temperature | -25 to +70 C (derating above 60 C) |
| Storage Temperature | -40 to +85 C |
| Humidity | 10-95% non-condensing |
| Altitude | Up to 5000 m (derating above 2000 m) |
| Vibration | 5g (IEC 60068-2-6) |
| Shock | 30g (IEC 60068-2-27) |
| MTBF | >500,000 hours (SN 29500, 40 C) |

## AMS-500 Installation Details

### Power Distribution

The QUINT4 PSU feeds a 24 VDC distribution rail through a primary circuit breaker (Phoenix Contact CB TM1 24DC/20A). Downstream branches are protected by individual circuit breakers:

| Branch | Circuit Breaker | Load | Current |
|--------|----------------|------|---------|
| PLC (S7-1500 + I/O) | CB TM1 24DC/6A | 5.2 A peak | 3.8 A steady |
| HMI (IPC477E) | CB TM1 24DC/4A | 3.5 A peak | 2.1 A steady |
| EtherCAT Coupler + Terminals | CB TM1 24DC/4A | 3.2 A peak | 2.4 A steady |
| Network Switches (3x RS20) | CB TM1 24DC/4A | 1.8 A total | 1.5 A steady |
| Field Instruments (sensors, valves) | CB TM1 24DC/6A | 4.8 A peak | 3.2 A steady |
| Spare | CB TM1 24DC/4A | — | — |
| **Total** | | **18.5 A peak** | **13.0 A steady** |

The 20 A PSU provides adequate headroom (35% above steady-state) for the installation. SFB Technology ensures selective tripping of branch breakers during fault conditions.

### Wiring

- **Input:** L, N, PE from 230 V AC mains via 16 A MCB in main distribution board
- **Output:** +24V, 0V to primary distribution rail
- **DC OK:** NO relay contact wired to PLC DI %I0.7 (power fail monitoring)
- **Grounding:** PE bonded to DIN rail via spring contact; 0V bonded to PE at single point (star ground)

## Security Considerations

### SEC-PSU-001: Power Supply Manipulation
The output voltage is adjustable via a front-mounted potentiometer (18-29.5 V DC). Physical access to the control cabinet allows an attacker to adjust the output voltage outside the safe operating range of connected equipment. Mitigation: seal the potentiometer after commissioning.

### SEC-PSU-002: Power Denial
Interrupting the AC supply or triggering the overtemperature protection (e.g., blocking ventilation) would cause a controlled shutdown of all 24 VDC systems, including the safety PLC. The safety system should be designed to fail-safe (de-energise-to-trip) independently of the main PSU.

### SEC-PSU-003: DC OK Signal Spoofing
The DC OK relay contact is a simple dry contact. If an attacker has access to the PLC I/O wiring, the signal could be spoofed (held closed) to prevent the PLC from detecting a genuine power supply fault. Consider using a hardwired safety relay instead of a programmable PLC input for critical power monitoring.

## Compliance and Certifications

- CE (LVD 2014/35/EU, EMC 2014/30/EU)
- UL 508 Listed (E197838)
- CSA C22.2 No. 107.1
- GL (Marine)
- DNV GL (Maritime)
- ATEX II 3G Ex nA IIC T3 (Zone 2)
- IECEx (hazardous areas)
- RoHS, REACH compliant

## Ordering

| Order Number | Description |
|-------------|-------------|
| 2904602 | QUINT4-PS/1AC/24DC/20 (20 A) |
| 2904601 | QUINT4-PS/1AC/24DC/10 (10 A) |
| 2904603 | QUINT4-PS/1AC/24DC/40 (40 A) |
| 2907719 | QUINT4-DIODE/1X40 (redundancy module) |
| 0911400 | CB TM1 24DC/6A (branch circuit breaker) |

---
*Source: Phoenix Contact. Datasheet 104652_en_06, 2024.*
