/**
 * STM32F407 Key Register Definitions
 * Extracted from RM0090 Reference Manual
 *
 * This header provides the critical register addresses and bit definitions
 * for security-relevant peripherals on the STM32F407VGT6.
 */

#ifndef STM32F4_REGISTER_MAP_H
#define STM32F4_REGISTER_MAP_H

#include <stdint.h>

/* ============================================================
 * FLASH INTERFACE REGISTERS (Security-Critical)
 * Base: 0x40023C00
 * ============================================================ */
#define FLASH_BASE          0x40023C00
#define FLASH_ACR           (*(volatile uint32_t *)(FLASH_BASE + 0x00))  /* Access control */
#define FLASH_KEYR          (*(volatile uint32_t *)(FLASH_BASE + 0x04))  /* Key register */
#define FLASH_OPTKEYR       (*(volatile uint32_t *)(FLASH_BASE + 0x08))  /* Option key */
#define FLASH_SR            (*(volatile uint32_t *)(FLASH_BASE + 0x0C))  /* Status */
#define FLASH_CR            (*(volatile uint32_t *)(FLASH_BASE + 0x10))  /* Control */
#define FLASH_OPTCR         (*(volatile uint32_t *)(FLASH_BASE + 0x14))  /* Option control */

/* Flash unlock keys — SECURITY SENSITIVE */
#define FLASH_KEY1          0x45670123
#define FLASH_KEY2          0xCDEF89AB
#define FLASH_OPT_KEY1      0x08192A3B
#define FLASH_OPT_KEY2      0x4C5D6E7F

/* Read-out protection levels */
#define RDP_LEVEL_0         0xAA    /* No protection */
#define RDP_LEVEL_1         0x00    /* Read protection (default if not 0xAA or 0xCC) */
#define RDP_LEVEL_2         0xCC    /* Full protection (IRREVERSIBLE!) */

/* ============================================================
 * GPIO REGISTERS
 * Ports A-I, Base: 0x40020000 + 0x400 * port_number
 * ============================================================ */
#define GPIOA_BASE          0x40020000
#define GPIOB_BASE          0x40020400
#define GPIOC_BASE          0x40020800

/* GPIO register offsets */
#define GPIO_MODER          0x00    /* Mode register */
#define GPIO_OTYPER         0x04    /* Output type */
#define GPIO_OSPEEDR        0x08    /* Output speed */
#define GPIO_PUPDR          0x0C    /* Pull-up/pull-down */
#define GPIO_IDR            0x10    /* Input data */
#define GPIO_ODR            0x14    /* Output data */
#define GPIO_BSRR           0x18    /* Bit set/reset */
#define GPIO_LCKR           0x1C    /* Configuration lock */
#define GPIO_AFRL           0x20    /* Alternate function low */
#define GPIO_AFRH           0x24    /* Alternate function high */

/* ============================================================
 * USART REGISTERS (Modbus RTU communication)
 * USART2 Base: 0x40004400
 * ============================================================ */
#define USART2_BASE         0x40004400
#define USART2_SR           (*(volatile uint32_t *)(USART2_BASE + 0x00))
#define USART2_DR           (*(volatile uint32_t *)(USART2_BASE + 0x04))
#define USART2_BRR          (*(volatile uint32_t *)(USART2_BASE + 0x08))
#define USART2_CR1          (*(volatile uint32_t *)(USART2_BASE + 0x0C))
#define USART2_CR2          (*(volatile uint32_t *)(USART2_BASE + 0x10))
#define USART2_CR3          (*(volatile uint32_t *)(USART2_BASE + 0x14))

/* ============================================================
 * SPI REGISTERS (Flash memory and sensor communication)
 * SPI1 Base: 0x40013000
 * ============================================================ */
#define SPI1_BASE           0x40013000
#define SPI1_CR1            (*(volatile uint32_t *)(SPI1_BASE + 0x00))
#define SPI1_CR2            (*(volatile uint32_t *)(SPI1_BASE + 0x04))
#define SPI1_SR             (*(volatile uint32_t *)(SPI1_BASE + 0x08))
#define SPI1_DR             (*(volatile uint32_t *)(SPI1_BASE + 0x0C))

/* SPI clock prescalers */
#define SPI_BAUDRATE_42MHZ  0x00    /* fPCLK/2 = 84/2 = 42 MHz */
#define SPI_BAUDRATE_21MHZ  0x08    /* fPCLK/4 */
#define SPI_BAUDRATE_10MHZ  0x10    /* fPCLK/8 */

/* ============================================================
 * CAN REGISTERS (Industrial communication)
 * CAN1 Base: 0x40006400
 * ============================================================ */
#define CAN1_BASE           0x40006400
#define CAN1_MCR            (*(volatile uint32_t *)(CAN1_BASE + 0x00))  /* Master control */
#define CAN1_MSR            (*(volatile uint32_t *)(CAN1_BASE + 0x04))  /* Master status */
#define CAN1_BTR            (*(volatile uint32_t *)(CAN1_BASE + 0x1C))  /* Bit timing */

/* ============================================================
 * DEBUG / JTAG REGISTERS (Attack surface)
 * DBGMCU Base: 0xE0042000
 * ============================================================ */
#define DBGMCU_BASE         0xE0042000
#define DBGMCU_IDCODE       (*(volatile uint32_t *)(DBGMCU_BASE + 0x00))
#define DBGMCU_CR           (*(volatile uint32_t *)(DBGMCU_BASE + 0x04))

/* SECURITY NOTE: JTAG/SWD pins are enabled by default after reset
 * PA13 = SWDIO, PA14 = SWCLK, PA15 = JTDI, PB3 = JTDO, PB4 = NJTRST
 * To disable JTAG (but keep SWD): set SWJ_CFG bits in AFIO_MAPR
 * To disable all debug: set DBGMCU_CR appropriately
 * WARNING: Disabling debug prevents firmware updates via debug probe! */

#endif /* STM32F4_REGISTER_MAP_H */
