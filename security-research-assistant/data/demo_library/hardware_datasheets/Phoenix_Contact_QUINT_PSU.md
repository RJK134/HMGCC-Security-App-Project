# Phoenix Contact QUINT POWER Power Supply -- Technical Datasheet

**Order Number:** 2904602  
**Product Family:** QUINT POWER  
**Full Designation:** QUINT4-PS/1AC/24DC/20 (2904602)  
**Document Type:** Technical Datasheet  
**Revision:** 2025-01  
**Source:** Phoenix Contact GmbH & Co. KG, Blomberg, Germany

---

## 1. Product Description

The Phoenix Contact QUINT POWER 2904602 (QUINT4-PS/1AC/24DC/20) is a high-performance DIN rail power supply designed for demanding industrial automation applications. It converts single-phase AC mains voltage (100-240 VAC or 100-350 VDC) to a regulated 24 VDC output at up to 20 A (480 W) continuous power.

The QUINT POWER series is distinguished by its SFB (Selective Fuse Breaking) Technology, which provides a patented 6x nominal current reserve (up to 120 A for 12 ms) to ensure reliable tripping of standard miniature circuit breakers (MCBs) in branch circuits. This guarantees selective fault clearing without causing total system power loss -- a critical requirement in industrial control systems where a single short circuit in one branch must not disable unrelated control circuits.

In the AMS-500 additive manufacturing system, the QUINT POWER 2904602 serves as the primary 24 VDC power supply for the control system, powering the Siemens S7-1500 PLC, Beckhoff EtherCAT coupler and I/O terminals, sensor inputs, valve outputs, and various auxiliary 24 VDC loads within the control cabinet.

### 1.1 Key Features

- High power density: 480 W in a compact 52 mm width enclosure
- SFB Technology: 6x In (120 A) for 12 ms for reliable MCB tripping
- Static POWER BOOST: 120% continuous output (24 A / 576 W) at up to 45 degrees C
- Dynamic POWER BOOST: Up to 25 A peak for motor starting and capacitive loads
- Preventive function monitoring with relay output
- Wide input voltage range: 100-240 VAC / 100-350 VDC
- High efficiency: up to 95.4%
- Full power across entire operating temperature range (-25 to +60 degrees C, derated above +45 degrees C)
- Conformal-coated PCB for enhanced environmental protection
- MTBF > 500,000 hours per IEC 61709 / SN 29500

---

## 2. Electrical Specifications

### 2.1 Input

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Input voltage (AC)               | 100 - 240 VAC (nominal), 85 - 264 VAC (operating range) |
| Input voltage (DC)               | 100 - 350 VDC                         |
| Input frequency                  | 45 - 65 Hz (AC) or DC                 |
| Input current (at 230 VAC, full load)| 2.6 A                             |
| Input current (at 120 VAC, full load)| 5.2 A                             |
| Inrush current (230 VAC)         | < 20 A peak (< 1 ms)                 |
| Inrush current (120 VAC)         | < 15 A peak (< 1 ms)                 |
| Power factor (at full load, 230 VAC)| > 0.99 (active PFC)               |
| Input fuse (recommended external)| 10 A slow-blow (for 230 VAC input)   |
| Input fuse (recommended external)| 16 A slow-blow (for 120 VAC input)   |
| Input connector                  | Screw terminal block (removable), 3-pin (L, N, PE) |
| Wire size (input)                | 0.2 - 6 mm^2 (AWG 24 - 10)          |
| Mains overvoltage category       | III (per IEC 60664-1)                 |

### 2.2 Output

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Output voltage (nominal)         | 24 VDC                                 |
| Output voltage (adjustable range)| 18 - 29.5 VDC (via front-panel potentiometer) |
| Output voltage accuracy          | < +/- 1% (static, at full load)       |
| Output current (continuous, nominal)| 20 A                                |
| Output current (static POWER BOOST)| 24 A (120%) continuous at <= 45 degC |
| Output current (SFB peak)        | 120 A (6x In) for 12 ms               |
| Output current (dynamic POWER BOOST)| 25 A for up to 5 seconds            |
| Output power (nominal)           | 480 W                                  |
| Output power (static BOOST)      | 576 W at <= 45 degrees C               |
| Ripple and noise (V_pk-pk)       | < 50 mV (20 MHz bandwidth)             |
| Output impedance                 | < 4 mOhm (DC) at full load            |
| Load regulation                  | < 0.5% (0 - 100% load change)         |
| Line regulation                  | < 0.2% (85 - 264 VAC input change)    |
| Output connector                 | Screw terminal block (removable), 4-pin (+, +, -, -) |
| Wire size (output)               | 0.2 - 16 mm^2 (AWG 24 - 6)           |
| Parallel operation               | Supported (active current sharing via droop mode) |
| Series operation                 | Supported (up to 60 VDC combined)      |
| Backfeed protection              | Integrated (reverse polarity protection on output) |

