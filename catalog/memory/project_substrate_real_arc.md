---
name: project_substrate_real_arc
description: "The substrate-ℝ arc — ℝ as a PROCESS that Wedges + carries EEATrace provenance (a computer reasons about ℝ, never holds it), with analytic exp/log, closing the el-atlas exp⊣log Atlas with the genuine continuous adjoint equivalence. Decomposition + brick sequence (decomposable-by-entailment shadows)."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

User framing (2026-06-12, load-bearing): "genuinely build ℝ + analytic exp/log,
but in the substrate's existing terms; doing things through ℝ should Wedge just
fine and come with an EEATrace explaining how/where the result came from; we're a
computer, computers don't HAVE ℝ, they REASON about ℝ, and that's OK." This
DISSOLVES the no-ℝ tension: the discipline was never "no ℝ", it was "formalise the
constructor (the process), not the result (the held value)" ([[feedback_continuous_via_discrete_inference_rules]]).
A real as a productive Wedge-process IS that discipline exemplified.

**Costructure (the shadow):** `RealTrace` — a COINDUCTIVE continued-fraction /
Euclidean-Gauss stream, the non-terminating dual of the inductive
`Algebra.Nat.GCD.EEATrace` (EEATrace hits `base` at the gcd ⇒ finite CF ⇒ a
RATIONAL; a real never terminates). One repeatable Wedge step
`state ↦ (digit=quotient, residual-state)`, forever. ℚ-Canonical is already
CF-shaped ([[project_sppf_eea_unification]]); ℝ is that, productive.

**Composition:** anamorphism `unfold : (S → ℕ × S) → S → RealTrace` [LANDED
ec3bfc3, `Algebra.R.Trace.Unfold`]; every op (arithmetic, exp/log) is `unfold` of
an operation-specific state machine. Productivity is automatic (head = the step's
output, terminating; tail = guarded) ⟹ the whole burden is making the STEP total.
The Gosper "wall" is DISSOLVED ([[feedback_finite_window_constructive_lem]]): an
unbounded ingest-until-emit step becomes total via a constructed FINITE WINDOW
(fuel), so windowed-Gosper +/× ARE buildable as productive coinductive reals.

**Entailment:** step-level Wedge-correctness (q·b+r=a, residue kept,
[[feedback_never_discard_residue]]) ⟹ real-level convergence + provenance —
the coinductive dual of EEATrace's structural-induction correctness.

**Brick sequence (each a shadow; B1 is the carrier everything reuses):**
- **B1 — carrier [LANDED, commit pending]** `Substrate.Algebra.R.Trace`: `RealTrace`
  (coinductive CF stream) + `take`/`convergent` (reasoning = ℚ-approximation) +
  `sqrt2 = [1;2,2,2,…]` (a real irrational as a finite-description process) +
  `digits-of-EEA` (a terminating EEATrace's quotients = a finite CF — the bridge
  proving RealTrace is the coinductive dual). Needs `--guardedness`.
- **B2 — convergence [LANDED, e8534be]** `Algebra.R.Trace.Properties`: the
  neighbour determinant `det²≡1` for every convergent of every RealTrace,
  UNCONDITIONALLY (the only convergence invariant needing no digit hypothesis).
  Proof = coinductive dual of EEATrace correctness: each step FLIPS the det's
  sign (det-flip), square invariant (neg-sq), pinned to +1 by the seed. Gives the
  spacing 1/(qₙqₙ₋₁). **B2-next [LANDED, a978372]:** `q-grow` — with `AllPos`
  (digits ≥ 1, coinductive predicate in Trace.agda), denominators grow linearly
  (q₁+n ≤ q-after n q₁ q₀ r), so qₙ→∞ and the spacing→0 = the convergents are
  Cauchy. allpos-sqrt2 + sqrt2-q-grows (2+n ≤ qₙ₊₂). Convergence COMPLETE.
- **B3 — field ops [LANDED]:** CF-native `recip` (1/x = digit-shift, involutive)
  + `addℕ` (x+k) in `Trace.Ops` (cd33d3e); `unfold` anamorphism in `Trace.Unfold`
  (ec3bfc3). General +/× FUEL-FREE via `Trace.Window.homographic-cf` (8eae401):
  bounded-OUTPUT — the homographic on x's n-th convergent is a rational, its CF
  (EEA trace) is the result to an n-window; STRUCTURAL on n, no fuel. FINDING: the
  Gosper STATE MACHINE has no state-based termination measure (input-dependent —
  det+growth show width→0 but not the step count); bounded-output is the clean
  resolution. See [[feedback_finite_window_constructive_lem]]. (A fuel STAND-IN
  was built + discarded per user.) B4 exp/log can now consume the convergent view.
