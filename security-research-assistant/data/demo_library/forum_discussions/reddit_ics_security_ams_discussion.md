# Reddit r/ICS Thread: Security concerns with industrial additive manufacturing

**URL:** https://www.reddit.com/r/ics/comments/1ab3xyz/security_concerns_with_additive_manufacturing_in/  
**Subreddit:** r/ICS  
**Posted:** 2025-12-09  
**Upvotes:** 187  
**Comments:** 34  

---

**u/process_ctrl_eng** | OP  
*Dec 9, 2025*

We're deploying metal additive manufacturing systems (powder bed fusion, fibre lasers) in a defence production environment. Our security team has been asked to assess the risk of these machines, but most of our ICS security experience is with traditional PLCs, DCS, and SCADA -- not additive manufacturing.

Specific concerns we've identified so far:
- The machines have Siemens S7-1500 PLCs running the motion control and process logic
- Laser power and scan parameters are set via the control network
- Build files (.CLI slice format) are transferred from an offline build preparation workstation over Ethernet
- There's no integrity checking on the build files once they're loaded

Has anyone done a security assessment on this class of equipment? What should we be looking at beyond the standard ICS hardening checklist?

---

**u/ics_red_teamer** | 48 points  
*Dec 9, 2025*

This is actually a really interesting attack surface that doesn't get enough attention. The threat with additive manufacturing is different from traditional ICS because you can introduce defects that are invisible to visual inspection.

Consider: an attacker modifies the laser power parameter by 5-8% during specific layers of a build. The part comes out looking perfectly normal. It passes dimensional checks. But the material microstructure is wrong -- incomplete fusion, porosity, or altered grain structure. The part is weaker than spec but you'd need destructive testing or CT scanning to detect it.

This has been studied academically. Search for "additive manufacturing cyber-physical attacks" -- there are papers from NYU, Georgia Tech, and the University of South Alabama. The core finding is the same: small parameter modifications can cause significant structural defects that are not detectable by standard quality control.

For your assessment, I'd focus on:
1. The build file transfer mechanism (integrity of .CLI files)
2. Process parameter storage and modification (who can change laser power, scan speed, layer thickness?)
3. Network isolation of the AM machines from the broader OT/IT network
4. Physical access to the control cabinet (debug ports, serial consoles, USB ports)

---

**u/nist_sp_800_reader** | 31 points  
*Dec 9, 2025*

Start with NIST SP 800-82 Rev 3 (Guide to OT Security) as your framework. It was updated in 2023 and covers a lot of the network architecture, access control, and monitoring basics that apply to any ICS including AM systems.

For additive manufacturing specifically, NIST published NISTIR 8183A Rev 1 (Cybersecurity Framework Manufacturing Profile) which has AM-relevant guidance. Also check NIST SP 1800-10 (Protecting Information and System Integrity in Industrial Control System Environments) for practical architecture examples.

The general approach:
- Zone the AM system in its own network segment per IEC 62443
- Treat the build preparation workstation as a high-value asset (hardened OS, application whitelisting, limited network access)
- Implement file integrity monitoring on build files
- Log all parameter changes with tamper-evident audit trail
- Physical security on the control cabinet (locks, tamper evidence, camera monitoring)

---

**u/mitre_attack_enthusiast** | 27 points  
*Dec 10, 2025*

Look at the MITRE ATT&CK for ICS framework. It maps out the tactics and techniques an adversary would use in an ICS environment. For your AM system, the relevant techniques include:

- **T0858 - Change Operating Mode:** Switching the PLC to STOP mode or reprogramming
- **T0836 - Modify Parameter:** Changing laser power, scan speed, or other process parameters
- **T0831 - Manipulation of Control:** Altering the scan path or layer exposure timing
- **T0882 - Theft of Operational Information:** Exfiltrating build files (which contain proprietary part geometry)
- **T0859 - Valid Accounts:** Using default or shared credentials to access PLCs, HMIs, or engineering workstations

