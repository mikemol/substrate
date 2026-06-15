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
- **AI-7d — ASPM-dynamic link.** the PCIe edge carries `(structural max, ephemeral current)` — the
  struct/ephemeral split in one edge. Surface: `current_link_speed`/`max_link_speed`. Witness: the
  link conductance is a dynamic edge (gen1 idle / gen4 max), not a fixed value.

## Status

7a discharged (dma_path.py). 7b discharged (igpu_contention.py — package-power shared node).
7c discharged (thermal_gate.py — clock-edge gate; package passive throttle is DPTF firmware-managed,
not sysfs). 7d remains a specified shadow. Shared-node ledger: iMC sink (7a, 7b), package-power (7b),
clock edges (7c); PCIe link (7d) pending — last brick, then AI-7 fully discharged.
