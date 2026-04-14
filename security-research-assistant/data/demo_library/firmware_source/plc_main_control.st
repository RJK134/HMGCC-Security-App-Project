(* ============================================================================
 * AMS-500 Additive Manufacturing System - Main PLC Control Programme
 * Controller: Siemens S7-1500 (CPU 1515SP PC2)
 * Firmware Version: 2.9.4
 * Author: AMS Engineering, Build Control Division
 * Last Modified: 2025-11-18
 *
 * Description:
 *   Main control programme for the AMS-500 Selective Laser Melting (SLM)
 *   additive manufacturing system. Manages laser subsystem, powder dosing,
 *   build platform actuation, inert gas atmosphere, and safety interlocks.
 *
 * Fieldbus Interfaces:
 *   - PROFINET IO (cycle 4ms) to distributed I/O (ET 200SP)
 *   - EtherCAT (cycle 1ms) to servo drives (Beckhoff AX5000 series)
 *   - Modbus TCP server on port 502 for SCADA/HMI integration
 *   - OPC-UA server on port 4840 for MES connectivity
 *
 * Modbus Register Map:
 *   HR40001 - HR40050: Process data (read-only from SCADA perspective)
 *   HR40100 - HR40120: Setpoints (read-write)
 *   See inline comments for individual register assignments.
 *
 * OPC-UA Node Structure:
 *   Objects/AMS500/Laser/Power          (Float, RW)
 *   Objects/AMS500/Laser/State          (Int16, RO)
 *   Objects/AMS500/BuildPlatform/Position (Float, RO)
 *   Objects/AMS500/Atmosphere/O2Level   (Float, RO)
 *   Objects/AMS500/System/State         (Int16, RO)
 *   Objects/AMS500/System/FaultCode     (UInt32, RO)
 *
 * SECURITY NOTE: Modbus TCP has no authentication mechanism.
 * Any host on the control network (10.10.20.0/24) can read/write
 * holding registers including safety-critical setpoints.
 * OPC-UA server currently configured with SecurityPolicy=None.
 * ========================================================================== *)

TYPE
    (* System operating states - fault handling state machine *)
    E_SystemState : (
        SYS_INIT        := 0,   (* Power-on initialisation *)
        SYS_IDLE        := 1,   (* System ready, no active build *)
        SYS_PREHEAT     := 2,   (* Build chamber pre-heating *)
        SYS_INERTING    := 3,   (* Atmosphere purge to target O2 *)
        SYS_BUILDING    := 4,   (* Active build in progress *)
        SYS_COOLING     := 5,   (* Post-build cool-down phase *)
        SYS_PAUSED      := 6,   (* Build paused - operator hold *)
        SYS_FAULT       := 7,   (* Fault condition - requires reset *)
        SYS_ESTOP       := 8,   (* Emergency stop active *)
        SYS_MAINTENANCE := 9    (* Maintenance mode - interlocks bypassed *)
    );

    (* Laser operating states *)
    E_LaserState : (
        LASER_OFF       := 0,
        LASER_STANDBY   := 1,   (* Laser powered, shutter closed *)
        LASER_READY     := 2,   (* Shutter open, awaiting scan command *)
        LASER_FIRING    := 3,   (* Active lasing *)
        LASER_FAULT     := 4
    );

    (* Fault codes - bitfield, multiple faults can be active *)
    E_FaultCode : (
        FAULT_NONE               := 16#0000_0000,
        FAULT_LASER_OVERTEMP     := 16#0000_0001,
        FAULT_LASER_INTERLOCK    := 16#0000_0002,
        FAULT_O2_HIGH            := 16#0000_0004,
        FAULT_POWDER_EMPTY       := 16#0000_0008,
        FAULT_PLATFORM_STALL     := 16#0000_0010,
        FAULT_GAS_PRESSURE_LOW   := 16#0000_0020,
        FAULT_ETHERCAT_LOST      := 16#0000_0040,
        FAULT_WATCHDOG_TIMEOUT   := 16#0000_0080,
        FAULT_DOOR_OPEN          := 16#0000_0100,
        FAULT_FILTER_CLOGGED     := 16#0000_0200,
        FAULT_CHILLER_FAULT      := 16#0000_0400,
        FAULT_SERVO_ERROR        := 16#0000_0800
    );