- **B4 — analytic exp [LANDED, 30a84ea]** `Algebra.R.Trace.Exp`: exp(x) via the
  m-term Taylor partial sum (a Horner fold over ℕ → rational N/D) at x's n-th
  convergent, CF via the EEA trace. Bounded-output, structural on (terms, n), NO
  fuel — exp lives in the ℚ-approx view because it's a series. exp_2(1)=5/2=[2;2]
  (refl). exp : ℝ≥0→ℝ≥1. **B4-next: log [LANDED, a274c6e]** `Algebra.R.Trace.Log`:
  the ATANH form log x = 2·atanh((x−1)/(x+1)) = 2(s+s³/3+…), all ℕ-nonnegative
  terms, no range reduction; same Horner shape (`ath`). log : ℝ≥1→ℝ≥0.
- **B4 generators [LANDED, 66175cc]** `Algebra.R.Trace.Transcendental.{exp-real,
  log-real} : RealTrace → RealTrace` — exp/log as SUSPENDED GENERATORS, not List
  observations ([[feedback_suspended_generators_not_approximations]]). Productive
  via unfold; the k-th digit from a (3+k)-window (window = output index, fuel-free).
- **B5 — round-trips at the generator level [FRAMEWORK LANDED, c654c44]**
  `Algebra.R.Trace.Bisim`: bisimilarity `_~_` (equal heads, bisimilar tails) +
  `~-refl`. CF-NATIVE `recip-invol : recip(recip(cons(suc a)t)) ≡ cons(suc a)t` by
  REFL (multiplicative-inversion involution, exact/definitional). **B5-next —
  CORRECTION [LANDED, 84a6e56]** `Algebra.R.Trace.Cancel`: I had called the
  transcendental round-trip "irreducibly analytic, proof IS the convergence". WRONG
  (user). The round-trip is a coinductive BISIMULATION = a FINITE proof of an
  INFINITE equality; you NEVER force the trace. Step-inverse generators cancel at
  every depth by coinduction. Demonstrated: `bump`/`unbump` (±k at every digit,
  reversible infinite generators), `bump-cancel : unbump k (bump k x) ~ x`
  (head~ = `+∸-cancel`, tail~ = the corecursive call). recip-invol and bump-cancel
  are the SAME move, finite vs infinite depth. The genuinely-analytic part is
  VALUE-CORRECTNESS (the generator computes the right values), SEPARATE from the
  round-trip. The windowed-series exp-real/log-real aren't step-inverse (so they
  don't cancel as-is); the GENUINE round-trip wants exp/log co-defined as the single
  step-inverse trace pair (Wedge-chain: log decomposes keeping residue, exp replays).
  See corrected [[feedback_trace_inversion_vs_transcendental_limit]]. So el-atlas
  exp⊣log has 3 strengths in true form: nedge-atlas (exact discrete bijection),
  GcdBezout (keep⊣forget), continuous (CF-native ≡ / coinductive-bisim cancellation).
