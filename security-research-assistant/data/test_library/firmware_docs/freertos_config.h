/*
 * FreeRTOS V10.4.3 Configuration for STM32F407 ICS Controller
 * Application: Industrial Additive Manufacturing Machine Controller
 *
 * This configuration is tuned for real-time sensor polling,
 * Modbus RTU communication, and safety watchdog monitoring.
 */

#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

/* Core FreeRTOS configuration */
#define configUSE_PREEMPTION                    1
#define configUSE_IDLE_HOOK                     0
#define configUSE_TICK_HOOK                     0
#define configCPU_CLOCK_HZ                      (168000000UL)  /* STM32F407 max clock */
#define configTICK_RATE_HZ                      (1000)         /* 1ms tick for sensor polling */
#define configMAX_PRIORITIES                    (7)
#define configMINIMAL_STACK_SIZE                (128)
#define configTOTAL_HEAP_SIZE                   (40 * 1024)    /* 40KB from 192KB SRAM */
#define configMAX_TASK_NAME_LEN                 (16)

/* Memory allocation */
#define configSUPPORT_DYNAMIC_ALLOCATION        1
#define configSUPPORT_STATIC_ALLOCATION         0

/* Task management */
#define configUSE_MUTEXES                       1
#define configUSE_RECURSIVE_MUTEXES             1
#define configUSE_COUNTING_SEMAPHORES           1
#define configQUEUE_REGISTRY_SIZE               8

/* Timer configuration */
#define configUSE_TIMERS                        1
#define configTIMER_TASK_PRIORITY               (configMAX_PRIORITIES - 1)
#define configTIMER_QUEUE_LENGTH                10
#define configTIMER_TASK_STACK_DEPTH            256

/* Interrupt priorities for STM32F4 */
#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY         15
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY    5
#define configKERNEL_INTERRUPT_PRIORITY         (configLIBRARY_LOWEST_INTERRUPT_PRIORITY << 4)
#define configMAX_SYSCALL_INTERRUPT_PRIORITY    (configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << 4)

/* WARNING: No stack overflow detection enabled in production build.
 * This is a security concern — stack overflow could corrupt memory
 * and lead to undefined behavior in safety-critical operations. */
#define configCHECK_FOR_STACK_OVERFLOW          0

/* Task priorities for ICS application */
/* NOTE: Higher number = higher priority in FreeRTOS */
#define TASK_PRIORITY_SAFETY_WATCHDOG           (configMAX_PRIORITIES - 1)  /* Highest */
#define TASK_PRIORITY_SENSOR_POLL               (configMAX_PRIORITIES - 2)
#define TASK_PRIORITY_MODBUS_HANDLER            (configMAX_PRIORITIES - 3)
#define TASK_PRIORITY_CAN_HANDLER               (configMAX_PRIORITIES - 4)
#define TASK_PRIORITY_DATA_LOGGING              (2)
#define TASK_PRIORITY_DIAGNOSTICS               (1)

/* Modbus RTU configuration */
#define MODBUS_UART                             USART2
#define MODBUS_BAUDRATE                         19200
#define MODBUS_SLAVE_ADDRESS                    0x01
#define MODBUS_HOLDING_REGISTERS                64
#define MODBUS_INPUT_REGISTERS                  32
#define MODBUS_COILS                            16

/* Sensor configuration */
#define SENSOR_ADC_CHANNELS                     8
#define SENSOR_POLL_INTERVAL_MS                 100    /* 10 Hz polling rate */
#define SENSOR_MOVING_AVERAGE_WINDOW            10

/* CAN Bus configuration */
#define CAN_BITRATE                             500000  /* 500 kbps */
#define CAN_FILTER_ID                           0x100
#define CAN_FILTER_MASK                         0x7F0

/* Security-relevant: Debug UART enabled in production */
#define DEBUG_UART                              USART1
#define DEBUG_BAUDRATE                          115200
/* TODO: Disable debug UART in production firmware release */

/* Security-relevant: No firmware signature verification */
/* The bootloader does not check firmware integrity before execution */
/* See STM32F4 AN2606 for bootloader documentation */

#endif /* FREERTOS_CONFIG_H */
