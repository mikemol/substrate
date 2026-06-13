#!/usr/bin/env python3
"""full_build_check.py — prove (or refute) that EVERY module builds.

The supported `make all` can't run to green completion: Substrate.All is in the
top-level FILES list and OOMs by design ([[feedback_never_build_all_agda]]), and the
per-dir `files:` loop stops at the first failure in a directory. This driver instead
typechecks every .agda EXCEPT Substrate.All individually, with the exact build flags
and RAM cap, COLLECTING EVERY FAILURE (never stops), so the output is the complete
blocking list of non-building modules.

Faithful to the per-dir build: `agda --safe --without-K +RTS -M1024m -RTS -i ..`
invoked from agda/. Parallel, but a shared-.agdai race can give a spurious failure;
re-run a reported failure solo to confirm.

Usage: full_build_check.py [-jN] [--timeout S]   (writes /tmp/full_build_results.tsv)
"""
import os, sys, subprocess, concurrent.futures as cf

HERE  = os.path.dirname(os.path.abspath(__file__))
AGDA_DIR = os.path.abspath(os.path.join(HERE, "..", "agda"))
SUB = os.path.join(AGDA_DIR, "Substrate")
FLAGS = ["--safe", "--without-K"]
MEM = "1024m"
J = 6
TIMEOUT = 600
for a in sys.argv[1:]:
    if a.startswith("-j"): J = int(a[2:])
    elif a.startswith("--timeout"): TIMEOUT = int(a.split("=")[-1] if "=" in a else sys.argv[sys.argv.index(a)+1])

files = []
for dp, _, fns in os.walk(SUB):
    for fn in fns:
        if fn.endswith(".agda"):
            p = os.path.join(dp, fn)
            if os.path.relpath(p, AGDA_DIR) == os.path.join("Substrate", "All.agda"):
                continue   # the one module we must never build
            files.append(p)
files.sort()

def check(p):
    cmd = ["agda", *FLAGS, "+RTS", f"-M{MEM}", "-RTS", "-i", "..", p]
    try:
        r = subprocess.run(cmd, cwd=AGDA_DIR, capture_output=True, text=True, timeout=TIMEOUT)
        if r.returncode == 0:
            return (p, "PASS", "")
        tail = (r.stdout + r.stderr).strip().splitlines()
        return (p, "FAIL", " | ".join(tail[-3:])[:300])
    except subprocess.TimeoutExpired:
        return (p, "TIMEOUT", f">{TIMEOUT}s")

total = len(files); done = 0
results = []
with cf.ThreadPoolExecutor(max_workers=J) as ex:
    for res in ex.map(check, files):
        done += 1
        results.append(res)
        if res[1] != "PASS":
            print(f"[{done}/{total}] {res[1]}: {os.path.relpath(res[0], AGDA_DIR)}  ::  {res[2]}", flush=True)
        elif done % 100 == 0:
            print(f"[{done}/{total}] … {done} checked", flush=True)

out = "/tmp/full_build_results.tsv"
with open(out, "w") as f:
    for p, st, msg in results:
        f.write(f"{st}\t{os.path.relpath(p, AGDA_DIR)}\t{msg}\n")

npass = sum(1 for _,s,_ in results if s == "PASS")
fails = [(p,s,m) for p,s,m in results if s != "PASS"]
print(f"\n==== full build: {npass}/{total} PASS, {len(fails)} not-building ====")
for p, s, m in sorted(fails):
    print(f"  {s}: {os.path.relpath(p, AGDA_DIR)}")
print(f"\nfull results: {out}")
sys.exit(1 if fails else 0)   # non-zero ⇒ a module doesn't build (gate-blocking)
