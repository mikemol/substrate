# ⟡jac-det-via-sppf — COMPACTION-SAFE ROOT (dense). Native Leibniz determinant + tightening co-apexes.

## STATE (one line)
MISSION DONE. Both halves of the Jacobian-conjecture counterexample F are machine-checked, the det by the tower's
OWN generic determinant. **HEAD `355c1d4`; 3 UNPUSHED (`937800d`·`be4324b`·`355c1d4`; user pushed through `5a71c14`),
all full-build-gated + amend-marked; the USER pushes.** Tracked tree CLEAN (only untracked `scratch/`).
WAIT-FOR-DIRECTION — every remaining ⟡ is optional/standing.

## DONE LEDGER (7 commits; each `--safe --without-K`, zero postulates/holes, full-build PASS)
- `8547454` **RUNG 2 ⟡jac-det-via-sppf** — `Algebra/Z/MonoCommMonoid`: `Mono = mono ℕ ℕ ℕ` is a `CommMonoid` (addM
  = componentwise +). The exponent triple IS already canonical (the free comm monoid on {x,y,z}).
- `fc61caa` **RUNG 3a ⟡jac-poly-normalize** — `Algebra/Z/MPolyNormalize(.Properties)`: `normalize` (sorted-insert,
  combine-on-equal-key, drop-zero) is a `Canonical` form; `coeff` is a homomorphism (`coeff-normalize`/`coeff-++`/
  `coeff-insertT`); `normalize-Canonical = idem-Canonical normalize normalize-idem`. DEF+`.Properties` split.
- `dcf9c73` **RUNG 3b ⟡jac-poly-semiring** — `Algebra/Z/MPolySemiring`: `NormPoly = Σ MPoly (isSortedB ≡ tt)` (h-prop
  via Hedberg 𝔹-UIP) IS a `Semiring`. `coeff-canonicity` (peel-the-min: two sorted polys w/ equal coeff-fns are ≡ ⇒
  coeff faithful); convolution linearity `*P-normalizeˡ`(insertT-surgery)/`*P-normalizeʳ`(shifted `c *ℤ coeff (m ∸ k)`);
  `*P` nose-associative. `ε₂ = normalize(kP -1)`, `ε₂-sq`.
- `5a71c14` **RUNG 3c ⟡jac-det-native** — `Algebra/Z/JacobianDetNative`: `detNative = det{3} JacMat` (tower's generic
  `LeibnizDet.Det.WithSign.det` over `NormPoly-Semiring`, sign spent as ⊗ε₂). Headline **`detNative-normal :
  proj₁ detNative ≡ normalize detJac` by refl** ⇒ `det-native-correct : (j) → coeffN j detNative ≡ coeff j detJac`.
  The machine's det IS the hand-written `detJac`.
- `937800d` **⟡normpoly-semiring-reuse-note** — pointer comment in `Semiring.Instances` (a re-export would CYCLE:
  MPolySemiring imports Instances for mk-monoid) naming `NormPoly-Semiring`'s home + confirming it's genuinely NEW
  (univariate Vec-backed Graded rings + F₂[x] differ). Bundled: dropped spurious `--guardedness` from all 4 jac poly
  modules (no coinduction — a `--guardedness` header must be truthful).
- `be4324b` **⟡jac-counterexample-capstone** — `Algebra/Q/JacobianCounterexample.IsJacobianCounterexample` conjoins
  HALF A (not-injective/ℚ: `C.collision₁/₂/₃` + `x-differs`) + HALF B **box-free** `norm-detJac-is-const :
  normalize detJac ≡ kP (-suc 1)` **by refl** (normalize enumerates the true support ⇒ full normal form = single −2
  term IS "det is the nonzero constant −2", strengthening box-bounded `residue-vanishes`).
- `355c1d4` **⟡normalize-via-coxeter** — `Algebra/Z/MPolyNormalizeCoxeter`: `normalize` IS an instance of the
  carrier-agnostic `Groups.Coxeter.Core` at `Word:=MPoly` (no List↔Word bridge). 3/4 obligations = RUNG 3a terms
  (normalize-sorted, normalize-fixed) + ++-assoc; new `normalize-distrib` = one `coeff-canonicity` argument.
  Inherits the Coxeter word-algebra on MPoly (`_·_`, `_≈_`, idem, higher-arity, clash).

## THE PROVEN RESULT (the counterexample)
F(x,y,z) = ( z(1+xy)³+y²(1+xy)(4+3xy) , y+3x(1+xy)²z+3xy²(4+3xy) , 2x−3x²y−x³z ). (i) NOT injective — F(0,0,−1/4) =
F(1,−3/2,13/2) = (−1/4,0,0), in ℚ (`Algebra.Q.JacobianCollision`). (ii) `det Jac F = −2`, a nonzero CONSTANT, in ℤ,
checked by the tower's generic Leibniz-over-S₃ determinant over a real `Semiring NormPoly`. Conjoined:
`Algebra.Q.JacobianCounterexample.jac-counterexample : IsJacobianCounterexample`.

