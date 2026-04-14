# OPC-UA Server Configuration - AMS-500 PLC

**Document ID:** AMS-OPCUA-001 Rev.B  
**Classification:** COMPANY CONFIDENTIAL  
**Author:** R. Thornton, OT Network Engineering  
**Reviewed:** K. Okonkwo, ICS Security  
**Date:** 2025-10-28  
**PLC:** Siemens S7-1515SP PC2 (PLC-AMS-01)  
**Firmware:** V2.9.4  

---

## 1. Overview

The Siemens S7-1515SP PC2 hosts an integrated OPC-UA server that exposes AMS-500 process data to supervisory systems. This document describes the current server configuration, the node address space, and security policy settings.

The OPC-UA server is the primary mechanism by which the SCADA server (WinCC on SCADA-01), the data historian (HIST-01), and the HMI panel (HMI-01) access process data from the PLC. The engineering workstations (ENG-WS-01, ENG-WS-02) also connect via OPC-UA for commissioning and diagnostics.

**Critical finding:** The OPC-UA server is currently deployed with SecurityPolicy=None and Anonymous authentication. This means any device that can reach TCP port 4840 on 10.10.20.10 can read and write all exposed process variables without any form of credential or certificate. This configuration was set during commissioning and has not been hardened.

---

## 2. Server Endpoints

The PLC exposes the following OPC-UA endpoints:

| Endpoint URL | Security Policy | Security Mode | Status |
|-------------|----------------|---------------|--------|
| `opc.tcp://10.10.20.10:4840` | None | None | **ACTIVE** (current) |
| `opc.tcp://10.10.20.10:4840` | Basic256Sha256 | Sign | Available but **NOT ENABLED** |
| `opc.tcp://10.10.20.10:4840` | Basic256Sha256 | SignAndEncrypt | Available but **NOT ENABLED** |
| `opc.tcp://10.10.20.10:4840` | Aes128_Sha256_RsaOaep | Sign | Available but **NOT ENABLED** |
| `opc.tcp://10.10.20.10:4840` | Aes128_Sha256_RsaOaep | SignAndEncrypt | Available but **NOT ENABLED** |
| `opc.tcp://10.10.20.10:4840` | Aes256_Sha256_RsaPss | SignAndEncrypt | Available but **NOT ENABLED** |

### 2.1 Discovery Endpoint

The server also exposes a discovery endpoint at `opc.tcp://10.10.20.10:4840/discovery` which responds to FindServers and GetEndpoints requests without requiring any security. This is standard OPC-UA behaviour but means that any client can enumerate the available endpoints and their security capabilities.

### 2.2 Recommended Configuration

Per IEC 62443-4-2 and the OPC Foundation Security Best Practices, the following configuration should be applied:

| Endpoint URL | Security Policy | Security Mode | Recommended |
|-------------|----------------|---------------|-------------|
| `opc.tcp://10.10.20.10:4840` | None | None | **DISABLE** |
| `opc.tcp://10.10.20.10:4840` | Basic256Sha256 | SignAndEncrypt | **ENABLE** (primary) |
| `opc.tcp://10.10.20.10:4840` | Aes128_Sha256_RsaOaep | SignAndEncrypt | **ENABLE** (fallback) |

All other policy/mode combinations should be disabled. The `None/None` endpoint must be removed to prevent clients from falling back to an insecure connection.

---

## 3. Authentication Configuration

### 3.1 Current State

| Token Type | Status | Details |
|-----------|--------|---------|
| Anonymous | **ENABLED** | No credentials required. Any client can connect. |
| Username/Password | Configured but **NOT ENFORCED** | Accounts exist in PLC user management but anonymous takes precedence. |
| X.509 Certificate | **NOT CONFIGURED** | No client certificates have been deployed. |

### 3.2 User Accounts (if Username token enforced)

These accounts are configured in the S7-1500 user management but are currently bypassed because Anonymous authentication is enabled:

| Username | Role | Access Level | Notes |
|----------|------|-------------|-------|
| opc_scada | SCADA | Read all, Write setpoints | For SCADA-01 connection |
| opc_historian | Historian | Read all | For HIST-01 connection |
| opc_hmi | Operator | Read all, Write commands | For HMI-01 connection |
| opc_engineer | Engineer | Read all, Write all, Browse | For engineering workstations |
| opc_admin | Administrator | Full access including server config | Emergency/maintenance use |

### 3.3 Recommended Authentication

1. **Disable Anonymous authentication.** This is the single most impactful security improvement.
2. **Enable Username/Password as minimum.** Assign per-device accounts with least-privilege access.
3. **Deploy X.509 certificates for production.** Each client should present a certificate signed by the site CA. The PLC's trust store should contain only the CA certificate, allowing new clients to be authenticated by issuing certificates without modifying PLC configuration.