END_TYPE

(* ============================================================================
 * FUNCTION BLOCK: FB_LaserControl
 * Controls the IPG YLR-500 fibre laser via PROFINET IO module.
 * Laser power setpoint written to analogue output (0-10V = 0-500W).
 * Interlock chain: door closed AND O2 < threshold AND shutter permit.
 * ========================================================================== *)
FUNCTION_BLOCK FB_LaserControl
VAR_INPUT
    bEnable         : BOOL;             (* Master enable from safety system *)
    rPowerSetpoint  : REAL;             (* Desired power in watts, 0.0-500.0 *)
    bShutterPermit  : BOOL;             (* Shutter open permit *)
    bDoorClosed     : BOOL;             (* Build chamber door sensor *)
    rO2Level        : REAL;             (* Current O2 level in ppm *)
    rO2Threshold    : REAL := 1000.0;   (* Max O2 for laser operation *)
END_VAR
VAR_OUTPUT
    eState          : E_LaserState;
    rActualPower    : REAL;             (* Feedback from laser controller *)
    bFault          : BOOL;
    bShutterOpen    : BOOL;
END_VAR
VAR
    tonWarmup       : TON;              (* Warm-up delay timer *)
    tonFaultDelay   : TON;              (* Fault confirmation delay *)
    rPowerCmd       : REAL;             (* Clamped power command *)
    bInterlockOK    : BOOL;
