#!/usr/bin/env python3
"""primitive_catalogue.py — REGENERATE the categorical-primitive → instance-module
catalogue by inference from the source tree, instead of trusting a frozen hand-written
aggregator (Substrate.Category.PrimitiveInstances) whose comments rot.

Per [[feedback_registry_as_pi_not_markdown]] and the el-atlas instrument idiom: the
value of an instance-catalogue is a DERIVATION, not a snapshot. PrimitiveInstances is a
pure leaf aggregator (0 exports, only importer = Substrate.All) whose sole content is a
curated list "these modules instantiate these primitives." That claim is mechanically
recoverable — and this script recovers it, witness-first.

DEFINITIONS (witness-level, like realizability_surface.py's "produced"):
  * A PRIMITIVE is a `record`/`data` declared under Substrate/Category/ — the
    categorical universal-property vocabulary (Cone, BCSquare, FreeLinearization,
    FieldBond, GTorsor, Strict2Monoid, …).
  * Module M INSTANTIATES primitive P iff M has a top-level definition `nm : Sig`
    whose RESULT type (last →-segment) names P. I.e. M produces a P. This is an
    approximate lower bound (misses some infix/where-bound producers), documented
    as such — the same caveat realizability_surface.py carries.

MODES:
  (default)            regenerate + print the catalogue: primitive → [modules].
  --audit MODULE       value-residue audit of one module (is it safe to remove?):
                       exports, real importers (ex-All), bare-import build-coverage.
  --diff MODULE        compare a bare-import aggregator (e.g. PrimitiveInstances) to
                       the regenerated catalogue: what it lists that inference misses,
                       and what inference finds that it never listed (its staleness).

Usage:
  scripts/primitive_catalogue.py
  scripts/primitive_catalogue.py --audit Substrate.Category.PrimitiveInstances
  scripts/primitive_catalogue.py --diff  Substrate.Category.PrimitiveInstances
"""
import os, re, sys, collections
from _agdatext import strip

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
AGDA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda"))

modre  = re.compile(r"^module\s+(\S+)", re.M)   # name = first token; `where` may be on next line
declre = re.compile(r"^(record|data)\s+([A-Za-z0-9_'⟦⟧]+)", re.M)
# a top-level definition signature: `name : type...` at column 0, name not a keyword.
sigre  = re.compile(r"^([A-Za-z0-9_'∘+*<>≈≅⊕⊗·-]+)\s*:\s*(.+)$", re.M)
impre  = re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)", re.M)
pubre  = re.compile(r"\bopen\s+import\s+\S+.*\bpublic\b|\bopen\s+\S+\s+public\b")

# ---- scan the tree -----------------------------------------------------------
text, raw_text, modof, fileof = {}, {}, {}, {}
for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p = os.path.join(dp, fn)
        r = open(p, encoding="utf-8").read()
        t = strip(r)
        m = modre.search(t)
        if not m: continue
        nm = m.group(1)
        raw_text[nm] = r; text[nm] = t; modof[p] = nm; fileof[nm] = p

def is_under_category(p):
    return os.sep + "Category" + os.sep in p or p.endswith(os.sep + "Category.agda")

# ---- the primitive vocabulary: record/data declared under Category/ ----------
PRIMS = set()
for nm, p in fileof.items():
    if is_under_category(p):
        for d in declre.finditer(text[nm]):
            PRIMS.add(d.group(2))
# drop trivially-generic helpers that are not universal-property primitives
PRIMS -= {"⊤", "⊥"}

def result_head_tokens(sig):
    """Tokens appearing in the RESULT type (after the last top-level →)."""
    # crude top-level arrow split: ignore arrows inside parens/braces
    depth = 0; last = 0
    i = 0
    s = sig
    while i < len(s) - 1:
        c = s[i]
        if c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        elif depth == 0 and s[i] == "→":
            last = i + 1
        elif depth == 0 and s[i:i+2] == "->":
            last = i + 2
        i += 1
    res = s[last:]
    return set(re.split(r"[\s()\[\]{};,.\"]+", res))

# ---- regenerate: primitive -> [modules that produce it] ----------------------
def regenerate():
    cat = collections.defaultdict(set)
    for nm in fileof:
        for sm in sigre.finditer(text[nm]):
            sig = sm.group(2)
            heads = result_head_tokens(sig)
            for P in heads & PRIMS:
                cat[P].add(nm)
    return cat