## LIVE ⟡ ROSTER (specify by symbol; USER allocates)
- **⟡push** — 3-commit stack (`937800d`·`be4324b`·`355c1d4`; `8547454`…`5a71c14` already pushed), amend-marked; USER pushes (`git fetch` + ff). The one pending item.
- **⟡jac-encoding-bridge** — the ONE unbuilt rung: a machine-checked term identifying HALF A's curried-ℚ `f₁/f₂/f₃`
  with HALF B's ℤ `MPoly` `f₁/f₂/f₃` (an `evalℚ : MPoly → ℚ³ → ℚ` hom + `evalℚ fᵢᴹ ≈ℚ C.fᵢ`). Currently the capstone
  conjoins the two encodings BY CONSTRUCTION, not by a term. SATURATED SPEC ↓ (agent, mirror on return).
- **⟡free-comm-monoid-3gen** — OPTIONAL family-completion: the free comm monoid on 3 gens as a `Coxeter.Core`/
  `ListPresentation` instance (Gen=Fin 3, Canonical=sorted-word, insert=pure sorted-insert, NO combine/drop) —
  completing FreeCyclic[1 free] / V₄[2 torsion] / [3 free]. NEW content, NOT a jac co-apex. SATURATED SPEC ↓.
- **⟡pyrig-object-carrier** — the mission's live edge (what IS the pyast rig-cat's Set₀ object carrier). Untouched; do NOT force.

## THE INVARIANT (recursive either/or collapse — dense)
Every fork of this whole arc collapsed to ONE move: **the native/generic and the bespoke are the SAME object, wired
by a checkable term — co-apex, NEVER deletion.** detNative≡detJac (refl); normalize IS Coxeter.Core's normalizer;
NormPoly-Semiring is the reused Semiring; det=−2-constant is the normal-form singleton. "retire the bespoke?" →
NEVER: the bridge is the deliverable, the reference stays. ⟡mono-via-coxeter dissolved the SAME way inverted — the
co-apex already existed (`Mono-CommMonoid`), so the honest move was NOT to build (rebuild-avoid). Tightening-loop P1
realized as tight `refl` terms meeting pre-existing generics. [[reuse-search-before-feasibility-conclusions]],
[[read-structure-dont-rebuild]], [[universal-property-free]], [[collapse-keeps-the-orientation-residue]].

## KEY DISCIPLINES (protect; dense)
- **Probe-the-cheap-route-FIRST**: 3c's `det-native-correct` collapsed from an anticipated coeff-hom slog to a `refl`
  one-liner because the determinant's normal form is UNIQUE (3a Canonical) — tested before slogging. Same for the
  capstone's box-free det-constant.
- **coeff-as-faithful-semantics**: `coeff-canonicity` (in MPolySemiring, NOT MPolyNormalize.Properties) makes every
  Semiring/normalize law a coeff equation. It's the reusable extensionality lemma.
- **Core is carrier-agnostic**: `Coxeter.Core` (`Word:Set` abstract) plugs in any normalization-monoid with no
  carrier bridge; `ListPresentation` is Word-hardwired (use Core directly). `Algebra.Quotient.Coxeter` is redundant
  with `normalize-Canonical` (same Quotient).
- **Correct-by-construction**: homed local `_∸_` to Foundation.Nat (not exempt); dropped spurious `--guardedness`
  at source (a `--guardedness` header must mean coinductive participation); pointer-comment not a cyclic re-export.
- **⟡mono-via-coxeter dissolved (do NOT re-try)**: `Mono = mono ℕ³` is already canonical (`Mono-CommMonoid` homes it
  in `Category.CommutativeMonoid`); nothing to bridge to (no `FreeCommMonoid`/`Word (Fin 3)`/`Multiset` in-tree);
  V₄ is NOT the free-comm-monoid 2-gen (it has torsion A²=B²=ε; free is ℕ²). A Mono re-representation = a rebuild.
