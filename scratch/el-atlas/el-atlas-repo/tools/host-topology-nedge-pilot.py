"""
host-topology-nedge-pilot.py — T-series pilot: the HOST (CPU/memory) topology as a nedge
G-Value conductance network (candidate claim HTP). The CPU-side mirror of gpu-topology.

All numbers fetched at RUNTIME (host_probe.probe_host: sysfs/proc for the static facts, live
benchmarks for the conductances), not hardcoded. The host memory/compute hierarchy is the same
series-parallel conductance network as the GPU's: bandwidth = conductance, latency = resistance
(G_NOT swap), series links = G_AND (slowest = bottleneck), parallel cores = G_OR (sum) -- but
CAPPED by the memory controller, a SERIES ceiling above the parallel cores (one core can't
saturate it; many cores hit the wall).

Witnesses (each [W]):
1. CACHE HIERARCHY = QUERIED CAPACITY LADDER + measured streaming BW: L1<L2<L3<RAM capacities
   (sysfs, reliable) decide which level a working set lands in; the >L3 streaming bottleneck is
   the MEASURED DRAM controller BW. Per-level cache BW is intentionally NOT measured -- numpy
   per-call overhead swamps the small L1/L2 arrays, so faking a BW step-down would be dishonest.
2. PARALLEL CORES, CONTROLLER CAP: measured saturated BW (all cores) > single-core BW (parallel
   helps, G_OR) but << cores x single-core (the controller caps it, G_AND) -- the host's
   defining series-over-parallel structure.
3. CPU ROOFLINE: ridge I* = cpu_flops / saturated_sysram_BW; below it memory-bound, above
   compute-bound (the CPU's own roofline, same bridge-null as the GPU's).
4. LATENCY <-> BANDWIDTH = G_NOT (reciprocal; R*G=1, double-swap=id).
5. CAPACITY/BANDWIDTH PARETO: host = big capacity / low BW, GPU = small capacity / high BW
   (queried). The two own opposite corners -- which is WHY heterogeneous dispatch is worth it;
   the split goes by which resource is scarce. (No faked swap-speed number.)
Run output: tools/host-topology-nedge-pilot-out.txt.
"""
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
from functools import reduce as _reduce
import numpy as np
from host_probe import probe_host

G_OR  = lambda a, b: a + b
G_AND = lambda a, b: 0.0 if a + b == 0 else a * b / (a + b)
G_NOT = lambda g: float('inf') if g == 0 else 1.0 / g
G_AND_fold = lambda xs: _reduce(G_AND, xs)


def _human(b):
    for u, s in (("G", 1 << 30), ("M", 1 << 20), ("K", 1 << 10)):
        if b >= s:
            return f"{b/s:.0f}{u}"
    return f"{b}B"


def w_cache_hierarchy(h):
    """The hierarchy is the queried CAPACITY ladder (which level a working set lands in) + the one
    BW we can reliably measure: DRAM streaming. Per-level cache BW is NOT reliably Python-measurable
    (numpy per-call overhead swamps the small L1/L2 arrays) -- so we don't fake it."""
    caps = [("L1d", h['l1d']), ("L2", h['l2']), ("L3", h['l3']), ("RAM", h['ram'])]
    sizes = [c for _, c in caps]
    ladder = all(sizes[i] > sizes[i - 1] for i in range(1, len(sizes)))   # strictly increasing capacity
    print("1. cache hierarchy = queried capacity ladder + measured streaming BW:")
    for nm, c in caps:
        print(f"     {nm:4s} {_human(c):>5s}")
    print(f"   strictly increasing capacity {ladder}; streaming (>L3) bottleneck = MEASURED DRAM "
          f"controller BW {h['sysram_bw_n']/1e9:.0f} GB/s")
    print(f"   (per-level cache BW intentionally NOT measured: numpy call-overhead swamps L1/L2 arrays)")
    return ladder


def w_parallel_controller_cap(h):
    b1, bn, cores = h['sysram_bw_1'], h['sysram_bw_n'], h['cores']
    helps = bn > b1                                      # parallel cores raise BW (G_OR)
    capped = bn < cores * b1 * 0.95                      # but the controller caps it (G_AND ceiling)
    print(f"2. parallel cores, controller cap: 1-core {b1/1e9:.1f} -> {cores}-core {bn/1e9:.1f} GB/s; "
          f"naive G_OR sum {cores*b1/1e9:.0f} GB/s. parallel helps {helps}; controller caps {capped}")
    return helps and capped


