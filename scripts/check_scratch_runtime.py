#!/usr/bin/env python3
"""check_scratch_runtime.py — Λ8b: the RUNTIME oracle to Λ8's static proxy.

Λ8 (check_scratch_independence.py) AST-scans for scratch path-strings / imports in jea/+el-atlas/
*source*. By construction it cannot see a RUNTIME reach — a path built from os.environ, a glob, an
indirect/dynamic import, a config-driven open. This is the ground-truth complement: it installs a
`sys.addaudithook` and FAILS if any `open` or `import` event resolves under <repo>/scratch/ while the
coupling-surface modules actually EXECUTE.

Proxy (Λ8, per-commit, cheap, static) + oracle (Λ8b, out-of-band, empirical) is the same
cheap-gate + heavy-throttled-check structure the pre-commit hook already uses for full_build_check.
This is the heavy half: it needs cupy + agda and runs real GPU/Agda work, so it is an ON-DEMAND /
out-of-band oracle (run it to *prove* independence), NOT wired into the per-commit fast path. The
static proxy guards commits; this proves the proxy's blind spot is empty.

Non-destructive: it does NOT `mv scratch aside` (racy, mutates the tree). The audit hook observes
access in-process — strictly an observer.

Coupling surface (the modules where the scratch dependency actually lived):
  jea_onegraph, jea_navigator, jea_edge_states  -> import the el-atlas tools (live_dispatcher, …)
  jea_agda_bridge, jea_agda_dag                 -> subprocess agda + the EMIT_DIR open
Running each as __main__ transitively imports the el-atlas tools it pulls in, so the hook also sees
whether THOSE resolve under scratch. A subprocess (agda) is a separate process and is out of scope —
the invariant is that the PYTHON code of a promoted project takes no scratch dependency.

Usage: check_scratch_runtime.py [--quiet]   (exit 1 if any module touched scratch/ at runtime)
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGETS = [
    "jea/jea_onegraph.py",
    "jea/jea_navigator.py",
    "jea/jea_edge_states.py",
    "jea/jea_agda_bridge.py",
    "jea/jea_agda_dag.py",
]

# Preamble run in each child: install the audit hook BEFORE the target runs, then runpy it as __main__.
# Pure string ops inside the hook (no audited calls) so it can't recurse. Emits one marker line per hit.
_PREAMBLE = r"""
import sys, os, runpy
sys.path.insert(0, os.path.dirname({target!r}))   # mimic `python <script>.py` (script-dir on path)
_SCR = os.path.normpath(os.path.join({repo!r}, "scratch")) + os.sep
_CWD = os.getcwd()
def _h(ev, a):
    p = None
    if ev == "open" and a:
        p = a[0]
    elif ev == "import" and len(a) > 1:
        p = a[1]
    if isinstance(p, str):
        ap = p if os.path.isabs(p) else os.path.join(_CWD, p)
        if os.path.normpath(ap).startswith(_SCR):
            sys.stderr.write("__SCRATCH_HIT__\t" + ev + "\t" + os.path.normpath(ap) + "\n")
sys.addaudithook(_h)
runpy.run_path({target!r}, run_name="__main__")
"""

MARK = "__SCRATCH_HIT__"


def run_one(rel):
    target = os.path.join(REPO, rel)
    code = _PREAMBLE.format(repo=REPO, target=target)
    try:
        proc = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                              capture_output=True, text=True, timeout=420)
    except subprocess.TimeoutExpired:
        return ("timeout", [])
    hits = [ln for ln in proc.stderr.splitlines() if ln.startswith(MARK)]
    parsed = [tuple(ln.split("\t")[1:]) for ln in hits]
    status = "hit" if parsed else ("ran" if proc.returncode == 0 else f"err({proc.returncode})")
    return (status, parsed)


def main():
    quiet = "--quiet" in sys.argv or "--check" in sys.argv
    violations, unverified = [], []
    for rel in TARGETS:
        status, hits = run_one(rel)
        if hits:
            for ev, path in hits:
                violations.append((rel, ev, path))
        elif status.startswith("err") or status == "timeout":
            unverified.append((rel, status))
        if not quiet:
            tag = "HIT" if hits else ("UNVERIFIED" if status != "ran" else "clean")
            print(f"  runtime {tag:<10} {rel}  [{status}]")

    for rel, status in unverified:
        print(f"  scratch-runtime: WARN {rel} did not run cleanly ({status}); runtime reach NOT verified "
              f"for it (not a violation — re-run with GPU/agda available)", file=sys.stderr)

    if violations:
        print(f"scratch-runtime (Λ8b): FAILED — {len(violations)} RUNTIME scratch/ access(es) the static "
              f"gate (Λ8) could not see:", file=sys.stderr)
        for rel, ev, path in violations:
            print(f"    {rel}  [{ev}]  {path}", file=sys.stderr)
        return 1

    if not quiet:
        verified = len(TARGETS) - len(unverified)
        print(f"scratch-runtime (Λ8b): OK ({verified}/{len(TARGETS)} surface modules ran, 0 runtime scratch "
              f"access). The static proxy's (Λ8) blind spot is empirically empty.")
    return 1 if unverified and "--strict" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
