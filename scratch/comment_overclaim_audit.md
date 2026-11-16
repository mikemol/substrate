# Comment-overclaim audit + proof-in-code plan (PROPOSAL)

> **CURRENT STATE (2026-06-18, authoritative — supersedes all "HELD" / "UNCOMMITTED" /
> "Nothing committed yet" status lines BELOW, which are dated WAL history, not current):**
> **6 streams △ Λ Β Ι Φ Π DONE, committed, ff'd to `main`, ⊨₁/⊨₂-verified.** Commits: `0e36a57` Λ ·
> `1eac16c` △ · `59ba727` Β · `1000293` Ι · `90b81c7` Φ · `109f171` Π · `016a3de` Ε(b′). main ==
> origin/main == `016a3de` (ALL PUSHED, CI-green 1500/1500). REMAINING: β̌, ŝ, Ε(b/c/d).
> POLICY (user): commit on main (no feature branches); main is CI-gated; AUTO-PUSH on green CI.
> Live status lives in `memory/project_overclaim_witness_arc.md`; this file is the WAL/design record.

Status: **proposal, not a claim** (per `memory/discipline/feedback_spec_is_proposal_not_claim.md`).
Nothing below is established until a `--safe` witness lands. Each row is a hypothesis about a
gap between a comment and what the slice proves; the proof-plan column is what *would* discharge it.

Governing policy: [`docs/governance/agda_comment_hygiene.md`](../docs/governance/agda_comment_hygiene.md).

Method: 6 parallel agents partitioned the 1496-file `agda/Substrate/` corpus (~1369 strong-signal
comment lines), each reporting only gaps it could pin precisely (comment-claims vs code-proves).
The 4 highest-impact findings (T1.1, T1.2, T1.3, T2.1) were re-verified by hand against source.

Corpus is **well-disciplined overall** — the vast majority of "every/unique/canonical/for-all"
comments are genuinely backed, exhaustively case-covered, or already marked prose/deferred. ~30
genuine gaps survived adversarial scrutiny, concentrated in `Category/`.

---

## Tier 1 — WRONG or self-contradictory (not merely "stronger than proved"). Fix first.

| ID | File:line | Comment claims | Reality | Fix |
|----|-----------|----------------|---------|-----|
| **T1.1** | `Category/TensorProduct/Antisymmetric.agda:70-71,107-109` | `antisymmetrize ∘ antisymmetrize = antisymmetrize` (idempotent projection onto Λ²V at F₂) | **FALSE at char 2.** `antisymmetrize T = T +T transpose T`, so `antisymmetrize² T = (T+Tᵀ)+(T+Tᵀ)ᵀ = T+Tᵀ+Tᵀ+T = 0`. The map is **square-zero (nilpotent)**, not idempotent — and gives `0` even on the "antisymmetric subspace", not identity. No lemma backs either form. | Delete the false bullets; replace with the *true* lemma `antisymmetrize-square-zero : (T) → antisymmetrize (antisymmetrize T) ≡ zeroT`. Prove via `+T` self-cancellation at F₂ (`x +F x ≡ 0`) + `transpose`-involution. **MEDIUM.** |
| **T1.2** | `Category/ChainDecomposition.agda:131` | "The Agda **postulate** is supported by the codec's exhaustive 24-element check (every g ∈ S₄ has a **unique** chain)." | No `postulate` exists in the file (line 117 of the *same file* says "forbids postulates"). `ChainDecomposition` is data-only; no uniqueness lemma; no S₄/24-element check in Agda. | Delete "The Agda postulate is supported by…"; drop "unique" (or cite the external `scratch/eliza/.../sylow_chain.py` check as *prose*, not as an Agda postulate). **SMALL.** |
| **T1.3** | `Groups/Subgroup.agda:124-126` | "Stab(X) … is **NOT normal** (only V₄-image is normal in S₄)." | Unbacked negative claim — the canonical `¬P`-by-absence shape the substrate rejects (`feedback_reject_lem_in_substrate`). File proves only that `Stab-Subgroup` is a subgroup and that V₄-image *is* normal. No `Stab-not-normal : … → ⊥`. | Either prove `Stab-not-normal : (X : Axis) → IsNormal (Stab X) → ⊥` via one explicit conjugation counterexample (decidable by `refl` on `Permutation Axis`) — **MEDIUM**; or soften to prose "(unlike V₄-image, Stab(X) is not normal — not proved here)". **SMALL.** |

