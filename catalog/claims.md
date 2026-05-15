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

## Representation algebra (M2–M4)

### K-representations-associahedron
- **Statement**: Rule representations form vertices of an associahedron-
  like polytope; transforms between them are edges; cycles compose to
  identity (Stasheff coherence).
- **Introduced**: M2.
- **Evidence**: [cotype-free-self-extending-grammar.md:116-150].
- **Status**: partial — vertices and edges enumerated; higher-cell
  coherence stated as obligation, not constructed.
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
- **Status**: shown (commitment).
- **Concepts**: C-formal-system, C-cons.

### K-K_n-coherence-for-composition
- **Statement**: Rule composition is governed by the Stasheff
  associahedron K_n; re-associations beyond binary are higher-cell
  coherences.
- **Introduced**: M7.
- **Evidence**: [cotype-free-self-extending-grammar.md:403-471].
- **Status**: stated; coherence cells not exhaustively verified.
- **Concepts**: C-associahedron-K_n.

### K-cocycle-unifies-formal-systems
- **Statement**: Multiple formal systems unify via projection from a
  cocycle in the cohomology of representational changes.
- **Introduced**: M8.
- **Evidence**: [cotype-free-self-extending-grammar.md:472-537].
- **Status**: open — stated as a framing principle; not formalised
  further in subsequent moves.
- **Concepts**: C-cocycle-projection.

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
- **Status**: shown.
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

### K-v4-twins-fail-cells
- **Statement**: **NEGATIVE** — implementations do not fully honor their
  claimed V₄ cells; V₄-twin claims fail structurally under strict
  inhabitation audit.
- **Introduced**: M33 (line 3653, "fail structurally"), restated
  at final M33 (line 8029, "implementations don't fully honor their
  claimed V₄ cells").
- **Evidence**: [cotype-free-self-extending-grammar.md:3653-3782],
  [cotype-free-self-extending-grammar.md:8029-8157].
- **Status**: negative — claim refuted by inhabitation audit, restated
  at the final move as a still-open finding.
- **Concepts**: C-V4-twins.

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
- **Status**: shown (principle).
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
- **Status**: shown (verifier).
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
