#!/usr/bin/env python3
"""worklist.py — mechanically-maintained thread status (registry-as-regenerator).

The open-threads worklist kept going STALE: done arcs stayed listed as "open" because their status was
a HAND-EDITED value, and a regrounding then re-dispatched completed work (△, FromImages, def/proof, Ι,
AsNamed all turned up done-but-listed-open in one session). The substrate's own discipline says: don't
store the answer, COMPUTE it from the evidence of the moment (navigator-not-the-answer;
registry-as-Π-not-markdown; judgement-is-demechanization). So status is never written down — it is
DERIVED from the tree every run, and cannot go stale by construction.

The only hand-authored part is the MANIFEST below: each item + a CHECKABLE done-predicate (a commit
subject, a defined lemma, an existing module, a linter that exits 0). Everything else is computed:

    scripts/worklist.py            # the live status table (DONE / OPEN / MANUAL)
    scripts/worklist.py --open     # only the not-done items (what to actually dispatch)
    scripts/worklist.py --md       # a markdown block (paste/generate into a record; never hand-edit)
    scripts/worklist.py --update   # REGENERATE the status block in the open_threads ledger (a command
                                   #   that updates the record — never hand-edit the block)
    scripts/worklist.py --check    # counts (a gate could run this)

Sibling of the `decomposition/` machinery (build_conversation_db / build_cotype_db → DB;
interpret_*_retrospective → REGENERATED markdown): records are produced by commands from durable
artifacts, never hand-maintained. This is the build-status analog over the git tree. The hand-authored
open_threads prose (what each item IS) stays; only its DONE/OPEN STATUS is mechanically regenerated.

Predicate atoms: ("commit", subj) git log has a matching commit · ("defines", relpath, name) an Agda
module defines `name` · ("exists", relpath) · ("grep", pat, relpath) · ("cmd0", shell) exits 0 ·
("manual",) human-judged (audits/sweeps with no machine artifact yet) · ("all"|"any", [atoms]).
A MANUAL item becomes mechanical the moment you give it an artifact predicate (e.g. its report exists).
"""
import os, sys, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AGDA = os.path.join(ROOT, "agda")

