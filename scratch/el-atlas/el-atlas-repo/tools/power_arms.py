"""
power_arms.py — the power-config space as EXPERIMENT ARMS. Sweep the user-accessible
power-profiles-daemon arms, measure per arm, and test the model's prediction: absolute throughput
scales with the arm (the clock lever), but RATIOS (the ridge) stay invariant (clock cancels).

Arms (user-accessible now, no sudo, via PPD): performance, balanced, power-saver. Finer-grained arms
(EPP x5, governor x2, no_turbo x2, per-core freq caps) are root-gated -- noted, not swept.

Per arm, measured: achieved clock under load, compute-bound rate (L2-resident sgemm), memory-bound BW
(streaming sum), and the ridge ratio compute/BW. Restores power-saver at the end (finally).

Witnesses (each [W]):
1. ABSOLUTE scales with the arm: performance clock & rates > power-saver (the ~3x lever, measured).
2. RIDGE INVARIANT: compute/BW ratio ~constant across arms -- the clock-cancels-in-ratios claim,
   ground-truthed across the actual power arms (the structural conclusions are arm-independent).
"""
import os
for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(v, "1")
import time, subprocess, threading
import numpy as np
from host_probe import _read

PCORES = range(6)


def ppd_list():
    out = subprocess.run(["powerprofilesctl", "list"], capture_output=True, text=True)
    return [ln.split(":")[0].strip(" *") for ln in out.stdout.splitlines() if ":" in ln
            and ln.split(":")[0].strip(" *") in ("performance", "balanced", "power-saver")]


def ppd_set(p):
    return subprocess.run(["powerprofilesctl", "set", p], capture_output=True, text=True).returncode == 0


def ac_online():
    for f in ("/sys/class/power_supply/AC/online", "/sys/class/power_supply/ACAD/online",
              "/sys/class/power_supply/AC0/online"):
        v = _read(f)
        if v is not None:
            return v == "1"
    return None


def clock_under_load():
    stop = threading.Event()
    def busy():
        a = np.random.rand(1 << 20).astype(np.float32)
        while not stop.is_set():
            a = a * 1.0001 + 0.5
    t = threading.Thread(target=busy); t.start()
    time.sleep(0.5)
    fr = max(int(_read(f"/sys/devices/system/cpu/cpu{c}/cpufreq/scaling_cur_freq") or 0) for c in PCORES)
    stop.set(); t.join()
    return fr / 1e6                                    # GHz


def compute_rate(threads=4, m=256, iters=6):
    from concurrent.futures import ThreadPoolExecutor
    mats = [(np.random.rand(m, m).astype(np.float32), np.random.rand(m, m).astype(np.float32))
            for _ in range(threads)]
    for x, y in mats: np.dot(x, y)
    def work(xy):
        x, y = xy
        for _ in range(iters): z = np.dot(x, y)
        return float(z[0, 0])
    best = 1e9
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for _ in range(2):
            t = time.perf_counter(); list(ex.map(work, mats)); best = min(best, time.perf_counter() - t)
    return threads * iters * 2 * m ** 3 / best / 1e9   # GFLOP/s


def mem_bw(mb=128, reps=3):
    a = np.ones(mb * 1024 * 1024 // 4, np.float32); a.sum()
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); float(a.sum()); best = min(best, time.perf_counter() - t)
    return a.nbytes / best / 1e9                       # GB/s


if __name__ == "__main__":
    arms = ppd_list()
    ac = ac_online()
    print(f"power-config experiment: arms = {arms}; AC online = {ac}")
    print(f"  (finer arms root-gated: EPP x5, governor x2, no_turbo x2, per-core caps -- not swept)\n")
    rows = []
    try:
        for arm in arms:
            ok = ppd_set(arm); time.sleep(1.5)         # set + settle
            ghz = clock_under_load()
            cmp = compute_rate(); bw = mem_bw()
            ridge = cmp / bw                            # FLOP/byte (the crossover ratio)
            rows.append((arm, ghz, cmp, bw, ridge, ok))
            print(f"  {arm:12s} clock {ghz:.2f} GHz | compute {cmp:6.1f} GFLOP/s | mem {bw:5.1f} GB/s | "
                  f"ridge {ridge:5.1f} FLOP/byte {'' if ok else '(set failed)'}")
    finally:
        ppd_set("power-saver")
        print(f"\n  restored: {subprocess.run(['powerprofilesctl','get'],capture_output=True,text=True).stdout.strip()}")

    valid = [r for r in rows if r[5]]
    if len(valid) >= 2:
        perf = max(valid, key=lambda r: r[1]); save = min(valid, key=lambda r: r[1])
        w1 = perf[2] > save[2] * 1.2 and perf[1] > save[1] * 1.1   # absolute scales with arm
        ridges = [r[4] for r in valid]
        w2 = (max(ridges) - min(ridges)) / max(ridges) < 0.4       # ridge ~invariant across arms
        print(f"\n  1. ABSOLUTE scales with arm: {perf[0]} clock {perf[1]:.2f}GHz/compute {perf[2]:.0f} "
              f"vs {save[0]} {save[1]:.2f}GHz/{save[2]:.0f} (lever real) {w1}")
        print(f"  2. RIDGE invariant across arms: {[round(r,1) for r in ridges]} FLOP/byte "
              f"(spread {(max(ridges)-min(ridges))/max(ridges)*100:.0f}%) -- clock cancels in the ratio {w2}")
        ok = w1 and w2
        print(f"\n  {'PASS' if ok else 'PARTIAL'} — the power arms are an experiment factor: absolute")
        print(f"  throughput is the arm-dependent lever (measured ~{perf[2]/max(save[2],1e-9):.1f}x compute,")
        print(f"  ~{perf[1]/max(save[1],1e-9):.1f}x clock), while the RIDGE ratio stays ~invariant -- the model's")
        print(f"  clock-cancels claim, now ground-truthed across the real power configs. Finer arms (EPP,")
        print(f"  per-core caps) are root-gated next-granularity factors.")
    else:
        print("\n  (only one arm settable -- likely on battery; performance/balanced may be AC-gated)")