### 2.3 SFB Technology (Selective Fuse Breaking)

SFB Technology is a patented current reserve capability that provides up to 6 times the nominal output current for a short duration (12 ms). This guarantees that standard miniature circuit breakers (MCBs) with B or C trip curves in 24 VDC distribution circuits will trip reliably in the event of a short circuit, even at the end of long cable runs where cable resistance limits fault current.

**SFB Current Reserve:**

| Duration  | Maximum Output Current | Multiple of Nominal |
|-----------|----------------------|---------------------|
| 12 ms     | 120 A                | 6x In               |
| 20 ms     | 100 A                | 5x In               |
| 50 ms     | 60 A                 | 3x In               |
| Continuous| 20 A (24 A BOOST)    | 1x (1.2x)           |

> **NOTE:** The SFB capability ensures that a 6 A MCB (C-trip curve) protecting a branch circuit will trip within the required time (<100 ms) even if the wiring impedance between the PSU and the fault location is significant. Without SFB, many industrial PSUs enter hiccup mode or current-limit during a short circuit, preventing the MCB from tripping and leaving the fault uncleared. This can cause unpredictable behaviour in the control system.

### 2.4 Efficiency

| Load       | Input Voltage | Efficiency |
|------------|---------------|------------|
| 100% (20 A)| 230 VAC      | 95.4%      |
| 100% (20 A)| 120 VAC      | 94.2%      |
| 75% (15 A) | 230 VAC      | 95.0%      |
| 50% (10 A) | 230 VAC      | 94.2%      |
| 25% (5 A)  | 230 VAC      | 91.8%      |
| No load     | 230 VAC      | < 1 W input |

---

## 3. Protection Features

### 3.1 Input Protection

| Protection Type                  | Specification                          |
|----------------------------------|----------------------------------------|
| Input fuse (internal)            | T6.3A / 250 VAC (ceramic, non-replaceable) |
| Inrush current limiting          | NTC thermistor with relay bypass       |
| Input overvoltage protection     | Varistor (MOV) across L-N, L-PE, N-PE |
| Input transient protection       | IEC 61000-4-5 (surge), Level 4: 4 kV / 2 kV |
| Input reverse polarity (DC input)| Protected (no damage, no operation)    |

### 3.2 Output Protection

| Protection Type                  | Specification                          |
|----------------------------------|----------------------------------------|
| Overcurrent protection           | Constant current limiting at ~105% of setpoint, followed by SFB activation for short circuit |
| Short circuit protection         | SFB mode (6x In / 12 ms), then hiccup mode if fault persists |
| Overvoltage protection           | Clamped at 30 VDC (internal zener clamp) |
| Output reverse polarity          | Protected (integrated blocking diode)  |
| Overtemperature protection       | Thermal derating above +45 degrees C; shutdown at +75 degrees C internal |
| Overtemperature recovery         | Automatic restart when temperature drops below threshold |

### 3.3 Isolation

| Isolation                        | Rating                                 |
|----------------------------------|----------------------------------------|
| Input to output                  | 4 kVAC / 1 minute (type test)         |
| Input to output                  | 3 kVAC / 1 minute (routine test)      |
| Input to PE                      | 2 kVAC / 1 minute                     |
| Output to PE                     | 500 VDC                                |
| Isolation class                  | Class I (protective earth required)    |
| Creepage / clearance (I-O)       | > 8 mm / > 5.5 mm                     |

---

## 4. Diagnostic Features

### 4.1 Preventive Function Monitoring

The QUINT POWER 2904602 includes a built-in preventive function monitoring system that continuously evaluates the power supply's operating condition and provides early warning of degradation before a failure occurs.

**Monitored Parameters:**

