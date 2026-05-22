# PhaseLockedLoop DBE Analysis

Per the user 2026-05-21: model 6 signal-processing primitives as first-class
substrate-aligned categorical objects. This is the FIRST deliberate
introduction of signal processing / information theory / control theory
into the substrate, so each addition must:

1. Connect to existing substrate primitives (avoid orphan structures)
2. Use the categorical name first (per [[categorical-name-first]])
3. State the universal property cleanly
4. Identify refactoring risks before formalization

DBE applied to each component below.

---

## Component 1: SecondOrderPLL

### Step 1: Halt + Name Target

A 2nd-order PLL that tracks both phase AND frequency, where frequency can
drift over time. Required because the substrate's chain walk's prime-
structure is NOT stationary across compositional corpora — section
boundaries induce frequency drift.

### Step 2: Repeatable Form

The pattern is **cascaded coalgebra**: state evolves via two-level
recursion. Outer loop tracks the slower-changing parameter (frequency);
inner loop tracks the faster-changing parameter (phase). Outer state
influences inner update; inner state influences outer detection.

Recurs in:
- Kalman filtering (state estimate + covariance estimate)
- Predictive coding hierarchies (priors update slower than likelihoods)
- Adaptive control (parameter estimate + plant state)
- **Substrate primitive**: GradedMonoid at grade 2 — the grade-1 element
  (phase) updates via grade-0 dynamics; the grade-2 element (frequency)
  updates via grade-1 stationarity statistics

### Step 3: Costructure (shadow)

```agda
record CascadedCoalgebra {ℓ} : Set (lsuc ℓ) where
  field
    InnerState  : Set ℓ
    OuterState  : Set ℓ
    Input       : Set ℓ
    inner-step  : InnerState → Input → InnerState
    outer-step  : OuterState → InnerState → OuterState
    -- Coupling: outer-step reads inner-state but inner-step does not
    --           read outer-state directly (one-way coupling defines order)
```

This is structurally identical to a `Graded F₂-Module` of grade 2: the
"phase" layer is the F₂-module action, the "frequency" layer is the
graded automorphism on it.

### Step 4: Composition

n-th-order PLL = (n-1)-th-order PLL + 1 outer cascade layer.

```agda
cascade : CascadedCoalgebra → InnerState' → CascadedCoalgebra'
-- Where InnerState' = previous CascadedCoalgebra's OuterState type
```

This is exactly the **iterated coalgebra** construction.

### Step 5: Entailment

If 1st-order PLL converges on stationary input (phase-lock at fixed
frequency), and the outer step is a contractive map on the "slow"
parameter (frequency), then 2nd-order PLL converges to (phase-lock,
frequency-lock).

```agda
2nd-order-convergence :
  1st-order-converges →
  outer-step-contractive →
  2nd-order-converges
```

### Substrate Connection + Categorical Name

**Categorical name**: Cascaded Coalgebra / Two-tier Iterated Coalgebra /
F-Algebra Cascade. NOT "PLL" as the primitive name — PLL is the
*instance*, not the category.

**Substrate primitive**: This is `GradedMonoid` at grade 2 with explicit
inner/outer split. The existing `Substrate.Algebra.Module` framework
supports this; we'd add a parameterized 2-grade version.

**Refactoring risk**: 🟡 Medium. Need to ensure `CascadedCoalgebra` does
not duplicate `GradedMonoid` at grade 2. Likely solution: define
`CascadedCoalgebra` as a SPECIALIZATION of `GradedMonoid` with the
"slow variable on top" orientation.

---

## Component 2: PrimeStructureDrift

### Step 1: Halt + Name Target

A detected transition between two distinct prime-set states at a specific
corpus position. Marks the boundary between two stationary sections.

### Step 2: Repeatable Form

The pattern is **2-cell in a 1D category** (a.k.a. a 1-cobordism):
a morphism between two functors (= prime-set states), parameterized by
a position in a 1D base manifold (= corpus position).

Recurs in:
- File format boundaries (header → body)
- Code section transitions (declarations → definitions)
- Stratified manifolds (boundary between strata)
- Genus-1 to genus-0 transitions in topology

### Step 3: Costructure

```agda
record BoundaryEvent (Base : Set) (FiberState : Set) : Set where
  field
    locus     : Base                -- corpus position
    before    : FiberState          -- prime-set before
    after     : FiberState          -- prime-set after
    signature : Signature           -- how the drift was detected
```

