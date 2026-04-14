/**
 * AMS-500 EtherCAT Motion Controller
 * ====================================
 * Target: BeagleBone Black Industrial (AM3358, 1GHz ARM Cortex-A8)
 * OS: Debian 11 with PREEMPT_RT kernel patch (5.10.168-rt83)
 * EtherCAT Master: SOEM (Simple Open EtherCAT Master) v1.4.0
 *
 * Controls three Beckhoff servo drives over EtherCAT:
 *   Slave 1: AX5206-0000 - Build platform Z-axis (linear motor, 350mm travel)
 *   Slave 2: AX5106-0000 - Recoater X-axis (linear motor, 300mm travel)
 *   Slave 3: AX5103-0000 - Powder dosing hopper (rotary servo)
 *
 * Real-time cycle: 1ms (1kHz) via SOEM distributed clock synchronisation
 *
 * SECURITY OBSERVATIONS:
 * -----------------------------------------------------------------------
 * [SEC-01] EtherCAT has NO authentication mechanism. Any device physically
 *          connected to the EtherCAT segment can inject frames or modify
 *          process data. The protocol relies entirely on physical security.
 *
 * [SEC-02] EtherCAT frames are NOT encrypted. All process data (position
 *          setpoints, actual positions, control words) is transmitted in
 *          cleartext on the wire. A passive tap can observe all data.
 *
 * [SEC-03] No firmware signature verification on servo drives. A
 *          compromised engineering workstation could push malicious
 *          firmware to drives via FoE (File over EtherCAT).
 *
 * [SEC-04] The EtherCAT master runs as root with CAP_NET_RAW. If the
 *          application is compromised, the attacker gains root-level
 *          access to the BeagleBone controlling physical actuators.
 *
 * [SEC-05] No integrity check on PDO mappings. A man-in-the-middle on
 *          the EtherCAT bus could modify position setpoints in-flight,
 *          potentially causing mechanical damage or unsafe conditions.
 * -----------------------------------------------------------------------
 *
 * Build: arm-linux-gnueabihf-gcc -O2 -lsoem -lpthread -lrt -o ams500_motion motion_controller_ethercat.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <signal.h>
#include <time.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <errno.h>

/* SOEM headers */
#include "ethercat.h"       /* soem/ethercat.h - main SOEM API */
#include "ethercattype.h"
#include "ethercatmain.h"
#include "ethercatdc.h"
#include "ethercatcoe.h"
#include "ethercatpdo.h"

#define ECAT_INTERFACE      "eth1"      /* Dedicated EtherCAT NIC (TI CPSW port 1) */
#define EXPECTED_SLAVES     3
#define CYCLE_TIME_NS       1000000     /* 1ms cycle time */
#define STACK_SIZE          (64 * 1024) /* 64KB stack for RT thread */

/* Slave addresses (auto-incremented during bus scan) */
#define SLAVE_PLATFORM_Z    1   /* Beckhoff AX5206-0000 */
#define SLAVE_RECOATER_X    2   /* Beckhoff AX5106-0000 */
#define SLAVE_DOSER_ROT     3   /* Beckhoff AX5103-0000 */

/* CiA 402 control/status word bits */
#define CW_SWITCH_ON        (1 << 0)
#define CW_ENABLE_VOLTAGE   (1 << 1)
#define CW_QUICK_STOP       (1 << 2)
#define CW_ENABLE_OP        (1 << 3)
#define CW_NEW_SETPOINT     (1 << 4)
#define CW_HALT             (1 << 8)

#define SW_READY_TO_SWITCH_ON   (1 << 0)
#define SW_SWITCHED_ON          (1 << 1)
#define SW_OP_ENABLED           (1 << 2)
#define SW_FAULT                (1 << 3)
#define SW_TARGET_REACHED       (1 << 10)
#define SW_HOMING_ATTAINED      (1 << 12)

