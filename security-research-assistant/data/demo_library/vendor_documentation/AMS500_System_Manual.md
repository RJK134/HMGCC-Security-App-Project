# AMS-500 Additive Manufacturing System -- System Manual

**Document Number:** AMS-500-MAN-001  
**Revision:** C  
**Date:** 2025-09-15  
**Classification:** COMMERCIAL IN CONFIDENCE  
**Manufacturer:** Meridian Advanced Manufacturing Systems Ltd.  
**Address:** Unit 14, Harwell Science & Innovation Campus, Didcot, Oxfordshire, OX11 0QX, United Kingdom

---

> **IMPORTANT SAFETY NOTICE:** This system contains a Class 4 laser source (IEC 60825-1:2014). Exposure to direct or scattered radiation can cause severe eye injury and skin burns. Only trained and authorised personnel shall operate, maintain, or service this equipment. Read this manual in its entirety before powering on the system.

---

## Table of Contents

1. [Introduction and Intended Use](#1-introduction-and-intended-use)
2. [System Overview](#2-system-overview)
3. [Technical Specifications](#3-technical-specifications)
4. [Major Subsystems](#4-major-subsystems)
5. [Control Architecture](#5-control-architecture)
6. [Communication Interfaces](#6-communication-interfaces)
7. [Safety Systems](#7-safety-systems)
8. [Installation Requirements](#8-installation-requirements)
9. [Operating Procedures](#9-operating-procedures)
10. [Maintenance Schedule](#10-maintenance-schedule)
11. [Troubleshooting](#11-troubleshooting)
12. [Spare Parts and Consumables](#12-spare-parts-and-consumables)
13. [Regulatory Compliance](#13-regulatory-compliance)

---

## 1. Introduction and Intended Use

The AMS-500 is a production-grade laser powder bed fusion (L-PBF) additive manufacturing system designed for high-density metal component fabrication. The system is intended for use in controlled industrial and research environments where dimensional accuracy, metallurgical integrity, and process repeatability are critical requirements.

The AMS-500 is designed to process reactive and non-reactive metal powders including, but not limited to: Ti-6Al-4V (Grade 5 titanium), Inconel 718, 316L stainless steel, AlSi10Mg, CoCrMo, Maraging Steel (MS1), and pure copper (Cu). Processing of reactive powders requires strict inert atmosphere control as described in Section 4.5.

**Intended operating environment:** Indoor installation in a climate-controlled facility with ambient temperature 18-28 degrees C, relative humidity 20-60% (non-condensing), and adequate ventilation per EN 626-1. The system is not rated for outdoor use, explosive atmospheres, or environments subject to significant vibration (>0.5g RMS).

### 1.1 Document Scope

This manual covers installation, commissioning, operation, and routine maintenance of the AMS-500 system. For advanced service procedures including laser alignment, optical train replacement, and control system firmware updates, refer to the AMS-500 Service Manual (AMS-500-SVC-001), available only to Meridian-certified service engineers.

### 1.2 Revision History

| Rev | Date       | Description                                      | Author      |
|-----|------------|--------------------------------------------------|-------------|
| A   | 2024-03-01 | Initial release                                  | D. Hargreaves |
| B   | 2024-11-20 | Updated for firmware V2.4, added Cu powder params | P. Novak    |
| C   | 2025-09-15 | Updated network configuration, added OPC-UA info | P. Novak    |

---

## 2. System Overview

The AMS-500 is an integrated metal additive manufacturing platform comprising a sealed build chamber, single-mode ytterbium fibre laser, galvanometric scanning system, automated powder handling, gas management, and a fully integrated control system.

### 2.1 System Architecture (Functional Block Diagram)

```
+--------------------------------------------------------------------+
|                        AMS-500 System                              |
|                                                                    |
|  +-------------------+    +------------------+    +--------------+ |
|  | Laser Assembly    |    | Build Chamber    |    | Powder       | |
|  | - Yb-fibre source |    | - Build platform |    | Handling     | |
|  | - Beam delivery   |--->| - Recoater       |<---| - Feed       | |
|  | - Galvo scanner   |    | - Gas flow       |    | - Overflow   | |
|  | - F-theta lens    |    | - Viewport       |    | - Sieve      | |
|  +--------+----------+    +--------+---------+    +------+-------+ |
|           |                        |                     |         |
|  +--------v------------------------v---------------------v-------+ |
|  |              Control System (PLC + HMI + Motion)              | |
|  |  Siemens S7-1500 CPU 1515SP PC2 | Allen-Bradley PanelView    | |
|  |  Beckhoff EtherCAT motion        | OPC-UA / Modbus TCP        | |
|  +-------------------------------------------------------------------+
|                                                                    |
|  +-------------------+    +------------------+    +--------------+ |
|  | Gas Management    |    | Thermal Mgmt     |    | Electrical   | |
|  | - Argon/N2 supply |    | - Build plate    |    | - Main power | |
|  | - O2 sensor       |    |   pre-heat       |    | - UPS        | |
|  | - Recirculation   |    | - Chiller loop   |    | - E-stop     | |
|  | - Filtration       |    | - Ambient sensors|    | - Interlocks | |
|  +-------------------+    +------------------+    +--------------+ |
+--------------------------------------------------------------------+
```

### 2.2 Physical Dimensions and Weight

| Parameter                 | Value                        |
|---------------------------|------------------------------|
| Overall dimensions (WxDxH)| 2400 x 1800 x 2200 mm       |
| Weight (without powder)   | 3200 kg                      |
| Weight (with full powder) | 3800 kg (approx.)            |
| Floor loading requirement | Minimum 5 kN/m^2             |
| Shipping dimensions       | 2600 x 2000 x 2400 mm (crated) |

---

## 3. Technical Specifications

### 3.1 Build Parameters

| Parameter                      | Specification                          |
|--------------------------------|----------------------------------------|
| Build volume (X x Y x Z)      | 500 x 500 x 500 mm                    |
| Layer thickness range          | 20 - 100 um (material dependent)       |
| Typical build rate             | 20 - 50 cm^3/hr (material dependent)  |
| Minimum feature size           | 150 um (XY), 1 layer (Z)              |
| Surface roughness (as-built)   | Ra 6 - 12 um (top surface)            |
| Dimensional accuracy           | +/- 50 um per 100 mm (typical)        |
| Maximum part density           | >99.95% (optimised parameters)        |
| Scan strategy                  | Stripe, checkerboard, contour/hatch   |
| Build plate material           | Tool steel (1.2344), 540 x 540 x 40 mm |

### 3.2 Laser System

| Parameter                      | Specification                          |
|--------------------------------|----------------------------------------|
| Laser type                     | Single-mode Yb-fibre (CW)             |
| Laser manufacturer             | IPG Photonics YLR-1000-WC-Y14         |
| Maximum output power           | 1000 W (1 kW)                          |
| Wavelength                     | 1070 +/- 10 nm                         |
| Beam quality (M^2)             | < 1.1                                  |
| Spot size at focus              | 80 um (1/e^2)                          |
| Variable spot size range       | 80 - 200 um (defocus adjustable)       |
| Maximum scan speed             | 7000 mm/s                              |
| Scan field                     | 530 x 530 mm (overshoot margin)        |
| Galvanometer scanner           | Scanlab intelliSCAN 30 (2x axis)      |
| F-theta lens                   | Sill Optics S4LFT4525/328, f=420 mm   |
| Beam delivery fibre            | 10 m armoured process fibre, QBH connector |
| Laser classification           | Class 4 (IEC 60825-1:2014)            |

### 3.3 Powder Handling

| Parameter                      | Specification                          |
|--------------------------------|----------------------------------------|
| Feed hopper capacity           | 80 litres (approx. 180 kg for Ti64)   |
| Overflow hopper capacity       | 40 litres                              |
| Recoater type                  | Rubber blade (silicone) or ceramic blade |
| Recoater speed                 | 50 - 250 mm/s (adjustable)            |
| Powder sieve                   | Ultrasonic, 63 um mesh (standard)      |
| Powder recirculation           | Automatic closed-loop via sieve        |
| Powder compatible size range   | 15 - 63 um (D10-D90)                  |

### 3.4 Atmosphere Control

| Parameter                      | Specification                          |
|--------------------------------|----------------------------------------|
| Inert gas                      | Argon (Grade 4.8 min.) or Nitrogen     |
| O2 level (operating)           | < 500 ppm (typ. < 100 ppm achieved)   |
| O2 level (alarm threshold)     | 1000 ppm (configurable)                |
| O2 level (auto-shutdown)       | 2000 ppm                               |
| Chamber pressure (operating)   | +10 to +25 mbar above ambient          |
| Gas flow rate (recirculation)  | 2.5 m^3/min                            |
| Gas filtration                 | 2-stage: HEPA H13 + activated carbon   |
| Inerting time (from air)       | < 45 minutes to < 500 ppm O2           |
| O2 sensor type                 | Zirconia electrochemical (SST Sensing LOX-02-S) |

### 3.5 Thermal Management

| Parameter                      | Specification                          |
|--------------------------------|----------------------------------------|
| Build plate pre-heat           | Up to 300 degrees C (resistive heater) |
| Pre-heat PID control accuracy  | +/- 3 degrees C at setpoint            |
| Chiller unit                   | SMC HRS060-WN-20 (6 kW cooling)       |
| Coolant                        | 50/50 ethylene glycol/deionised water  |
| Coolant flow rate              | 15 L/min                               |
| Coolant temperature            | 20 +/- 1 degrees C (setpoint)         |
| Laser head cooling             | Dedicated loop, 22 degrees C setpoint  |

### 3.6 Electrical

| Parameter                      | Specification                          |
|--------------------------------|----------------------------------------|
| Main supply                    | 400 VAC 3-phase + N + PE, 50 Hz       |
| Main supply current            | 32 A per phase (max)                  |
| Total power consumption        | 12 kW typical, 18 kW peak             |
| Control voltage                | 24 VDC (internal, from QUINT PSU)     |
| UPS                            | APC Smart-UPS SRT 3000VA (for control) |
| Main circuit breaker           | Schneider NSXm 40A, 4P, 36kA          |

---

## 4. Major Subsystems

### 4.1 Laser Assembly

The laser source is an IPG Photonics YLR-1000-WC-Y14 single-mode continuous-wave ytterbium fibre laser. The laser is housed in a dedicated enclosure mounted on the rear of the machine frame and delivers the beam via a 10-metre armoured process fibre (QBH connector) to the scan head mounted atop the build chamber.

**Galvanometric Scanner:** The Scanlab intelliSCAN 30 dual-axis galvo scanner provides high-speed beam positioning across the 530 x 530 mm scan field. The scanner operates in closed-loop position control mode with a position resolution of 1 urad and a maximum angular velocity of 20 rad/s per axis. The galvo mirrors are silicon carbide (SiC) with gold coating optimised for 1070 nm.

**F-theta Lens:** The telecentric f-theta lens (Sill Optics S4LFT4525/328, focal length 420 mm) ensures consistent spot size and perpendicular beam incidence across the entire build field. The lens is mounted in a sealed nitrogen-purged housing to prevent contamination.

**Beam Path Monitoring:** A photodiode-based back-reflection monitor is integrated into the beam delivery to detect anomalous reflections during processing. A back-reflection level exceeding 5% of incident power triggers an automatic laser shutdown (error code E-LAS-012).

> **WARNING:** The laser output at 1070 nm is invisible to the naked eye. Never attempt to view the beam path directly or with optical instruments. Always verify interlock status before opening any access panel on the optical train.

### 4.2 Build Chamber

The build chamber is a fully sealed, gas-tight enclosure fabricated from 304L stainless steel with a usable volume of approximately 600 x 600 x 700 mm (internal). The top of the chamber incorporates a laser-grade fused silica window (100 mm diameter, AR-coated for 1070 nm) through which the laser beam enters.

**Build Platform:** The build platform is a precision Z-axis stage driven by a ball screw actuator (THK BNK2020-3.6G0+620LC5) through a Beckhoff servo axis. The platform positions with a repeatability of +/- 5 um and a minimum step of 1 um. The platform heater is a 3 kW resistive element (Watlow FIREROD J8A-15150) embedded in the platform body.

**Recoater:** The recoater arm traverses the X-axis on linear guide rails and is driven by a Beckhoff linear servo motor. Blade pressure is adjustable via a pneumatic cylinder with proportional valve control. Blade contact detection is provided by a strain gauge sensor that triggers recoater retraction if excessive force (>15 N) is detected, indicating a collision with a raised feature.

**Viewport:** A 200 x 150 mm observation window (multi-layer laminated glass with OD7+ filter for 1070 nm) is provided on the front panel for visual inspection of the build process. The viewport includes an automated shutter that closes during laser operation unless the operator explicitly enables viewing mode.

### 4.3 Powder Handling System

The powder handling system is a closed-loop design that minimises operator exposure to metal powder. Powder flows from the feed hopper to the build chamber via a gravity-fed channel, is spread by the recoater, and excess powder falls into the overflow hopper. The overflow hopper is connected to an ultrasonic sieve (Russell Finex Finex Separator) that separates acceptable powder (< 63 um) and returns it to the feed hopper.

**Powder Level Sensing:** Capacitive level sensors (IFM Electronic KQ5100) in both hoppers provide continuous level monitoring. Low powder level in the feed hopper triggers a warning at 20% capacity and pauses the build at 10%.

**Inert Powder Handling:** All powder transfer paths are enclosed and purged with inert gas. The sieve unit operates under argon/nitrogen atmosphere. Powder loading and unloading is performed through a glove box antechamber with double interlock doors.

> **CAUTION:** Metal powders, particularly titanium and aluminium alloys, are combustible and present an explosion hazard when dispersed in air. Follow all applicable regulations (ATEX Directive 2014/34/EU) for powder handling, storage, and disposal. Always use ESD-safe equipment and ground all powder-handling components.

### 4.4 Gas Management System

The gas management system maintains an inert atmosphere within the build chamber throughout the manufacturing process. It comprises:

1. **Gas Supply Interface:** Quarter-turn isolation valve, pressure regulator (set to 4 bar), and check valve for connection to bulk argon or nitrogen supply. Inlet connection: 12 mm Swagelok compression fitting.

2. **Gas Purge Controller:** Automated purge sequence controlled by PLC. Evacuates chamber atmosphere via a vacuum pump (Busch R5 RA 0025 F, 25 m^3/hr) to -500 mbar, then backfills with inert gas. Repeated 3x to achieve < 500 ppm O2.

3. **Recirculation Loop:** A high-flow blower (EBM-Papst R3G310-AN43-71) circulates gas across the build surface at 2.5 m^3/min. The laminar flow pattern removes spatter and condensate from the laser interaction zone. Flow velocity at the build surface is approximately 2-3 m/s.

4. **Filtration:** Two-stage filtration consisting of a primary HEPA H13 filter (99.95% at 0.3 um) for particulate removal and a secondary activated carbon filter for volatile organic compound (VOC) absorption.

5. **Oxygen Monitoring:** A zirconia-type oxygen sensor (SST Sensing LOX-02-S, range 0-25% O2, accuracy +/- 0.01% at low ppm levels) provides continuous O2 measurement. The sensor signal is read by an analogue input module (Siemens 6ES7 531-7KF00-0AB0, 4-20 mA input) and processed by the PLC safety programme.

### 4.5 Thermal Management System

Thermal control is critical for build quality and includes three independent loops:

**Loop 1 -- Build Plate Heating:** A PID-controlled resistive heater maintains the build plate at a user-defined setpoint (ambient to 300 degrees C). Temperature is measured by a Type K thermocouple (Omega KQXL-18G-12) embedded in the build plate, read via a thermocouple module (Siemens 6ES7 531-7NF10-0AB0). The PID loop runs at 100 ms cycle time in the PLC.

**Loop 2 -- Laser Head Cooling:** A dedicated chiller loop maintains the galvo scanner and f-theta lens assembly at 22 +/- 1 degrees C. An inline flow switch (IFM Electronic SI5010) verifies coolant flow; loss of flow triggers immediate laser shutdown.

**Loop 3 -- Process Chiller:** The main process chiller (SMC HRS060-WN-20) provides cooling to the laser source, beam delivery fibre, and auxiliary heat exchangers. Coolant temperature and flow are monitored by the PLC.

---

## 5. Control Architecture

### 5.1 Primary Controller

The primary controller is a Siemens SIMATIC S7-1500 CPU 1515SP PC2 (order number 6ES7 677-2AA41-0FL0). This is a combined PLC and industrial PC platform featuring:

- Processor: Intel Celeron 3965U, dual-core, 2.2 GHz
- RAM: 2 GB DDR4
- PLC work memory: 100 MB (for user programme)
- Operating system: SIMATIC IPC runtime (Windows 10 IoT Enterprise LTSC 2021)
- Runtime: SIMATIC S7-1500 Software Controller V21.9
- Programming: TIA Portal V17 (Update 6 or later)

The PLC programme is structured in accordance with IEC 61131-3 and comprises:

- **OB1 (Main):** Cyclic programme, 10 ms cycle time
- **OB35 (Cyclic Interrupt):** Fast cyclic tasks (motion interpolation), 2 ms cycle time
- **OB82 (Diagnostic Interrupt):** Hardware fault handling
- **OB121/122 (Programme Errors):** Exception handling
- **Safety Programme (F-OB):** Runs in F-runtime on the integrated fail-safe CPU, 50 ms cycle time. Manages E-stop, door interlocks, laser safety, O2 monitoring, and pressure relief.

**I/O Configuration:**

| Module                       | Order Number            | Slot | Function                        |
|------------------------------|------------------------|------|---------------------------------|
| CPU 1515SP PC2               | 6ES7 677-2AA41-0FL0    | 0    | Main controller                 |
| DI 16x24VDC HF               | 6ES7 521-1BH50-0AA0    | 1    | Digital inputs (interlocks)     |
| DI 8x24VDC F                 | 6ES7 526-1BH00-0AB0    | 2    | Safety digital inputs           |
| DQ 16x24VDC/0.5A HF          | 6ES7 522-1BH50-0AA0    | 3    | Digital outputs (valves, relays)|
| DQ 4x24VDC/2A F              | 6ES7 526-2BF00-0AB0    | 4    | Safety digital outputs          |
| AI 8xU/I/RTD/TC ST           | 6ES7 531-7NF10-0AB0    | 5    | Thermocouple inputs             |
| AI 4xU/I ST                  | 6ES7 531-7KF00-0AB0    | 6    | Analogue inputs (O2, pressure)  |
| AQ 4xU/I ST                  | 6ES7 532-5HD00-0AB0    | 7    | Analogue outputs (proportional valves) |
| CM PtP RS422/485 HF          | 6ES7 541-1AD00-0AB0    | 8    | Serial comms (laser RS-232 via adapter) |

### 5.2 Human-Machine Interface

The operator interface is a Rockwell Automation / Allen-Bradley PanelView Plus 7 Performance terminal:

- Model: 2711P-T15C22D9P (15-inch colour TFT touchscreen)
- Resolution: 1024 x 768 pixels
- Processor: Intel Atom E3845 quad-core, 1.91 GHz
- Memory: 4 GB RAM, 32 GB SSD
- Operating system: Windows 10 IoT Enterprise
- Runtime: FactoryTalk View SE (Station) V13.00
- Communication to PLC: OPC-UA client (connects to S7-1500 OPC-UA server)

The HMI application provides:

- Real-time process visualisation (laser power, scan position, O2 level, temperatures, pressures)
- Recipe management (build parameters, material profiles)
- Build job management (queue, start, pause, resume, abort)
- Alarm display and acknowledgement (ISA 18.2 compliant)
- Trend recording (up to 90 days on local SSD)
- User authentication (4-tier: Operator, Technician, Engineer, Administrator)

### 5.3 Motion Control

All motion axes are controlled via Beckhoff EtherCAT servo drives:

| Axis       | Function                | Drive                  | Motor                    | Encoder            |
|------------|-------------------------|------------------------|--------------------------|--------------------|
| Z (Build)  | Build platform vertical | AX5206-0000 (2-ch)    | AM8042-1F20 (4 Nm)      | Absolute (BiSS-C)  |
| X (Recoat) | Recoater traverse       | AX5206-0000 (2-ch)    | AL2815-0000 (linear)     | Integrated linear   |
| Y (Feed)   | Powder feed piston      | AX5203-0000            | AM8032-1J20 (1.34 Nm)   | Absolute (BiSS-C)  |
| R (Sieve)  | Sieve rotation          | AX5103-0000            | AM8021-1C20 (0.5 Nm)    | Incremental (1024)  |

The EtherCAT master is a Beckhoff EK1100 EtherCAT coupler connected to the S7-1500 controller via the PROFINET/EtherCAT gateway module (Beckhoff EL6692). EtherCAT cycle time is configured at 1 ms with distributed clock synchronisation. Motion interpolation and path planning run in the PLC OB35 (2 ms cycle).

The galvanometer scanner (Scanlab intelliSCAN 30) is controlled via a dedicated RTC6 Ethernet scanner control board (Scanlab), which receives vector data from the PLC via a TCP/IP socket interface on port 50000. The RTC6 operates independently during laser marking sequences, synchronising with the PLC via digital I/O handshake signals.

---

## 6. Communication Interfaces

### 6.1 Network Architecture Overview

The AMS-500 employs a segmented network architecture with three distinct VLANs:

| VLAN | Subnet          | Purpose           | Switch Port Group |
|------|------------------|--------------------|-------------------|
| 10   | 192.168.1.0/24  | Control network    | Ports 1-4         |
| 20   | 192.168.2.0/24  | Motion network     | Ports 5-6         |
| 30   | 192.168.10.0/24 | Management network | Ports 7-8         |

Network switching is provided by a Hirschmann RS20-0800T1T1SDAEHC managed switch. See the AMS-500 Network Configuration Guide (AMS-500-NET-001) for detailed configuration.

### 6.2 OPC-UA Server

The S7-1500 CPU runs an integrated OPC-UA server (Part 4 of IEC 62541) on TCP port 4840. The server exposes the following namespaces:

- **Namespace 0:** OPC-UA standard types
- **Namespace 1:** Siemens S7 device information
- **Namespace 3 (urn:meridian:ams500):** AMS-500 process data, including:
  - Build status (idle / inerting / building / cooling / complete / error)
  - Current layer number, total layers, estimated completion time
  - Laser power (actual and setpoint)
  - O2 concentration (ppm)
  - Build plate temperature (degrees C)
  - Chamber pressure (mbar)
  - Alarm and event information

**Authentication:** The OPC-UA server supports Anonymous access (disabled by default), Username/Password authentication, and X.509 certificate-based authentication. The default configuration uses Username/Password with the following factory-set accounts:

| Username       | Default Password | Access Level |
|----------------|-----------------|--------------|
| opc_operator   | Ams500!opc      | Read-only    |
| opc_engineer   | Ams500!eng      | Read/Write   |

> **SECURITY NOTE:** Change all default passwords before commissioning. Configure X.509 certificate-based authentication for production use. See the Network Configuration Guide for certificate management procedures.

**Security Policy:** The server supports the following OPC-UA security policies:
- None (disabled in default configuration)
- Basic256Sha256 (SignAndEncrypt) -- **recommended**
- Aes128_Sha256_RsaOaep (SignAndEncrypt)

### 6.3 Modbus TCP

A Modbus TCP server runs on the S7-1500 via the integrated Modbus TCP communication function block (MB_SERVER, FB 8603). The server listens on TCP port 502 and provides access to a subset of process data for integration with third-party SCADA or historian systems.

**Register Map (Holding Registers, FC 03/06/16):**

| Address    | Data Type | Description                    | Unit     | R/W |
|------------|-----------|--------------------------------|----------|-----|
| 40001      | UINT16    | System status word             | Bitmap   | R   |
| 40002      | UINT16    | Current layer number           | --       | R   |
| 40003-40004| UINT32    | Total layer count              | --       | R   |
| 40005-40006| FLOAT32   | Laser power setpoint           | W        | R/W |
| 40007-40008| FLOAT32   | Laser power actual             | W        | R   |
| 40009-40010| FLOAT32   | O2 concentration               | ppm      | R   |
| 40011-40012| FLOAT32   | Build plate temperature        | deg C    | R   |
| 40013-40014| FLOAT32   | Chamber pressure               | mbar     | R   |
| 40015-40016| FLOAT32   | Build plate temp setpoint      | deg C    | R/W |
| 40017      | UINT16    | Alarm count (active)           | --       | R   |
| 40018      | UINT16    | Build progress (%)             | %        | R   |

**Coils (FC 01/05):**

| Address | Description              | R/W |
|---------|--------------------------|-----|
| 00001   | Build start command      | R/W |
| 00002   | Build pause command      | R/W |
| 00003   | Build abort command      | R/W |
| 00004   | Gas purge start          | R/W |
| 00005   | Laser enable             | R/W |

> **WARNING:** Write access to Modbus registers enables remote control of safety-critical parameters (laser power, build plate temperature). Ensure Modbus TCP access is restricted to authorised systems via network segmentation and firewall rules. Meridian strongly recommends disabling Modbus TCP if not required for integration.

### 6.4 PROFINET

The S7-1500 controller communicates with its local I/O modules and the EtherCAT gateway via PROFINET IO. PROFINET operates on VLAN 10 (192.168.1.0/24) using the following device addresses:

| Device                       | IP Address     | Device Name      | PROFINET Role |
|------------------------------|---------------|------------------|---------------|
| CPU 1515SP PC2               | 192.168.1.1   | ams500-plc       | IO Controller |
| Beckhoff EK1100 (EtherCAT)  | 192.168.1.10  | ams500-ethercat  | IO Device     |
| Siemens I/O (local backplane)| --            | (internal)       | Integrated    |

PROFINET send clock: 1 ms. Reduction ratio: 1 (every cycle). Watchdog: 50 ms.

### 6.5 EtherCAT

EtherCAT operates on a dedicated physical segment (VLAN 20, 192.168.2.0/24 -- note: EtherCAT itself is a Layer 2 protocol and does not use IP addressing; the VLAN is for physical isolation only). The EtherCAT topology is:

```
EK1100 (Coupler) --> AX5206 (Z + X axes) --> AX5206 (Y axis) --> AX5103 (R axis) --> EL1008 (DI) --> EL2008 (DQ) --> EL3064 (AI)
```

Distributed Clock reference: EK1100 (first device). Cycle time: 1 ms. Jitter: < 1 us.

### 6.6 Additional Interfaces

| Interface      | Protocol           | Port/Connection      | Purpose                         |
|----------------|--------------------|----------------------|---------------------------------|
| HMI to PLC     | OPC-UA client      | TCP 4840             | Process data exchange           |
| Laser serial   | RS-232 (via CM PtP)| 19200 baud, 8N1      | Laser power control and status  |
| Scanner control| TCP/IP socket      | TCP 50000            | RTC6 vector data                |
| Chiller        | Modbus RTU         | RS-485, 9600 baud    | Temperature setpoint and status |
| O2 analyser    | 4-20 mA analogue   | AI slot 6, ch 0      | Oxygen concentration            |
| Web server     | HTTPS              | TCP 443              | S7-1500 built-in web server     |
| SNMP           | SNMP v2c           | UDP 161              | Network switch monitoring       |

---

## 7. Safety Systems

### 7.1 Safety Architecture

The AMS-500 safety system is implemented as an F-programme (failsafe) on the S7-1500 CPU 1515SP PC2, using Siemens Safety Integrated functionality (SIL 2 rated per IEC 62061). Safety-rated I/O modules (F-DI and F-DQ) process all safety-relevant signals.

### 7.2 Emergency Stop (E-Stop)

Three E-stop pushbuttons are provided:

1. **Front panel** (operator position) -- Schneider Electric XB5AS8442, 40mm mushroom head, twist-to-release
2. **Rear panel** (service position) -- Schneider Electric XB5AS8442
3. **Remote pendant** (optional) -- cable length up to 10 m

E-stop activation triggers:
- Immediate laser shutdown (< 1 ms, via hardwired interlock to laser enable)
- Servo drives disable (STO - Safe Torque Off, SIL 3)
- Build plate heater off
- Gas recirculation blower off
- Safety relay de-energises, latching fault state
- Alarm "E-STOP ACTIVATED" (Alarm ID 9001, Priority: Critical)

Reset requires: E-stop button release, acknowledgement on HMI, and key switch in "Reset" position.

### 7.3 Laser Safety Interlocks

The laser can only fire when ALL of the following conditions are met:

1. E-stop circuit healthy (closed)
2. Build chamber door closed and locked (Schmersal AZM 161-B1 safety switch, magnetically coded)
3. Laser safety shutter closed between laser source and process fibre (verified by position switch)
4. Viewport shutter in correct position (closed or filtered viewing mode)
5. O2 concentration < 1000 ppm
6. Coolant flow confirmed (flow switch inputs)
7. Laser enable command from PLC safety programme
8. RTC6 scanner board interlock input active

Failure of any interlock condition triggers immediate laser shutdown and alarm generation.

### 7.4 Oxygen Monitoring

| Condition          | O2 Level  | Action                                                |
|--------------------|-----------|-------------------------------------------------------|
| Normal operation   | < 500 ppm | Green indicator on HMI                                |
| Warning            | 500-999 ppm| Amber warning on HMI, event logged                   |
| Alarm              | 1000-1999 ppm| Red alarm, laser inhibited, build paused            |
| Critical shutdown  | >= 2000 ppm| Laser off, gas supply isolated, build aborted        |

### 7.5 Pressure Relief

The build chamber is equipped with a mechanical pressure relief valve (Swagelok SS-4R3A, cracking pressure +50 mbar) and a burst disc (Fike HOV-2.0, 100 mbar) as a secondary protection against overpressure. Chamber pressure is monitored by a pressure transmitter (Endress+Hauser Cerabar PMC21, 4-20 mA, range -1 to +1 bar) connected to the PLC analogue input.

Overpressure alarm: +35 mbar. Overpressure shutdown: +45 mbar (gas supply isolated, blower stopped).

### 7.6 Fire Suppression

An FM-200 (HFC-227ea) clean agent fire suppression system protects the laser enclosure and control cabinet. The system is triggered by a linear heat detection cable (Protectowire) at 68 degrees C. Manual release is available via a pull station adjacent to the main power disconnect.

---

## 8. Installation Requirements

### 8.1 Site Preparation

- **Floor:** Level to within 5 mm per metre. Minimum load capacity 5 kN/m^2. Anti-vibration mounts provided.
- **Clearance:** Minimum 1000 mm on all sides for maintenance access. 2000 mm at rear for laser fibre routing.
- **Ventilation:** Extract ventilation rated for 500 m^3/hr minimum. Metal powder extraction must comply with ATEX Zone 22 requirements.
- **Electrical:** 400 VAC 3-phase supply, 32A, TN-S earthing system. Dedicated circuit recommended.
- **Gas Supply:** Bulk argon (or nitrogen) supply with minimum delivery pressure of 6 bar and flow capacity of 50 Nm^3/hr during inerting.
- **Compressed Air:** 6 bar clean dry air, ISO 8573-1 Class 1.4.1, for pneumatic actuators. Consumption: 50 NL/min peak.

### 8.2 Environmental Requirements

| Parameter           | Operating Range          | Storage Range           |
|---------------------|--------------------------|-------------------------|
| Temperature         | 18 - 28 degrees C        | -10 - 50 degrees C      |
| Relative humidity   | 20 - 60% (non-condensing)| 10 - 90% (non-condensing)|
| Altitude            | Up to 2000 m             | Up to 5000 m            |
| Vibration           | < 0.5 g RMS (10-500 Hz) | < 1.0 g RMS             |

---

## 9. Operating Procedures

### 9.1 Pre-Build Checklist

1. Verify build plate is clean, flat, and securely clamped to the platform.
2. Verify powder hopper level is adequate for the build (check estimated powder consumption in build preparation software).
3. Verify gas supply pressure (>= 4 bar at regulator).
4. Close and lock the build chamber door.
5. Initiate gas purge sequence from HMI (Purge screen > Start Purge). Wait for O2 < 500 ppm.
6. Set build plate temperature setpoint if required. Wait for temperature stabilisation (+/- 3 degrees C).
7. Load build file (.ams500 format) to the HMI via USB or network transfer.
8. Verify build parameters in Recipe Review screen (laser power, scan speed, layer thickness, hatch spacing).
9. Perform recoater test run (Diagnostics > Recoater Test) to verify smooth blade travel.
10. Enable laser via key switch on operator panel.

### 9.2 Build Execution

1. Press "Start Build" on the HMI.
2. The system will execute: lower platform by one layer thickness, deposit powder via recoater, expose layer with laser, repeat.
3. Monitor the build via the HMI process screen. Key parameters: laser power stability, O2 level, build plate temperature, recoater force.
4. The system automatically pauses on any alarm condition. Review the alarm, resolve the root cause, and press "Resume" on the HMI.
5. Build completion is indicated by "Build Complete" status on the HMI.

### 9.3 Post-Build Procedure

1. Allow the build chamber to cool for a minimum of 2 hours (or until build plate temperature < 50 degrees C).
2. Do NOT open the chamber door until O2 level has returned to safe levels after gas supply is stopped (> 19.5% O2 in ambient check).
3. Remove excess powder using the integrated vacuum system (glove box side).
4. Remove the build plate with printed parts using the build plate extraction tool.
5. Transfer to post-processing (stress relief heat treatment, support removal, machining as required).

---

## 10. Maintenance Schedule

### 10.1 Daily (Every Build or Every 24 Hours of Operation)

- Inspect and clean the build chamber viewport (isopropyl alcohol, lint-free cloth)
- Verify O2 sensor reading against calibration gas (100 ppm span check)
- Empty overflow hopper if more than 50% full
- Check coolant level in chiller reservoir
- Inspect recoater blade for damage or powder adhesion

### 10.2 Weekly (Every 100 Hours of Operation)

- Clean the laser window (top of build chamber) using approved lens cleaning procedure
- Inspect gas filtration differential pressure gauges (replace filters if dP > 25 mbar)
- Run PLC diagnostic check via web server (https://192.168.1.1/diagnostics)
- Backup PLC programme and HMI project to USB
- Inspect all safety interlocks (door switch, E-stop, key switch)
- Lubricate build platform Z-axis ball screw (Klüber ISOFLEX NBU 15, 2 pumps via grease nipple)

### 10.3 Monthly (Every 500 Hours of Operation)

- Full O2 sensor calibration (zero gas: 100% N2, span gas: 100 ppm O2 in N2)
- Laser power calibration check (using Ophir power meter on internal port)
- EtherCAT network diagnostics (check for CRC errors, lost frames)
- PROFINET network diagnostics (check for discarded frames, retransmissions)
- Inspect and clean gas recirculation blower impeller
- Replace HEPA filter (or based on differential pressure)
- Inspect all cable connections and terminal blocks for tightness

### 10.4 Annual (Or Every 2000 Hours of Operation)

- Full laser alignment verification (service engineer only)
- F-theta lens inspection and cleaning (service engineer only)
- Safety system validation (full functional test of all interlocks per IEC 62061)
- Galvo scanner calibration (using Scanlab calibration target)
- Replace coolant in all chiller loops
- Replace UPS battery (APC RBC replacement cartridge #APCRBC152)
- Firmware review and update (PLC, HMI, drives -- coordinate with Meridian support)

---

## 11. Troubleshooting

### 11.1 Common Alarms

| Alarm ID | Description                    | Probable Cause                        | Action                                 |
|----------|-------------------------------|---------------------------------------|----------------------------------------|
| E-LAS-001| Laser source fault            | Internal laser error                  | Check laser status via serial console  |
| E-LAS-012| Back-reflection detected      | Reflective powder surface             | Reduce laser power, check material     |
| E-GAS-001| O2 level high (>1000 ppm)    | Chamber leak, seal degradation        | Check door seal, gas line connections  |
| E-GAS-002| Chamber pressure high (>35 mbar)| Blocked exhaust, valve fault        | Check exhaust path, relieve pressure   |
| E-MOT-001| Z-axis following error        | Mechanical binding, overload          | Check platform for obstructions        |
| E-MOT-002| Recoater collision detected   | Raised feature in build               | Inspect build, adjust recoater height  |
| E-THR-001| Build plate over-temperature  | Heater control fault                  | Check thermocouple, PID parameters     |
| E-THR-002| Coolant flow loss             | Pump failure, blockage                | Check chiller, inspect flow switch     |
| E-NET-001| EtherCAT bus error            | Cable fault, device failure           | Check cables, run diagnostics          |
| E-SAF-001| E-Stop activated              | Operator-initiated                    | Release E-stop, acknowledge on HMI     |
| E-SAF-002| Door interlock open           | Door opened during operation          | Close and lock door, reset safety      |

### 11.2 Network Diagnostics

If communication issues occur between the PLC, HMI, or external systems:

1. Check physical connections and link LEDs on the Hirschmann RS20 switch.
2. Verify IP address configuration (see Network Configuration Guide).
3. Check VLAN configuration -- control devices must be on VLAN 10.
4. For OPC-UA issues, verify certificate validity and security policy settings.
5. For Modbus TCP issues, verify Unit ID (default: 1) and register addressing (0-based vs 1-based offset).
6. Use the S7-1500 web server diagnostic pages: https://192.168.1.1 (login required).

---

## 12. Spare Parts and Consumables

### 12.1 Recommended Spare Parts

| Part Number           | Description                           | Qty | Lead Time |
|-----------------------|---------------------------------------|-----|-----------|
| AMS-REC-BLD-001       | Recoater blade, silicone, 560 mm     | 5   | Stock     |
| AMS-REC-BLD-002       | Recoater blade, ceramic, 560 mm      | 2   | 4 weeks   |
| AMS-OPT-WIN-001       | Laser window, fused silica, AR 1070nm| 2   | 6 weeks   |
| AMS-FIL-HEPA-001      | HEPA H13 filter cartridge            | 4   | Stock     |
| AMS-FIL-CARB-001      | Activated carbon filter cartridge    | 4   | Stock     |
| SST LOX-02-S          | O2 sensor (zirconia cell)            | 1   | 2 weeks   |
| 6ES7 531-7KF00-0AB0   | Siemens AI module (spare)            | 1   | 4 weeks   |
| APC APCRBC152         | UPS replacement battery              | 1   | Stock     |

### 12.2 Consumables

| Item                        | Specification                  | Consumption Rate             |
|-----------------------------|--------------------------------|------------------------------|
| Argon gas                   | Grade 4.8 (99.998% purity)    | ~50 Nm^3 per build (typical) |
| Metal powder (Ti-6Al-4V)    | 15-45 um, ASTM F2924          | Build-dependent              |
| Recoater blade              | Silicone or ceramic            | Replace every 100-500 hours  |
| Laser window                | AR-coated fused silica         | Replace every 500-1000 hours |
| HEPA filter                 | H13 grade                      | Replace every 500 hours      |
| Coolant (ethylene glycol)   | 50% concentration              | Replace annually             |

---

## 13. Regulatory Compliance

The AMS-500 has been designed and tested in accordance with the following standards and directives:

| Standard / Directive                  | Description                                    |
|---------------------------------------|------------------------------------------------|
| EU Machinery Directive 2006/42/EC     | Essential health and safety requirements       |
| EU EMC Directive 2014/30/EU          | Electromagnetic compatibility                  |
| EU Low Voltage Directive 2014/35/EU  | Electrical safety                              |
| IEC 60825-1:2014                      | Safety of laser products (Class 4)             |
| IEC 62061:2021                        | Safety of machinery -- functional safety (SIL) |
| EN ISO 12100:2010                     | Safety of machinery -- risk assessment         |
| EN 626-1:1994                         | Safety of machinery -- reduction of health risks |
| ATEX Directive 2014/34/EU            | Equipment for explosive atmospheres            |
| EN 61000-6-2:2005                    | EMC -- Immunity for industrial environments    |
| EN 61000-6-4:2007                    | EMC -- Emissions for industrial environments   |

**CE Declaration of Conformity** is available upon request from Meridian Advanced Manufacturing Systems Ltd.

---

**End of Document**

*AMS-500-MAN-001 Rev C -- Copyright 2025 Meridian Advanced Manufacturing Systems Ltd. All rights reserved.*
*Unauthorised reproduction or distribution of this document is prohibited.*