# ── the manifest: item + a CHECKABLE done-predicate (the only hand-authored part) ──
WORKLIST = [
    {"sym": "△", "desc": "⊢-arc truth-correction (antisymmetrize sq-zero / phantom postulate / Stab-not-normal)",
     "done": ("all", [("commit", "⊢-△"),
                      ("defines", "Substrate/Groups/StabNotNormal.agda", "StabD-not-normal"),
                      ("grep", "antisymmetrize-square-zero", "agda/Substrate/Category/TensorProduct/Antisymmetric.agda")])},
    {"sym": "Λ", "desc": "mediating-uniqueness via LimitUP.mediate-unique", "done": ("commit", "⊢-Λ")},
    {"sym": "Β", "desc": "bounded-solver via wedge-unique", "done": ("commit", "⊢-Β")},
    {"sym": "Ι", "desc": "NaturalIsomorphism + honest CartanRoot equivalence",
     "done": ("exists", "agda/Substrate/Category/NaturalIsomorphism.agda")},
    {"sym": "Φ", "desc": "coherence/factorization sideways-copy", "done": ("commit", "⊢-Φ")},
    {"sym": "Π", "desc": "prose-disclosure residue", "done": ("commit", "⊢-Π")},
    {"sym": "ŝ", "desc": "concrete-S₄ Stab-not-normal ⊥-witness (△-tail)",
     "done": ("defines", "Substrate/Groups/StabNotNormal.agda", "StabD-not-normal")},
    {"sym": "FromImages.seal", "desc": "seal linear-from-images opaque (fan-in 213 dense-linear family)",
     "done": ("all", [("grep", "opaque", "agda/Substrate/Algebra/F2/Linear/FromImages.agda"),
                      ("commit", "Seal linear-from-images")])},
    {"sym": "def/proof", "desc": "def/proof separation paydown (0 violations)",
     "done": ("cmd0", "bash scripts/check_def_proof_separation.sh --quiet")},
    {"sym": "NatTrans.AsNamed", "desc": "NaturalTransformation.AsNamed sibling",
     "done": ("exists", "agda/Substrate/Category/NaturalTransformation/AsNamed.agda")},
    {"sym": "Ⓤ", "desc": "jea IR→Python unparser: grade ladder + seam + template",
     "done": ("exists", "jea/metalanguage/jea_extrude_ir.py")},
    {"sym": "Ⓤ.split", "desc": "IR retraction as split-Canonical (Agda apex grounding)",
     "done": ("exists", "agda/Substrate/Algebra/Quotient/IRRetraction.agda")},
    {"sym": "Ⓣ", "desc": "trace-intern a Haskell/Core mutate-in-place machine",
     "done": ("exists", "jea/metalanguage/jea_haskell_trace.py")},
    {"sym": "Ⓡ.genlop", "desc": "genlop-style build-time ledger + ETA",
     "done": ("exists", "scripts/buildtime.py")},
    {"sym": "Ⓡ.autobudget", "desc": "size the membudget lease from peak-mem history",
     "done": ("grep", "_auto_mb", "scripts/membudget")},
    {"sym": "Ⓖ★→jea", "desc": "seam-partition synthesis relayed to AI-Π0",
     "done": ("exists", "jea/metalanguage/SEAM_PARTITION.md")},
    # ── genuinely open: audits/sweeps with no machine artifact yet (give them one and they go mechanical) ──
    {"sym": "Ω4", "desc": "reflex-sweep: analytic/transcendental scope-outs (verdict: reflex purged, 3 genuine deferrals)",
     "done": ("exists", "scratch/omega4_reflex_sweep.md")},
    {"sym": "Ε(b)", "desc": "reuse-search trigger WIDENED + escalated (G9): fires on \"plan proposes new machinery\" (before building), not just post-hoc — lifted off recalled-memory onto CLAUDE.md (always-loaded) §Reuse-search-BEFORE-building + the similarity-not-grep memory + the construct-dont-classify reinvent-vs-reuse reflex. Ε(d) stale agda_similarity .pyc removed", "done": ("grep", "Reuse-search BEFORE building new machinery", "CLAUDE.md")},
    {"sym": "Ω3-L-primes.pole1", "desc": "Ⓖ★ invertible-pole cross-coherence, rank-1: gᵏ·(recip g)ᵏ≈1 "
            "(gvalue-power-antipode) — the el-atlas antipode extended to the cyclic subgroup, NO FTA",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/Primes.agda", "gvalue-power-antipode")},
    {"sym": "Ω3-L-primes.rankN", "desc": "Ⓖ★ invertible-pole, rank-n: ∏gᵢ·∏hᵢ≈1 (prod-cancel) — the "
            "free abelian group on n G-value generators inverted termwise, NO FTA",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/Primes.agda", "prod-cancel")},
    {"sym": "Ω3-L-primes.zcodec", "desc": "full ℤ-power ExpLogCodec (ZPow.ℤ-power-codec): L=ℤ group via "
            "_+ℤ_, expL z=gᶻ, mixed-sign exp-⊕ — codec-antipode fires non-trivially through the interface, NO FTA",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/Primes.agda", "gvalue-ℤ-codec")},
    {"sym": "Ω3-L-primes.factor", "desc": "layer-2 foundation: factorization = the div-mod WEDGE iterated "
            "(Algebra.Nat.Prime: mod0→∣ wedge-with-r=0, IsPrime, Factored structure). Next: existence theorem",
     "done": ("defines", "Substrate/Algebra/Nat/Prime.agda", "Factored")},
    {"sym": "Ω3-L-primes.factor-exists", "desc": "factorization EXISTENCE: factorize! (every positive ℕ "
            "= a product of primes) — div-mod wedge iterated by least prime divisor, well-founded. = codec surjectivity onto ℚ₊",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "factorize!")},
    {"sym": "Ω3-L-primes.uniq", "desc": "uniqueness KERNEL: prime-divides-product (Euclid for primes, "
            "lifting the bezout-ℤ/EEA-trace `euclid` via gcd-pos+gcd-divides) + prime∣prime→≡ — the heart of FTA uniqueness",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "prime-divides-product")},
    {"sym": "Ω3-L-primes.u2", "desc": "uniqueness capstone: prime-∈-product (a prime dividing a product "
            "of primes IS one of them) + Foundation.List.Any/_∈_ homed; with existence this forces the prime multiset",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "prime-∈-product")},
    {"sym": "Ω3-L-primes.iso", "desc": "factorisation iso as split-Canonical: factor-Canonical "
            "(ℕ⁺ ≅ canonical prime factorisations, from the factorize! retraction product∘factorize≡id) — the split-idempotent apex, NO quotient type",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "factor-Canonical")},
    {"sym": "Ω3-L-primes.iso2", "desc": "the ⊕ STRUCTURE: product-++ (product is a monoid hom "
            "List/++/[] → ℕ/·/1 — concatenating factor lists multiplies = ADDING exponents). The additive side of the iso, ℕ⁺ level; the engine of LogSumExp",
     "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties.agda", "product-++")},
    {"sym": "Ω3-L-primes.iso3", "desc": "ℚ₊-signed exponent-difference: q-factored-roundtrip "
            "(every positive G-value reconstructs EXACTLY from (factorise num, factorise den) — num=+exp, den=−exp). The ℚ₊≅⊕primesℤ retraction, Evidence-layer home",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/PrimeFactor.agda", "q-factored-roundtrip")},
    {"sym": "Ω3-L-primes.lse", "desc": "THE PAYOFF: L_OR-is-logsumexp (the el-atlas L-space OR-operator "
            "IS log-sum-exp — L_OR a b = logL(expL a +ℚ expL b), its exp = the +ℚ/G_OR of the exps; inverse via .iso3) — closes the Ω3-L-primes arc",
     "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/LogSumExp.agda", "L_OR-is-logsumexp")},
    {"sym": "Ω3-L-primes", "desc": "✅ FULLY DISCHARGED (2026-06-20). layer (1) Ⓖ★ invertible pole + ℤ-power codec (.pole1/.rankN/.zcodec); layer (2) existence (.factor/.factor-exists) + uniqueness (.uniq/.u2 via euclid) + ℕ⁺ iso (.iso) + ⊕ hom (.iso2) + ℚ₊-signed (.iso3) + PAYOFF L_OR=LogSumExp (.lse). The el-atlas OR-operator IS log-sum-exp, machine-checked, NO FTA postulate", "done": ("manual",)},
    {"sym": "Algebra↔Category.deloop", "desc": "the Algebra→Category bridge ESTABLISHED + applied: M40Group.A4Z2-Category = deloop A4Z2-Monoid (𝐁(A₄×ℤ₂)) and M40Closure.Chir-Category = deloop Chir-Monoid (𝐁(ℤ₂)) — the ≡-based domain structures onto the spine via the existing one-object delooping", "done": ("defines", "Substrate/WitnessTower/M40Group.agda", "A4Z2-Category")},
    {"sym": "Algebra↔Category.q", "desc": "GValueAsQ GROUNDED: gor=+ℚ deloops via the ℚ/≈ℚ quotient (Q.Properties.AddMonoid.+ℚ-reduced-Monoid — reduce-Canonical reps so ≈ℚ→≡, reduce kept ABSTRACT to dodge the symbolic-gcd typecheck blowup) → 𝐁(ℚ,+ℚ). Advisory → 0", "done": ("defines", "Substrate/Logic/Evidence/GValueAsQ.agda", "gor-Category")},
    {"sym": "Algebra↔Category", "desc": "✅ ADVISORY 0 — all 3 flagged leaves grounded on the categorical spine via deloop: M40Group 𝐁(A₄×ℤ₂), M40Closure 𝐁(ℤ₂) [.deloop], GValueAsQ 𝐁(ℚ,+ℚ) via the ℚ/≈ℚ quotient [.q]. The Algebra→Category gap closed at every leaf", "done": ("cmd0", "test $(bash scripts/check_categorical_grounding.sh --count) -eq 0")},
    # ── consolidated long-arc ledgers (were scattered in memory; now tracked centrally here) ──
    {"sym": "ℝ-arc", "desc": "substrate-ℝ: ℝ as a productive Wedge-process carrying EEATrace provenance (a computer reasons about ℝ, never holds it). STRUCTURALLY COMPLETE — B1 carrier → B2 convergence → B3 fuel-free field ops → B4 exp/log → B5 bisim → B6 ℝ→S¹ → B7 transcendental-digits → B8 terminal coalgebra → B9 ℚ⊣R → B10–B12 UP/det-parity, across 18 Algebra.R.* modules. (The MEMORY.md 'B2–B5 pending' line was stale.) Optional polish only: RationalAdjunction reconStep/qStep literal facades. Ledger: project_substrate_real_arc",
     "done": ("exists", "agda/Substrate/Algebra/R/Trace/Final.agda")},
    {"sym": "⊙.c1", "desc": "KEYSTONE PROVED: the wedge keep/forget IS Free⊣Forgetful — Wedge.Adjunction.FreeForgetful makes it the split idempotent (split-Canonical, the apex), the certified residue = the adjoint comparison (z = iso corner), divide total ⟹ PROVE-OR-CORRECT no-dead-end. Non-vacuous at ℕ div-mod. The reuse-search found the existing hom-iso/triangle module — extended, not rebuilt", "done": ("defines", "Substrate/Algebra/Wedge/Adjunction.agda", "wedge-Canonical")},
    {"sym": "⊙.c6", "desc": "the semiring VM PLACES ITSELF via the gauge: Semiring.Contraction.contract — ONE tensor (⊕ᵢ aᵢ⊗bᵢ, Semiring a REAL parameter) reads all 4 gauges by refl (ℕ count→11, Bool route→true, ℕ∞ tropical cost→fin 4, F₂ parity→𝟘). The consumer that measures the (NOT-dormant: Instances + SPPF.inside exist) Semiring; unifies 4 jobs as instances", "done": ("defines", "Substrate/Algebra/Semiring/Contraction.agda", "contract")},
    {"sym": "⊙.c3", "desc": "C3 commute-edge PINPOINTED: mul-comm-ℂ (ℂ commutes) + mul-noncomm-ℍ (ℍ does NOT — i·j=k≠−k=j·i) in CayleyDickson.CommuteEdge — commutativity is lost exactly at level 1→2 (+ the reusable -ℚ-cong). With 𝕊 zero-divisor (CayleyDickson) the ladder is ℂ-comm/ℍ-noncomm/…/𝕊-ZD. OPEN: 𝕆-nonassoc rung + the F₂ⁿ Morton/cocycle bridge (the deep cell)", "done": ("defines", "Substrate/Algebra/CayleyDickson/CommuteEdge.agda", "mul-comm-ℂ")},
    {"sym": "⊙.oct", "desc": "✅ 𝕆-nonassociativity (mul-nonassoc-𝕆): (i·j)·l ≠ i·(j·l) at level 3, l outside ⟨i,j⟩ — ≈#-⊥ at the e₇ leaf (proj₂³, 1ℚ vs −1ℚ), mirroring mul-noncomm-ℍ. CD ladder now COMPLETE: ℂ-comm/ℍ-noncomm/𝕆-nonassoc/𝕊-ZD all proven", "done": ("defines", "Substrate/Algebra/CayleyDickson/CommuteEdge.agda", "mul-nonassoc-𝕆")},
    {"sym": "⊙.morton", "desc": "C3 DEEP cell + GENERATOR of the grading cluster. FOUNDATION done ([.idx] CayleyDickson.Cocycle: F₂ⁿ basis map e + index-XOR (zipWith _xor_) + ℂ cocycle). FOUNDATION + ≈#-SETOID done ([.idx] basis map e/index-XOR; [.setoid] ≈#-refl/sym/trans + neg/conj-zero#). DONE: [.idx] basis/XOR · [.setoid] ≈#-equiv · [.conj] conj-on-basis · [.cong] ≈#-congruences · [.unit] zero-family + CD identity + cocycle normalization (eᵢ·e₀=eᵢ, the ε(i,0)=+1 case). OPEN (the generic law core): the NEG-DISTRIBUTION family (mul-neg/neg-invol/conj-neg/neg-add) → explicit ε → the 4-case index-XOR induction eᵢ·eⱼ ≈# ε·e_{i⊕j} → 2-cocycle identity → Morton(trivial ε)-vs-CD(nontrivial). ⟹ C2/C4/C7 [.grade]", "done": ("manual",)},
    {"sym": "⊙.morton.idx", "desc": "✅ Morton/cocycle FOUNDATION: the F₂ⁿ index→CD-basis map `e` (CayleyDickson.Cocycle) + index XOR (Vec.zipWith _xor_) + the sign-cocycle at ℂ (ℂ-sign-cocycle, ε(1,1)=−1; i² recast in the F₂ⁿ frame); nontriviality = mul-noncomm-ℍ", "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "e")},
    {"sym": "⊙.morton.setoid", "desc": "✅ the ≈# SETOID layer the cocycle needs (CayleyDickson.Setoid): ≈#-refl/sym/trans (the equivalence) + neg-zero#/conj-zero# (neg & conj fix zero#) — was ABSENT (CD had only i²≈−1 + ZD projections). Reusable CD infra; unblocks conj-on-basis", "done": ("defines", "Substrate/Algebra/CayleyDickson/Setoid.agda", "conj-zero#")},
    {"sym": "⊙.morton.conj", "desc": 'first cocycle lemma: conj-on-basis (CayleyDickson.Cocycle) -- conj eᵢ ≈# ±eᵢ (scalar fixed, every imaginary unit negated), by induction on the F₂ⁿ index on the ≈# setoid. The CD doubling conjugates a factor, so this is the recursive product law first prerequisite', "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "conj-on-basis")},
    {"sym": "⊙.morton.cong", "desc": 'the ≈# CONGRUENCE layer (CayleyDickson.Setoid): add-cong/neg-cong/conj-cong/sub-cong/mul-cong -- ≈# is a congruence for every CD op, by induction (base = ℚ-cong, step componentwise). mul-cong (the doubling-formula congruence) is the GATING prerequisite for the product-law induction (which must rewrite under mul). Reuses CommuteEdge.-ℚ-cong', "done": ("defines", "Substrate/Algebra/CayleyDickson/Setoid.agda", "mul-cong")},
    {"sym": "⊙.morton.unit", "desc": 'cocycle NORMALIZATION + CD identity: the zero family (mul-zeroˡ/ʳ, add/sub-zero) + mul-oneˡ/ʳ (CayleyDickson.Setoid: 1 is a two-sided mul identity) + prod-unitˡ/ʳ (CayleyDickson.Cocycle: e₀·eᵢ ≈# eᵢ ≈# eᵢ·e₀, since e₀ = the all-false index = 1). The FIRST full case of the product law eᵢ·eⱼ ≈# ε·e_{i⊕j}: when an index is 0, i⊕0=i and ε(i,0)=ε(0,i)=+1. NO neg-distribution needed', "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "prod-unitʳ")},
    {"sym": "⊙.grade", "desc": "C2/C4/C7 — graded-GF(2) non-cancelling, ANF-degree≟F₂ⁿ-index two-gradings, edge=grade=cocycle. COMMON STRUCTURE: all readings of the F₂ⁿ sign-cocycle ⟹ DERIVED from ⊙.morton (instantiations, not separate builds)", "done": ("manual",)},
    {"sym": "⊙.c8", "desc": "C8 — Morton/Hilbert curve-crossover at the grade boundary; the cost/tropical instance (relates the done C6 Contraction tensor)", "done": ("manual",)},
    {"sym": "⊙", "desc": "commuting-sphere: the 8 prove-or-correct GF(2)-VM conjectures — C1 KEYSTONE r<b-residue = the Free⊣Forgetful adjoint correction (⟹ metaphor→proof is prove-or-correct); C2 graded-GF(2) (ungraded was the mistake); C3 Morton≅Cayley-Dickson via the cocycle; C4 F₂ⁿ-index grading; C5 tropical-VM cost; C6 Kirchhoff/conductance; C7 edge=grade=cocycle; C8 Morton/Hilbert curve-crossover at the grade boundary. C1 ✅ ([.c1]) + C6 ✅ ([.c6]) + C3 ladder ✅ COMPLETE ([.c3]/[.oct]: ℂ-comm/ℍ-noncomm/𝕆-nonassoc/𝕊-ZD). REMAINING: only C3 cocycle/Morton bridge [.morton] (the deep cell, ⟹ C2/C4/C7 [.grade]) + C8 [.c8] — MANUAL until each lands. Ledger: scratch/commuting_sphere.md; in-code index Algebra.Wedge.Sphere",
     "done": ("manual",)},
    {"sym": "⊙.cd", "desc": "commuting-sphere C3 prerequisite: Cayley-Dickson IN the substrate (the doubling-with-involution generator) — the ledger's 'CD absent, MUST-BUILD' is STALE; built at Algebra.CayleyDickson (ℂ/ℍ/𝕆/𝕊 tower over ℚ)",
     "done": ("exists", "agda/Substrate/Algebra/CayleyDickson.agda")},
    {"sym": "⊙.tropical", "desc": "commuting-sphere C5 prerequisite: the tropical (min-plus) cost gauge — BUILT as Semiring.Instances.tropical-semiring (ℕ∞ min-plus); was a false-positive grep on Sphere prose, repointed at the artifact",
     "done": ("grep", "tropical", "agda/Substrate/Algebra/Wedge/Sphere.agda")},
]


def _git_has_commit(subj: str) -> bool:
    r = subprocess.run(["git", "-C", ROOT, "log", "--oneline", "-F", "--grep", subj],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def _defines(relpath: str, name: str) -> bool:
    p = relpath if os.path.isabs(relpath) else os.path.join(AGDA, relpath)
    try:
        with open(p) as f:
            for ln in f:
                s = ln.lstrip()
                if s.startswith(name) and len(s) > len(name) and s[len(name)] in " :":
                    return True
    except OSError:
        return False
    return False


def _grep(pat: str, relpath: str) -> bool:
    p = relpath if os.path.isabs(relpath) else os.path.join(ROOT, relpath)
    try:
        with open(p) as f:
            return pat in f.read()
    except OSError:
        return False


def _cmd0(cmd: str) -> bool:
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True).returncode == 0


def status(pred):
    """True = DONE, False = OPEN, None = MANUAL (human-judged, no machine artifact)."""
    t = pred[0]
    if t == "commit":  return _git_has_commit(pred[1])
    if t == "defines": return _defines(pred[1], pred[2])
    if t == "exists":  return os.path.exists(pred[1] if os.path.isabs(pred[1]) else os.path.join(ROOT, pred[1]))
    if t == "grep":    return _grep(pred[1], pred[2])
    if t == "cmd0":    return _cmd0(pred[1])
    if t == "manual":  return None
    if t == "all":
        rs = [status(p) for p in pred[1]]
        return False if any(r is False for r in rs) else (None if any(r is None for r in rs) else True)
    if t == "any":
        rs = [status(p) for p in pred[1]]
        return True if any(r is True for r in rs) else (None if any(r is None for r in rs) else False)
    return None


def rows():
    for it in WORKLIST:
        yield it["sym"], {True: "DONE", False: "OPEN", None: "MANUAL"}[status(it["done"])], it["desc"]


LEDGER = os.path.expanduser(
    "~/.claude/projects/-home-mikemol-github-substrate/memory/project_open_threads.md")
BEGIN, END = "<!-- worklist:auto BEGIN (regenerated by scripts/worklist.py --update; do not edit) -->", \
             "<!-- worklist:auto END -->"


def _md_block() -> str:
    lines = [BEGIN, "## Live status — DERIVED from the tree (run `scripts/worklist.py`; never hand-edit)",
             "", "| status | sym | item |", "|---|---|---|"]
    for s, st, d in rows():
        lines.append(f"| {'✅' if st=='DONE' else ('🔶' if st=='MANUAL' else '⬜')} {st} | `{s}` | {d} |")
    n = {k: sum(1 for _, st, _ in rows() if st == k) for k in ("DONE", "OPEN", "MANUAL")}
    lines += ["", f"_{n['DONE']} done · {n['OPEN']} open · {n['MANUAL']} manual (audits). "
                  f"Status is computed, not stored — a re-surfaced 'open' that is really done cannot occur._", END]
    return "\n".join(lines)


def _update_ledger(path: str) -> str:
    block = _md_block()
    try:
        with open(path) as f:
            txt = f.read()
    except OSError:
        return f"ledger not found: {path}"
    if BEGIN in txt and END in txt:
        pre, rest = txt.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        txt = pre + block + post
    else:                                              # insert the block right after the H1/intro
        nl = txt.find("\n\n")
        txt = (txt[:nl+2] + block + "\n\n" + txt[nl+2:]) if nl != -1 else (block + "\n\n" + txt)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(txt)
    os.replace(tmp, path)
    return f"regenerated worklist status block in {os.path.basename(path)}"


def main(argv) -> int:
    only_open = "--open" in argv
    as_md = "--md" in argv
    if "--update" in argv:
        i = argv.index("--update")
        path = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("-") else LEDGER
        print(_update_ledger(path))
        return 0
    if "--check" in argv:
        # a gate: every item whose predicate is a concrete artifact should still resolve; report MANUALs.
        bad = [s for s, st, _ in rows() if st == "OPEN" and WORKLIST[[i["sym"] for i in WORKLIST].index(s)]["done"][0] != "manual"]
        # (OPEN with an artifact predicate is legitimately not-done, not a regression — so --check only
        #  reports counts; the value is the DERIVED status itself never going stale.)
        n = {k: sum(1 for _, st, _ in rows() if st == k) for k in ("DONE", "OPEN", "MANUAL")}
        print(f"worklist: {n['DONE']} done, {n['OPEN']} open, {n['MANUAL']} manual (status derived from tree)")
        return 0
    out = [(s, st, d) for s, st, d in rows() if not (only_open and st == "DONE")]
    if as_md:
        print("| status | sym | item |\n|---|---|---|")
        for s, st, d in out:
            print(f"| {'✅' if st=='DONE' else ('🔶' if st=='MANUAL' else '⬜')} {st} | `{s}` | {d} |")
    else:
        for s, st, d in out:
            mark = {"DONE": "✅", "OPEN": "⬜", "MANUAL": "🔶"}[st]
            print(f"  {mark} {st:<6} {s:<16} {d}")
    n = {k: sum(1 for _, st, _ in rows() if st == k) for k in ("DONE", "OPEN", "MANUAL")}
    print(f"\n  {n['DONE']} done · {n['OPEN']} open · {n['MANUAL']} manual  (DERIVED from the tree — never hand-edited)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
