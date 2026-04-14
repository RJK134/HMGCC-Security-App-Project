# CVE Analysis: STM32 System Bootloader Vulnerabilities

## CVE-2020-8004: STM32 UART Bootloader Bypass
**CVSS Score:** 6.8 (Medium)
**Affected Products:** STM32F4xx, STM32F7xx, STM32H7xx series

### Description
The system bootloader in STM32 microcontrollers allows an attacker with physical UART access to bypass Read-out Protection (RDP) Level 1 by exploiting a race condition during the bootloader handshake sequence. This allows firmware extraction from devices that should be read-protected.

### Technical Details
- The STM32 system bootloader (ROM-based) responds to UART at 115200 baud
- When RDP Level 1 is set, the bootloader should reject read commands
- A timing-based attack during the ACK/NACK sequence allows partial memory reads
- The bootloader uses GPIO PA0 (BOOT0 pin) to enter bootloader mode
- AN2606 documents the bootloader protocol but does not disclose this vulnerability

### Impact
- **Firmware extraction**: Proprietary code can be dumped from protected devices
- **Credential theft**: Hardcoded keys, certificates, and passwords exposed
- **Cloning**: Enables unauthorised reproduction of the device

### Mitigations
1. Set RDP Level 2 (irreversible — cannot be downgraded)
2. Physically remove or disable BOOT0 pin after programming
3. Use secure boot chain with signature verification
4. Implement application-level encryption for sensitive data in flash
5. Consider STM32L5/U5 with TrustZone for security-critical applications

## CVE-2021-34432: STM32 DFU Mode Vulnerability
**CVSS Score:** 5.3 (Medium)
**Affected Products:** STM32F1xx, STM32F2xx, STM32F4xx with USB DFU

### Description
The USB Device Firmware Update (DFU) mode in STM32 microcontrollers does not implement any authentication mechanism. Any USB host can upload new firmware to the device when in DFU mode, regardless of RDP settings.

### Impact
- **Firmware replacement**: Malicious firmware can be loaded onto the device
- **Persistent compromise**: Replaced firmware survives power cycles
- **Supply chain attack vector**: Pre-programmed devices can be re-flashed

### Mitigations
1. Implement application-level firmware signature verification
2. Disable DFU mode in production via option bytes
3. Physical tamper detection on USB connector
4. Use STM32 Secure Boot Manager (SBSFU) for verified boot chain

## General STM32 Security Recommendations
- Always enable RDP Level 1 minimum for production devices
- Configure write protection on critical flash sectors
- Use PCROP (Proprietary Code Read-Out Protection) for cryptographic keys
- Enable MPU (Memory Protection Unit) to isolate security-critical code
- Implement watchdog timers to detect and recover from fault injection attacks
- Consider using STM32Trust ecosystem for comprehensive security features