## Tier 2 — universal/uniqueness/bijection claims, PROVABLE in-slice. Strongest first.

| ID | File:line | Claim | Code proves | Proof plan | Size |
|----|-----------|-------|-------------|-----------|------|
| **T2.1** | `Category/Equalizer.agda:80,105-106` | "factors **uniquely**"; commutes-lemma mislabeled "the uniqueness half" (it's the *existence* half) | `equalizer-factor` + `…-commutes ≡ refl` (commutation only) | Add `equalizer-factor-unique : (k : Z → Equalizer-Of f g) → ((z) → equalizer-incl (k z) ≡ h z) → (z) → k z ≡ equalizer-factor h h-eq z`. Σ-ext over the `IsEqualised` prop. Fix the line-105 label. | MEDIUM |
| **T2.2** | `Category/Pullback.agda:13,106-107` | "factors **uniquely** through the pullback" | existence + π₁/π₂ commutation (`refl`) | Add `pullback-factor-unique : (k) → (…π₁…) → (…π₂…) → (z) → k z ≡ pullback-factor h₁ h₂ sq z`. | MEDIUM |
| **T2.3** | `Algebra/Involution.agda:11-12` | involution is a "bijection / self-inverse iso" | `invol-injective` only | Add `invol-surjective` (preimage of `y` is `f y`, one line from `invol`) → bundle `Bijection`/`Iso`. | SMALL |
| **T2.4** | `Algebra/Abelian/Z6JointGenViaProduct.agda:10` | "factors **UNIQUELY** as n = a·g₁+b·g₂" | reconstruction/soundness only (`represent-Z6-correct`) | Add `represent-Z6-unique : (g)(r₁ r₂) → eval r₁ ≡ g → eval r₂ ≡ g → r₁ ≡ r₂` (CRT bijectivity). | MEDIUM |
| **T2.5** | `Algebra/Abelian/Z6-AsChainDecomp.agda:8` | "**every** n admits a **unique** chain decomp" | record + specific-element constructors; no totality, no uniqueness | Add `chain-total : (n : Z6) → Z6ChainData n` and `chain-unique : (n)(c₁ c₂) → c₁ ≡ c₂`. | MEDIUM |
| **T2.6** | `WitnessTower/SupportGrading.agda:57` | "support 1 is impossible at **every** rung" | only `support-1-impossible-{3,4} ≡ refl` (n=3,4) | Add `support-1-impossible : (n) → by-support n 1 ≡ 0` (no permutation moves exactly one point). | MEDIUM |
| **T2.7** | `Algebra/F2/Vector/Universal.agda:140-142` | basis decomp is "**unique** linear combination" | `basis-decomp` = existence only | Add `basis-coeff-unique : (v)(c) → v ≡ sum (λ i → c i *ₛ basis i) → (i) → c i ≡ lookup v i` (via `lookup-sum` already in file). | SMALL/MED |
| **T2.8** | `Category/AutomorphismGroup.agda:68` | "group axioms hold pointwise via apply" (as element-level laws) | only pointwise-on-`apply` equations | Add `_≈Aut_` (carrier-equiv) + `compose-assoc`/`-idˡ/ʳ`/`-invˡ/ʳ`; or soften to "pointwise on `apply`". | MEDIUM |

## Tier 3 — PROSE-UNMARKED: mark as prose, or build the named machinery. (selection)

Equivalence / adjunction / UP framings asserted as fact over existence-only or placeholder code:

- `Category/CartanRootEquivalence.agda:4-6,33-34` — "**equivalence of categories** … isomorphism nat-trans". Fields are plain `NaturalTransformation` (no invertibility). Also propagated in `OrphanAudit.agda:22`. → rename `FG⇒Id`/`GF⇒Id`, drop `≅`, retitle `…-EquivalenceCandidate`; or build a real `NaturalIsomorphism`.
- `Category/HC/MacLane.agda:8-13` — "Mac Lane coherence … pentagon+triangle IMPLY this". Body is the trivial `⊤`-UPArrow placeholder. → mark PLACEHOLDER.
- `Category/YonedaEmbedding.agda:5` — "**Fully faithful** by Yoneda lemma". `y` is a module *parameter*; nothing Yoneda proved. → mark prose, or build `よ` + `yoneda-full`/`-faithful`.
- `Category/UniversalProperty/Backed.agda:9,17` + `Registry.agda:4-13` — "backing a **universal property**" / "REALLY has a UP". `BackedUP` has no uniqueness field → it certifies a *non-vacuous solver* (existence), not universality. → add `solve-unique` field (then ~several of these upgrade to backed), or reword "solving bridge".
- `Category/Adjunction.agda:77` + `GaloisAdjunction/AsAdjunction.agda:5` — "satisfying the **triangle identities**" / "**full** … + triangle identities". No triangle field/lemma (same files list them deferred). → drop "full"/"+ triangle identities", or add the two triangle lemmas.
- `Category/TensorProduct.agda:5` + `TensorProduct/Bilinearity.agda:5` — "packages the **universal property** … factoring uniquely" / "the **UNIVERSAL** bilinear map". Only bilinearity of `pair` proved; factorization/uniqueness deferred (N-3/N-5). → soften to "bilinear (prerequisite for universality)".
- `Category/Interop.agda:1`, `ConjugationCoalgebra/CharacterOrthogonality.agda:21-23`, `AutomorphismGroup/AsFunctor.agda:9-12,22-26`, `WedgeProduct.agda:14`, `ExteriorAlgebra.agda:8,62-66`, `AbelianPFG.agda:14-19`, `Coequalizer.agda:70-71`, `UniversalProperty/Quotient.agda:10-17` — UP/functorial/adjoint/factor framings over signatures-only or parameters. → prose markers (each SMALL).
- `Algebra/Q/AsField.agda:116` — "F₁ + F₂ as Field instances are **complete TODAY**". F₂ is a Field (M9); F₁ is Monoid-grade. → "F₂ lands as a Field; F₁ is the trivial-Monoid stage".
- `Algebra/GL3F2.agda:9` ("≅ PSL(2,7), simple"), `GL3F2/MultiRouteEquivariance.agda:26` & `AsChainDecomp.agda:12` (joint-generation / per-element existence) — classical facts not formalized in-slice. → prose markers.
- `Algebra/Wedge/Certified.agda:15,53` — "the **canonical** instance". → "natural/standard instance" (no UP/terminality proved).
- `Groups/FreeCyclic-Coxeter-GradedMonoid.agda:77` — "**faithful** representation of (ℕ,+,0)". Only the hom (`length-distrib`) proved here; injectivity lives in `…-Length`. → cite provenance.
- `Probability/Simplex.agda:4-6,13,64` — distribution defined "such that summing all values gives 1", but `DiscreteDistribution` has only `pmf`, no sum-to-one field. → add `sum-p` + `sum-to-one` field, or soften set-builder to an instance-side obligation.
- `Algebra/F2/V4LagrangeInstance.agda:131` — "translation action … is **free** (orbit = F₂²)" + "Aut(V₄)=GL(2,F₂)". → prove freeness (4×4 case-split, SMALL) / mark Aut claim prose.

Also a STALE under-claim (out of target class, but misleading): `Groups/V4-Embedding.agda:167-172`
points at a nonexistent `…Normality` module "that postulates it (not --safe)"; normality is now
proved constructively under `--safe` in `Groups/S4-Iso/V4Normal.agda`. → fix the pointer.

---

## Reusable machinery (build once, discharges many)

The Category gaps share three missing primitives. Building these first collapses ~7 Tier-2/3 items:

1. **`equalizer/pullback/interop/CRT factor-unique`** — the uniqueness half of the universal
   property, currently everywhere replaced by the commutation lemma. A shared
   `IsUnique-mediating` helper over Σ-types would serve T2.1, T2.2, Interop, Backed.
2. **`solve-unique` field on `BackedUP`** — turns the Registry "REALLY has a UP" gate from
   existence-of-solver into genuine universality; upgrades Backed/Registry/Interop.
3. **`NaturalIsomorphism` record** (nat-trans + pointwise inverse + round-trips) — backs
   CartanRootEquivalence "equivalence of categories" and any future equivalence claim.

Plus a smaller one: **carrier-`≈` on automorphism elements** → element-level group laws (T2.8 + AsFunctor).

## Directive (user, 2026-06-18): PROVE EVERYTHING
When execution begins, the stance is **prove the claim in code, not soften the comment** — even
for the LARGE items. Softening is only a fallback for a claim that proves genuinely out of scope
(and that itself must be justified, not assumed — `feedback_test_the_wall_before_declaring_it`).
This promotes the Tier-3 items from "mark prose" to "build the machinery + prove": i.e. build
`NaturalIsomorphism` and prove CartanRootEquivalence is a real equivalence; build the Yoneda
embedding `よ` and prove `yoneda-full`/`-faithful`; add carrier-`≈` + element-level Aut laws;
construct the MacLane coherence / TensorProduct factorization rather than placeholder them.
T1.1 still becomes the *corrected* lemma (`antisymmetrize-square-zero`) — proving the truth, not
the false "idempotent" prose. T1.3 becomes the `Stab-not-normal` counterexample proof.

## Suggested sequencing (prove-everything)
1. **Tier 1** (3 items) — wrong/contradictory, highest risk; T1.1 is a real false theorem-in-prose.
   Prove corrected statements (square-zero; remove phantom postulate + prove/cite the real check;
   `Stab-not-normal` counterexample).
2. **Machinery #1 + #2** (`factor-unique` helper, `BackedUP.solve-unique`) then the Tier-2 uniqueness
   lemmas (T2.1, T2.2, T2.4, T2.5, T2.6, T2.7).
3. **Tier 2** standalone (T2.3 Involution bijection — trivial; T2.8 Aut element-level laws via `≈Aut`).
4. **Machinery #3** (`NaturalIsomorphism`) + the heavy Tier-3 proofs (Yoneda full-faithfulness,
   MacLane coherence, TensorProduct universal-bilinear factorization, GL3F2≅PSL/joint-generation,
   Simplex sum-to-one, V4Lagrange freeness/Aut). Soften ONLY where a proof is shown out of scope.

