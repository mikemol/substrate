"""
het-dispatch-nedge-pilot.py — T-series pilot: heterogeneous CPU+GPU dispatch as a nedge
parallel-conductance balance (candidate claim HET).

A heterogeneous kernel with compute capacity on BOTH the host (CPU) and the GPU, dispatching a
divisible workload between them. The two compute resources work in PARALLEL, so their
conductances ADD (G_OR). Each is gated in SERIES by its feed (G_AND): the CPU by system RAM, the
GPU by whatever feeds it -- PCIe if the data lives on host, DRAM if device-resident. Hence

  throughput(split) bounded by  G_OR( G_AND(cpu_flops, sysram*I), G_AND(gpu_flops, feed*I) )

WHAT MAXIMIZES THROUGHPUT: split the work in proportion to each branch's EFFECTIVE (feed-gated)
conductance, so both finish at the same instant. That load balance IS the Wheatstone bridge
NULL (zero idle-time difference between the two rails); at it, total = the parallel SUM
r_cpu + r_gpu (G_OR). Any other split idles one side and falls below the sum.

The OPTIMAL SPLIT moves with the kernel-type knob (data residence): a host-streaming low-I
kernel has its GPU branch throttled by PCIe, so the CPU -- fed by fast system RAM and not gated
by PCIe -- can out-throughput the GPU and should get most of the work. A device-resident or
compute-bound kernel feeds the GPU at DRAM/full speed, so the GPU dominates the split.

Witnesses (each [W]):
1. PARALLEL = SUM (G_OR): the balanced split's throughput == r_cpu + r_gpu; a sweep over the
   split fraction has its MAX exactly at the balance point, and the max equals the sum.
2. OPTIMUM = BRIDGE BALANCE: optimal f_gpu = r_gpu/(r_cpu+r_gpu) is where the two branches'
   completion times are equal (the idle-time difference nulls).
3. KERNEL-TYPE SHIFTS THE OPTIMUM: host-streaming low-I => CPU-favored (f_gpu < 0.5); device-
   resident => GPU-favored (f_gpu high). The PCIe gate flips who the better worker is.
4. COUNTERINTUITIVE: for a host-streaming low-I kernel the CPU's effective rate EXCEEDS the
   GPU's, because PCIe starves the GPU -- quantified. (The bottleneck-spectrum pilot's PCIe=90%
   finding, now as a dispatch decision.)
Run output: tools/het-dispatch-nedge-pilot-out.txt.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")

G_OR  = lambda a, b: a + b
G_AND = lambda a, b: 0.0 if a + b == 0 else a * b / (a + b)


def query():
    import cupy as cp
    a = cp.cuda.Device(0).attributes
    props = cp.cuda.runtime.getDeviceProperties(0)
    nm = props['name']; nm = nm.decode() if isinstance(nm, (bytes, bytearray)) else nm
    gpu_flops = a['MultiProcessorCount'] * 128 * 2 * (a['ClockRate'] * 1e3)
    dram_bw = 2 * (a['GlobalMemoryBusWidth'] / 8) * (a['MemoryClockRate'] * 1e3)
    return dict(name=nm, gpu_flops=gpu_flops, dram_bw=dram_bw)


# host-side estimates (flagged [est]; structure is exact, numbers locate this box):
CPU_FLOPS = 500e9    # [est] ~10 cores * 8-wide AVX2 * 2 FMA * ~3.9 GHz FP32
SYSRAM_BW = 64e9     # [est] DDR5 dual-channel ~64 GB/s
PCIE_BW   = 16e9     # [est] gen4 x8 laptop


def branch_rate(compute_flops, feed_bw, I):
    """effective FLOP/s of one branch = the per-branch roofline: min(compute, feed*I) = G_AND-ish
    (the binding of compute and feed). Here min is the hard roofline; G_AND is its smooth kin."""
    return min(compute_flops, feed_bw * I)


def optimal_split(r_cpu, r_gpu):
    tot = r_cpu + r_gpu
    return (r_gpu / tot if tot else 0.0), tot           # f_gpu, max throughput (= the parallel sum)


def throughput(f_gpu, r_cpu, r_gpu):
    """divisible unit work; CPU does (1-f_gpu), GPU does f_gpu, in parallel. throughput = 1/time,
    time = max(branch times). Maxed when the branches finish together (load balanced)."""
    t = max((f_gpu / r_gpu if r_gpu else 1e30), ((1 - f_gpu) / r_cpu if r_cpu else 1e30))
    return 1.0 / t if t else 0.0


def w_parallel_sum(t):
    I = 4.0
    r_cpu = branch_rate(CPU_FLOPS, SYSRAM_BW, I)
    r_gpu = branch_rate(t['gpu_flops'], PCIE_BW, I)         # host-streaming feed
    fstar, summ = optimal_split(r_cpu, r_gpu)
    # sweep the split; the max throughput is at fstar and equals the sum
    grid = [i / 1000 for i in range(1001)]
    best_f = max(grid, key=lambda f: throughput(f, r_cpu, r_gpu))
    best_v = throughput(best_f, r_cpu, r_gpu)
    ok = abs(best_f - fstar) < 0.01 and abs(best_v - summ) < summ * 1e-6
    print(f"1. parallel = sum (G_OR): r_cpu={r_cpu/1e9:.0f} + r_gpu={r_gpu/1e9:.0f} = {summ/1e9:.0f} GFLOP/s; "
          f"swept argmax f_gpu={best_f:.3f} (opt {fstar:.3f}), max={best_v/1e9:.0f} == sum {ok}")
    return ok


def w_optimum_is_balance(t):
    I = 4.0
    r_cpu = branch_rate(CPU_FLOPS, SYSRAM_BW, I); r_gpu = branch_rate(t['gpu_flops'], PCIE_BW, I)
    fstar, _ = optimal_split(r_cpu, r_gpu)
    t_cpu = (1 - fstar) / r_cpu; t_gpu = fstar / r_gpu     # branch completion times at the optimum
    ok = abs(t_cpu - t_gpu) < 1e-15
    print(f"2. optimum = bridge balance: at f_gpu={fstar:.3f} branch times equal "
          f"(cpu {t_cpu*1e12:.3f} == gpu {t_gpu*1e12:.3f} ps/unit) -> idle-difference null {ok}")
    return ok


def w_kernel_type_shifts(t):
    rows = []
    for label, feed, I in [("host-stream lowI", PCIE_BW, 4.0),
                           ("device-resident", t['dram_bw'], 4.0),
                           ("compute-bound",   t['dram_bw'], 200.0)]:
        r_cpu = branch_rate(CPU_FLOPS, SYSRAM_BW, I)
        r_gpu = branch_rate(t['gpu_flops'], feed, I)
        fstar, summ = optimal_split(r_cpu, r_gpu)
        rows.append((label, fstar, r_cpu, r_gpu, summ))
    host = next(r for r in rows if r[0].startswith("host"))
    dev  = next(r for r in rows if r[0].startswith("device"))
    cpu_favored_host = host[1] < 0.5
    gpu_favored_dev  = dev[1] > 0.5
    print(f"3. kernel-type shifts the optimum (f_gpu = GPU's share of the work):")
    for label, fstar, rc, rg, summ in rows:
        print(f"     {label:17s} f_gpu={fstar:.3f}  (r_cpu={rc/1e9:6.0f}, r_gpu={rg/1e9:7.0f} GFLOP/s, "
              f"total {summ/1e9:.0f})")
    print(f"   host-streaming low-I is CPU-favored {cpu_favored_host}; device-resident is GPU-favored {gpu_favored_dev}")
    return cpu_favored_host and gpu_favored_dev


def w_cpu_beats_gpu_when_pcie_bound(t):
    I = 4.0
    r_cpu = branch_rate(CPU_FLOPS, SYSRAM_BW, I)
    r_gpu = branch_rate(t['gpu_flops'], PCIE_BW, I)
    ratio = r_cpu / r_gpu
    ok = r_cpu > r_gpu
    print(f"4. counterintuitive: host-streaming low-I -> r_cpu={r_cpu/1e9:.0f} > r_gpu={r_gpu/1e9:.0f} "
          f"GFLOP/s (CPU is {ratio:.1f}x the GPU; PCIe starves the GPU) {ok}")
    return ok


if __name__ == "__main__":
    try:
        t = query()
    except Exception as e:
        print(f"HET DISPATCH NEDGE PILOT: SKIP (no device / cupy: {e})"); raise SystemExit(0)
    print(f"device: {t['name']}  (GPU {t['gpu_flops']/1e9:.0f} GFLOP/s, DRAM {t['dram_bw']/1e9:.0f} GB/s) "
          f"vs host (CPU ~{CPU_FLOPS/1e9:.0f} GFLOP/s [est], sysram ~{SYSRAM_BW/1e9:.0f} GB/s [est], "
          f"PCIe ~{PCIE_BW/1e9:.0f} GB/s [est])\n")
    ws = [w_parallel_sum(t), w_optimum_is_balance(t), w_kernel_type_shifts(t),
          w_cpu_beats_gpu_when_pcie_bound(t)]
    ok = all(ws)
    print(f"\nHET DISPATCH NEDGE PILOT: parallel=sum {ws[0]}; optimum=balance {ws[1]}; "
          f"kernel-type-shifts {ws[2]}; cpu-beats-gpu-when-pcie-bound {ws[3]}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — heterogeneous CPU+GPU dispatch is a nedge parallel-conductance")
    print(f"  balance: the two compute resources are PARALLEL branches (G_OR, conductances add), each")
    print(f"  SERIES-gated by its feed (G_AND). Throughput is MAXED by splitting work in proportion to")
    print(f"  each branch's effective conductance so both finish together -- the Wheatstone bridge null;")
    print(f"  total = the parallel sum. The optimum MOVES with the kernel-type knob: PCIe-bound work")
    print(f"  favors the CPU (the GPU is starved), device-resident/compute-bound favors the GPU.")
