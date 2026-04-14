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