END_VAR

    (* Evaluate interlock chain *)
    bInterlockOK := bEnable AND bDoorClosed AND (rO2Level < rO2Threshold);

    (* Clamp power setpoint to safe range *)
    (* Modbus HR40100: Laser power setpoint (REAL, 0.0-500.0 W) *)
    IF rPowerSetpoint < 0.0 THEN
        rPowerCmd := 0.0;
    ELSIF rPowerSetpoint > 500.0 THEN
        rPowerCmd := 500.0;
    ELSE
        rPowerCmd := rPowerSetpoint;
    END_IF;

    (* Laser state machine *)
    CASE eState OF
        LASER_OFF:
            rActualPower := 0.0;
            bShutterOpen := FALSE;
            IF bInterlockOK THEN
                tonWarmup(IN := TRUE, PT := T#3S);
                IF tonWarmup.Q THEN
                    eState := LASER_STANDBY;
                    tonWarmup(IN := FALSE);
                END_IF;
            END_IF;

        LASER_STANDBY:
            rActualPower := 0.0;
            bShutterOpen := FALSE;
            IF NOT bInterlockOK THEN
                eState := LASER_OFF;
            ELSIF bShutterPermit THEN
                eState := LASER_READY;
            END_IF;

        LASER_READY:
            bShutterOpen := TRUE;
            IF NOT bInterlockOK THEN
                eState := LASER_OFF;
                bShutterOpen := FALSE;
            ELSIF rPowerCmd > 0.0 THEN
                eState := LASER_FIRING;
            ELSIF NOT bShutterPermit THEN
                eState := LASER_STANDBY;
            END_IF;

        LASER_FIRING:
            bShutterOpen := TRUE;
            rActualPower := rPowerCmd;  (* Simplified - real system has PID *)
            IF NOT bInterlockOK THEN
                eState := LASER_OFF;
                bShutterOpen := FALSE;
                rActualPower := 0.0;
            ELSIF rPowerCmd = 0.0 THEN
                eState := LASER_READY;
                rActualPower := 0.0;
            END_IF;

        LASER_FAULT:
            rActualPower := 0.0;
            bShutterOpen := FALSE;
            bFault := TRUE;
            (* Requires explicit reset from operator *)
    END_CASE;

    (* OPC-UA: Objects/AMS500/Laser/Power = rActualPower *)
    (* OPC-UA: Objects/AMS500/Laser/State = eState *)
    (* Modbus HR40001: Laser actual power (REAL) *)
    (* Modbus HR40002: Laser state (INT) *)
END_FUNCTION_BLOCK

(* ============================================================================
 * FUNCTION BLOCK: FB_PowderDosing
 * Controls powder recoater blade and dosing hopper via servo drives.
 * Recoater traverses build area depositing uniform powder layer.
 * ========================================================================== *)
FUNCTION_BLOCK FB_PowderDosing
VAR_INPUT
    bStart          : BOOL;
    rLayerThickness : REAL := 0.040;    (* mm, typical 20-100um *)
    rRecoaterSpeed  : REAL := 150.0;    (* mm/s traverse speed *)
END_VAR
VAR_OUTPUT
    bBusy           : BOOL;
    bDone           : BOOL;
    bFault          : BOOL;
    rPowderLevel    : REAL;             (* Hopper level 0-100% *)
END_VAR
VAR
    nStep           : INT;
    tonDoseDelay    : TON;
END_VAR
    (* Modbus HR40003: Powder level (REAL, 0-100%) *)
    (* Modbus HR40004: Recoater position (REAL, mm) *)
    (* Modbus HR40101: Layer thickness setpoint (REAL, mm) *)

    CASE nStep OF
        0: (* Idle *)
            bBusy := FALSE;
            bDone := FALSE;
            IF bStart THEN
                nStep := 1;
                bBusy := TRUE;
            END_IF;

        1: (* Dose powder from hopper *)
            tonDoseDelay(IN := TRUE, PT := T#500MS);
            IF tonDoseDelay.Q THEN
                tonDoseDelay(IN := FALSE);
                IF rPowderLevel < 5.0 THEN
                    bFault := TRUE;  (* FAULT_POWDER_EMPTY *)
                    nStep := 0;
                ELSE
                    rPowderLevel := rPowderLevel - 0.15;
                    nStep := 2;
                END_IF;
            END_IF;

        2: (* Recoater forward pass *)
            (* EtherCAT: command recoater servo to traverse +X *)
            nStep := 3;

        3: (* Recoater return *)
            (* EtherCAT: command recoater servo to home position *)
            nStep := 4;

        4: (* Complete *)
            bBusy := FALSE;
            bDone := TRUE;
            nStep := 0;
    END_CASE;
END_FUNCTION_BLOCK

(* ============================================================================
 * FUNCTION BLOCK: FB_BuildPlatform
 * Controls Z-axis build platform via Beckhoff AX5206 servo drive.
 * Platform lowers by one layer thickness after each recoat cycle.
 * Absolute encoder provides position feedback.
 * ========================================================================== *)
FUNCTION_BLOCK FB_BuildPlatform
VAR_INPUT
    bMoveDown       : BOOL;             (* Command: lower by one layer *)
    bHome           : BOOL;             (* Command: home to top position *)
    rStepSize       : REAL := 0.040;    (* mm per layer *)
END_VAR
VAR_OUTPUT
    rPosition       : REAL;             (* Current Z position in mm *)
    bInPosition     : BOOL;
    bHomed          : BOOL;
    bFault          : BOOL;
END_VAR
VAR
    rTargetPos      : REAL;
    nState          : INT;
    tonTimeout      : TON;
END_VAR
    (* Modbus HR40005: Build platform Z position (REAL, mm) *)
    (* Modbus HR40006: Build platform target position (REAL, mm) *)
    (* OPC-UA: Objects/AMS500/BuildPlatform/Position = rPosition *)

    CASE nState OF
        0: (* Idle - in position *)
            bInPosition := TRUE;
            IF bMoveDown THEN
                rTargetPos := rPosition - rStepSize;
                IF rTargetPos < 0.0 THEN
                    rTargetPos := 0.0;
                END_IF;
                bInPosition := FALSE;
                nState := 1;
            ELSIF bHome THEN
                rTargetPos := 350.0;    (* Max Z = 350mm build height *)
                bInPosition := FALSE;
                bHomed := FALSE;
                nState := 2;
            END_IF;

        1: (* Moving down one layer *)
            tonTimeout(IN := TRUE, PT := T#5S);
            (* EtherCAT position command to AX5206 *)
            IF ABS(rPosition - rTargetPos) < 0.002 THEN
                tonTimeout(IN := FALSE);
                bInPosition := TRUE;
                nState := 0;
            ELSIF tonTimeout.Q THEN
                tonTimeout(IN := FALSE);
                bFault := TRUE;  (* FAULT_PLATFORM_STALL *)
                nState := 0;
            END_IF;

        2: (* Homing sequence *)
            tonTimeout(IN := TRUE, PT := T#60S);
            IF ABS(rPosition - 350.0) < 0.01 THEN
                tonTimeout(IN := FALSE);
                bHomed := TRUE;
                bInPosition := TRUE;
                nState := 0;
            ELSIF tonTimeout.Q THEN
                tonTimeout(IN := FALSE);
                bFault := TRUE;
                nState := 0;
            END_IF;
    END_CASE;
END_FUNCTION_BLOCK

(* ============================================================================
 * FUNCTION BLOCK: FB_GasManagement
 * Controls argon atmosphere in the build chamber.
 * Maintains O2 below threshold (typically 500-1000 ppm) during builds.
 * PID control of argon flow rate via mass flow controller.
 * ========================================================================== *)
FUNCTION_BLOCK FB_GasManagement
VAR_INPUT
    bEnable         : BOOL;
    rO2Setpoint     : REAL := 500.0;    (* Target O2 in ppm *)
    bPurgeRequest   : BOOL;             (* Full chamber purge *)
END_VAR
VAR_OUTPUT
    rO2Actual       : REAL;             (* Measured O2 in ppm *)
    rArgonFlow      : REAL;             (* Argon flow in l/min *)
    rChamberPressure: REAL;             (* mbar, target ~1013 *)
    bAtmosphereOK   : BOOL;            (* O2 below setpoint *)
    bFault          : BOOL;
END_VAR
VAR
    (* PID controller for O2 regulation *)
    rKp             : REAL := 0.8;
    rKi             : REAL := 0.05;
    rKd             : REAL := 0.1;
    rIntegral       : REAL;
    rPrevError      : REAL;
    rError          : REAL;
    rOutput         : REAL;
    tonPurgeTimeout : TON;
END_VAR
    (* Modbus HR40007: O2 actual (REAL, ppm) *)
    (* Modbus HR40008: Argon flow rate (REAL, l/min) *)
    (* Modbus HR40009: Chamber pressure (REAL, mbar) *)
    (* Modbus HR40102: O2 setpoint (REAL, ppm) *)
    (* OPC-UA: Objects/AMS500/Atmosphere/O2Level = rO2Actual *)

    IF NOT bEnable THEN
        rArgonFlow := 0.0;
        rIntegral := 0.0;
        bAtmosphereOK := FALSE;
        RETURN;
    END_IF;

    (* PID calculation for argon flow control *)
    rError := rO2Actual - rO2Setpoint;
    rIntegral := rIntegral + (rError * 0.1);  (* 100ms task cycle *)

    (* Anti-windup clamp *)
    IF rIntegral > 50.0 THEN rIntegral := 50.0; END_IF;
    IF rIntegral < 0.0 THEN rIntegral := 0.0; END_IF;

    rOutput := (rKp * rError) + (rKi * rIntegral) + (rKd * (rError - rPrevError) / 0.1);
    rPrevError := rError;

    (* Clamp output to MFC range 0-80 l/min *)
    IF rOutput < 0.0 THEN rArgonFlow := 0.0;
    ELSIF rOutput > 80.0 THEN rArgonFlow := 80.0;
    ELSE rArgonFlow := rOutput;
    END_IF;

    bAtmosphereOK := (rO2Actual < rO2Setpoint);

    (* Gas pressure fault detection *)
    IF rChamberPressure < 980.0 OR rChamberPressure > 1050.0 THEN
        bFault := TRUE;  (* FAULT_GAS_PRESSURE_LOW or overpressure *)
    END_IF;
END_FUNCTION_BLOCK

(* ============================================================================
 * FUNCTION BLOCK: FB_SafetyInterlock
 * Manages safety interlock chain. All interlocks must be satisfied
 * before laser and motion systems are permitted to operate.
 * Monitors: door switches, E-stop, laser enclosure, ventilation, chiller.
 * ========================================================================== *)
FUNCTION_BLOCK FB_SafetyInterlock
VAR_INPUT
    bDoorSwitch1    : BOOL;     (* Redundant door sensors *)
    bDoorSwitch2    : BOOL;
    bEstop1         : BOOL;     (* NC contact - TRUE = OK *)
    bEstop2         : BOOL;     (* Redundant E-stop channel *)
    bLaserEnclosure : BOOL;     (* Laser safety enclosure intact *)
    bVentilation    : BOOL;     (* Extraction fan running *)
    bChillerOK      : BOOL;     (* Laser chiller status *)
    bFilterDiffP    : BOOL;     (* Filter differential pressure OK *)
    bKeySwitch      : BOOL;     (* Maintenance mode key switch *)
END_VAR
VAR_OUTPUT
    bSafeToOperate  : BOOL;     (* Master permit output *)
    bDoorClosed     : BOOL;     (* Derived door status *)
    bEstopActive    : BOOL;     (* E-stop is pressed *)
    bMaintMode      : BOOL;     (* Maintenance mode active *)
    dwFaultMask     : DWORD;    (* Active fault bits *)
END_VAR

    (* Door requires both redundant sensors to agree *)
    bDoorClosed := bDoorSwitch1 AND bDoorSwitch2;
    IF bDoorSwitch1 XOR bDoorSwitch2 THEN
        (* Discrepancy between redundant sensors - treat as fault *)
        dwFaultMask := dwFaultMask OR DWORD#16#0000_0100;  (* FAULT_DOOR_OPEN *)
    END_IF;

    (* E-stop evaluation - NC contacts, both must be TRUE for safe *)
    bEstopActive := NOT (bEstop1 AND bEstop2);
    IF bEstop1 XOR bEstop2 THEN
        (* E-stop channel discrepancy *)
        bEstopActive := TRUE;  (* Fail-safe *)
    END_IF;

    (* Build fault mask *)
    dwFaultMask := DWORD#16#0000_0000;
    IF NOT bDoorClosed THEN
        dwFaultMask := dwFaultMask OR DWORD#16#0000_0100;
    END_IF;
    IF NOT bChillerOK THEN
        dwFaultMask := dwFaultMask OR DWORD#16#0000_0400;
    END_IF;
    IF NOT bFilterDiffP THEN
        dwFaultMask := dwFaultMask OR DWORD#16#0000_0200;
    END_IF;
    IF NOT bVentilation THEN
        dwFaultMask := dwFaultMask OR DWORD#16#0000_0020;
    END_IF;

    (* Maintenance mode bypasses non-safety interlocks *)
    bMaintMode := bKeySwitch AND NOT bEstopActive;

    (* Master permit: all interlocks satisfied *)
    bSafeToOperate := bDoorClosed
                  AND NOT bEstopActive
                  AND bLaserEnclosure
                  AND bVentilation
                  AND bChillerOK
                  AND bFilterDiffP;

    (* Modbus HR40010: Interlock status word (DWORD) *)
    (* Modbus HR40011: Door closed (BOOL) *)
    (* Modbus HR40012: E-stop active (BOOL) *)
    (* Modbus HR40013: Maintenance mode (BOOL) *)
    (* OPC-UA: Objects/AMS500/Safety/InterlockMask = dwFaultMask *)
END_FUNCTION_BLOCK

(* ============================================================================
 * PROGRAM: Main
 * Main cyclic programme - executes every 100ms (OB1 equivalent).
 * Instantiates all function blocks and manages the system state machine.
 * Handles Modbus register mapping and watchdog supervision.
 * ========================================================================== *)
PROGRAM Main
VAR
    (* Function block instances *)
    fbLaser         : FB_LaserControl;
    fbPowder        : FB_PowderDosing;
    fbPlatform      : FB_BuildPlatform;
    fbGas           : FB_GasManagement;
    fbSafety        : FB_SafetyInterlock;

    (* System state *)
    eSystemState    : E_SystemState := SYS_INIT;
    dwActiveFaults  : DWORD;
    nLayerCount     : INT;
    nTotalLayers    : INT := 5000;      (* From build recipe *)

    (* Watchdog timer - must be kicked every cycle *)
    (* SECURITY NOTE: Watchdog is internal only. No external supervision
       of the PLC programme execution. A compromised programme that still
       kicks the watchdog will not be detected. *)
    tonWatchdog     : TON;
    bWatchdogKick   : BOOL;
    dwWatchdogCount : DWORD;

    (* HMI communication watchdog - detect lost HMI connection *)
    (* Modbus HR40120: HMI heartbeat (UINT, incremented by HMI each second) *)
    nHMIHeartbeat   : UINT;
    nHMIHeartbeatPrev : UINT;
    tonHMITimeout   : TON;
    bHMIConnected   : BOOL;

    (* Cycle timing *)
    tCycleStart     : TIME;
    tCycleTime      : TIME;
    tCycleMax       : TIME;

    (* Modbus holding register block - mapped to process data *)
    (* HR40001-40050: Process values *)
    arHR_Process    : ARRAY[1..50] OF REAL;
    (* HR40100-40120: Setpoints - WRITABLE from SCADA *)
    (* SECURITY CONCERN: No authentication on Modbus writes.
       Any device on 10.10.20.0/24 can modify laser power setpoint,
       O2 thresholds, and build parameters via function code 16. *)
    arHR_Setpoints  : ARRAY[1..20] OF REAL;
END_VAR

    (* ---- Watchdog kick ---- *)
    tonWatchdog(IN := NOT tonWatchdog.Q, PT := T#500MS);
    IF tonWatchdog.Q THEN
        bWatchdogKick := TRUE;
        dwWatchdogCount := dwWatchdogCount + 1;
    END_IF;

    (* ---- HMI heartbeat monitoring ---- *)
    IF nHMIHeartbeat <> nHMIHeartbeatPrev THEN
        nHMIHeartbeatPrev := nHMIHeartbeat;
        tonHMITimeout(IN := FALSE);
        bHMIConnected := TRUE;
    ELSE
        tonHMITimeout(IN := TRUE, PT := T#10S);
        IF tonHMITimeout.Q THEN
            bHMIConnected := FALSE;
            (* Log event but do not stop build - operator may reconnect *)
        END_IF;
    END_IF;

    (* ---- Safety interlock evaluation (always runs) ---- *)
    fbSafety(
        bDoorSwitch1    := %I0.0,   (* PROFINET: ET200SP DI module, slot 2 *)
        bDoorSwitch2    := %I0.1,
        bEstop1         := %I0.2,
        bEstop2         := %I0.3,
        bLaserEnclosure := %I0.4,
        bVentilation    := %I0.5,
        bChillerOK      := %I0.6,
        bFilterDiffP    := %I0.7,
        bKeySwitch      := %I1.0
    );

    (* Merge fault sources *)
    dwActiveFaults := fbSafety.dwFaultMask;
    IF fbLaser.bFault THEN
        dwActiveFaults := dwActiveFaults OR DWORD#16#0000_0003;
    END_IF;
    IF fbPowder.bFault THEN
        dwActiveFaults := dwActiveFaults OR DWORD#16#0000_0008;
    END_IF;
    IF fbPlatform.bFault THEN
        dwActiveFaults := dwActiveFaults OR DWORD#16#0000_0010;
    END_IF;
    IF fbGas.bFault THEN
        dwActiveFaults := dwActiveFaults OR DWORD#16#0000_0020;
    END_IF;

    (* ---- Main system state machine ---- *)
    CASE eSystemState OF

        SYS_INIT:
            (* Initialisation: check all subsystems, load recipe *)
            fbGas(bEnable := FALSE);
            fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
            IF fbSafety.bSafeToOperate THEN
                eSystemState := SYS_IDLE;
            END_IF;

        SYS_IDLE:
            (* Waiting for build start command from HMI/SCADA *)
            (* Modbus HR40103: Build start command (BOOL) *)
            IF arHR_Setpoints[4] > 0.5 THEN  (* Start command *)
                arHR_Setpoints[4] := 0.0;     (* Clear command *)
                nLayerCount := 0;
                eSystemState := SYS_PREHEAT;
            END_IF;
            IF fbSafety.bEstopActive THEN
                eSystemState := SYS_ESTOP;
            END_IF;

        SYS_PREHEAT:
            (* Pre-heat build platform to recipe temperature *)
            (* Modbus HR40014: Platform temperature (REAL, degC) *)
            (* Modbus HR40104: Preheat setpoint (REAL, degC) *)
            fbGas(bEnable := TRUE, bPurgeRequest := TRUE);
            IF fbSafety.bEstopActive THEN
                eSystemState := SYS_ESTOP;
            ELSIF dwActiveFaults <> 0 THEN
                eSystemState := SYS_FAULT;
            ELSIF arHR_Process[14] >= arHR_Setpoints[5] THEN
                eSystemState := SYS_INERTING;
            END_IF;

        SYS_INERTING:
            (* Purge chamber with argon until O2 is below threshold *)
            fbGas(bEnable := TRUE, rO2Setpoint := arHR_Setpoints[3]);
            IF fbSafety.bEstopActive THEN
                eSystemState := SYS_ESTOP;
            ELSIF dwActiveFaults <> 0 THEN
                eSystemState := SYS_FAULT;
            ELSIF fbGas.bAtmosphereOK THEN
                eSystemState := SYS_BUILDING;
            END_IF;

        SYS_BUILDING:
            (* Active build loop: dose -> recoat -> scan -> lower platform *)
            fbLaser(
                bEnable         := fbSafety.bSafeToOperate,
                rPowerSetpoint  := arHR_Setpoints[1],  (* HR40100: Laser power SP *)
                bShutterPermit  := TRUE,
                bDoorClosed     := fbSafety.bDoorClosed,
                rO2Level        := fbGas.rO2Actual,
                rO2Threshold    := arHR_Setpoints[3]    (* HR40102: O2 threshold *)
            );

            fbGas(bEnable := TRUE, rO2Setpoint := arHR_Setpoints[3]);

            fbPowder(
                bStart          := TRUE,
                rLayerThickness := arHR_Setpoints[2],   (* HR40101: Layer thickness *)
                rRecoaterSpeed  := 150.0
            );

            IF fbPowder.bDone THEN
                fbPlatform(
                    bMoveDown := TRUE,
                    rStepSize := arHR_Setpoints[2]
                );
                nLayerCount := nLayerCount + 1;
            END_IF;

            (* Check completion *)
            IF nLayerCount >= nTotalLayers THEN
                eSystemState := SYS_COOLING;
            END_IF;

            (* Fault handling during build *)
            IF fbSafety.bEstopActive THEN
                fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
                eSystemState := SYS_ESTOP;
            ELSIF dwActiveFaults <> 0 THEN
                fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
                eSystemState := SYS_FAULT;
            END_IF;

            (* Pause command from HR40105 *)
            IF arHR_Setpoints[6] > 0.5 THEN
                arHR_Setpoints[6] := 0.0;
                fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
                eSystemState := SYS_PAUSED;
            END_IF;

        SYS_COOLING:
            (* Post-build: laser off, maintain atmosphere, cool down *)
            fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
            fbGas(bEnable := TRUE, rO2Setpoint := arHR_Setpoints[3]);
            (* Wait for platform temp to drop below 50C *)
            IF arHR_Process[14] < 50.0 THEN
                fbGas(bEnable := FALSE);
                eSystemState := SYS_IDLE;
            END_IF;

        SYS_PAUSED:
            (* Build paused - atmosphere maintained, laser off *)
            fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
            fbGas(bEnable := TRUE, rO2Setpoint := arHR_Setpoints[3]);
            (* Resume command from HR40106 *)
            IF arHR_Setpoints[7] > 0.5 THEN
                arHR_Setpoints[7] := 0.0;
                eSystemState := SYS_BUILDING;
            END_IF;
            IF fbSafety.bEstopActive THEN
                eSystemState := SYS_ESTOP;
            END_IF;

        SYS_FAULT:
            (* Fault state - all actuators safe, wait for reset *)
            fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
            (* Modbus HR40107: Fault reset command (BOOL) *)
            IF arHR_Setpoints[8] > 0.5 AND dwActiveFaults = 0 THEN
                arHR_Setpoints[8] := 0.0;
                eSystemState := SYS_IDLE;
            END_IF;
            IF fbSafety.bEstopActive THEN
                eSystemState := SYS_ESTOP;
            END_IF;

        SYS_ESTOP:
            (* Emergency stop - immediate shutdown of all systems *)
            fbLaser(bEnable := FALSE, rPowerSetpoint := 0.0);
            fbGas(bEnable := FALSE);
            (* Requires E-stop release AND manual reset *)
            IF NOT fbSafety.bEstopActive THEN
                IF arHR_Setpoints[8] > 0.5 THEN
                    arHR_Setpoints[8] := 0.0;
                    eSystemState := SYS_INIT;
                END_IF;
            END_IF;

        SYS_MAINTENANCE:
            (* Maintenance mode - interlocks partially bypassed *)
            (* Only accessible via physical key switch *)
            IF NOT fbSafety.bMaintMode THEN
                eSystemState := SYS_INIT;
            END_IF;
    END_CASE;

    (* ---- Update Modbus process data registers ---- *)
    arHR_Process[1]  := fbLaser.rActualPower;           (* HR40001 *)
    arHR_Process[2]  := INT_TO_REAL(fbLaser.eState);    (* HR40002 *)
    arHR_Process[3]  := fbPowder.rPowderLevel;          (* HR40003 *)
    arHR_Process[5]  := fbPlatform.rPosition;            (* HR40005 *)
    arHR_Process[7]  := fbGas.rO2Actual;                 (* HR40007 *)
    arHR_Process[8]  := fbGas.rArgonFlow;                (* HR40008 *)
    arHR_Process[9]  := fbGas.rChamberPressure;          (* HR40009 *)
    arHR_Process[10] := DWORD_TO_REAL(fbSafety.dwFaultMask); (* HR40010 *)
    arHR_Process[15] := INT_TO_REAL(eSystemState);       (* HR40015 *)
    arHR_Process[16] := INT_TO_REAL(nLayerCount);        (* HR40016 *)
    arHR_Process[17] := INT_TO_REAL(nTotalLayers);       (* HR40017 *)
    arHR_Process[18] := DWORD_TO_REAL(dwActiveFaults);   (* HR40018 *)
    arHR_Process[19] := DWORD_TO_REAL(dwWatchdogCount);  (* HR40019 *)

    (* OPC-UA: Objects/AMS500/System/State = eSystemState *)
    (* OPC-UA: Objects/AMS500/System/FaultCode = dwActiveFaults *)

END_PROGRAM