Certificate requirements for the S7-1515SP:
- Key type: RSA 2048-bit minimum (4096-bit recommended)
- Signature algorithm: SHA-256
- Key usage: Digital Signature, Key Encipherment
- Extended key usage: Client Authentication (1.3.6.1.5.5.7.3.2)
- Validity: 2 years maximum

---

## 4. Node Address Space

The OPC-UA server exposes the following node structure under the `Objects` folder. All nodes use namespace index 2 (`ns=2`).

### 4.1 Node Hierarchy

```
Objects/
  Server/                                       (OPC-UA standard server object)
  AMS500/                                       (ns=2; s=AMS500)
    Laser/                                      (ns=2; s=AMS500.Laser)
      Power                                     (ns=2; s=AMS500.Laser.Power)
      PowerSetpoint                             (ns=2; s=AMS500.Laser.PowerSetpoint)
      State                                     (ns=2; s=AMS500.Laser.State)
      ShutterOpen                               (ns=2; s=AMS500.Laser.ShutterOpen)
      OperatingHours                            (ns=2; s=AMS500.Laser.OperatingHours)
      WavelengthNm                              (ns=2; s=AMS500.Laser.WavelengthNm)
    BuildPlatform/                              (ns=2; s=AMS500.BuildPlatform)
      Position                                  (ns=2; s=AMS500.BuildPlatform.Position)
      TargetPosition                            (ns=2; s=AMS500.BuildPlatform.TargetPosition)
      Temperature                               (ns=2; s=AMS500.BuildPlatform.Temperature)
      TemperatureSetpoint                       (ns=2; s=AMS500.BuildPlatform.TemperatureSetpoint)
      Homed                                     (ns=2; s=AMS500.BuildPlatform.Homed)
      InPosition                                (ns=2; s=AMS500.BuildPlatform.InPosition)
    Recoater/                                   (ns=2; s=AMS500.Recoater)
      Position                                  (ns=2; s=AMS500.Recoater.Position)
      Speed                                     (ns=2; s=AMS500.Recoater.Speed)
      Force                                     (ns=2; s=AMS500.Recoater.Force)
      CycleActive                               (ns=2; s=AMS500.Recoater.CycleActive)
    PowderDosing/                               (ns=2; s=AMS500.PowderDosing)
      HopperLevel                               (ns=2; s=AMS500.PowderDosing.HopperLevel)
      DoseWeight                                (ns=2; s=AMS500.PowderDosing.DoseWeight)
      LayerThickness                            (ns=2; s=AMS500.PowderDosing.LayerThickness)
      LayerThicknessSetpoint                    (ns=2; s=AMS500.PowderDosing.LayerThicknessSetpoint)
    Atmosphere/                                 (ns=2; s=AMS500.Atmosphere)
      O2Level                                   (ns=2; s=AMS500.Atmosphere.O2Level)
      O2Setpoint                                (ns=2; s=AMS500.Atmosphere.O2Setpoint)
      ArgonFlow                                 (ns=2; s=AMS500.Atmosphere.ArgonFlow)
      Pressure                                  (ns=2; s=AMS500.Atmosphere.Pressure)
      MoistureLevel                             (ns=2; s=AMS500.Atmosphere.MoistureLevel)
      AtmosphereOK                              (ns=2; s=AMS500.Atmosphere.AtmosphereOK)
    System/                                     (ns=2; s=AMS500.System)
      State                                     (ns=2; s=AMS500.System.State)
      FaultCode                                 (ns=2; s=AMS500.System.FaultCode)
      LayerCount                                (ns=2; s=AMS500.System.LayerCount)
      TotalLayers                               (ns=2; s=AMS500.System.TotalLayers)
      BuildProgress                             (ns=2; s=AMS500.System.BuildProgress)
      BuildTimeElapsed                          (ns=2; s=AMS500.System.BuildTimeElapsed)
      BuildTimeRemaining                        (ns=2; s=AMS500.System.BuildTimeRemaining)
      RecipeName                                (ns=2; s=AMS500.System.RecipeName)
      WatchdogCounter                           (ns=2; s=AMS500.System.WatchdogCounter)
    Safety/                                     (ns=2; s=AMS500.Safety)
      DoorClosed                                (ns=2; s=AMS500.Safety.DoorClosed)
      EStopActive                               (ns=2; s=AMS500.Safety.EStopActive)
      InterlockMask                             (ns=2; s=AMS500.Safety.InterlockMask)
      SafeToOperate                             (ns=2; s=AMS500.Safety.SafeToOperate)
      MaintenanceMode                           (ns=2; s=AMS500.Safety.MaintenanceMode)
    Commands/                                   (ns=2; s=AMS500.Commands)
      BuildStart                                (ns=2; s=AMS500.Commands.BuildStart)
      BuildPause                                (ns=2; s=AMS500.Commands.BuildPause)
      BuildResume                               (ns=2; s=AMS500.Commands.BuildResume)
      FaultReset                                (ns=2; s=AMS500.Commands.FaultReset)
      HomeAxes                                  (ns=2; s=AMS500.Commands.HomeAxes)
```

