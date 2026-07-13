#!/usr/bin/env python3
"""synth_pyrig.py — ⟡pyrig-synth / -graph / -UP: Agda-core → python (the mirror of
synth_agda_prototype). Read the TYPECHECKED core `PyAstRig.agdai` through the SHARED SPPF
term-algebra interner (jea_agdai → the same Intern jea_pyalg uses for pyast), reconstruct the
CATEGORICAL PRESENTATION from the definition graph, and EMIT runnable python. Closes the loop:

    PyAstRig.agdai  →  definition graph  →  initial F-algebra + catamorphism  →  python.

⟡pyrig-synth-UP — NOT local heuristics over single defs, but a semantic reconstruction:
  * CALL GRAPH        — each def's genuine CALLS = the qualified names applied in its clause
                        BODIES (not "mentions"; not the type signature). act CALLS {mapSPPF, apply}.
  * POLYNOMIAL FUNCTOR — a self-recursive reconstructing def is a CATAMORPHISM; from its clauses
                        recover F: per constructor, its ARITY and its RECURSIVE POSITIONS (a field
                        holding a self-call = an X; a non-recursive field = a generator A). So the
                        SPPF data type is recovered AS the initial F-algebra μF, `mapSPPF` as fmap.
  * CATAMORPHISM       — the eliminator into any F-algebra: emitted GENERIC over an algebra dict
                        {constructor ↦ operation}, so the ⊗-is-× / ⊕-is-+ assignment is the CALLER's
                        (the rig structure), never a Unicode heuristic here. (Removes the old `_role`.)
  * COMPOSITION        — a non-recursive, non-proof def whose call set includes a fold (act = fmap∘apply).
  * PROOF              — skipped structurally: references the identity type `_≡_` / its congruences.

The only thing NOT recovered locally: which of the two binary products is × vs + — that is a rig fact
living in SPPF.inside/OrientationRig, not in PyAstRig; the functor sees two symmetric X²-summands and
leaves their algebra to the caller. Honest boundary, and it is INFORMATION (the functor cannot tell them
apart; the semiring structure does).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_agdai as A
import jea_pyalg as P

DEFAULT_AGDAI = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "agda", "_build", "2.8.0", "agda", "Substrate", "WitnessTower", "Wedge", "PyAstRig.agdai")


# ── DISCOVER: intern the .agdai into the shared SPPF term algebra ─────────────────────
def discover(agdai_path):
    I = P.Intern()
    return I, A.core_intern_agdai(agdai_path, I)


def _module_agdai(main_agdai, def_qname):
    # the .agdai holding a qualified def, from its module path (drop the def name)
    marker = "/agda/Substrate/"
    if marker not in main_agdai:
        return None
    mod = ".".join(def_qname.split(".")[:-1])
    p = main_agdai.split(marker)[0] + "/agda/" + mod.replace(".", "/") + ".agdai"
    return p if os.path.exists(p) else None


# ── graph helpers over the interned Agda core ────────────────────────────────────────
def _op(I, i):  return I.nodes[i].op or ""
def _ch(I, i):  return I.nodes[i].children
def _is_qname(op): return bool(op) and "." in op
def _clauses(I, root): return [c for c in _ch(I, root) if _op(I, c) == "Clause"]
def _pat_body(I, clause):
    ch = _ch(I, clause)                       # Clause = [ …implicits…, PATTERN, BODY ]
    return (ch[-2], ch[-1]) if len(ch) >= 2 else (None, None)


def _subtree_has(I, root, qname):
    st, seen = [root], set()
    while st:
        i = st.pop()
        if i in seen:
            continue
        seen.add(i)
        if _op(I, i) == qname:
            return True
        st.extend(_ch(I, i))
    return False


def _subtree_qnames(I, root):
    st, seen, out = [root], set(), set()
    while st:
        i = st.pop()
        if i in seen:
            continue
        seen.add(i)
        if _is_qname(_op(I, i)):
            out.add(_op(I, i))
        st.extend(_ch(I, i))
    return out


def _is_proof(I, root):
    return any(q.endswith("._≡_") or q.endswith("._≡_.refl") or q.endswith(".cong₂")
               or q.endswith(".cong") or "≡" in q for q in _subtree_qnames(I, root))


# ── RECONSTRUCT the presentation from the definition graph (⟡pyrig-synth-UP) ─────────
def reconstruct(I, res, agdai):
    units = dict(res["units"])                          # full-qname -> root
    short = {n: n.split(".")[-1] for n in units}

    # 1. CALL GRAPH: each def -> the qnames it APPLIES in its clause bodies (calls, not mentions)
    calls = {}
    for name, root in units.items():
        cs = set()
        if _op(I, root) == "Defn":
            for cl in _clauses(I, root):
                _, body = _pat_body(I, cl)
                if body is not None:
                    cs |= _subtree_qnames(I, body)
        calls[name] = cs

    # 2. FOLDS + the POLYNOMIAL FUNCTOR: a self-recursive reconstructing def is a catamorphism;
    #    recover F = {ctor: (arity, recursive-positions)} from its clauses.
    folds, functor = [], {}
    for name, root in units.items():
        if _op(I, root) != "Defn" or name not in calls[name]:      # must be self-recursive
            continue
        ctor_cases, reconstructs, local = 0, False, {}
        for cl in _clauses(I, root):
            pat, body = _pat_body(I, cl)
            if pat is None or not _is_qname(_op(I, pat)):
                continue
            ph, arity = _op(I, pat), len(_ch(I, pat))
            ctor_cases += 1
            if _op(I, body) == ph:                                 # body rebuilds the constructor
                reconstructs = True
                bch = _ch(I, body)
                recpos = tuple(k for k in range(min(arity, len(bch)))
                               if _subtree_has(I, bch[k], name))   # a field carrying a self-call = X
                local[ph.split(".")[-1]] = (arity, recpos)
            else:
                local.setdefault(ph.split(".")[-1], (arity, ()))
        if ctor_cases >= 2 and reconstructs:
            folds.append(short[name])
            functor.update(local)
    fold_full = {n for n in units if short[n] in folds}

    # 3. COMPOSITIONS + EVALUATORS: non-recursive, non-proof defs. An EVALUATOR's carrier is a rig
    #    (Semiring in its signature); a COMPOSITION calls a fold in its body (act = fmap ∘ apply).
    comps, evals = [], []
    for name, root in units.items():
        if short[name] in folds or _op(I, root) != "Defn":
            continue
        if name in calls[name] or _is_proof(I, root):
            continue
        if _subtree_has(I, root, "Substrate.Algebra.Semiring.Semiring"):
            evals.append(short[name])
        elif any(fq in calls[name] for fq in fold_full):
            comps.append(short[name])

    # 3b. ORBIT COORDINATES: a def that CALLS a composition (one level above act, which calls a
    #     fold) — a further application of the group action to a residue (pyRecon = act ∘ decode).
    comp_full = {n for n in units if short[n] in comps}
    orbits = []
    for name, root in units.items():
        s = short[name]
        if s in folds or s in comps or s in evals or _op(I, root) != "Defn":
            continue
        if name in calls[name] or _is_proof(I, root):
            continue
        if any(cq in calls[name] for cq in comp_full):
            orbits.append(s)

    # 4. RECOVER the ×/+ ROLES — the point of the rig. Follow an evaluator's call into the module
    #    that defines the SPPF fold (inside), and read WHICH monoid each constructor's clause uses:
    #    Semiring.*-monoid ⇒ × (multiplicative), Semiring.+-monoid ⇒ + (additive). NOT a symbol guess.
    roles = {}
    ext = set()
    for name in units:
        if short[name] in evals:
            ext |= {q for q in calls[name] if q not in units}       # external calls of the evaluator
    ctor_names = set(functor)
    for q in ext:
        p = _module_agdai(agdai, q)
        if not p:
            continue
        I2 = P.Intern()
        r2 = A.core_intern_agdai(p, I2)
        for n2, root2 in dict(r2["units"]).items():
            if _op(I2, root2) != "Defn":
                continue
            got = {}
            for cl in _clauses(I2, root2):
                pat, body = _pat_body(I2, cl)
                if pat is None or not _is_qname(_op(I2, pat)):
                    continue
                cs = _op(I2, pat).split(".")[-1]
                if cs not in ctor_names:
                    continue
                bq = _subtree_qnames(I2, body)
                if any(x.endswith(".*-monoid") for x in bq):
                    got[cs] = "mul"
                elif any(x.endswith(".+-monoid") for x in bq):
                    got[cs] = "add"
            if len(got) >= 2:                                       # a genuine rig-fold assignment
                roles = got
                break
        if roles:
            break
    return functor, folds, comps, evals, roles, orbits


# ── EMIT: initial F-algebra + fmap + catamorphism ────────────────────────────────────
def _pyname(c):
    m = {"gen": "gen", "one": "one", "_⊗_": "otimes", "_⊕_": "oplus"}
    if c in m:
        return m[c]
    return ("".join(ch if ch.isalnum() else "_" for ch in c).strip("_")) or "ctor"


def _summand(ctor, arity, recpos):
    x, a = len(recpos), arity - len(recpos)
    parts = ([f"X^{x}" if x > 1 else "X"] if x else []) + ([f"A^{a}" if a > 1 else "A"] if a else [])
    return f"{'·'.join(parts) or '1'} ({ctor})"


_RIGSYM = {"mul": "×", "add": "+"}


def emit(agdai_path, functor, folds, comps, evals, roles, orbits):
    order = sorted(functor.items(), key=lambda kv: (kv[1][0], kv[0]))     # by (arity, name)
    def _tag(c, ar):
        return f" [{_RIGSYM[roles[c]]}]" if c in roles and ar >= 1 else ""
    F = " + ".join(_summand(c, ar, rp) + _tag(c, ar) for c, (ar, rp) in order)
    L = []
    w = L.append
    w(f'"""GENERATED by synth_pyrig.py from {os.path.relpath(agdai_path)}.')
    w("The rig category recovered from the definition graph as an initial F-algebra + catamorphism.")
    w(f"  polynomial functor  F(X) = {F}")
    w(f"  rig roles (recovered from inside's clauses: *-monoid⇒×, +-monoid⇒+): {roles}")
    w(f"  fold(s)/fmap        : {folds}")
    w(f"  composition(s)      : {comps}")
    w(f"  evaluator(s) (cata) : {evals}")
    w('"""')
    w("from dataclasses import dataclass")
    w("")
    w("# --- μF : the initial F-algebra (one class per constructor; arity from the clause patterns) ---")
    w("class SPPF: pass")
    for c, (ar, _rp) in order:
        py = _pyname(c)
        if ar == 0:
            w(f"class {py}(SPPF):")
            w(f"    def __eq__(s, o): return isinstance(o, {py})")
            w(f"    def __hash__(s): return hash('{py}')")
        else:
            w("@dataclass(frozen=True)")
            w(f"class {py}(SPPF):")
            for k in range(ar):
                w(f"    f{k}: object")
    w("")
    if folds:
        w(f"# --- {folds[0]} = fmap : the functor's action on A (relabel A-fields, recurse at X-positions) ---")
        w("def mapSPPF(f, t):")
        for c, (ar, rp) in order:
            py = _pyname(c)
            if ar == 0:
                w(f"    if isinstance(t, {py}): return t")
            else:
                args = ", ".join((f"mapSPPF(f, t.f{k})" if k in rp else f"f(t.f{k})") for k in range(ar))
                w(f"    if isinstance(t, {py}): return {py}({args})")
        w("    raise TypeError(t)")
        w("")
    if comps:
        w(f"# --- {comps[0]} : the group action = fmap ∘ apply (σ acts on generator positions) ---")
        w("def act(sigma, t):")
        w("    return mapSPPF(lambda i: sigma[i], t)")
        w("")
    if orbits:
        _oname = "pyRecon" if "pyRecon" in orbits else orbits[0]
        w(f"# --- {_oname} : the orbit COORDINATE — a point = an orbit representative reconstructed")
        w("#     with a residue (the group element; in Agda a LehmerPath, decode'd to a permutation).")
        w("#     `a = recon(rep, residue)`. NB the FORGET direction (normalize: point → canonical")
        w("#     orbit-rep = the interning key) is NOT modelled in PyAstRig — that is ⟡pyrig-normalizer,")
        w("#     so this extrudes the coordinate + torsor, NOT a running orbit-intern.")
        w("def pyRecon(rep, residue):")
        w("    return act(residue, rep)")
        w("")
    if evals:
        w(f"# --- cata : the UNIQUE F-algebra morphism out of μF (`alg` = constructor ↦ operation) ---")
        w("def cata(alg, t):")
        for c, (ar, rp) in order:
            py = _pyname(c)
            if ar == 0:
                w(f"    if isinstance(t, {py}): return alg['{py}']")
            else:
                args = ", ".join((f"cata(alg, t.f{k})" if k in rp else f"t.f{k}") for k in range(ar))
                w(f"    if isinstance(t, {py}): return alg['{py}']({args})")
        w("    raise TypeError(t)")
        w("")
        # the semiring fold: the F-algebra is BUILT from the recovered ×/+ roles (not a symbol guess).
        w(f"# --- {evals[0]} : the semiring fold. ×/+ RECOVERED from inside's clauses: {roles} ---")
        w("def pyEval(semiring, val, t):")
        w("    # semiring = {'mul','add','one'}; roles recovered from the SPPF fold, not guessed.")
        items = []
        for c, (ar, rp) in order:
            py = _pyname(c)
            if ar == 0:                              # the multiplicative unit (rig has no zero)
                items.append(f"'{py}': semiring['one']")
            elif ar == 1:                            # the generator: valued by `val`
                items.append(f"'{py}': val")
            else:                                    # a binary product: its RECOVERED rig operation
                items.append(f"'{py}': semiring['{roles.get(c, 'mul')}']")
        w("    return cata({" + ", ".join(items) + "}, t)")
        w("")
    return "\n".join(L) + "\n"


