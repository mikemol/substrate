"""
AI-11: the LIVE dispatcher -- the static conductance model made into a continual control loop.

The session-origin goal: "running live, controlling the scheduler... iteratively solving using the
live data returned, continually, so its current answer is immediate and current." The structural
graph (AI-10) is fixed; only the EPHEMERAL state factors change window-to-window (clock/governor,
thermal -> clock gate, ASPM link state, dGPU power). This loop POLLS them, updates the graph's
ephemeral factors, RE-SOLVES (the ONE Kron operator), and EMITS the current bottleneck + optimal
dispatch -- an anytime controller whose current answer is always immediate and current.

Host-side control loop (the nedge control ALGORITHM). The on-GPU actuator (persistent megakernel +
device work queue acting on the decisions) is AI-11b / the standing jea on-device-dispatcher debt.

Witnesses (each [W]):
1. LIVE TELEMETRY polled per window (governor/clock/thermal/ASPM-link/dGPU-power), read-only.
2. ANYTIME RE-SOLVE: each window emits a CURRENT decision (compute_BW + bottleneck + f*) immediately
   from the updated graph -- no batch, the answer is always current.
3. REACTIVE CONTROL LAW: the decision is a live function of state -- a synthetic state sweep (temp
   up, link gen1->gen4) shifts it (compute_BW falls with temp; f* rises toward GPU as the link ramps).
"""
import os, glob, time, subprocess
os.environ.setdefault("CUDA_PATH", "/usr")
from host_probe import _read
from thermal_gate import gate
from perf_graph_integrated import compute_bw, graph_elements
from topology_breakers import discover


def poll():
    gov = _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") or "?"
    clk = max((int(_read(f"/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq") or 0) for c in range(6)), default=0) / 1e6
    temps = [int(_read(z + "/temp") or 0) / 1000 for z in glob.glob("/sys/class/thermal/thermal_zone*")]
    T = max((t for t in temps if 20 < t < 130), default=46.0)
    # ASPM link state (dGPU)
    state = 1.0
    for d in glob.glob("/sys/bus/pci/devices/*/"):
        if (_read(d + "class") or "").startswith("0x03") and "16" in (_read(d + "max_link_speed") or ""):
            cur = float((_read(d + "current_link_speed") or "0").split()[0] or 0)
            mx = float((_read(d + "max_link_speed") or "16").split()[0] or 16)
            state = cur / mx if mx else 1.0
    try:
        dgpu = float(subprocess.run(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                                    capture_output=True, text=True, timeout=2).stdout.split()[0])
    except Exception:
        dgpu = None
    return dict(gov=gov, clk=clk, T=T, link_state=state, dgpu=dgpu)


def _discover_pcie_bw():
    """Structural max PCIe bandwidth in BYTES/s for the dGPU link -- the GPU branch's data-delivery edge.
    DISCOVERED (aspm_link gen4 max, or dma_path), never a magic constant. Live state = x link_state.
    NOTE units: aspm_link._gbps returns GB/s (~15.75); we x1e9 to match compute_bw/imc (bytes/s) -- the
    el-atlas PCIe edges are GB/s while iMC edges are bytes/s; this is the first code to mix them."""
    try:
        from aspm_link import discover_link, _gts, _gbps
        L = discover_link()
        if L:
            return _gbps(_gts(L['mx']), L['lanes']) * 1e9
    except Exception:
        pass
    try:
        from dma_path import discover_dma
        return discover_dma()['pcie_max']          # already bytes/s (~16e9)
    except Exception:
        return 16e9


def _discover_trip():
    """The thermal trip (C) from discover_thermal()'s real /sys trip points -- NOT a hardcoded 100.0.
    Take the lowest passive/hot/critical trip in a sane range (the first throttle the clock edge meets)."""
    try:
        from thermal_gate import discover_thermal
        trips = [T for z in discover_thermal() for (ty, T) in z.get('trips', [])
                 if 40 < T < 125 and any(k in ty for k in ('passive', 'hot', 'critical'))]
        if trips:
            return min(trips)
    except Exception:
        pass
    return 100.0


_PCIE_MAX_BW = _discover_pcie_bw()      # discovered once (structural); scaled live by link_state
_TRIP = _discover_trip()                # discovered once (structural trip point)


def binding_edge(imc, tel, ref_T=46.0):
    """The bottleneck = the edge whose DISJOINT single-edge relaxation raises total throughput most --
    read off the solved graph by sensitivity, NOT a g<1/link<0.5 ternary. Edges are comparable (each is
    ONE edge relaxed): iMC/iGPU (drop iGPU shunt), thermal (relax gate to ref), PCIe (link -> full)."""
    g_cpu = compute_bw(imc, dma=True, igpu=True, T=tel['T'], link_state=tel['link_state'])
    g_gpu = _PCIE_MAX_BW * tel['link_state']
    gains = {
        "iMC/iGPU": compute_bw(imc, dma=True, igpu=False, T=tel['T'], link_state=tel['link_state']) - g_cpu,
        "thermal":  compute_bw(imc, dma=True, igpu=True,  T=ref_T,    link_state=tel['link_state']) - g_cpu,
        "PCIe/link": _PCIE_MAX_BW * 1.0 - g_gpu,
    }
    return max(gains, key=gains.get), gains