### 4.2 Node Details

| Node ID | Display Name | Data Type | Access | Unit | Range | Description |
|---------|-------------|-----------|--------|------|-------|-------------|
| AMS500.Laser.Power | Laser Power | Float | ReadOnly | W | 0 - 500 | Actual laser output power |
| AMS500.Laser.PowerSetpoint | Laser Power SP | Float | **ReadWrite** | W | 0 - 500 | Laser power setpoint |
| AMS500.Laser.State | Laser State | Int16 | ReadOnly | - | 0 - 4 | 0=Off, 1=Standby, 2=Ready, 3=Firing, 4=Fault |
| AMS500.Laser.ShutterOpen | Shutter Open | Boolean | ReadOnly | - | - | Laser shutter status |
| AMS500.Laser.OperatingHours | Operating Hours | Float | ReadOnly | h | 0 - 100000 | Total laser on-time |
| AMS500.Laser.WavelengthNm | Wavelength | UInt16 | ReadOnly | nm | - | Fixed: 1070nm (Yb fibre) |
| AMS500.BuildPlatform.Position | Platform Pos | Float | ReadOnly | mm | 0 - 350 | Current Z-axis position |
| AMS500.BuildPlatform.TargetPosition | Platform Target | Float | ReadOnly | mm | 0 - 350 | Commanded Z-axis position |
| AMS500.BuildPlatform.Temperature | Platform Temp | Float | ReadOnly | degC | 0 - 500 | Build platform temperature |
| AMS500.BuildPlatform.TemperatureSetpoint | Platform Temp SP | Float | **ReadWrite** | degC | 20 - 300 | Preheat temperature setpoint |
| AMS500.BuildPlatform.Homed | Platform Homed | Boolean | ReadOnly | - | - | Homing complete flag |
| AMS500.BuildPlatform.InPosition | In Position | Boolean | ReadOnly | - | - | At target position |
| AMS500.Recoater.Position | Recoater Pos | Float | ReadOnly | mm | 0 - 300 | Recoater X position |
| AMS500.Recoater.Speed | Recoater Speed | Float | ReadOnly | mm/s | 0 - 200 | Current recoater velocity |
| AMS500.Recoater.Force | Recoater Force | Float | ReadOnly | N | 0 - 50 | Recoater blade force (anomaly indicator) |
| AMS500.Recoater.CycleActive | Recoat Active | Boolean | ReadOnly | - | - | Recoat cycle in progress |
| AMS500.PowderDosing.HopperLevel | Hopper Level | Float | ReadOnly | % | 0 - 100 | Powder hopper fill level |
| AMS500.PowderDosing.DoseWeight | Dose Weight | Float | ReadOnly | g | 0 - 50 | Weight of last powder dose |
| AMS500.PowderDosing.LayerThickness | Layer Thickness | Float | ReadOnly | mm | 0.02 - 0.10 | Actual measured layer thickness |
| AMS500.PowderDosing.LayerThicknessSetpoint | Layer Thick. SP | Float | **ReadWrite** | mm | 0.02 - 0.10 | Layer thickness setpoint |
| AMS500.Atmosphere.O2Level | O2 Level | Float | ReadOnly | ppm | 0 - 210000 | Measured oxygen concentration |
| AMS500.Atmosphere.O2Setpoint | O2 Setpoint | Float | **ReadWrite** | ppm | 100 - 5000 | Oxygen threshold setpoint |
| AMS500.Atmosphere.ArgonFlow | Argon Flow | Float | ReadOnly | l/min | 0 - 80 | Argon mass flow rate |
| AMS500.Atmosphere.Pressure | Chamber Pressure | Float | ReadOnly | mbar | 900 - 1100 | Build chamber absolute pressure |
| AMS500.Atmosphere.MoistureLevel | Moisture | Float | ReadOnly | ppm | 0 - 10000 | Atmospheric moisture content |
| AMS500.Atmosphere.AtmosphereOK | Atmosphere OK | Boolean | ReadOnly | - | - | All atmosphere parameters in range |
| AMS500.System.State | System State | Int16 | ReadOnly | - | 0 - 9 | See E_SystemState enum |
| AMS500.System.FaultCode | Fault Code | UInt32 | ReadOnly | - | 0x0-0xFFF | Active fault bitmask |
| AMS500.System.LayerCount | Layer Count | Int32 | ReadOnly | - | 0 - 99999 | Current layer number |
| AMS500.System.TotalLayers | Total Layers | Int32 | ReadOnly | - | 0 - 99999 | Total layers in recipe |
| AMS500.System.BuildProgress | Build Progress | Float | ReadOnly | % | 0 - 100 | Percentage complete |
| AMS500.System.BuildTimeElapsed | Time Elapsed | UInt32 | ReadOnly | s | 0 - 999999 | Elapsed build time |
| AMS500.System.BuildTimeRemaining | Time Remaining | UInt32 | ReadOnly | s | 0 - 999999 | Estimated time remaining |
| AMS500.System.RecipeName | Recipe Name | String | ReadOnly | - | - | Active recipe identifier |
| AMS500.System.WatchdogCounter | Watchdog | UInt32 | ReadOnly | - | - | PLC cycle watchdog counter |
| AMS500.Safety.DoorClosed | Door Closed | Boolean | ReadOnly | - | - | Build chamber door status |
| AMS500.Safety.EStopActive | E-Stop Active | Boolean | ReadOnly | - | - | Emergency stop status |
| AMS500.Safety.InterlockMask | Interlock Mask | UInt32 | ReadOnly | - | - | Interlock fault bitmask |
| AMS500.Safety.SafeToOperate | Safe to Operate | Boolean | ReadOnly | - | - | Master interlock permit |
| AMS500.Safety.MaintenanceMode | Maint. Mode | Boolean | ReadOnly | - | - | Maintenance bypass active |
| AMS500.Commands.BuildStart | Build Start | Boolean | **ReadWrite** | - | - | Start build command |
| AMS500.Commands.BuildPause | Build Pause | Boolean | **ReadWrite** | - | - | Pause build command |
| AMS500.Commands.BuildResume | Build Resume | Boolean | **ReadWrite** | - | - | Resume build command |
| AMS500.Commands.FaultReset | Fault Reset | Boolean | **ReadWrite** | - | - | Reset faults command |
| AMS500.Commands.HomeAxes | Home Axes | Boolean | **ReadWrite** | - | - | Initiate homing sequence |

