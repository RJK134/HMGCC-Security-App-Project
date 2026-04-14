# PLCTalk.net Forum Thread: Securing Modbus on S7-1500

**URL:** https://www.plctalk.net/threads/securing-modbus-tcp-on-s7-1500-what-are-you-guys-actually-doing.142847/  
**Forum:** PLCTalk.net > PLC/PAC > Siemens  
**Started:** 2025-11-03  
**Last reply:** 2026-01-18  
**Views:** 4,283  
**Replies:** 22  

---

**AutomationDave** | Senior Member | Posts: 1,247  
*Nov 3, 2025 at 8:14 AM*

Hey all,

Got a question that I'm sure has come up before but I can't find a definitive answer. We've got a site with about 15 S7-1500 PLCs running various process lines, and we're getting pressure from corporate IT security to "encrypt Modbus traffic". Currently we've got S7-1516 CPUs talking Modbus TCP to a bunch of third-party HMIs and a historian.

I know Modbus TCP has no built-in encryption -- it's basically just raw register reads/writes over TCP port 502. But what are people actually doing in practice to secure this? Our IT guys want TLS on everything, but I don't think the S7-1500's Modbus server supports that.

Anyone running Modbus TCP/TLS in production on Siemens gear? Or is everyone just relying on network segmentation?

---

**PLCMechanic_22** | Active Member | Posts: 631  
*Nov 3, 2025 at 9:42 AM*

Short answer: no one is running Modbus TCP/TLS on S7-1500 because it doesn't support it. The Modbus TCP server in the S7-1500 firmware is plain TCP. Full stop.

Siemens' official position is "use OPC-UA instead" because OPC-UA supports certificates and encryption natively and the S7-1500 has a built-in OPC-UA server. But that means replacing your HMIs and historian connections, which is usually the point where the project dies.

What we actually do: VLANs. Keep Modbus traffic on its own VLAN, restrict access with ACLs on the managed switches, and call it a day. It's not encryption but it's better than having everything on one flat network.

---

**InstrumentGirl** | Member | Posts: 203  
*Nov 3, 2025 at 11:58 AM*

