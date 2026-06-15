# AI-4: chassis power budget — verdict (root-blocked on this hardware) + recipe

**Goal:** pin the chassis (`psys`) power budget via combined CPU+GPU load measurement, turning the
het-dispatch `r_cpu + r_gpu` upper bound into an exact cap.

## Verdict: NOT user-measurable on this box (tested the wall)

All user-accessible chassis-power surfaces are dead here:

| surface | result |
|---|---|
| `BAT0/power_now` (ACPI) | **0** (broken) |
| `BAT0/current_now` | **empty** |
| `hwmon2/power1_input` (BAT0) | **0** |
| `BAT0/voltage_now` | 14984 mV (works) |
| `/sys/class/powercap/intel-rapl:0/energy_uj` | **root-gated** |
| AC adapter | **offline** (on battery), ADP power not exposed |

The battery EC reports **voltage but not current/power** — a *fourth* instance of the
present-but-firmware-unpopulated category (cf EDAC/IBECC, the -274 °C thermal trips/DPTF, ASPM detail).
So the chassis aggregate cannot be read unprivileged on this machine.

## What IS user-measurable

- **dGPU power**: `nvidia-smi --query-gpu=power.draw,enforced.power.limit` (enforced cap ~30 W of 75 W).
- So the GPU half of the het-sum power is unprivileged; only the **CPU-package + chassis aggregate**
  need root.

## Root recipe (for whoever has sudo)

```
# combined CPU+GPU load in one shell, then in another:
sudo turbostat --quiet --show PkgWatt,GFXWatt,CorWatt --interval 1
# (PkgWatt = CPU package incl iGPU via RAPL MSR);  alongside:
nvidia-smi --query-gpu=power.draw --format=csv -l 1     # dGPU, no sudo
# chassis aggregate ~ PkgWatt + dGPU draw + platform; or read RAPL psys:
sudo cat /sys/class/powercap/intel-rapl:1/energy_uj   # psys domain, delta over 1s = platform W
```
The chassis cap = the sustained combined draw the platform allows; if `Pkg + dGPU` saturates below
`PL0(45W) + dGPU(30W) = 75W`, the chassis envelope is binding (het-sum is then sub-additive in power).

## Measured (root, venv python, performance EPP, combined CPU+GPU load)

CPU package (incl iGPU) = **35.9 W** (RAPL, valid); dGPU = **23.8 W** (nvidia-smi); combined SoC proxy
= **59.7 W**. psys = 0.3 W (BROKEN, ignored). This is the SoC PROXY (package+dGPU), NOT the true
chassis aggregate (excludes display/RAM/VRM/peripherals). The "chassis binds" auto-conclusion is
OVER-CLAIMED: neither side hit its own cap (CPU 35.9<45, dGPU 23.8<30), which could be the chassis
throttling OR the workload not maxing them — distinguishing needs P_cpu_alone + P_gpu_alone vs combined.

## psys broken = KNOWN/DOCUMENTED on Alder Lake consumer laptops (web research)

The static psys counter is EXPECTED, not a fault. PSys (platform domain) needs OEM/BIOS platform
wiring that consumer/gaming laptops omit; the domain still ENUMERATES (kernel exposes it for the CPU
model) but the MSR is never populated -> energy_uj static, even as root. package-0/core/uncore work;
psys doesn't. Confirms the present-but-firmware-unpopulated category with upstream sources:
- Intel kernel PSys patch (Pandruvada): "not all systems will support PSys".
- Vince Weaver RAPL page: PSys needs platform+BIOS support absent in many systems.
- linux-pm "lose the psys counter"; Intel Community "rapl domain psys issues".
True platform/wall power on such hardware needs an EXTERNAL meter (battery EC also dead here).

## Status

AI-4 is **root-blocked on this hardware**. CONFIRMED: battery `power1_input` reads 0 EVEN AS ROOT
(2026-06-14, root@cassian) -> not privilege, the EC genuinely produces no current/power (only voltage)
-> present-but-firmware-unpopulated, immune to root. But RAPL energy_uj IS just privilege-gated and is
root-readable, so the empirical close runs via RAPL: **`sudo python3 power_probe_root.py`** (measures
CPU-package + psys via RAPL energy deltas under self-generated combined CPU+GPU load, + dGPU via
nvidia-smi; reports whether the chassis envelope binds below PL0+dGPU). Structurally it's the
package/chassis shared-power NODE already added in AI-7b/7c; only the magnitude needs the root run.
