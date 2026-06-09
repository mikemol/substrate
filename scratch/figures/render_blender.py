#!/usr/bin/env python3
"""Render the Blender/Cycles figures, optionally across both GPUs.

Each *_bl.py runs inside Blender's bundled Python (3.14) which imports our venv
packages + data builders. Cycles can't mix compute backends within one render,
but these are independent stills — so we parallelise by *instance*: launch
several headless Blender processes at once, each pinned to one GPU via
BL_BACKEND (the NVIDIA RTX via CUDA, the Intel iGPU via ONEAPI).

    python scratch/figures/render_blender.py                      # all, RTX/CUDA
    python scratch/figures/render_blender.py klein fano           # a subset
    python scratch/figures/render_blender.py --devices CUDA,ONEAPI --jobs 2

Caveat: the Intel iGPU's first ONEAPI launch silently compiles kernels for
2–15 min (then caches); the RTX vastly outperforms it, so dual-GPU mainly helps
when batch size is large.
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLENDER = "blender"


def render_one(fig: Path, backend: str):
    env = dict(os.environ)
    if backend:
        env["BL_BACKEND"] = backend
        if backend == "ONEAPI":
            env["CYCLES_ONEAPI_ALL_DEVICES"] = "1"
    proc = subprocess.run([BLENDER, "--background", "--python", str(fig)],
                          capture_output=True, text=True, env=env)
    lines = proc.stdout.splitlines()
    wrote = any("BL_WROTE" in ln for ln in lines)
    dev = next((ln.split("BL_DEVICE", 1)[1].strip()
                for ln in lines if "BL_DEVICE" in ln), "?")
    tail = (proc.stderr.strip().splitlines()[-1:] or [""])[0]
    return fig.stem, wrote, dev, tail


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("filters", nargs="*", help="Only figures whose stem contains these.")
    ap.add_argument("--devices", default="CUDA",
                    help="Comma list of backends to spread across (e.g. CUDA,ONEAPI).")
    ap.add_argument("--jobs", type=int, default=0, help="Concurrent instances (default = #devices).")
    a = ap.parse_args(argv)

    figs = sorted(HERE.glob("*_bl.py"))
    if a.filters:
        figs = [f for f in figs if any(w in f.stem for w in a.filters)]
    if not figs:
        print("no matching *_bl.py figures")
        return 1

    devices = [d.strip() for d in a.devices.split(",") if d.strip()]
    jobs = a.jobs or len(devices)
    assign = [(f, devices[i % len(devices)]) for i, f in enumerate(figs)]
    print(f"rendering {len(figs)} figures · devices={devices} · jobs={jobs}")

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for stem, wrote, dev, tail in ex.map(lambda fb: render_one(*fb), assign):
            status = "ok" if wrote else "FAIL"
            print(f"  [{status:>4}] {stem:<22} [{dev}]" + ("" if wrote else f"  {tail}"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
