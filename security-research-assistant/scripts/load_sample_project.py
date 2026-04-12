"""Load the sample ICS product assessment project with test data."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_sample_files(dest: Path) -> dict[str, Path]:
    """Generate sample documents for the demo project."""
    dest.mkdir(parents=True, exist_ok=True)
    files: dict[str, Path] = {}

    # Microcontroller datasheet (PDF)
    pdf_path = dest / "STM32F407_Technical_Reference.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    pages = [
        ("STM32F407VGT6 Technical Reference Manual",
         ["ARM Cortex-M4 core with FPU, 168 MHz maximum frequency",
          "1 MB Flash memory, 192+4 KB SRAM",
          "Up to 82 GPIO pins with alternate functions",
          "3x SPI, 3x I2C, 4x UART/USART, 2x CAN interfaces",
          "12-bit ADC (up to 24 channels), 2x 12-bit DAC",
          "Operating voltage: 1.8V to 3.6V",
          "Package: LQFP100 (14x14mm)"]),
        ("Pin Configuration and GPIO",
         ["SPI1: PA5 (SCK), PA6 (MISO), PA7 (MOSI), PA4 (NSS)",
          "I2C1: PB6 (SCL), PB7 (SDA) with 400kHz fast mode",
          "UART2: PA2 (TX), PA3 (RX) for debug console",
          "JTAG/SWD: PA13 (SWDIO), PA14 (SWCLK) for debug access",
          "CAN1: PB8 (RX), PB9 (TX) for industrial communication"]),
        ("Power Supply and Electrical Characteristics",
         ["VDD supply voltage: 1.8V to 3.6V (typical 3.3V)",
          "Maximum current consumption: 150mA at 168MHz all peripherals active",
          "Standby current: 2.4uA typical",
          "Operating temperature: -40C to +85C (industrial grade)",
          "ESD protection: 2kV HBM on all pins"]),
    ]
    for title, lines in pages:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 780, title)
        c.setFont("Helvetica", 10)
        y = 750
        for line in lines:
            c.drawString(50, y, line)
            y -= 15
        c.showPage()
    c.save()
    files["datasheet"] = pdf_path

    # Firmware code
    code_path = dest / "firmware_main.c"
    code_path.write_text("""\
/* ICS Controller Firmware - Main Application
 * Target: STM32F407VGT6
 * Protocol: Modbus RTU over RS-485
 */
#include <stdint.h>
#include "stm32f4xx.h"
#include "modbus_rtu.h"

#define SENSOR_COUNT     8
#define MODBUS_ADDR      0x01
#define BAUD_RATE        19200

static uint16_t sensor_data[SENSOR_COUNT];
static modbus_ctx_t modbus;

void system_init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    SPI1_Init(SPI_BAUDRATE_42MHZ);
    I2C1_Init(I2C_SPEED_400KHZ);
    UART2_Init(BAUD_RATE);
    modbus_init(&modbus, MODBUS_ADDR, UART2);
}

void read_sensors(void) {
    for (int i = 0; i < SENSOR_COUNT; i++) {
        sensor_data[i] = ADC_Read(i);
    }
}

int main(void) {
    system_init();
    while (1) {
        read_sensors();
        modbus_process(&modbus, sensor_data, SENSOR_COUNT);
    }
}
""", encoding="utf-8")
    files["firmware"] = code_path

    # Component specs CSV
    csv_path = dest / "component_inventory.csv"
    csv_path.write_text("""\
Component,Part Number,Type,Interface,Voltage,Package,Manufacturer
Main MCU,STM32F407VGT6,Processor,SPI/I2C/UART/CAN,3.3V,LQFP100,STMicroelectronics
Temp Sensor,TMP117AIDRVR,Sensor,I2C,3.3V,SOT-6,Texas Instruments
Flash Memory,W25Q128JVSIQ,Memory,SPI,3.3V,SOIC-8,Winbond
CAN Transceiver,MCP2551-I/SN,Transceiver,CAN,5V,SOIC-8,Microchip
RS-485 Driver,MAX485ESA,Transceiver,UART,5V,SOIC-8,Maxim
Power Regulator,AMS1117-3.3,Regulator,N/A,3.3V out,SOT-223,AMS
EEPROM,24LC256-I/SN,Memory,I2C,3.3V,SOIC-8,Microchip
Crystal,HC49-16MHz,Oscillator,N/A,N/A,HC49,Various
""", encoding="utf-8")
    files["csv"] = csv_path

    # Security analysis notes
    notes_path = dest / "security_assessment_notes.txt"
    notes_path.write_text("""\
# ICS Product Security Assessment Notes

## Debug Interfaces
- JTAG/SWD debug port is accessible on the PCB via unpopulated header J3
- No readout protection (RDP) configured on the STM32 — firmware can be dumped
- UART2 debug console outputs diagnostic messages at 19200 baud

## Communication Security
- Modbus RTU protocol has no authentication mechanism
- RS-485 bus is not encrypted — all traffic visible to any connected device
- CAN bus messages are unencrypted and unauthenticated

## Firmware Concerns
- Firmware update mechanism uses UART bootloader with no signature verification
- Default Modbus address is 0x01 — standard and easily discoverable
- No watchdog timer implementation observed

## Physical Security
- PCB has no conformal coating or tamper detection
- Flash memory IC is accessible for physical chip-off attack
- Power analysis side-channel attack is feasible via VDD pin
""", encoding="utf-8")
    files["notes"] = notes_path

    # Forum post
    forum_path = dest / "forum_discussion_modbus.txt"
    forum_path.write_text("""\
# Forum: IndustrialControlSec.net
# Thread: Modbus RTU security considerations for STM32-based controllers

User: security_researcher_42
Date: 2024-11-15

Has anyone looked at the Modbus RTU implementation on STM32F4-based controllers?
I've found that most implementations don't implement any form of access control
beyond the unit address. The protocol specification itself doesn't mandate
authentication, which means any device on the RS-485 bus can read/write any
register on any connected device.

Reply: embedded_expert
The STM32F407 UART peripheral supports 9-bit mode which some vendors use for
a basic address filtering scheme, but this is trivially spoofable. The real
concern is that function codes 5 (Write Single Coil) and 6 (Write Single Register)
allow arbitrary write access to the device's holding registers.

Reply: ics_auditor
In our assessments, we've seen this exact issue across dozens of ICS products.
The mitigation is usually network segmentation — keeping the Modbus bus physically
isolated. However, if an attacker gains physical access to the RS-485 bus,
all connected devices are compromised.
""", encoding="utf-8")
    files["forum"] = forum_path

    return files


def main() -> None:
    """Create and load the sample project."""
    sample_dir = PROJECT_ROOT / "data" / "sample_project"
    files = create_sample_files(sample_dir)
    print(f"Sample files created in: {sample_dir}")
    for name, path in files.items():
        print(f"  {name}: {path.name} ({path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
