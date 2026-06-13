#!/usr/bin/env python3
"""law_motif_apex.py — surface apex-candidates by clustering FUNCTION SIGNATURES on
relational LAW-MOTIFS, the index neither agda_similarity (token-cosine) nor type_sppf
(data/record skeletons) builds.

WHY THE OTHER TOOLS MISS IT
  agda_similarity is multi-scale token cosine: instances of one categorical law
  (eval/reify, ℚ reduce, wedge recon, GenericHodgeStar star/star-inv, CRT) live in
  disjoint vocabularies → near-zero overlap → never cluster. The shared content is a
  ~3-token TYPE motif (`f (g x) ≡ x`) drowned in domain tokens and split across a TRIPLE
  (F, s, the law-proof). type_sppf reads only data/record skeletons, never function
  signatures. The proof TERMS differ wildly (refl / sym (wedge-eq w) / a field); only
  the TYPE is invariant. So the law is invisible to both.

THE DISCRIMINATOR (what makes this accurate)
  A law INSTANCE has CONCRETE F, s — named top-level defs (eval/reify, recon/divide).
  A law APEX has BOUND F, s — parameters — with the law itself as a HYPOTHESIS
  (split-Canonical : (F …)(s …) → ((y) → F (s y) ≡ y) → …). Parsing the telescope and
  asking "are F, s bound here or concrete?" separates instances from apexes and kills
  the false positives a flat regex produces.

OUTPUT  Per motif (retraction f(g x)≡x, involution f(f x)≡x, idempotent f(f x)≡f x,
  homomorphism f(x⊕y)≡f x⊗f y): the concrete instances, and whether a parametric apex
  exists. Apex present ⇒ convergence-check (how many instances are *built through* it).
  Apex absent + many instances ⇒ APEX-CANDIDATE (cluster-means-find-apex, mechanised).

Approximate (a focused paren-aware parser, not full Agda; misses infix/where-bound
laws) — a documented lower bound. Usage: law_motif_apex.py [--min N] [--show K]
"""
import os, re, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
MIN  = int(sys.argv[sys.argv.index("--min") + 1])  if "--min"  in sys.argv else 3
SHOW = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 24

OPEN, CLOSE = "({⦃", ")}⦄"
IDENT = re.compile(r"^[^\s()\[\]{}⦃⦄:;,]+$")

def strip(s):
    s = re.sub(r"\{-.*?-\}", " ", s, flags=re.S)
    return re.sub(r"--[^\n]*", "", s)

def depth_split(s, seps):
    """Split s on any separator in `seps` at bracket-depth 0. seps: list of strings."""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        if c in OPEN: depth += 1; cur += c; i += 1; continue
        if c in CLOSE: depth -= 1; cur += c; i += 1; continue
        if depth == 0:
            hit = next((sep for sep in seps if s.startswith(sep, i)), None)
            if hit:
                parts.append(cur); cur = ""; i += len(hit); continue
        cur += c; i += 1
    parts.append(cur)
    return parts

def unwrap(s):
    """Peel fully-enclosing parens: '(g x)' → 'g x'."""
    s = s.strip()
    while len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        depth = 0; ok = True
        for j, c in enumerate(s):
            if c in OPEN: depth += 1
            elif c in CLOSE:
                depth -= 1
                if depth == 0 and j != len(s) - 1: ok = False; break
        if ok: s = s[1:-1].strip()
        else: break
    return s

def spine(s):
    """Application spine: 'f (g x) y' → ('f', ['(g x)', 'y']). Left-assoc."""
    s = unwrap(s)
    parts = [p for p in depth_split(s, [" "]) if p.strip()]
    if not parts: return ("", [])
    return (parts[0].strip(), [p.strip() for p in parts[1:]])

def is_ident(s):
    return bool(IDENT.match(s.strip())) and s.strip() not in ("→", "≡", "∀", "λ")

def result_and_hyps(ty):
    """Split a type telescope on top-level → ; return (hypothesis-segments, result)."""
    segs = depth_split(ty, ["→", "->"])
    segs = [x.strip() for x in segs if x.strip()]
    return (segs[:-1], segs[-1]) if segs else ([], ty)

def binder_groups(ty):
    """Contents of each TOP-LEVEL (…)/{…} binder group. Agda juxtaposes binders
    `(F : A)(s : B)`, so these are NOT →-separated — extract them by bracket depth."""
    groups, depth, cur = [], 0, ""
    for c in ty:
        if c in OPEN:
            if depth == 0: cur = ""
            else: cur += c
            depth += 1
        elif c in CLOSE:
            depth -= 1
            if depth == 0: groups.append(cur)
            else: cur += c
        elif depth >= 1:
            cur += c
    return groups

def bound_names(ty):
    """Names bound by the telescope's binder groups: '(F : …)', '{a b : …}'."""
    names = set()
    for g in binder_groups(ty):
        if " : " in g:
            for n in g.split(" : ", 1)[0].replace("{", " ").replace("}", " ").split():
                if is_ident(n): names.add(n)
    return names

def eq_sides(seg):
    """If seg (a result type) is an equation, return (lhs, rhs) at top level."""
    parts = depth_split(seg, ["≡"])
    if len(parts) != 2: return None
    return (parts[0].strip(), parts[1].strip())