def emit_orbit_normalizer(agdai_main):
    # ⟡pyrig-synth-normalize: if the sibling normalizer module is present, extrude `normalize`
    # (the orbit interning KEY) so orbit-interning RUNS: intern(normalize(t)) interns orbits.
    norm = agdai_main[:-len(".agdai")] + "Normalize.agdai"
    if not os.path.exists(norm):
        return ""
    I, res = discover(norm)
    units = dict(res["units"])

    def bodycalls(root):
        cs = set()
        for cl in _clauses(I, root):
            _, b = _pat_body(I, cl)
            if b is not None:
                cs |= _subtree_qnames(I, b)
        return cs

    # the LEAF-FOLD (positions): a self-recursive SPPF-fold whose clause bodies build a List.
    has_leaf = any(_op(I, r) == "Defn" and (n in bodycalls(r))
                   and any(".List" in q for q in bodycalls(r))
                   for n, r in units.items())
    # normalize: a non-recursive def whose body CALLS mapSPPF (relabel by the rank of the positions).
    has_norm = any(_op(I, r) == "Defn" and (n not in bodycalls(r))
                   and any(q.endswith(".mapSPPF") for q in bodycalls(r))
                   for n, r in units.items())
    if not (has_leaf and has_norm):
        return ""
    L = []
    w = L.append
    w("")
    w("# === ORBIT INTERNING (⟡pyrig-synth-normalize) — extruded from PyAstRigNormalize.agdai ===")
    w("# positions: the leaf-fold, recognised as a cata into List (gen↦[g], one↦[], ⊗/⊕↦append).")
    w("def positions(t):")
    w("    return cata({'gen': (lambda g: [g]), 'one': [], "
      "'otimes': (lambda a, b: a + b), 'oplus': (lambda a, b: a + b)}, t)")
    w("# rank: first-appearance index (Agda: [] ↦ 0; x∷xs ↦ 0 if x≟y else suc(rank xs y)).")
    w("def rank(xs, y):")
    w("    return xs.index(y) if y in xs else len(xs)")
    w("# normalize: the orbit KEY = mapSPPF (rank (positions t)) t. PROVEN orbit-invariant in Agda")
    w("# (normalize-orbit-inv: normalize(act σ t) == normalize(t)), so intern(normalize(t)) interns ORBITS.")
    w("def normalize(t):")
    w("    ps = positions(t)")
    w("    return mapSPPF(lambda i: rank(ps, i), t)")
    w("")
    return "\n".join(L) + "\n"