## Status: HELD at audit (user: "Just the audit"). Execution awaits go-ahead. [SUPERSEDED — see top banner: all 5 streams since executed + verified]

---

# GROUNDING (2026-06-18): the "machinery" mostly ALREADY EXISTS — reroute, don't reinvent

User direction: ground in the term algebra + wedge apparatus + JEA + similarity scripts BEFORE
building machinery. Did so. Result: of the four "reusable primitives" the audit proposed building,
**only `NaturalIsomorphism` is genuinely new — and even it is a 2-field composition of existing
parts.** Everything else reroutes onto an established idiom. `never_discard_residue` applies: I was
about to re-derive residue that's already in the repo. Concrete reroutes:

| Audit "build" | Reroute → EXISTING apparatus | Why |
|---------------|------------------------------|-----|
| `factor-unique` for Equalizer T2.1 / Pullback T2.2 / Interop | **`LimitUP.mediate-unique`** (`Category/LimitUniversalProperty.agda:60`), OBSERVATIONAL/leg-by-leg | Equalizer = Cone(2,1), Pullback = Cone(3,1) per `project_cone_subsumes_equalizer_pullback`. Realize them as LimitUP instances (or copy its idiom) and inherit uniqueness. State at the **inclusion/projection (action) level** `incl (k z) ≡ incl (factor … z)` — NOT full `k z ≡ factor … z`, which needs proof-irrelevance of the `IsEqualised` field. That observational form is exactly how `Wedge/Monoidal.agda` HONEST SCOPE (lines 35-39) handles `--without-K`. So the agent's "needs IsEqualised to be a prop" worry dissolves. |
| `solve-unique` on `BackedUP` (Backed/Registry/Interop) | **`WedgeUP.wedge-unique` → `divmod-unique`** (`Nat/DivMod/Unique.agda:36`), BOUNDED-target idiom | Mediating-map uniqueness in this repo is only available for **bounded targets** (`r < suc b`); unbounded has no unique solution. `solve-unique` must carry the same bound, mirroring `wedge-unique`, not a generic uniqueness field. |
| `NaturalIsomorphism` for CartanRootEquivalence T3 | **GENUINELY NEW** — but = `NaturalTransformation` (`Category/NaturalTransformation.agda`) + pointwise `IsIso` (`Category/DeloopingGroup.agda`), modeled on `WedgeIso` (`Algebra/Wedge/Iso.agda`) | Confirmed absent. `TwoEquivalence`/`TwoNaturalTransformation` skeletons already anticipate it. A 2-field record (`nat-trans`, `(a) → IsIso D (components a)`), not a reinvention. |
| Build Mac Lane coherence for `Category/HC/MacLane.agda` (T3) | **`Algebra/Wedge/Monoidal.agda`** already proves pentagon + triangle + hexagon + naturality (all `refl`) for `⊗ᴰ` | Do NOT attempt the abstract Mac Lane theorem. Either honestly mark the `⊤`-placeholder, or instantiate concrete diagrams for a real monoidal structure following Monoidal.agda's pattern + its HONEST SCOPE note. |
| TensorProduct universal-bilinear factorization (T3) | **`FreeF2Module.ext-unique` / `linear-extensionality`** (`F2/Linear/Universal.agda:85`) basis-agreement idiom; `FreeLinearization` (`project_freelinearization_names_linear_from_images`) | "factors uniquely" follows the linear-from-images / extend-unique pattern already proven. |
| ChainDecomposition "unique chain" T1.2; Z6 uniqueness T2.4/T2.5 | **`split-Canonical` / `idem-Canonical`** (`Algebra/Quotient.agda:140,155`); CRT-combine is listed as a split-Canonical instance; `Quotient/CRT/*` exists | A unique canonical representative = the split idempotent of a retraction. Route the CRT/chain uniqueness through the existing Canonical apparatus, don't hand-roll injectivity. |
| T1.1 Antisymmetric `square-zero` | Just an **F₂ self-cancellation** arithmetic lemma (`x +F x ≡ 0`, already used in `FreeF2Module.ext-unique` via `⊕-self`) + transpose-involution | No machinery — a few lines. |
| T2.3 Involution bijection; T2.8 Aut element laws | `invol-surjective` one-liner → bundle existing `Bijection`/`_↔_`; Aut laws follow the pointwise-on-`apply` / setoid idiom | Small per-site, established shapes. |

