# AI ledger (WAL cotype) — kernel-perf / el-atlas hardware program

Single source of truth for all action items. Updated atomically with the work (cotype-as-WAL).
"Everything remaining is part of a named AI." Other substrate arcs (CD follow-on, fuel sweep,
el-atlas Frontier) live in the project_open_threads memory, not here.

## CLOSED

- **AI-1** governing-law-before-special-case discipline -> memory.
- **AI-2** het-dispatch validated vs ground truth (+ corrected CPU-favored overclaim) -> het_validate.py.
- **AI-3** six perf pilots -> ONE engine (Kron solve + views) -> jea_perf_engine.py.
- **AI-5** hunt-opacity-after-green discipline -> memory.
- **AI-6** engine views validated vs real measured bottlenecks -> engine_validate.py.
- **AI-7** unmodeled in-path components -> conductance graph (decomposed; ai7_decomposition.md):
  - 7a DMA sub-network (dma_path.py) · 7b iGPU contention (igpu_contention.py) ·
    7c thermal gate (thermal_gate.py) · 7d ASPM-dynamic link (aspm_link.py). All discharged.
- **AI-8** wire interned DMI into discover() + engine edge-weights -> dmi_intern.py + topology_breakers + engine.
- **AI-9** validate-outputs-not-inputs discipline -> memory.
- **AI-13** firmware-unpopulated-surface gate-type (G9 this turn) -> memory feedback_firmware_unpopulated_surface.
- **bw_alloc rung** BW probe is strategy-laden -> DMI structural ceiling + dmi_intern headroom.
- **AI-4** chassis power -> CLOSED TO HARDWARE LIMIT (ai4_chassis_power.md): SoC proxy package+dGPU
  = 59.7 W measured; psys permanently unavailable (firmware-unpopulated, unfixable by BIOS/microcode,
  web-confirmed); true platform power needs an external meter.
- **AI-10** engine integration -> perf_graph_integrated.py. 10a GraphElement registry (all 4 kinds
  from discover()) · 10b combined multi-terminal graph builder + ONE g_eff · 10c COMPOSITION verified:
  compute_BW idle 51.2 > +DMA 43.2 > +DMA+iGPU 30.4 (contenders stack at iMC); thermal(130C)->12.2
  (clock gate); ASPM gen1-idle steals less than gen4. Bricks compose, not just coexist. Supersedes the
  simplified perf_graph; the engine now models the full operational path over shared nodes.
- **AI-11** live dispatcher (CONTROL LOOP, session-origin capstone) -> live_dispatcher.py. Polls live
  ephemeral state (governor/clock/thermal/ASPM-link/dGPU-power) -> re-solves the integrated graph (ONE
  Kron op) each window -> emits the current bottleneck + optimal dispatch f*, anytime/immediate. The
  decision is a live function of state: f* rises as the link ramps gen1->gen4 (0.02->0.10), compute_BW
  falls as temp rises (30.4->12.2), the bottleneck identity shifts (PCIe -> iMC -> thermal). The static
  model is now a continual controller. (On-device actuator = AI-11b.)
- **AI-11b** on-device actuator -> live_dispatcher_ondevice.py. A persistent GPU megakernel (ONE launch,
  resident until host stop) steered by ZERO-COPY mapped-memory CPU stores -- host writes decisions, the
  kernel reads them over PCIe (volatile + threadfence_system), no copy/stream/sync. Witnesses PASS:
  persistent (one launch across 4 pushes), async-push, live-steer (work-bands {1,3,5,9} match pushed
  knobs exactly). KEY FINDING (the right primitive): async DEVICE-buffer writes via a separate stream
  do NOT reach a concurrently-resident kernel in cupy (stop never landed -> timeout); ZERO-COPY pinned/
  mapped host memory (UVA pointer device-accessible) is the correct host->persistent-kernel channel.
  Deploys AI-11 on the GPU = the jea on-device-dispatcher debt. Toy bucket-work stands in for real work
  distribution (production fill-in); the MECHANISM is complete.

## OPEN (named)

- **AI-12 — CHASSIS-CAP BINDING TEST. [CLOSED -> chassis_cap_test.py]** Measured CPU-alone 48.3W ->
  combined 51.7W (x1.07); dGPU-alone 25.9W -> combined 30.3W (x1.17, at its 30W cap); alone-sum 74.1W
  vs combined 82.0W (111%). Both sides ran AT/ABOVE their alone draw under combined -> chassis does NOT
  bind at this load -> het-sum is ADDITIVE in power (not sub-additive). AI-4's "BINDS" RETRACTED
  (over-claimed; it compared to nameplate caps not alone-draws). The AI-7 chassis-coupling node exists
  structurally but does not bind at measured loads. Original spec retained below.
- **AI-12 — CHASSIS-CAP BINDING TEST (small).** AI-4's "chassis BINDS" is over-claimed: it compared
  combined draw (59.7 W) to the nameplate cap sum (75 W), but neither side hit its own cap. Measure
  P_cpu_alone + P_gpu_alone (RAPL + nvidia-smi, root, performance governor) vs P_combined: if
  combined < alone-sum, the chassis throttles; else the workload just isn't maxing. Distinguishes
  chassis-throttle from not-maxed. Extends power_probe_root.py with alone/alone/combined phases.

## Status

ALL AIs CLOSED: AI-1..12 + 11b + 13 + bw_alloc + AI-4. The kernel-perf nedge program is COMPLETE
end-to-end and ground-truthed: discover -> structural conductance graph -> Kron settle -> views ->
host control loop -> on-GPU persistent-megakernel actuator (zero-copy steered); chassis-cap measured
non-binding (het-sum additive in power at load). No open named AIs. Production fill-ins (AI-11b real
work distribution; external wall meter for true platform power) are deployment, not modeling.
