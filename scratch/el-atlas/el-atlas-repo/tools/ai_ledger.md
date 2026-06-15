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

## OPEN (named)

- **AI-11b — ON-DEVICE ACTUATOR.** The control loop (AI-11) runs host-side and EMITS decisions;
  AI-11b wires them into the on-GPU dispatcher (persistent megakernel + device work queue / indirect
  launches acting on the bottleneck + f* decisions). This is the standing jea "on-device dynamic
  dispatcher" debt -- the deployment of the now-built control algorithm.

- **AI-12 — CHASSIS-CAP BINDING TEST (small).** AI-4's "chassis BINDS" is over-claimed: it compared
  combined draw (59.7 W) to the nameplate cap sum (75 W), but neither side hit its own cap. Measure
  P_cpu_alone + P_gpu_alone (RAPL + nvidia-smi, root, performance governor) vs P_combined: if
  combined < alone-sum, the chassis throttles; else the workload just isn't maxing. Distinguishes
  chassis-throttle from not-maxed. Extends power_probe_root.py with alone/alone/combined phases.

## Status

AI-1..11 + 13 + bw_alloc + AI-4 closed (the kernel-perf nedge program is complete as a HOST-SIDE
live controller). Open: AI-11b (on-device actuator -- deploy the control loop on the GPU; = the jea
on-device-dispatcher debt), AI-12 (chassis-cap binding test, small). Nothing remaining is un-named.
Pick up any open AI from this file.