- Output voltage (compared against adjustable threshold)
- Internal temperature (compared against thermal limits)
- Component aging (estimated remaining life based on operating stress)

### 4.2 Signalling Outputs

| Output              | Type                       | Description                            |
|--------------------|----------------------------|----------------------------------------|
| DC OK relay         | Potential-free relay (SPDT)| Indicates output voltage within specification |
| DC OK signal (pin)  | Transistor output, 24V/50mA| Electronic signal: output voltage OK    |

**DC OK Relay Specification:**

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Contact type                 | SPDT (1 changeover: COM, NO, NC)           |
| Maximum switching voltage    | 250 VAC / 30 VDC                           |
| Maximum switching current    | 1 A (resistive load)                       |
| Minimum switching load       | 10 mA / 10 VDC                             |
| Contact material             | AgNi (silver-nickel alloy)                 |
| Relay state (PSU OK)         | Energised (NO closed, NC open)             |
| Relay state (PSU fault)      | De-energised (NO open, NC closed)          |
| Trip threshold               | Output voltage < 90% of setpoint (adjustable) |

**Operating Modes of DC OK:**

The DC OK relay can be configured for different signalling modes via a DIP switch on the side of the unit:

| Mode               | DIP Setting | Behaviour                                |
|--------------------|-------------|------------------------------------------|
| Standard           | SW1: OFF    | DC OK active when output is within spec  |
| Preventive         | SW1: ON     | DC OK deactivates on early warning (component aging, temperature) |

### 4.3 Front Panel LEDs

| LED    | Colour        | State            | Meaning                            |
|--------|---------------|------------------|------------------------------------|
| OUTPUT | Green         | Steady on        | Output voltage within specification|
| OUTPUT | Green         | Blinking         | Output voltage in BOOST mode (>100% load) |
| OUTPUT | Off           | --               | No output or voltage below threshold |
| INPUT  | Green         | Steady on        | Input voltage present and within range |
| INPUT  | Off           | --               | No input voltage                   |
| STATUS | Green         | Steady on        | All parameters nominal             |
| STATUS | Amber/Yellow  | Steady on        | Preventive warning (check operating conditions) |
| STATUS | Red           | Steady on        | Fault condition (overtemperature, output failure) |

---

## 5. Mechanical Specifications

### 5.1 Dimensions

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Width                        | 52 mm (3 TE)                               |
| Height                       | 130 mm                                     |
| Depth                        | 125 mm (including DIN rail clip)           |
| Weight                       | 590 g                                      |

### 5.2 Mounting

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| Mounting method              | DIN rail, 35 mm (EN 60715)                 |
| DIN rail clip                | Integrated, tool-free snap-on               |
| Mounting orientation         | Vertical (preferred) or horizontal         |
| Minimum clearance (top)      | 25 mm (for ventilation / convection)       |
| Minimum clearance (bottom)   | 25 mm (for ventilation / convection)       |
| Minimum clearance (left/right)| 0 mm (side-by-side mounting permitted)    |

> **NOTE:** Although side-by-side mounting is permitted, spacing of 5-10 mm between adjacent PSUs improves thermal performance in high ambient temperature installations. For installations above +40 degrees C, follow the derating curve in Section 6.

### 5.3 Terminal Connections

| Terminal Block | Pins | Function                        | Torque          |
|---------------|------|---------------------------------|-----------------|
| Input          | 3    | L (Line), N (Neutral), PE (Earth)| 0.6 - 0.8 Nm  |
| Output         | 4    | +V, +V, -V, -V (dual pins each)| 0.6 - 0.8 Nm   |
| DC OK Relay    | 3    | COM, NO, NC                     | 0.4 - 0.6 Nm   |
| DC OK Signal   | 2    | +, - (transistor output)        | 0.4 - 0.6 Nm   |

All terminal blocks are removable plug-in type, allowing the PSU to be replaced without disconnecting individual wires.

---

## 6. Environmental Specifications

### 6.1 Operating Conditions

