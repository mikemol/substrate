#!/usr/bin/env python3
"""bridge_graph_shred.py — the VALUE-layer companion to rank4_shred.

rank4_shred reads the TYPE-dependency skeleton (data/record refs) — the rigid
top-down DAG. The wedge fluidity lives one layer down, in VALUES: `DivStr`
instances (the founded roots) and `Bridge`/`WedgeIso` definitions (the edges).

The methodology this tool serves: the top-down shred is the SPECIFICATION —
it enumerates the structural edges we want realized as wedge bridges at the
root level ("achieve identity down there"). This tool reads the value layer
and OVERLAYS it on the shred, reporting:

  * REALIZED   — a structural shred-edge between two founded roots that has a
                 wedge bridge (the two layers coincide on that edge: identity);
  * RIGID      — a structural shred-edge whose endpoints are founded but which
                 has NO bridge yet (the next bridges to build);
  * UNFOUNDED  — a shred-edge endpoint not yet a `DivStr` root (the next roots
                 to found), ranked by how many founded roots it would connect;
  * EXTRA      — a bridge with NO structural counterpart (pure new fluidity,
                 e.g. parity ℕ↠F₂: mod-2 is a constructed correspondence, not
                 a structural dependency).

When REALIZED = all founded-founded shred-edges and RIGID/UNFOUNDED are empty,
the bridge graph reproduces the shred graph: identity achieved down there.

Heuristic, like the other shred tools (regex over stripped source); rank is a
lower bound. Run from anywhere.
"""
import os, re, collections
from _agdatext import split_arrows, strip
sa = split_arrows

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))



# ---- 1. the top-down shred graph (reuse rank4_shred's ranking) -------------
text = {}
kind = {}
home = {}
modof = {}
fileof = {}
body = collections.defaultdict(list)
modre = re.compile(r"^module\s+(\S+)\s+where", re.M)
declre = re.compile(r"^(data|record)\s+(\S+)(.*)$")
for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"):
            continue
        p = os.path.join(dp, fn)
        t = strip(open(p, encoding="utf-8").read())
        text[p] = t
        mm = modre.search(t)
        if mm:
            modof[p] = mm.group(1)
            fileof[mm.group(1)] = p
        lines = t.splitlines()
        i = 0
        while i < len(lines):
            m = declre.match(lines[i])
            if m:
                name, rest = m.group(2), m.group(3)
                body[name].append(rest)
                kind.setdefault(name, m.group(1))
                home.setdefault(name, p)
                j = i + 1
                while j < len(lines) and (lines[j].strip() == "" or lines[j][:1] in " \t"):
                    if " : " in lines[j]:
                        body[name].append(lines[j].split(" : ", 1)[1])
                    j += 1
                i = j
                continue
            i += 1
known = set(kind)



def toks(s):
    return [t for t in re.split(r"[\s()\[\]{};,.]+", s) if t in known]


produced = set()
consumed = set()
sig = re.compile(r"^\s*[^\s:]+\s*:\s*(.+)$")
for t in text.values():
    for line in t.splitlines():
        m = sig.match(line)
        if not m:
            continue
        if "→" in m.group(1):
            parts = sa(m.group(1))
            for a in parts[:-1]:
                consumed |= set(toks(a))
            produced |= set(toks(parts[-1]))
        else:
            produced |= set(toks(m.group(1)))
imports = collections.defaultdict(set)
impre = re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)", re.M)
for p, t in text.items():
    if p not in modof:
        continue
    for m in impre.finditer(t):
        if m.group(1) in fileof:
            imports[modof[p]].add(m.group(1))
importers = collections.defaultdict(set)
for m, ds in imports.items():
    for d in ds:
        importers[d].add(m)


def reach(mod):
    seen = {mod}
    q = collections.deque([mod])
    while q:
        u = q.popleft()
        for v in importers[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) - 1


def rank(T):
    mod = modof.get(home[T], "")
    if T in consumed:
        return 4 if reach(mod) >= 40 else 3
    if T in produced:
        return 2
    return 1


ranks = {T: rank(T) for T in known}
peak = [T for T in known if ranks[T] == 4]


def refs(T):
    r = set()
    for b in body[T]:
        r |= set(toks(b))
    r.discard(T)
    return r


# structural edges (undirected) among rank-4 types, plus all refs of peak types
shred_edges = set()
for T in peak:
    for r in refs(T):
        shred_edges.add(frozenset((T, r)))


# ---- 2. the value layer: founded roots + bridge/iso edges ------------------
# roots: `<name> [params] = record { C = <CarrierHead> ; ...`
root_carrier = {}      # root-name -> carrier head type
rootdef = re.compile(r"^([^\s=]+)(?:\s+[^\s=]+)*\s*=\s*record\s*\{\s*C\s*=\s*([^\s;]+)")
for t in text.values():
    for line in t.splitlines():
        m = rootdef.match(line)
        if m:
            root_carrier[m.group(1)] = m.group(2)

# also recognize GRADED roots (Algebra.Wedge.Graded.GradedDivStr) — multi-line
# records the single-line rootdef regex misses (e.g. tower-graded). Detected by
# type signature; the graded carrier (C : ℕ → Set) is read from the record body.
graded_carrier = {}
gradedsig = re.compile(r"^([^\s:]+)\s*:\s*GradedDivStr\b", re.M)
for t in text.values():
    for gm in gradedsig.finditer(t):
        nm = gm.group(1)
        cm = re.search(re.escape(nm) + r"\s*=\s*record\s*\{[^}]*?\bC\s*=\s*([^\s;]+)", t, re.S)
        if cm:
            graded_carrier[nm] = cm.group(1)