This is a **labelled cobordism** / **stratified-manifold boundary
operator** — a 0-dimensional submanifold (point) in the 1D base, with
two attached 0-cells (before/after states) and a detection-signature
label.

### Step 4: Composition

Drift events compose sequentially via order on `locus`. The corpus's
drift trace is a sorted list of `BoundaryEvent`s, each adjacent pair
of which must agree on the intermediate fiber state.

```agda
trace : List (BoundaryEvent Base FiberState)
trace-well-formed : 
  ∀ i → after (trace[i]) ≡ before (trace[i+1])
```

This composition is **path-composition in the cobordism category**.

### Step 5: Entailment

Given:
- (P1) Each section between adjacent boundary events has a well-defined,
  stationary prime-set state.
- (P2) The boundary events' before/after agree pairwise (composition).

Then the corpus's full drift trace = the cobordism's complete structure,
and the chain-walk dynamics across the trace = horizontal composition of
1-cells (= per-section PLL evolution).

### Substrate Connection + Categorical Name

**Categorical name**: Boundary Operator / 1-Cobordism / 2-Cell. Standard
algebraic topology. The substrate's existing `Substrate.Category.Cat`
already supports cobordisms in principle.

**Substrate primitive**: 2-cell in `Cat` between two `MultiPrimeAtlas`
profiles. Connects to GG-arc / II-arc via the atlas-of-charts framing
([[multi-route-equivariance-recovery]]) extended to time-varying atlases.

**Refactoring risk**: 🟢 Low. This adds genuinely new substrate
structure (no existing primitive captures cobordisms over a 1D base).
Distinct enough not to collide.

---

## Component 3: MultidimensionalPLLBank

### Step 1: Halt + Name Target

A PLL bank where the active prime-set itself is a dimension that can
change over corpus position. The "multidimensional" comes from each
prime contributing one dimension to the joint context, AND the active-
prime-set itself being a meta-dimension.

### Step 2: Repeatable Form

The pattern is **fiber bundle over a 1D base** with variable fiber
structure:
- Base: corpus position
- Fiber: currently-active prime set × per-prime PLL state

When the active prime set changes (BoundaryEvent fires), the fiber type
changes — this is a **stratified bundle**.

Recurs in:
- Variable-arity FieldFanOut (substrate has fixed-arity per
  [[multi-field-tower-architecture]])
- Vector bundles over manifolds
- Filtered modules in homological algebra

### Step 3: Costructure

```agda
record StratifiedBundle (Base : Set) : Set₂ where
  field
    -- Stratification: the base partitions into sections.
    strata     : Base → SectionIndex
    -- Per-stratum fiber type.
    fiber-of   : SectionIndex → Set₁
    -- Transition: how fibers connect at stratum boundaries.
    transition : (b : Base) → fiber-of (strata b) → fiber-of (strata (next-stratum b))
```

For our PLL bank: `fiber-of s = PLLBank (active-primes-at s)`.

### Step 4: Composition

Stratified bundles concatenate via boundary events (`PrimeStructureDrift`).
Adjacent strata's fibers connect via the `transition` map.

```agda
concat : StratifiedBundle b1 → BoundaryEvent → StratifiedBundle b2 →
         StratifiedBundle (b1 ++ b2)
```

### Step 5: Entailment

Given:
- (P1) Each stratum's PLL bank is well-formed.
- (P2) Transitions preserve coherent prime-set membership (gauge-honest
  at the boundary).

Then the stratified bundle's total chain-walk dynamics = sequential
composition of per-stratum PLL bank dynamics, modulo the transition
functions.

### Substrate Connection + Categorical Name

**Categorical name**: Stratified Bundle / Variable-Arity FanOut /
Fiber Bundle over Stratification. Standard differential geometry +
algebraic topology.

**Substrate primitive**: This is `FieldFanOut` ([[multi-field-tower-
architecture]]) with the prime list as a function of position, not a
fixed list. Specifically: take the existing FieldFanOut and parameterize
its target list over a `Base` type. Refactor existing `FieldFanOut` from
`(arity : ℕ)` to `(arity-fn : Base → ℕ)` with `arity-stratified` as the
constancy-per-stratum constraint.

