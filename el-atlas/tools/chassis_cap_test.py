"""
AI-12: chassis-cap binding test (RUN AS ROOT, venv python). Resolves AI-4's over-claimed "chassis
BINDS", which compared combined draw to the NAMEPLATE cap sum (75W) -- but neither side hit its own
cap, so that couldn't distinguish chassis-throttle from workload-not-maxing.

The PROPER test: measure each side ALONE, then COMBINED.
  P_cpu_alone   (CPU load only)  -- RAPL package W
  P_gpu_alone   (GPU load only)  -- dGPU W (nvidia-smi)
  P_combined    (both)           -- RAPL package W + dGPU W
If under combined the CPU and/or GPU power drops below its alone value, the shared chassis/thermal
budget throttled them -> the cap BINDS (the het-sum is sub-additive in power). If each ~= its alone
value, the chassis is NOT binding at this load (the AI-4 'binds' was over-claimed).

Usage:  powerprofilesctl set performance
        sudo $HOME/github/substrate/.venv/bin/python chassis_cap_test.py
        powerprofilesctl set power-saver
"""
import os, time, threading
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np
from power_probe_root import rapl_domains, gpu_draw

_GPU_OK = {"loaded": False}


def cpu_worker(stop):
    a = (np.random.rand(512, 512).astype(np.float32) * 0.01 + 0.5); b = a.copy()
    while not stop.is_set():
        a = (a @ b) * 0.5 + 0.25


def gpu_worker(stop):
    try:
        import cupy as cp
        x = cp.random.rand(2048, 2048, dtype=cp.float32); y = x.copy()
        _GPU_OK["loaded"] = True
        while not stop.is_set():
            z = x @ y; cp.cuda.Stream.null.synchronize()
    except Exception:
        pass


def measure(secs, cpu_on, gpu_on):
    stop = threading.Event(); ts = []
    if cpu_on:
        ts += [threading.Thread(target=cpu_worker, args=(stop,)) for _ in range(os.cpu_count())]
    if gpu_on:
        ts.append(threading.Thread(target=gpu_worker, args=(stop,)))
    for t in ts: t.start()
    e0 = rapl_domains(); t0 = time.perf_counter(); g = []
    end = t0 + secs
    while time.perf_counter() < end:
        d = gpu_draw()
        if d is not None: g.append(d)
        time.sleep(0.3)
    dt = time.perf_counter() - t0; e1 = rapl_domains()
    stop.set()
    for t in ts: t.join(timeout=1)
    pkg = None
    if "package-0" in e0:
        _, a, mx = e0["package-0"]; _, b, _ = e1["package-0"]
        pkg = ((b - a) if b >= a else (b - a + mx)) / 1e6 / dt
    dgpu = sum(g) / len(g) if g else None
    return pkg, dgpu


if __name__ == "__main__":
    if not rapl_domains():
        print("RAPL not readable -- run as ROOT"); raise SystemExit(1)
    gov = open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read().strip()
    print(f"chassis-cap binding test (governor={gov})\n")

    pkg_cpu, _ = measure(3.0, cpu_on=True, gpu_on=False)
    _, dgpu_gpu = measure(3.0, cpu_on=False, gpu_on=True)
    pkg_both, dgpu_both = measure(3.0, cpu_on=True, gpu_on=True)
    if not _GPU_OK["loaded"]:
        print("GPU not loaded -- use the venv python (sudo .venv/bin/python). Aborting."); raise SystemExit(1)

    print(f"  CPU package: alone {pkg_cpu:.1f} W  -> combined {pkg_both:.1f} W")
    print(f"  dGPU:        alone {dgpu_gpu:.1f} W -> combined {dgpu_both:.1f} W")
    cpu_drop = pkg_both / pkg_cpu if pkg_cpu else 1.0
    gpu_drop = dgpu_both / dgpu_gpu if dgpu_gpu else 1.0
    alone_sum = pkg_cpu + dgpu_gpu; combined = pkg_both + dgpu_both
    binds = cpu_drop < 0.9 or gpu_drop < 0.9
    print(f"\n  alone-sum {alone_sum:.1f} W vs combined {combined:.1f} W "
          f"({combined/alone_sum*100:.0f}%); CPU x{cpu_drop:.2f}, dGPU x{gpu_drop:.2f}")
    print(f"  -> chassis cap {'BINDS (a side throttled under combined -- het-sum sub-additive in power)' if binds else 'does NOT bind at this load (combined ~= alone-sum; AI-4 binds was over-claimed)'}")
    print(f"  (governor={gov}: use performance to stress the envelope)")
