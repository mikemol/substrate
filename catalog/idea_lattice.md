# Idea lattice

Structural-dependence ordering of the substrate's concepts and
claims. Each level depends only on levels above it; reading top-to-
bottom gives the reconstruction sequence. Concepts are tagged
`[gauge]` when they are a gauge degree of freedom (an operational
choice) and `[invariant]` when they are gauge-invariant content (a
structural commitment that survives gauge changes). This separation
is the *key tool* for a clarified rewrite: future implementations
should encode `[invariant]` content as load-bearing structure and
`[gauge]` choices as parametrised conventions.

The 9 levels below correspond loosely to M-move epochs but are not
identical with them — M-numbering is the *chronological* order of
the development conversation, retrofitted; the lattice is the
*structural* order that future-you should follow to reconstruct.

## Level 0 — foundations (M1 Context)

The framing rules. Everything else is constrained by these.

- **C-realizability-charter** [invariant]: every distinction must
  satisfy constructible → reachable → observable → coverable.
- **C-hashcons** [invariant]: structurally-identical rules share
  reference.
- **C-acyclicity** [invariant]: rule k references only rules with
  index < k.
- **C-monotonic-growth** [invariant]: chart only grows.
- **LEM-rejection** [invariant — repo discipline]: P ∨ ¬P is not
  automatic; ¬P requires constructive P ⊢ ⊥. See
  [README § Epistemic discipline](README.md#epistemic-discipline-lem-is-rejected).

## Level 1 — founding micro-ops (M1)

The six (later seven) primitives. Everything term-algebraic derives
from these.

- **C-nil** [invariant]: well-founded base.
- **C-cons** [invariant]: binary constructor with hash-consing.
- **C-leftright** [invariant]: projections.
- **C-eq** [invariant]: decidable structural equality.
- **C-apply** [invariant]: the realizability ground. *Refined to
  single-step at M4.*
- **C-parse** [invariant]: parse under the live grammar; routes
  through cons.
- **C-apply-single-step** [invariant]: M4 refinement.

Underlying claim: [K-six-micro-ops-suffice](claims.md).

## Level 2 — representation gauge (M2 — gauge stratum)

**The first cocycle.** Representations of rule references are
gauge-equivalent under transform morphisms.

- **C-representation-multiplicity** [gauge]: four representations
  are first-class.
- **C-transform** [gauge]: S7 morphism between representations
  (operationally empty bridge — see [CY-1](cocycles.md#cy-1--representation-cocycle-m2)).
- **rule-identity** [invariant]: the abstract rule the
  representations encode (each fiber's gauge-invariant content).

This is the FIRST cocycle in the project; the M8 cohomological
framing later generalises it.

## Level 3 — algebraic substrate (M5–M8)

The substrate's algebraic identity, plus the framing for everything
gauge-structural that follows.

- **C-chart-as-memoization** [invariant]: hash-consing IS
  memoization.
- **C-formal-system** [invariant]: free magma on `cons` mod
  hash-cons.
- **C-associahedron-K_n** [invariant]: composition coherence
  (becomes per-Hadamard-level at M24).
- **C-cocycle-projection** [framing]: the cohomological vocabulary
  for gauge structures across the corpus. M2's polytope = M8's
  cocycle in different vocabulary (see
  [entailment.md § M2 ≈ M8](entailment.md#m2-representational-multiplicity--m8-cocycle-same-pattern-different-vocabulary)).

## Level 4 — chart kernel + meta-circularity (M9–M11, M14, M17)

The runnable substrate plus the first meta-rule layer with its own
gauge structure.

- **C-chart-kernel** [invariant]: concrete implementation of
  Level-1 micro-ops with M3's structural choices fixed.
- **C-meta-circular-fixpoint** [invariant]: `apply(parser,
  grammar-text)` is the L₅-closing fixpoint.
- **C-K-marker-variables** [invariant]: M14's K-marker variables
  for K-rule pattern positions.
- **C-K-rule-gauge** [gauge — second cocycle]: S_n renaming on
  K-rule variable positions; cohomology classes = {off-diagonal,
  diagonal}. See [CY-2](cocycles.md#cy-2--k-rule-variable-cocycle-m17).

## Level 5 — coding-theoretic layer (M18–M21)

The architectural identification of the rule structure as a Reed-
Muller / Hamming family.

- **C-RM-1-3** [invariant]: tier-1 default_table = Reed-Muller code
  RM(1, 3).
- **C-parity-basins** [gauge — emerges as basis of CY-3]: parity
  basins partition RM codewords; the equivalence will become
  CY-3's gauge.
- **C-hamming-7-4** [invariant]: punctured RM = Hamming(7, 4).
- **C-walsh-hadamard-quotient** [gauge — third cocycle]: parity-
  basin equivalence on WHT codewords. See [CY-3](cocycles.md#cy-3--wht-quotient-cocycle-m22).
- **C-hamming-scaling** [invariant]: family (n=2^m−1, k=n−m, d=3);
  symmetry GL(m, F₂); ambient PG(m−1, F₂).
- **C-stasheff-at-hadamard** [invariant]: K_n at each Hadamard
  level. M7 realised here.

## Level 6 — F₂³ gauge / DCSW emergence (M22-bis–M24-bis)

The architectural reframing: 8 puncturings, F₂³ gauge, S as pivot,
DCSW axes as the operational substrate.

- **C-eight-puncturings** [gauge — fourth cocycle base]: 8 RM(1,3)
  puncturings form an F₂³ torsor. See
  [CY-4](cocycles.md#cy-4--f_23-puncturing-gauge-cocycle-m22-bis).
- **C-S-gauge-pivot** [invariant]: S is the gauge-invariant pivot
  of the 8-frame rotation.
- **C-DCSW-axes** [gauge — naming convention]: the 4-axis label
  set {D, C, S, W}. **This is a labelling convention, not a
  primitive** — see
  [drift_archaeology.md § Finding 3](drift_archaeology.md) for the
  retconned argument that the user attempted.
- **C-triadic-decomposition** [invariant]: (D × C × S) factoring; W
  emerges via Hodge ★ in dim 4.

## Level 7 — V₄ / S₄ programme (M28–M37)

The Klein-four / symmetric group structure on DCSW; the resolution
of the V₄-twin programme.

- **C-V4-Klein** [invariant — group structure]: V_4 = three double-
  transpositions + identity.
- **C-V4-twins** [invariant — but historically aspirational]: V_4-
  related operations. Existence-form findings now recorded
  ([K-v4-twins-partial-inhabitation](claims.md), 9/9 coherent
  after the M33 reclassification).
- **K-chirality-is-parity** [invariant]: chirality = sign of S_4
  permutation. Q-Z2 quotient (see [cocycles.md](cocycles.md#q-z2--chirality-m34)).
- **K-Z3-is-4axis-generator** [invariant]: Z_3 = A_4 / V_4 generates
  4-axis chained operations. Q-Z3 quotient.
- **K-V4-extension-completes-S4-orbit** [invariant]: V_4 extension
  completes the S_4 orbit through any A_4 element.

## Level 8 — architectural identification (M38–M40)

The closure: the architectural symmetry group is named (A_4 × Z_2),
distinguished from S_4, with Hadamard-mixing as the principal
operation.

- **C-unified-hamming-address** [invariant]: 5-bit codeword layout
  encoding (chirality, pairing, witness). *Bit positions are a
  partially-motivated Type-D rigidification.*
- **C-symmetry-governed-mixing** [invariant — principle]: the
  architecture is Hadamard-basis mixing under some symmetry. M40
  fills in *which* symmetry.
- **C-architecture-WHT** [invariant]: architecture = WHT system
  (Fourier identification).
- **C-A4-Z2-group** [invariant — load-bearing]: closure of
  admissible generators is A_4 × Z_2, not S_4. Distinguished by
  center order (|Z| = 2 vs 1). See
  [K-M40-aggregator](claims.md).
- **C-oriented-affine-even-vs-full-affine** [invariant]: V_4 ⋊ A_3
  + central chirality vs V_4 ⋊ GL_2(F₂) — both order 24, non-
  isomorphic.

## Level 9 — M41 structural-address stack

The verification edifice: every operation gets a structural address
in the V_4 ⋊ S_3 ≅ S_4 algebra; every receipt content-addresses
through it.

- **C-V4-semidirect-S3** [invariant — primary algebra]: S_4 ≅
  V_4 ⋊ S_3 where S_3 is Stab(D). **D-as-anchor is a Type-D
  rigidification** (Stab(C/S/W) would be equally valid).
- **C-hodge-star-dim4** [invariant]: 32 = |S_4| + 2·dim(Λ¹) = 24 +
  8 (Hodge ★ pairs ordered-triples and signed-singletons).
- **C-cayley-dickson-seam** [invariant]: |S_n| vs 2^n; at level 4
  the parity-sieve ratio is 24/32 = 3/4.
- **C-orbit-canonical-decomposition** [gauge — fifth cocycle]:
  signatures decompose as (orbit_key, v4_delta). **Lex-min canonical
  is a Type-D rigidification** (any V_4 translate is mathematically
  valid). See [CY-5](cocycles.md#cy-5--v_4-signature-cocycle-m41-v16v19).
- **C-structural-address** [invariant]: StructuralAddress as
  object-first identity.
- **C-codeword-address-bijection** [invariant]: codeword ↔ address
  inversion.
- **C-parity-sieve** [invariant]: characterises the 24 valid
  signatures within the 32 raw codewords.
- **C-addressed-op** [invariant]: AddressedOp = (op_name, address)
  bundle; accepted by all three receipt constructors.
- **C-registry-domain** [invariant]: REGISTRY_DOMAIN separator on
  digests.
- **C-receipt-sumtype** [invariant]: three disjoint receipt
  constructors.
- **C-transactional-verification** [invariant]: snapshot → test →
  classify → restore; verification is observationally pure.
- **C-grade-meet-monoid** [invariant]: verification grades form a
  meet-monoid.

## The lattice as visible cocycle tower

Reading the levels through the [cocycle catalog](cocycles.md):

| Level | Layer / cocycle | Gauge | Invariant becomes Level… |
|-------|-----------------|-------|--------------------------|
| 2 | CY-1 representation | transform morphisms | rule identity (Level-3 base) |
| 4 | CY-2 K-rule variables | S_n renaming | partition refinement |
| 5 | CY-3 WHT quotient | parity-basin | Walsh-row index |
| 6 | CY-4 F_2³ puncturings | F_2³ translation | the WHT core (Level-7 base) |
| 9 | CY-5 V_4 signatures | V_4 axis swaps | orbit_key (becomes content-address) |

Five nested cocycles produce the tower; the M40 aggregator names
its closure (A_4 × Z_2); the M41 stack content-addresses operations
through the bottom.

## Gauge / invariant separation as a recovery rule

The catalog's drift findings show that **Type-D rigidifications
occur exactly when [gauge] concepts get coded as [invariant]**:

- Lex-min canonical was the implementation collapsing
  C-orbit-canonical-decomposition (Level-9 gauge) into a fixed
  reference frame.
- AXES = ('D','C','S','W') was the implementation collapsing
  C-DCSW-axes (Level-6 gauge / labelling convention) into a fixed
  tuple.
- D-as-anchor was the implementation collapsing the choice of
  S_3 = Stab(?) into Stab(D).
- Integer-as-path empty bridge was the implementation collapsing
  C-representation-multiplicity (Level-2 gauge) into a single
  implemented case.

In every case, the discipline rule is the same: **`[gauge]`-tagged
concepts should appear in code as parameters or `# Convention:`
comments, never as verified contracts**. The
[clarified foundation](clarified_foundation.md) operationalises this
rule per layer.

## Cross-references

- [Cocycle catalog](cocycles.md) — the five cocycles' normalised
  records.
- [Clarified foundation](clarified_foundation.md) — the minimum
  axiomatic base for a reconstruction.
- [Concepts](concepts.md) and [claims](claims.md) — the records this
  lattice indexes.
- [Drift archaeology](drift_archaeology.md) — where the
  rigidifications crept in.
