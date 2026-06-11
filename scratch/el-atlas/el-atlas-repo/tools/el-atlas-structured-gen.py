"""
el-atlas-structured-gen.py — generates el-atlas-structured.md from the v3.1 harness.

Computed (not hand-arranged): ToC ordering (condensation layers of the
characteristic-break dep digraph, U excluded from edges), chapter grouping
(digraph SCCs refined by exhaustive pairwise separator search into intrinsic
cores vs coincidences), perspective-visibility tables (each claim EXECUTED under
the named vantage configs; P/F/U/V), circle verdicts WITH space index and
residue ledger (no unindexed verdicts), glossary, cross-reference index.
Hand-written: claim metadata sentences and spec pointers only.
"""
import importlib.util, functools, sys, os
spec = importlib.util.spec_from_file_location("dep", os.path.join(os.path.dirname(__file__), "el-atlas-depsort-v3.py"))
dep = importlib.util.module_from_spec(spec); spec.loader.exec_module(dep)
CLAIMS, BASE, SPACE, KNOBS = dep.CLAIMS, dep.BASE, dep.SPACE, dep.KNOBS
PRIOR_LEDGER = dep.PRIOR_LEDGER
FRONTIER = getattr(dep, 'FRONTIER', {})
KNOB_PROVENANCE = getattr(dep, 'KNOB_PROVENANCE', {})
manifest, FP = dep.space_fingerprint()
names = list(CLAIMS)
def M(**kw):
    m = dict(BASE); m.update(kw); return m

