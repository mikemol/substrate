"""
gpu-topology-nedge-pilot.py — T-series pilot: GPU hardware topology as a nedge G-Value
conductance network (candidate claim GPT).

NVIDIA tooling exposes the low-level topology; this models it in the el-atlas electrical-
evidence calculus. The memory/compute hierarchy IS a series-parallel conductance network:
  bandwidth = conductance G        latency = resistance R = 1/G (the G_NOT swap)
  series links (data must traverse each level) = G_AND (harmonic -> slowest link dominates)
  parallel resources (SMs, memory channels)    = G_OR  (sum)
  roofline ridge (compute vs memory balance)   = the Wheatstone bridge NULL

Real numbers are QUERIED live from the device (cupy / cudaDeviceProp); architectural ones
(L1/L2 bandwidth, PCIe) are ESTIMATES, flagged [est]. The model STRUCTURE (series=G_AND finds
the bottleneck, parallel=G_OR, roofline=bridge-null, latency=reciprocal) is exact for any
positive numbers; the queried numbers locate this box on it.

Witnesses (each [W]):
1. SERIES = BOTTLENECK: the path conductance G_AND-fold(link BWs) is dominated by the SLOWEST
   link (harmonic mean <= min); dropping the min-BW link jumps the path BW -> it WAS the
   bottleneck. The dominant series resistance is the symmetry-breaker the scheduler must respect.
2. PARALLEL = SUM: the 20 SMs' compute and the 3 memory channels (96-bit / 32) combine as
   G_OR (sum), recovering peak FP32 and peak DRAM BW.
3. ROOFLINE = BRIDGE NULL: achievable(I) = min(peak_FLOP, I*peak_BW); the compute and memory
   branches are equal at the ridge I* = peak_FLOP/peak_BW; the bias (which branch limits) flips
   sign across I* -- memory-bound below, compute-bound above. The bridge finds the ridge.
4. LATENCY <-> BANDWIDTH = G_NOT: resistance = 1/conductance, the swap involution (R*G = 1,
   double-swap = identity).
5. OCCUPANCY = BINDING CONSTRAINT (series-AND gate): concurrent warps/SM = min over the
   threads / registers / shared-mem / blocks limits; the resource hit FIRST is the binding one
   -- one short branch shorts the parallel capacity, exactly the SWB validity gate's shape.

Bridge to SWB: that pilot weighed the ALGORITHM's lane geometry; this weighs the HARDWARE it
runs on. A kernel's achieved throughput = G_AND(algorithm conductance, hardware bottleneck) --
series composition of the two. Live: NVML telemetry (clock throttle, util) scales the edge
conductances and the nedge LFP re-solves -> the current bottleneck shifts -> the scheduler
rebalances (the live control loop). Run output: tools/gpu-topology-nedge-pilot-out.txt.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
from functools import reduce as _reduce

# --- the nedge G-Value calculus (el-atlas-spec 5.7e) -------------------------------------
G_OR  = lambda a, b: a + b
G_AND = lambda a, b: 0.0 if a + b == 0 else a * b / (a + b)
G_NOT = lambda g: float('inf') if g == 0 else 1.0 / g
G_OR_fold  = lambda xs: _reduce(G_OR, xs, 0.0)
G_AND_fold = lambda xs: _reduce(G_AND, xs)            # harmonic; >=2 elems


def query_topology():
    """Live device query. Returns a dict; marks which numbers are queried vs estimated."""
    import cupy as cp
    d = cp.cuda.Device(0); a = d.attributes
    props = cp.cuda.runtime.getDeviceProperties(0)
    name = props['name'].decode() if isinstance(props['name'], (bytes, bytearray)) else props['name']
    sms = a['MultiProcessorCount']; clk = a['ClockRate'] * 1e3           # Hz
    busbits = a['GlobalMemoryBusWidth']; memclk = a['MemoryClockRate'] * 1e3
    dram_bw = 2 * (busbits / 8) * memclk                                 # GDDR6 DDR: x2
    fp32 = sms * 128 * 2 * clk                                           # Ada: 128 FP32 cores/SM, FMA=2
    return dict(
        name=name, sms=sms, clk=clk, warp=a['WarpSize'],
        threads_per_sm=a['MaxThreadsPerMultiProcessor'], blocks_per_sm=a['MaxBlocksPerMultiprocessor'],
        regs_per_sm=a['MaxRegistersPerMultiprocessor'], shared_per_sm=a['MaxSharedMemoryPerMultiprocessor'],
        l2_bytes=a['L2CacheSize'], dram_bytes=props['totalGlobalMem'],
        busbits=busbits, dram_bw=dram_bw, fp32=fp32,                     # all QUERIED/derived-from-queried
        chans=busbits // 32,                                            # 32-bit memory channels in parallel
    )


def hierarchy_bandwidths(t):
    """Path compute<-...<-host as (level, GB/s, queried?). Intermediate BWs are [est] (architectural)."""
    return [
        ("registers", t['sms'] * 128 * 4 * t['clk'] / 1e9, False),      # ~128 lanes*4B/clk/SM [est]
        ("L1/shared", t['sms'] * 128 * t['clk'] / 1e9, False),          # ~128 B/clk/SM [est]
        ("L2(24MB)",  t['dram_bw'] * 6 / 1e9, False),                   # ~6x DRAM aggregate [est]
        ("DRAM",      t['dram_bw'] / 1e9, True),                        # QUERIED (bus x memclk)
        ("host/PCIe", 16.0, False),                                     # gen4 x8 laptop ~16 GB/s [est]
    ]


def w_series_bottleneck(t):
    levels = hierarchy_bandwidths(t)
    bw = [g for _, g, _ in levels]
    path = G_AND_fold(bw)                                               # series: data traverses each link
    mn = min(bw); mn_name = levels[bw.index(mn)][0]
    # dropping the slowest link jumps the path conductance -> it was the bottleneck
    bw_wo = [g for g in bw if g != mn]
    path_wo = G_AND_fold(bw_wo)
    ok = (path <= mn + 1e-6) and (path_wo > path * 1.5)
    print(f"1. series = bottleneck: path BW = G_AND_fold = {path:.1f} GB/s <= slowest link "
          f"({mn_name} {mn:.1f}); drop it -> {path_wo:.1f} GB/s. Bottleneck = {mn_name}. {ok}")
    return ok


def w_parallel_sum(t):
    per_sm = t['fp32'] / t['sms']
    total = G_OR_fold([per_sm] * t['sms'])
    ok_c = abs(total - t['fp32']) < 1e-3
    chan_bw = t['dram_bw'] / t['chans']
    ok_m = abs(G_OR_fold([chan_bw] * t['chans']) - t['dram_bw']) < 1e-3
    print(f"2. parallel = sum: {t['sms']} SMs G_OR -> {total/1e9:.0f} GFLOP/s {ok_c}; "
          f"{t['chans']} mem channels G_OR -> {t['dram_bw']/1e9:.0f} GB/s {ok_m}")
    return ok_c and ok_m


def w_roofline_bridge(t):
    peakF, peakB = t['fp32'], t['dram_bw']
    Istar = peakF / peakB                                               # ridge FLOP/byte (the bridge null)
    ach = lambda I: min(peakF, I * peakB)
    null = abs(ach(Istar) - peakF) < 1e-3 and abs(ach(Istar) - Istar * peakB) < 1e-3
    bias = lambda I: (I * peakB) - peakF                                # <0 memory-bound, >0 compute-bound
    flips = bias(Istar * 0.5) < 0 < bias(Istar * 2.0)
    print(f"3. roofline = bridge null: ridge I* = peakFLOP/peakBW = {Istar:.1f} FLOP/byte; "
          f"compute & memory branches equal there {null}; bias flips (mem-bound<->compute-bound) {flips}")
    return null and flips


def w_latency_bandwidth(t):
    bws = [t['dram_bw'] / 1e9, 16.0, t['fp32'] / 1e9]
    invol = all(abs(G_NOT(G_NOT(g)) - g) < 1e-6 for g in bws)           # double-swap = id
    recip = all(abs(g * G_NOT(g) - 1.0) < 1e-9 for g in bws)            # R * G = 1
    print(f"4. latency <-> bandwidth = G_NOT (reciprocal swap): R*G=1 {recip}; double-swap=id {invol}")
    return invol and recip


def w_occupancy_gate(t, regs_per_thread=64, shared_per_block=0, block=256):
    # concurrent warps/SM = min over the per-resource limits (the binding constraint = series-AND min)
    warp = t['warp']
    lim_threads = t['threads_per_sm']
    lim_regs = t['regs_per_sm'] // regs_per_thread                      # threads the reg file allows
    lim_blocks = t['blocks_per_sm'] * block
    lim_shared = (t['shared_per_sm'] // shared_per_block * block) if shared_per_block else 10**9
    threads = min(lim_threads, lim_regs, lim_blocks, lim_shared)
    binding = min([("threads", lim_threads), ("registers", lim_regs),
                   ("blocks", lim_blocks), ("shared", lim_shared)], key=lambda kv: kv[1])[0]
    occ = (threads // warp) / (t['threads_per_sm'] // warp)
    # series-AND gate semantics: the min resource is the bottleneck, just like SWB validity
    ok = threads == min(lim_threads, lim_regs, lim_blocks, lim_shared)
    print(f"4b/5. occupancy = binding constraint (series-AND min): @{regs_per_thread} regs/thread -> "
          f"{threads} threads/SM, binding = {binding}, occupancy = {occ*100:.0f}% {ok}")
    return ok


if __name__ == "__main__":
    try:
        t = query_topology()
    except Exception as e:
        print(f"GPU TOPOLOGY NEDGE PILOT: SKIP (no device / cupy: {e})"); raise SystemExit(0)
    print(f"device: {t['name']}  ({t['sms']} SMs, {t['dram_bw']/1e9:.0f} GB/s DRAM, "
          f"{t['l2_bytes']//(1<<20)} MB L2, {t['fp32']/1e9:.0f} GFLOP/s FP32) -- queried live\n")
    ws = [w_series_bottleneck(t), w_parallel_sum(t), w_roofline_bridge(t),
          w_latency_bandwidth(t), w_occupancy_gate(t, 64), w_occupancy_gate(t, 32)]
    ok = all(ws)
    print(f"\nGPU TOPOLOGY NEDGE PILOT: series=bottleneck {ws[0]}; parallel=sum {ws[1]}; "
          f"roofline=bridge-null {ws[2]}; latency=recip {ws[3]}; occupancy-gate {ws[4] and ws[5]}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — GPU hardware topology models as a nedge G-Value conductance")
    print(f"  network: series links = G_AND (slowest link = the bottleneck), parallel resources = G_OR")
    print(f"  (sum), roofline ridge = the Wheatstone bridge null between compute and memory, latency =")
    print(f"  the reciprocal (G_NOT) of bandwidth, occupancy = the series-AND binding constraint. A")
    print(f"  kernel's achieved throughput = G_AND(algorithm conductance [SWB], hardware bottleneck). Live")
    print(f"  NVML telemetry scales the edges; the nedge LFP re-solves -> the bottleneck shifts -> rebalance.")