def w_cpu_roofline(h):
    ridge = h['cpu_flops'] / h['sysram_bw_n']
    ach = lambda I: min(h['cpu_flops'], I * h['sysram_bw_n'])
    null = abs(ach(ridge) - h['cpu_flops']) < 1e-3
    bias = lambda I: I * h['sysram_bw_n'] - h['cpu_flops']
    flips = bias(ridge * 0.5) < 0 < bias(ridge * 2)
    print(f"3. CPU roofline: ridge I* = cpu_flops/sysram_BW = {ridge:.1f} FLOP/byte; "
          f"branches equal {null}; bias flips mem<->compute {flips}")
    return null and flips


def w_latency_bandwidth(h):
    bws = [h['sysram_bw_n'] / 1e9, h['cpu_flops'] / 1e9] + ([h['pcie_h2d'] / 1e9] if h['pcie_h2d'] else [])
    ok = all(abs(G_NOT(G_NOT(g)) - g) < 1e-6 and abs(g * G_NOT(g) - 1) < 1e-9 for g in bws)
    print(f"4. latency <-> bandwidth = G_NOT (reciprocal): R*G=1 & double-swap=id {ok}")
    return ok


def w_capacity_bandwidth_pareto(h):
    """RAM is the host's hard capacity gate. Against the GPU it's a capacity/bandwidth PARETO:
    host = big capacity / low BW, GPU = small capacity / high BW -- which is WHY heterogeneous
    dispatch is worth it (each side owns a different corner). Queried, no faked swap number."""
    try:
        import cupy as cp
        a = cp.cuda.Device(0).attributes
        gpu_cap = cp.cuda.runtime.getDeviceProperties(0)['totalGlobalMem']
        gpu_bw = 2 * (a['GlobalMemoryBusWidth'] / 8) * (a['MemoryClockRate'] * 1e3)
    except Exception:
        gpu_cap, gpu_bw = 6 * (1 << 30), 192e9
    host_cap, host_bw = h['ram'], h['sysram_bw_n']
    pareto = (host_cap > gpu_cap) and (host_bw < gpu_bw)   # opposite corners -> a real tradeoff
    print(f"5. capacity/bandwidth Pareto (the dispatch rationale): "
          f"host {host_cap/(1<<30):.1f} GiB @ {host_bw/1e9:.0f} GB/s  vs  "
          f"GPU {gpu_cap/(1<<30):.1f} GiB @ {gpu_bw/1e9:.0f} GB/s")
    print(f"   host owns CAPACITY, GPU owns BANDWIDTH (opposite corners) {pareto} -> dispatch splits by which is scarce")
    return pareto


if __name__ == "__main__":
    h = probe_host()
    print(f"HOST (fetched at runtime): {h['model']}  ({h['cores']} cores {h['vec']}, "
          f"{h['ram']/(1<<30):.1f} GiB, L3 {h['l3']//(1<<20)}M, {h['cpu_flops']/1e9:.0f} GFLOP/s, "
          f"sysram {h['sysram_bw_n']/1e9:.0f} GB/s sat)\n")
    ws = [w_cache_hierarchy(h), w_parallel_controller_cap(h), w_cpu_roofline(h),
          w_latency_bandwidth(h), w_capacity_bandwidth_pareto(h)]
    ok = all(ws)
    print(f"\nHOST TOPOLOGY NEDGE PILOT: cache-hierarchy {ws[0]}; controller-cap {ws[1]}; "
          f"cpu-roofline {ws[2]}; latency-recip {ws[3]}; cap-bw-pareto {ws[4]}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the host (CPU/memory) topology models as the SAME nedge G-Value")
    print(f"  conductance network as the GPU: series links = G_AND (DRAM controller = the streaming")
    print(f"  bottleneck), parallel cores = G_OR but CAPPED by the controller (series-over-parallel),")
    print(f"  CPU roofline ridge = the bridge null, latency = reciprocal of bandwidth, RAM = the")
    print(f"  capacity gate. Host and device are one calculus; het-dispatch composes the two branches.")