- **⚑ REUSE-SEARCH-THE-TOWER'S-STRUCTURE, not a same-shape sibling (the §SAT-B miss, user-caught 2026-07-22)**: I
  framed ⟡free-comm-monoid-3gen as a horizontal family-completion ("mirror V₄-Coxeter, build a Gen3 instance") — a
  BUILD, inherited from an agent's "separate new artifact" note — instead of running the reuse-search on the STRUCTURAL
  question ("what IS the free comm monoid on n gens here?"). The tower ALREADY generalizes the Sₙ/sorting side:
  `coxeter-complete` (∀-n), `LehmerPath ≅ Perm`. Free comm monoid = permutohedron/type-A Coxeter (commutativity =
  sorting), NOT the associahedron (associativity/bracketing; the tower realizes the hexagon+distributor, no non-trivial
  Stasheff cell). SHARPER RULE than the standing memories: before framing an agent to BUILD a "new instance / complete
  a family", run the reuse-search on the structural question FIRST — does the tower already generalize this? — and treat
  any inherited "separate new artifact" framing as a HYPOTHESIS, not a premise (an agent's build-framed prompt fans out
  and AMPLIFIES the miss). Widens [[feedback_reuse_search_carrier_shape]] + [[feedback_route_through_witness_tower]] +
  [[feedback_plan_notes_are_hypotheses]]; the un-banked delta = "fires on a framing inherited THROUGH a prior agent."
  → ⟡memory-reuse-search-before-agent-build-framing (save when the user confirms).

## SATURATION — RETURNED (2 read-only agents, 2026-07-22; both turnkey specs mirrored below → §SAT-A / §SAT-B). Both MEDIUM, buildable, `--safe --without-K`; neither is on the critical path (mission done). Implement turnkey myself when allocated.