**Net:** the audit's "Machinery #1 (factor-unique)" and "MacLane build" were going to reinvent
`mediate-unique` and `Monoidal.agda`. Machinery #2 (`solve-unique`) must be bounded-scoped to be
provable at all. Machinery #3 (`NaturalIsomorphism`) is the only real new build, and it's small.

## JEA context (why the term-algebra constraint is load-bearing)
JEA (`jea/`, syllabus `jea/evolution/00_SYLLABUS.md`) is the downstream consumer: roots → carrier →
generator → engine → control → **integrate** (rung 44 `jea_agda_dispatch`: an Agda-emitted term run
on the cooperative GPU evaluator, MODE chosen by the oracle). The Agda term-algebra (`UPTerm`, `eval`
= the Free⊣Forgetful fold, `foldUPTerm-unique`) is JEA's FRONT-END. Any new categorical machinery
must compose with the `eval`/term-fold structure (`Category/UniversalProperty/Eval.agda`) — that fold
is `ker eval`'s universal extension and what feeds the emitter. Don't add structure that can't be
emitted (cf. `project_agda_cubical_extraction_discipline`: extractable subset only).

## Tooling note (orphan)
`scripts/agda_similarity/` is now stale `.pyc`-only bytecode (source retired in b20a1d2, recoverable
via git). Live similarity instrument: `jea/metalanguage/jea_pysim.py` (+ `jea_agdai.py` for `.agdai`).
Use it (`--clusters --extract --skeleton`) to find shape-equivalent sites for any fix — e.g. all the
existence-only "universal property" placeholders, or every `factor`/`mediate` site — before editing.
Memory `feedback_similarity_not_grep` updated to match.