/* Motion parameters - units in encoder counts (10000 counts/mm for linear) */
#define PLATFORM_COUNTS_PER_MM  10000
#define RECOATER_COUNTS_PER_MM  10000
#define DOSER_COUNTS_PER_DEG    1000

/* PDO output structure (master -> slave) - mapped to 0x1600 RxPDO */
typedef struct __attribute__((packed)) {
    uint16_t control_word;      /* 0x6040:00 - CiA 402 control word */
    int32_t  target_position;   /* 0x607A:00 - Target position */
    int32_t  velocity_limit;    /* 0x6081:00 - Profile velocity */
    int32_t  acceleration;      /* 0x6083:00 - Profile acceleration */
    int32_t  deceleration;      /* 0x6084:00 - Profile deceleration */
    int8_t   mode_of_operation; /* 0x6060:00 - Modes of operation */
} pdo_output_t;

/* PDO input structure (slave -> master) - mapped to 0x1A00 TxPDO */
typedef struct __attribute__((packed)) {
    uint16_t status_word;       /* 0x6041:00 - CiA 402 status word */
    int32_t  actual_position;   /* 0x6064:00 - Actual position */
    int32_t  actual_velocity;   /* 0x606C:00 - Actual velocity */
    int16_t  actual_torque;     /* 0x6077:00 - Actual torque (0.1% rated) */
    uint32_t error_code;        /* 0x603F:00 - Error code */
} pdo_input_t;

/* Global state */
static volatile int g_running = 1;
static char g_io_map[4096];        /* Process data image */
static int g_expected_wkc;         /* Expected working counter */
static volatile int g_actual_wkc;

/* Shared memory for PLC communication via /dev/shm/ams500_motion */
typedef struct {
    /* Inputs from PLC (written by PLC, read by motion controller) */
    int32_t  cmd_platform_pos;      /* Target Z position in 0.001mm */
    int32_t  cmd_recoater_pos;      /* Target X position in 0.001mm */
    int32_t  cmd_doser_angle;       /* Target angle in 0.001deg */
    uint16_t cmd_flags;             /* Bit 0: enable, Bit 1: home, Bit 2: halt */

    /* Outputs to PLC (written by motion controller, read by PLC) */
    int32_t  fb_platform_pos;
    int32_t  fb_recoater_pos;
    int32_t  fb_doser_angle;
    uint16_t fb_status;             /* Bit 0: enabled, Bit 1: homed, Bit 2: fault */
    uint32_t fb_error_code;
    uint64_t cycle_count;
    uint32_t max_jitter_ns;
} shm_exchange_t;

static shm_exchange_t *g_shm = NULL;

/**
 * Signal handler for graceful shutdown.
 * Transitions drives to safe torque off before exit.
 */
static void signal_handler(int sig)
{
    printf("[MOTION] Received signal %d, initiating shutdown...\n", sig);
    g_running = 0;
}

/**
 * Configure PDO mapping for a Beckhoff AX5xxx drive.
 * Uses CoE (CANopen over EtherCAT) SDO access to set up
 * the process data objects exchanged each cycle.
 *
 * [SEC-03] SDO writes have no authentication. Any EtherCAT master
 * on the bus can reconfigure drive parameters including limits.
 */
