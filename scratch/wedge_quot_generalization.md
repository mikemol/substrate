# Shadow: generalize `DivStr.recon`'s quotient type (ℕ → per-carrier `Quot`)

Status: IN FLIGHT. Owner: assistant (took over from suspended jea/Q agent).
Gate-invisible (.md). Keep new `.agda` OUT of the build tree until it compiles
+ regen-makefiles + stage-by-path in one checkpoint (adopted protocol, see
agda/Substrate/Algebra/Q/GIT_COORDINATION_NOTE.md thread).

## Target (one sentence)
Replace the frozen judgement `DivStr.recon : ℕ → C → C → C` with a per-carrier
`Quot : Set` + `recon : Quot → C → C → C`, so polynomial division (polynomial
quotient) is a lawful `DivStr` instance and the PARALLEL F₂[x] world
(`PolyEEATrace` / `eea-fold-poly` / `gcd-fold-poly` / `bezout-poly`) collapses
into instances of the generic `Trace` / `trace-fold`, with all ℕ/ℤ/F₂/ℚ wedge
identities and the build preserved.

## The repeatable form (where the quotient is used)
The quotient appears in exactly three usage MODES; the decomposition is by mode:
- (A) OPAQUE pass-through — `forget`, `cell`, `Trace`, `collapse`, `fromℕ-Wedge`,
  `fromEEATrace`, `Bridge.transport-wedge/-trace`, `Cross`. Already polymorphic
  in q; free once recon is retyped. NO monoid needed.
- (B) MONOID element — `Compose` (`quot w₁ * quot w₂`, identity `suc zero`),
  `Adjunction.eval` (the (1,z) corner). Needs a multiplicative monoid on `Quot`.
- (C) SEQUENCE element — `Shape` (`List ℕ` of quotients) and its downstream
  (Shape/Transport, Shape/Register/FromTrace, ShapeParity, Coalgebra). Carries
  `Quot` but needs no algebra; `List ℕ` → `List (Quot D)`.

