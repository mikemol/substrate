"""
power_probe_root.py — AI-4 empirical close (RUN AS ROOT). Battery EC reports no power even to root,
but RAPL energy_uj is root-readable. Measures CPU-package (incl iGPU) + platform(psys) power via
RAPL energy deltas under self-generated combined CPU+GPU load, plus the dGPU draw via nvidia-smi
(no root needed). Reports whether the chassis envelope binds below PL0(45W) + dGPU(enforced ~30W).

Usage:  sudo python3 power_probe_root.py        (optionally flip to performance first for a real cap)
"""
import os, glob, time, subprocess, threading
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np


def rapl_domains():
    out = {}
    for d in sorted(glob.glob("/sys/class/powercap/intel-rapl:*")):
        try:
            name = open(d + "/name").read().strip()
            e = int(open(d + "/energy_uj").read())
            mx = int(open(d + "/max_energy_range_uj").read())
            out[name] = (d, e, mx)
        except Exception:
            pass
    return out


def gpu_draw():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=3)
        return float(r.stdout.strip().splitlines()[0])
    except Exception:
        return None


_GPU_OK = {"loaded": False, "err": ""}

def combined_load(stop, secs):
    def cpu():
        a = (np.random.rand(512, 512).astype(np.float32) * 0.01 + 0.5); b = a.copy()
        while not stop.is_set():
            a = (a @ b) * 0.5 + 0.25                     # bounded (no overflow spam)
    def gpu():
        try:
            import cupy as cp
            x = cp.random.rand(2048, 2048, dtype=cp.float32); y = x.copy()
            _GPU_OK["loaded"] = True
            while not stop.is_set():
                z = x @ y; cp.cuda.Stream.null.synchronize()
        except Exception as e:
            _GPU_OK["err"] = repr(e)
    ts = [threading.Thread(target=cpu) for _ in range(os.cpu_count())] + [threading.Thread(target=gpu)]
    for t in ts: t.start()
    return ts


if __name__ == "__main__":
    d0 = rapl_domains()
    if not d0:
        print("RAPL energy_uj not readable -- run as ROOT (sudo python3 power_probe_root.py)"); raise SystemExit(1)
    gov = open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read().strip()
    print(f"RAPL domains: {list(d0)}; governor: {gov}\n")

    SECS = 4.0
    stop = threading.Event()
    gpu_samples = []
    ts = combined_load(stop, SECS)
    t0 = time.perf_counter(); e0 = rapl_domains()
    end = t0 + SECS
    while time.perf_counter() < end:
        g = gpu_draw()
        if g is not None: gpu_samples.append(g)
        time.sleep(0.4)
    dt = time.perf_counter() - t0; e1 = rapl_domains()
    stop.set()
    for t in ts: t.join(timeout=1)

    def watts(name):
        _, a, mx = e0[name]; _, b, _ = e1[name]
        delta = (b - a) if b >= a else (b - a + mx)        # handle wrap
        return delta / 1e6 / dt
    pkg = watts("package-0") if "package-0" in e0 else None
    psys = watts("psys") if "psys" in e0 else None
    dgpu = sum(gpu_samples) / len(gpu_samples) if gpu_samples else None

    # validity gates (do NOT conclude on confounded inputs)
    gpu_ok = _GPU_OK["loaded"]
    psys_ok = (psys is not None and pkg is not None and psys >= pkg * 0.9)   # psys must be >= package
    print(f"under combined load ({dt:.1f}s):")
    print(f"  CPU package (incl iGPU) = {pkg:.1f} W  [VALID]" if pkg else "  CPU package: n/a")
    print(f"  platform (psys)         = {psys:.1f} W  [{'valid' if psys_ok else 'BROKEN counter -- reads < package; ignore'}]"
          if psys is not None else "  platform (psys): not exposed")
    print(f"  dGPU (nvidia-smi)       = {dgpu:.1f} W  [{'loaded' if gpu_ok else 'NOT LOADED -- cupy unavailable in this python; idle draw'}]"
          if dgpu else "  dGPU: n/a")
    if not gpu_ok:
        print(f"\n  GPU not loaded ({_GPU_OK['err'] or 'no cupy'}) -> run with the venv python:")
        print(f"     sudo $HOME/github/substrate/.venv/bin/python {os.path.basename(__file__)}")
    if pkg and dgpu and gpu_ok:
        combined = pkg + dgpu; budget = 45 + 30
        print(f"\n  combined pkg+dGPU = {combined:.1f} W vs PL0+dGPU budget {budget} W"
              + (f"; psys {psys:.1f} W" if psys_ok else " (psys broken)"))
        binds = combined < budget * 0.9
        print(f"  -> chassis envelope {'BINDS (sub-additive)' if binds else 'not binding at governor='+gov}")
    else:
        print(f"\n  VERDICT: not a valid combined measurement (GPU idle and/or psys broken). Only CPU")
        print(f"  package ({pkg:.1f} W, powersave) is valid. Re-run with venv python + performance governor.")
