# Communication Gateway Module Inspection

**Project:** AMS-500 Security Assessment  
**Document ID:** TD-AMS500-003  
**Classification:** OFFICIAL  
**Assessor:** [REDACTED]  
**Date:** 2026-03-21  
**Reference:** Follows TD-AMS500-001 (Physical Assessment)  

---

## 1. Module Overview

The communication gateway module is a DIN-rail mounted unit in a Phoenix Contact ME 45 UT/FE BUS/6+2 housing (grey polycarbonate, approximately 115mm x 75mm x 45mm). It is located on the bottom DIN rail of the main control cabinet, between the relay block and the terminal strips. The module's primary function is protocol translation between the PROFINET network (connected to the Siemens S7-1500 PLC) and Modbus TCP/IP devices on a secondary network segment.

The module carries no visible manufacturer branding -- only a white adhesive label with part number "AMS-CGW-200 Rev B" and serial "CGW-0024-00891". A separate label reads "FW: v2.1.4 | MAC: 00:1A:2B:3C:4D:5E / 00:1A:2B:3C:4D:5F".

---

## 2. External Interfaces

### 2.1 Front Panel

- **ETH1 (RJ-45):** Connected to the Hirschmann managed switch port 3. Link LED green (100 Mbps). Labelled "PROFINET / ETH1". This is the PROFINET IO-device interface.
- **ETH2 (RJ-45):** Not connected at time of inspection. Labelled "MODBUS TCP / ETH2". Intended for connection to Modbus TCP field devices or a secondary network segment.
- **STATUS LED:** Blinking green (normal operation pattern: 1 Hz, 50% duty cycle).
- **FAULT LED:** Off.
- **POWER LED:** Solid green.
- **LINK/ACT LEDs:** One pair per Ethernet port, standard green/amber.

### 2.2 Bottom Panel

- **Serial port (9-pin D-sub male):** Labelled "RS-232/485". A 4-position DIP switch bank (SW1) adjacent to the connector selects the mode:

| SW1 | SW2 | SW3 | SW4 | Mode |
|-----|-----|-----|-----|------|
| OFF | OFF | - | - | RS-232 |
| ON | OFF | - | - | RS-485 half-duplex (2-wire) |
| ON | ON | - | - | RS-485 full-duplex (4-wire) |
| - | - | ON | - | 120 ohm termination enabled |
| - | - | - | ON | Reserved |

At time of inspection: SW1=ON, SW2=OFF, SW3=ON, SW4=OFF (RS-485 half-duplex with termination).

- **Power connector:** 2-pin Phoenix Contact MSTB 2.5 (24VDC input). Measured 24.1VDC, 0.35A draw.

### 2.3 Rear Panel

- **Factory reset button:** Recessed tactile button, accessible with a paperclip. Label: "Press and hold 5s to restore factory defaults." No tamper protection.

---

## 3. Internal Inspection

Opened the housing by releasing four snap-fit clips on the sides. Single PCB, approximately 100mm x 65mm, 4-layer, green solder mask. Board marking "CGW-200-B REV2.1 2024-06".

### 3.1 Major Components Identified

**U1 -- Xilinx Spartan-6 XC6SLX9-2TQG144C:**
FPGA, TQFP-144 package. The Spartan-6 handles the real-time protocol translation logic. Based on the LX9 variant, this has 9,152 logic cells, 32 DSP48A1 slices, and 576 Kbit block RAM. The FPGA configuration is loaded at power-up from an adjacent SPI flash.

**U2 -- Winbond W25Q32JVSIQ:**
32 Mbit (4 MB) SPI NOR flash, SOIC-8. Stores the FPGA bitstream and the embedded soft-core processor firmware. Probing the SPI bus during power-up confirmed the FPGA loads its configuration from this device. The bitstream is not encrypted (Spartan-6 supports AES-256 bitstream encryption, but the encryption fuse is not blown -- confirmed by reading the FPGA IDCODE and status register via JTAG).

**U3 -- Microchip ENC28J60-I/SS:**
Stand-alone Ethernet controller, SSOP-28. This provides the second Ethernet port (ETH2 / Modbus TCP). The ENC28J60 is an older, simpler Ethernet controller that operates at 10 Mbps only. It is connected to the FPGA via SPI.

**U4 -- Microchip LAN8720A-CP:**
10/100 Ethernet PHY, QFN-24. This provides the first Ethernet port (ETH1 / PROFINET). Connected to the FPGA's MII interface.

**U5 -- Lattice ispMACH LC4064V-75TN100C:**
CPLD, TQFP-100. Appears to handle glue logic and I/O multiplexing between the serial port, DIP switches, and FPGA.

**U6 -- Maxim MAX3232CSE+:**
RS-232 transceiver, SOIC-16. Provides RS-232 voltage levels for the serial port when in RS-232 mode.

**U7 -- Maxim MAX3485ESA+:**
RS-485 transceiver, SOIC-8. Provides RS-485 differential signalling when in RS-485 mode.

**U8 -- Microchip PIC16F1829-I/SS:**
8-bit microcontroller, SSOP-20. Likely handles housekeeping: LED control, DIP switch reading, watchdog monitoring, factory reset button debouncing, and reporting status to the FPGA.