## Costructure (the shadow)
1. `DivStr` gains `Quot : Set`; `recon : Quot → C → C → C`. `Wedge.quot : Quot D`.
2. `QuotMonoid D` — the structure mode (B) silently used: `_⊛_ : Quot D → Quot D →
   Quot D` + `one : Quot D`. This was ℕ's `(_*_, 1)`. Compose/Adjunction take it
   as a parameter instead of baking ℕ. (More generic = the user's ask.)

## Composition operation
Each existing DivStr instance sets `Quot = ℕ`; recon lambdas are UNCHANGED (q was
already ℕ everywhere — ℕ-div, ℤ-div via `+ q`, F₂ `scale`, List `lrepeat`, Cyc,
⊤, two, Slices `power₀`, flatten, ⊗ᴰ). Mode-(B) consumers get ℕ's `(_*_, 1)`
monoid. Mode-(C) `shape : Trace D → List (Quot D)`. Then:
- `Poly-div : DivStr` with `Quot = QPoly`, `recon q b r = q *P b +P r` (poly).
- `fromPolyEEATrace : PolyEEATrace a b g → Trace Poly-div a b g`, each step a
  `Wedge Poly-div` with quot=`div-quot`, rem=`div-rem`, wedge-eq=`Div.recon-nth`.
- `gcd-fold-poly`, `eea-fold-poly`, `bezout-poly` ⟹ instances of generic
  `collapse` / `trace-fold` / bezout-fold (the dedup payoff).

## Entailment
Quot=ℕ everywhere ⟹ recon values unchanged ⟹ every ℕ/ℤ/F₂/ℚ identity holds by
the SAME proof (refl-stable). Mode-(B) given `(_*_,1)` ⟹ Compose green.
Poly recon-nth IS the wedge-eq witness ⟹ Poly is a lawful instance ⟹ the
parallel poly trace/fold/bezout are provably the generic instances (redundant).

## Phases (annealing: one degree, verify per file)
- P0 keystone: DivStr + Wedge.quot retype; fix all instances (Quot=ℕ); fix
  generic consumers (Compose+QuotMonoid, Shape→List(Quot), Adjunction, Bridge).
  Build green, ZERO new poly functionality. ← the step the prior agent skipped.
- P1: `Poly-div`. P2: `fromPolyEEATrace` (via recon-nth). P3: collapse
  eea-fold-poly / bezout-poly to generic instances.

## PIVOT (user decision, 2026-06-16): Quot = C (quotient is a carrier representative)

Supersedes the `Quot : Set` + `qtranslate` prototype below. Final design:
- `DivStr.recon : C → C → C → C` — the quotient q is a CARRIER ELEMENT, not a
  separate type, not a ℕ count. (The ℕ count was a FROZEN COORDINATE,
  [[feedback_coordinate_to_geometry]].)
- `Bridge` has NO `qtranslate`; `respects (q b r) : translate (recon D₁ q b r) ≡
  recon D₂ (translate q) (translate b) (translate r)` — `translate` maps the
  quotient like any element. DONE + GREEN (Wedge.agda, Bridge.agda).

### Vocabulary (research, do NOT invent "mode"/"phase")
"modes/phases" is a CROSS-WIRE: `Verdict.Phase` = H²(V₄,ℤ₂) cocycle class;
`ShadowArchitecture/Mode` = skill lattice. The operation = existing trio:
- `Bridge`/`translate` (Wedge/Bridge.agda) — strip rep from A, reconstitute in B.
- `cross`/`CrossMix` (Wedge/CrossMul.agda:56) — cospan A→R←B, cross-multiply reps.
- `representative` (Discipline.agda:172, CocycleSection) — chosen rep per class.
"basis change" = informal prose for the wedge itself (feedback_wedge_not_projection).

### Carrier classification (research)
- RING-ELEMENT (fit Quot=C directly, pure wins): ℕ (q*b+r ✓done), ℤ (drop +_,
  q:ℤ — also de-lossifies, allows negative q), F₂ (q:F₂ field mult, replaces
  Peano `scale`), Cyc (q:Fin via toℕ), and the MOTIVATING Poly (q*P b +P r;
  recon-nth at F2/Polynomial/Graded/Div.agda:113 IS the wedge-eq witness).
- COUNT (mature home = GradedDivStr grade index; flat Quot=C = its shadow):
  List (qw word, count=length), flatten/slice (q-deep wedge term, proven by
  power-replicate Product.agda:90). two/⊤ degenerate (ignore q).
- OBSTACLE: Cross._⊗ᴰ_ threads ONE shared q into both factors (lockstep,
  shared-quot); under Quot=C the shared quotient becomes a pair — re-express.
- MulDivStr (Wedge/Mul.agda) gives `mul` but not `+`; a uniform ring-recon would
  want a RingDivStr/SemiringDivStr (mul+add) that doesn't exist yet — NOT needed
  per-instance (each defines its own recon), but is the eventual clean home.

### STATE (checkpoint 2, 2026-06-16)
GREEN + VERIFIED (14): Wedge, Bridge, Compose, Compose/Laws, Cross (free product
+ quot-is-pair), Z/Wedge, F2/Wedge (recon now F₂ mult `_·_`, scale kept for
bridges), Fin/Wedge (toℕ q), Shape (List (C D); WedgeShape : DivStr → Set),
Adjunction, Graded (allegory reframing done), InclusionBridge (auto-adapted),
Certified, Mul.

RED — remaining tail (uncommitted WIP tree; do NOT commit till green + regen):
- ParityBridge: NEEDS NEW PROOF `parity-* : parity (x*y) ≡ parity x · parity y`
  (F₂-div recon became F₂ MULTIPLICATION, so the bridge must respect mult, not
  the old Peano `scale`). Provable (parity = ℕ→F₂ ring hom). IntParityBridge,
  Fin/Wedge/ModBridge likely similar.
- Correspondence + Iso + Monoidal: bridges/coherence under the new pair-quotient
  ⊗ᴰ and translate-handles-quotient respects. Check pentagon/triangle still refl.
- COUNT→GRADED migration (its own sub-project): List/Wedge, Product (flatten),
  Product/Slices (retire slice-scalar — no consumers), + consumers Registry,
  Product/ListIso, Product/{LawTypes,Hom,Laws}. These carriers lack a natural
  recon:C→C→C→C; they belong in GradedDivStr (count = grade index). Cascades.
- Shape downstream: Shape/Transport, Shape/Twist, Shape/Double, ShapeParity,
  Shape/Register/FromTrace (WedgeShape is now carrier-indexed).
- PAYOFF P1-P3 (the GOAL, new work, RING-carrier so clean): Poly-div : DivStr
  {C=QPoly, recon q b r = q *P b +P r}; fromPolyEEATrace via Div.recon-nth
  (Div.agda:113) as wedge-eq; then eea-fold-poly/gcd-fold-poly/bezout-poly become
  instances of generic Trace/collapse — retire the parallel construction.

### PAYOFF DELIVERED (checkpoint 3, 2026-06-16) — GREEN + verified
- Wedge.agda: added generic `trace-fold` (the Trace recursor, Seam B) +
  `collapse-fold`/`collapse-fold≡collapse`. Purely additive; dependents unaffected.
- NEW agda/Substrate/Algebra/F2/Polynomial/Wedge/PolyDiv.agda (GREEN):
  * `Poly-div : DivStr` {C = QPoly, recon q b r = length-|q| poly with coeffs
    `convCoeff qv bv k + nth rv k`} — F₂[x] is a GENUINE wedge instance, quotient
    = a carrier polynomial. Length-mismatch crux dissolved by `buildPoly` +
    `buildPoly-correct` (the inverse-of-nth) ∘ `Div.Over.recon-nth`.
  * `fromPolyEEATrace : PolyEEATrace a b g → Trace Poly-div a b g` — the parallel
    construction collapses into the generic Trace.
  * `gcd-fold-poly-is-collapse` — poly gcd-fold IS the generic `collapse`.
- HONEST BOUNDARY: the generic Trace keeps (quot, rem, divisor-as-QPoly) but
  FORGETS the (d, f-lo) presentation. `gcd-fold-poly` (needs only indices)
  collapses cleanly; `bezout-poly` uses `f-lo` directly, so it does NOT trivially
  factor through generic `trace-fold` (the step-interp gets a Wedge, not d/f-lo).
  f-lo IS recoverable from the divisor (b-poly = snoc (-P f-lo) 𝟙) — a deeper
  collapse, follow-up. The gcd collapse is the clean, complete demonstration.

### BEZOUT DEEPER COLLAPSE (checkpoint 4, 2026-06-16) — recovery DELIVERED + boundary
- PolyDiv.agda §5 (GREEN): `recover-flo : vinit b-poly ≡ f-lo` — f-lo IS recoverable
  from the divisor polynomial (char-2: b-poly = snoc (-P f-lo) 𝟙, -P = id, so
  f-lo = vinit b-poly). Plus `-P-id` (char-2 poly negation = id) and `vinit-snoc`.
- ANALYSIS (tested, not assumed): bezout's STEP RECURRENCE (new s=t', new t=s'+t'·q)
  needs only the QUOTIENT, already carried by the generic wedge as `quot w`. Its
  CORRECTNESS needs `recon-nth` ∀k; `wedge-eq` only pins k<|a| (a QPoly ≡ can't
  constrain beyond the length), so the generic step must call the REAL recon-nth,
  which needs (d, f-lo) — now recovered by `recover-flo`.