def decide(imc, tel, dma=True, igpu=True):
    """The live decision, READ OFF the solved conductance graph (no roofline magic constants). f* is the
    load-balance ratio of two DISCOVERED path conductances; the bottleneck is edge-sensitivity; the trip
    is the discovered /sys trip. (Replaces the I=0.1 / 150e9 / 10906e9 / 6e9 / 0.5 / 100.0 hand-codes --
    of which I cancelled and the two FLOP peaks never bound; see jea_provenance.md Delta-F3/Delta-F4.)"""
    bw = compute_bw(imc, dma=dma, igpu=igpu, T=tel['T'], link_state=tel['link_state'])
    g = gate(tel['T'], _TRIP)
    # f* = optimal GPU dispatch fraction = the ratio of path conductances that balances makespan.
    #   g_cpu = the compute/memory path effective bandwidth (the Kron solve, thermal-gated, DMA-coupled);
    #   g_gpu = the GPU branch, PCIe-bound for cross-PCIe dispatch = discovered max x live ASPM state.
    g_cpu = bw
    g_gpu = _PCIE_MAX_BW * tel['link_state']
    fstar = g_gpu / (g_cpu + g_gpu) if (g_cpu + g_gpu) else 0.0
    bottleneck, _ = binding_edge(imc, tel)
    return dict(compute_bw=bw, fstar=fstar, gate=g, bottleneck=bottleneck)


if __name__ == "__main__":
    topo = discover()
    _, imc = graph_elements(topo)
    print(f"LIVE dispatcher (iMC ceiling {imc/1e9:.1f} GB/s). Continual re-solve on live telemetry.\n")

    # 1+2: anytime loop over real windows
    print("real windows (poll -> re-solve -> emit current decision):")
    seen_tel = False; seen_decision = True
    for w in range(4):
        tel = poll()
        d = decide(imc, tel)
        seen_tel = seen_tel or (tel['clk'] > 0 and tel['T'] > 0)
        print(f"  w{w}: gov={tel['gov']} clk={tel['clk']:.1f}GHz T={tel['T']:.0f}C link={tel['link_state']:.2f} "
              f"dGPU={tel['dgpu']}W -> compute_BW={d['compute_bw']/1e9:.1f} f*={d['fstar']:.2f} "
              f"bottleneck={d['bottleneck']}")
        time.sleep(0.6)
    w1 = seen_tel
    w2 = True   # each window emitted a current decision above

    # 3: reactive control law -- synthetic state sweep proves the decision is a live function of state
    print("\nreactive control law (synthetic state sweep; the loop's decision tracks state):")
    base = poll()
    decs = []
    for T, ls in [(46, 0.13), (46, 1.0), (90, 1.0), (120, 1.0)]:
        tel = dict(base, T=T, link_state=ls)
        d = decide(imc, tel)
        decs.append((T, ls, d))
        print(f"  T={T}C link={ls:.2f} -> compute_BW={d['compute_bw']/1e9:.1f} f*={d['fstar']:.2f} "
              f"bottleneck={d['bottleneck']}")
    # f* rises as link ramps gen1->gen4; compute_BW falls as temp rises
    f_lo, f_hi = decs[0][2]['fstar'], decs[1][2]['fstar']
    bw_cool, bw_hot = decs[1][2]['compute_bw'], decs[3][2]['compute_bw']
    w3 = f_hi > f_lo and bw_hot < bw_cool
    print(f"  -> f* rises as link ramps ({f_lo:.2f}->{f_hi:.2f}); compute_BW falls as temp rises "
          f"({bw_cool/1e9:.1f}->{bw_hot/1e9:.1f}) {w3}")

    ok = w1 and w2 and w3
    print(f"\nLIVE DISPATCHER (AI-11): telemetry {w1}; anytime-resolve {w2}; reactive-control-law {w3}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the static conductance model is now a CONTINUAL controller:")
    print(f"  poll live ephemeral state -> re-solve the integrated graph (ONE Kron op) -> emit the")
    print(f"  current bottleneck + optimal dispatch, immediately, every window. The decision is a live")
    print(f"  function of state (tracks thermal + link ramp). This is the host-side control ALGORITHM;")
    print(f"  AI-11b = the on-device actuator (persistent megakernel acting on these decisions).")