The intellectual property theft angle is underrated. Those .CLI build files contain the exact geometry of whatever you're manufacturing. If it's defence components, the build files are potentially classified. Are they encrypted at rest? In transit? I'd bet money they're not.

---

**u/air_gap_is_a_lie** | 22 points  
*Dec 10, 2025*

> There's no integrity checking on the build files once they're loaded

This is the big one for me. In most AM systems I've seen, the build file goes from the CAD/CAM workstation to the AM machine with no digital signature, no hash verification, nothing. It's usually a network file share or USB transfer. Anyone who can write to that share can modify the build file.

The argument for air-gapping these machines is strong: they're not doing anything that requires real-time internet connectivity. But in practice, "air-gapped" AM systems still need:
- Build files transferred in somehow
- Firmware updates applied periodically
- Log data extracted for quality records
- Sometimes remote diagnostics from the vendor

So the air gap always has holes. USB drives, maintenance laptops, vendor service ports. Each one is a potential vector.

My preference is monitored isolation over claimed air gaps. Put the AM machines on their own network segment with a hardware firewall, enable deep packet inspection for the protocols in use (S7Comm, Modbus, OPC-UA), and log everything. At least then you can detect anomalies rather than having blind faith in an air gap that probably isn't one.

---

**u/siemens_integrator_42** | 19 points  
*Dec 10, 2025*

I work as a Siemens integrator and have configured security on several S7-1500 systems. Some practical advice:

1. **Access level protection in TIA Portal:** Set up access levels with strong passwords. Level 1 (read) for operators, Level 3 (read/write) for maintenance, Full access for engineering only. Most sites I visit have no access protection at all.

2. **Know-how protection on function blocks:** Encrypt your safety-critical FBs so they can't be viewed or modified without the password. Won't stop a determined attacker but raises the bar.

3. **Disable unused protocols:** The S7-1500 enables a LOT of protocols by default. If you're not using SNMP, disable it. If you don't need the web server, turn it off. Every open port is an attack surface.

4. **Memory card protection:** Enable password protection on the SIMATIC memory card. Without it, anyone with physical access can pull the card, copy the PLC program, and put it back.

5. **Firmware version:** Update to V3.0+ for the individual per-PLC key protection on S7CommPlus. The older global key vulnerability (CVE-2022-38465) was a really bad one.

6. **Audit trail:** Configure the S7-1500's diagnostic buffer to log access events. Forward these to a syslog server via SNMP traps if possible. At minimum you'll have a record of who connected to the PLC and when.

---

**u/process_ctrl_eng** | OP | 8 points  
*Dec 11, 2025*

Thank you all, this is incredibly helpful. The intellectual property angle on the build files is something our security team hadn't fully considered -- you're right that the .CLI files effectively contain the complete manufacturing recipe for the part.

Going to put together a risk register based on the MITRE ATT&CK for ICS framework and map our mitigations to NIST SP 800-82. Will update the thread once we've done the assessment.

One follow-up question: has anyone had experience with the Hirschmann managed switches that come with these systems? Specifically around VLAN configuration and port-based access control? Our machines have RS20 series switches and we want to make sure we're using them properly for network segmentation within the machine itself.

---

**u/ics_red_teamer** | 12 points  
*Dec 11, 2025*

Hirschmann RS20 series are decent managed switches. They support 802.1Q VLANs, port-based access control (802.1X if you have a RADIUS server), and SNMP monitoring. The web interface is functional.

Watch out for:
- Default credentials (admin/admin on Classic platform firmware, admin/private on HiOS platform)
- The console port (RS-232 via RJ-45) which gives direct CLI access
- SNMP v1/v2c enabled by default with community string "public" -- gives read access to the MAC address table, port statistics, and VLAN configuration

For your use case, I'd create separate VLANs for: (1) the PLC PROFINET ring, (2) the HMI/operator network, (3) the service/engineering access port. Lock down inter-VLAN routing on the firewall, not on the switch -- the RS20 is a Layer 2 switch, not a router.

---

*[Thread continues with additional comments about vendor support, insurance requirements, and procurement standards. Truncated.]*