def classify(seg):
    """Match the equation `seg` against a law-motif. Returns (motif, F, s, x) or None."""
    eq = eq_sides(seg)
    if not eq: return None
    lhs, rhs = eq
    F, fargs = spine(lhs)
    rh, rargs = spine(rhs)
    if not is_ident(F) or not fargs: return None
    s, sargs = spine(fargs[-1])             # inner application = s (… x)
    if not is_ident(s) or not sargs:
        # homomorphism? f (x ⊕ y) ≡ (f x) ⊗ (f y)
        inner = unwrap(fargs[-1])
        if any(op in inner for op in ("⊕", "+", "·", "*", "∙")) and rargs:
            return ("homomorphism        f (x⊕y) ≡ f x ⊗ f y", F, F, inner)
        return None
    x = unwrap(sargs[-1])
    # retraction / section: f (g x) ≡ x      (rhs is the bare bound var x)
    if not rargs and rh == x:
        if F == s: return ("involution          f (f x) ≡ x", F, s, x)
        return ("retraction/section  f (g x) ≡ x", F, s, x)
    # idempotent: f (f x) ≡ f x
    if F == s and rh == F and rargs and unwrap(rargs[-1]) == x:
        return ("idempotent          f (f x) ≡ f x", F, s, x)
    return None

# ---- pass 1: collect every top-level signature + the global def-name set ----
sig_re = re.compile(r"^([A-Za-z_][^\s():{}⦃⦄]*)\s*:\s*(.+?)(?=^\S|\Z)", re.M | re.S)
field_re = re.compile(r"^\s+([A-Za-z_][^\s():{}⦃⦄]*)\s*:\s*(.+?)(?=^\s*[A-Za-z_]|\Z)", re.M | re.S)
sigs = []          # (name, file, type_flat)  — top-level defs AND record fields
defnames = set()   # all identifier names that name a def/field (the "concrete" set)
corpus_text = ""   # all stripped sources, for counting apex use-sites
for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p = os.path.join(dp, fn); rel = os.path.relpath(p, ROOT)
        txt = strip(open(p, encoding="utf-8").read())
        corpus_text += txt + "\n"
        # top-level signatures (col-0) AND record/where field signatures (indented) —
        # laws live in BOTH (e.g. GenericHodgeStar.retraction is a field). Concrete F,s
        # may be a field too, so fields populate `defnames` as well.
        for rx in (sig_re, field_re):
            for m in rx.finditer(txt):
                name, ty = m.group(1), re.sub(r"\s+", " ", m.group(2)).strip()
                defnames.add(name); sigs.append((name, rel, ty))

# token-boundary index for the convergence count (avoids substring bleed, e.g.
# 'sum' inside 'sum-F₂'); Agda idents survive this split intact.
tok_count = collections.Counter(re.split(r"[\s()\[\]{}⦃⦄:;,]+", corpus_text))

# ---- pass 2: classify each signature as INSTANCE (concrete F,s) or APEX (bound F,s) ----
instances = collections.defaultdict(list)   # motif -> [(name, file, F, s)]
apexes    = collections.defaultdict(list)    # motif -> [(name, file)]
for name, rel, ty in sigs:
    _, res = result_and_hyps(ty)
    bound = bound_names(ty)
    # APEX: some binder's TYPE is the law-motif, over BOUND F, s (parametric over the law).
    for g in binder_groups(ty):
        if " : " not in g: continue
        _, gres = result_and_hyps(g.split(" : ", 1)[1])
        c = classify(gres)
        if c and c[1] in bound and c[2] in bound:
            apexes[c[0]].append((name, rel)); break
    # INSTANCE: the RESULT is the law-motif, over CONCRETE (defined, not bound) F, s.
    c = classify(res)
    if c and c[1] not in bound and c[2] not in bound and c[1] in defnames and c[2] in defnames:
        instances[c[0]].append((name, rel, c[1], c[2]))

# ---- report ----
print("# law-motif apex scan — relational motifs over function signatures\n")
instances = {m: sorted(set(v)) for m, v in instances.items()}   # dedup (sig+field overlap)
apexes    = {m: sorted(set(v)) for m, v in apexes.items()}
for motif in sorted(set(instances) | set(apexes), key=lambda k: -len(instances.get(k, []))):
    inst = instances.get(motif, []); ap = apexes.get(motif, [])
    if len(inst) < MIN and not ap: continue
    print(f"## {motif}   — {len(inst)} concrete instances")
    for name, rel, F, s in sorted(inst)[:SHOW]:
        print(f"   {name:30s} {rel}   [{F} ∘ {s}]")
    if len(inst) > SHOW: print(f"   … +{len(inst) - SHOW} more")
    if ap:
        apex_names = sorted({n for n, _ in ap})
        # convergence: count corpus USE-sites of each apex (occurrences − its 1 def site).
        uses = sum(max(0, tok_count[an] - 1) for an in apex_names)  # token-exact, −1 for the def
        print(f"   ✔ APEX PRESENT (parametric over the law): {', '.join(apex_names[:4])}")
        print(f"   → convergence: ~{uses} apex use-site(s) vs {len(inst)} instances — "
              f"{len(inst) - uses} candidate(s) to route through it.")
    else:
        print(f"   ⚠ NO PARAMETRIC APEX — apex-candidate (cluster-means-find-apex).")
    print()
