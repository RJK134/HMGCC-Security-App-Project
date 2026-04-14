# PCB Analysis -- AMS-500 Main Controller Board

**Project:** AMS-500 Security Assessment  
**Document ID:** TD-AMS500-002  
**Classification:** OFFICIAL  
**Assessor:** [REDACTED]  
**Date:** 2026-03-20  
**Reference:** Follows TD-AMS500-001 (Physical Assessment)  

---

## 1. Board Overview

The main controller board (referred to hereafter as "MCB") was removed from its sealed enclosure above the control cabinet. Board marking: "AMS-MCB Rev C.2", date code "2024-W30". PCB dimensions 160mm x 100mm, estimated 6-layer stackup based on edge profile inspection. Green solder mask, white silkscreen, ENIG (gold) finish on pads. All components are surface-mount on top and bottom sides.

The MCB acts as the central coordinator between the Siemens S7-1500 PLC (via PROFINET), the laser control subsystem (via CAN bus), legacy sensors (via RS-485), and the operator-facing application logic. It runs its own real-time firmware independently of the PLC.

---

## 2. IC Identification and Function Mapping

### 2.1 STM32F407VGT6 -- Main Microcontroller (U1)

**Package:** LQFP-100  
**Marking:** STM32F407VGT6, date code 2348  
**Function:** Central processing. ARM Cortex-M4 core at 168 MHz, hardware FPU, 1MB internal flash, 192KB SRAM.

Pin assignments determined by PCB trace analysis and cross-reference with STM32F407 datasheet (DS8626 Rev 9):