# ---- module export surface + reverse deps ------------------------------------
def exports(nm):
    pubs = len(pubre.findall(text.get(nm, "")))
    defs = [sm.group(1) for sm in sigre.finditer(text.get(nm, ""))]
    return pubs, defs

def importers(target):
    real = []
    for nm in fileof:
        if nm == target: continue
        for m in impre.finditer(text[nm]):
            if m.group(1) == target:
                real.append(nm)
                break
    return real

def bare_imports(nm):
    out = []
    for ln in raw_text.get(nm, "").splitlines():
        m = re.match(r"^import\s+(\S+)", ln.strip())
        if m: out.append(m.group(1))
    return out

def makefile_covered(mod):
    rel = os.path.join(AGDA, *mod.split(".")) + ".agda"
    if not os.path.isfile(rel): return None          # no file
    mk = os.path.join(os.path.dirname(rel), "Makefile")
    base = os.path.basename(rel)
    if os.path.isfile(mk) and base in open(mk, encoding="utf-8").read():
        return True
    return False

# ---- drivers -----------------------------------------------------------------
def cmd_catalogue():
    cat = regenerate()
    print(f"# regenerated primitive catalogue — {len(PRIMS)} primitives, "
          f"{sum(len(v) for v in cat.values())} (primitive,module) witnesses\n")
    for P in sorted(cat, key=lambda k: (-len(cat[k]), k)):
        print(f"## {P}  ({len(cat[P])})")
        for m in sorted(cat[P]):
            print(f"  - {m}")
    empty = sorted(PRIMS - set(cat))
    if empty:
        print(f"\n# primitives with NO inferred producer ({len(empty)}): " + ", ".join(empty))

def cmd_audit(target):
    pubs, defs = exports(target)
    imps = importers(target)
    bims = bare_imports(target)
    print(f"# value-residue audit: {target}\n")
    print(f"export surface : {pubs} `open … public`, {len(defs)} top-level defs"
          + ("  → exports NOTHING" if pubs == 0 and not defs else ""))
    nonall = [i for i in imps if i != "Substrate.All"]
    print(f"real importers : {len(imps)} total; ex-All = {len(nonall)}"
          + ("  → only All.agda depends on it" if not nonall else ""))
    for i in nonall: print(f"   · {i}")
    if bims:
        cov = [makefile_covered(m) for m in bims]
        nfile = sum(1 for c in cov if c is None)
        ncov  = sum(1 for c in cov if c is True)
        nunc  = sum(1 for c in cov if c is False)
        print(f"\nbare imports   : {len(bims)} modules force-typechecked")
        print(f"   build-covered by a per-dir Makefile : {ncov}/{len(bims)}")
        print(f"   UNIQUE build-reach (not covered)     : {nunc}")
        print(f"   import path resolves to no file      : {nfile}")
        if nunc:
            print("   --- uncovered (removal loses build-coverage): ---")
            for m, c in zip(bims, cov):
                if c is False: print(f"       {m}")
        verdict = (pubs == 0 and not defs and not nonall and nunc == 0)
        print("\nVERDICT: " + ("REDUNDANT — 0 exports, only All imports it, every listed "
                                "module is independently build-covered. Safe to remove once "
                                "the catalogue is regenerable (this script)."
                                if verdict else
                                "NOT trivially removable — see non-zero residue above."))

def cmd_diff(target):
    cat = regenerate()
    listed = set(bare_imports(target))
    inferred = set().union(*cat.values()) if cat else set()
    only_listed   = sorted(listed - inferred)
    only_inferred = sorted(inferred - listed)
    print(f"# diff {target}  vs  regenerated catalogue\n")
    print(f"listed-but-not-inferred ({len(only_listed)}) — modules it names that produce "
          f"no Category primitive (support/infra, or inference miss):")
    for m in only_listed: print(f"   - {m}")
    print(f"\ninferred-but-not-listed ({len(only_inferred)}) — primitive producers the "
          f"frozen aggregator MISSES (its staleness; the regen is fresher):")
    for m in only_inferred: print(f"   + {m}")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--audit" in args:
        cmd_audit(args[args.index("--audit") + 1])
    elif "--diff" in args:
        cmd_diff(args[args.index("--diff") + 1])
    else:
        cmd_catalogue()