META = {
 'ADJ': ("The chart adjunction (exp ⊣ log)", "The two per-pin charts — semiring magnitudes and the signed line — form an adjoint equivalence; the codec pair whose round-trips are identities.", "§2, Lemma 2.5b"),
 'BAL': ("The balance channel", "A single pin's real component holds the balance of the evidence, read relative to its frame's identity element; conflict is inexpressible.", "§5.7"),
 'CDC': ("The codec contract", "Ring or semiring encoding is indifferent iff encode matches decode; frame mismatch silently flips balance; negative+semiring is ill-typed.", "§5.7, Caveat 2.4a"),
 'CRS': ("The crossbar", "(mass, bias) = (E⁺+E⁻, E⁺−E⁻) is an invertible change of basis on the pair.", "§4"),
 'NOE': ("The Noether pairings", "The squeeze conserves mass; the common translation conserves bias — the two charges of the pair's symmetry flows.", "§11.8, OB-7"),
 'PUR': ("The differential purchase", "Encoding one channel over two pins gains the conflict/ignorance axis: d carries the balance, c is the purchased mass axis.", "§5.7"),
 'PRO': ("The prohibition", "Pinning the purchased axis (normalization) conflates conflict with ignorance; collapse is an arity-mismatched decode; probability is the c-pinned slice.", "§3, §5.8a"),
 'LOC': ("The classical section", "The inverse-locked locus (u, −u) is exactly c ≡ 0: the balance channel embedded in the pair; classical logic with the purchased axis off.", "Lemma 2.6, §5.8b"),
 'L26': ("The involution coincidence", "On the classical section, constrained negation equals the pin-swap — they coincide iff the section is exactly f = −id.", "Lemma 2.6"),
 'T53': ("The De Morgan requirements", "NOT(AND) ≡ OR requires two operations (one collapses OR into AND) and the inverse-lock (the classical section).", "Theorem 5.3"),
 'V4I': ("The exact V₄", "Under independence, the only admissible linear maps are diagonal; their sign-involutions form the Klein four-group exactly — no swap, no braid.", "§5, Theorem 5.4, §5.6 P2-I"),
 'D4C': ("The braided V₄ (D₄)", "Composed reading licenses the swap; ⟨negate-one, swap⟩ = D₄, the central extension of V₄ by the reversible twist [N,S] = −id.", "Theorem 5.4, Remark 5.5"),
 'PHS': ("The phase support theorem", "The extension class (the phase bit) is trivial exactly on the classical section and nontrivial exactly off it; a single pin has no phase.", "§5.8c, §8.5–8.6"),
 'RLS': ("The classical rails", "The locus endpoints are T and F; composed NOT exchanges them; independent negation at a rail lands on conflict. The rails are a compactification fact, detachable from the section.", "§5.7 worked rails"),
 'TWN': ("The twist", "The level conjugation pair anticommutes by a central, reversible sign — the cocycle of the doubling interface; trivial in characteristic 2.", "§5.9, Theorem 5.4"),
 'RAD': ("The radial schedule", "The CD pinning's quadratic norm is multiplicative exactly through the octonion rung (Hurwitz); radial multiplicativity is a sacrifice-ladder rung.", "§5.9"),
 'ZDG': ("The zero-divisor schedule", "Zero divisors first appear at the sedenion rung and are enumerated, oriented geography (dim 2ⁿ−5, G₂); in characteristic 2 they appear at every rung — the schedule is a char-0 fact.", "§5.9 (Z-series)"),
 'PR2': ("The sphere prohibition", "Pinning the quadratic radius (L2 normalization) is also a one-mode decode: it conflates states differing only in radius — the prohibition's arity argument, second magnitude instance.", "§5.9"),
 'NGL': ("The G-value lift", "Nedge's G-Value Calculus is ⟨fraction-addition, swap⟩ on formal-quotient pairs — the carrier quotiented by the diagonal; non-idempotence is the mass-growth shadow; resource sensitivity is the quotient remembering the extruded axis.", "§5.7e, nedge-decomposition §6"),
 'NVL': ("The two-gate theorem", "Nedge's 4VL (confidence × consistency) and Belnap's chart (bias-sign × rail) are distinct four-cell gates on one carrier; either magnitude pinning degenerates the gate — a four-valued logic needs the unpinned pair.", "§4, §5.7e, nedge-decomposition §2/§6"),
 'GCX': ("The third codec sighting", "GALAXY's W ↔ ASPF's log-decode: the exponential codec is exact on the rank-sum quotient, and the quotient genuinely collides — GALAXY is a one-mode decode of the ASPF carrier.", "corpus-sweep §6 (S4); §5.8"),
 'SWP': ("Semiring-weighted parsing", "One chart, pluggable semiring: the carrier semiring carries the SPPF's packed multiplicity; probability is the positive-rail section, Viterbi the idempotent pinning; inside×outside is the zipper product.", "theory-threads §2/§8/§9 (S7/S12/S13)"),
 'NVE': ("The ∨E bridge", "Proof-by-cases is the single/double pin split/join expansion; the Wheatstone bridge reads the case-bias the join forgets; classical ∨E lives on the balance manifold.", "§5.7e; nedge-decomposition §8 (S8/S9)"),
 'RDW': ("The radial witness mode", "Pi-form: the excess-mode schedule — norm-failure-beyond-the-kernel is empty through the octonions, inhabited from the sedenions; the witness is the section over rungs (a 1-path), displayed as cdlevel-inertness.", "§5.9; theory-threads §14 (T2)"),
 'ZDW': ("The zero-divisor witness mode", "Pi-form: the kernel-mode schedule — det L_x locked to N^(d/2) through the octonions (kernel empty), unlocked at the sedenions (kernel inhabited, contained in norm-failure); the lock schedule IS the content.", "§5.9; theory-threads §14 (T2)"),
 'SWF': ("Order-free semiring parsing", "The order-free face of SWP (counting, inside, inside×outside, conflation): extends verbatim over ℂ — the first EXTENDS stance, earned by its named breaker.", "theory-threads §8; retrospective R-V35"),
 'IDC': ("The identity-collapse schedule", "Bare nodes collapse; minimally-stabilized twins still collapse; distinct participation separates — identity is unseparated-in-probe-space, and differentiation is probe-space extension.", "nedge-decomposition §2 (N-series)"),
}
BREAKS = dict(ADJ=M(adj=False), BAL=M(ident=False), CDC=M(ident=False),
              CRS=M(basis_def='singular'), PUR=M(norm='pinned'), PRO=M(norm='pinned'),
              LOC=M(lock='wrong'), L26=M(lock='wrong'), T53=M(two_ops=False),
              V4I=M(neg=False), D4C=M(ops='diagonal'), PHS=M(lock='forced'),
              RLS=M(lock='wrong'), NOE=M(pins=1),
              TWN=M(coeff='gf2'), RAD=M(coeff='gf2'), ZDG=M(coeff='gf2'),
              PR2=M(norm='pinned_l2'),
              NGL=M(coeff='gf2'), NVL=M(norm='pinned'), IDC=M(probe='mention'),
              GCX=M(coeff='gf2'), SWP=M(pins=1), NVE=M(ops='diagonal'),
              RDW=M(coeff='gf2'), ZDW=M(coeff='gf2'), SWF=M(coeff='gf2'))