## §SAT-A (⟡jac-encoding-bridge) — SATURATED (MEDIUM, worth building; home `Algebra/Q/JacobianEncodingBridge.agda`)
PRESENCE: MPoly→ℚ eval **ABSENT** (grep `eval`/`⟦_⟧`/fold over Mono/Term/MPoly — none; the SPPF `inside` is over SPPF
not MPoly). ℤ→ℚ **PRESENT** `Algebra/Q/Embeddings.agda:39` (`ℤ→ℚ z = mkℚ z 0`). `_+ℚ_`/`_*ℚ_` present; **no ℚ power**
(need a local `powℚ`). All ℚ ring laws over `≈ℚ` present + complete: `Q/Properties/Field.agda` (+ℚ/*ℚ assoc/comm/
identity/`distribˡ:154`/`distribʳ:201`/zero-absorb), congruence `Q/Properties/Congruence.agda:33,43`, setoid `Q/Equiv.agda:44-50`.
- **evalℚ (cheapest)**: `powℚ x zero=1ℚ; powℚ x (suc n)=x *ℚ powℚ x n` (new). `evalT x y z (term (mono a b c) k) =
  ℤ→ℚ k *ℚ (powℚ x a *ℚ (powℚ y b *ℚ powℚ z c))`. `evalℚ x y z [] = 0ℚ; evalℚ x y z (t∷p) = evalT … t +ℚ evalℚ … p`.
- **THE PROOF is NOT refl/structural**: `f₁ᴹ` is EAGERLY DISTRIBUTED into a flat monomial list (`*P` = scaleT/++),
  `C.f₁` is the FACTORED tree; equal only by genuine ring algebra, up to `≈ℚ` (ℚ unnormalized). Route: prove `evalℚ`
  is a `+P`/`*P`→`+ℚ`/`*ℚ` HOM up to `≈ℚ`, then the two skeletons rewrite term-by-term.
- **Lemmas** (all provable, support all in-tree): `ℤ→ℚ-*ℚ-hom : ℤ→ℚ (c *ℤ d) ≈ℚ ℤ→ℚ c *ℚ ℤ→ℚ d` (NEW, small) ·
  `powℚ-+ : powℚ x (a + b) ≈ℚ powℚ x a *ℚ powℚ x b` (NEW) · `evalT-mulT` (via those + reshuffle) · `evalℚ-+P-hom`
  (list induction + +ℚ-assoc/identity/cong) · `evalℚ-scaleT-hom` (distribˡ + *ℚ-assoc) · `evalℚ-*P-hom` (induction +
  distribʳ) · generators X↦x/Y↦y/Z₁↦z/kP k↦ℤ→ℚ k/𝟙P↦1ℚ (+ `u`/`v` exported at JacobianResidue:178-180 → `gen-u`/`gen-v`
  shorten the chains). `f₃` also needs `a -ℚ b ≈ℚ a +ℚ (-ℚ b)` (Q/Sub) + `ℤ→ℚ (-suc n)`.
- **Deliverable**: `bridge₁/₂/₃ : (x y z : ℚ) → evalℚ x y z R.fᵢ ≈ℚ C.fᵢ x y z` — each a fixed `≈ℚ-trans` chain walking
  the component's `+P`/`*P` skeleton. Lean on MPoly `*P` structural lemmas `scaleT-++`/`scaleT-*P`/`*P-++-distˡ`
  (`MPolySemiring.agda:101-133`). ~6 hom lemmas + 2 arithmetic; MEDIUM, self-contained, `--safe --without-K`. Closes
  the capstone's flagged single-object-identification gap.

## §SAT-B (⟡free-comm-monoid-3gen) — ⚑ RE-AIMED (USER, 2026-07-22): NOT associahedra; route through the tower's Sₙ normalizer, don't hand-roll Gen3.
The free comm monoid is COMMUTATIVITY (sorting) ⇒ the PERMUTOHEDRON / type-A Coxeter (Sₙ) side, NOT the ASSOCIAHEDRON
(associativity/bracketing/pentagon — a different polytope + coherence). The tower's named higher-coherence is the
symmetric-monoidal HEXAGON + distributor (`OrientationHexagon`/`OrientationDistributorCoherence`), no associahedron
module. (The old "pentagon strict / Fano S(2,3,7), not Stasheff" note cited `scripts/enumerate_associahedra.py` which is
GONE — UNVERIFIED, do not assert. `associahedr/permutohedr/stasheff` is only MENTIONED in `Wedge/Simplicial.agda` +
`Wedge/Adjunction.agda`, unread.) THE CO-APEX the question surfaces: the tower ALREADY generalizes the Sₙ/Coxeter
(commutativity) side — `coxeter-complete : (σ : Perm n) → IsPerm σ → CoxGen σ` (∀-n,
`Wedge/OrientationRigCatPermCoxeterGeneral/Properties.agda:7`) + `LehmerPath ≅ Perm`. So the RIGHT build is to
instantiate the tower's general-n sorting machinery at the ABELIANIZED level, NOT a bespoke `Gen3` V₄-mirror.
⚑ HONESTY CAVEAT: Sₙ (Coxeter GROUP: torsion sᵢ²=1, each gen once) ≠ free comm MONOID (ℕⁿ: no torsion, unbounded
multiplicities). V₄-Coxeter is the GROUP; the free comm monoid is the torsion-free multiplicity-bearing "all-pairs-
commute trace monoid" — they share sorting, not identity. So the co-apex = "instantiate the tower's Sₙ-sorting at the
abelianized level," not "Sₙ = ℕⁿ". BELOW is the agent's original hand-rolled-Gen3 skeleton — SUPERSEDED by the re-aim,
kept only as the fallback if a standalone instance is ever wanted after checking the tower route.

## §SAT-B-fallback (⟡free-comm-monoid-3gen, hand-rolled — SUPERSEDED by the re-aim above; medium, ~120-160 lines; home `Groups/FreeCommMonoid3-Coxeter.agda`)
A THIRD structural point, not a copy: FreeCyclic (1 gen, cons already sorted, all refl) and V₄ (bounded words ≤2,
finite refl-table) are trivial; 3 free gens has UNBOUNDED sorted words ⇒ everything is RECURSIVE (insertion-sort
correctness). It's FreeCyclic's shape (no torsion) + a RECURSIVE `insert-commute` (V₄'s tabular commute, made recursive).
- **Gen**: `data Gen3 : Set where x y z : Gen3` + a 9-entry hand-table `_≼_`/`_≼?_` (NOT `Fin 3` — there is NO Fin
  trichotomy/`compare`/`_<?_` in-tree, only `ℕ._≤?_/_<?_` at `Foundation/Nat.agda:92,99`; a 3-ctor table is cleaner + self-contained).
- **Canonical** = inductive sorted (nondecreasing) predicate: `c-[] : Canonical []`; `c-one : (g)→Canonical (g∷[])`;
  `c-cons : (g h w)→ g ≼ h → Canonical (h∷w) → Canonical (g∷h∷w)`. Multiplicities = repeated letters; NO combine/drop.
- **insert** = recursive: `insert g [] = g∷[]`; `insert g (h∷w) = if g ≼ h then g∷h∷w else h∷insert g w`.
- **Obligations** (the `ListPresentation`/`WithLemmas` interface, `Coxeter/ListPresentation.agda:30-61`):
  `insert-canonical` (MEDIUM: induction on w + case on g≼h; needs head lemma "insert keeps sortedness"); `canonical-is-fixed`
  (EASY: induction, via helper `insert-min : g ≼ head → insert g w ≡ g∷w`); `insert-append-lemma` (MEDIUM, THE CRUX:
  induction via a recursive `insert-commute : Canonical w → insert g (insert h w) ≡ insert h (insert g w)`). NO involution
  lemma (no torsion, unlike V₄). `same-canonical` free via `SameCanonical.same-canonical-via-Gen gen-≟` (9-case `gen-≟`).
- Two proofs carry the weight: `insert-commute` + `insert-append-lemma`; rest is induction / tables. Templates:
  `V4-Coxeter.agda` (insert-commute:99, insert-append-lemma-V4:124, 8 cases), `FreeCyclic-Coxeter.agda` (the induction shapes).
