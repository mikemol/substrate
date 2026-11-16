# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The worklist ROSTER — every tracked thread and its checkable done-predicate.

⚑⚑⚑ THIS IS A RELOCATION, NOT A REWRITE, AND THE DISTINCTION IS THE WHOLE SAFETY ARGUMENT. The
roster lived in `scripts/worklist.py`, which carries findings past the per-file gate's
all-or-nothing threshold, so a one-token path repair was refused exactly as any other edit
(gate-G217). The gate's own refusal names the only route: extract the concern into a new module
written clean in one pass. Nothing here is re-decided — the items arrived through
`roster_extract`, which parses the literal rather than reading it.

⚑⚑ AND IT WAS EXTRACTED BY A PARSER BECAUSE READING IT BY EYE PRODUCED A FALSE COUNT (gate-G216).
A hand transcription of this roster read 47 where three instruments say 60, and that figure was
then filed as a CORRECTION to the tools that had been right. `roster_extract.count_elements` is
the authority for the population, and `scripts/roster_span.py` is its CLI.

⚑⚑⚑ SEVEN PREDICATES ARE REPOINTED HERE, AND THE CAUSE WAS UNIFORM.
`check_worklist_predicates.py` reported seven items naming an artifact that no longer exists — six
at `Substrate/Algebra/Nat/Prime/Properties.agda` and one at
`Substrate/Algebra/R/Trace/Final.agda`. Neither file was deleted: both were DECOMPOSED into
one-definition-per-file siblings by the ban-decompose pipeline, so every definition the items name
is still proved and still present, under a new home. Each target was located with
`agda_defs.py <name>` rather than guessed — and one guess would have been wrong, since
`factorize!` lives in `Factorize2`, not `Factorize`.

⚑⚑ A STALE PREDICATE IS WORSE THAN AN OPEN ONE, WHICH IS WHY THIS IS A REPOINT AND NOT A DELETION.
`worklist.py`'s `status()` collapses every failure onto False = OPEN, so an item whose artifact
moved reads as work not yet done — indistinguishable from a live thread, and re-dispatchable
forever. The items below are all DONE; pointing them at their real homes is what lets them say so.

⚑ THE \N{DOUBLE-STRUCK CAPITAL R}-arc ITEM ALSO CHANGES KIND, from `exists` to `defines`. Its
predicate named a FILE, and the file is gone while its content is not, so `exists` can never hold
again. `defines` asks the question the item actually means — is the B8 terminal-coalgebra result
proved — and `Final.AnaUnique` is where the decomposition put it.

⚑⚑ AND THIS DOCSTRING WAS ITSELF REFUSED FOR SPELLING THAT GLYPH LITERALLY (gate-G219). The
paragraph explaining why the roster's characters are escaped was written with an unescaped one, so
the data was clean and the commentary about the data was not — the second instance of a class
`glyph_escape.py` records about its own docstring.