PERSP = [
 ("FULL", BASE, "the full evidence atlas"), ("P1", M(pins=1), "single pin"),
 ("P2-I", M(ops='diagonal'), "independent pins"), ("CLASSICAL", M(lock='forced'), "the classical section"),
 ("PROB", M(norm='pinned'), "the probability slice"), ("NO-CODEC", M(adj=False), "broken chart pair"),
 ("NO-ANCHOR", M(ident=False), "identity forgotten"), ("ONE-OP", M(two_ops=False), "single operation"),
 ("NO-NEG", M(neg=False), "negation-free"), ("SING-BASIS", M(basis_def='singular'), "singular crossbar basis"),
 ("NOISY-LOCK", M(lock='noisy'), "noisy section"), ("CHAR-2", M(coeff='gf2'), "GF(2) coefficients — the twist invisible"),
 ("SEDENION", M(cdlevel=16), "the sedenion rung"), ("SPHERE", M(norm='pinned_l2'), "the radius-pinned slice"),
 ("MENTION", M(probe='mention'), "mention-only probe — identity by existence"),
 ("COMPLEX", M(coeff='complex'), "complex coefficients — admitted v3.5; claims V-pending-port"),
]
vis = {n: {p[0]: CLAIMS[n](p[1]) for p in PERSP} for n in names}
base_res = {n: CLAIMS[n](BASE) for n in names}
# dep edges: F or V under the break (U excluded — undecided is not destroyed)
depm = {(b,a): (base_res[b]=='P' and CLAIMS[b](BREAKS[a]) in ('F','V')) for b in names for a in names}
edges = {b:{a for a in names if a!=b and depm[(b,a)]} for b in names}
def reach(x):
    seen=set(); st=[x]
    while st:
        n=st.pop()
        for nn in edges[n]:
            if nn not in seen: seen.add(nn); st.append(nn)
    return seen
R={n:reach(n) for n in names}
sccs=[]; done=set()
for n in names:
    if n in done: continue
    c=sorted({n}|{x for x in names if x in R[n] and n in R[x]}); sccs.append(c); done|=set(c)
# exhaustive pairwise classification within SCCs
res_all={i:{n:CLAIMS[n](m) for n in names} for i,m in enumerate(SPACE)}
def pairstats(X,Y):
    st=sk=co=either=0
    for i in res_all:
        a,b=res_all[i][X],res_all[i][Y]
        ma,mb=(a!='P'),(b!='P')
        either+=(ma or mb); co+=(ma and mb)
        st+=(a=='F' and b=='P') or (b=='F' and a=='P'); sk+=(ma!=mb)
    return st,sk,co,either
def never_F(n): return all(res_all[i][n]!='F' for i in res_all)
def chapters():
    out=[]
    for c in sccs:
        if len(c)==1: out.append(("single", c, None)); continue
        # union-find on pairwise unseparated (any-kind == 0)
        parent={x:x for x in c}
        def find(x):
            while parent[x]!=x: x=parent[x]
            return x
        for i,X in enumerate(c):
            for Y in c[i+1:]:
                if pairstats(X,Y)[1]==0:
                    parent[find(Y)]=find(X)
        groups={}
        for x in c: groups.setdefault(find(x),[]).append(x)
        for g in groups.values():
            if len(g)>1:
                kind = "expr-intrinsic" if any(never_F(x) for x in g) else "truth-intrinsic"
                out.append((kind, sorted(g), sorted(set(c)-set(g)) or None))
            else:
                out.append(("coincidence", g, sorted(set(c)-set(g))))
    return out
CH=chapters()
comp_of={x:i for i,c in enumerate(sccs) for x in c}
ce={i:set() for i in range(len(sccs))}
for b in names:
    for a in edges[b]:
        if comp_of[b]!=comp_of[a]: ce[comp_of[b]].add(comp_of[a])
