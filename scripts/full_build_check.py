#!/usr/bin/env python3
"""full_build_check.py — prove (or refute) that EVERY module builds.

The supported `make all` can't run to green completion: Substrate.All is in the
top-level FILES list and OOMs by design ([[feedback_never_build_all_agda]]), and the
per-dir `files:` loop stops at the first failure in a directory. This driver instead
typechecks every .agda EXCEPT Substrate.All individually, with the exact build flags
and RAM cap, COLLECTING EVERY FAILURE (never stops), so the output is the complete
blocking list of non-building modules.

Faithful to the per-dir build: `agda --safe --without-K +RTS -M256m -RTS -i ..`
invoked from agda/. Parallel, but a shared-.agdai race can give a spurious failure;
re-run a reported failure solo to confirm.

Usage: full_build_check.py [-jN] [--timeout S]   (writes /tmp/full_build_results.tsv)
"""
import os, sys, time, subprocess, concurrent.futures as cf
import buildtime   # genlop-style per-dir timing ledger + ETA (same dir as this script)

HERE  = os.path.dirname(os.path.abspath(__file__))
AGDA_DIR = os.path.abspath(os.path.join(HERE, "..", "agda"))
SUB = os.path.join(AGDA_DIR, "Substrate")
FLAGS = ["--safe", "--without-K"]
MEM = os.environ.get("AGDA_FBC_MEM", "256m")   # ⟡cap-384: strict per-module GHC-heap gate (was 1024m)
J = 6
TIMEOUT = 600
ONLY = None
for a in sys.argv[1:]:
    if a.startswith("-j"): J = int(a[2:])
    elif a.startswith("--timeout"): TIMEOUT = int(a.split("=")[-1] if "=" in a else sys.argv[sys.argv.index(a)+1])
    elif a.startswith("--only"): ONLY = a.split("=")[-1] if "=" in a else sys.argv[sys.argv.index(a)+1]

files = []
for dp, _, fns in os.walk(SUB):
    for fn in fns:
        if fn.endswith(".agda"):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, AGDA_DIR)
            if rel == os.path.join("Substrate", "All.agda"):
                continue   # the one module we must never build
            if ONLY and not rel.startswith(ONLY):
                continue   # targeted subtree (testing / a focused re-check)
            files.append(p)
files.sort()

def check(p):
    cmd = ["agda", *FLAGS, "+RTS", f"-M{MEM}", "-RTS", "-i", "..", p]
    t0 = time.perf_counter()
    try:
        r = subprocess.run(cmd, cwd=AGDA_DIR, capture_output=True, text=True, timeout=TIMEOUT)
        dt = time.perf_counter() - t0
        if r.returncode == 0:
            return (p, "PASS", "", dt)
        tail = (r.stdout + r.stderr).strip().splitlines()
        return (p, "FAIL", " | ".join(tail[-3:])[:300], dt)
    except subprocess.TimeoutExpired:
        return (p, "TIMEOUT", f">{TIMEOUT}s", time.perf_counter() - t0)

total = len(files); done = 0
results = []
# genlop -p: estimate up-front from history.
hist = buildtime.read_all()
relpaths = [os.path.relpath(p, AGDA_DIR) for p in files]
pred = buildtime.predict(hist, relpaths)
print(f"genlop: estimated ~{buildtime.fmt(pred['total_cpu'] / J)} wall (-j{J}); "
      f"{pred['known']}/{pred['n']} modules have history", flush=True)
wall0 = time.perf_counter()
completed = set(); times = {}
with cf.ThreadPoolExecutor(max_workers=J) as ex:
    for res in ex.map(check, files):
        done += 1
        rel = os.path.relpath(res[0], AGDA_DIR)
        completed.add(rel); times[rel] = res[3]
        results.append(res[:3])
        if res[1] != "PASS":
            print(f"[{done}/{total}] {res[1]}: {rel}  ::  {res[2]}", flush=True)
        elif done % 100 == 0:
            # genlop -c: live ETA = Σ history(remaining) / J.
            remaining = [r for r in relpaths if r not in completed]
            eta = buildtime.predict(hist, remaining)["total_cpu"] / J
            print(f"[{done}/{total}] … {done} checked  elapsed {buildtime.fmt(time.perf_counter()-wall0)}"
                  f"  ETA ~{buildtime.fmt(eta)}", flush=True)
# record this run's times into the per-dir ledgers (parallel to make).
for rel, dt in times.items():
    buildtime.append(rel, dt)
print(f"genlop: actual {buildtime.fmt(time.perf_counter()-wall0)} wall "
      f"(estimate was ~{buildtime.fmt(pred['total_cpu'] / J)})", flush=True)

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
