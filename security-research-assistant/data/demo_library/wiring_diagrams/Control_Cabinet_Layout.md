# AMS-500 Control Cabinet Physical Layout

**Project:** AMS-500 Security Assessment  
**Document ID:** WD-AMS500-002  
**Classification:** OFFICIAL  
**Assessor:** [REDACTED]  
**Date:** 2026-03-25  
**Reference:** Supplements WD-AMS500-001 (Electrical Schematic Description)  

---

## 1. Cabinet Specification

The main control cabinet is a sheet-metal enclosure integrated into the right side of the AMS-500 chassis. It is not a standard off-the-shelf enclosure but a custom fabrication specific to the AMS-500 platform.

**Dimensions:** 600mm (W) x 400mm (D) x 750mm (H)  
**Material:** 1.5mm mild steel, powder-coated RAL 7035 light grey (interior and exterior)  
**Door:** Single-leaf, hinged on the left side (when viewed from the front), opening to the right. The door has a standard 7mm triangular insert lock (keyed alike, matching common Rittal/Schneider cabinet keys). No additional latching mechanism.  
**IP rating:** IP54 when door is closed (as marked on the vendor specification). Cable entry is from the bottom only, through a steel gland plate.

---

## 2. DIN Rail Layout

Three 35mm top-hat DIN rails are mounted horizontally across the full 600mm width of the cabinet interior. Rail spacing is approximately 200mm vertical centre-to-centre. Rails are designated Top, Middle, and Bottom from the vendor's assembly drawings.

### 2.1 Top DIN Rail -- Power Distribution

Reading left to right when facing the open cabinet:

| Position | Component | Description |
|----------|-----------|-------------|
| 1 | -Q1 | Main breaker, 3-pole 32A (Siemens 5SY4332-7). 45mm wide. |
| 2 | -Q2 | Aux breaker, 2-pole 6A (Siemens 5SY4206-7). Labelled "CTRL 24V". 36mm wide. |
| 3 | -Q3 | Aux breaker, 2-pole 10A (Siemens 5SY4210-7). Labelled "SERVO PWR". 36mm wide. |
| 4 | -Q4 | Aux breaker, 3-pole 16A (Siemens 5SY4316-7). Labelled "DRIVE MAINS". 45mm wide. |
| 5 | -- | 20mm gap (end stop) |
| 6 | -G1 | Siemens SITOP PSU8200 24VDC/10A. 70mm wide. |
| 7 | -A1 | Phoenix Contact QUINT4-UPS. 130mm wide. |
| 8 | -G2 | Mean Well SDR-480-24 24VDC/20A. 85mm wide. |

Remaining rail space: approximately 130mm unused, filled with blanking strips.

The incoming mains wiring enters from the bottom gland plate, rises along the left cable duct, and terminates at -Q1 and -Q5 (laser breaker, not on this rail -- see note below). The 24VDC output from -G1 routes through -A1 (UPS) and then down to the fuse holder row at the bottom of the top rail area. Six cylindrical fuse holders (-F1 through -F6) are mounted on a short secondary DIN rail segment (200mm) bolted below the main top rail on the right side.

**Note on laser supply:** Breakers -Q5 (laser, 3-pole 30A) and -Q6 (chiller, 3-pole 16A) are not in the main control cabinet. They are mounted in a separate small enclosure on the rear panel of the AMS-500 chassis, near the mains input. This separation is intentional -- the laser draws up to 30A at 400V and the vendor isolates this high-power circuit from the control electronics cabinet.

### 2.2 Middle DIN Rail -- PLC and I/O

Reading left to right:

| Position | Component | Width | Description |
|----------|-----------|-------|-------------|
| 1 | CPU 1516-3 PN/DP | 70mm | S7-1500 PLC CPU. PROFINET x2, PROFIBUS x1, USB. |
| 2 | SM 1231 AI 8x13bit | 35mm | Thermocouple inputs (Slot 1). |
| 3 | SM 1231 AI 4x16bit | 35mm | Pressure/analogue inputs (Slot 2). |
| 4 | SM 1221 DI 16x24VDC | 35mm | Digital inputs (Slot 3). |
| 5 | SM 1222 DQ 16xRelay | 35mm | Digital outputs (Slot 4). |
| 6 | CM 1241 RS422/485 | 35mm | Serial communication (Slot 5). |
| 7 | -- | 15mm | End stop and gap. |
| 8 | F-DI 8x24VDC | 35mm | Safety digital inputs (safety PLC enclosure -- NOTE: the safety PLC and its I/O are actually in the separate -A2 enclosure, not on this rail. See section 3.) |

Correction: positions 1-6 are on the middle DIN rail of the main cabinet. The safety PLC (-A2) is in its own enclosure mounted to the left of the main cabinet. The middle rail in the main cabinet carries only the standard PLC and I/O modules.

The S7-1500 modules are connected via the backplane bus connector (U-connector) that snaps between adjacent modules. The CPU is at the left end of the row. A 24VDC power feed from fuse -F1 connects to the CPU's power terminal. Each signal module draws power from the backplane bus.

The front of each module has a spring-loaded wiring connector that pulls out for field wiring access. All field wiring enters from the bottom cable duct, runs horizontally along a wire trough at the base of the middle rail, and connects to the appropriate module terminal.

### 2.3 Bottom DIN Rail -- Relays, Terminal Blocks, and Ancillary

Reading left to right:

| Position | Component | Description |
|----------|-----------|-------------|
| 1-8 | -K1 to -K8 | Eight Finder 40.52 miniature relays on 95.05 sockets. These are interposing relays driven by the PLC digital outputs (SM 1222 contacts rated only 2A) to switch larger loads (contactors, solenoid valves, heaters). |
| 9 | -K3 | Schneider LC1D09 contactor, 9A, for extraction fan motor. Coil driven by relay -K5. |
| 10 | -K4 | Crydom D1225 solid-state relay, 25A, for build plate heater. Controlled by relay -K6. |
| 11-70 | -X1 to -X60 | Weidmuller WDU 2.5 terminal blocks, approximately 60 positions. These form the field wiring interface. All sensor, actuator, and signal cables terminate here. Cross-wiring from these terminals routes to the PLC I/O modules on the middle rail. |

The terminal strip is divided into logical groups, separated by end plates and partition markers:

- Terminals 1-16: Digital inputs (sensors to PLC DI module)
- Terminals 17-24: Digital outputs (PLC DQ module to relay coils)
- Terminals 25-36: Analogue inputs (sensors to PLC AI modules)
- Terminals 37-44: Safety circuit connections (to/from safety PLC in -A2)
- Terminals 45-52: RS-485 bus connections (to sensor daisy-chain)
- Terminals 53-60: Spare / reserved

Each terminal is labelled with a ferrule marker corresponding to the wire number in the schematic (format: cabinet-terminal-wire, e.g., "C1-X23-W04"). Wire colours follow the vendor's convention: blue for 0VDC/neutral, brown or red for 24VDC/phase, green-yellow for earth, white for signal/analogue, grey for RS-485 data.

---

## 3. Safety PLC Enclosure (-A2)

The safety PLC is housed in a separate small enclosure, a Phoenix Contact ME MAX 45 2-8 G BK wall-mount box (approximately 200mm x 120mm x 90mm), bolted to the AMS-500 chassis to the left of the main control cabinet. This separation is deliberate -- the safety system is physically distinct from the standard control system.

Contents:
- Siemens S7-1511F-1 PN CPU (safety-rated F-CPU)
- F-DI 8x24VDC safety input module
- F-DQ 4x24VDC/2A safety output module
- Terminal strip for safety circuit field wiring (E-stop, door interlock, key switch, emission indicator feedback, laser ready, external interlock)

The -A2 enclosure has its own 24VDC supply feed from fuse -F6 in the main cabinet. A multi-conductor cable (10-core, shielded) runs between -A2 and the main cabinet terminal strip (terminals 37-44) for safety signal cross-wiring.