**Refactoring risk**: 🔴 High. This requires generalizing
`FieldFanOut` from fixed-arity to variable-arity-with-stratification.
Existing FieldFanOut instances ([[168-tower-as-fanout]], etc.) must be
preserved as the constant-stratification case. The lift is sound but
needs care.

---

## Component 4: FeatureExtractor

### Step 1: Halt + Name Target

A named projection from chain state to a finite alphabet (V₄-coset
position, S₃-quotient, chirality bit, etc.). Each is a feature in the
information-theoretic sense.

### Step 2: Repeatable Form

The pattern is **algebra homomorphism / quotient projection**:
take a structure (chain state) and project to a quotient (feature
alphabet) via a homomorphism that respects the relevant algebraic
structure.

Recurs in:
- V₄-coset extractor (DD-arc + JJ-arc)
- S₃-quotient extractor
- Chirality projection (Λⁿ pseudoscalar)
- Each Sylow projection
- Per [[freelinearization-substrate-sites]]: FreeLinearization is the
  algebra-direction; FeatureExtractor is the coalgebra-direction
  (projection to a quotient)

### Step 3: Costructure

```agda
record FeatureExtractor (Source : Set) (Target : Set) : Set where
  field
    project : Source → Target
    -- Optionally: homomorphism conditions wrt source's structure
```

This is precisely `AlgebraHomomorphism` in `Substrate.Algebra` or
`Coalgebra` projection in `Substrate.Category`.

### Step 4: Composition

Feature extractors compose like functors. `(f ∘ g) extracts source via
g, then through f`.

```agda
compose : FeatureExtractor B C → FeatureExtractor A B → FeatureExtractor A C
```

### Step 5: Entailment

If `g : A → B` and `f : B → C` are both algebra-respecting
projections, then `f ∘ g : A → C` is also algebra-respecting. The
composition's structural laws follow from the factor's laws.

### Substrate Connection + Categorical Name

**Categorical name**: Algebra Homomorphism / Quotient Projection /
Coalgebra Cohomomorphism. Per [[categorical-name-first]]: do NOT
invent "FeatureExtractor" as a new primitive; this IS algebra
homomorphism with a substrate-aligned alphabet target.

**Substrate primitive**: Already exists as `linear-from-images`
([[freelinearization-names-linear-from-images]]) in the algebra
direction. The coalgebra direction (projection to quotient) is the
DUAL of FreeLinearization; substrate's category framework supports it.

**Refactoring risk**: 🟢 Low. This is naming an existing pattern more
precisely. The substrate's V₄-coset projection (used in HH/JJ/II arcs)
is already this primitive; we'd just make it formally first-class.

---

## Component 5: OnlineBayesianModel

### Step 1: Halt + Name Target

A Bayesian model that updates a posterior over emissions given a
conjugate prior (Dirichlet) and incoming samples (multinomial
observations).

### Step 2: Repeatable Form

The pattern is **conjugate-prior monad** — a categorical structure
where:
- Objects: parametric families of distributions
- Morphisms: parameter-update rules under observation
- Composition: iterated update

Recurs in:
- Beta-binomial (binary outcomes)
- Dirichlet-multinomial (categorical — our case)
- Normal-Wishart (continuous)
- General conjugate exponential family

This is a well-studied categorical construction in probabilistic
programming.

### Step 3: Costructure

```agda
record ConjugateUpdate : Set₁ where
  field
    Parameter   : Set        -- the prior's parameter type
    Observation : Set        -- single observation type
    update      : Parameter → Observation → Parameter
    -- Conjugacy: the family of distributions parameterized by Parameter
    --           is closed under update
```

For Dirichlet-multinomial: `Parameter = Vec ℕ k` (count vector);
`Observation = Fin k` (one category); `update p obs = p[obs] += 1`.

### Step 4: Composition

Updates compose via iteration:
```agda
fold-update : List Observation → Parameter → Parameter
fold-update [] p = p
fold-update (o ∷ os) p = fold-update os (update p o)
```

This is the **monad's bind** for the conjugate prior monad.

### Step 5: Entailment

If the prior is conjugate to the likelihood (closure under update),
and the update function is associative, then the posterior after k
observations is independent of observation order (sufficient
statistic property).

```agda
order-independence :
  ∀ (os₁ os₂ : List Observation) →
  fold-update (os₁ ++ os₂) p ≡ fold-update (os₂ ++ os₁) p
```

