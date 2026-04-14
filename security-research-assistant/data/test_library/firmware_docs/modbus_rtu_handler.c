/**
 * Modbus RTU Communication Handler
 * Target: STM32F407VGT6 (USART2, RS-485 via MAX485 transceiver)
 *
 * Protocol: Modbus RTU over RS-485 half-duplex
 * Baud: 19200, 8N1
 * Slave address: 0x01
 *
 * SECURITY NOTES:
 * - No authentication on Modbus protocol (by design — protocol limitation)
 * - Any device on the RS-485 bus can read/write all registers
 * - Function codes 5 (Write Single Coil) and 6 (Write Single Register)
 *   allow arbitrary write access to holding registers
 * - No encryption on the bus — all traffic is plaintext
 * - No rate limiting on requests — susceptible to DoS
 */

#include <stdint.h>
#include <string.h>
#include "stm32f4xx.h"
#include "modbus_rtu.h"
#include "sensor_data.h"

/* Modbus register map */
#define REG_FIRMWARE_VERSION    0x0000  /* Read-only: firmware version */
#define REG_DEVICE_STATUS       0x0001  /* Read-only: device status flags */
#define REG_SENSOR_START        0x0010  /* Read-only: sensor data (8 channels) */
#define REG_SETPOINT_START      0x0020  /* Read-write: control setpoints */
#define REG_ALARM_THRESHOLD     0x0030  /* Read-write: alarm thresholds */
#define REG_CALIBRATION_START   0x0040  /* Read-write: calibration values */
#define REG_SYSTEM_CONTROL      0x0050  /* Read-write: system control register */

/* System control register bits */
#define CTRL_EMERGENCY_STOP     0x0001  /* Bit 0: Emergency stop */
#define CTRL_MOTOR_ENABLE       0x0002  /* Bit 1: Motor enable */
#define CTRL_HEATER_ENABLE      0x0004  /* Bit 2: Heater enable */
#define CTRL_RESET_ALARMS       0x0008  /* Bit 3: Reset alarm flags */
#define CTRL_FACTORY_RESET      0x8000  /* Bit 15: Factory reset (DANGEROUS) */

static uint16_t holding_registers[64];
static uint16_t input_registers[32];
static uint8_t coils[16];

static uint8_t rx_buffer[256];
static uint8_t tx_buffer[256];
static volatile uint16_t rx_count = 0;

/**
 * Calculate Modbus CRC-16
 * Standard CRC-16/MODBUS polynomial: 0xA001
 */
static uint16_t modbus_crc16(const uint8_t *data, uint16_t length) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001)
                crc = (crc >> 1) ^ 0xA001;
            else
                crc >>= 1;
        }
    }
    return crc;
}

/**
 * Initialize Modbus RTU on USART2
 * RS-485 direction control via GPIO pin (DE/RE on MAX485)
 */
void modbus_init(void) {
    /* Enable USART2 clock */
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    /* Configure PA2 (TX) and PA3 (RX) as alternate function */
    GPIOA->MODER |= (2 << 4) | (2 << 6);  /* AF mode */
    GPIOA->AFR[0] |= (7 << 8) | (7 << 12); /* AF7 = USART2 */

    /* Configure USART2: 19200 baud, 8N1 */
    USART2->BRR = 168000000 / 4 / 19200;  /* APB1 = HCLK/4 */
    USART2->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE | USART_CR1_RXNEIE;

    /* RS-485 direction control: PA1 = DE/RE */
    GPIOA->MODER |= (1 << 2);  /* Output mode */

    /* Initialize default register values */
    holding_registers[REG_FIRMWARE_VERSION] = 0x0103;  /* v1.3 */
    holding_registers[REG_DEVICE_STATUS] = 0x0000;     /* All clear */

    /* SECURITY ISSUE: Default setpoints are writable without authentication */
    holding_registers[REG_SETPOINT_START] = 2500;      /* Default temp setpoint: 250.0°C */
    holding_registers[REG_ALARM_THRESHOLD] = 3000;     /* Alarm at 300.0°C */

    /* SECURITY ISSUE: Factory reset accessible via Modbus without any protection */
    /* Writing 0x8000 to REG_SYSTEM_CONTROL will erase all calibration data */

    NVIC_EnableIRQ(USART2_IRQn);
}

/**
 * Process incoming Modbus RTU frame
 * WARNING: No authentication, no rate limiting, no access control
 */
void modbus_process_frame(void) {
    if (rx_count < 4) return;  /* Minimum frame: addr + func + CRC16 */

    uint8_t slave_addr = rx_buffer[0];
    uint8_t function = rx_buffer[1];

    /* Check slave address */
    if (slave_addr != MODBUS_SLAVE_ADDRESS && slave_addr != 0x00) {
        rx_count = 0;
        return;  /* Not for us (broadcast addr 0x00 is accepted) */
    }

    /* Verify CRC */
    uint16_t received_crc = (rx_buffer[rx_count-1] << 8) | rx_buffer[rx_count-2];
    uint16_t calc_crc = modbus_crc16(rx_buffer, rx_count - 2);
    if (received_crc != calc_crc) {
        rx_count = 0;
        return;  /* CRC error — silently discard */
    }

    switch (function) {
        case 0x03:  /* Read Holding Registers */
            modbus_read_registers(holding_registers);
            break;
        case 0x04:  /* Read Input Registers */
            modbus_read_registers(input_registers);
            break;
        case 0x05:  /* Write Single Coil */
            /* SECURITY: No access control — any bus device can toggle coils */
            modbus_write_single_coil();
            break;
        case 0x06:  /* Write Single Register */
            /* SECURITY: No access control — any bus device can write registers */
            /* Including CTRL_FACTORY_RESET and CTRL_EMERGENCY_STOP */
            modbus_write_single_register();
            break;
        default:
            modbus_exception_response(0x01);  /* Illegal function */
            break;
    }

    rx_count = 0;
}