The -A2 enclosure has a single PROFINET cable (Cat6, 1.2m) running to the Hirschmann switch in the main cabinet (port 4).

---

## 4. Hirschmann Switch Mounting

The Hirschmann RS20-0800T2T1SDAEHH06.0 managed switch is not on the DIN rails. It is bracket-mounted on the right interior wall of the cabinet, positioned vertically between the top and middle DIN rails. This location provides:

- Easy access to the eight RJ-45 ports from the front when the door is open
- Proximity to the cable duct for Ethernet cable routing
- Adequate ventilation clearance (the switch is passively cooled)

The switch is powered by 24VDC from fuse -F2 via a dedicated 2-wire cable. The console port (RJ-45 serial, bottom of the switch) faces downward and is accessible with the cabinet door open.

---

## 5. Cable Routing and Management

### 5.1 Vertical Cable Ducts

Two vertical 40mm x 60mm slotted cable ducts (Panduit F4X6 series, light grey) run along the left and right interior walls of the cabinet, from bottom to top. These carry:

- **Left duct:** Incoming mains wiring (3-phase + N + PE), 24VDC distribution wiring, safety circuit cabling.
- **Right duct:** Ethernet cables, RS-485 bus cable, signal wiring from PLC modules to terminal strip.

The mains wiring (left duct) and signal/data wiring (right duct) are segregated. This separation is consistent with EMC best practice and IEC 61439 requirements for control cabinet wiring.

### 5.2 Horizontal Wire Troughs

A horizontal wire trough (Panduit H2X4, 50mm x 100mm) runs along the base of each DIN rail, providing a routing path for inter-rail connections.

### 5.3 Cable Entry

All external cables enter the cabinet from the bottom through a 3mm steel gland plate. Cable glands installed:

| Gland | Size | Cable | Destination |
|-------|------|-------|-------------|
| M1 | M25 | Mains supply 5-core (from rear panel CEE plug) | -Q1 main breaker |
| M2 | M20 | 24VDC to safety PLC -A2 (2-core) | Fuse -F6 |
| M3 | M20 | Safety signals to -A2 (10-core shielded) | Terminals 37-44 |
| M4 | M16 | Thermocouple bundle (8x TC extension wire) | Terminals 25-32 |
| M5 | M16 | 4-20mA sensor cables (4-core shielded) | Terminals 33-36 |
| M6 | M16 | Digital I/O field wiring (multi-core) | Terminals 1-24 |
| M7 | M16 | RS-485 bus cable (shielded twisted pair) | Terminals 45-46 |
| M8 | M20 | Ethernet cables x3 (to HMI, service port, -A2) | Switch ports 2, 4, 7 |
| M9 | M25 | EtherCAT cable (to EK1100 coupler) | Switch port 5 |
| M10 | M16 | CAN bus cable (to laser control unit) | Main controller board |

All glands are rated IP68. Cable shields are bonded to the gland plate via the gland body and cable armour clamps. The gland plate is bonded to the cabinet earth bus bar (-PE1) with a 6mm2 green-yellow conductor.

---

## 6. Grounding Scheme

### 6.1 Protective Earth

The cabinet frame is bonded to the incoming mains protective earth (PE) conductor at the main terminal block -X0. From -X0, a 10mm2 green-yellow conductor runs to the cabinet earth bus bar (-PE1, bare copper, mounted at the bottom of the cabinet).

All equipment with metal enclosures is bonded to -PE1:
- PLC rack (via DIN rail bonding)
- Hirschmann switch (via mounting bracket)
- Power supplies (via DIN rail bonding)
- Relay sockets (via DIN rail bonding)
- Cable gland plate (via 6mm2 conductor)
- DIN rails bonded to cabinet with star washers

### 6.2 Functional Earth (FE)