## Revised execution stance (prove-everything, grounded)
1. **Tier 1** — corrected lemmas (T1.1 square-zero arithmetic; T1.2 drop phantom postulate + route
   chain-uniqueness through `split-Canonical`; T1.3 `Stab-not-normal` counterexample).
2. **Equalizer/Pullback uniqueness (T2.1/T2.2)** — realize as `LimitUP` instances OR copy
   `mediate-unique`'s observational form; fix the Equalizer:105 "uniqueness half" mislabel.
3. **`solve-unique`** — add to `BackedUP` as a BOUNDED-target field (wedge-unique idiom); then
   Backed/Registry/Interop T3 upgrade.
4. **`NaturalIsomorphism`** (the one real new build) → fix CartanRootEquivalence + OrphanAudit:22.
5. **MacLane / TensorProduct / remaining T3** — route to `Monoidal.agda` / `linear-extensionality`;
   honestly mark only the genuinely-out-of-scope (each justified, per `test_the_wall_before_declaring_it`).
Run `jea_pysim --clusters` over the touched subtrees first to catch sibling sites.

---

# FORWARD MAP — the ⊢-arc (labeled streams) — 2026-06-18

Regrounding anchor (compaction-safe). WHERE WE ARE [SUPERSEDED — see top banner]: audit done + HELD; grounding done; reroute
mapped (most "machinery" already exists). NOW: forward streams labeled so they can be dispatched
by symbol. Meta-S₃ arc position: leaving **D-dominant** (planning/scoping) → entering **DRS-triple**
(execution). The whole arc is ONE operation — **⊢ witness-attachment** — recursively the common
structure of every either/or (build-vs-reuse, prove-vs-disclose, instance-vs-copy all collapse to
"emit the witness equation, or disclose its absence").