# the LAWVERE ATOM axis: the flip/residue atom (Category.Lawvere) instantiated
# across silos — the cross-silo composability orthogonal to wedge-carrier
# bridges. Direct instances `name : <Atom> <carrier>` (record declarations and
# combinators have other shapes after the colon, so are excluded).
atom_re = re.compile(
    r"^([^\s:]+)\s*:\s*(FixedPointFree|InvolutiveResidue|CommutingInvolutions|TorsorAtom)\b\s*(.*)$",
    re.M)
atom_instances = []
for p, t in text.items():
    for am in atom_re.finditer(t):
        atom_instances.append((am.group(1), am.group(2), am.group(3).strip(), modof.get(p, "")))

# bridge/iso edges: `<name> : Bridge X Y` or `: WedgeIso X Y` with X,Y roots.
base_edges = []        # (kind, carrierX, carrierY, defname)
structural_iso = 0     # tensor-level structure maps (skipped as base edges)
# match the codomain Bridge/WedgeIso anywhere in a type signature line (so a
# parametric `name : (n) → Bridge ℕ-div (Cyc-div n)` is caught, not just direct).
edgere = re.compile(r"\b(Bridge|WedgeIso)\s+(.+)$")
for t in text.values():
    for line in t.splitlines():
        if " : " not in line:
            continue
        m = edgere.search(line)
        if not m:
            continue
        # extract known-root tokens (handles applied/parametric roots like
        # `Bridge ℕ-div (Cyc-div n)`); a base edge needs ≥2 distinct roots.
        rtoks = [t for t in re.split(r"[\s()]+", m.group(2)) if t in root_carrier]
        if len(rtoks) >= 2:
            base_edges.append((m.group(1), root_carrier[rtoks[0]], root_carrier[rtoks[1]], line.split(":")[0].strip()))
        else:
            structural_iso += 1

founded = set(root_carrier.values())
bridge_carrier_edges = {frozenset((a, b)) for _, a, b, _ in base_edges}


# ---- 3. overlay report -----------------------------------------------------
print("== founded roots (DivStr instances) ==")
for r, c in sorted(root_carrier.items()):
    deg = sum(1 for e in bridge_carrier_edges if c in e)
    print(f"   {r:14s} carries {c:8s}  (bridge-degree {deg})")

print("\n== bridge edges (value layer) ==")
for k, a, b, nm in sorted(base_edges, key=lambda x: x[3]):
    structural = frozenset((a, b)) in shred_edges
    tag = "matches a structural edge" if structural else "EXTRA (no structural edge — pure new fluidity)"
    print(f"   {nm:18s} {a} —{k}→ {b}   [{tag}]")

# founded-founded structural edges: realized vs rigid
ff = [e for e in shred_edges if all(x in founded for x in e)]
realized = [e for e in ff if e in bridge_carrier_edges]
rigid = [e for e in ff if e not in bridge_carrier_edges]
print(f"\n== structural edges between FOUNDED roots ({len(ff)}) ==")
print(f"   REALIZED ({len(realized)}) — identity achieved on this edge:")
for e in sorted(map(tuple, realized)):
    print(f"      {e[0]} ≡ {e[1]}")
print(f"   RIGID ({len(rigid)}) — both founded, NO bridge yet (build these):")
for e in sorted(map(tuple, rigid)):
    print(f"      {e[0]} — {e[1]}")

# unfounded endpoints: rank-4 types in shred edges not yet founded, ranked by
# how many founded roots they'd connect to.
cand = collections.Counter()
for e in shred_edges:
    a, b = tuple(e)
    for x, y in ((a, b), (b, a)):
        if x not in founded and y in founded and x in known:
            cand[x] += 1
print("\n== UNFOUNDED shred-types adjacent to founded roots (next roots to found) ==")
for T, n in cand.most_common():
    nbrs = sorted({(set(e) - {T}).pop() for e in shred_edges if T in e and (set(e) - {T}) and list(set(e) - {T})[0] in founded})
    print(f"   {T:18s} would connect to {n} founded root(s): {', '.join(nbrs)}")

print(f"\n(structure-map isos skipped as base edges: {structural_iso}; "
      f"identity achieved when RIGID and UNFOUNDED are both empty.)")

# ---- 4. the GRADED roots (index = grade) — invisible to the plain shred ------
if graded_carrier:
    print("\n== GRADED roots (GradedDivStr — the index-is-grade lift) ==")
    for r, c in sorted(graded_carrier.items()):
        print(f"   {r:18s} carries {c:8s}  (ℕ-graded; the plain-DivStr shred is blind to these)")

# ---- 5. the ATOM axis — cross-silo composability the bridge graph can't see --
if atom_instances:
    print("\n== ATOM axis (Lawvere flip/residue, shared across silos) ==")
    by_struct = collections.defaultdict(list)
    for nm, st, arg, mod in atom_instances:
        by_struct[st].append((nm, arg, mod))
    for st in sorted(by_struct):
        print(f"   {st}:")
        for nm, arg, mod in sorted(by_struct[st]):
            print(f"      {nm:18s} {arg:16s} [{mod}]")
    silos = sorted({mod for _, _, _, mod in atom_instances if mod})
    print(f"   → the SAME atom instantiated across {len(silos)} module(s): the cross-silo")
    print("     composability the wedge-carrier graph cannot see (Cantor = grade-★ = cone = V₄).")