**Security concern:** All ReadWrite nodes are writable by any connected client when Anonymous authentication is enabled. This includes safety-critical setpoints (O2 threshold, laser power) and process commands (BuildStart, FaultReset). An unauthenticated client could start a build, modify laser power during active lasing, or reset safety faults without operator knowledge.

---

## 5. Subscription and Sampling Configuration

### 5.1 Default Subscription Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Requested Publishing Interval | 500 ms | Server may revise upward under load |
| Requested Lifetime Count | 1000 | Max missed publish cycles before subscription deleted |
| Requested Max KeepAlive Count | 10 | Publish empty notifications to confirm connection |
| Max Notifications Per Publish | 0 (unlimited) | Could cause burst traffic on state changes |
| Publishing Enabled | True | |
| Priority | 0 | All subscriptions at equal priority |

### 5.2 Monitored Item Defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| Sampling Interval | 250 ms | PLC scan cycle is 100ms, so 250ms captures every change |
| Queue Size | 10 | Buffers up to 10 value changes between publish cycles |
| Discard Oldest | True | Oldest queued value dropped if queue full |
| Filter Type | None | No deadband filtering by default |
| Data Change Trigger | StatusValue | Publishes on value change or status change |

### 5.3 Recommended Per-Node Deadband Settings

To reduce unnecessary traffic, the following absolute deadband values are recommended:

| Node Group | Deadband Type | Deadband Value | Rationale |
|------------|--------------|----------------|-----------|
| Laser Power | Absolute | 0.5 W | 0.1% of range, sufficient for monitoring |
| Temperatures | Absolute | 0.2 degC | Within sensor accuracy |
| O2 Level | Absolute | 5 ppm | Within analyser accuracy |
| Platform Position | Absolute | 0.005 mm | Half of positioning resolution |
| Argon Flow | Absolute | 0.1 l/min | Within MFC accuracy |
| Chamber Pressure | Absolute | 0.5 mbar | Within transducer accuracy |
| Boolean values | None | N/A | Always report state changes |

---

## 6. Historical Data Access (HDA)

### 6.1 Current Configuration

Historical data access is enabled on the PLC's OPC-UA server with the following parameters:

