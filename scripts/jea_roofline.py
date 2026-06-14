#!/usr/bin/env python3
"""jea_roofline.py — counter-free bottleneck diagnosis for the jea_gpu ℚ kernels,
by ABLATION. The durable lesson: you cannot predict a GPU kernel's bottleneck from a
STATIC property. Measure it — strip each component, see what moves the time.

THE STORY (why this script exists). The tiled-ℚ fold was predicted to be the biggest
win and came out ~0.82x SLOWER. EPISTEMIC GUARD: do NOT read each mispredict as a
categorical refutation ("NOT compute-bound", "static lied") — that is excluded-middle
reasoning the substrate rejects (feedback_reject_lem_in_substrate). The axes COEXIST;
static analysis NAMES them, ablation RANKS them at an operating point; "not binding
here" is not "false". Every line below is bounded to (workload, config), not a law.
Three static predictions, each naming a real axis it then mis-ranked:

  * "32-byte values ⇒ bandwidth axis dominates ⇒ tiling wins"     → tiling was SLOWER
    here; bandwidth was not the binding axis at this operating point.
  * "SASS shows a 256-iter nested 128-bit-divide ⇒ compute axis"  → the divide IS real
    and expensive in isolation, but here adding 5 software 128-bit multiplies + 2
    divides costs ~0 ms (they hide under memory latency) — compute did not bind here.
  * "gcd runs 256 but the data needs ~2 steps ⇒ 134x headroom"    → windowing 256→4
    gives ~1.2x; the gcd is ~20% of runtime at this config.

  ABLATION RANKING AT THIS OPERATING POINT: the floor is set by memory latency / launch.
  ~402 MB of node traffic in ~16.6 ms ≈ 24 GB/s, against the RTX 4050's ~200 GB/s peak
  (~12% — few in-flight requests to saturate the bus). The 128-bit multiplies/divides
  hide under that latency; the 256-iter gcd is where arithmetic stops hiding (~5 ms over
  the floor), recoverable by a bounded window (below). WHICH axis binds is itself a
  coordinate that shifts with the workload — the reason the real answer is DYNAMIC
  rebalancing, not a new fixed verdict.

  WHY TILING IS SLOWER (correctly, this time): a latency-bound kernel lives on
  memory-level parallelism = concurrent in-flight requests = OCCUPANCY. The tiled
  fold's in-block reduction tree drops to 22% dynamic thread-utilization (256+128+
  ...+1 active across 9 levels). It cuts total BYTES (the non-bottleneck) at the cost
  of OCCUPANCY (the bottleneck). Backwards.

  THE REAL LEVER (what actually attacks the measured bottleneck): fuse the 22
  dependent per-level launches into ONE persistent kernel with a work queue —
  "partial-EEA-ladder + pack work into the freed slots" (user). Each lane runs a
  bounded window of Euclidean steps; a converged node spills and the lane REFILLS from
  the queue. No warp divergence (uniform steps), no idle lanes (refill), occupancy
  pinned high (the latency-bound win), and the 22-launch latency chain collapses to
  one launch. This is the substrate spine: finite-window walk + never-discard-residue
  (the (a,b) state IS the EEATrace residue, a freed lane is a freed slot refilled from
  it) + escalate-don't-truncate (a node not converged in the window is left UNREDUCED
  — still exact — and flagged for a wide-gcd compaction pass). A bounded window of K=4
  is bit-exact for the small-denominator workload and ~1.2x faster; the structural win
  is the fusion, not the window.

WHAT THE NVIDIA TOOLCHAIN PROVIDES, and what works UNPRIVILEGED on this box:
  * cuobjdump / nvdisasm  — SASS disassembly (loop structure, instr count). ✓
  * nvcc --resource-usage — registers/thread, shared/block → analytic occupancy. ✓
  * cupyx.profiler.benchmark — warmup + CPU(launch)/GPU(kernel)-split timing. ✓
  * ABLATION (this script) — ranks the named axes at an operating point. ✓
  * nsys — CUPTI timeline (durations/gaps/launch); traces, not SM counters. ✓
  * ncu — per-kernel SM HW counters (roofline chart, stall reasons, bank conflicts).
    GATED: /proc/driver/nvidia/params shows RmProfilingAdminOnly:1 and sudo needs a
    password ⇒ ERR_NVGPUCTRPERM. To enable: set the kernel module param
    NVreg_RestrictProfilingToAdminUsers=0 (root, persists after reboot), or run ncu as
    root. When counters ARE available, cupy's NVRTC header lookup crashes under ncu's
    process wrapper (the pathfinder canary subprocess exits 255); fix with CUDA_PATH=/usr
    so the CUDA_PATH find-step hits /usr/include/cuda_runtime.h before the canary:
        CUDA_PATH=/usr ncu --section SpeedOfLight --section Occupancy \
          --section WarpStateStats --kernel-name 'regex:combine_level_q|fold_subtree_q' \
          --launch-count 2 python3 scripts/jea_roofline.py --bench

USAGE:
  python3 scripts/jea_roofline.py            # ablation report (the bottleneck finder)
  python3 scripts/jea_roofline.py --bench    # cupyx GPU-only A/B (per-level vs tiled)
  python3 scripts/jea_roofline.py --sass     # SASS loop structure of combine_level_q
"""
import os, re, subprocess, sys, tempfile
import numpy as np

