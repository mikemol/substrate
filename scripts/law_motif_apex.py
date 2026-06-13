#!/usr/bin/env python3
"""law_motif_apex.py — find apex-candidates by clustering FUNCTION SIGNATURES on
relational LAW-MOTIFS, the thing agda_similarity (token-cosine) and type_sppf
(data/record skeletons) both miss.

WHY THE OTHER TOOLS MISS IT
  * agda_similarity = multi-scale token cosine. Instances of one categorical law
    (eval/reify, ℚ reduce, wedge recon, GenericHodgeStar star/star-inv, CRT) live
    in disjoint vocabularies → near-zero token overlap → never cluster. The shared
    content is ~3 tokens of TYPE (`f (g x) ≡ x`) drowned in domain tokens, and it is
    spread across a TRIPLE (F, s, the law-proof), not one comparable unit.
  * type_sppf = hash-consed skeletons of `data`/`record` decls only. A law lives in a
    FUNCTION signature (`name : … ≡ …`), which it never reads. And the proof TERMS are
    wildly different (refl / sym (wedge-eq w) / a field) — only the TYPE is invariant.

WHAT THIS DOES
  Reads every top-level `name : Type` (function/lemma) signature, flattens it, and
  matches the equation it ends in against a library of categorical law-motifs:
      retraction/section   f (g x) ≡ x
      idempotent           f (f x) ≡ f x
      involution           f (f x) ≡ x
  Clusters instances by motif. For each motif with ≥ MIN instances, reports whether a
  PARAMETRIC apex exists — a signature quantified over the motif's function symbols
  that *takes the law as a hypothesis* (e.g. split-Canonical : … (F∘s≡id) → …). Absent
  ⇒ APEX-CANDIDATE (mechanises [[feedback_cluster_means_find_apex]]); present ⇒
  convergence-check (do the instances route through it, or re-prove the law?).

Approximate by construction (regex over flattened sigs; misses infix/where-bound laws)
— a LOWER bound, like realizability_surface.py. Usage: law_motif_apex.py [--min N]
"""
import os, re, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
MIN = 3
if "--min" in sys.argv:
    MIN = int(sys.argv[sys.argv.index("--min") + 1])

def strip(s):
    s = re.sub(r"\{-.*?-\}", " ", s, flags=re.S)
    return re.sub(r"--[^\n]*", "", s)

# top-level `name : type` signatures (col-0 name, may span indented lines), and the
# data/record FIELD signatures (indented `field` members) — laws often live as fields.
ID = r"[^\s():{}]+"
sig_top = re.compile(r"^([A-Za-z_]" + r"[^\s():{}]*)\s*:\s*(.+?)(?=^\S|\Z)", re.M | re.S)

def flatten(t):
    return re.sub(r"\s+", " ", t).strip()

def last_arrow_segment(t):
    # the result type: after the last top-level → (depth 0)
    depth = 0; last = 0; i = 0
    while i < len(t):
        c = t[i]
        if c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        elif depth == 0 and c == "→": last = i + 1
        i += 1
    return t[last:].strip()

# motif matchers on a flattened "LHS ≡ RHS" result type.
# tokens of an application: split on spaces respecting parens.
def split_eq(seg):
    # top-level ≡
    depth = 0
    for i, c in enumerate(seg):
        if c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        elif depth == 0 and c == "≡":
            return seg[:i].strip(), seg[i+1:].strip()
    return None

def atoms(s):
    # split an application into head + args at depth 0 (very rough)
    out = []; depth = 0; cur = ""
    for c in s:
        if c in "([{": depth += 1; cur += c
        elif c in ")]}": depth -= 1; cur += c
        elif c == " " and depth == 0:
            if cur: out.append(cur); cur = ""
        else: cur += c
    if cur: out.append(cur)
    return out

def unparen(s):
    s = s.strip()
    while s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()
    return s

def classify(seg):
    eq = split_eq(seg)
    if not eq: return None
    lhs, rhs = unparen(eq[0]), unparen(eq[1])
    la = atoms(lhs)
    if len(la) < 2: return None
    f = la[0]                       # head of LHS application
    inner = unparen(" ".join(la[1:]))   # the argument(s) to f
    ia = atoms(inner)
    if len(ia) < 2: return None
    g = ia[0]                       # head of the inner application
    x = unparen(ia[-1])             # innermost argument
    # f (g … x) ≡ ?
    if rhs == x and g != f:        return ("retraction/section  f (g x) ≡ x", f, g, x)
    if rhs == x and g == f:        return ("involution          f (f x) ≡ x", f, g, x)
    if unparen(rhs) == flatten(f + " " + x) and g == f:
        return ("idempotent          f (f x) ≡ f x", f, g, x)
    return None

# ---- scan ----
instances = collections.defaultdict(list)   # motif -> [(name, file, f, g)]
apex = collections.defaultdict(list)         # motif -> [parametric apex sigs]
for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p = os.path.join(dp, fn); rel = os.path.relpath(p, ROOT)
        t = strip(open(p, encoding="utf-8").read())
        for m in sig_top.finditer(t):
            name, ty = m.group(1), flatten(m.group(2))
            seg = last_arrow_segment(ty)
            c = classify(seg)
            if c:
                instances[c[0]].append((name, rel, c[1], c[2]))
            # apex heuristic: a sig that takes a law-shaped HYPOTHESIS (… ≡ … →) and is
            # quantified (has explicit (F : …)(s : …) binders) — i.e. parametric over the law.
            if "≡" in ty and "→" in ty and re.search(r"\([A-Za-z]\w*\s*:\s*[^)]*→", ty):
                for seg2 in re.split(r"→", ty):
                    cc = classify(seg2.strip())
                    if cc:
                        apex[cc[0]].append((name, rel)); break

print(f"# law-motif apex scan — function signatures matching categorical law-motifs\n")
for motif in sorted(instances, key=lambda k: -len(instances[k])):
    inst = instances[motif]
    if len(inst) < MIN: continue
    print(f"## {motif}   — {len(inst)} instances")
    for name, rel, f, g in sorted(inst)[:30]:
        print(f"   {name:28s} {rel}")
    ap = apex.get(motif, [])
    if ap:
        print(f"   APEX PRESENT (parametric over the law): " + ", ".join(n for n,_ in ap[:4]))
        print(f"   → convergence-check: do the {len(inst)} instances route through it?")
    else:
        print(f"   ⚠ NO PARAMETRIC APEX — apex-candidate (cluster-means-find-apex).")
    print()