| Parameter | Value |
|-----------|-------|
| HDA Enabled | Yes |
| Storage Location | PLC internal (SD card) |
| Storage Capacity | 32 GB (SIMATIC Memory Card) |
| Recording Interval | 1 second (process data), 100ms (safety data) |
| Retention Period | 72 hours (rolling buffer) |
| Archive to External | Via SCADA/Historian (OPC-UA HDA client) |
| Compression | Swinging Door Trending (SDT) |
| SDT Deviation | 1% of engineering range |

### 6.2 Historical Nodes

The following nodes are configured for historical recording:

- AMS500.Laser.Power (1s interval)
- AMS500.BuildPlatform.Position (1s interval)
- AMS500.BuildPlatform.Temperature (1s interval)
- AMS500.Atmosphere.O2Level (1s interval)
- AMS500.Atmosphere.ArgonFlow (1s interval)
- AMS500.Atmosphere.Pressure (1s interval)
- AMS500.System.State (on change)
- AMS500.System.FaultCode (on change)
- AMS500.Safety.DoorClosed (100ms interval)
- AMS500.Safety.EStopActive (100ms interval)
- AMS500.Safety.InterlockMask (on change)

### 6.3 Security Implications of HDA

Historical data provides a forensic trail of process execution. However, because the OPC-UA server has no authentication:

- Any client can read the full 72-hour history of all recorded variables.
- Historical data includes the exact timing of safety events (door openings, E-stops, fault conditions), which could be used to profile operator behaviour or identify maintenance windows.
- The historian client (HIST-01) pulls data over an unauthenticated, unencrypted OPC-UA connection. A man-in-the-middle could modify historical records in transit without detection.

---

## 7. Server Certificate

The PLC generates a self-signed certificate at first boot. The current certificate details:

| Field | Value |
|-------|-------|
| Subject | CN=PLC-AMS-01, O=AMS Manufacturing, C=GB |
| Issuer | CN=PLC-AMS-01 (self-signed) |
| Serial Number | 0x01A4C8F3 |
| Valid From | 2024-03-15 08:00:00 UTC |
| Valid To | 2029-03-15 08:00:00 UTC |
| Key Algorithm | RSA 2048-bit |
| Signature Algorithm | SHA-256 |
| Key Usage | Digital Signature, Key Encipherment, Data Encipherment |
| Subject Alt Names | DNS:PLC-AMS-01, IP:10.10.20.10, URI:urn:PLC-AMS-01:Siemens:S7-1500 |
| Thumbprint (SHA-1) | 4A:7B:C3:91:0E:F2:38:D5:A6:11:BB:C0:94:7D:E8:F3:21:55:AA:09 |

This certificate is used when a client connects with a secure security policy (Basic256Sha256, etc.). However, since only the None/None endpoint is currently active, the certificate is not used in practice.

**Note:** The 5-year validity period exceeds the recommended maximum of 2 years per the OPC Foundation Security Best Practices. The certificate should be regenerated with a shorter validity period or, preferably, issued by a dedicated OT PKI infrastructure.

---

## 8. Implementation Plan for Security Hardening

### Phase 1: Enable Username Authentication (1 day, no downtime required)

1. Configure user accounts on the PLC via TIA Portal (accounts listed in Section 3.2).
2. Update OPC-UA server configuration to require Username token.
3. Disable Anonymous authentication.
4. Update all client configurations (SCADA-01, HIST-01, HMI-01) with appropriate credentials.
5. Test all client connections and verify data flow.
6. Monitor for 48 hours before proceeding to Phase 2.

### Phase 2: Enable Transport Security (2 days, brief downtime per client)

1. Generate a site CA certificate using OpenSSL or XCA.
2. Issue server certificate for the PLC signed by the site CA.
3. Issue client certificates for SCADA-01, HIST-01, HMI-01, ENG-WS-01, ENG-WS-02.
4. Import the site CA certificate into the PLC trust store.
5. Import client certificates into respective client trust stores.
6. Enable Basic256Sha256/SignAndEncrypt endpoint on the PLC.
7. Disable the None/None endpoint.
8. Update all client endpoint configurations.
9. Verify encrypted connections using Wireshark capture on SW-CTL-01 SPAN port.

### Phase 3: Enable Certificate Authentication (1 day, no downtime)

1. Configure X.509 user token mapping on the PLC.
2. Map each client certificate to its corresponding user role.
3. Disable Username/Password authentication (optional - can run both).
4. Test and verify.

**Estimated total effort:** 4 days including testing and verification.  
**Risk:** Low. Each phase can be rolled back independently. Phase 1 is the critical step and should be prioritised.