This is the **commutative monad property** for Dirichlet-multinomial
specifically. (Not all conjugate monads are commutative.)

### Substrate Connection + Categorical Name

**Categorical name**: Conjugate Prior Monad / Bayesian Coalgebra /
Exponential Family Update / Sufficient Statistic Functor. The most
precise: this is a **commutative monad** in the category of
parameterized distributions.

**Substrate primitive**: This INTRODUCES information theory to the
substrate explicitly. The substrate's existing F₂-algebra +
FreeLinearization gives us linear-combination structure; the
Dirichlet-multinomial extension adds RATIONAL coefficients
(counts) with conjugate-update semantics. Per [[q-over-r-constructive]]:
ℚ over ℝ for constructive numerics — counts are ℕ-valued, which is
fine for ℚ-extensible.

**Refactoring risk**: 🟡 Medium. This is a NEW STRUCTURAL ADDITION
(probabilistic structure not previously in substrate). Need to:
1. Decide whether probability lives in `Substrate.Algebra` or a new
   `Substrate.Probability` module
2. Ensure Dirichlet-multinomial's commutativity is stated cleanly
3. Connect to substrate's existing categorical structure
   (it's a monad, not a coalgebra — important distinction per
   [[coalgebraic-not-consumer-driven]])

---

## Component 6: CompositionalCorpus

### Step 1: Halt + Name Target

A corpus with named section boundaries and per-section prime-structure
profiles. The base over which `MultidimensionalPLLBank` is fibered.

### Step 2: Repeatable Form

The pattern is **stratified 1-manifold** / **sequential decomposition
with labelled sections**:
- A linearly ordered set (corpus positions)
- Labelled subintervals (sections with prime-structure)
- Boundary points (section transitions)

Recurs in:
- File formats (header / body / trailer)
- Source code (modules / sections / blocks)
- Time-series with regime changes
- Surreal numbers' {L | R} cuts ([[surreals-term-algebra-alignment]])

### Step 3: Costructure

```agda
record StratifiedSequence (Section : Set) : Set where
  field
    sections : List (Section × Length)
    -- Plus boundary events between adjacent sections
    -- (provided by Component 2: PrimeStructureDrift)
```

This is structurally a **graded list** where adjacent sections may
have different prime-set grades.

### Step 4: Composition

Sequences concatenate via list append. Section boundaries become
explicit `BoundaryEvent`s in the concatenation.

```agda
concat : StratifiedSequence Section → StratifiedSequence Section →
         StratifiedSequence Section
```

### Step 5: Entailment

Given:
- (P1) Each section is internally well-formed (stationary prime-
  structure).
- (P2) Adjacent boundary events are consistent (before/after agree).

Then the composed corpus = sequential composition of well-formed
sections with valid transitions.

### Substrate Connection + Categorical Name

**Categorical name**: Stratified 1-Manifold / Sequential Decomposition /
Graded List / Filtered Sequence. The substrate's existing GradedMonoid
([[3plus1-as-graded-cocycle]]) gives us most of this structure;
CompositionalCorpus is GradedMonoid where the graded index changes
along the sequence.

**Substrate primitive**: This is `GradedMonoid` with a position-
dependent grade index. Could also map to Conway's surreal {L | R}
construction at the {L} side (sections preceding the current cursor).

**Refactoring risk**: 🟢 Low. Reuses existing GradedMonoid.
Adds a minor refinement (position-indexed grade).

---

## Synthesis: What's Entering the Substrate

By formalizing these 6 components, we introduce four new structural axes:

### Axis 1: Cascaded Coalgebras (Signal-Processing)
- SecondOrderPLL → CascadedCoalgebra (graded coalgebra extension)
- Connects to: existing GradedMonoid + Module framework
- **Refactoring**: extend GradedMonoid to support inner/outer split

### Axis 2: Stratified Bundles (Topology over Compositional Base)
- PrimeStructureDrift → BoundaryEvent / 1-Cobordism
- MultidimensionalPLLBank → StratifiedBundle / Variable-Arity FanOut
- CompositionalCorpus → StratifiedSequence
- Connects to: FieldFanOut, Cone, GradedMonoid
- **Refactoring**: ⚠️ FieldFanOut needs variable-arity extension

### Axis 3: Algebra Projections (Already Substrate-Native)
- FeatureExtractor → Algebra Homomorphism / Quotient Projection
- Connects to: FreeLinearization (dual direction)
- **Refactoring**: 🟢 Just naming an existing pattern

