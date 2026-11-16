---
name: feedback_firmware_unpopulated_surface
description: "a hardware introspection surface can be PRESENT in the kernel yet produce no data (reads 0/static/empty) because firmware/board doesn't populate it — a third gate-type, immune to root"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When a hardware introspection surface reads **0 / static / empty**, there are THREE distinct gate-types
— distinguish them before acting:

1. **not-yet-enumerated** — the fact is in a different surface you haven't read (fix: find the surface).
2. **privilege-gated** — present but root-only (fix: read as root; e.g. RAPL energy_uj, full DMI, MSR).
3. **present-but-firmware-unpopulated** — the surface ENUMERATES (appears in sysfs/powercap) but the
   firmware/board never populates it, so it reads 0/static **even as root**. NOT fixable by privilege,
   and usually not by BIOS/microcode (it's a board hardware-design omission). This is the one that
   masquerades as the others.

Instances (kernel-perf hardware arc, 2026-06-14), all confirmed:
- **RAPL psys** (platform domain): enumerates but energy_uj static (~0.3 W under 35.9 W load), 0 even
  as root. Intel ADL datasheet: PSys must be sourced from charger/VR + routed via SVID + BIOS-enabled,
  "MSR reads 0 if not valid"; consumer/gaming laptops omit the wiring. UNFIXABLE by BIOS or microcode
  (web-confirmed). HP Victus board 8C2D doesn't route it.
- **EDAC/igen6_edac**: loads but binds zero devices — needs in-band ECC enabled in firmware, absent.
- **thermal passive trips**: x86_pkg_temp reads -274 C sentinel = disabled; package throttle is
  DPTF/INT3400 firmware policy, not kernel trips.
- **battery current/power**: BAT0 reports voltage only; power_now / hwmon power1_input = 0 even as root.
- **ASPM LnkSta detail**: needs root (privilege-gated, distinct — included as the contrast case).

**Why:** a 0-reading is ambiguous across the three gates; assuming "needs root" wastes effort on a
firmware-unpopulated surface that root can't fix, and assuming "broken" misses a privilege gate.
**How to apply:** on a 0/static read, (a) check if root changes it (privilege vs firmware); (b) if
0-even-as-root, it's firmware-unpopulated — check the datasheet / known-issues (DELEGATE a web-search
agent — it's documented for common hardware), don't chase a BIOS/microcode "fix" that doesn't exist;
(c) find an alternative surface or accept it's unavailable on this hardware. Refines the surface
taxonomy of [[feedback_hunt_opacity_after_green]]; sibling of [[feedback_validate_outputs_not_inputs]].