def demo(src):
    # RUN the reconstructed rig category; CHECK exactly the Agda-proved laws (act-id, act-∘, torsor)
    # + the equivariance mapSPPF-functoriality gives. `cata` takes the F-ALGEBRA as a parameter, so
    # the semiring (× for otimes, + for oplus) is supplied HERE, not baked into the synthesizer.
    ns = {}
    exec(compile(src, "<pyrig_synth>", "exec"), ns)
    gen, oplus, otimes = ns["gen"], ns["oplus"], ns["otimes"]
    act, pyEval = ns["act"], ns["pyEval"]
    spine = oplus(gen(0), oplus(gen(1), gen(2)))
    idp = {0: 0, 1: 1, 2: 2}
    s = {0: 1, 1: 2, 2: 0}
    t = {0: 1, 1: 0, 2: 2}
    st = {i: s[t[i]] for i in range(3)}
    val = {0: 2, 1: 3, 2: 5}
    N = {"add": (lambda a, b: a + b), "mul": (lambda a, b: a * b), "one": 1}   # the ℕ semiring
    print("demo: reconstructed rig category runs — the Agda-proved laws, in python:")
    print(f"  act-id    act(id,x) == x                        -> {act(idp, spine) == spine}")
    print(f"  act-∘     act(s∘t,x) == act(s, act(t,x))        -> {act(st, spine) == act(s, act(t, spine))}")
    lhs = pyEval(N, (lambda i: val[i]), act(s, spine))
    rhs = pyEval(N, (lambda i: val[s[i]]), spine)                # valuation v∘s
    print(f"  equivar   pyEval(v, act s x) == pyEval(v∘s, x)  -> {lhs == rhs}   ({lhs}=={rhs})")
    print(f"  torsor    s≠t ⇒ act s spine ≠ act t spine       -> {act(s, spine) != act(t, spine)}")
    # the ×/+ roles are RECOVERED, so ⊗ folds to product, ⊕ to sum — check on a mixed term:
    mixed = otimes(gen(0), oplus(gen(1), gen(2)))               # 2 × (3 + 5) = 16
    print(f"  rig-roles ⊗↦× ⊕↦+ recovered: 2×(3+5) = {pyEval(N, (lambda i: val[i]), mixed)}  (==16)")
    if "pyRecon" in ns:
        pyRecon = ns["pyRecon"]
        print(f"  orbit-coord pyRecon(rep,id)==rep -> {pyRecon(spine, idp) == spine}; "
              f"distinct residues → distinct points -> {pyRecon(spine, s) != pyRecon(spine, t)}")
    if "normalize" in ns:
        normalize = ns["normalize"]
        moved = act(s, spine)                          # same orbit as spine (a position permutation)
        other = otimes(gen(0), gen(1))                 # a different structure ⇒ a different orbit
        print(f"  ORBIT-INTERN normalize(spine)==normalize(act s spine) -> "
              f"{normalize(spine) == normalize(moved)}  (proven: normalize-orbit-inv)")
        print(f"  distinct orbit → distinct key -> {normalize(spine) != normalize(other)}  "
              f"⇒ intern(normalize(t)) interns ORBITS, not points")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    agdai = args[0] if args and args[0] else DEFAULT_AGDAI
    out = args[1] if len(args) > 1 else None
    I, res = discover(agdai)
    functor, folds, comps, evals, roles, orbits = reconstruct(I, res, agdai)
    src = emit(agdai, functor, folds, comps, evals, roles, orbits)
    src += emit_orbit_normalizer(agdai)
    if out:
        with open(out, "w") as f:
            f.write(src)
        print(f"synth_pyrig: wrote {out}  (F={functor}, folds {folds}, comps {comps}, evals {evals}, "
              f"roles {roles}, orbits {orbits})")
    else:
        sys.stdout.write(src)
    if "--demo" in sys.argv:
        demo(src)


if __name__ == "__main__":
    main()