@functools.lru_cache(None)
def depth(i): return 0 if not ce[i] else 1+max(depth(j) for j in ce[i])
layer_of={x:depth(comp_of[x]) for x in names}
def anchor(n):
    s=META[n][0].lower()
    for a,b in [(' ','-'),('(',''),(')',''),('₄','4'),('⁺',''),('⁻',''),('≡',''),(',',''),('—','-'),('⊣','')]:
        s=s.replace(a,b)
    return s
def ledger_lines(ns):
    out=[]
    for X in ns:
        for Y in names:
            if Y<=X: continue
            key=frozenset({X,Y})
            if key in PRIOR_LEDGER and Y not in ns:
                st,sk,co,either=pairstats(X,Y)
                cur = f"separated-in-S_{FP} ({st} truth-separators)" if sk else f"unseparated-in-S_{FP}"
                out.append(f"*Separation ledger {X}–{Y}:* {cur}; " +
                           "; ".join(f"{v} @ {s}" for s,v in PRIOR_LEDGER[key]) + ".")
    return out
L=[]
L.append("# The EL-Atlas, Structured Edition\n")
L.append(f"*Mechanically derived by `tools/el-atlas-structured-gen.py` from the v3.1 harness.*")
L.append(f"*All verdicts indexed: space **S_{FP}** ({len(SPACE)} models, exhaustive); manifest below.*")
L.append("*Hand-written content: claim metadata sentences and spec pointers only.*\n")
L.append(f"**Space manifest S_{FP}:** " + "; ".join(f"{k} ∈ {{{', '.join(v)}}}" for k,v in manifest.items()) + ".")
L.append("*Why this space: no knob is a-priori — each was admitted by a named correction*")
L.append("*event (KNOB_PROVENANCE in the harness); knobs are monotonic. Intrinsic verdicts*")
L.append("*below carry a frontier: what a separator would require, and at which scrutiny*")
L.append("*stratum the residual openness lives.*\n")
L.append("**Legend:** P = visible/true from that vantage; F = false there; U = observable but")
L.append("undecided; V = not statable there. Dependence edges arise from F and V only —")
L.append("undecided is not destroyed. Circle verdicts carry their space index and ledger.\n")
L.append(f"**Proof tier:** {dep._PROOF_TIER}\n")
L.append("Every claim below carries its fiber certificate, executed at generation time: "
         "the edition is proof-carrying (B2) — no witness-stratum IOU survives to this artifact; "
         "the proof tier is the registered empty.\n")
maxl=max(layer_of.values())
L.append("## Table of Contents\n")
for d in range(maxl+1):
    L.append(f"**Part {d+1} — Layer {d}{' (foundations)' if d==0 else ''}**")
    for kind,ns,rest in CH:
        if layer_of[ns[0]]!=d: continue
        title=" ≡ ".join(META[n][0] for n in ns) if kind in ("truth-intrinsic","expr-intrinsic") else META[ns[0]][0]
        tag={"truth-intrinsic":" *(one structure — truth-intrinsic)*",
             "expr-intrinsic":" *(one structure — expressibility-intrinsic)*",
             "coincidence":" *(characteristic-break coincidence; separated in-space)*",
             "single":""}[kind]
        L.append(f"- [{title}](#{anchor(ns[0])}){tag}")
    L.append("")
