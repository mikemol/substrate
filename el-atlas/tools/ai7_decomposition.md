# AI-7 decomposition (decompose-by-entailment + strictification)

**Target:** add the unmodeled in-path components (from `operational_path_inventory.md`) to the
discovered conductance graph, consumed by the ONE Kron operator (`g_eff` / kron_reduction).

## Shared costructure (strictification)

Every sub-AI adds a **discovered GraphElement** = `(name, kind, value, surface)` where
`kind in {series-link, shunt, gate, dynamic}`, consumed by the SAME `g_eff` solve. The new elements
and the existing compute path **share resource NODES** — the iMC (DRAM sink), the package-power node,
the clock edges. A shared node IS the contention (the `G_AND` cap), exactly like cores-on-controller.

- **Composition:** the combined graph is multi-terminal — the compute sub-network and the new
  sub-networks meet at shared nodes (iMC / power / clock); `g_eff` over the combined graph captures
  contention/gating by construction.
- **Entailment:** if each sub-network reduces correctly AND they share the iMC/power/clock nodes,
  the combined `g_eff` gives the contended/gated effective conductance — no new operator needed.

## Sub-AIs (bricks)

- **AI-7a — DMA sub-network.** device(GPU/NVMe) -> host-bridge (fan-in apex, shared node) -> IOMMU
  (inline series; primarily a LATENCY element) -> iMC (shared sink). Surfaces: lspci topology,
  `/sys/class/iommu`, DMI iMC ceiling. Witness: the DMA path reduces; the iMC is shared with the
  compute path; concurrent DMA steals iMC BW from compute. **[DISCHARGE THIS PASS -> dma_path.py]**
- **AI-7b — iGPU contention edge. [DISCHARGED -> igpu_contention.py]** iGPU as a parallel consumer
  (`G_OR`) on the iMC BW node AND the package-power node -> reduces what the cores get. Surface:
  `drm/card[0-9]` vendor 0x8086, `intel-rapl:0` PL0. Witnessed (PASS): iGPU detected; cores' iMC BW
  51.2 -> 38.4 with iGPU pulling 13 GB/s; cores' PL0 share 45W -> 37W (82% compute headroom) with
  iGPU @ 8W. Adds the package-power shared NODE (7a only had the iMC sink).
- **AI-7c — thermal gate. [DISCHARGED -> thermal_gate.py]** temperature as a multiplier g(T) closing
  the clock edge(s) (ties two-clock + TDP). Surface: `thermal_zone*`. Witnessed (PASS): trip = 100C
  (acpitz hot); pkg @ 46C -> g=1 (free); clamps above. FINDING: x86_pkg/TCPU passive trips are
  DISABLED in sysfs (-274 sentinel) -> package passive throttle is DPTF/INT3400 FIRMWARE policy, not
  kernel trips (surface present but firmware-unpopulated, like EDAC/IBECC). OPEN (validate-outputs):
  whether the gate is common-mode (both clocks -> ridge invariant) or core-only (ridge moves) is
  empirically testable (drive temp, watch ridge) -- NOT asserted.
- **AI-7d — ASPM-dynamic link. [DISCHARGED -> aspm_link.py]** the PCIe edge carries `(structural max,
  ephemeral current)`. Surface: `current_link_speed`/`max_link_speed`. Witnessed (PASS): current
  2.5 GT/s (2.0 GB/s, gen1 ASPM-idle) / max 16 GT/s (15.8 GB/s gen4) x8 -> structural edge = max,
  link_state factor 0.13. Same bound x ephemeral-state decomposition as clock cur/max and strategy
  efficiency; the state cancels in structural ratios.

## Status

**AI-7 FULLY DISCHARGED.** 7a dma_path.py · 7b igpu_contention.py · 7c thermal_gate.py · 7d
aspm_link.py. Shared-node/edge ledger COMPLETE: iMC sink (7a, 7b), package-power (7b), clock edges
(7c), PCIe link (7d). All four are discovered GraphElements consumed by the ONE Kron operator over
shared nodes. Two cross-cutting findings: (i) several surfaces are present-but-firmware-unpopulated
(EDAC/IBECC, the -274 thermal trips/DPTF) — a third gate-type beyond privilege/unenumerated; (ii) the
dynamic edges (clock cur/max, PCIe cur/max) and the eval strategy all share ONE decomposition:
structural bound x ephemeral state, the state cancelling in structural ratios.
NEXT: integrate these four elements into jea_perf_engine's graph builder (currently standalone
pilots); then AI-4 (root RAPL energy) and the live dispatcher capstone.