**Y1, Y2:** 25.000 MHz crystal (Ethernet reference), 50.000 MHz crystal oscillator (FPGA main clock).

### 3.2 JTAG Interface

A 6-pin 2.54mm header (J3) is populated on the board. Pin labels on silkscreen:

| Pin | Signal |
|-----|--------|
| 1 | VCC (3.3V) |
| 2 | TMS |
| 3 | TCK |
| 4 | TDO |
| 5 | TDI |
| 6 | GND |

This is the Spartan-6 JTAG port. Connected with a Digilent HS3 JTAG adapter and confirmed access using Xilinx Vivado Hardware Manager. The FPGA IDCODE reads 0x04001093 (XC6SLX9). As noted, the bitstream is not encrypted -- a full bitstream readback was performed and saved for analysis.

---

## 4. Network Services Discovery

### 4.1 TFTP Server

Port-scanned ETH1 (IP address obtained from the PLC's PROFINET device list: 192.168.1.20). Nmap results:

```
PORT     STATE SERVICE
69/udp   open  tftp
80/tcp   open  http
102/tcp  open  iso-tsap
502/tcp  open  modbus
4840/tcp open  opcua
```

The TFTP server on UDP port 69 is enabled by default. Tested file retrieval:

```
$ tftp 192.168.1.20
tftp> get config.xml
Received 14832 bytes in 0.3 seconds
tftp> get firmware.bin
Received 3145728 bytes in 8.2 seconds
```

Both files were retrieved without authentication. The TFTP server allows both GET and PUT operations. The firmware binary (`firmware.bin`, 3 MB) matches the SPI flash contents extracted via JTAG, confirming this is the FPGA bitstream plus soft-core firmware.

### 4.2 Web Interface

HTTP on port 80 serves a basic configuration web interface. Tested with a browser:

- Login page accepts "admin" / "admin" (factory default -- the same credentials printed on a sticker inside the housing).
- Configuration pages allow: IP address settings, PROFINET device name, Modbus register mapping table, serial port parameters, firmware update upload, diagnostic logs download.
- The web interface runs on a MicroBlaze soft-core processor instantiated in the FPGA.

### 4.3 Configuration Backup

Retrieved `config.xml` via TFTP. The file is plaintext XML with no encryption or authentication:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<GatewayConfig version="2.1.4">
  <Network>
    <ETH1 ip="192.168.1.20" mask="255.255.255.0" gateway="192.168.1.1" />
    <ETH2 ip="10.0.50.1" mask="255.255.255.0" gateway="" />
  </Network>
  <PROFINET deviceName="ams500-gw" />
  <Modbus>
    <Server port="502" unitID="1" maxConnections="5" />
    <RegisterMap>
      <Register address="40001" type="HoldingRegister" source="PN" 
               pnSlot="1" pnSubslot="1" offset="0" length="2" 
               description="Laser power setpoint" />
      <Register address="40003" type="HoldingRegister" source="PN"
               pnSlot="1" pnSubslot="1" offset="2" length="2"
               description="Scan speed setpoint" />
      <!-- ... additional register mappings ... -->
    </RegisterMap>
  </Modbus>
  <Serial mode="RS485" baud="9600" dataBits="8" parity="none" 
          stopBits="1" />
  <Security>
    <WebUI username="admin" password="admin" />
    <TFTP enabled="true" readOnly="false" />
  </Security>
</GatewayConfig>
```

Key observations from the configuration:
- Web UI credentials are stored in plaintext in the XML configuration.
- TFTP is explicitly enabled and set to read-write mode.
- The Modbus register map exposes laser power setpoint and scan speed setpoint as holding registers accessible from any Modbus TCP client on the ETH2 network.
- OPC-UA endpoint on port 4840 is also exposed (not shown in XML excerpt -- configured in a separate section).

---

## 5. Security-Relevant Findings

1. **TFTP server enabled by default with read-write access.** Any host on the PROFINET network segment can extract the full firmware image and configuration, or upload modified versions. No authentication is required.

2. **Configuration stored in plaintext XML.** Credentials, network parameters, and the complete Modbus-to-PROFINET register mapping are exposed. The register mapping reveals which PLC data points are accessible and provides a roadmap for targeted attacks on process parameters.

3. **FPGA bitstream is unencrypted.** The Spartan-6 FPGA loads an unencrypted bitstream from SPI flash. An attacker could reverse-engineer the protocol translation logic, identify vulnerabilities, or create a modified bitstream that alters data in transit between PROFINET and Modbus. Replacement bitstream could be uploaded via TFTP or JTAG.

4. **Default web credentials.** The web interface uses admin/admin with no forced password change on first login.

5. **Factory reset with no physical protection.** The rear-panel reset button restores all settings to factory defaults, including resetting credentials and re-enabling TFTP if it had been disabled by an operator.

6. **Modbus TCP has no authentication.** Modbus TCP on port 502 is accessible without authentication. Combined with the register map from the XML configuration, an attacker on the ETH2 segment can directly read and write laser power setpoints and scan speed values.

---

*Document version: 1.0 | Last updated: 2026-03-21*
