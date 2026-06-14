"""host_probe.py — fetch the HOST topology at RUNTIME (measured, not hardcoded), the CPU-side
analogue of cudaDeviceProp. Shared by host-topology-nedge-pilot.py and het-dispatch-nedge-pilot.py.

Static facts come from sysfs/proc (cores, caches, RAM); conductances are MEASURED live (sysram
bandwidth single- and multi-threaded, CPU FP32 via BLAS sgemm, PCIe H2D/D2H via cupy). Cached so
repeated calls in one process don't re-measure. Numbers are this box's actual achievable rates,
not spec peaks -- the honest input to the nedge conductance model.
"""
import os, glob, time, functools
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np
from concurrent.futures import ThreadPoolExecutor


def _read(path, default=None):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return default


def _parse_size(s):                       # "48K" / "1280K" / "24576K" -> bytes
    if not s:
        return None
    u = s[-1]
    return int(s[:-1]) * (1024 if u == 'K' else 1024 * 1024 if u == 'M' else 1) if u in "KM" else int(s)


def _cache_bytes(level, typ):
    for d in sorted(glob.glob("/sys/devices/system/cpu/cpu0/cache/index*")):
        if _read(d + "/level") == str(level):
            t = _read(d + "/type") or ""
            if typ is None or t.startswith(typ):
                return _parse_size(_read(d + "/size"))
    return None


def _measure_sysram_bw(threads, mb=256, reps=5):
    """Streaming READ bandwidth (sum), array >> L3 so it hits DRAM. threads disjoint slices
    (np.sum releases the GIL -> real parallel memory traffic)."""
    n = mb * 1024 * 1024 // 4
    a = np.ones(n, np.float32)
    chunk = n // threads
    slices = [a[i * chunk:(i + 1) * chunk if i < threads - 1 else n] for i in range(threads)]
    best = 1e9
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for _ in range(reps):
            t = time.perf_counter()
            list(ex.map(lambda s: float(s.sum()), slices))
            best = min(best, time.perf_counter() - t)
    return a.nbytes / best                # bytes/s


def _measure_cpu_gflops(m=4096, reps=3):
    x = np.random.rand(m, m).astype(np.float32); y = np.random.rand(m, m).astype(np.float32)
    np.dot(x, y); best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); np.dot(x, y); best = min(best, time.perf_counter() - t)
    return 2 * m ** 3 / best               # FLOP/s


def _measure_pcie(mb=256, reps=5):
    try:
        import cupy as cp
    except Exception:
        return None
    n = mb * 1024 * 1024 // 4
    host = np.ones(n, np.float32); dev = cp.empty(n, cp.float32); out = np.empty(n, np.float32)
    sync = cp.cuda.Stream.null.synchronize
    def bench(fn):
        sync(); best = 1e9
        for _ in range(reps):
            t = time.perf_counter(); fn(); sync(); best = min(best, time.perf_counter() - t)
        return n * 4 / best
    return dict(h2d=bench(lambda: dev.set(host)), d2h=bench(lambda: dev.get(out=out)))


@functools.lru_cache(None)
def probe_host():
    cores = os.cpu_count()
    memtotal = _read("/proc/meminfo") or "MemTotal: 0 kB"
    ram = int(memtotal.split()[1]) * 1024
    model = "unknown"
    for line in (_read("/proc/cpuinfo") or "").splitlines():
        if line.startswith("model name"):
            model = line.split(":", 1)[1].strip(); break
    flags = set((_read("/proc/cpuinfo") or "").split())
    vec = "avx512" if "avx512f" in flags else ("avx2" if "avx2" in flags else "sse")
    pcie = _measure_pcie()
    return dict(
        model=model, cores=cores, vec=vec, ram=ram,
        l1d=_cache_bytes(1, "Data"), l2=_cache_bytes(2, None), l3=_cache_bytes(3, None),
        sysram_bw_1=_measure_sysram_bw(1),            # single-core (cannot saturate the controller)
        sysram_bw_n=_measure_sysram_bw(cores),        # saturated (the memory-controller ceiling)
        cpu_flops=_measure_cpu_gflops(),              # sustained BLAS sgemm
        pcie_h2d=(pcie or {}).get('h2d'), pcie_d2h=(pcie or {}).get('d2h'),
    )


if __name__ == "__main__":
    h = probe_host()
    print(f"HOST (fetched at runtime): {h['model']}")
    print(f"  cores={h['cores']} vec={h['vec']} RAM={h['ram']/(1<<30):.1f} GiB")
    print(f"  caches: L1d={h['l1d']//1024}K L2={h['l2']//1024}K L3={h['l3']//(1<<20)}M")
    print(f"  sysram BW: 1-core={h['sysram_bw_1']/1e9:.1f} GB/s, {h['cores']}-core saturated="
          f"{h['sysram_bw_n']/1e9:.1f} GB/s (controller ceiling)")
    print(f"  CPU FP32 (sgemm): {h['cpu_flops']/1e9:.0f} GFLOP/s")
    print(f"  PCIe: H2D={None if h['pcie_h2d'] is None else round(h['pcie_h2d']/1e9,1)} GB/s, "
          f"D2H={None if h['pcie_d2h'] is None else round(h['pcie_d2h']/1e9,1)} GB/s")