os.environ.setdefault("CUDA_PATH", "/usr")          # cupy NVRTC + ncu header resolution
ARCH = "sm_89"
ADA = dict(REGS_SM=65536, THREADS_SM=1536, SMEM_SM=101376, WARP=32, PEAK_GBs=200)

_QHEAD = r'''typedef unsigned long long u64; typedef unsigned __int128 u128; typedef __int128 i128;
__device__ __forceinline__ u128 absu(i128 x){ return x<0?(u128)(-x):(u128)x; }
__device__ __forceinline__ i128 ldn(const u64*lo,const u64*hi,int i){return (i128)(((u128)hi[i]<<64)|lo[i]);}'''


# ---- ablation harness: one parametric ℚ combine, components toggled ----------
def _combine(K, ovcheck):
    """Per-level ℚ combine RawKernel with K-step gcd window and optional ovf-check divides."""
    import cupy as cp
    ov = (r'o|=(an!=0)&&(nm/an!=bn); o|=(ad!=0)&&(D/ad!=bd); o|=(bd!=0)&&(p1/bd!=an);'
          r'o|=(ad!=0)&&(p2/ad!=bn); o|=((p1>0)==(p2>0))&&((na>0)!=(p1>0))&&(p1!=0);') if ovcheck else ''
    src = _QHEAD + r'''
extern "C" __global__ void cb(const u64* anl,const u64* anh,const u64* adl,const u64* adh,
  const signed char* tags,u64* nnl,u64* nnh,u64* ndl,u64* ndh,int* ovf,int* deep,int n){
  int i=blockDim.x*(long long)blockIdx.x+threadIdx.x; if(i>=n)return;
  i128 an=ldn(anl,anh,2*i),ad=ldn(adl,adh,2*i),bn=ldn(anl,anh,2*i+1),bd=ldn(adl,adh,2*i+1);
  int isMul=(tags[i]==2); i128 p1=an*bd,p2=bn*ad,nm=an*bn,na=p1+p2,D=ad*bd; int o=0;
  OVCHECK
  i128 N=isMul?nm:na; u128 a=absu(N),b=absu(D);
  #pragma unroll
  for(int k=0;k<KK;k++){u128 r=(b!=0)?(a%b):(u128)0; a=(b!=0)?b:a; b=(b!=0)?r:b;}
  int conv=(b==0); u128 g=conv?(a==0?(u128)1:a):(u128)1; N=N/(i128)g; D=D/(i128)g;
  nnl[i]=(u64)(u128)N;nnh[i]=(u64)((u128)N>>64);ndl[i]=(u64)(u128)D;ndh[i]=(u64)((u128)D>>64);
  if(o)ovf[0]=1; if(!conv)deep[0]=1;
}'''.replace('OVCHECK', ov).replace('KK', str(K))
    return cp.RawKernel(src, 'cb', options=('--device-int128',))


