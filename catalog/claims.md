# Claims

Propositions the corpus attempts (or attempted) to establish, with
status, evidence, and concepts used. See [concepts.md](concepts.md) for
C-ids and [README.md](README.md) for status semantics.

## Foundational entailment claims (M1)

### K-six-micro-ops-suffice
- **Statement**: The six micro-ops {nil, cons, left/right, eq, apply,
  parse} are necessary and sufficient to ground a free self-extending
  grammar under the stated [C-realizability-charter].
- **Introduced**: M1.
- **Evidence**: [cotype-free-self-extending-grammar.md:14-99].
- **Status**: shown by entailment construction (M1 is a pure-GS lift;
  each shadow's necessity is argued from the constraints).
- **Concepts**: C-nil, C-cons, C-leftright, C-eq, C-apply, C-parse,
  C-hashcons, C-acyclicity.

### K-apply-grounds-realizability
- **Statement**: `apply` is the unique micro-op that cannot be defined
  purely in the grammar's own term algebra; it grounds the topos's
  exponential objects.
- **Introduced**: M1 (S5 entailment).
- **Evidence**: [cotype-free-self-extending-grammar.md:46-50].
- **Status**: shown by argument; no executable witness in this repo.
- **Concepts**: C-apply.

### K-charter-honored-corpus-wide
- **Statement**: Every distinction introduced in any major move from
  M26 onward passes the four-stage realizability charter
  (constructible → reachable → observable → coverable), exhibited
  via explicit per-move charter-check tables.
- **Introduced**: derived (realisation of C-realizability-charter
  across the corpus); the practice stabilises at M26.
- **Evidence**: 14 charter-check tables — see [entailment.md
  § Charter-check practice → M1 realizability charter](entailment.md#charter-check-practice--m1-realizability-charter)
  for the full list with line anchors.
- **Status**: shown via repeated witness across the corpus.
- **Concepts**: C-realizability-charter.
- **Editorial note**: this claim was not originally authored in the
  narrative; it is the catalog's reading of a pattern the corpus
  consistently exhibits. The M1 charter is therefore not a manifesto
  but a *practiced discipline*.

## Representation algebra (M2–M4)

### K-representations-associahedron
- **Statement**: Rule representations form vertices of an associahedron-
  like polytope; transforms between them are edges; cycles compose to
  identity (Stasheff coherence).
- **Introduced**: M2.
- **Evidence**: [cotype-free-self-extending-grammar.md:116-150].
- **Status**: shown via three parallel realisations at three
  operational layers (M17 K-rule variables / M22 WHT codewords /
  M41 v16+v19 signatures). M2 and M8 are alternative vocabularies
  for the same gauge-equivalence pattern; the three M8-realising
  claims also realise M2 with different gauge groups (S_n /
  parity-basin / V_4). The "topos's freedom" of M2's commitment #4
  is concretely exercised at
  [../applied_grammar.py:923-931](../applied_grammar.py)
  (`canonical_signature_in_orbit` picks lex-min over V_4 translates;
  any translate could have been canonical). Higher-cell coherence
  remains abstract in M2's strict sense but the gauge structure the
  polytope encodes is fully operational. See [entailment.md § M2
  representational multiplicity ≈ M8 cocycle](entailment.md#m2-representational-multiplicity--m8-cocycle-same-pattern-different-vocabulary).
- **Concepts**: C-representation-multiplicity, C-transform,
  C-associahedron-K_n.

### K-apply-single-step-terminates-structurally
- **Statement**: Refining `apply` to single-step reduction makes
  non-termination a structural property of the chart (a fixed-point
  approached over time) rather than a runtime exception.
- **Introduced**: M4.
- **Evidence**: [cotype-free-self-extending-grammar.md:196-253].
- **Status**: shown by re-specification of S5; not implemented in the
  committed code.
- **Concepts**: C-apply-single-step, C-monotonic-growth.

## Algebraic / cohomological (M5–M8)

### K-chart-is-memoization
- **Statement**: Hash-consing **is** memoization for `apply`; no separate
  cache.
- **Introduced**: M5.
- **Evidence**: [cotype-free-self-extending-grammar.md:254-309].
- **Status**: shown by identification.
- **Concepts**: C-chart-as-memoization, C-hashcons.

### K-formal-system-algebraic
- **Statement**: The substrate is the free magma on the binary
  constructor modulo hash-consing.
- **Introduced**: M6.
- **Evidence**: [cotype-free-self-extending-grammar.md:310-402].
- **Status**: shown via pair-realisation. M6's algebraic commitment
  was necessary-but-not-sufficient; the corpus grounds the formal
  system in TWO mutually-constraining algebraic structures —
  term-algebra (chart_chained / applied_grammar: cons-tree free
  magma + hash-cons + apply) and symmetry-algebra (meta_protocol /
  s4_structure: V_4 ⋊ S_3 ≅ S_4 + Hodge ★ in dim 4 + Cayley-Dickson
  seam). The spokesperson claim K-V4-semidirect-S3-is-primary (M41
  v19) ties them together via AddressedOp / StructuralAddress. The
  realisation also *strengthens* M6 — the formal system is more
  than a free magma; it is a free magma whose operation set carries
  an S_4 symmetry verified end-to-end. See [entailment.md § M6
  algebraic commitment realised as a term-algebra / symmetry-algebra
  pair](entailment.md#m6-algebraic-commitment-realised-as-a-term-algebra--symmetry-algebra-pair).
- **Concepts**: C-formal-system, C-cons, C-V4-semidirect-S3.

### K-K_n-coherence-for-composition
- **Statement**: Rule composition is governed by the Stasheff
  associahedron K_n; re-associations beyond binary are higher-cell
  coherences.
- **Introduced**: M7.
- **Evidence**: [cotype-free-self-extending-grammar.md:403-471].
- **Status**: shown via realisation by K-stasheff-per-hadamard-level
  (M24). The abstract K_n framing is instantiated concretely at each
  Hadamard level m as K_{2^m-1}. See [entailment.md § Subsidiary
  realisation: M7 → M24](entailment.md#subsidiary-realisation-m7--m24).
- **Concepts**: C-associahedron-K_n.

### K-cocycle-unifies-formal-systems
- **Statement**: Multiple formal systems unify via projection from a
  cocycle in the cohomology of representational changes.
- **Introduced**: M8.
- **Evidence**: [cotype-free-self-extending-grammar.md:472-537].
- **Status**: **shown via three parallel realisations** at three
  operational levels:
  - K-K-rule-gauge-structure (M17) — S_n renaming gauge on K-rule
    variable assignments; orbits as cohomology classes.
  - K-WHT-quotient-algebra (M22) — parity-basin equivalence on WHT
    codewords; the WH projection IS the cocycle projection.
  - K-orbit-canonical-bijection (M41 v16+v19) — V_4 axis-swap gauge
    on signatures; orbit_key (∈ Stab(D)-representatives) is the
    cohomology class, v4_delta is the gauge.
  All three realisations share the same cohomological pattern
  ("orbits as cohomology classes; quotient is gauge-invariant data")
  with different specific gauge groups. See [entailment.md
  § M8 cocycle → three parallel realisations](entailment.md#m8-cocycle--three-parallel-realisations).
- **Concepts**: C-cocycle-projection, C-walsh-hadamard-quotient.

## Chart kernel and self-extension (M9–M11)

### K-chart-kernel-implements-micro-ops
- **Statement**: The chart kernel artefact correctly implements the six
  M1 micro-ops with the M3-fixed structural choices.
- **Introduced**: M9.
- **Evidence**: [cotype-free-self-extending-grammar.md:538-595].
- **Status**: **referenced but absent** in committed code; the imports
  to `chart_chained` in [../applied_grammar.py:175](../applied_grammar.py)
  and [../verify_applied_grammar.py:15](../verify_applied_grammar.py)
  cannot be resolved from this repo alone. See drift.
- **Concepts**: C-chart-kernel.

### K-self-extension-closes-L5
- **Statement**: `apply(parser-rule, grammar-text)` is a fixpoint that
  closes the L₅ line (triadic-full axis-signature 111).
- **Introduced**: M11 (first instance).
- **Evidence**: [cotype-free-self-extending-grammar.md:655-713].
- **Status**: shown by structural argument.
- **Concepts**: C-meta-circular-fixpoint, C-line-discipline.

### K-DBE-applied-to-itself
- **Statement**: The decompose-by-entailment procedure, when run on the
  grammar, yields shadows that are exactly the grammar rules used to
  extend itself.
- **Introduced**: M11 (second instance, line 714).
- **Evidence**: [cotype-free-self-extending-grammar.md:714-839].
- **Status**: shown by exhibition.
- **Concepts**: C-operational-meta-circularity.

## Tier-2 and beam search (M12–M17)

### K-tier2-regroup-well-formed
- **Statement**: The tier-2 regroup of M11 under M13's vertex with
  K-marker variables produces a well-formed decomposition that
  preserves L₅ closure.
- **Introduced**: M12–M14.
- **Evidence**: [cotype-free-self-extending-grammar.md:840-1185].
- **Status**: partial — regroup constructed; meta-principle audit
  follows at M15.
- **Concepts**: C-K-marker-variables.

### K-meta-principle-lifted
- **Statement**: A closure audit can be lifted to the meta-principle
  level (axis 101: guard-cleared lift against goal-artefact smuggling).
- **Introduced**: M15.
- **Evidence**: [cotype-free-self-extending-grammar.md:1186-1283].
- **Status**: shown.
- **Concepts**: C-axis-signature.

### K-table2-minimal
- **Statement**: The minimal table₂ (tier-2 instruction table) exists
  and is found by beam search.
- **Introduced**: M16.
- **Evidence**: [cotype-free-self-extending-grammar.md:1284-1338].
- **Status**: shown computationally (beam search reported as completed).
- **Concepts**: C-K-rule-gauge.

### K-K-rule-gauge-structure
- **Statement**: K-rule variable assignments admit a gauge structure;
  the table₂ minimum is unique only up to this gauge.
- **Introduced**: M17.
- **Evidence**: [cotype-free-self-extending-grammar.md:1339-1410].
- **Status**: shown. Also `realizes` K-cocycle-unifies-formal-systems
  at the K-rule layer (the S_n renaming gauge gives orbits as
  cohomology classes; M17 explicitly identifies this as the M8
  cocycle structure becoming directly observable).
- **Concepts**: C-K-rule-gauge.

## Coding-theoretic layer (M18–M22)

### K-default-table-is-RM-1-3
- **Statement**: `default_table` is the Reed-Muller code RM(1, 3).
- **Introduced**: M19.
- **Evidence**: [cotype-free-self-extending-grammar.md:1504-1580].
- **Status**: shown by identification.
- **Concepts**: C-RM-1-3.

### K-parity-basins-rotational
- **Statement**: RM(1, 3) codewords partition into parity basins under
  a rotation action; basin transitions are parity-guarded.
- **Introduced**: M20.
- **Evidence**: [cotype-free-self-extending-grammar.md:1581-1667].
- **Status**: shown.
- **Concepts**: C-parity-basins.

### K-punctured-RM-is-Hamming
- **Statement**: Puncturing RM(1, 3) by one coordinate yields the
  perfect Hamming(7, 4) code; content bits ↔ rule body, parity bits ↔
  axis-signature.
- **Introduced**: M21.
- **Evidence**: [cotype-free-self-extending-grammar.md:1668-1751].
- **Status**: shown.
- **Concepts**: C-hamming-7-4, C-RM-1-3, C-axis-signature.

### K-WHT-quotient-algebra
- **Statement**: Architecture factors as data × compute × state under
  the Walsh-Hadamard quotient algebra; axis-signatures index Walsh
  rows of WHT_8.
- **Introduced**: M22 (first instance).
- **Evidence**: [cotype-free-self-extending-grammar.md:1752-1873].
- **Status**: shown (identification + table at line 1801).
- **Concepts**: C-walsh-hadamard-quotient, C-axis-signature.

## Scaling and gauge (M23–M27)

### K-hamming-family-scales
- **Statement**: The Hamming family scales as n = 2^m − 1; symmetry
  group GL(m, F₂); ambient projective space PG(m−1, F₂).
- **Introduced**: M23 (first instance).
- **Evidence**: [cotype-free-self-extending-grammar.md:1874-2026].
- **Status**: shown by the scaling-hierarchy table (4× `table_*`
  predicates in retrospective theme signal for this move).
- **Concepts**: C-hamming-scaling.

### K-stasheff-per-hadamard-level
- **Statement**: Each Hadamard level m has its own K_{n=2^m-1} Stasheff
  polytope governing composition tradeoff.
- **Introduced**: M24 (first instance).
- **Evidence**: [cotype-free-self-extending-grammar.md:2027-2220].
- **Status**: stated; cell-by-cell coherence not exhaustively verified.
- **Concepts**: C-stasheff-at-hadamard.

### K-F2-3-gauge-on-puncturings
- **Statement**: The 8 puncturings of RM(1, 3) form an F₂³ torsor; the
  WH core is gauge-invariant, the translation gauge is F₂³.
- **Introduced**: M22-bis (renumbered, line 2221).
- **Evidence**: [cotype-free-self-extending-grammar.md:2221-2331].
- **Status**: shown.
- **Concepts**: C-eight-puncturings.

### K-S-is-pivot
- **Statement**: The state axis S is the gauge-invariant pivot of the
  8-frame rotation; (D, C, W) rotate around it.
- **Introduced**: M23-bis.
- **Evidence**: [cotype-free-self-extending-grammar.md:2332-2454].
- **Status**: shown.
- **Concepts**: C-S-gauge-pivot, C-DCSW-axes.

### K-triadic-with-witness
- **Statement**: Computation triadically factors as (D × C × S) with W
  emerging as the dim-4 Hodge ★ of the triadic system.
- **Introduced**: M24-bis (line 2455); formalised at M41 v19.
- **Evidence**: [cotype-free-self-extending-grammar.md:2455-2582],
  [../s4_structure.py:14-21](../s4_structure.py).
- **Status**: shown via Hodge identification at v19.
- **Concepts**: C-triadic-decomposition, C-hodge-star-dim4.

### K-gauge-is-semantic-axis
- **Statement**: The scratch (workspace) axis IS the semantic axis —
  the gauge degree of freedom carries the semantic content.
- **Introduced**: M27.
- **Evidence**: [cotype-free-self-extending-grammar.md:2868-3036].
- **Status**: stated.
- **Concepts**: C-DCSW-axes.

## V₄ / S₄ programme (M28–M37)

### K-v4-under-explored
- **Statement**: A coverage analysis using V₄ / Klein-four orbits
  identifies an under-explored region of the structural space.
- **Introduced**: M28.
- **Evidence**: [cotype-free-self-extending-grammar.md:3037-3177].
- **Status**: shown.
- **Concepts**: C-V4-Klein.

### K-state-machine-verified
- **Statement**: A formal state machine for the under-explored region
  is constructible and verifiable.
- **Introduced**: M29.
- **Evidence**: [cotype-free-self-extending-grammar.md:3178-3304].
- **Status**: shown (axis 111).
- **Concepts**: —

### K-F-populated
- **Statement**: The state set F can be populated to cover the entire
  state space using V₄-twins.
- **Introduced**: M30 (first twins), M31 (full population).
- **Evidence**: [cotype-free-self-extending-grammar.md:3305-3547].
- **Status**: shown.
- **Concepts**: C-V4-twins.

### K-v4-twins-fail-cells (rejected; replaced by K-v4-twins-cell-labels-aspirational and K-v4-twins-partial-inhabitation)
- **Statement (as authored)**: "Implementations do not fully honor
  their claimed V₄ cells; V₄-twin claims fail structurally under
  strict inhabitation audit."
- **Introduced**: M33 (line 3653, "fail structurally"), restated
  at final M33 (line 8029, "implementations don't fully honor their
  claimed V₄ cells").
- **Evidence**: [cotype-free-self-extending-grammar.md:3653-3782],
  [cotype-free-self-extending-grammar.md:8029-8157],
  [../scratch/audit_inhabitation.py](../scratch/audit_inhabitation.py),
  [../scratch/verify_cell_inhabitation.py](../scratch/verify_cell_inhabitation.py).
- **Status**: **rejected-as-overclaim** under
  [README § Epistemic discipline](README.md). The claim's universal
  form is unwarranted; the audit's actual content (run 2026-05-15
  on Python 3.13 with scratch/ on PYTHONPATH) is positive and
  cleanly decomposable. Replaced by the two existence-form claims
  below.
- **Concepts**: C-V4-twins.

### K-v4-twins-partial-inhabitation
- **Statement** (existence-form): there exist 4 of 9 audited
  operations that exhibit structural V₄ coherence at runtime —
  their axis-engagement profiles honor the V₄ cell their nominal
  classification claims.
- **Introduced**: derived from the audit by LEM-rejection-aware
  restatement (2026-05-15).
- **Evidence**: [../scratch/verify_cell_inhabitation.py](../scratch/verify_cell_inhabitation.py)
  output: `4/9 operations are STRUCTURALLY V₄-coherent`.
- **Status**: shown (executable witness).
- **Concepts**: C-V4-twins, C-V4-Klein.

### K-v4-twins-cell-labels-aspirational
- **Statement** (existence-form): there exist 5 of 9 audited
  operations whose nominal V₄ cell label is broader than the
  axis-engagement the implementation actually exhibits. The audit
  itself characterises the gap as "the original cotype was
  aspirational; the implementation is honest" and recommends
  reclassification of labels to match implementations, not patches
  to the constructions.
- **Introduced**: derived from the audit by LEM-rejection-aware
  restatement (2026-05-15).
- **Evidence**: [../scratch/audit_inhabitation.py](../scratch/audit_inhabitation.py)
  (specific call-outs: `compute_identity` engages no axes;
  `workspace_marker` and `compute_marker` have indistinguishable
  engagement; `store` and `load` are not engagement-symmetric);
  [../scratch/verify_cell_inhabitation.py](../scratch/verify_cell_inhabitation.py)
  (reclassification recommendations: identity ops as (X, {X}) not
  (X, ∅); `load` as (W, ∅); `workspace_driven_state` as (W, {C});
  `workspace_marker` as (W, {W}); `workspace_witness` as (W, {C, D})
  with caveat about second-level normalize routing).
- **Status**: shown (executable witness exhibits the 5 specific
  label-vs-runtime gaps).
- **Concepts**: C-V4-twins.
- **Action**: reclassification of these 5 cells in the
  meta_protocol registry would close the audit findings without
  changing any implementation. Listed as deferred work.

### K-chirality-is-parity
- **Statement**: Chirality of a directed witnessed-pair is the parity
  bit of the quotient S_4 / A_4 ≅ Z_2.
- **Introduced**: M34.
- **Evidence**: [cotype-free-self-extending-grammar.md:3783-3920].
- **Status**: shown.
- **Concepts**: C-S4-A4-chirality.

### K-inverse-pair-completes-via-Z2
- **Statement**: Inverse-pair completion proceeds along the Z_2 path
  (chirality flip).
- **Introduced**: M35.
- **Evidence**: [cotype-free-self-extending-grammar.md:3921-4018].
- **Status**: shown.
- **Concepts**: C-S4-A4-chirality.

### K-V4-extension-completes-S4-orbit
- **Statement**: V₄-extension of an A_4 element completes the S_4 orbit
  through it.
- **Introduced**: M36.
- **Evidence**: [cotype-free-self-extending-grammar.md:4019-4111].
- **Status**: shown.
- **Concepts**: C-V4-Klein, C-S4-A4-chirality.

### K-Z3-is-4axis-generator
- **Statement**: Z_3 = A_4 / V_4 is the generator of 4-axis chained
  operations.
- **Introduced**: M37.
- **Evidence**: [cotype-free-self-extending-grammar.md:4112-4228].
- **Status**: shown.
- **Concepts**: C-Z3-A4-V4.

## Unified address and M40 architecture theorem

### K-unified-address-guardrails
- **Statement**: A unified Hamming-coded address space provides
  guardrails (parity bits) for level transitions.
- **Introduced**: M38.
- **Evidence**: [cotype-free-self-extending-grammar.md:4229-4359].
- **Status**: partial — design shown; `unified_address` module
  referenced but absent.
- **Concepts**: C-unified-hamming-address.

### K-architecture-is-hadamard-mixing
- **Statement**: The architecture's principal operation is symmetry-
  governed Hadamard-basis mixing.
- **Introduced**: M39.
- **Evidence**: [cotype-free-self-extending-grammar.md:4360-4485].
- **Status**: shown (principle), realised at level 2 by
  K-M40-aggregator (which specifies the symmetry as A_4 × Z_2, not
  S_4). See [entailment.md § M39 principle → M40 specific
  identification](entailment.md#m39-principle--m40-specific-identification).
- **Concepts**: C-symmetry-governed-mixing.

### K-M40-aggregator
- **Statement** (the M40 main theorem, v6 packaging): The architectural
  group, defined as the closure of admissible generators {V_4
  translations T₁,T₂,T₃; Z_3 cycle Z; chirality} under composition,
  is order 24 and is isomorphic to A_4 × Z_2 — NOT S_4. Distinguished
  by order distribution (A₄×Z₂: {1:1, 2:7, 3:8, 6:8} vs S₄: {1:1, 2:9,
  3:8, 4:6}) and center order (2 vs 1). Adding any S_3 transposition
  extends to S_4 × Z_2 of order 48.
- **Introduced**: M40 v3 (initial); aggregated v6.
- **Evidence**: [cotype-free-self-extending-grammar.md:4486-4605],
  particularly [cotype-free-self-extending-grammar.md:4504-4534]
  (`verify_m40_group_is_a4z2_not_s4`).
- **Status**: shown (98 tests passing per v6's reported test count;
  `spectral_view` module referenced but absent in this repo, so we
  cannot re-run).
- **Concepts**: C-A4-Z2-group, C-architecture-WHT,
  C-oriented-affine-even-vs-full-affine.

### K-chirality-is-central
- **Statement**: The design intent of M40 is that chirality is CENTRAL
  — captured by |Z(A_4 × Z_2)| = 2, distinguishing it from S_4 whose
  center is trivial.
- **Introduced**: M40 v6 (audit-refined framing).
- **Evidence**: [cotype-free-self-extending-grammar.md:4536-4549].
- **Status**: shown.
- **Concepts**: C-A4-Z2-group, C-oriented-affine-even-vs-full-affine.

## M41 stack — structural-address obligation

### K-V4-semidirect-S3-is-primary
- **Statement**: S_4 ≅ V_4 ⋊ S_3 is the **primary** formal foundation
  of M41's address space; the selection-sort descent S_4 → S_3 → S_2
  → S_1 is the **derived** enumeration.
- **Introduced**: M41 v19.
- **Evidence**: [cotype-free-self-extending-grammar.md:5752-5904],
  [../s4_structure.py:5-21](../s4_structure.py).
- **Status**: shown (verifier `v4_swap_consistency`,
  factor_s4/unfactor_s4 round-trip).
- **Concepts**: C-V4-semidirect-S3.

### K-hodge-32-24-8
- **Statement**: In dim 4, 32 = |S_4| + 2·dim(Λ^1) = 24 + 8; the 24
  valid codewords are ordered triples (∈ S_4), the 8 forbidden
  codewords are signed singletons; Hodge ★ pairs them.
- **Introduced**: M41 v19.
- **Evidence**: [../s4_structure.py:14-21](../s4_structure.py),
  [../s4_structure.py:466-475](../s4_structure.py)
  (`verify_32_constructed_from_triadic_plus_hodge`).
- **Status**: shown (verifier).
- **Concepts**: C-hodge-star-dim4.

### K-cayley-dickson-level4
- **Statement**: |S_n| vs 2^n is (1,1,2,6,24,120) vs (1,2,4,8,16,32);
  at level 4 the embedding S_4 ⊂ 2^5 = 32 has parity-sieve ratio 3/4
  with Hodge-complement 8.
- **Introduced**: M41 v16, v19.1-3.
- **Evidence**: [../s4_structure.py:659+](../s4_structure.py),
  [cotype-free-self-extending-grammar.md:6411-6593].
- **Status**: shown.
- **Concepts**: C-cayley-dickson-seam.

### K-orbit-canonical-bijection
- **Statement**: Every valid signature decomposes uniquely as
  (orbit_key ∈ Stab(D)-representatives, v4_delta ∈ V_4); decomposition
  and recomposition are mutual inverses.
- **Introduced**: M41 v16, formalised at v19.
- **Evidence**: [../applied_grammar.py:861-956](../applied_grammar.py),
  verifier `verify_signature_decomposition_bijection`.
- **Status**: shown (verifier passes — see 2026-05-15 run).
  Also `realizes` K-cocycle-unifies-formal-systems and
  K-representations-associahedron at the address-space layer (V_4
  axis-swap gauge; orbit_key is the cohomology class / V_4-invariant
  content; v4_delta is the gauge degree of freedom). See
  [entailment.md § M8 cocycle → three parallel realisations](entailment.md#m8-cocycle--three-parallel-realisations).
  **Operational caveat**: the v17 lex-min canonical choice is
  rigidified into receipt content-addressing and verifier
  contracts; M2's "topos's freedom" is realised mathematically
  but not operationally. See [entailment.md § Type-D drift:
  operational choice-rigidification](entailment.md#type-d-drift-operational-choice-rigidification).
- **Concepts**: C-orbit-canonical-decomposition.

### K-v17-v19-agree
- **Statement**: The v17 orbit decomposition (lex-min canonical) and the
  v19 Stab(D)-canonical decomposition agree on orbit_key and differ
  on v4_delta by a fixed per-orbit V_4 element δ.
- **Introduced**: M41 v19.
- **Evidence**: [../applied_grammar.py:1313-1328](../applied_grammar.py)
  (`verify_v17_v19_decomposition_agreement`).
- **Status**: shown.
- **Concepts**: C-orbit-canonical-decomposition.

### K-parity-sieve-characterises-24
- **Statement**: The 24 valid codewords are exactly the codewords
  passing a 3-bit parity sieve on the 32 raw codewords.
- **Introduced**: M41 v17.
- **Evidence**: [../applied_grammar.py:1021+](../applied_grammar.py)
  (`verify_parity_sieve_characterization`).
- **Status**: shown.
- **Concepts**: C-parity-sieve, C-hodge-star-dim4.

### K-codeword-address-bijection
- **Statement**: `codeword_to_address` and `address_to_codeword` are
  mutual inverses on the valid set.
- **Introduced**: M41 v13.
- **Evidence**: [../applied_grammar.py:632-696](../applied_grammar.py),
  verifier `verify_codeword_address_bijection`.
- **Status**: shown.
- **Concepts**: C-codeword-address-bijection, C-structural-address.

### K-receipt-carries-address
- **Statement**: Every receipt carries a `StructuralAddress` consistent
  with its codeword; the address can be auto-derived if not supplied.
- **Introduced**: M41 v21.
- **Evidence**: [cotype-free-self-extending-grammar.md:5523-5629],
  [../applied_grammar.py:2084+](../applied_grammar.py)
  (`verify_receipt_address_codeword_agreement`).
- **Status**: shown.
- **Concepts**: C-structural-address, C-receipt-sumtype.

### K-structural-address-obligation-closed
- **Statement** (v21.1): The receipt-level structural-address obligation
  is closed end-to-end (umbrella verifier
  `verify_every_receipt_carries_structural_address`).
- **Introduced**: M41 v21.1.
- **Evidence**: [cotype-free-self-extending-grammar.md:5429-5522]
  including [cotype-free-self-extending-grammar.md:5473-5495]
  (the umbrella verifier definition).
- **Status**: shown.
- **Concepts**: C-structural-address, C-receipt-sumtype.

### K-addressed-op-paths-commute
- **Statement**: All three receipt-construction paths agree on the
  AddressedOp they construct; AddressedOp's structural digest matches
  `compute_structural_address_digest`.
- **Introduced**: M41 v22.0.
- **Evidence**: [../applied_grammar.py:1734-1765](../applied_grammar.py)
  (`verify_addressed_op_*`).
- **Status**: shown.
- **Concepts**: C-addressed-op, C-registry-domain.

### K-bridge-content-addressed
- **Statement**: `_check_codeword_bridge` collapses to address-equality;
  ContentAddressedReceiptFields make verification observationally pure.
- **Introduced**: M41 v18 (purity), v21.1 (bridge collapse).
- **Evidence**: [cotype-free-self-extending-grammar.md:5454-5495],
  [cotype-free-self-extending-grammar.md:5905-6145].
- **Status**: shown.
- **Concepts**: C-transactional-verification, C-codeword-address-bijection.

## Verifier-run summary (2026-05-15)

Verifier suite executed under Python 3.13.7 (.venv) with
`PYTHONPATH=scratch:.`. All test files pass:

| File | Checks |
|------|--------|
| [../scratch/verify_meta_protocol.py](../scratch/verify_meta_protocol.py) | 20/20 |
| [../scratch/verify_s4_structure.py](../scratch/verify_s4_structure.py) | 62/62 |
| [../scratch/verify_unified_address.py](../scratch/verify_unified_address.py) | 13/13 |
| [../scratch/verify_spectral.py](../scratch/verify_spectral.py) | 98/98 (incl. `M40_GROUP_IS_A4Z2_NOT_S4` aggregator) |
| [../scratch/verify_chained.py](../scratch/verify_chained.py) | 19/19 |
| [../scratch/verify_full_v4.py](../scratch/verify_full_v4.py) | 20/20 |
| [../scratch/verify_inverses.py](../scratch/verify_inverses.py) | 17/17 |
| [../scratch/verify_v4_twins.py](../scratch/verify_v4_twins.py) | 13/13 |
| [../scratch/verify_shadows.py](../scratch/verify_shadows.py) | S1–S7 + M-move invariants verified |
| [../verify_applied_grammar.py](../verify_applied_grammar.py) | 160/160 (incl. `every_receipt_carries_structural_address` umbrella + all `addressed_op_*` checks) |

**Aggregate: 422 explicit checks pass plus the S1–S7 / M-move
invariants suite.** Under [the LEM-rejection rule](README.md#epistemic-discipline-lem-is-rejected),
this is what "shown" means: a constructive witness exists and was
exhibited. Every claim with `Status: shown` in this file that is
bound to one of these verifiers below is constructively backed,
not paper-proof.

The two M33 audit files
([../scratch/audit_inhabitation.py](../scratch/audit_inhabitation.py),
[../scratch/verify_cell_inhabitation.py](../scratch/verify_cell_inhabitation.py))
also ran and produced the existence-form findings now recorded in
K-v4-twins-partial-inhabitation and
K-v4-twins-cell-labels-aspirational. The audit's universal-negative
conclusion is rejected per the epistemic rule; the audit's positive
content is preserved as two existence-form claims.

## Implementation bindings (K-claim → scratch artefact)

Each K-claim is bound to the file(s) that purport to witness it.
"shown by paper proof, no runnable witness" claims promote to
"executable witness" — see the Verifier-run summary above for the
2026-05-15 results.

| K-claim | Implementation | Verifier (if separate) |
|---------|---------------|------------------------|
| K-six-micro-ops-suffice | [../scratch/chart (6).py](../scratch/chart%20%286%29.py) | — |
| K-apply-grounds-realizability | [../scratch/chart (6).py](../scratch/chart%20%286%29.py) | — |
| K-apply-single-step-terminates-structurally | [../scratch/chart (6).py](../scratch/chart%20%286%29.py) (CBNeed) | — |
| K-chart-is-memoization | [../scratch/chart (6).py](../scratch/chart%20%286%29.py) (hash-cons) | — |
| K-chart-kernel-implements-micro-ops | [../scratch/chart (6).py](../scratch/chart%20%286%29.py) | — |
| K-self-extension-closes-L5 | [../scratch/chart (6).py](../scratch/chart%20%286%29.py) (meta-circular interp) | — |
| K-K_n-coherence-for-composition | [../scratch/enumerate_associahedra.py](../scratch/enumerate_associahedra.py) (M18) | — |
| K-tier2-regroup-well-formed | M10 regroup pass | [../scratch/verify_shadows (5).py](../scratch/verify_shadows%20%285%29.py) |
| K-table2-minimal | [../scratch/search_table2.py](../scratch/search_table2.py) | — |
| K-K-rule-gauge-structure | [../scratch/search_k_variants.py](../scratch/search_k_variants.py) | — |
| K-default-table-is-RM-1-3 | [../scratch/rm_in_tier1.py](../scratch/rm_in_tier1.py) | — |
| K-parity-basins-rotational | [../scratch/rm_codeword_basins.py](../scratch/rm_codeword_basins.py) | — |
| K-punctured-RM-is-Hamming | [../scratch/hamming_7_4_codewords.py](../scratch/hamming_7_4_codewords.py) | — |
| K-WHT-quotient-algebra | [../scratch/walsh_hadamard_readings.py](../scratch/walsh_hadamard_readings.py) | — |
| K-hamming-family-scales | [../scratch/hamming_scaling_hardware.py](../scratch/hamming_scaling_hardware.py) | — |
| K-stasheff-per-hadamard-level | [../scratch/stasheff_per_hadamard_level.py](../scratch/stasheff_per_hadamard_level.py) | — |
| K-F2-3-gauge-on-puncturings | [../scratch/walsh_hadamard_core.py](../scratch/walsh_hadamard_core.py) | — |
| K-S-is-pivot | [../scratch/s_as_pivot.py](../scratch/s_as_pivot.py) | — |
| K-triadic-with-witness | [../scratch/triadic_decomposition.py](../scratch/triadic_decomposition.py), [../scratch/witnessed_pairs.py](../scratch/witnessed_pairs.py) | — |
| K-gauge-is-semantic-axis | [../scratch/scratch_axis_audit.py](../scratch/scratch_axis_audit.py) | — |
| K-v4-under-explored | [../scratch/v4_klein_four_coverage.py](../scratch/v4_klein_four_coverage.py), [../scratch/engagement_matrix.py](../scratch/engagement_matrix.py) | — |
| K-state-machine-verified | [../scratch/architecture_state_machine (2).py](../scratch/architecture_state_machine%20%282%29.py) | — |
| K-F-populated | [../scratch/construct_v4_twins (2).py](../scratch/construct_v4_twins%20%282%29.py), [../scratch/construct_v4_twins_final (1).py](../scratch/construct_v4_twins_final%20%281%29.py) | [../scratch/verify_v4_twins.py](../scratch/verify_v4_twins.py) |
| K-v4-twins-fail-cells (negative) | [../scratch/audit_inhabitation.py](../scratch/audit_inhabitation.py), [../scratch/verify_cell_inhabitation.py](../scratch/verify_cell_inhabitation.py) | — |
| K-chirality-is-parity | [../scratch/chirality_as_parity.py](../scratch/chirality_as_parity.py), [../scratch/directed_witnessed_pairs.py](../scratch/directed_witnessed_pairs.py) | — |
| K-inverse-pair-completes-via-Z2 | [../scratch/chart_with_inverses (1).py](../scratch/chart_with_inverses%20%281%29.py) | [../scratch/verify_inverses (1).py](../scratch/verify_inverses%20%281%29.py) |
| K-V4-extension-completes-S4-orbit | [../scratch/chart_full_v4 (1).py](../scratch/chart_full_v4%20%281%29.py) | [../scratch/verify_full_v4 (1).py](../scratch/verify_full_v4%20%281%29.py) |
| K-Z3-is-4axis-generator | [../scratch/chart_chained.py](../scratch/chart_chained.py) | [../scratch/verify_chained.py](../scratch/verify_chained.py) |
| K-unified-address-guardrails | [../scratch/unified_address.py](../scratch/unified_address.py) | [../scratch/verify_unified_address.py](../scratch/verify_unified_address.py) |
| K-architecture-is-hadamard-mixing | [../scratch/hadamard_basis.py](../scratch/hadamard_basis.py) | — |
| K-M40-aggregator | [../scratch/spectral_view.py](../scratch/spectral_view.py) (`verify_m40_group_is_a4z2_not_s4`) | [../scratch/verify_spectral.py](../scratch/verify_spectral.py) |
| K-chirality-is-central | [../scratch/spectral_view.py](../scratch/spectral_view.py) (center order tests) | — |
| K-V4-semidirect-S3-is-primary | [../s4_structure.py](../s4_structure.py) | [../scratch/verify_s4_structure.py](../scratch/verify_s4_structure.py) |
| K-hodge-32-24-8 | [../s4_structure.py](../s4_structure.py) (`verify_32_constructed_from_triadic_plus_hodge`) | [../scratch/verify_s4_structure.py](../scratch/verify_s4_structure.py) |
| K-cayley-dickson-level4 | [../s4_structure.py:659+](../s4_structure.py) (`sn_cayley_dickson_table`) | — |
| K-orbit-canonical-bijection | [../applied_grammar.py:861-956](../applied_grammar.py) | [../applied_grammar.py:969+](../applied_grammar.py) (`verify_signature_decomposition_bijection`) |
| K-v17-v19-agree | [../applied_grammar.py:1313-1328](../applied_grammar.py) | same file |
| K-parity-sieve-characterises-24 | [../applied_grammar.py:1021+](../applied_grammar.py) (`verify_parity_sieve_characterization`) | — |
| K-codeword-address-bijection | [../applied_grammar.py:632-696](../applied_grammar.py) | [../applied_grammar.py:694+](../applied_grammar.py) (`verify_codeword_address_bijection`) |
| K-receipt-carries-address | [../applied_grammar.py](../applied_grammar.py) | [../verify_applied_grammar.py](../verify_applied_grammar.py) (suite covers this) |
| K-structural-address-obligation-closed | [../applied_grammar.py](../applied_grammar.py) (`verify_every_receipt_carries_structural_address` umbrella) | [../verify_applied_grammar.py](../verify_applied_grammar.py) |
| K-addressed-op-paths-commute | [../applied_grammar.py:1734-1765](../applied_grammar.py) (`verify_addressed_op_*`) | [../verify_applied_grammar.py](../verify_applied_grammar.py) |
| K-bridge-content-addressed | [../applied_grammar.py](../applied_grammar.py) (transactional verification block) | [../verify_applied_grammar.py](../verify_applied_grammar.py) |

**Claims without a dedicated implementation** (narrative-only or
realised-via-other):

- K-representations-associahedron (M2): realised by three layers —
  M17, M22, M41 v16+v19 — sharing the gauge-equivalence pattern with
  M8 (see entailment.md). No single dedicated artefact; the
  realisation is across the pattern.
- K-formal-system-algebraic (M6): realised as a term-algebra /
  symmetry-algebra pair (chart_chained+applied_grammar /
  meta_protocol+s4_structure); no single dedicated artefact.
- K-cocycle-unifies-formal-systems (M8): realised by three parallel
  claims (M17, M22, M41 v16+v19) — see entailment.md.
- K-meta-principle-lifted (M15): narrative.
- K-DBE-applied-to-itself (M11 second instance): narrative
  demonstration; the methodology is its own witness.

## Coverage gaps in this first-pass claim ledger

- L₂, L₄ closure claims are stated in probe-state tables across early
  moves; I did not enumerate each as a separate K-record.
- M5's "memoization soundness" claim was identified with hash-consing,
  so no separate K-record was created — that may be too aggressive a
  collapse.
- The 11 M41 versions are summarised by their landing claims; the
  intermediate proof-state at each version is not separately catalogued
  (see [entailment.md drift section](entailment.md#drift) for the
  version-chain shape).
- Charter-check tables (constructible / reachable / observable /
  coverable) appear at the bottom of major moves; I did not transcribe
  these as individual K-records.