| Parameter                        | Specification                          |
|----------------------------------|----------------------------------------|
| Operating temperature            | -25 to +70 degrees C                   |
| Full output power range          | -25 to +45 degrees C (480 W / 20 A)   |
| Derating above +45 degrees C    | Linear derating to 60% at +70 degrees C |
| Storage temperature              | -40 to +85 degrees C                   |
| Relative humidity                | 10% to 95% (non-condensing)            |
| Operating altitude               | Up to 2000 m (without derating)        |
| Operating altitude (derated)     | Up to 5000 m (derating per IEC 62103)  |
| Vibration (IEC 60068-2-6)        | 5g, 10-150 Hz                          |
| Shock (IEC 60068-2-27)           | 30g, 11 ms, half-sine                  |
| Pollution degree                 | 2                                       |
| Protection rating                | IP20                                    |

### 6.2 Thermal Derating Curve

```
Output Current (A)
  |
24 +-----+
20 +-----+---------+
   |     |          \
15 +     |           \
   |     |            \
12 +     |             +
   |     |             |
   +--+--+--+--+--+--+--+--> Temperature (deg C)
  -25  0  25  45  55  65  70
```

Full 20 A output is available from -25 to +45 degrees C. Above +45 degrees C, output current derates linearly. At +60 degrees C, maximum output is approximately 15 A. At +70 degrees C, maximum output is approximately 12 A (60%).

### 6.3 Reliability

| Parameter                    | Specification                              |
|------------------------------|--------------------------------------------|
| MTBF (IEC 61709 / SN 29500) | > 500,000 hours (at +25 degrees C, full load) |
| MTBF (MIL-HDBK-217F)        | > 300,000 hours                            |
| Expected service life        | > 60,000 hours at +45 degrees C, full load |
| Warranty                     | 5 years (manufacturer standard)            |

---

## 7. EMC and Safety Compliance

### 7.1 Safety Certifications

| Certification                    | Standard                               |
|----------------------------------|----------------------------------------|
| CE Marking                       | EU LVD 2014/35/EU, EMC 2014/30/EU     |
| UL Listed                        | UL 61010-2-201 (File E200296)          |
| cUL Listed                       | CSA C22.2 No. 61010-2-201             |
| ATEX / IECEx                    | II 3 G Ex nA nC IIC T4 Gc             |
| Class I, Division 2              | Groups A, B, C, D (UL, FM)            |
| Marine                           | GL, LR, DNV, BV, ABS                  |
| Railway                          | EN 50155:2007 (OT4 = -25..+70 degC)   |
| CB Scheme                        | IEC 61010-2-201                        |
| Functional Safety (SIL)          | Suitable for SIL 2 applications per IEC 62061 (with redundant architecture) |

### 7.2 EMC Compliance

| Standard                         | Class / Level                          |
|----------------------------------|----------------------------------------|
| EN 61000-6-2:2005               | Industrial immunity (passed)           |
| EN 61000-6-4:2007               | Industrial emissions (passed)          |
| EN 61000-4-2 (ESD)              | Level 4: 8 kV contact, 15 kV air      |
| EN 61000-4-3 (Radiated immunity)| Level 3: 10 V/m                        |
| EN 61000-4-4 (Fast transient)   | Level 4: 4 kV                          |
| EN 61000-4-5 (Surge)            | Level 4: 4 kV CM, 2 kV DM             |
| EN 61000-4-6 (Conducted immunity)| Level 3: 10 V                         |
| EN 61000-4-11 (Voltage dips)    | Class A criteria met                   |
| EN 55032 / CISPR 32             | Class B (residential emissions limits) |
| FCC Part 15                      | Class A                                |

---

## 8. Application Notes for the AMS-500

### 8.1 Load Calculation

The following table shows the estimated 24 VDC power budget for the AMS-500 control cabinet:

| Load                              | Typical Current (A) | Peak Current (A) |
|-----------------------------------|---------------------|-------------------|
| Siemens S7-1500 CPU 1515SP PC2   | 1.8                 | 2.5               |
| Siemens I/O modules (8 modules)  | 1.2                 | 2.0               |
| Beckhoff EK1100 + terminals      | 1.5                 | 2.2               |
| Allen-Bradley PanelView Plus 7   | 1.5                 | 2.0               |
| Hirschmann RS20 switch           | 0.5                 | 0.5               |
| Pneumatic valve island (24V coils)| 2.0                | 4.0               |
| Sensors and transmitters          | 0.8                 | 1.0               |
| Indicator lamps and beacons       | 0.3                 | 0.5               |
| Safety relays (Pilz / Schmersal)  | 0.4                 | 0.6               |
| Door lock solenoid                | 0.5                 | 1.0               |
| **TOTAL**                         | **10.5 A**          | **16.3 A**        |