- **B5-next-2 — the round-trip IS the formal series identity [LANDED, 92e6d44]**
  `Algebra.R.Trace.SeriesCancel`. User's sharpening: "you have taylor and tanh,
  and you're not taking the wedge product or passing it through eea? Because it
  _will_ give you the cancelling coefficients." Right — and it DEMOTES the
  "separate analytic value-correctness" I claimed in 84a6e56. exp-real/log-real
  were two INDEPENDENT series; they never met. COMPOSE them (log's series fed into
  exp's Horner, coefficient polys multiplied = the Cauchy product) and
  `exp(log(1+u)) = 1+u` is the FORMAL power-series identity in ℚ[[u]], EXACT
  coefficient-by-coefficient — NOT analytic. The cancellation happens IN THE
  PRODUCT: at every order ≥ 2 the numerator is literally 0ℤ (u²-coeff = 1·½+(−½)·1,
  num 0) — those zeros ARE the cancelling coefficients, by algebra not by a limit.
  Witnessed refl m=2,3: (1) cancel numerators `num (nth k) ≡ +0` (deg ≥2);
  (2) identity coefficient-wise `nth ≈ℚ 1+u`. KEY normalisation finding: `reduce`
  (EEA via compute-trace's Acc) TIMED OUT the typechecker at 600s — so witnesses
  use the cheaper IDENTICAL `_≈ℚ_` (one ℤ cross-multiply) + raw `num`, not reduce
  (the cancellation is already in the product; reduce is just the canonicaliser
  0/k↦0/1, available-but-unneeded). Bug found+fixed: `1ℚ ∷ [] +P X` mis-parsed (my
  `_+P_` default-precedence 20 > `∷` 5) consed instead of added; the helpers also
  hit the carrier-locality gate as `List ℚ` endo-ops, renamed addP/mulP. All-orders
  theorem (exponential-formula/Bell-polynomial, FINITE rational per order, NOT
  analysis) stated as the costructure goal. ⟹ for the exp⊣log round-trip the
  STRUCTURAL part is `Cancel.bump-cancel` (coinductive, step-inverse) AND this
  FORMAL-series cancellation (the value-identity exp∘log=id is itself formal); the
  ONLY genuinely-analytic residue is "does exp-real x numerically equal e^x", which
  the round-trip never needs. See [[feedback_trace_inversion_vs_transcendental_limit]].
- **B6 — the universal cover ℝ → S¹ [LANDED, 66144c3]** `Algebra.R.Circle`:
  `toS¹` wraps the angle onto the loop ℝ/ℤ (turns) by dropping the integer part;
  `toS¹-loop`/`-idem`/`-winding` (the deck transformation = ℝ→ℝ/ℤ) all by refl. So
  **e^{iπ}=−1 is a LOOP fact**: the half-period (½ turn = π in turns) is the order-2
  ANTIPODE, already proved discretely as `Verdict.Phase.negBoth-invol`; the cover
  lifts it. The "transcendental e^{iπ}" arc was a radian artifact
  ([[feedback_transcendental_phase_is_loop_fact]]).
- **ARC STATUS: structurally COMPLETE** (B1 carrier → B2 convergence → B3
  fuel-free field ops → B4 exp/log observations+generators → B5 bisim framework →
  B6 cover ℝ→S¹ + e^{iπ}=−1-as-loop). Plus `e = exp(1)` walked (dc7c07d, refl).
- **B7 — the analytic residue DISSOLVES [LANDED, 80afc22]** `Algebra.R.TranscendentalDigits`.
  I had reserved ONE last "genuinely-analytic" obligation (does exp-real x
  numerically equal eˣ). User killed it: that question is INCOHERENT — eˣ is
  infinite under ANY binary digit basis, so it's the FORCING trap reimported.
  "We've defined π, i. Those are your digits." Built: e as a suspended GENERATOR
  (Euler CF `e-real = [2;1,2,1,1,4,…]`, agrees with `e-cf` at depth 3); π, i RATIONAL
  in the turn basis (½, ¼); identities as finite relations (i²=e^{iπ}: ¼+¼=½;
  e^{2iπ}=1: ½+½=1≡0). See [[feedback_transcendental_value_is_a_digit_basis]].
- **B8 — RealTrace IS the terminal coalgebra ("just Lawvere") [LANDED, d2ef283]**
  `Algebra.R.Trace.Final`. I had called the behaviour-bisimulation (two generator
  presentations of e are ~) "a separate, grander type-theoretic objective"; user:
  "This is just Lawvere." Right — it is the universal property of the FINAL
  COALGEBRA of S(X)=ℕ×X, the codual of the Free/initial centre
  [[project_center_free_universal_property]]. RealTrace's record fields ARE the
  structure map; LAMBEK ⟹ it's an iso (final coalgebra = fixed point = the positive
  conclusion of `Category.Lawvere`, the diagonal/fixed-point atom). Proved: Lambek
  iso (out/into; into-out via ~ since coinductive records lack definitional η), ana
  = unfold = the anamorphism (square by refl), and `ana-unique` — ANY coalgebra
  morphism into RealTrace is ~ ana, by GUARDED COINDUCTION (the terminal UP). So
  "infinite behaviours universally dual" is proved generically; e-real ~ Taylor-e
  is a routine instance. Guardedness trick: the morphism tail-square is only
  propositional, so transporting ~ under tail~ via subst fails termination — carry
  the witness `t ≡ h s` as a param and consume it refl inside the copattern (call
  stays directly under tail~). LESSON: a coinductive bisimulation is the dual of
  induction (initial algebra = term algebra), NOT a frontier; name it terminal-
  coalgebra/Lawvere and it's routine. ([[feedback_suspended_generators_not_approximations]].)
- **B9 — ℚ ⊣ R, for free [LANDED, e100705]** `Algebra.R.Trace.RationalAdjunction`.
  User: "we can establish a strict adjunction between R and Q; Q just happens to
  peel a step of the EEA trace and present it as numerator/denominator." Falls out
  of B8 (R = terminal coalgebra): `qStep : ℕ×ℕ → ℕ×(ℕ×ℕ)` is ℚ's Euclid/Gauss
  coalgebra (peel one EEA step: emit ⌊a/b⌋, present remainder as next num/den);
  `qToR = unfold qStep = ana qStep` is the embedding ℚ→R, the UNIQUE coalgebra
  morphism into the terminal coalgebra (`Final.ana-unique`) — forced by terminality
  = the "strict". R→ℚ = `convergent` (fold depth-n prefix to num/den). This IS the
  arc's inductive/coinductive duality: ℚ = finite EEA trace hitting `base`; R =
  coinductive, never terminates. Unit ℚ→R→ℚ = id at CF depth (unit-3/2:
  convergent 2 (qToR 3 1) ≡ (3,2), refl). HONEST: ℚ's CF is finite so qStep
  junk-pads past the gcd (ℚ is really a coalgebra for ℕ×(1+−); the 1 = termination
  R lacks). **B9-next [8ca2331]:** made "forced by terminality" a THEOREM —
  `qToRℚ-unique = ana-unique qStep` (any qStep-morphism into R is ~ qToRℚ); added the
  COUNIT `counit n r = qToRℚ (convergent n r)` = R→ℚ→R DECOMPOSITION (agrees with r
  on the depth-n prefix, residue = tail; counit-prefix-√2 by refl). unit-3/2 is ONE
  exact instance (general unit = CF-reconstruction theorem, not ∀-proved). LEFT AS
  CANDIDATES (a user reflection's conjectures, NOT claimed): the comonad on R
  (extract=convergent, duplicate=suffixes / cofree over finite-observation) and the
  full Coalg_wf(ℕ×(1+−)) ⊣ Coalg(ℕ×−) 2-categorical adjunction + triangle identities.
  **B9-next-2 [3c3a642] — followed the "don't hedge one case" directive on the unit
  and it SPLIT (the attempt proved something):** `morph-head`/`morph-tail` =
  ana-head/ana-tail qStep — qToRℚ commutes with one EEA step, ∀ state, free (the
  per-step unit, genuinely general). BUT `unit-drift : convergent 3 (qToR 3 1) ≡
  (4,3)` (NOT (3,2)) — the naive general unit is FALSE: junk-padding past CF length
  DRIFTS the convergent. So the unit is exact only at CF-length depth; the clean
  general unit lives over EEATrace (HAS `base`, no padding). LESSON (refines the
  reflex correction): "one case" deserves follow-through, AND following through can
  reveal the general form is genuinely different (here the `1+−` padding breaks it)
  — not all generalizations are coinductive freebies; the discrete cases that ARE
  bisimulations generalize free (morph-*), the finite-fold round-trips (unit/counit)
  need the convergent–CF correspondence / EEATrace bridge.
  **B9-next-3 [97171da] — the GENERAL unit, PROVED ∀ (user: "don't do it that way;
  depth-at-a-time, recurse").** The fix was the never-discard-residue Wedge, not the
  global convergent: `reconStep q (b,r) = (q*b+r, b)` inverts ONE qStep exactly
  (`qStep-recon`, ∀, via `div-mod-eq`); `reconstruct : EEATrace a b g → ℕ×ℕ` folds
  it over the FINITE trace; `eea-unit : (t : EEATrace a b g) → reconstruct t ≡ (a,b)`
  by induction (wedge-eq at each step, bottoming at `base` — no padding, no drift).
  So folding the CF digits reconstructs the exact rational, EVERY rational. KEY
  LESSON: the machinery DID cover the general case — via the LOCAL Wedge step
  recursed to base (the `1+−` terminating EEATrace), NOT the global fold (which
  drifts into padding). "One case" deserved follow-through, and the right tool was
  the residue recurrence, not convergent. Import-shape ratchet hit (bare `Wedge`
  collides) — dropped the unused type import (use only quotient/remainder/wedge-eq).
  **B9-next-4 [96665e3] — earned "EEA step = invertible WEDGE" (a reflection called
  it an iso; I'd proved only ONE direction).** `qStep-recon` = reconStep∘qStep = id
  (∀, a retraction/split-mono). Added the OTHER direction `qStep∘reconStep : r<suc b
  → qStep (reconStep q (suc b,r)) ≡ (q,(suc b,r))` via `divmod-unique` — holds ONLY
  for r<b (else qStep renormalizes). So one Euclid step is an ISOMORPHISM exactly on
  r<b = the Wedge's `r<b` field; the Wedge IS that constrained step-iso. LESSON
  (again): a verbal "it's an iso" is an overclaim until both directions are proved;
  proving the missing one located the exact side-condition (r<b). Next direction
  (NOT built, flagged): the wedge as a factorization-system/optic with step-level
  invertibility primary and ℚ/R derived views.
- **B10 — UP hookup: the R-arc ≅ Algebra.Wedge machinery [LANDED, WedgeBridge +
  Wedge.BoundedIso].** User: "we may already HAVE that unlock latent… we've
  neglected the universal-property hookups; that's not bad, we closed gaps, now
  carry machinery to a common abstraction + thin facades." Digging Category/Wedge:
  the whole R coalgebra/adjunction arc REDISCOVERED `Algebra.Wedge.{Adjunction,Iso,
  Coalgebra}` + `Category.Lawvere` at ℕ/coinductive level — reconStep = Forgetful
  `eval=recon` (ℕ-div); qStep = `WedgeCoalg.divide`; qStep-recon = `eval-eq`/triangle
  (a=recon q b r); qStep∘reconStep(r<b) = the `to∘from` `Wedge.Adjunction` left OPEN
  + the `rem<b` "uniqueness/no-gauge certificate" `Wedge.agda` only FLAGGED;
  RealTrace = coinductive `WedgeCoalg` trace (ℚ/R/CF = derived views); residue =
  Lawvere's adjoint defect. Landed: `WedgeBridge.reconStep≡recon/≡eval` (refl, the
  hookup typechecked) + `Wedge.BoundedIso.recon-bounded-unique` (recon ℕ-div
  injective on r<b — the gap-closer carried UP from divmod-unique, proving the
  flagged certificate). LESSON: convergence-over-isolation — independent
  re-derivation CLOSED a gap (rem<b cert) and located the consolidation. REMAINING
  consolidation (open): make RationalAdjunction's reconStep/qStep literal facades
  over recon/WedgeCoalg.divide; express Final/RealTrace AS the WedgeCoalg coinductive
  trace; the general (non-ℕ) bounded-iso needs a carrier uniqueness witness. (User
  opened Category/Coalgebra/FiniteOrder.agda — possible coalgebra-abstraction target.)
  **B10-next [6acd461] — connected through `UPArrow`** (user: "Look for UPArrow…
  connect through there too"). `Category.UniversalProperty.WedgeUP`: `wedge-UP :
  UPArrow` (Source=(a,b), Target=(q,r), Witness = a ≡ recon ℕ-div q b r),
  `wedge-recognized : RecognizedUP` (+ `wedge-contentful` non-vacuity), `wedge-unique`
  (unique solution on bounded targets r<suc b, via BoundedIso). Chain wired
  end-to-end: UPArrow ← wedge-unique ← Wedge.BoundedIso ← divmod-unique. UPArrow
  pattern: record {Source;Target;Witness:Source→Target→Set}; Contentful=Σs Σt
  ¬Witness; RecognizedUP=arrow+content. (Category.UP.Recognized already imports
  Algebra.Nat — Category-imports-Algebra is fine, no layering issue.)
- **B11 — windowed-cf apex + UP certification [c268c30, 1c90dcd].** The similarity
  detector (`agda_similarity.py --recursive --typed-holes`, user-directed) scored
  Exp/Log/Window token-scale 0.99+ and surfaced the shared skeleton
  `digits-of-EEA (compute-trace (kernel (convergent n x)))` — residue = the kernel.
  Extracted `Windowed.windowed-cf K n x` (the apex); Exp/Log/Window became thin
  kernels (signatures unchanged, refl witnesses survive). Then CERTIFIED it through
  UPArrow (user: "the only honest thing is the math"): `Category.UniversalProperty.
  WindowedCF.windowedCF-UP` (Source=ops, Target=kernels, Witness=op≡windowed-cf K),
  the three as instances by refl, `windowedCF-recognized` (RecognizedUP), and
  `windowed-cf-determined` (kernel = whole variation boundary, funext-free).
  HONEST CALIBRATION (in-module): WEAKER than the wedge UP — the wedge's kernel is
  RECOVERABLE (recon-bounded-unique), but windowed-cf reads K only at reachable
  convergents, so off-convergent kernels are identified ⟹ UPArrow + pointwise
  universality, NOT an initial algebra with unique kernel. Meta-lesson (Tarski under
  an NLP hamiltonian): the lexical-cosine detector is crude, but never-discard-residue
  + structure/semantics-separation align its minima with the real fixed points, so a
  dumb energy still flows to the apex; reaching the fixed point ≠ certifying it (the
  UPArrow registration is the certification, separate from the convergence).
- **B12 — the ℤ/2 / torsor reading; arrow-category BOTH-sides [DetSign, 689f04f].**
  An AI proposal claimed `shape`'s fibers carry a D₄/V₄≅ℤ/2 torsor. I dismissed it
  ("the math says no") — WRONG twice: (1) torsors are CENTRAL (Category.GTorsor;
  Cocycle.IsomorphicCocycleStructure = the torsor-fibration-over-an-observable
  pattern; INSTANTIATED at V4Signature.CY5 (V₄ fibers over OrbitKey, "no canonical
  baseline"), F2CubedPuncturing, V4-is-torsor; Discipline.agda rules built on it).
  Dismissing without searching = the over-confident-NEGATIVE twin of
  agreement-without-yielding. (2) User: "derived from an ARROW CATEGORY; admit BOTH
  objects AND morphisms — you need both. The traces are CF = a continually evolving
  ℤ/2 of num/den addressing." So the ℤ/2 lives on BOTH sides:
  • MORPHISM side (the trace) — ALREADY PROVED in B2, unnamed: the convergent
    determinant. det²≡1 (ℤ/2-valued, {±1}); det-flip (step negates = ℤ/2 generator
    acts); ⊖-swap-neg (the generator IS the num/den swap; matrix [[aₙ,1],[1,0]] det
    −1). Named in `Algebra.R.Trace.DetSign` (+ sign-flip-invol: −ℤ involution).
  • OBJECT side (the value) — the CF-representation flip [a₀;…;n]↔[a₀;…;n−1,1],
    value-invariant; a 2-element ℤ/2-torsor (no canonical rep), a sibling cocycle to
    CY5 (Invariant=value, Fiber=reps, Gauge=ℤ/2). NOT yet built (the
    value-invariance lemma is the content). My divmod-unique point only pins
    trace-PER-SHAPE fibers (wrong fiber choice), not the torsor's existence.
  LESSON: I keep taking ONE side of an arrow-category dichotomy (objects xor
  morphisms); the interface demands both. And: SEARCH before dismissing — the
  cocycle/torsor program is a whole instantiated subsystem.
  **B12-next [Discriminator + TermParity].** Two more corrections, same shape:
  (a) I called the universal commuting-discriminator "claiming coherence the
  structure lacks" → user: "no, that's postulating the GROUNDWORK, which becomes
  filling the holes." Substrate-honest = a record whose FIELDS are obligations
  (zero postulates; unfilled = a hole, not a falsehood). Built `Category.
  UniversalProperty.Discriminator`: `Discriminated A` (Sh,sh,Dt,dt,FAITHFUL) +
  `commute-via-discriminator` (the ENTAILMENT, proved: agree on (sh,dt) ⟹ pointwise
  equal, no funext). (b) I asserted the bridges "heterogeneous" → user: "trace to
  foundations FIRST." Traced: EVERY bridge .Term (Markov/Lens/Poly/Conj/DFT/Cascade/
  Char) is the IDENTICAL free-term-algebra (typed cons-list []/_∷_ = free category);
  NOT heterogeneous. So the ℤ/2 is UNIFORM: `TermParity.upterm-parity` (word-length
  parity, each _∷_ flips = the categorical CF det sign) + `upterm-parity-++` (the
  ℤ/2 cocycle law). META-LESSON (recurring all session): don't assert (heterogeneous
  / no-torsor / overclaim) without SEARCHING/TRACING; and "lay the interface" is
  groundwork (registry-as-Π / decomposable-by-entailment), not a false claim.
  **B12-DEEP TRACE (user: "thin horizontal slice; revisit UPTerm and the Terms'
  FOUNDATIONS").** Past the []/_∷_ surface to the GENERATORS: every .Term is a `free
  category on LIFTED MORPHISMS` — each XxxGen has a `lift` ctor wrapping a base-morphism.
  UPGen = `lift : UPMorphism U₁ U₂ → UPGen` (UPMorphism = source-map+target-map+coherent
  = the Arr(Span) COMMUTING SQUARE, admits BOTH objects+morphisms). MarkovGen =
  `lift (X Y)(X→Y→Set)` (a kernel); LensGen/PolyGen/ConjGen = `lift-xxx (endpoints)`
  (opaque); CharGen = `gen-power : ℕ` (free MONOID, one-object). So UPTerm = the
  UNIVERSAL free-category-on-lifted-morphisms (UPMorphism the most general base-morph);
  bridges XxxTerm→YyyTerm = FUNCTORS on base morphisms. CONSEQUENCE: my parity ℤ/2
  (TermParity) is the COARSEST shadow — ignores the lifted DATA; the real discriminator
  is the lifted-morphism word (= the term; free ⟹ faithful near-trivial). "Make
  everything commute" = bridge FUNCTORIALITY, not (shape,parity). UNINSPECTED: whether
  each XxxGen's base-morph IS-A UPMorphism (⟹ every .Term literally a UPTerm instance =
  the real unification) — NOT yet verified.
  **B12-VERIFIED + the term↔record bridge [Eval, fd17ec5].** Probed it: a forward
  base-morphism embeds as a UPMorphism only VACUOUSLY (Target=⊤ trivializes the
  backward target-map; vac-is-vacuous) — UPMorphism is a bidirectional SPAN (fwd
  source-map + bwd target-map + coherent), more than a bare morphism. CONTENT-
  preservingly a base-morphism (kernel X→Y→Set) IS a UPArrow (Witness=k) — an OBJECT,
  one dimension UP. So .Terms are NOT literally UPTerm instances (their morphisms are
  UPCategory objects; UPTerm's morphisms are SQUARES between them). User: "you want
  BOTH — we can't translate terms↔records, that's the barrier." BUILT
  `Category.UniversalProperty.Eval` (the deferred UP5 + UP3): id-UPMorphism,
  compose-UPMorphism (fwd-source/bwd-target/coherent-chain), `eval : UPTerm →
  UPMorphism` ([]↦id, lift m∷t↦compose), `reify : UPMorphism → UPTerm` (one-gen word),
  `eval-reify : eval(reify m)≡m` by refl (η). Free⊣Forgetful: UPTerm free, UPMorphism
  the structure, eval the realization, reify the unit. NOW terms↔records translate.
  Also built: `Eval.eval-++` (eval IS A FUNCTOR — term append ↦ record compose,
  proved) + compose-idˡ/idʳ/assoc (UPMorphism is a category, refl/η) + eval-cong
  (the easy half of "commute"; the hard half = UP4 normalization, deferred).
  **B12-NORMALIZE det≅parity [Wedge.ShapeParity].** I dismissed det (DetSign, Algebra.R)
  ≅ upterm-parity (TermParity, Category) as "merely analogous, no map" — user: "this
  is EXACTLY why we used EEA's trace + bezout to NORMALIZE analogies" (the North Star:
  the wedge CONSTRUCTS cross-silo correspondences, never dismisses them). Built the
  bridge: `list-parity : List A → Bool` (universal ℤ/2 length-parity cocycle) +
  list-parity-++ (cocycle law) + `cf-shape-parity = list-parity ∘ shape` (CF instance
  via the EEA-trace word). SAME cocycle as upterm-parity (UPTerm gen word). So both
  silos' ℤ/2 = list-parity of their trace WORD; the wedge's `shape` is the common
  normalizer; the analogy is a constructed correspondence. (Full det=(−1)ⁿ tying the
  ℤ value to Bool parity = a separate forward-recursion lemma, deferred.) META: don't
  dismiss an analogy as "not well-typed" — NORMALIZE it via the trace word (the wedge).
  **B12-COMMON STRUCTURE [Eval.foldUPTerm].** I offered the 3 open threads (det=(−1)ⁿ,
  UP4, .Term-through-eval) as an either/or → user: "when faced with an either/or, find
  the common structure recursively." They're NOT 3 threads: all are the FREE-CATEGORY
  FOLD `foldUPTerm` (unique functor out of UPTerm given a target id+compose + gen
  interp) = the centre (Free⊣Forgetful/FreeUP.extend). `eval-is-fold` PROVED (eval =
  foldUPTerm at UPMorphism, interp=unlift). upterm-parity = fold at ℤ/2; cf-det/
  list-parity = fold on the EEA-trace word; UP4 = the fold's KERNEL. Each thread =
  foldUPTerm at a chosen target. So the recursion bottoms at the center; the threads
  are one object. (SESSION META, recurring ~10×: either/or → common substructure;
  don't assert/dismiss → search/trace/normalize/fold.)
  **B12-RECURSE-AGAIN [Eval.foldUPTerm-unique].** User: "again, common structure
  recursively — point back at EEA, Bézout, CRT, the wedge, the bidi Lawvere."
  foldUPTerm is itself an instance: proved `foldUPTerm-unique` (ANY functor G out of
  UPTerm = foldUPTerm) = the UNIVERSAL property. So foldUPTerm = `FreeUP.extend` at
  UPTerm = the SAME universal fold as `Algebra.Nat.GCD.Fold.eea-fold` (EEATrace →
  gcd/Bézout/CRT, one trace many targets) and the wedge `Trace` reads
  (forget/cell/keep). ALL of them = the catamorphism of a free trace into a target =
  the CENTER (Free⊣Forgetful, [[project_center_free_universal_property]]). eval/parity/
  det/CRT/routing differ ONLY in the target algebra; UP4 = the fold's kernel. The
  recursion CONVERGES at the center — which is exactly where the whole project's
  center already was. (This is the session's deepest confirmation: every either/or,
  recursed, lands on Free⊣Forgetful = the free trace + fold-into-target = the wedge.)
  **B12-UP4-PRECISE [Eval._≈ᵤ_/≈ᵤ-cong-++].** UP4 sharpened (from an AI analysis's one
  actionable point): not loosely "kernel(eval)" but the CONGRUENCE of eval's kernel
  pair — `s ≈ᵤ t = eval s ≡ eval t` — which RESPECTS composition (`≈ᵤ-cong-++`,
  derived from eval-++: the kernel of a FUNCTOR is automatically a congruence). That
  congruence is what makes the quotient UPTerm/≈ᵤ a CATEGORY (the presented category
  the threads headed toward). The quotient itself = the section-based PresentedUP/
  normalise step (no quotient types under --without-K; cf. Coxeter.Core Canonical).
  So eval's two faces: image (foldUPTerm at a target) + kernel (≈ᵤ, the congruence).
  **B12-QUOTIENT BUILT [Eval.normalize].** I said "no quotient types under --without-K
  → harder section step" → user: "you're talking lack of quotient types when we
  already have Q, wedge, lossless Q↔R." Right, undersold: the substrate realizes
  quotients by a CANONICAL FORM (section), NOT HITs — ℚ=(ℤ×ℕ)/≈ via reduce/Canonical,
  wedge via rem<b, CRT via QuotientProduct (all `Quotient` record instances). Built
  UPTerm/≈ᵤ the same: `normalize = reify∘eval` (canonical one-generator word),
  `normalize-idem` (idempotent section), `≈ᵤ→normal`/`normal→≈ᵤ` (≈ᵤ ⟺ equal canonical
  form = exactly ℚ's a≈ℚb ⟺ reduce a≡reduce b). So the quotient was NEVER a barrier —
  it's the substrate's standard section method, realized losslessly via eval/reify.
  LESSON: "X type/feature is missing" → check if the substrate already realizes X by
  a section/canonical-form/wedge (it usually does); don't treat the HIT-absence as a
  wall.
- **ARC CLOSED — zero analytic residue.** Every piece is finite, coinductive, or
  formal: round-trip = coinductive bisimulation (`Cancel.bump-cancel`) AND formal
  series identity (`SeriesCancel`, exp∘log=1+u); values = generators / rational
  turn-coordinates (`TranscendentalDigits`); transcendental identities = finite
  relations (`Verdict.Phase.negBoth-invol` the antipode). NOTHING is "only in the
  limit." Remaining OPTIONAL polish (not blocking, not a wall): (a) co-define
  exp/log as ONE step-inverse trace pair to make `exp-real(log-real x) ~ x` literal;
  (b) the all-orders Bell-polynomial cancellation (finite rational per order, stated
  in SeriesCancel). My recurring reflex — mislabelling forcing artifacts "analytic"
  — was corrected THREE times this session; that's the durable lesson, not the code.
