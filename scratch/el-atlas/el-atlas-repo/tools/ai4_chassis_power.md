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

## Status

AI-4 is **root-blocked on this hardware** (battery EC firmware-unpopulated for current/power; RAPL
root-gated). Structurally it's the package/chassis shared-power NODE already added in AI-7b/7c (power
contention + thermal gate); only the magnitude needs root. Not fabricated. Recipe above closes it the
moment a root reading (or external wall meter) is available.