With a nominal 20 A output (24 A in BOOST mode), the QUINT POWER 2904602 provides adequate capacity with approximately 47% headroom for future expansion and inrush transients.

### 8.2 Wiring Recommendations

1. **Input wiring:** Use 2.5 mm^2 H05VV-F cable with a 10 A MCB (C-curve) on the incoming AC supply.
2. **Output wiring:** Use 2.5 mm^2 minimum for the main 24 VDC bus. Use 1.5 mm^2 for branch circuits.
3. **Branch circuit protection:** Install MCBs on each 24 VDC branch (2 A - 10 A as appropriate). SFB Technology ensures reliable tripping.
4. **PE connection:** The PE terminal on the input must be connected to the protective earth bus in the control cabinet. This is a safety requirement, not optional.
5. **Output terminal usage:** Both +V terminals are internally connected, as are both -V terminals. Use both pairs for high-current applications to reduce terminal heating.

### 8.3 Redundancy Configuration

For applications requiring high availability, two QUINT POWER units can be connected in parallel using the Phoenix Contact QUINT4-ORING/24DC/2X20/1X40 (order number 2904596) redundancy module. This module provides:

- Diode-isolated decoupling of two PSU outputs
- Seamless switchover if one PSU fails (< 5 ms)
- Individual PSU status monitoring
- Combined 40 A output capacity

### 8.4 Installation in AMS-500 Control Cabinet

The QUINT POWER 2904602 is mounted on the top DIN rail in the AMS-500 control cabinet, with the following layout:

```
[MCB 10A]--[QUINT POWER 2904602]--[MCB 6A]--[MCB 6A]--[MCB 4A]--[MCB 2A]
   |              |                    |          |          |         |
  AC In        24V Bus               PLC      HMI+Net    Motion    Sensors
                                   Branch    Branch      Branch    Branch
```

---

## 9. Ordering Information

| Order Number | Description                                              |
|-------------|----------------------------------------------------------|
| 2904602     | QUINT4-PS/1AC/24DC/20 (1-phase, 24V, 20A, with SFB)     |
| 2904601     | QUINT4-PS/1AC/24DC/10 (1-phase, 24V, 10A, with SFB)     |
| 2904603     | QUINT4-PS/1AC/24DC/40 (1-phase, 24V, 40A, with SFB)     |
| 2904604     | QUINT4-PS/3AC/24DC/20 (3-phase, 24V, 20A, with SFB)     |
| 2904596     | QUINT4-ORING/24DC/2X20/1X40 (redundancy module)          |
| 2905635     | QUINT4-BUFFER/24DC/40 (capacitor buffer module, 40A/20ms)|

### 9.1 Accessories

| Order Number | Description                                    |
|-------------|------------------------------------------------|
| 2908787     | Replacement terminal block set (input + output) |
| 2907832     | DIN rail end stop (clip-on)                     |
| 2905235     | Conformal coating spray (for field touch-up)    |

---

## 10. Dimensional Drawing

```
     52 mm
  +----------+
  |          | 130 mm
  | QUINT    |
  | POWER    |
  |          |
  | [OUTPUT] |  <-- Green LED
  | [INPUT]  |  <-- Green LED
  | [STATUS] |  <-- Multi-colour LED
  |          |
  | [V ADJ]  |  <-- Output voltage potentiometer
  |          |
  | [DIP SW] |  <-- Configuration switches (side)
  +----------+
       |
  125 mm depth
  (including DIN rail)
```

**Front Panel Elements:**
- OUTPUT LED (green): Output voltage status
- INPUT LED (green): Input voltage status
- STATUS LED (green/amber/red): Preventive monitoring status
- V ADJ potentiometer: Output voltage adjustment (18 - 29.5 VDC, factory set to 24.0 VDC)
- DIP switches (side access): Configure DC OK mode, parallel operation, BOOST enable

---

**End of Document**

*Based on Phoenix Contact product documentation. Phoenix Contact, QUINT POWER, and SFB Technology are registered trademarks of Phoenix Contact GmbH & Co. KG. All specifications subject to change without notice. Refer to official Phoenix Contact documentation for binding specifications.*