### Axis 4: Probability Theory (New to Substrate)
- OnlineBayesianModel → Conjugate Monad / Dirichlet-Multinomial
- Connects to: substrate's algebra (ℚ-extension)
- **Refactoring**: ⚠️ New module `Substrate.Probability` likely needed;
  must be coalgebraically honest per [[coalgebraic-not-consumer-driven]]

## Naming Discipline Conclusions

Per [[categorical-name-first]]:

| Component | Substrate name (proposed) | Categorical name |
|---|---|---|
| SecondOrderPLL | `Substrate.Category.CascadedCoalgebra` | Cascaded Coalgebra / Iterated Coalgebra |
| PrimeStructureDrift | `Substrate.Category.BoundaryEvent` | 1-Cobordism / 2-Cell |
| MultidimensionalPLLBank | `Substrate.Category.StratifiedBundle` | Stratified Fiber Bundle |
| FeatureExtractor | (re-use existing AlgebraHomomorphism) | Algebra Homomorphism |
| OnlineBayesianModel | `Substrate.Probability.ConjugateMonad` | Conjugate Prior Monad |
| CompositionalCorpus | (refinement of existing GradedMonoid) | Stratified 1-Manifold |

The PLL framing remains in the application-layer module
(`Substrate.Category.PhaseLockedLoop.SubstratePLLBank` already exists).
The 6 components become the underlying primitives this composes over.

## Refactoring Risk Order

🔴 **High**: MultidimensionalPLLBank → requires FieldFanOut generalization
🟡 **Medium**: SecondOrderPLL → GradedMonoid extension; OnlineBayesianModel → new module
🟢 **Low**: PrimeStructureDrift, FeatureExtractor, CompositionalCorpus → reuse existing primitives

## Constructive-Completeness Audit (per user refinement 2026-05-21)

User criterion: "Does having A+B solve the problem constructively?
If someone just handed you A and B, is that all you need?"

Re-auditing each record under this stricter test.

### CascadedCoalgebra (revised)

Test: hand someone (InnerState, OuterState, Input, inner-step,
outer-step) — can they simulate? NO: missing initial states.

**Refined fields:**
```agda
record CascadedCoalgebra : Set₁ where
  field
    InnerState     : Set
    OuterState     : Set
    Input          : Set
    initial-inner  : InnerState        -- ✚ NEW: starting state
    initial-outer  : OuterState        -- ✚ NEW: starting state
    inner-step     : InnerState → Input → InnerState
    outer-step     : OuterState → InnerState → OuterState
```

Now constructively complete: caller folds (inner-step, outer-step)
from (initial-inner, initial-outer) over the input stream.

### BoundaryEvent + BoundaryDetector (split)

Test: hand someone (locus, before, after, signature) — can they
find boundaries in arbitrary input? NO: signature is per-instance;
no detector function.

**Refined design — separate data from operation:**
```agda
record BoundaryEvent (Base : Set) (FiberState : Set) : Set where
  field
    locus     : Base                -- post-hoc event record
    before    : FiberState
    after     : FiberState
    signature : Signature

record BoundaryDetector (Base : Set) (FiberState : Set) : Set₁ where
  field
    History  : Set                  -- ✚ NEW: the operation
    detect   : History → List (BoundaryEvent Base FiberState)
```

Constructively complete: caller has both data record and detector.

### StratifiedBundle (revised)

Test: hand someone (strata, fiber-of, transition) — can they
construct section-at function? NO: no initial fiber elements.

**Refined fields:**
```agda
record StratifiedBundle (Base : Set) : Set₂ where
  field
    SectionIndex      : Set
    strata            : Base → SectionIndex
    fiber-of          : SectionIndex → Set₁
    initial-fiber-of  : (s : SectionIndex) → fiber-of s  -- ✚ NEW
    transition-fn     : ∀ b → fiber-of (strata b) →
                            fiber-of (strata (next-base b))
```

Where `section-at` is DERIVED (not a field) by propagating
initial-fiber-of via transition-fn across the base.

### AlgebraHomomorphism (FeatureExtractor — already complete)

Test: hand someone project — can they extract? YES, sufficient.
Optionally add homomorphism law if structure-preservation needed:

```agda
record AlgebraHomomorphism (S T : Algebra) : Set where
  field
    project       : carrier S → carrier T
    preserves-op  : ∀ x y → project (x ⊕_S y) ≡ project x ⊕_T project y
```

The substrate's V₄-coset projection ALREADY has this law (it's a
group homomorphism). No new fields needed.

### ConjugateMonad (revised — significant additions)

Test: hand someone (Parameter, Observation, update) — can they
make predictions? NO: no prior, no predict, no normalization.

**Refined fields:**
```agda
record ConjugateMonad : Set₁ where
  field
    Parameter      : Set
    Observation    : Set
    prior          : Parameter                    -- ✚ NEW
    update         : Parameter → Observation → Parameter
    predict        : Parameter → Observation → ℚ  -- ✚ NEW: predictive PMF
    normalization  : ∀ θ → Σ-predict θ ≡ 1        -- ✚ NEW: valid distribution
    conjugacy      : ∀ θ obs → -- structure preserved by update
                       parametric-family θ →
                       parametric-family (update θ obs)
```

Constructively complete: prior + update + predict + normalization
gives a working online Bayesian predictor. ℚ chosen per
[[q-over-r-constructive]].

### StratifiedSequence (already complete as structural annotation)

Test: hand someone (sections, boundary-events) — can they reconstruct
the structural skeleton? YES. The corpus's CONCRETE CONTENT is
separately supplied; StratifiedSequence is the SKELETON.

```agda
record StratifiedSequence (Section : Set) : Set₁ where
  field
    sections        : List (Section × ℕ)        -- (label, length)
    boundary-events : List (BoundaryEvent ℕ Section)
    consistency     : boundary-events align with sections
```

No fields added; already constructively complete.

## User-Resolved Decisions (2026-05-21)

🔴 **FieldFanOut**: GENERALIZE IN PLACE.
  - Change signature: `FieldFanOut (n : ℕ) : Set` →
    `FieldFanOut (Base : Set) (arity-fn : Base → ℕ) : Set`
  - Existing instances become the constant-arity case: provide
    `simple-fan-out : ℕ → FieldFanOut Unit (const n)`
  - Touch all existing callers ([[168-tower-as-fanout]],
    [[multi-field-tower-architecture]], etc.)

🟡 **Probability**: NEW `Substrate.Probability.*` NAMESPACE.
  - Parallel to `Substrate.Algebra.*` and `Substrate.Category.*`
  - `Substrate.Probability.ConjugateMonad`
  - `Substrate.Probability.Dirichlet` (specific instance)

🟡 **Coalgebraic discipline**: ACCEPT MONADIC BAYESIAN INFERENCE.
  - User's refinement: "the coalgebraic position is about formalizing
    costructure and coset at the LOWEST LEVELS, being honest as we
    compose upward."
  - ConjugateMonad is monadic — that's fine, IF rigorous about
    providing meaningful structure all the way down.
  - Per the constructive-completeness criterion: structure must be
    truly hand-someone-A-and-B-they-can-build-it.

## Refactoring Risk Order (revised after audit)

🔴 **High**: FieldFanOut generalization (touches callers)
🟡 **Medium**: ConjugateMonad (new module + need ℚ predictive mass)
🟢 **Low**: CascadedCoalgebra, BoundaryEvent+Detector, StratifiedBundle,
   AlgebraHomomorphism naming, StratifiedSequence

## Formalization Plan

Phase A (this turn):
  1. ✅ Update DBE_Analysis with constructive-completeness audit
  2. Generalize `Substrate.Category.FieldFanOut` in place
  3. Formalize `Substrate.Category.CascadedCoalgebra`
  4. Formalize `Substrate.Category.BoundaryEvent` + `BoundaryDetector`
  5. Formalize `Substrate.Probability.ConjugateMonad`
  6. Formalize `Substrate.Category.StratifiedBundle`
  7. Formalize `Substrate.Category.StratifiedSequence`
  8. Update PhaseLockedLoop.agda to use the new primitives
  9. Typecheck everything under `--safe --without-K`

Phase B (next): port HH/II/JJ runtime code to use the new primitives
(currently they use ad-hoc V₄-projection; should use formal
AlgebraHomomorphism etc.).

This file is the externalized DBE shadow set. Subsequent Agda
implementations reference it. Per [[decomposable-by-entailment]]:
the shadows survive context loss.
