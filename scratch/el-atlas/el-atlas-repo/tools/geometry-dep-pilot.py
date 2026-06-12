"""
geometry-dep-pilot.py — S24: speculative Cartesian joining proximate to
breakers; geometry dependencies beyond the declarations.

Three nested certificates, now all instrumented:
  DECLARED support (_CLAIM_DEPS)  >=  READ support (dep-audit)  >=
  GEOMETRICALLY ACTIVE support (this pilot).
A. Within each claim's declared projection: (i) INERT axes — declared
   (and possibly read) but the verdict is constant along them under every
   fixing of the rest: read != geometric dependence. (ii) The INTERACTION
   GRAPH — knob pairs (i,j) where whether-i-matters depends on j (the
   discrete epistasis test): joint corner geometry the dep-SET never
   declared. Empty graph after inert-removal = the claim's geometry
   factors per-axis (CRT-splittable: a joiner candidate); edges =
   entanglement (cross-talk).
B. SPECULATIVE JOIN PROXIMATE TO BREAKERS: for each claim, take a breaker
   cell (verdict != base) and Cartesian-join it with every undeclared
   axis (all values) and every undeclared axis PAIR, read-recorder on:
   any undeclared read or verdict variation is a finding. This upgrades
   the dep-audit from 600 random samples to exhaustive coverage of the
   corners where conditional reads would hide.
"""
import importlib.util, itertools
from collections import defaultdict
spec = importlib.util.spec_from_file_location("h", "tools/el-atlas-depsort-v3.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)

class Rec(dict):
    def __init__(self, m): super().__init__(m); self.reads = set()
    def __getitem__(self, k): self.reads.add(k); return super().__getitem__(k)
    def get(self, k, d=None): self.reads.add(k); return super().get(k, d)

print("A. geometry within declared support  (claim: declared -> active; inert; interaction edges)")
splittable, entangled = [], []
for name in h.CLAIMS:
    deps = list(h._CLAIM_DEPS[name])
    V = {}
    for vals in itertools.product(*(h.KNOBS[k] for k in deps)):
        m = dict(h.BASE); m.update(zip(deps, vals)); V[vals] = h.CLAIMS[name](m)
    inert = []
    for ax in range(len(deps)):
        g = defaultdict(set)
        for vals, vd in V.items(): g[tuple(v for t, v in enumerate(vals) if t != ax)].add(vd)
        if all(len(s) == 1 for s in g.values()): inert.append(deps[ax])
    edges = []
    for i, j in itertools.combinations(range(len(deps)), 2):
        if deps[i] in inert or deps[j] in inert: continue
        g = defaultdict(dict)
        for vals, vd in V.items():
            g[tuple(v for t, v in enumerate(vals) if t not in (i, j))][(vals[i], vals[j])] = vd
        inter = False
        for tab in g.values():
            for a, a2 in itertools.combinations(h.KNOBS[deps[i]], 2):
                for b, b2 in itertools.combinations(h.KNOBS[deps[j]], 2):
                    if (tab[(a, b)] == tab[(a2, b)]) != (tab[(a, b2)] == tab[(a2, b2)]): inter = True; break
                if inter: break
            if inter: break
        if inter: edges.append((deps[i], deps[j]))
    active = [k for k in deps if k not in inert]
    tag = "SPLITTABLE" if not edges and len(active) > 1 else ("entangled" if edges else "")
    (splittable if tag == "SPLITTABLE" else entangled if edges else []).append(name)
    print(f"  {name:4s}: {len(deps)} declared -> {len(active)} active; inert {inert if inert else '-'}; edges {edges if edges else '-'} {tag}")

print("\nB. speculative Cartesian join proximate to breakers (undeclared axes, singles + all pairs, recorder on)")
bad, checked = [], 0
for name in h.CLAIMS:
    deps = set(h._CLAIM_DEPS[name]); basev = h.CLAIMS[name](h.BASE)
    cell = dict(h.BASE)
    for vals in itertools.product(*(h.KNOBS[k] for k in sorted(deps))):
        m = dict(h.BASE); m.update(zip(sorted(deps), vals))
        if h.CLAIMS[name](m) != basev: cell = m; break
    cellv = h.CLAIMS[name](cell)
    und = [k for k in h.KNOBS if k not in deps]
    joins = [((k,), (v,)) for k in und for v in h.KNOBS[k]]
    joins += [((k1, k2), (v1, v2)) for k1, k2 in itertools.combinations(und, 2)
              for v1 in h.KNOBS[k1] for v2 in h.KNOBS[k2]]
    for ks, vs in joins:
        m = dict(cell); m.update(zip(ks, vs)); r = Rec(m); checked += 1
        val = h._RAW_CLAIMS[name](r)
        if (not r.reads <= deps) or val != cellv:
            bad.append((name, ks, vs, sorted(r.reads - deps), val, cellv))
print(f"  {checked} breaker-proximate joined cells across {len(h.CLAIMS)} claims: " +
      ("ALL FLAT, ALL READS DECLARED — the random audit is now breaker-proximate-exhaustive" if not bad else f"FINDINGS: {bad[:6]}"))