⚑ THE PREDICATE VOCABULARY IS `worklist.py`'s, AND ITS TWO PATH CONVENTIONS DIFFER. `defines` is
`(head, relpath, name)` with the path at index 1 resolved against the AGDA root; `grep` is
`(head, pattern, relpath)` with the path at index 2 against the REPO root; `exists` is
`(head, relpath)` against the repo root. Reading `defines` as `grep`-shaped is a recorded defect
(gate-F94), caught by a fixture and by nothing else.
"""

from __future__ import annotations

#: Every tracked thread: a symbol, a description, and a predicate deciding DONE from the tree.
#: ⚑ The population is answered by `roster_span.py substrate/worklist_manifest.py WORKLIST`,
#: never by counting these rows by eye.
#: ⚑⚑ THE ANNOTATION IS LOAD-BEARING, NOT DECORATION. Without it the literal infers as
#: `list[object]` and every consumer's call is a type error — the mixed value types (a `str` desc
#: beside a nested predicate tuple) give the inferencer no common shape to find. Declaring it here
#: is what lets the shim pass it straight through rather than casting at the call site, which
#: would put a claim about this module's shape in a file that cannot check it.
WORKLIST: list[dict[str, object]] = [
    {
        "sym": "△",
        "desc": "⊢-arc truth-correction (antisymmetrize sq-zero / phantom postulate / "
        "Stab-not-normal)",
        "done": (
            "all",
            [
                ("commit", "⊢-△"),
                ("defines", "Substrate/Groups/StabNotNormal.agda", "StabD-not-normal"),
                (
                    "grep",
                    "antisymmetrize-square-zero",
                    "agda/Substrate/Category/TensorProduct/Antisymmetric.agda",
                ),
            ],
        ),
    },
    {
        "sym": "Λ",
        "desc": "mediating-uniqueness via LimitUP.mediate-unique",
        "done": ("commit", "⊢-Λ"),
    },
    {
        "sym": "\N{GREEK CAPITAL LETTER BETA}",
        "desc": "bounded-solver via wedge-unique",
        "done": ("commit", "⊢-\N{GREEK CAPITAL LETTER BETA}"),
    },
    {
        "sym": "\N{GREEK CAPITAL LETTER IOTA}",
        "desc": "NaturalIsomorphism + honest CartanRoot equivalence",
        "done": ("exists", "agda/Substrate/Category/NaturalIsomorphism.agda"),
    },
    {"sym": "Φ", "desc": "coherence/factorization sideways-copy", "done": ("commit", "⊢-Φ")},
    {"sym": "Π", "desc": "prose-disclosure residue", "done": ("commit", "⊢-Π")},
    {
        "sym": "ŝ",
        "desc": "concrete-S₄ Stab-not-normal ⊥-witness (△-tail)",
        "done": ("defines", "Substrate/Groups/StabNotNormal.agda", "StabD-not-normal"),
    },
    {
        "sym": "FromImages.seal",
        "desc": "seal linear-from-images opaque (fan-in 213 dense-linear family)",
        "done": (
            "all",
            [
                ("grep", "opaque", "agda/Substrate/Algebra/F2/Linear/FromImages.agda"),
                ("commit", "Seal linear-from-images"),
            ],
        ),
    },
    {
        "sym": "def/proof",
        "desc": "def/proof separation paydown (0 violations)",
        "done": ("cmd0", "bash scripts/check_def_proof_separation.sh --quiet"),
    },
    {
        "sym": "NatTrans.AsNamed",
        "desc": "NaturalTransformation.AsNamed sibling",
        "done": ("exists", "agda/Substrate/Category/NaturalTransformation/AsNamed.agda"),
    },
    {
        "sym": "Ⓤ",
        "desc": "jea IR→Python unparser: grade ladder + seam + template",
        "done": ("exists", "jea/metalanguage/jea_extrude_ir.py"),
    },
    {
        "sym": "Ⓤ.split",
        "desc": "IR retraction as split-Canonical (Agda apex grounding)",
        "done": ("exists", "agda/Substrate/Algebra/Quotient/IRRetraction.agda"),
    },
    {
        "sym": "Ⓣ",
        "desc": "trace-intern a Haskell/Core mutate-in-place machine",
        "done": ("exists", "jea/metalanguage/jea_haskell_trace.py"),
    },
    {
        "sym": "Ⓡ.genlop",
        "desc": "genlop-style build-time ledger + ETA",
        "done": ("exists", "scripts/buildtime.py"),
    },
    {
        "sym": "Ⓡ.autobudget",
        "desc": "size the membudget lease from peak-mem history",
        "done": ("grep", "_auto_mb", "scripts/membudget"),
    },
    {
        "sym": "Ⓖ★→jea",
        "desc": "seam-partition synthesis relayed to AI-Π0",
        "done": ("exists", "jea/metalanguage/SEAM_PARTITION.md"),
    },
    # ── genuinely open: audits/sweeps with no machine artifact yet (give them one and they go
    #    mechanical) ──
    {
        "sym": "Ω4",
        "desc": "reflex-sweep: analytic/transcendental scope-outs (verdict: reflex purged, 3 genuine "
        "deferrals)",
        "done": ("exists", "scratch/omega4_reflex_sweep.md"),
    },
    {
        "sym": "\N{GREEK CAPITAL LETTER EPSILON}(b)",
        "desc": 'reuse-search trigger WIDENED + escalated (G9): fires on "plan proposes new '
        'machinery" (before building), not just post-hoc — lifted off recalled-memory onto '
        "CLAUDE.md (always-loaded) §Reuse-search-BEFORE-building + the similarity-not-grep "
        "memory + the construct-dont-classify reinvent-vs-reuse reflex. "
        "\N{GREEK CAPITAL LETTER EPSILON}(d) stale agda_similarity .pyc removed",
        "done": ("grep", "Reuse-search BEFORE building new machinery", "CLAUDE.md"),
    },
    {
        "sym": "Ⓥ",
        "desc": "verify-the-verifier (G9 of Ⓩ): the worklist tracker is now GATED — pre-commit runs "
        "`worklist.py --check`, so the derived-status tracker must PARSE + RUN end-to-end "
        "(every entry well-formed, every predicate evaluating) or the commit is blocked. "
        "Closes the instrument↔execution residue: a dropped comma had made worklist.py "
        "unparseable for ~10 commits, invisible because no gate ran it. "
        "Correct-by-construction (a gate, not memory)",
        "done": ("grep", "worklist tracker integrity", ".githooks/pre-commit"),
    },
    {
        "sym": "Ω3-L-primes.pole1",
        "desc": "Ⓖ★ invertible-pole cross-coherence, rank-1: gᵏ·(recip g)ᵏ≈1 "
        "(gvalue-power-antipode) — the el-atlas antipode extended to the cyclic subgroup, "
        "NO FTA",
        "done": (
            "defines",
            "Substrate/Logic/Evidence/GValueLSpace/Primes.agda",
            "gvalue-power-antipode",
        ),
    },
    {
        "sym": "Ω3-L-primes.rankN",
        "desc": "Ⓖ★ invertible-pole, rank-n: ∏gᵢ·∏hᵢ≈1 (prod-cancel) — the free abelian group on n "
        "G-value generators inverted termwise, NO FTA",
        "done": ("defines", "Substrate/Logic/Evidence/GValueLSpace/Primes.agda", "prod-cancel"),
    },
    {
        "sym": "Ω3-L-primes.zcodec",
        "desc": "full \N{DOUBLE-STRUCK CAPITAL Z}-power ExpLogCodec "
        "(ZPow.\N{DOUBLE-STRUCK CAPITAL Z}-power-codec): L=\N{DOUBLE-STRUCK CAPITAL Z} group "
        "via _+\N{DOUBLE-STRUCK CAPITAL Z}_, expL z=gᶻ, mixed-sign exp-⊕ — codec-antipode "
        "fires non-trivially through the interface, NO FTA",
        "done": (
            "defines",
            "Substrate/Logic/Evidence/GValueLSpace/Primes.agda",
            "gvalue-\N{DOUBLE-STRUCK CAPITAL Z}-codec",
        ),
    },
    {
        "sym": "Ω3-L-primes.factor",
        "desc": "layer-2 foundation: factorization = the div-mod WEDGE iterated (Algebra.Nat.Prime: "
        "mod0→\N{DIVIDES} wedge-with-r=0, IsPrime, Factored structure). Next: existence "
        "theorem",
        "done": ("defines", "Substrate/Algebra/Nat/Prime.agda", "Factored"),
    },
    # ⚑ REPOINTED (gate-F96): Prime/Properties.agda decomposed into one-definition siblings.
    #   `factorize!` is in Factorize2, NOT Factorize — located with `agda_defs.py factorize!`,
    #   and a guess would have named the wrong sibling.
    {
        "sym": "Ω3-L-primes.factor-exists",
        "desc": "factorization EXISTENCE: factorize! (every positive \N{DOUBLE-STRUCK CAPITAL N} = a "
        "product of primes) — div-mod wedge iterated by least prime divisor, well-founded. "
        "= codec surjectivity onto \N{DOUBLE-STRUCK CAPITAL Q}₊",
        "done": ("defines", "Substrate/Algebra/Nat/Prime/Properties/Factorize2.agda", "factorize!"),
    },
    {
        "sym": "Ω3-L-primes.uniq",
        "desc": "uniqueness KERNEL: prime-divides-product (Euclid for primes, lifting the "
        "bezout-\N{DOUBLE-STRUCK CAPITAL Z}/EEA-trace `euclid` via gcd-pos+gcd-divides) + "
        "prime\N{DIVIDES}prime→≡ — the heart of FTA uniqueness",
        "done": (
            "defines",
            "Substrate/Algebra/Nat/Prime/Properties/PrimeDividesProduct.agda",
            "prime-divides-product",
        ),
    },
    {
        "sym": "Ω3-L-primes.u2",
        "desc": "uniqueness capstone: prime-∈-product (a prime dividing a product of primes IS one "
        "of them) + Foundation.List.Any/_∈_ homed; with existence this forces the prime "
        "multiset",
        "done": (
            "defines",
            "Substrate/Algebra/Nat/Prime/Properties/PrimeProduct.agda",
            "prime-∈-product",
        ),
    },
    {
        "sym": "Ω3-L-primes.iso",
        "desc": "factorisation iso as split-Canonical: factor-Canonical "
        "(\N{DOUBLE-STRUCK CAPITAL N}⁺ ≅ canonical prime factorisations, from the factorize! "
        "retraction product∘factorize≡id) — the split-idempotent apex, NO quotient type",
        "done": (
            "defines",
            "Substrate/Algebra/Nat/Prime/Properties/FactorCanonical.agda",
            "factor-Canonical",
        ),
    },
    {
        "sym": "Ω3-L-primes.iso2",
        "desc": "the ⊕ STRUCTURE: product-++ (product is a monoid hom List/++/[] → "
        "\N{DOUBLE-STRUCK CAPITAL N}/·/1 — concatenating factor lists multiplies = ADDING "
        "exponents). The additive side of the iso, \N{DOUBLE-STRUCK CAPITAL N}⁺ level; the "
        "engine of LogSumExp",
        "done": (
            "defines",
            "Substrate/Algebra/Nat/Prime/Properties/ProductAppend.agda",
            "product-++",
        ),
    },
    {
        "sym": "Ω3-L-primes.iso3",
        "desc": "\N{DOUBLE-STRUCK CAPITAL Q}₊-signed exponent-difference: q-factored-roundtrip "
        "(every positive G-value reconstructs EXACTLY from (factorise num, factorise den) — "
        "num=+exp, den=\N{MINUS SIGN}exp). The \N{DOUBLE-STRUCK CAPITAL Q}₊≅⊕primes"
        "\N{DOUBLE-STRUCK CAPITAL Z} retraction, Evidence-layer home",
        "done": (
            "defines",
            "Substrate/Logic/Evidence/GValueLSpace/PrimeFactor/QFactoredRoundtrip.agda",
            "q-factored-roundtrip",
        ),
    },
    {
        "sym": "Ω3-L-primes.lse",
        "desc": "THE PAYOFF: L_OR-is-logsumexp (the el-atlas L-space OR-operator IS log-sum-exp — "
        "L_OR a b = logL(expL a +\N{DOUBLE-STRUCK CAPITAL Q} expL b), its exp = the "
        "+\N{DOUBLE-STRUCK CAPITAL Q}/G_OR of the exps; inverse via .iso3) — closes the "
        "Ω3-L-primes arc",
        "done": (
            "defines",
            "Substrate/Logic/Evidence/GValueLSpace/LogSumExp.agda",
            "L_OR-is-logsumexp",
        ),
    },
    {
        "sym": "Ω3-L-primes",
        "desc": "✅ FULLY DISCHARGED (2026-06-20). layer (1) Ⓖ★ invertible pole + "
        "\N{DOUBLE-STRUCK CAPITAL Z}-power codec (.pole1/.rankN/.zcodec); layer (2) "
        "existence (.factor/.factor-exists) + uniqueness (.uniq/.u2 via euclid) + "
        "\N{DOUBLE-STRUCK CAPITAL N}⁺ iso (.iso) + ⊕ hom (.iso2) + "
        "\N{DOUBLE-STRUCK CAPITAL Q}₊-signed (.iso3) + PAYOFF L_OR=LogSumExp (.lse). The "
        "el-atlas OR-operator IS log-sum-exp, machine-checked, NO FTA postulate",
        "done": (
            "defines",
            "Substrate/Logic/Evidence/GValueLSpace/LogSumExp.agda",
            "L_OR-is-logsumexp",
        ),
    },
    {
        "sym": "Algebra↔Category.deloop",
        "desc": "the Algebra→Category bridge ESTABLISHED + applied: M40Group.A4Z2-Category = deloop "
        "A4Z2-Monoid (\N{MATHEMATICAL BOLD CAPITAL B}(A₄\N{MULTIPLICATION SIGN}"
        "\N{DOUBLE-STRUCK CAPITAL Z}₂)) and M40Closure.Chir-Category = deloop Chir-Monoid "
        "(\N{MATHEMATICAL BOLD CAPITAL B}(\N{DOUBLE-STRUCK CAPITAL Z}₂)) — the ≡-based "
        "domain structures onto the spine via the existing one-object delooping",
        "done": ("defines", "Substrate/WitnessTower/M40Group.agda", "A4Z2-Category"),
    },
    {
        "sym": "Algebra↔Category.q",
        "desc": "GValueAsQ GROUNDED: gor=+\N{DOUBLE-STRUCK CAPITAL Q} deloops via the "
        "\N{DOUBLE-STRUCK CAPITAL Q}/≈\N{DOUBLE-STRUCK CAPITAL Q} quotient "
        "(Q.Properties.AddMonoid.+\N{DOUBLE-STRUCK CAPITAL Q}-reduced-Monoid — "
        "reduce-Canonical reps so ≈\N{DOUBLE-STRUCK CAPITAL Q}→≡, reduce kept ABSTRACT to "
        "dodge the symbolic-gcd typecheck blowup) → \N{MATHEMATICAL BOLD CAPITAL B}"
        "(\N{DOUBLE-STRUCK CAPITAL Q},+\N{DOUBLE-STRUCK CAPITAL Q}). Advisory → 0",
        "done": ("defines", "Substrate/Logic/Evidence/GValueAsQ.agda", "gor-Category"),
    },
    {
        "sym": "Algebra↔Category",
        "desc": "✅ ADVISORY 0 — all 3 flagged leaves grounded on the categorical spine via deloop: "
        "M40Group \N{MATHEMATICAL BOLD CAPITAL B}(A₄\N{MULTIPLICATION SIGN}"
        "\N{DOUBLE-STRUCK CAPITAL Z}₂), M40Closure \N{MATHEMATICAL BOLD CAPITAL B}"
        "(\N{DOUBLE-STRUCK CAPITAL Z}₂) [.deloop], GValueAsQ "
        "\N{MATHEMATICAL BOLD CAPITAL B}(\N{DOUBLE-STRUCK CAPITAL Q},"
        "+\N{DOUBLE-STRUCK CAPITAL Q}) via the \N{DOUBLE-STRUCK CAPITAL Q}/"
        "≈\N{DOUBLE-STRUCK CAPITAL Q} quotient [.q]. The Algebra→Category gap closed at "
        "every leaf",
        "done": ("cmd0", "test $(bash scripts/check_categorical_grounding.sh --count) -eq 0"),
    },
    # ── consolidated long-arc ledgers (were scattered in memory; now tracked centrally here) ──
    # ⚑ REPOINTED (gate-F96), AND THE KIND CHANGED. `Trace/Final.agda` became a ten-module
    #   subtree, so `exists` on the file can never hold again. The item's claim is B8 — the
    #   terminal coalgebra — and `defines` on `Final.AnaUnique` asks that question directly.
    {
        "sym": "\N{DOUBLE-STRUCK CAPITAL R}-arc",
        "desc": "substrate-\N{DOUBLE-STRUCK CAPITAL R}: \N{DOUBLE-STRUCK CAPITAL R} as a productive "
        "Wedge-process carrying EEATrace provenance (a computer reasons about "
        "\N{DOUBLE-STRUCK CAPITAL R}, never holds it). STRUCTURALLY COMPLETE — B1 carrier → "
        "B2 convergence → B3 fuel-free field ops → B4 exp/log → B5 bisim → B6 "
        "\N{DOUBLE-STRUCK CAPITAL R}→S¹ → B7 transcendental-digits → B8 terminal coalgebra → "
        "B9 \N{DOUBLE-STRUCK CAPITAL Q}⊣R → B10\N{EN DASH}B12 UP/det-parity, across 18 "
        "Algebra.R.* modules. (The MEMORY.md 'B2\N{EN DASH}B5 pending' line was stale.) "
        "Optional polish only: RationalAdjunction reconStep/qStep literal facades. Ledger: "
        "project_substrate_real_arc",
        "done": ("defines", "Substrate/Algebra/R/Trace/Final/AnaUnique.agda", "ana-unique"),
    },
    {
        "sym": "⊙.c1",
        "desc": "KEYSTONE PROVED: the wedge keep/forget IS Free⊣Forgetful — "
        "Wedge.Adjunction.FreeForgetful makes it the split idempotent (split-Canonical, the "
        "apex), the certified residue = the adjoint comparison (z = iso corner), divide "
        "total ⟹ PROVE-OR-CORRECT no-dead-end. Non-vacuous at "
        "\N{DOUBLE-STRUCK CAPITAL N} div-mod. The reuse-search found the existing "
        "hom-iso/triangle module — extended, not rebuilt",
        "done": ("defines", "Substrate/Algebra/Wedge/Adjunction.agda", "wedge-Canonical"),
    },
    {
        "sym": "⊙.c6",
        "desc": "the semiring VM PLACES ITSELF via the gauge: Semiring.Contraction.contract — ONE "
        "tensor (⊕ᵢ aᵢ⊗bᵢ, Semiring a REAL parameter) reads all 4 gauges by refl "
        "(\N{DOUBLE-STRUCK CAPITAL N} count→11, Bool route→true, "
        "\N{DOUBLE-STRUCK CAPITAL N}∞ tropical cost→fin 4, F₂ parity→"
        "\N{MATHEMATICAL DOUBLE-STRUCK DIGIT ZERO}). The consumer that measures the "
        "(NOT-dormant: Instances + SPPF.inside exist) Semiring; unifies 4 jobs as instances",
        "done": ("defines", "Substrate/Algebra/Semiring/Contraction.agda", "contract"),
    },
    {
        "sym": "⊙.c3",
        "desc": "C3 commute-edge PINPOINTED: mul-comm-\N{DOUBLE-STRUCK CAPITAL C} "
        "(\N{DOUBLE-STRUCK CAPITAL C} commutes) + mul-noncomm-\N{DOUBLE-STRUCK CAPITAL H} "
        "(\N{DOUBLE-STRUCK CAPITAL H} does NOT — i·j=k≠\N{MINUS SIGN}k=j·i) in "
        "CayleyDickson.CommuteEdge — commutativity is lost exactly at level 1→2 (+ the "
        "reusable -\N{DOUBLE-STRUCK CAPITAL Q}-cong). With "
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL S} zero-divisor (CayleyDickson) the ladder is "
        "\N{DOUBLE-STRUCK CAPITAL C}-comm/\N{DOUBLE-STRUCK CAPITAL H}-noncomm/…/"
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL S}-ZD. OPEN: "
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}-nonassoc rung + the F₂ⁿ Morton/cocycle "
        "bridge (the deep cell)",
        "done": (
            "defines",
            "Substrate/Algebra/CayleyDickson/CommuteEdge.agda",
            "mul-comm-\N{DOUBLE-STRUCK CAPITAL C}",
        ),
    },
    {
        "sym": "⊙.oct",
        "desc": "✅ \N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}-nonassociativity "
        "(mul-nonassoc-\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}): (i·j)·l ≠ i·(j·l) at level "
        "3, l outside ⟨i,j⟩ — ≈#-⊥ at the e₇ leaf (proj₂³, 1\N{DOUBLE-STRUCK CAPITAL Q} vs "
        "\N{MINUS SIGN}1\N{DOUBLE-STRUCK CAPITAL Q}), mirroring "
        "mul-noncomm-\N{DOUBLE-STRUCK CAPITAL H}. CD ladder now COMPLETE: "
        "\N{DOUBLE-STRUCK CAPITAL C}-comm/\N{DOUBLE-STRUCK CAPITAL H}-noncomm/"
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}-nonassoc/"
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL S}-ZD all proven",
        "done": (
            "defines",
            "Substrate/Algebra/CayleyDickson/CommuteEdge.agda",
            "mul-nonassoc-\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}",
        ),
    },
    {
        "sym": "⊙.morton",
        "desc": "✅ C3 PROVED — the GENERIC PRODUCT LAW (CayleyDickson.Cocycle.prod): eᵢ·eⱼ ≈# "
        "ε(i,j)·e_{i⊕j} for ALL n, with the explicit recursive 2-cochain ε. Built bottom-up: "
        "[.idx] basis-map e + index-XOR · [.setoid] ≈#-equivalence · [.conj] conj-on-basis · "
        "[.cong] ≈#-congruences · [.unit] zero-family + CD identity + normalization "
        "(ε(i,0)=+1) · [.neg] negation-distribution · [.prod] the 4-case index-XOR "
        "induction. Morton = trivial cochain (ε≡false, pure XOR); CD = this nontrivial ε "
        "(noncomm = mul-noncomm-\N{DOUBLE-STRUCK CAPITAL H}, strict-2-cocycle failure = the "
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O} associator). Grounds C7 "
        "(edge=grade=cocycle); C2/C4 [.grade] remain",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "prod"),
    },
    {
        "sym": "⊙.assoc",
        "desc": "✅ the ASSOCIATOR as a measured 3-cochain (CayleyDickson.Cocycle) — the ⊙.measure "
        "instance turning prod's unclaimed \N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}-"
        "associator into a tracked obstruction. dε = the coboundary 3-cochain of ε; "
        "associator proves (eᵢ·eⱼ)·eₖ ≈# dε(i,j,k)·(eᵢ·(eⱼ·eₖ)) (both land at e_{i⊕j⊕k}, dε "
        "is the sign difference); associative-at: dε=false ⟹ associates; "
        "dε-\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O} ≡ true recovers "
        "mul-nonassoc-\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O} from the cochain. Unifies #3 "
        "(cocycle) + #5 (graded obstruction): nonassociativity = ε's non-closure, graded",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "associator"),
    },
    {
        "sym": "⊙.pentagon",
        "desc": "✅ the PENTAGON — dε is a CLOSED 3-cochain (CayleyDickson.Cocycle), discharging the "
        "G8 suspicion (the one unverified claim in the closed sphere). δ²/δ³ = the F₂ⁿ "
        "group-cohomology coboundary operators; dε-is-coboundary proves dε ≡ δ²ε (dε IS the "
        "coboundary of ε, hence closed since coboundaries are closed/d²=0); "
        "pentagon-\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}₁₂₃ verify δ³(dε) ≡ false at "
        "octonion 4-tuples where dε itself is nonzero — the associator obstruction is "
        "COHERENT (higher cell closes). Fully-generic d²=0 ∀φ (a 20-term xor-AC "
        "cancellation, each face-pair via ⊕-assoc + xor-same) is the remaining cohomological "
        "refinement",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "dε-is-coboundary"),
    },
    {
        "sym": "⊙.dd",
        "desc": "✅ generic d²=0 ∀φ (CayleyDickson.Coboundary.d²-zero) — makes ⊙.pentagon "
        "UNCONDITIONAL. δ³(δ²φ) ≡ false for EVERY 2-cochain φ (not just the "
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O} witnesses): the 20-term face expansion has "
        "each of 10 distinct values twice (simplicial pairing), so it cancels over F₂. "
        "Proved via a foldrB xor-parity framework (foldrB-++ homomorphism + "
        "remove-head-pair) — flatten the tree to a list, cancel the 10 pairs head-first; the "
        "two diagonal faces aligned by ⊕-assoc. So dε = δ²ε is closed for ALL cochains",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Coboundary.agda", "d²-zero"),
    },
    {
        "sym": "⊙.morton.idx",
        "desc": "✅ Morton/cocycle FOUNDATION: the F₂ⁿ index→CD-basis map `e` (CayleyDickson.Cocycle) "
        "+ index XOR (Vec.zipWith _xor_) + the sign-cocycle at \N{DOUBLE-STRUCK CAPITAL C} "
        "(\N{DOUBLE-STRUCK CAPITAL C}-sign-cocycle, ε(1,1)=\N{MINUS SIGN}1; i² recast in the "
        "F₂ⁿ frame); nontriviality = mul-noncomm-\N{DOUBLE-STRUCK CAPITAL H}",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "e"),
    },
    {
        "sym": "⊙.morton.setoid",
        "desc": "✅ the ≈# SETOID layer the cocycle needs (CayleyDickson.Setoid): ≈#-refl/sym/trans "
        "(the equivalence) + neg-zero#/conj-zero# (neg & conj fix zero#) — was ABSENT (CD "
        "had only i²≈\N{MINUS SIGN}1 + ZD projections). Reusable CD infra; unblocks "
        "conj-on-basis",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Setoid.agda", "conj-zero#"),
    },
    {
        "sym": "⊙.morton.conj",
        "desc": "first cocycle lemma: conj-on-basis (CayleyDickson.Cocycle) -- conj eᵢ ≈# ±eᵢ "
        "(scalar fixed, every imaginary unit negated), by induction on the F₂ⁿ index on the "
        "≈# setoid. The CD doubling conjugates a factor, so this is the recursive product "
        "law first prerequisite",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "conj-on-basis"),
    },
    {
        "sym": "⊙.morton.cong",
        "desc": "the ≈# CONGRUENCE layer (CayleyDickson.Setoid): "
        "add-cong/neg-cong/conj-cong/sub-cong/mul-cong -- ≈# is a congruence for every CD "
        "op, by induction (base = \N{DOUBLE-STRUCK CAPITAL Q}-cong, step componentwise). "
        "mul-cong (the doubling-formula congruence) is the GATING prerequisite for the "
        "product-law induction (which must rewrite under mul). Reuses "
        "CommuteEdge.-\N{DOUBLE-STRUCK CAPITAL Q}-cong",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Setoid.agda", "mul-cong"),
    },
    {
        "sym": "⊙.morton.unit",
        "desc": "cocycle NORMALIZATION + CD identity: the zero family (mul-zeroˡ/ʳ, add/sub-zero) + "
        "mul-oneˡ/ʳ (CayleyDickson.Setoid: 1 is a two-sided mul identity) + prod-unitˡ/ʳ "
        "(CayleyDickson.Cocycle: e₀·eᵢ ≈# eᵢ ≈# eᵢ·e₀, since e₀ = the all-false index = 1). "
        "The FIRST full case of the product law eᵢ·eⱼ ≈# ε·e_{i⊕j}: when an index is 0, "
        "i⊕0=i and ε(i,0)=ε(0,i)=+1. NO neg-distribution needed",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "prod-unitʳ"),
    },
    {
        "sym": "⊙.morton.neg",
        "desc": "the NEG-DISTRIBUTION family (CayleyDickson.Setoid): neg-invol "
        "(\N{MINUS SIGN}\N{MINUS SIGN}x=x), conj-neg (conj∘neg=neg∘conj), neg-add "
        "(\N{MINUS SIGN}(x+y)=\N{MINUS SIGN}x+\N{MINUS SIGN}y), sub-neg, and mul-negˡ/ʳ (mul "
        "distributes negation through either factor, mutually via the doubling formula). The "
        "last foundation cluster — needed to push conj-on-basis's ± sign through the product "
        "in the imaginary\N{MULTIPLICATION SIGN}imaginary cases. \N{DOUBLE-STRUCK CAPITAL Q} "
        "bases via mk\N{DOUBLE-STRUCK CAPITAL Q}-pattern + "
        "≈\N{DOUBLE-STRUCK CAPITAL Q}-from-≡(subst)",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Setoid.agda", "mul-negʳ"),
    },
    {
        "sym": "⊙.morton.prod",
        "desc": "THE THEOREM: prod (CayleyDickson.Cocycle) — eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j} ∀n by induction "
        "on the level; each of the 4 doubling cases reduces via mul-zero (off-diagonal "
        "halves) + conj-on-basis + mul-neg (push the ± sign) + the IH to the signed XOR "
        "basis unit. Plus the explicit ε, ⊕-comm (XOR commutes), and the sgn-threading "
        "helpers (sgn-cons/zero#/cong, mul-sgn-l/r, neg-sgn, sgn-xor). Capstone of ⊙.morton",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Cocycle.agda", "prod"),
    },
    {
        "sym": "⊙.grade",
        "desc": "✅ C4 + C2 PROVED (CayleyDickson.Grade). The F₂ⁿ index carries TWO gradings: the "
        "LENGTH (Wedge.VecGraded.vec-graded Bool — the generic length-grading at Bool, "
        "reused not reinvented; = the ambient F₂ⁿ dimension) and POPCOUNT (the ANF degree = "
        "Hamming weight) — they don't coincide, both grade the one index. C4: the two "
        "index-PRODUCTS (CD/Morton XOR vs ANF/Reed-Muller OR-union) bridged by "
        "\N{LOGICAL OR}-anf (OR=XOR⊕AND). C2: popcount-or-and "
        "(popcount(i\N{LOGICAL OR}j)+popcount(i∧j)=popcount i+popcount j) — the cancellation "
        "defect IS the overlap popcount(i∧j), zero iff disjoint supports; graded index "
        "retains it, only the ungraded popcount projection loses it. C7 grounded by "
        "⊙.morton.prod",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Grade.agda", "popcount-or-and"),
    },
    {
        "sym": "⊙.c8",
        "desc": "✅ GROUNDED (framing, CayleyDickson.Curve) — the Morton/Hilbert curve-crossover as a "
        "tropical (cost) instance. morton = the Z-order linearization (F₂ⁿ index → rank, "
        "reusing Grade.bit); crossover IS the tropical min ⊓ (NatInf, the cost gauge ⊙.c6's "
        "Contraction reads) — the chosen curve is the argmin, the boundary is where it flips "
        "(concrete Morton-cheaper-low / Hilbert-wins-high). Full Hilbert construction "
        "(recursive quadrant reflection) is a separate build; only the SELECTION mechanism "
        "is C8's content",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Curve.agda", "crossover"),
    },
    {
        "sym": "⊙.hilbert",
        "desc": "✅ the HILBERT curve built — the last ⊙.measure instance, de-degenerating crossover "
        "(CayleyDickson.Curve). gray = the binary-reflected (Gray) code = the 1D "
        "Hilbert/reflected-binary curve (recursive reflection, b_i↦b_i⊕b_{i+1}); "
        "gray-roundtrip proves it's a bijection (faithful linearization like morton). "
        "LOCALITY is now real: morton-jump≡2 vs gray-jump≡1 on the 01→10 step (popcount of "
        "the actual curve steps), and crossover-gray-wins feeds those to the tropical min "
        "(Gray wins) — costs no longer hand-picked fin. Full 2D Hilbert (quadrant ROTATION) "
        "is the remaining refinement",
        "done": ("defines", "Substrate/Algebra/CayleyDickson/Curve.agda", "gray-roundtrip"),
    },
    {
        "sym": "⊙.hilbert2d",
        "desc": "✅ the full 2D HILBERT curve (reflection + ROTATION) — CayleyDickson.Hilbert2D, "
        "resolving the Gray=Hilbert wedge (gray = 1D reflection-only corner; this adds the "
        "quadrant rotation 2D locality needs). hilbert : \N{DOUBLE-STRUCK CAPITAL N}→List"
        "(\N{DOUBLE-STRUCK CAPITAL N}\N{MULTIPLICATION SIGN}\N{DOUBLE-STRUCK CAPITAL N}), "
        "recursive: 4 transformed copies/level (A transpose + D anti-diagonal reflect = the "
        "rotations, B/C translate). hilbert-1 ≡ the U tetromino; hilbert-2-continuous "
        "(maxjump ≡ 1 across ALL quadrant seams) validates the construction by refl — a "
        "wrong rotation would jump >1. ∀n continuity (inductive entry/exit-adjacency "
        "invariant) is the remaining refinement",
        "done": (
            "defines",
            "Substrate/Algebra/CayleyDickson/Hilbert2D.agda",
            "hilbert-2-continuous",
        ),
    },
    {
        "sym": "⊙.hilbert∀n",
        "desc": "✅ FULL ∀n continuity (CayleyDickson.Hilbert2DContinuous.hilbert-continuous): the 2D "
        "Hilbert curve is continuous (consecutive points Manhattan-adjacent, Cont) at EVERY "
        "order n, generalizing the concrete hilbert-2-continuous. Built: the entry/exit "
        "recursion (hilbert n runs (0,0)→(2ⁿ\N{MINUS SIGN}1,0)); the 4 quadrant transforms "
        "named + proved Manhattan ISOMETRIES (D's reflection via bounded-monus "
        "(k∸a)∸(k∸b)≡b∸a + the coordinate-BOUND invariant); Cont-app gluing the 4 isometric "
        "sub-curves with the 3 seams = 1 (from entry/exit). ~150 lines, all the deferred "
        "pieces from .entry now discharged",
        "done": (
            "defines",
            "Substrate/Algebra/CayleyDickson/Hilbert2DContinuous.agda",
            "hilbert-continuous",
        ),
    },
    {
        "sym": "⊙.c5",
        "desc": "✅ C5 PROVED (Wedge.Wedderburn) — nilpotent-not-annihilating ⟹ no dead-end. "
        "Annihilator (kills EVERY product, Wedge.Mul) separated from Nilpotent (kills only "
        "own powers): e₁₂ is a nonzero nilpotent (e₁₂²="
        "\N{MATHEMATICAL BOLD DIGIT ZERO}) yet e₁₂-not-annihilating (e₁₂·e₂₁=e₁₁≠"
        "\N{MATHEMATICAL BOLD DIGIT ZERO} — the corner glues back to a live idempotent). The "
        "obstruction is graded by degree, never a collapse; ties #1 (the wedge correction "
        "always survives)",
        "done": ("defines", "Substrate/Algebra/Wedge/Wedderburn.agda", "e₁₂-not-annihilating"),
    },
    {
        "sym": "⊙.c5b",
        "desc": "✅ the GRADED-COST half of #5 + ⊙.measure instance (Wedge.CrossMulGraded) — a "
        "CrossMix Two→M₂ whose cross-term nilpotency degree GENUINELY VARIES, replacing "
        "coherent-everywhere's all-degree-0 (two-mul square-zero). Embeds ε↦e₁₁ (left)/e₁₂ "
        "(right): coherent-graded gives (ε,ε)↦e₁₁·e₁₂=e₁₂ degree-2 (n=1) vs others↦"
        "\N{MATHEMATICAL BOLD DIGIT ZERO} degree-0 (n=0); cross-εε-not-clean proves the "
        "(ε,ε) term is a NONZERO obstruction (can't be witnessed clean). M₂ is the 'richer "
        "common carrier' CrossMul's comment flagged as needed",
        "done": ("defines", "Substrate/Algebra/Wedge/CrossMulGraded.agda", "coherent-graded"),
    },
    {
        "sym": "⊙",
        "desc": "commuting-sphere: the 8 prove-or-correct GF(2)-VM conjectures (authoritative ledger "
        "+ live index: Algebra.Wedge.Sphere; prose: scratch/commuting_sphere.md). ALL 8 now "
        "machine-checked & live-referenced: #1 KEYSTONE r<b=Free⊣Forgetful ✅ "
        "Wedge.Adjunction [.c1] · #2 graded-GF(2) non-cancelling ✅ CayleyDickson.Grade "
        "[.grade] · #3 Morton≅CD cocycle ✅ Cocycle.prod [.morton] · #4 two gradings ✅ Grade "
        "[.grade] · #5 nilpotent≠annihilating ✅ Wedderburn [.c5] · #6 semiring-VM gauge ✅ "
        "Semiring.Contraction [.c6] · #7 edge=grade=cocycle ✅ grounded by prod · #8 "
        "Morton/Hilbert crossover ✅ Curve [.c8] + Gray [.hilbert] + 2D-rotation "
        "[.hilbert2d]. PLUS the ⊙.measure family: associator/dε [.assoc], graded-degree "
        "CrossMix [.c5b], pentagon dε-closed [.pentagon]. The arc is CLOSED end-to-end; "
        "remaining = DEEP refinements (not conjectures): generic d²=0 ∀φ, ∀n Hilbert "
        "continuity",
        "done": (
            "all",
            [
                ("defines", "Substrate/Algebra/Wedge/Sphere.agda", "cell-cocycle"),
                ("defines", "Substrate/Algebra/Wedge/Sphere.agda", "cell-pentagon"),
            ],
        ),
    },
    {
        "sym": "⊙.cd",
        "desc": "commuting-sphere C3 prerequisite: Cayley-Dickson IN the substrate (the "
        "doubling-with-involution generator) — the ledger's 'CD absent, MUST-BUILD' is "
        "STALE; built at Algebra.CayleyDickson (\N{DOUBLE-STRUCK CAPITAL C}/"
        "\N{DOUBLE-STRUCK CAPITAL H}/\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL O}/"
        "\N{MATHEMATICAL DOUBLE-STRUCK CAPITAL S} tower over "
        "\N{DOUBLE-STRUCK CAPITAL Q})",
        "done": ("exists", "agda/Substrate/Algebra/CayleyDickson.agda"),
    },
    {
        "sym": "⊙.tropical",
        "desc": "commuting-sphere C5 prerequisite: the tropical (min-plus) cost gauge — BUILT as "
        "Semiring.Instances.tropical-semiring (\N{DOUBLE-STRUCK CAPITAL N}∞ min-plus); was a "
        "false-positive grep on Sphere prose, repointed at the artifact",
        "done": ("grep", "tropical", "agda/Substrate/Algebra/Wedge/Sphere.agda"),
    },
]