**Dispatch grammar:** specify a stream by its symbol (e.g. "run Λ", "Ω1 then Ι"). Each stream is one
"AI" (agent unit of work). `⊢` is the spine (not dispatchable — it's the invariant the rest instantiate).

| Sym | Label | Stream | Routes through (EXISTING apparatus) | Sites | Lattice region | Dep |
|-----|-------|--------|-------------------------------------|-------|----------------|-----|
| **⊢** | OC0 | **The Witness Spine** (meta-frame) | — every fix attaches a witness or discloses its absence | (all) | DBE meta-frame | — |
| **△** | OC1 | **Truth-correction** (claims that are FALSE/phantom, not just weak) | F₂ self-cancellation; `split-Canonical`; constructive negation | T1.1 antisymmetrize-square-zero, T1.2 phantom-postulate + chain-uniqueness, T1.3 `Stab-not-normal` | DRS-triple | none — **highest priority** |
| **Λ** | OC2 | **Mediating-uniqueness** (observational, leg-level) | `LimitUP.mediate-unique` (Equalizer=Cone(2,1), Pullback=Cone(3,1)) | T2.1 Equalizer, T2.2 Pullback, Interop; fix Equalizer:105 mislabel | RFS-dominant triple (≥3 share the shadow) | after **Ε** verify |
| **Β** | OC3 | **Bounded-solver uniqueness** | `wedge-unique → divmod-unique` (bounded-target idiom) | `solve-unique` on `BackedUP`, then Backed/Registry/Interop T3 upgrade | DRS-triple | after **Ε** verify |
| **Ι** | OC4 | **Iso / equivalence** — the ONE genuinely-new build | `NaturalTransformation` + pointwise `IsIso`, modeled on `WedgeIso` | build `NaturalIsomorphism`; fix CartanRootEquivalence + OrphanAudit:22; adjunction triangles; fill TwoEquivalence/TwoNaturalTransformation skeletons | DRS-triple, DBE-heavy | independent |
| **Φ** | OC5 | **Coherence / factorization** (sideways copy) | `Wedge/Monoidal.agda` (coherence); `linear-extensionality`/FreeLinearization (factorization) | MacLane placeholder, TensorProduct universal-bilinear, ExteriorAlgebra, WedgeProduct | DBE+S2G (#6 sideways grid projection) | independent |
| **Π** | OC6 | **Prose-disclosure residue** (survives the wall-test) | honest prose-mark, each justified per `test_the_wall_before_declaring_it` | GL3F2≅PSL simplicity, joint-generation, PontryaginDual, V4Lagrange Aut, … | S2G-dominant | LAST (residue after Λ/Β/Φ/Ι proof attempts) |
| **Ε** | OC7 | **Escalation / tooling / meta** (the standing prevention layer) | G9 binding-ladder; `jea_pysim` | (a) compile-verify ONE reroute before banking [G7]; (b) widen reuse-search trigger so it fires on "plan proposes new machinery" [G9]; (c) `jea_pysim --clusters` sweep before each edit; (d) clean stale `agda_similarity` `.pyc` | S2G + would-be hook | (a) GATES Λ,Β |

## Lattice classification (shadow-architecture)
- **△, Λ, Β, Ι** = triple-point (DRS) — substantive structural arcs (design + shadow + catalogue).
- **Φ** = dual-point #6 (DBE+S2G) — sideways grid projection: copy an existing row (Monoidal/linear-ext) into the Category cell. No RFS because the pattern already has its universal home.
- **Π** = single-point S2G — pure disclosure/cataloguing.
- **Ε** = single-point S2G now, **escalates to a hook/gate** (the G9 move: lift the reuse-search measure off the skippable memory layer).
- **Orbit-saturation check (discipline rule 6):** Λ's three sites (Equalizer/Pullback/Interop) are NOT free duplication — they are **orbit-elements** of the Cone generator at shapes (2,1)/(3,1)/(pair). So per the rule, the move is **route through the existing universal (`LimitUP`/Cone), resist extracting a wrapper-record.** `mediate-unique` IS the universal; do not build a `factor-unique` wrapper above it.

## Recommended order
**Ε(a)** verify one reroute compiles → then in parallel: **△** (independent, highest), **Ι** (independent new build), **Φ** (sideways copy). Then **Λ, Β** (gated by Ε). Then **Π** (residue). **Ε(b–d)** fold in as the prevention layer throughout.

## STATUS UPDATE 2026-06-18 — Ε(a) ✅ DONE, Λ/Β UNBLOCKED
**Ε(a) green:** `Category/Equalizer.agda` typechecks `--safe --without-K` (EXIT 0) with
`equalizer-factor-unique` (observational `mediate-unique` idiom) added + the :105 "uniqueness half"
mislabel fixed. Reroute VERIFIED — the observational form is provable & trivial, no `IsEqualised`
proof-irrelevance needed. **T2.1 effectively DONE (UNCOMMITTED).** Gotcha: pin `{f=f}{g=g}`
explicitly (higher-order `h-eq` won't solve the implicits; first compile failed UnsolvedMetas).
Λ/Β no longer gated. Nothing committed yet.

## Λ ✅ DONE 2026-06-18 (UNCOMMITTED — 3 modules green --safe --without-K)
- **T2.1 Equalizer** (via Ε(a)): `equalizer-factor-unique` + :105 mislabel fixed.
- **T2.2 Pullback**: `pullback-factor-unique-π₁/π₂` (leg-by-leg observational form) + N-3 header + line-13 doc fixed. EXIT 0.
- **Interop**: NOT the mediate-unique idiom (cone witness, no mediating `factor`). Fixed the title-line overclaim ("universal property of the PAIR" → "backed CONE over the PAIR"); terminality-among-cones DEFERRED WITH CAUSE (needs a BackedUP cone-morphism layer — a separate categorical build, not the trivial observational lemma). File already self-disclosed at lines 10-13. EXIT 0.
- All edits ADDITIVE (new lemmas + comments) → no downstream API breakage possible; full-build not needed.
- Confirms the orbit-saturation discipline: routed through the existing `mediate-unique` universal idiom, built NO `factor-unique` wrapper record.
NEXT unblocked: **Β** (solve-unique, bounded), **△** (independent, highest), **Ι** (new build).

## △ ✅ DONE 2026-06-18 (UNCOMMITTED — 4 modules green --safe --without-K)
RE-FRAMED per user: "reject LEM; when faced with an either/or, find the common structure
recursively." Each T1 either/or was NOT resolved by picking the true horn — it dissolved into the
common structure of which both horns are degenerate readings:
- **T1.1 Antisymmetric** (idempotent ⊻ nilpotent): proved `antisymmetrize-square : antisymmetrize² T ≡ antisymmetrize T +T antisymmetrize T` — the char-AGNOSTIC law `P² = P + P` (=2P). Idempotent = char≠2 reading (½P), `antisymmetrize-square-zero` = char-2 reading (this F₂ carrier). Did the Vec-rewriting the slice deferred; added generic `tabulate-cong`/`vec-ext` to `Foundation/Vec/Properties` (reusable matrix extensionality).
- **T1.3 Subgroup** (normal ⊻ not-normal — a `¬P`-by-absence, the LEM trap): proved `Stab-conj-equivariant : Stab X σ → Stab (applyₛ g X) ((g·σ)·g⁻¹)` — conjugation-equivariance, the positive common structure. "Normal" = its degenerate reading (axis-orbit trivial); S₄ moves axes so it's not — now GROUNDED, not asserted. Constructive ¬-witness recipe recorded (X=D, g=(D C), σ=(C S) → conjugate (D S) moves D) for a concrete-S₄ follow-on.
- **T1.2 ChainDecomposition** (postulate ⊻ no-postulate): common structure = WHERE the existence-witness lives. No Agda postulate (existence by INSTANCE, externally checked); "unique" dropped — contradicted by the file's own §1 (order is a chirality choice). Comment-only.
All edits ADDITIVE (new lemmas) or comment-only → no downstream API breakage.

## COMMITTED on branch feat/overclaim-witness-arc (off main, NOT pushed)
- `0e36a57` ⊢-Λ (Equalizer/Pullback/Interop) · `1eac16c` ⊢-△ (Antisymmetric/Subgroup/ChainDecomposition/Vec.Properties)
- `59ba727` ⊢-Β: built `Category/UniversalProperty/Unique.agda` — `WitnessUnique U Adm` (≤1 admissible witness; Adm = the BOUND = common structure under wedge-unique) + `wedge-witness-unique` (bounded exemplar) + `eq-witness-unique` (unconditional corner) + `solver-unique` (BackedUP existence ⊕ WitnessUnique ⟹ unique admissible solution). Backed/Registry prose: SOLVER/existence ≠ universality. COINDUCTIVE ESCAPE documented: Adm = finite/halting window, unbounded reading = `Final.ana-unique` (terminal-coalgebra UP via `Bisim._~_`), same WedgeCoalg per `WedgeBridge`. Git rigor: gate caught a stale Makefile (new module) → regenerated, NOT --no-verify.

- `1000293` ⊢-Ι: the one genuinely-new build. `Category/Iso.agda` (NEW: IsIso/IsGroupoid proper home + id-IsIso; DeloopingGroup re-exports → M40Groupoid unaffected) + `Category/NaturalIsomorphism.agda` (NEW: nat-trans pointwise-IsIso, model WedgeIso, + id) + CartanRootEquivalence witnesses/fields now NaturalIsomorphism (was bare nat-trans → not an equivalence) + OrphanAudit O8 annotated. 6 modules green. Continues Ω2. Git rigor: regen Makefile for 2 new modules.

- `90b81c7` ⊢-Φ (comment-only): delegate-to-existing. MacLane → marked placeholder honest + redirect to `Algebra.Wedge.Monoidal` (concrete ⊗ᴰ coherence). TensorProduct/Bilinearity → existence IS in `Algebra.F2.Linear.BilinearFromImages` (now cited); bilinearity = prerequisite not full UP. SCOPED follow-on: pair-factorization bridge + arity-2 `bilinear-extensionality` (TensorProduct N-3).

REMAINING: **Π** (prose-disclosure residue: GL3F2≅PSL/joint-gen, PontryaginDual, V4Lagrange Aut, adjunction-triangle items, …), **Ε(b–d)** (reuse-search trigger [G9] + jea_pysim sweep + stale agda_similarity .pyc cleanup). Optional builds: `bilinear-extensionality` (Φ tail), the concrete-S₄ `Stab-not-normal` witness (△ tail). scratch doc untracked.