- PRINCIPLED BOUNDARY (the honest wall, tested): a full `bezout-from-trace :
  Trace Poly-div a b g → BezoutNthWitness a b g` over the BARE generic trace is
  BLOCKED — the witness type references the actual divisor b, and step-bezout-poly
  yields `… a (divisor-q d f-lo) g`, so it needs `b ≡ divisor-q d (vinit (proj₂ b))`
  ⟺ b is MONIC (vlast = 𝟙). The bare Trace allows non-monic divisors, so this is
  unprovable generically. gcd-fold collapses (ignores the divisor); bezout folds
  MONIC-divisor traces (= the EEA image of fromPolyEEATrace), not the bare trace.
  recover-flo is the bridge for that monic case. The proper home for the bezout
  collapse is a monic-divisor-aware (allegory residual) fold, not the bare recursor.

### REMAINING AIs — symbol table (arc prefix WQ- = Wedge-Quotient pivot)

Address any item by its symbol. Recommended order is top-to-bottom.

- **WQ-PAR** — ✅ DONE + GREEN (3/3). ParityBridge: `parity-*` (parity multiplicative)
  replaces parity-scale; respects via parity-+ ∘ parity-*. IntParityBridge: `parity-ℤ-*`
  (4-case on sign-magnitude *ℤ; parity-negPos kills the mixed-sign cases) replaces
  parity-ℤ-scale. ModBridge: respects-ℕ/toℕ-RHS/respects-cyc now reduce the quotient
  too (translate q = reduce n q), via `mod-mult-hom` (two-sided) replacing mod-*-right.
  InclusionBridge auto-adapted (respects = refl, +_ maps the quotient). Files done:
  Wedge/ParityBridge, Wedge/IntParityBridge, Fin/Wedge/ModBridge.
