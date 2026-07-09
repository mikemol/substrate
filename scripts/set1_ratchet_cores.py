#!/usr/bin/env python3
"""set1_ratchet_cores.py — the Set₁ policy gate, measured from ELABORATED CORES.

WHY NOT GREP (read before changing)
  The predecessor grepped `Set₁` in stripped source. That counts SOURCE TOKENS, not
  definitions: one `record R : Set₁` token yields ~4 Set₁ definitions in the core
  (the record, its constructor, and Agda's generated transp-/hcomp- helpers), and
  Set₁-TYPED FUNCTIONS carry no token at all. Measured on Substrate/Algebra:
  5 tokens vs 26 Set₁ definitions. Different quantities, not a noisy estimate.
  A sort is elaborated information; source text is elaboration's INPUT.

THE MEASURE
  A definition inhabits Set₁ iff the codomain sort of its type (Πs peeled; when the
  codomain is itself `Sort s`, that s) is `Type` at level >= 1. The shim emits this
  per defmark as {"sort":"Type","level":n}.

TWO INVARIANTS THE SHIM IMPOSES (both learned by failing)
  (a) CWD must be the agda include root; decodeInterface resolves the interface's
      recorded include paths against CWD. Elsewhere: "decode Nothing".
  (b) LC_ALL must be UTF-8; qnames contain `≈`/`₁`. Under C locale the shim decodes
      successfully then dies in commitBuffer. The error text lies in both cases.

EMPTY IS NOT SUCCESS
  If the core tree is absent or a core fails to decode, this gate EXITS NONZERO and
  says so. "Cannot measure" is not "no debt" — the residue pre-commit's worklist
  gate exists to close (a tracker that can't execute is not tracking).

BASELINE  scripts/set1_baseline_cores.txt holds "<defs> <cores>". BOTH are recorded:
  the Set₁ count is taken over whatever cores exist, so a baseline over a different
  core set is not comparable. If the core count changed, the gate says so and refuses
  to compare (it does not silently ratchet against a moving denominator). Rebuild the
  full tree (agda/Makefile) so the denominator is the whole corpus.
"""
import os, sys, glob, json, subprocess

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGDA_ROOT = os.path.join(ROOT, "agda")
SHIM      = os.environ.get("AGDAI_SHIM", os.path.join(ROOT, "jea", "metalanguage", "agdai_shim"))
BASELINE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set1_baseline_cores.txt")
QUIET     = "--quiet" in sys.argv

def find_cores():
    build = os.path.join(AGDA_ROOT, "_build")
    roots = []
    if os.path.isdir(build):
        for v in sorted(os.listdir(build)):
            d = os.path.join(build, v, "agda", "Substrate")
            if os.path.isdir(d): roots.append(d)
    roots.append(os.path.join(AGDA_ROOT, "Substrate"))     # --local-interfaces
    seen, out = set(), []
    for r in roots:
        for c in glob.glob(os.path.join(r, "**", "*.agdai"), recursive=True):
            k = os.path.relpath(c, AGDA_ROOT)
            if k not in seen: seen.add(k); out.append(c)
    return sorted(out)

def defmarks(core):
    env = dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")
    p = subprocess.run([SHIM, os.path.relpath(core, AGDA_ROOT)],
                       cwd=AGDA_ROOT, env=env, capture_output=True, text=True, timeout=180)
    if "decode Nothing" in p.stderr: return None
    return [json.loads(l) for l in p.stdout.splitlines() if l.startswith('{"unit"')]

def assert_shim_reports_sorts():
    """A shim that DECODES but omits the `sort` field makes every definition look
    non-Set₁, and the ratchet would silently lower the baseline to 0. The probe must
    be present, not merely the decoder. (The repo's 2.8.0 shim decodes but predates
    the sort field — see ⟡shim-upstream.) Detect absence; never infer it from a low count."""
    for c in cores[:8]:
        dm = defmarks(c)
        if dm:
            if any("sort" in d for d in dm):
                return
            print(f"set1-ratchet(cores): shim {SHIM} decodes but emits NO 'sort' field.")
            print("  It cannot measure universe levels, so it cannot certify Set₁ debt.")
            print("  Use a sort-emitting shim (AGDAI_SHIM=...) or upstream the field (⟡shim-upstream).")
            sys.exit(1)
    print("set1-ratchet(cores): no decodable core carried defmarks — cannot verify the shim.")
    sys.exit(1)

cores = find_cores()
if not cores:
    print("set1-ratchet(cores): NO CORES — cannot measure, so cannot certify.")
    print("  build the tree first (agda/Makefile: one agda per file, -i ..).")
    sys.exit(1)

assert_shim_reports_sorts()

n, undec = 0, []
for c in cores:
    dm = defmarks(c)
    if dm is None: undec.append(c); continue
    n += sum(1 for d in dm if isinstance(d.get("level"), int) and d["level"] >= 1)

if undec:
    print(f"set1-ratchet(cores): {len(undec)} of {len(cores)} cores UNDECODABLE — census incomplete.")
    for c in undec[:3]: print(f"  {os.path.relpath(c, AGDA_ROOT)}")
    print("  An incomplete census is not a low count. Rebuild cores; do not certify.")
    sys.exit(1)

if os.path.exists(BASELINE):
    parts = open(BASELINE).read().split()
    base, base_cores = int(parts[0]), (int(parts[1]) if len(parts) > 1 else None)
else:
    open(BASELINE, "w").write(f"{n} {len(cores)}\n")
    print(f"set1-ratchet(cores): baseline recorded = {n} Set₁ definitions over {len(cores)} cores")
    sys.exit(0)

if base_cores is not None and base_cores != len(cores):
    print(f"set1-ratchet(cores): CORE SET CHANGED — {len(cores)} cores now, baseline took {base_cores}.")
    print(f"  Set₁ count {n} is not comparable to baseline {base} over a different denominator.")
    print("  Rebuild the full tree, then re-baseline. (A moving denominator is not a ratchet.)")
    sys.exit(1)

if n > base:
    print(f"set1-ratchet(cores): BROKEN — {n} > baseline {base} Set₁-inhabiting definitions.")
    print("  Set₁ is policy debt: do not FIELD a Set-valued carrier/relation — PARAMETERIZE it")
    print("  (see Substrate.Category.Lawvere's carrier-generic atoms).")
    sys.exit(1)
if n < base:
    open(BASELINE, "w").write(f"{n}\n")
    print(f"set1-ratchet(cores): baseline LOWERED {base} -> {n} (debt paid down)")
elif not QUIET:
    print(f"set1-ratchet(cores): at baseline {base} ({len(cores)} cores, legacy debt, frozen)")
sys.exit(0)