We went through this exact exercise last year. The Modbus TCP/TLS spec exists (it's in the Modbus.org spec, uses port 802) but practically zero industrial equipment supports it. Definitely not the S7-1500.

Our compromise was:
1. VLANs for OT networks
2. Firewall between IT and OT (Fortinet with ICS-specific rules)
3. Move the historian connection to OPC-UA with certificates
4. Accept that Modbus between PLCs and local HMIs stays unencrypted on the isolated OT VLAN

Corporate IT grumbled but accepted it once we showed them the network diagram with all the segmentation.

---

**SiemensGuru_UK** | Senior Member | Posts: 3,412  
*Nov 3, 2025 at 2:30 PM*

> Siemens' official position is "use OPC-UA instead"

This is technically correct but let me warn you about the OPC-UA rabbit hole on S7-1500. Yes, it supports encryption and certificates. No, it is not straightforward to manage.

The S7-1500 OPC-UA server supports Security Mode: Sign, SignAndEncrypt, and None. If you want proper security you need SignAndEncrypt with Basic256Sha256 policy. This means:

1. You need to generate or import X.509 certificates on every PLC
2. Every client needs its own certificate
3. The PLC needs to trust each client certificate (you do this in TIA Portal or via the PLC web server)
4. Certificates expire and need to be rotated

On a site with 15 PLCs and maybe 20 clients, you're managing 35+ certificates with expiry tracking. There's no centralised certificate management -- you're logging into each PLC and manually trusting certificates one at a time in TIA Portal.

We had a site go down for 4 hours last year because a certificate expired on a Friday night and the OPC-UA historian lost connection to 8 PLCs simultaneously. The on-call engineer had no idea what was happening because the PLC diagnostics just showed "OPC-UA client connection rejected".

My honest recommendation: VLANs + managed switches + monitoring. If you absolutely need encrypted historian data, put a single OPC-UA aggregation server on the OT network that talks Modbus to the PLCs and OPC-UA with certificates to the historian. That way you're managing certificates on one box, not 15.

---

**NetSecDan** | Member | Posts: 87  
*Nov 4, 2025 at 10:17 AM*

I'm a network security analyst (IT side) who does OT assessments. Just want to share something that might be useful for this discussion.

I did a capture of S7Comm traffic (the native Siemens protocol, not Modbus) between TIA Portal and an S7-1516 on a client site. Using Wireshark with the s7comm dissector plugin. Everything was plaintext -- PLC program uploads, downloads, variable reads, diagnostics, all of it visible in the packet capture.

The s7comm protocol has an "authentication" mechanism but it's basically a challenge-response with a known algorithm. There have been multiple publications showing how to bypass it. 

The newer S7CommPlus protocol (used by 1500-series) was supposed to fix this with proper encryption. And then CVE-2022-38465 happened.

---

**AutomationDave** | Senior Member | Posts: 1,247  
*Nov 4, 2025 at 11:30 AM*

> And then CVE-2022-38465 happened.

Can you elaborate? I saw something about this but didn't fully understand the implications.

---

**NetSecDan** | Member | Posts: 87  
*Nov 4, 2025 at 1:15 PM*

CVE-2022-38465 was a big one. Researchers from Claroty (Team82) discovered that Siemens used a single hardcoded global private key for the S7CommPlus protocol across ALL S7-1200 and S7-1500 PLCs. The key was embedded in TIA Portal and in the PLC firmware.

Once extracted (which the researchers did), anyone with that key could:
- Intercept and decrypt all S7CommPlus traffic
- Upload/download PLC programs
- Read/write PLC variables
- Basically full control of any S7-1500 on the network

Siemens released firmware updates (V3.0.x for the 1500 series) that moved to individual per-PLC keys using a proper TLS 1.3 handshake. But:
1. Not everyone has updated their firmware
2. The update requires TIA Portal V18 or later
3. It's a breaking change -- all engineering stations need the new TIA Portal version
4. Old TIA Portal project backups can't connect to updated PLCs without project migration

So in practice, there are still a LOT of S7-1500s out there running pre-V3.0 firmware with the compromised global key.

---

**PLC_Oldtimer** | Senior Member | Posts: 5,891  
*Nov 4, 2025 at 3:44 PM*

I'll add to the pile: don't forget about the PLC web server. The S7-1500 has a built-in web server that's enabled by default in many configurations. If you haven't explicitly disabled it or set credentials, it's accessible from any browser on the network. It shows PLC status, diagnostics, and in some configurations allows variable monitoring.

The web server supports HTTPS but uses a self-signed certificate by default, which most browsers will complain about, which means your engineers will train themselves to click through certificate warnings, which rather defeats the purpose.

---

**ModeratorJim** | Moderator | Posts: 12,456  
*Nov 5, 2025 at 8:22 AM*

Good discussion here. I want to pin a reminder for everyone:

**Please change default passwords on all your equipment.** I know it sounds obvious but we still see it constantly in the field:
- Siemens PLC web server: default depends on configuration, often "admin" or blank
- Hirschmann switches: admin/admin (Classic platform) or admin/private (HiOS)
- Siemens HMI panels: frequently no password set at all
- OPC-UA anonymous access: often enabled by default

If your PLC has a web server with no password, anyone on the network can view your I/O status, diagnostics, and depending on configuration, your tag values. That's a free reconnaissance tool for an attacker.

---

**AutomationDave** | Senior Member | Posts: 1,247  
*Nov 5, 2025 at 10:30 AM*

Thanks everyone, this has been really helpful. So to summarise what I'm taking away:

1. Modbus TCP encryption on S7-1500: not possible natively
2. OPC-UA encryption: possible but certificate management is painful
3. S7CommPlus: make sure we're on V3.0+ firmware for individual keys
4. Network segmentation (VLANs + managed switches + ACLs) is the pragmatic baseline
5. Change all default passwords (adding this to my punch list)
6. Consider an OPC-UA aggregation server as a single point for encrypted northbound data

Going to put together a proposal for our plant manager. The certificate management issue with OPC-UA is going to be the sticking point -- we don't have the IT support bandwidth to manage 15+ certificate rotations.

---

**ICS_Red_Team** | New Member | Posts: 12  
*Nov 18, 2025 at 4:52 PM*

Late to this thread but wanted to add a perspective from the security assessment side.

Network segmentation is necessary but not sufficient. VLANs can be bypassed (VLAN hopping attacks), ACLs can be misconfigured, and the biggest threat is usually an already-compromised engineering workstation that's legitimately on the OT VLAN.

Things I see on almost every assessment:
- Engineering laptops dual-homed (one NIC on IT, one on OT -- bridging the air gap)
- TIA Portal installed on general-purpose workstations that also have email and web browsers
- Shared credentials for PLC access ("everyone uses the same project password")
- No monitoring or logging of PLC access at all -- if someone uploads a modified program at 3 AM, nobody would know

The Modbus encryption question is important but it's one small piece. Start with: who can reach the PLCs, from where, and would you notice if someone did something malicious?

---

**SiemensGuru_UK** | Senior Member | Posts: 3,412  
*Nov 19, 2025 at 9:15 AM*

> Engineering laptops dual-homed

This one. This is the one that keeps me awake at night. We have a strict policy against it but I've caught engineers plugging in a USB WiFi dongle on their TIA Portal laptops "just to quickly check email" while connected to the OT switch. One compromised laptop and VLANs are meaningless.

We're now looking at dedicated engineering workstations that physically live in the control room, no WiFi adapters, no USB ports (epoxy'd shut), and remote access only via a jump server with MFA. It's expensive and the engineers hate it, but after the Triton/TRISIS incident we don't really have a choice.

---

**InstrumentGirl** | Member | Posts: 203  
*Jan 18, 2026 at 2:04 PM*

Following up on this thread -- we implemented the OPC-UA aggregation server approach that SiemensGuru_UK suggested. Running a Kepware KEPServerEX instance on a hardened Windows Server box on the OT VLAN. It talks Modbus TCP to all the PLCs and OPC-UA with SignAndEncrypt to the historian on the IT side.

Total certificate management: 2 certificates (Kepware server + historian client) instead of 30+. Works well. Took about 3 weeks to set up and validate all the tag mappings.

Only downside: single point of failure. If the Kepware box goes down, we lose all historian data. Looking at adding a redundant instance.

---

*Thread locked by ModeratorJim on 2026-02-01: "Good information here, pinning for reference. If you have new questions please start a new thread."*