def _fold(nums, dens, tags, k):
    import cupy as cp
    anl = cp.asarray(nums, cp.uint64); anh = cp.zeros(nums.size, cp.uint64)
    adl = cp.asarray(dens, cp.uint64); adh = cp.zeros(dens.size, cp.uint64)
    dt = [cp.asarray(t) for t in tags]; ovf = cp.zeros(1, cp.int32); deep = cp.zeros(1, cp.int32)
    for tg in dt:
        m = int(tg.size)
        a = cp.empty(m, cp.uint64); b = cp.empty(m, cp.uint64); c = cp.empty(m, cp.uint64); d = cp.empty(m, cp.uint64)
        k(((m+255)//256,), (256,), (anl, anh, adl, adh, tg, a, b, c, d, ovf, deep, np.int32(m)))
        anl, anh, adl, adh = a, b, c, d
    cp.cuda.Stream.null.synchronize()
    return (int(anl.get()[0]), int(adl.get()[0]), int(ovf.get()[0]), int(deep.get()[0]))


def cmd_ablate(h=22, seed=2):
    import cupy as cp, jea_gpu as J
    from cupyx.profiler import benchmark
    nums, dens, tags = J._build_q_add(h, seed)
    def t(k):
        _fold(nums, dens, tags, k)
        return benchmark(lambda: _fold(nums, dens, tags, k), n_repeat=15, n_warmup=3).gpu_times.mean()*1e3
    nodes = nums.size - 1
    bytes_moved = nodes * 96            # per node ~64B read + 32B write (4 u64 lanes)
    print(f"ABLATION, 2^{h} ℚ tree ({nodes:,} fold nodes), GPU-only (15 reps):")
    rows = [("256 gcd + ovf-div (CURRENT)", _combine(256, True)),
            ("  4 gcd + ovf-div", _combine(4, True)),
            ("  4 gcd, no ovf-div", _combine(4, False)),
            ("  0 gcd, no ovf-div (mul+final-div floor)", _combine(0, False))]
    base = None
    for nm, k in rows:
        ms = t(k); base = base or ms
        print(f"  {nm:44s} {ms:6.2f} ms")
    floor = t(_combine(0, False))
    print(f"\n  effective bandwidth at floor: {bytes_moved/1e6:.0f} MB / {floor:.1f} ms "
          f"= {bytes_moved/1e6/floor:.0f} GB/s  (peak ~{ADA['PEAK_GBs']} GB/s "
          f"⇒ {bytes_moved/1e6/floor/ADA['PEAK_GBs']*100:.0f}% of peak ⇒ latency axis ranks "
          f"above bandwidth/compute AT THIS operating point)")
    print("  reading (bounded to this workload/config): arithmetic adds little over the memory")
    print("  floor ⇒ memory-latency/launch is the binding axis here; the lever is more in-flight")
    print("  requests (occupancy, fused launches), not less traffic. A different workload may rank differently.")


def cmd_bench(h=22, s=9, seed=2):
    import jea_gpu as J
    from cupyx.profiler import benchmark
    nums, dens, tags = J._build_q_add(h, seed)
    gpl = benchmark(lambda: J.inside_perlevel_q(nums, dens, tags), n_repeat=20, n_warmup=3).gpu_times.mean()*1e3
    gti = benchmark(lambda: J.inside_tiled_q(nums, dens, tags, s), n_repeat=20, n_warmup=3).gpu_times.mean()*1e3
    print(f"cupyx.benchmark 2^{h} ℚ leaves (GPU-only, 20 reps):")
    print(f"  per-level {gpl:6.2f} ms | tiled {gti:6.2f} ms | ratio {gpl/gti:.2f}x "
          f"({'tiling slower' if gpl < gti else 'tiling faster'})")


def cmd_sass():
    with tempfile.TemporaryDirectory() as d:
        cu = os.path.join(d, "k.cu"); cb = os.path.join(d, "k.cubin")
        open(cu, "w").write(_QHEAD + r'''
__device__ __forceinline__ u128 gcd_u(u128 a,u128 b){for(int k=0;k<256;k++){u128 r=(b!=0)?(a%b):(u128)0;
 a=(b!=0)?b:a; b=(b!=0)?r:b;} return a;}
extern "C" __global__ void combine_level_q(const u64*anl,const u64*anh,const u64*adl,const u64*adh,
 const signed char*tags,u64*nnl,u64*nnh,u64*ndl,u64*ndh,int*ovf,int n){
 int i=blockDim.x*(long long)blockIdx.x+threadIdx.x; if(i>=n)return;
 i128 an=ldn(anl,anh,2*i),ad=ldn(adl,adh,2*i),bn=ldn(anl,anh,2*i+1),bd=ldn(adl,adh,2*i+1);
 int isMul=(tags[i]==2); i128 p1=an*bd,p2=bn*ad,nm=an*bn,na=p1+p2,D=ad*bd; int o=0;
 o|=(an!=0)&&(nm/an!=bn); i128 N=isMul?nm:na; u128 g=gcd_u(absu(N),absu(D)); g=(g==0)?(u128)1:g;
 N=N/(i128)g; D=D/(i128)g; nnl[i]=(u64)(u128)N; ndl[i]=(u64)(u128)D; if(o)ovf[0]=1;}''')
        info = subprocess.run(["nvcc", f"-arch={ARCH}", "-cubin", "-o", cb, cu, "--resource-usage"],
                              capture_output=True, text=True)
        regs = re.search(r"Used (\d+) registers", info.stderr)
        sass = subprocess.run(["cuobjdump", "-sass", cb], capture_output=True, text=True).stdout
        lines = sass.splitlines()
        instr = sum(1 for ln in lines if re.search(r"/\*[0-9a-f]+\*/", ln))
        has256 = any("0x100" in ln and "ISETP" in ln for ln in lines)
        print(f"combine_level_q @ {ARCH}: {instr} static SASS instr, "
              f"{regs.group(1) if regs else '?'} registers; 256-gcd counter present: {has256}")
        print("  (static SASS NAMES the compute axis; at this operating point the gcd hides under")
        print("   memory latency. Static names axes; ablation ranks them — neither refutes the other.)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--bench"]:
        cmd_bench()
    elif a == ["--sass"]:
        cmd_sass()
    else:
        cmd_ablate()