| MCU Pin | Net Name | Function | Destination |
|---------|----------|----------|-------------|
| PA0 | ADC_IN0 | ADC Channel 0 | Analogue sensor conditioning circuit |
| PA1 | ETH_REF_CLK | RMII reference clock | LAN8742A pin 14 |
| PA2 | ETH_MDIO | RMII management data | LAN8742A pin 10 |
| PA5 | SPI1_SCK | SPI clock | W25Q128 pin 6 (CLK) |
| PA6 | SPI1_MISO | SPI data in | W25Q128 pin 2 (DO) |
| PA7 | SPI1_MOSI | SPI data out | W25Q128 pin 5 (DI) |
| PA9 | USART1_TX | Debug UART TX | J12 pin 2 |
| PA10 | USART1_RX | Debug UART RX | J12 pin 3 |
| PA11 | CAN1_RX | CAN receive | MCP2551 pin 4 (RXD) |
| PA12 | CAN1_TX | CAN transmit | MCP2551 pin 1 (TXD) |
| PA13 | SWDIO | Debug data | J5 pin 2 |
| PA14 | SWCLK | Debug clock | J5 pin 4 |
| PB6 | I2C1_SCL | I2C clock | ATECC608A pin 6, 24LC256 pin 6 |
| PB7 | I2C1_SDA | I2C data | ATECC608A pin 5, 24LC256 pin 5 |
| PB8 | USART3_TX | RS-485 TX | MAX485 pin 4 (DI) |
| PB9 | USART3_RX | RS-485 RX | MAX485 pin 1 (RO) |
| PB10 | RS485_DE | RS-485 direction | MAX485 pins 2,3 (RE/DE) |
| PC1 | ETH_MDC | RMII management clock | LAN8742A pin 9 |
| PC4 | ETH_RXD0 | RMII receive data 0 | LAN8742A pin 16 |
| PC5 | ETH_RXD1 | RMII receive data 1 | LAN8742A pin 15 |
| PC6 | SPI1_CS0 | SPI chip select (flash) | W25Q128 pin 1 (CS#) |
| PC7 | ATECC_CS | I2C address select | ATECC608A |
| PD0 | STATUS_LED_R | Red status LED | LED D3 via 470R |
| PD1 | STATUS_LED_G | Green status LED | LED D4 via 470R |
| PE4 | BOOT0_SEL | Boot mode select | R47 pull-down to GND |

### 2.2 W25Q128JVSIQ -- SPI NOR Flash (U3)

**Package:** SOIC-8  
**Capacity:** 128 Mbit (16 MB)  
**Function:** Primary firmware storage, configuration data, and log buffer.

Flash memory layout determined by firmware dump analysis (extracted via SPI bus sniffing during boot):

| Address Range | Size | Content |
|---------------|------|---------|
| 0x000000 - 0x00FFFF | 64 KB | Bootloader image |
| 0x010000 - 0x0FFFFF | 960 KB | Firmware slot A (active) |
| 0x100000 - 0x1FFFFF | 1 MB | Firmware slot B (update staging) |
| 0x200000 - 0x20FFFF | 64 KB | Configuration block (plaintext key-value) |
| 0x210000 - 0x21FFFF | 64 KB | Calibration data (CRC32-protected) |
| 0x220000 - 0x23FFFF | 128 KB | Certificate store |
| 0x240000 - 0x2FFFFF | 768 KB | Event log (circular buffer) |
| 0x300000 - 0xFFFFFF | 13 MB | Reserved / 0xFF |

The dual firmware slot arrangement supports A/B update with rollback. The configuration block at 0x200000 was found to be in plaintext with no authentication or encryption. It contains network parameters, CAN bus configuration, PROFINET device name, and Modbus register mappings.

### 2.3 ATECC608A-MAHDA-S -- Secure Element (U7)

**Package:** UDFN-8  
**Interface:** I2C (shared bus with U4 EEPROM)  
**Function:** Firmware signature verification, potentially key storage.

The ATECC608A is Microchip's secure element with hardware ECDSA, AES-128, SHA-256, and protected key storage. The "A" designation indicates the Trust&GO pre-provisioned variant with a Microchip-signed certificate chain.

Observations:
- The bootloader queries the ATECC608A during startup for firmware signature verification (observed on I2C bus via logic analyser).
- Signature verification uses ECDSA P-256. The public key is stored in ATECC608A slot 0.
- If signature verification fails, the bootloader halts with a repeating error message on UART: "FW SIG FAIL -- SYSTEM HALTED".
- However, the BOOT0 pin (PE4) is pulled low by a 10K resistor (R47) but is accessible via test point TP9 (not listed on the silkscreen but identified by trace). Pulling BOOT0 high during reset forces the STM32 into its internal ROM bootloader, bypassing the secure boot entirely. The ROM bootloader accepts UART and USB DFU firmware uploads without signature checks.

### 2.4 MCP2551-I/SN -- CAN Bus Transceiver (U5)

**Package:** SOIC-8  
**Function:** Physical layer for CAN bus to laser control subsystem.

The CAN bus operates at 500 kbps. The bus has 120-ohm termination resistors at both ends (one on the MCB at R12, one presumably at the laser controller). CAN_H and CAN_L are available on test points TP4 and TP5.

### 2.5 MAX485ESA+ -- RS-485 Transceiver (U6)

**Package:** SOIC-8  
**Function:** Physical layer for the RS-485 legacy sensor bus.

Half-duplex RS-485 running at 9600 baud 8N1. The direction control (DE/RE) is managed by PB10 on the STM32. The bus addresses 16 legacy temperature and humidity sensors in the build chamber environment monitoring system.

### 2.6 LAN8742A-CZ -- Ethernet PHY (U2)

**Package:** QFN-24  
**Function:** 10/100 Ethernet physical layer for PROFINET and service access.

Connected to the STM32's RMII interface. The Ethernet magnetics are a Pulse H1102NL transformer. Single RJ-45 jack (J1) with integrated LEDs (green = link, amber = activity). This Ethernet port connects to the Hirschmann managed switch in the control cabinet.

### 2.7 24LC256-I/SN -- I2C EEPROM (U4)

**Package:** SOIC-8  
**Capacity:** 256 Kbit (32 KB)  
**Function:** Machine-specific calibration and identification data.

Address 0x50 on the I2C bus. Contains the machine serial number, laser power calibration offsets, galvo scanner alignment parameters, and build platform Z-axis home position offset. This data is read during boot and is referenced in the calibration verification routine. The EEPROM write-protect pin (WP) is tied low -- no write protection is enabled. An attacker with I2C bus access (via the SWD header or by probing the bus) could modify calibration values.

---

## 3. Debug Interfaces

### 3.1 SWD Debug Port (J5)

10-pin 1.27mm Cortex Debug Connector (standard ARM pinout):

| Pin | Signal |
|-----|--------|
| 1 | VTref (3.3V) |
| 2 | SWDIO |
| 3 | GND |
| 4 | SWCLK |
| 5 | GND |
| 6 | SWO (trace output) |
| 7 | -- (key, no pin) |
| 8 | NC |
| 9 | GND |
| 10 | nRST |

Connected a Segger J-Link EDU to J5. The STM32 is detected:
```
J-Link> connect
Device: STM32F407VG
Target interface: SWD
Speed: 4000 kHz
Device ID: 0x10076413
Flash size: 1024 KB
RDP Level: 1
```

RDP Level 1 blocks:
- Direct flash memory read via debugger
- SRAM read when debugger attached from reset

RDP Level 1 allows:
- Halting the CPU, setting breakpoints
- Reading RAM during runtime after firmware has started
- Debugging application code

Downgrading from RDP Level 1 to Level 0 triggers a full flash erase, which destroys the firmware but would allow re-flashing. However, the BOOT0 bypass (section 2.3) provides a more practical alternative for firmware manipulation.

### 3.2 UART Debug Console (J12)

4-pin 2.54mm header (through-hole pads, unpopulated -- requires soldering pin header or use of pogo pins):

| Pin | Signal | Direction |
|-----|--------|-----------|
| 1 | GND | -- |
| 2 | TX | MCB to host |
| 3 | RX | Host to MCB |
| 4 | 3V3 | Power reference |

Baud rate: 115200, 8N1. 3.3V logic levels.

The UART console provides read-only boot messages during normal operation. However, sending a break condition (holding TX low for >500ms) within the first 3 seconds of boot enters a hidden diagnostic mode:

```
AMS-500 Diagnostics v1.2.0
> help
Commands:
  info       - System information
  memread    - Read memory address
  memwrite   - Write memory address  
  flashdump  - Dump flash region (hex)
  cansniff   - Monitor CAN bus traffic
  reboot     - Restart system
  fwupdate   - Enter firmware update mode
>
```

The diagnostic mode provides unrestricted memory read/write access with no authentication. The `fwupdate` command places the system into DFU mode, accepting firmware over UART.

---

## 4. Power Supply Analysis

The MCB is powered via a 4-pin Molex Micro-Fit 3.0 connector (J2):

| Pin | Voltage | Current (measured) |
|-----|---------|-------------------|
| 1 | +24VDC | 180 mA typical |
| 2 | GND | -- |
| 3 | GND | -- |
| 4 | +24VDC | -- (redundant) |

On-board regulation:
- U8 (TPS5430DDA): 24V to 5V buck converter, 560 mA measured
- U9 (TPS5430DDA): 5V to 3.3V buck converter, 320 mA measured
- U10 (MCP1700-3302E): 3.3V LDO, dedicated supply for ATECC608A (low-noise)

Power consumption profile during boot shows a distinct signature -- a 150ms spike at the ATECC608A signature verification step, which could be a target for power analysis side-channel attacks.

---

## 5. Security-Relevant Findings

1. **BOOT0 bypass negates secure boot.** The STM32's internal ROM bootloader can be activated by pulling TP9 high during reset, allowing unsigned firmware upload via UART or USB DFU. Physical access to the MCB is required, but the tamper seal is the only barrier.

2. **UART diagnostic mode provides unrestricted access.** The hidden diagnostic console has no authentication and provides full memory read/write plus firmware update capability. This is likely a development/manufacturing artefact that was not disabled in production firmware.

3. **Configuration data is unencrypted.** The SPI flash configuration block at 0x200000 is plaintext. Network parameters, device names, and register mappings could be extracted and modified.

4. **EEPROM write protection is disabled.** Calibration data in the 24LC256 EEPROM can be modified via I2C bus access, potentially affecting laser power calibration, scanner alignment, or build platform positioning.

5. **CAN bus is unencrypted and unauthenticated.** The CAN bus link to the laser control subsystem carries power set-points and enable/disable commands with no message authentication codes (MACs) or encryption. An attacker with access to TP4/TP5 could inject arbitrary CAN frames.

6. **RDP Level 1 is insufficient.** While flash readout is blocked, runtime debugging is still possible. Combined with the BOOT0 bypass, the RDP protection provides minimal security value.

---

*Document version: 1.0 | Last updated: 2026-03-20*