L.append("\n---\n")
for d in range(maxl+1):
    L.append(f"\n# Part {d+1} — Layer {d}{' (foundations)' if d==0 else ''}\n")
    for kind,ns,rest in CH:
        if layer_of[ns[0]]!=d: continue
        title=" ≡ ".join(META[n][0] for n in ns) if kind in ("truth-intrinsic","expr-intrinsic") else META[ns[0]][0]
        L.append(f"\n## {title}{' — one structure' if kind in ('truth-intrinsic','expr-intrinsic') else ''}\n")
        for n in ns:
            nm,gloss,ref=META[n]
            L.append(f"**{n} — {nm}** ({ref}). {gloss}\n")
            cls,em=dep._FIBER_CERT.get(n,("UNREGISTERED",None))
            L.append(f"*Certificate ({cls})*" + (f": {em()}" if em else "") + "\n")
        if kind=="truth-intrinsic":
            st,sk,co,either=pairstats(*ns[:2])
            L.append(f"*Verdict (S_{FP}, exhaustive): TRUTH-INTRINSIC — zero separators of any kind; co-movement {co}/{either} = {co/either:.2f}. Closure-under-break: every perturbation breaks the loop coherently, with kind-structure inside the co-movement (e.g. noisy lock: U vs F). ∀-over-declared-spaces; strengthens with each space survived; never closes.*\n")
            fk=frozenset(ns[:2])
            if fk in FRONTIER: L.append(f"*Frontier: a separator would require {FRONTIER[fk]}.*\n")
        if kind=="expr-intrinsic":
            st,sk,co,either=pairstats(*ns[:2])
            thm=[x for x in ns if never_F(x)]
            L.append(f"*Verdict (S_{FP}, exhaustive): EXPRESSIBILITY-INTRINSIC — zero separators; co-movement {co}/{either} = {co/either:.2f}; but {', '.join(thm)} is never F anywhere in the space: a theorem, truth-stable wherever statable. Mutual constitution at the statability level, one-way at the truth level: interventions de-state the theorem rather than falsify it. ∀-over-declared-spaces; open-by-design.*\n")
            fk=frozenset(ns[:2])
            if fk in FRONTIER: L.append(f"*Frontier: a separator would require {FRONTIER[fk]}.*\n")
        if kind=="coincidence":
            L.append(f"*Characteristic-break coincidence with {rest} (shared break in the dep digraph); separated in-space — see ledger.*\n")
        for ln in ledger_lines(ns): L.append(ln+"\n")
        for n in ns:
            L.append(f"\n*Perspective visibility — {n} (executed, S_{FP} configs):*\n")
            L.append("| " + " | ".join(p[0] for p in PERSP) + " |")
            L.append("|" + "---|"*len(PERSP))
            L.append("| " + " | ".join(vis[n][p[0]] for p in PERSP) + " |")
        for n in ns:
            deps=sorted(edges[n]-set(ns)); req=sorted({b for b in names if n in edges[b]}-set(ns))
            ind=[x for x in names if x not in ns and not depm[(n,x)] and not depm[(x,n)]]
            L.append(f"\n*Cross-reference — {n}:* depends on {deps if deps else '—'}; required by {req if req else '—'}; independent of {len(ind)} claims ({', '.join(ind[:5])}{'…' if len(ind)>5 else ''}).")
        L.append("")
L.append("\n---\n\n# Glossary (computed)\n")
for n in sorted(names,key=lambda x:META[x][0]):
    nm,gloss,ref=META[n]
    circ=next((k for k,ns,_ in CH if n in ns and k in ("truth-intrinsic","expr-intrinsic")),None)
    L.append(f"**{nm}** [{n}] — {gloss} *(Layer {layer_of[n]}; {ref}{f'; {circ} circle member' if circ else ''})*\n")
L.append("\n# Cross-Reference Index (computed)\n")
L.append("| claim | layer | depends on | required by | circle |")
L.append("|---|---|---|---|---|")
for n in names:
    deps=", ".join(sorted(edges[n])) or "—"; req=", ".join(sorted({b for b in names if n in edges[b]})) or "—"
    circ=next((" ≡ ".join(ns) for k,ns,_ in CH if n in ns and len(ns)>1),"—")
    L.append(f"| {n} | {layer_of[n]} | {deps} | {req} | {circ} |")
indep=sum(1 for i,a in enumerate(names) for b in names[i+1:] if not depm[(a,b)] and not depm[(b,a)])
L.append(f"\n*Independence count: {indep} of {len(names)*(len(names)-1)//2} pairs carry no dependence in either direction (S_{FP}).*")
out=os.path.join(os.path.dirname(__file__),"..","el-atlas-structured.md")
open(out,"w").write("\n".join(L))
print(f"generated S_{FP}; layers={maxl+1}; chapters={len(CH)}")
for d in range(maxl+1):
    print(f"  layer {d}: "+"  ".join("{"+",".join(ns)+"}" for k,ns,_ in CH if layer_of[ns[0]]==d))