static int configure_pdo_mapping(uint16_t slave)
{
    int retval = 0;
    uint8_t  u8val;
    uint16_t u16val;
    uint32_t u32val;
    int      wkc;

    /* Clear existing RxPDO mapping (0x1600) */
    u8val = 0;
    wkc = ec_SDOwrite(slave, 0x1600, 0x00, FALSE, sizeof(u8val), &u8val, EC_TIMEOUTRXM);
    if (wkc <= 0) { fprintf(stderr, "[MOTION] SDO write failed: slave %d, 0x1600:00\n", slave); return -1; }

    /* Map control word -> 0x1600:01 */
    u32val = 0x60400010;  /* Index 0x6040, subindex 0x00, 16 bits */
    ec_SDOwrite(slave, 0x1600, 0x01, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    /* Map target position -> 0x1600:02 */
    u32val = 0x607A0020;  /* 32 bits */
    ec_SDOwrite(slave, 0x1600, 0x02, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    /* Map profile velocity -> 0x1600:03 */
    u32val = 0x60810020;
    ec_SDOwrite(slave, 0x1600, 0x03, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    /* Map profile acceleration -> 0x1600:04 */
    u32val = 0x60830020;
    ec_SDOwrite(slave, 0x1600, 0x04, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    /* Map profile deceleration -> 0x1600:05 */
    u32val = 0x60840020;
    ec_SDOwrite(slave, 0x1600, 0x05, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    /* Map modes of operation -> 0x1600:06 */
    u32val = 0x60600008;  /* 8 bits */
    ec_SDOwrite(slave, 0x1600, 0x06, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    /* Set number of mapped objects */
    u8val = 6;
    ec_SDOwrite(slave, 0x1600, 0x00, FALSE, sizeof(u8val), &u8val, EC_TIMEOUTRXM);

    /* Configure TxPDO mapping (0x1A00) - similar pattern for inputs */
    u8val = 0;
    ec_SDOwrite(slave, 0x1A00, 0x00, FALSE, sizeof(u8val), &u8val, EC_TIMEOUTRXM);

    u32val = 0x60410010;  /* Status word, 16 bits */
    ec_SDOwrite(slave, 0x1A00, 0x01, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    u32val = 0x60640020;  /* Actual position, 32 bits */
    ec_SDOwrite(slave, 0x1A00, 0x02, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    u32val = 0x606C0020;  /* Actual velocity, 32 bits */
    ec_SDOwrite(slave, 0x1A00, 0x03, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    u32val = 0x60770010;  /* Actual torque, 16 bits */
    ec_SDOwrite(slave, 0x1A00, 0x04, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    u32val = 0x603F0020;  /* Error code, 32 bits */
    ec_SDOwrite(slave, 0x1A00, 0x05, FALSE, sizeof(u32val), &u32val, EC_TIMEOUTRXM);

    u8val = 5;
    ec_SDOwrite(slave, 0x1A00, 0x00, FALSE, sizeof(u8val), &u8val, EC_TIMEOUTRXM);

    printf("[MOTION] PDO mapping configured for slave %d\n", slave);
    return 0;
}

/**
 * CiA 402 state machine transition.
 * Transitions drive from any state to Operation Enabled.
 * Returns 0 on success, -1 on timeout.
 */
static int drive_enable(uint16_t slave, pdo_output_t *out, pdo_input_t *in)
{
    int timeout = 2000;  /* 2 second timeout (2000 cycles at 1ms) */

    /* Fault reset if in fault state */
    if (in->status_word & SW_FAULT) {
        out->control_word = 0x0080;  /* Fault reset */
        while ((in->status_word & SW_FAULT) && timeout-- > 0) {
            ec_send_processdata();
            g_actual_wkc = ec_receive_processdata(EC_TIMEOUTRET);
        }
        if (timeout <= 0) return -1;
    }

    /* Shutdown: transition to Ready to Switch On */
    out->control_word = CW_QUICK_STOP | CW_ENABLE_VOLTAGE;  /* 0x0006 */
    timeout = 500;
    while (!(in->status_word & SW_READY_TO_SWITCH_ON) && timeout-- > 0) {
        ec_send_processdata();
        g_actual_wkc = ec_receive_processdata(EC_TIMEOUTRET);
    }

    /* Switch On */
    out->control_word = CW_SWITCH_ON | CW_QUICK_STOP | CW_ENABLE_VOLTAGE;  /* 0x0007 */
    timeout = 500;
    while (!(in->status_word & SW_SWITCHED_ON) && timeout-- > 0) {
        ec_send_processdata();
        g_actual_wkc = ec_receive_processdata(EC_TIMEOUTRET);
    }

    /* Enable Operation */
    out->control_word = CW_SWITCH_ON | CW_QUICK_STOP | CW_ENABLE_VOLTAGE | CW_ENABLE_OP;  /* 0x000F */
    timeout = 500;
    while (!(in->status_word & SW_OP_ENABLED) && timeout-- > 0) {
        ec_send_processdata();
        g_actual_wkc = ec_receive_processdata(EC_TIMEOUTRET);
    }

    if (timeout <= 0) {
        fprintf(stderr, "[MOTION] Drive enable timeout on slave %d, status=0x%04X\n",
                slave, in->status_word);
        return -1;
    }

    printf("[MOTION] Slave %d enabled, status=0x%04X\n", slave, in->status_word);
    return 0;
}

/**
 * Execute homing sequence for a single axis.
 * Uses CiA 402 homing mode (mode 6) with method 35 (current position as home).
 * Platform Z uses method 1 (home on negative limit switch).
 */
static int execute_homing(uint16_t slave, pdo_output_t *out, pdo_input_t *in,
                          int8_t homing_method)
{
    int timeout = 30000;  /* 30 second timeout for homing */

    out->mode_of_operation = 6;  /* Homing mode */
    out->control_word = CW_SWITCH_ON | CW_QUICK_STOP | CW_ENABLE_VOLTAGE | CW_ENABLE_OP;

    /* Set homing method via SDO */
    ec_SDOwrite(slave, 0x6098, 0x00, FALSE, sizeof(homing_method), &homing_method, EC_TIMEOUTRXM);

    /* Set homing speed */
    int32_t homing_speed = 50000;  /* 5mm/s for platform, safe speed */
    ec_SDOwrite(slave, 0x6099, 0x01, FALSE, sizeof(homing_speed), &homing_speed, EC_TIMEOUTRXM);
    homing_speed = 10000;  /* 1mm/s for final approach */
    ec_SDOwrite(slave, 0x6099, 0x02, FALSE, sizeof(homing_speed), &homing_speed, EC_TIMEOUTRXM);

    /* Start homing - set bit 4 of control word */
    out->control_word |= CW_NEW_SETPOINT;  /* 0x001F */

    while (!(in->status_word & SW_HOMING_ATTAINED) && timeout-- > 0) {
        ec_send_processdata();
        g_actual_wkc = ec_receive_processdata(EC_TIMEOUTRET);
        if (in->status_word & SW_FAULT) {
            fprintf(stderr, "[MOTION] Fault during homing, slave %d, error=0x%08X\n",
                    slave, in->error_code);
            return -1;
        }
    }

    if (timeout <= 0) {
        fprintf(stderr, "[MOTION] Homing timeout on slave %d\n", slave);
        return -1;
    }

    /* Switch to Profile Position mode for normal operation */
    out->mode_of_operation = 1;  /* Profile Position mode */
    printf("[MOTION] Slave %d homing complete, position=%d\n", slave, in->actual_position);
    return 0;
}

/**
 * Real-time cyclic task.
 * Executes at 1ms intervals with SCHED_FIFO priority 99.
 * Reads commands from shared memory, updates servo targets,
 * exchanges process data with EtherCAT slaves.
 *
 * [SEC-04] This thread runs as root. Memory is locked to prevent
 * page faults. No privilege separation from the motion control loop.
 */
static void *realtime_cycle(void *arg)
{
    struct timespec ts, ts_ref, ts_start, ts_end;
    int64_t jitter;
    uint32_t max_jitter = 0;

    pdo_output_t *out_platform = (pdo_output_t *)ec_slave[SLAVE_PLATFORM_Z].outputs;
    pdo_input_t  *in_platform  = (pdo_input_t *)ec_slave[SLAVE_PLATFORM_Z].inputs;
    pdo_output_t *out_recoater = (pdo_output_t *)ec_slave[SLAVE_RECOATER_X].outputs;
    pdo_input_t  *in_recoater  = (pdo_input_t *)ec_slave[SLAVE_RECOATER_X].inputs;
    pdo_output_t *out_doser    = (pdo_output_t *)ec_slave[SLAVE_DOSER_ROT].outputs;
    pdo_input_t  *in_doser     = (pdo_input_t *)ec_slave[SLAVE_DOSER_ROT].inputs;

    /* Set default motion parameters for all axes */
    out_platform->velocity_limit = 100000;   /* 10mm/s max */
    out_platform->acceleration   = 500000;   /* 50mm/s^2 */
    out_platform->deceleration   = 500000;
    out_platform->mode_of_operation = 1;     /* Profile Position */

    out_recoater->velocity_limit = 1500000;  /* 150mm/s max */
    out_recoater->acceleration   = 5000000;  /* 500mm/s^2 */
    out_recoater->deceleration   = 5000000;
    out_recoater->mode_of_operation = 1;

    out_doser->velocity_limit = 360000;      /* 360deg/s */
    out_doser->acceleration   = 1000000;
    out_doser->deceleration   = 1000000;
    out_doser->mode_of_operation = 1;

    clock_gettime(CLOCK_MONOTONIC, &ts);

    while (g_running) {
        /* Calculate next wakeup time */
        ts.tv_nsec += CYCLE_TIME_NS;
        if (ts.tv_nsec >= 1000000000L) {
            ts.tv_nsec -= 1000000000L;
            ts.tv_sec++;
        }

        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, NULL);

        clock_gettime(CLOCK_MONOTONIC, &ts_start);

        /* --- Read commands from shared memory --- */
        if (g_shm != NULL && (g_shm->cmd_flags & 0x01)) {
            /* Convert from 0.001mm to encoder counts */
            out_platform->target_position = (g_shm->cmd_platform_pos * PLATFORM_COUNTS_PER_MM) / 1000;
            out_recoater->target_position = (g_shm->cmd_recoater_pos * RECOATER_COUNTS_PER_MM) / 1000;
            out_doser->target_position    = (g_shm->cmd_doser_angle * DOSER_COUNTS_PER_DEG) / 1000;

            /* Set new setpoint bit to trigger motion */
            out_platform->control_word |= CW_NEW_SETPOINT;
            out_recoater->control_word |= CW_NEW_SETPOINT;
            out_doser->control_word    |= CW_NEW_SETPOINT;

            /* Halt command */
            if (g_shm->cmd_flags & 0x04) {
                out_platform->control_word |= CW_HALT;
                out_recoater->control_word |= CW_HALT;
                out_doser->control_word    |= CW_HALT;
            }
        }

        /* --- Exchange process data with slaves --- */
        /* [SEC-02] All data below is transmitted unencrypted on the wire */
        ec_send_processdata();
        g_actual_wkc = ec_receive_processdata(EC_TIMEOUTRET);

        /* Verify working counter - detects missing/added slaves */
        /* [SEC-05] WKC only detects frame loss, not modification */
        if (g_actual_wkc < g_expected_wkc) {
            fprintf(stderr, "[MOTION] WKC mismatch: expected=%d, actual=%d\n",
                    g_expected_wkc, g_actual_wkc);
            /* Do NOT immediately halt - could be transient */
            /* TODO: implement consecutive-miss counter for robust detection */
        }

        /* --- Update feedback to shared memory --- */
        if (g_shm != NULL) {
            g_shm->fb_platform_pos = (in_platform->actual_position * 1000) / PLATFORM_COUNTS_PER_MM;
            g_shm->fb_recoater_pos = (in_recoater->actual_position * 1000) / RECOATER_COUNTS_PER_MM;
            g_shm->fb_doser_angle  = (in_doser->actual_position * 1000) / DOSER_COUNTS_PER_DEG;

            g_shm->fb_status = 0;
            if (in_platform->status_word & SW_OP_ENABLED) g_shm->fb_status |= 0x01;
            if (in_platform->status_word & SW_HOMING_ATTAINED) g_shm->fb_status |= 0x02;
            if (in_platform->status_word & SW_FAULT) g_shm->fb_status |= 0x04;

            g_shm->fb_error_code = in_platform->error_code;
            g_shm->cycle_count++;
            g_shm->max_jitter_ns = max_jitter;
        }

        /* Jitter measurement */
        clock_gettime(CLOCK_MONOTONIC, &ts_end);
        jitter = (ts_end.tv_sec - ts_start.tv_sec) * 1000000000LL +
                 (ts_end.tv_nsec - ts_start.tv_nsec);
        if ((uint32_t)jitter > max_jitter) {
            max_jitter = (uint32_t)jitter;
        }

        /* Toggle new setpoint bit for next cycle (edge-triggered on drives) */
        out_platform->control_word &= ~CW_NEW_SETPOINT;
        out_recoater->control_word &= ~CW_NEW_SETPOINT;
        out_doser->control_word    &= ~CW_NEW_SETPOINT;
    }

    /* Shutdown: disable all drives */
    out_platform->control_word = 0x0000;  /* Quick stop & disable */
    out_recoater->control_word = 0x0000;
    out_doser->control_word    = 0x0000;
    ec_send_processdata();

    printf("[MOTION] Real-time cycle stopped. Total cycles: %lu, max jitter: %u ns\n",
           g_shm ? g_shm->cycle_count : 0, max_jitter);

    return NULL;
}

/**
 * Main entry point.
 * Initialises EtherCAT master, configures slaves, starts RT thread.
 */
int main(int argc, char *argv[])
{
    int slave_count;
    pthread_t rt_thread;
    pthread_attr_t rt_attr;
    struct sched_param rt_param;

    printf("AMS-500 EtherCAT Motion Controller v2.1.0\n");
    printf("SOEM v%d.%d.%d\n", SOEM_VERSION_MAJOR, SOEM_VERSION_MINOR, SOEM_VERSION_PATCH);

    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    /* Lock all memory to prevent page faults in RT context */
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("[MOTION] mlockall failed (are we running as root?)");
        /* [SEC-04] Requires root privileges for real-time operation */
        return 1;
    }

    /* Initialise SOEM */
    /* [SEC-01] Raw socket access - no authentication of master identity */
    if (!ec_init(ECAT_INTERFACE)) {
        fprintf(stderr, "[MOTION] Failed to initialise EtherCAT on %s\n", ECAT_INTERFACE);
        fprintf(stderr, "[MOTION] Ensure interface exists and we have CAP_NET_RAW\n");
        return 1;
    }

    printf("[MOTION] EtherCAT master initialised on %s\n", ECAT_INTERFACE);

    /* Scan bus and auto-configure slaves */
    slave_count = ec_config_init(FALSE);
    if (slave_count != EXPECTED_SLAVES) {
        fprintf(stderr, "[MOTION] Expected %d slaves, found %d\n", EXPECTED_SLAVES, slave_count);
        if (slave_count == 0) {
            ec_close();
            return 1;
        }
        fprintf(stderr, "[MOTION] Continuing with %d slaves (degraded mode)\n", slave_count);
    }

    printf("[MOTION] %d EtherCAT slaves found:\n", slave_count);
    for (int i = 1; i <= slave_count; i++) {
        printf("  Slave %d: %s (VendorID=0x%08X, ProductCode=0x%08X)\n",
               i, ec_slave[i].name,
               (unsigned int)ec_slave[i].eep_man,
               (unsigned int)ec_slave[i].eep_id);
    }

    /* Configure PDO mappings for each drive */
    for (int i = 1; i <= slave_count; i++) {
        if (configure_pdo_mapping(i) != 0) {
            fprintf(stderr, "[MOTION] PDO configuration failed for slave %d\n", i);
            ec_close();
            return 1;
        }
    }

    /* Map process data to IO buffer */
    ec_config_map(&g_io_map);
    ec_configdc();

    printf("[MOTION] Process data mapped. IO map size: %d bytes\n", (int)sizeof(g_io_map));

    /* Calculate expected working counter */
    g_expected_wkc = (ec_group[0].outputsWKC * 2) + ec_group[0].inputsWKC;
    printf("[MOTION] Expected WKC: %d\n", g_expected_wkc);

    /* Transition all slaves to SAFE-OP */
    ec_statecheck(0, EC_STATE_SAFE_OP, EC_TIMEOUTSTATE * 4);
    if (ec_slave[0].state != EC_STATE_SAFE_OP) {
        fprintf(stderr, "[MOTION] Not all slaves reached SAFE-OP\n");
        for (int i = 1; i <= slave_count; i++) {
            if (ec_slave[i].state != EC_STATE_SAFE_OP) {
                fprintf(stderr, "  Slave %d state: 0x%02X, AL status: 0x%04X\n",
                        i, ec_slave[i].state, ec_slave[i].ALstatuscode);
            }
        }
        ec_close();
        return 1;
    }

    /* Transition to OP */
    ec_slave[0].state = EC_STATE_OPERATIONAL;
    ec_send_processdata();
    ec_receive_processdata(EC_TIMEOUTRET);
    ec_writestate(0);

    /* Wait for OP state */
    int timeout = 200;  /* 200 * 50ms = 10 seconds */
    do {
        ec_send_processdata();
        ec_receive_processdata(EC_TIMEOUTRET);
        ec_statecheck(0, EC_STATE_OPERATIONAL, 50000);
    } while (ec_slave[0].state != EC_STATE_OPERATIONAL && --timeout > 0);

    if (ec_slave[0].state != EC_STATE_OPERATIONAL) {
        fprintf(stderr, "[MOTION] Failed to reach OP state\n");
        ec_close();
        return 1;
    }

    printf("[MOTION] All slaves in OPERATIONAL state\n");

    /* Create real-time thread */
    pthread_attr_init(&rt_attr);
    pthread_attr_setstacksize(&rt_attr, STACK_SIZE);
    pthread_attr_setschedpolicy(&rt_attr, SCHED_FIFO);
    rt_param.sched_priority = 99;  /* Maximum RT priority */
    pthread_attr_setschedparam(&rt_attr, &rt_param);
    pthread_attr_setinheritsched(&rt_attr, PTHREAD_EXPLICIT_SCHED);

    if (pthread_create(&rt_thread, &rt_attr, realtime_cycle, NULL) != 0) {
        perror("[MOTION] Failed to create RT thread");
        ec_close();
        return 1;
    }

    printf("[MOTION] Real-time cycle started (1ms / 1kHz)\n");
    printf("[MOTION] Press Ctrl+C to stop\n");

    /* Main thread monitors slave state and handles recovery */
    while (g_running) {
        struct timespec sleep_ts = { .tv_sec = 0, .tv_nsec = 100000000 };  /* 100ms */
        nanosleep(&sleep_ts, NULL);

        /* Check for slave state changes */
        if (g_actual_wkc < g_expected_wkc) {
            ec_readstate();
            for (int i = 1; i <= slave_count; i++) {
                if (ec_slave[i].state != EC_STATE_OPERATIONAL) {
                    fprintf(stderr, "[MOTION] Slave %d dropped from OP (state=0x%02X, AL=0x%04X)\n",
                            i, ec_slave[i].state, ec_slave[i].ALstatuscode);

                    /* Attempt automatic recovery */
                    ec_slave[i].state = EC_STATE_OPERATIONAL;
                    ec_writestate(i);
                }
            }
        }
    }

    /* Cleanup */
    pthread_join(rt_thread, NULL);

    /* Return all slaves to INIT state */
    ec_slave[0].state = EC_STATE_INIT;
    ec_writestate(0);
    ec_statecheck(0, EC_STATE_INIT, EC_TIMEOUTSTATE);

    ec_close();
    printf("[MOTION] EtherCAT master closed. Exiting.\n");

    return 0;
}
