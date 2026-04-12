"""Generate test fixture files for the ingestion test suite.

Run this script once to create sample files in tests/fixtures/.
Also used by conftest.py to create temporary fixtures per test session.
"""

from pathlib import Path


def create_sample_pdf(dest: Path) -> Path:
    """Create a 3-page PDF about a microcontroller using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    filepath = dest / "sample.pdf"
    c = canvas.Canvas(str(filepath), pagesize=A4)

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 780, "STM32F407VGT6 Technical Overview")
    c.setFont("Helvetica", 11)
    y = 750
    for line in [
        "The STM32F407VGT6 is a high-performance microcontroller based on the",
        "ARM Cortex-M4 core with FPU, running at up to 168 MHz.",
        "",
        "Key Features:",
        "- 1 MB Flash memory, 192 KB SRAM",
        "- Up to 82 GPIO pins with alternate functions",
        "- SPI, I2C, UART, CAN, USB OTG interfaces",
        "- 12-bit ADC with up to 24 channels",
        "- Operating voltage: 1.8V to 3.6V",
    ]:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 780, "Pin Configuration and Interfaces")
    c.setFont("Helvetica", 11)
    y = 750
    for line in [
        "GPIO Port A: PA0-PA15 — general purpose I/O",
        "SPI1: PA5 (SCK), PA6 (MISO), PA7 (MOSI), PA4 (NSS)",
        "I2C1: PB6 (SCL), PB7 (SDA)",
        "UART2: PA2 (TX), PA3 (RX)",
        "JTAG: PA13 (SWDIO), PA14 (SWCLK)",
        "",
        "The processor communicates with external peripherals via:",
        "- SPI bus for high-speed data transfer to sensors",
        "- I2C bus for configuration of low-speed peripherals",
        "- UART for debug console and logging output",
    ]:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()

    # Page 3
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 780, "Power Supply and Operating Conditions")
    c.setFont("Helvetica", 11)
    y = 750
    for line in [
        "Supply voltage (VDD): 1.8V to 3.6V",
        "Maximum current consumption: 150mA at 168MHz",
        "Operating temperature: -40C to +85C (industrial grade)",
        "Package: LQFP100 (100-pin low-profile quad flat package)",
        "",
        "Modbus RTU communication is supported via UART interfaces.",
        "The device supports OPC-UA protocol stacks for ICS integration.",
    ]:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()

    c.save()
    return filepath


def create_sample_image(dest: Path) -> Path:
    """Create a simple image with text for OCR testing."""
    from PIL import Image, ImageDraw, ImageFont

    filepath = dest / "sample.png"
    img = Image.new("RGB", (400, 200), color="white")
    draw = ImageDraw.Draw(img)

    # Use default font
    draw.text((20, 20), "Component: STM32F407", fill="black")
    draw.text((20, 50), "Interface: SPI, I2C, UART", fill="black")
    draw.text((20, 80), "Voltage: 3.3V", fill="black")
    draw.text((20, 110), "Package: LQFP100", fill="black")

    img.save(filepath)
    return filepath


def create_sample_c(dest: Path) -> Path:
    """Create a C source file with functions, structs, and comments."""
    filepath = dest / "sample.c"
    filepath.write_text("""\
/* STM32F407 GPIO Driver
 * Author: Security Research Team
 * Purpose: Basic GPIO initialization and control
 */

#include <stdint.h>
#include <stdbool.h>
#include "stm32f407.h"

#define GPIO_PIN_HIGH  1
#define GPIO_PIN_LOW   0
#define MAX_PINS       16

/* GPIO pin configuration structure */
typedef struct {
    uint8_t pin_number;
    uint8_t mode;       /* 0=input, 1=output, 2=alternate, 3=analog */
    uint8_t pull;       /* 0=none, 1=pullup, 2=pulldown */
    uint8_t speed;      /* 0=low, 1=medium, 2=fast, 3=high */
} gpio_config_t;

/* Initialize a GPIO pin with the given configuration */
void gpio_init(gpio_config_t *config) {
    if (config == NULL || config->pin_number >= MAX_PINS) {
        return;
    }
    /* Set mode register bits */
    uint32_t mode_bits = (uint32_t)(config->mode) << (config->pin_number * 2);
    GPIOA->MODER |= mode_bits;
}

/* Read the current state of a GPIO pin */
bool gpio_read(uint8_t pin_number) {
    if (pin_number >= MAX_PINS) {
        return false;
    }
    return (GPIOA->IDR >> pin_number) & 0x01;
}

/* Write a value to a GPIO pin */
void gpio_write(uint8_t pin_number, uint8_t value) {
    if (pin_number >= MAX_PINS) {
        return;
    }
    if (value == GPIO_PIN_HIGH) {
        GPIOA->BSRR = (1 << pin_number);
    } else {
        GPIOA->BSRR = (1 << (pin_number + 16));
    }
}
""", encoding="utf-8")
    return filepath


def create_sample_txt(dest: Path) -> Path:
    """Create a plain text file with section headings."""
    filepath = dest / "sample.txt"
    filepath.write_text("""\
# Industrial Control System Overview

## Communication Protocols

The system uses Modbus RTU over RS-485 for field device communication.
OPC-UA is used for supervisory level data exchange.
MQTT handles lightweight telemetry from edge sensors.

## Hardware Architecture

The main controller board contains an STM32F407 processor.
It interfaces with 4 analog input modules via SPI bus.
Each module reads 8 channels of 0-10V analog signals.

## Known Vulnerabilities

Default credentials on the HMI web interface (admin/admin).
Modbus protocol has no built-in authentication mechanism.
Firmware update mechanism does not verify digital signatures.
""", encoding="utf-8")
    return filepath


def create_sample_csv(dest: Path) -> Path:
    """Create a CSV file with component specifications."""
    filepath = dest / "sample.csv"
    filepath.write_text("""\
Component,Part Number,Interface,Voltage,Package
Main Processor,STM32F407VGT6,SPI/I2C/UART,3.3V,LQFP100
Temperature Sensor,TMP117,I2C,3.3V,SOT-6
Flash Memory,W25Q128,SPI,3.3V,SOIC-8
CAN Transceiver,MCP2551,CAN,5V,DIP-8
Power Regulator,AMS1117-3.3,N/A,3.3V,SOT-223
""", encoding="utf-8")
    return filepath


def create_all_fixtures(dest: Path) -> dict[str, Path]:
    """Create all test fixture files in the given directory.

    Returns:
        Dict mapping fixture name to file path.
    """
    dest.mkdir(parents=True, exist_ok=True)
    return {
        "pdf": create_sample_pdf(dest),
        "image": create_sample_image(dest),
        "c_code": create_sample_c(dest),
        "text": create_sample_txt(dest),
        "csv": create_sample_csv(dest),
    }


if __name__ == "__main__":
    fixtures_dir = Path(__file__).parent
    paths = create_all_fixtures(fixtures_dir)
    for name, path in paths.items():
        print(f"  Created: {name} -> {path}")