- **WQ-COH** — ✅ DONE + GREEN (3/3). Correspondence `_⊚_`: composite respects
  translates the quotient through f (`respects g (translate f q) …`). Monoidal `_⊗ᵇ_`:
  projects the pair quotient (`respects f (proj₁ q) …`, `respects g (proj₂ q) …`);
  associators' `λ _ _ _ → refl` unchanged. Iso green (imports Correspondence).
  PENTAGON / TRIANGLE / HEXAGON / naturality ALL STILL refl — the pair-quotient ⊗ᴰ
  preserves full Mac Lane coherence. Files done: Wedge/Correspondence, Iso, Monoidal.
- **WQ-GRD** — ✅ DONE + GREEN. Count-as-grade (not physical retirement, which would
  cascade destructively through ~10 flatten/List-div consumers): the count is now
  DERIVED from the carrier-element quotient's grade/length.
  * List-div: recon q b r = lrepeat (length q) b ++ r — count = |q| (Foundation.List.Length).
  * flatten: flatten-recon (qn,_) (i,b)(j,r) — count = qn (the grade component of the
    Σ ℕ (C P) quotient; the flattened carrier carries its own grade).
  * slice-scalar: RETIRED (+ power₀) — its grade-0 quotient C P 0 has no grade to host
    a count, and it had no consumers; slice-step (graded) + slice-flat (=flatten) survive.
  * ListIso: bridge respects fixed (q→proj₁ q) + new `vecToList-length` (Vec grade =
    List length), so the flatten≅List-div bridge holds with both count readings.
  * Graded/Morphism gradedHom→bridge: q→qn (flatten-map is grade-preserving).
  All consumers green on recompile (LawTypes/Hom/Laws/Certified/MonoidalAdjunction(+Props)).
  UNBLOCKED: Wedge/Sphere + Wedge/Registry now GREEN. Generic-carrier Register (vs the
  ℕ-div specialization from WQ-SHP) remains a future nicety.
- **WQ-SHP** — ✅ DONE + GREEN (10 files). The pivot turned `shape` from bridge-
  INVARIANT (carrier-free `List ℕ`) to bridge-NATURAL (`List (C D)`, shape∘transport
  = mapL translate ∘ shape). Consequences carried through: Transport's `shape-transport`
  now `≡ mapL (translate br) (shape t)` (local `mapL`, Foundation.List has no map);
  Double redesigned — `Corr` same-carrier, `square` is the SINGLE-bridge naturality
  square (the two-different-bridge square was only valid under invariance); Twist's
  companion/conjoint re-expressed as the bridge-mediated (mapL∘translate) relation;
  Register + Register/Properties + Q/Decidable + Double/Interned + FromTrace specialized
  to ℕ-div (the Register's practical shape carrier; generic-carrier register is a
  future nicety). ShapeParity needed no change. Files green: Shape, Shape/Transport,
  Shape/Double, Shape/Twist, ShapeParity, Shape/Register, Shape/Register/Properties,
  Shape/Register/FromTrace, Shape/Double/Interned, Q/Properties/Decidable.
  NOTE: Wedge/Sphere.agda is RED but blocked on WQ-GRD (imports List/Wedge), not WQ-SHP.
- **WQ-BEZ** — (deferred) bezout monic-divisor fold: the allegory residual fold that
  folds MONIC-divisor traces (EEA image), using `recover-flo` as the bridge. The bare
  trace-fold is bounded by monic-ness (see BEZOUT boundary above). Lower priority.
- **WQ-SEAL** — the landing: broad full-tree typecheck sweep, `gen_build_makefiles.py`
  regen (PolyDiv.agda is a NEW file → Makefile staleness), then commit by path with full
  gates (never --no-verify). Do LAST, once WQ-PAR/COH/GRD/SHP are green.

## Allegory reframing (user, 2026-06-16)
"Wedge ⊄ GradedWedge" overclaim (Graded.agda:16) is NOT fixed by a direct
embedding — it is meant to be replaced by the FORMAL ALLEGORY. TraceDescent.agda
already ties PolyEEATrace termination to `Category/Allegory/Refinement.chain`
(ALG-7, the Φ-chain descent). So the plain↔graded relationship routes through the
allegory refinement chain, NOT a GradedWedge instance of Wedge. Do not build the
embedding; retract the comment and point it at the allegory. The generic-Quot
DivStr + allegory is the unifying frame.