Analogue signal shields and RS-485 cable shields are terminated at a separate functional earth bar (-FE1) mounted adjacent to -PE1. The -FE1 bar is bonded to -PE1 at a single point (star earthing) to avoid ground loops.

The EtherCAT and Ethernet cable shields are bonded at the gland plate (360-degree contact via the cable gland) and at the device end (RJ-45 connector shell).

---

## 7. EMC Considerations

The following EMC measures were observed during inspection:

1. **Mains filter:** A Schaffner FN3258-30-33 3-phase EMC filter is installed between the incoming mains terminal -X0 and the main breaker -Q1. The filter is mounted on the left wall of the cabinet below the bottom DIN rail.

2. **Separation of power and signal cables:** As described in section 5.1, mains power and low-voltage signal cables are routed in separate cable ducts on opposite sides of the cabinet.

3. **Shielded cables:** All Ethernet, EtherCAT, RS-485, and CAN bus cables are shielded. Shields are bonded at both ends (cable gland at cabinet entry, connector shell at device end).

4. **Ferrite cores:** Snap-on ferrite cores (Fair-Rite 0431176451) are installed on the 24VDC power cables entering the PLC CPU and the communication gateway module.

5. **Surge protection:** A Phoenix Contact VAL-MS 230/3+1 surge arrester is installed on the incoming mains between the filter and -Q1.

---

## 8. Ventilation

A 120mm axial fan (ebm-papst 4114N/2H8) is mounted on the top wall of the cabinet, exhausting upward into the AMS-500 chassis (which has its own ventilation path to ambient). The fan runs continuously when the cabinet is powered. Air intake is through a filtered grille on the bottom of the cabinet door.

The fan provides approximately 10 m3/h airflow, sufficient to maintain interior temperature below 45C at 25C ambient with all equipment operating at full load. The interior temperature is not monitored electronically -- there is no temperature sensor or thermostat for the cabinet itself.

---

## 9. Labelling Convention

All components are labelled with self-adhesive white labels (Brother TZe-231 type) in the format:

```
-[Designator][Number]
[Description]
[Order/Part Number]
```

Example: The main PLC label reads:
```
-A10
CPU 1516-3 PN/DP
6ES7516-3AN02-0AB0
```

Wire ferrules are white, printed with the wire number in the format `C1-Xnn-Wnn` where C1 is the cabinet identifier, Xnn is the destination terminal, and Wnn is the wire number from the schematic.

Terminal blocks are labelled with sequential numbers (1-60) and colour-coded end plates (blue for signal, orange for safety, grey for power, green-yellow for earth).

---

## 10. Security Observations from Physical Layout

1. **Single lock, common key.** The cabinet door uses a standard 7mm triangular insert lock with a key that matches thousands of installed electrical cabinets. The lock provides no meaningful access control. A standard electrical cabinet key set (available for under 10 GBP from any electrical supplier) will open this cabinet.

2. **All ports accessible with door open.** Opening the cabinet door provides immediate physical access to: PLC USB port, PLC memory card slot, all PROFINET/PROFIBUS ports, Hirschmann switch console port, communication gateway serial port, and all DIN-rail mounted equipment.

3. **No internal tamper detection.** There are no tamper switches, intrusion sensors, or break-wire seals inside the cabinet. Opening the door does not generate any alert or log entry. The PLC and switch have no mechanism to detect that the cabinet has been opened.

4. **Safety PLC in separate enclosure is positive.** The physical separation of the safety PLC (-A2) from the standard control cabinet means that compromising the main cabinet does not directly compromise the safety system. However, the PROFINET cable between -A2 and the main cabinet switch runs through an exposed cable path (approximately 0.3m outside both enclosures) where it could be tapped or severed.

5. **Cable gland plate access from below.** The bottom-mounted gland plate is accessible from below the machine without opening the cabinet. While the glands themselves are secure (IP68, cable-clamped), an attacker could potentially route additional cables through unused gland knockouts to establish covert network connections.

---

*Document version: 1.0 | Last updated: 2026-03-25*
