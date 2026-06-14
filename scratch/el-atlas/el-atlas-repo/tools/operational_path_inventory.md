# Operational-path inventory (HP Victus 15: i7-12650H / RTX 4050)

Which hardware surfaces are in the COMPUTE/MEMORY/POWER conductance path vs edge peripherals.
Research-agent sweep, read-only/unprivileged. The point: find in-path components we DON'T model.

## In the operational path

| Component | surface | conductance / gate | modeled? |
|---|---|---|---|
| P/E cores (6+4 hybrid) | `/sys/devices/system/cpu`, intel_pstate | compute; core clock domain | yes |
| L1/L2/L3 + LLC sharing | `cpu*/cache/shared_cpu_list` | BW/latency; coherence | yes |
| iMC + DDR5 (1 NUMA) | `intel-rapl:0:1` (uncore), EDAC (unpopulated) | DRAM BW; uncore clock | yes |
| **PCIe root complex / host bridge 00:00.0** | `lspci -tvnn`, iommu_groups/1 | **DMA fan-in apex — all device DMA funnels here** | **NO** |
| dGPU root port 00:01.0 (CPU PCIe) | `current_link_speed`=2.5 idle / max 16 | CPU↔dGPU BW gate (ASPM-dynamic) | partial |
| dGPU 01:00.0 (AD107) + copy engines | `drm/card1`, renderD128 | GPU compute + DMA | yes |
| **iGPU 00:02.0 (UHD, on-package)** | `drm/card2`, shares `intel-rapl:0` | **steals DRAM BW + package power from cores** | **NO** |
| NVMe via CPU port 00:06.0 | both gen4 16 GT/s (no downshift) | storage→DRAM feed | n/a |
| **IOMMU / intel-iommu (DMAR x2, ENABLED)** | `/sys/class/iommu/dmar*`, ACPI DMAR, 19 groups | **inline on EVERY DMA path: IOTLB-miss latency** | **NO** |
| RAPL tree (package/core/uncore/psys) | `/sys/class/powercap/intel-rapl*` | power budget caps clocks | yes |
| **Thermal zones (pkg/TCPU/acpitz/INT3400 DPTF)** | `/sys/class/thermal/thermal_zone*` | **active gate: PROCHOT/pkg-temp clamps clocks** | **NO** |
| C-states C1E…C10 / LPIT | `cpu0/cpuidle/state*`, ACPI LPIT | latency gates (exit 0→230 µs) | no |
| GNA accelerator 00:08.0 | `lspci -s 00:08.0` | on-die engine; in-path only if driven | conditional |

## The surprising in-path elements to ADD to discover()

1. **IOMMU inline on all DMA** — translation latency on GPU/NVMe↔RAM, currently ignored. A latency
   conductance element (IOTLB). Detect: `/sys/class/iommu/dmar*`; quantify (IOTLB stats) needs root.
2. **Single PCIe host bridge = DMA fan-in apex** — the conductance-network analog of the memory
   controller, but for *DMA*: all devices' DMA share it (a shared SERIES resource). `lspci -tvnn`.
3. **iGPU as a contention edge** — shares the iMC (DRAM BW) AND the `intel-rapl:0` package power with
   the cores. A parallel consumer on two already-shared resources. `drm/card2` + rapl.
4. **Thermal as an active valve** — pkg temp clamps clocks (ties to the TDP / two-clock findings: the
   clock gate has a thermal cause too). `thermal_zone*/temp` + trip points + INT3400 DPTF policy.
5. **dGPU ASPM-dynamic link** — gen1 idle / gen4 max; a *variable* conductance edge, not a fixed link.
   `current_link_speed` (poll); LnkSta detail needs root.
6. **EDAC unbound** — the iMC channel/rank topology surface exists but no driver bound; loading
   `igen6_edac` would expose memory-channel structure.

## Edge peripherals — dismissed (not in compute path)

USB/xHCI, Thunderbolt, I2C SerialIO, HECI/ME, SD reader (RTS5288), MT7921 wifi, Realtek GbE, eSPI/EC,
HD-audio (PCH + NVIDIA HDA), SMBus, SPI flash, NHLT, webcam/HID, battery/charger hwmons.

## Privilege note

All in-path components are DETECTABLE read-only/unprivileged. Only numeric MAGNITUDES need root:
ASPM LnkSta, RAPL joules/PL caps, IOMMU/IOTLB stats, iMC channel topology (EDAC driver), deeper GPU
telemetry.
