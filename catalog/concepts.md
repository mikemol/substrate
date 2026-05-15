# Concepts

Mathematical objects and structural notions introduced in the corpus,
with line-anchored evidence. Records are grouped roughly by phase, but
each is independent.

## Foundational micro-ops (M1)

### C-nil
- **Name**: `nil` — designated rule at reserved index.
- **Statement**: The well-founded base case of the rule term algebra;
  the unique rule with no proper structure.
- **Introduced**: M1 / S1.
- **Evidence**: [cotype-free-self-extending-grammar.md:22-27].
- **Status**: live.

### C-cons
- **Name**: `cons(l, q) → k` — binary constructor with hash-consing.
- **Statement**: Canonical rule reference for the pair (l, q); idempotent
  on identical inputs; forced binary by domain constraint.
- **Introduced**: M1 / S2.
- **Evidence**: [cotype-free-self-extending-grammar.md:28-32].
- **Status**: live.

### C-leftright
- **Name**: `left(k)`, `right(k)` — projections.
- **Statement**: Pair-inverse of `cons`; total on the cons-image.
- **Introduced**: M1 / S3.
- **Evidence**: [cotype-free-self-extending-grammar.md:34-38].
- **Status**: live.

### C-eq
- **Name**: `eq(a, b) → bool` — structural equality.
- **Statement**: Decidable equivalence on rule references, reducible to
  reference equality by hash-consing.
- **Introduced**: M1 / S4.
- **Evidence**: [cotype-free-self-extending-grammar.md:40-44].
- **Status**: live.

### C-apply
- **Name**: `apply(f, x) → k` — the realizability ground.
- **Statement**: Reduces f applied to x via the term structure of f;
  partial (may diverge); the primitive that grounds realizability.
- **Introduced**: M1 / S5.
- **Evidence**: [cotype-free-self-extending-grammar.md:46-50].
- **Status**: live, refined to single-step by [C-apply-single-step].

### C-parse
- **Name**: `parse(grammar, input) → k`.
- **Statement**: Parse input under the live grammar; routes new rules
  through `cons` for canonical entry to the chart.
- **Introduced**: M1 / S6.
- **Evidence**: [cotype-free-self-extending-grammar.md:52-56].
- **Status**: live.

## Domain constraints (Context, M3)

### C-hashcons
- **Name**: hash-consing.
- **Statement**: Structurally-identical rules share a single reference;
  equality reduces to reference comparison.
- **Introduced**: Context.
- **Evidence**: [cotype-free-self-extending-grammar.md:7-12].
- **Status**: live.

### C-acyclicity
- **Name**: acyclicity.
- **Statement**: Rule k references only rules with index < k; forces a
  minimal element ([C-nil]).
- **Introduced**: Context.
- **Evidence**: [cotype-free-self-extending-grammar.md:9].
- **Status**: live.

### C-monotonic-growth
- **Name**: monotonic chart growth.
- **Statement**: The chart only grows, never retracts.
- **Introduced**: Context.
- **Evidence**: [cotype-free-self-extending-grammar.md:11].
- **Status**: live.

### C-realizability-charter
- **Name**: realizability charter.
- **Statement**: constructible → reachable → observable → coverable, as
  a four-stage admission discipline for any distinction.
- **Introduced**: Context.
- **Evidence**: [cotype-free-self-extending-grammar.md:12].
- **Status**: live; reappears as the "Charter check" table at the end of
  major moves (e.g., [cotype-free-self-extending-grammar.md:4585-4592]).

## Axis-signature discipline

### C-axis-signature
- **Name**: axis-signature (3-bit code over {G,S,A}).
- **Statement**: A triple (g, s, a) ∈ {0,1}³ marking a move's direction
  in (goal, shadows, artefact) space. `100` = pure-GS lift, `010` =
  pure-SA regroup, `110` = mediated-composite (goal→shadows→artefact),
  `011` = guard-cleared SA, `101` = guard-cleared GS, `111` = triadic-
  full.
- **Introduced**: M1 (first appears as axis-signature 100).
- **Evidence**: [cotype-free-self-extending-grammar.md:16],
  [cotype-free-self-extending-grammar.md:540],
  [cotype-free-self-extending-grammar.md:598],
  [cotype-free-self-extending-grammar.md:657],
  [cotype-free-self-extending-grammar.md:1073],
  [cotype-free-self-extending-grammar.md:1188],
  [cotype-free-self-extending-grammar.md:1682-1704] (axes ↔ Walsh row
  table).
- **Status**: live. Folded into [C-walsh-hadamard-quotient] at M22.

### C-line-discipline
- **Name**: L₁, L₂, L₄, L₅ — axis-signature "lines" (probe triples).
- **Statement**: Three-element subsets of the 7 nonzero codewords whose
  joint coverage is a structural commitment. L₁ = {100, 010, 110}
  (positive-closure), L₂ = {100, 001, 101} (GS-guard-coverage), L₄ =
  {100, 011, 111} (GS-triadic-completion), L₅ named at M11's
  completion.
- **Introduced**: M1 (probe state table).
- **Evidence**: [cotype-free-self-extending-grammar.md:67-76],
  [cotype-free-self-extending-grammar.md:655-660].
- **Status**: live.

## Representation algebra (M2)

### C-representation-multiplicity
- **Name**: representational multiplicity.
- **Statement**: Rule references admit multiple representations
  (integer-as-path, function-as-path, trace-as-path,
  polynomial-as-path over GF(2^k)); choice is a structural axis.
- **Introduced**: M2.
- **Evidence**: [cotype-free-self-extending-grammar.md:106-117].
- **Status**: live.

### C-transform
- **Name**: `transform(k, src_rep, tgt_rep) → k_tgt` — S7.
- **Statement**: Coherent change-of-representation; round-trips must
  compose to identity per associahedron coherence.
- **Introduced**: M2 / S7.
- **Evidence**: [cotype-free-self-extending-grammar.md:118-150].
- **Status**: live.

### C-associahedron-K_n
- **Name**: Stasheff associahedron K_n.
- **Statement**: The polytope whose vertices are binary parenthesisations
  and whose higher cells govern coherence of re-associations. Used
  here both for representation-change coherence (M2) and for rule-
  composition coherence (M7).
- **Introduced**: M2 (implicit), M7 (explicit).
- **Evidence**: [cotype-free-self-extending-grammar.md:116],
  [cotype-free-self-extending-grammar.md:403-471],
  [cotype-free-self-extending-grammar.md:2027-2220] (Stasheff at each
  Hadamard level).
- **Status**: live.

## Operational refinement (M4–M5)

### C-apply-single-step
- **Name**: single-step `apply` with structural non-termination
  resolution.
- **Statement**: [C-apply] refined to one reduction step at a time;
  non-termination becomes a structural condition on the chart rather
  than a runtime exception.
- **Introduced**: M4.
- **Evidence**: [cotype-free-self-extending-grammar.md:196-253].
- **Status**: live; supersedes the naïve apply of M1.

### C-chart-as-memoization
- **Name**: chart-as-memoization substrate.
- **Statement**: The hash-consed chart **is** the memoization table for
  `apply`; no separate cache layer is needed.
- **Introduced**: M5.
- **Evidence**: [cotype-free-self-extending-grammar.md:254-309].
- **Status**: live.

## Algebraic substrate (M6–M8)

### C-formal-system
- **Name**: formal system via algebraic decomposition.
- **Statement**: Commit to the substrate algebraically: the term algebra
  is the free magma on the binary constructor modulo hash-consing.
- **Introduced**: M6.
- **Evidence**: [cotype-free-self-extending-grammar.md:310-402].
- **Status**: live.

### C-cocycle-projection
- **Name**: cocycle projection (cohomological framing).
- **Statement**: Multiple formal systems unify via projection from a
  cocycle in the cohomology of representational changes; the
  unification preserves the entailment lattice.
- **Introduced**: M8.
- **Evidence**: [cotype-free-self-extending-grammar.md:472-537].
- **Status**: live but rarely re-used directly after M22.

## Chart kernel artefact (M9, M32)

### C-chart-kernel
- **Name**: chart kernel artefact.
- **Statement**: Concrete implementation of the six micro-ops as a
  hash-consed table with `apply` reducer; the running substrate.
- **Introduced**: M9 (constructed), M32 (workspace axis + V₄-twin
  operations added).
- **Evidence**: [cotype-free-self-extending-grammar.md:538-595],
  [cotype-free-self-extending-grammar.md:3548-3652].
- **Status**: **referenced but absent** — imported as
  `chart_chained.ChartChained` in [../applied_grammar.py:175](../applied_grammar.py)
  and [../verify_applied_grammar.py:15](../verify_applied_grammar.py),
  but `chart_chained.py` is not in this repo. See [drift section in
  entailment.md](entailment.md#drift).

## Self-extension and meta-circularity (M11)

### C-meta-circular-fixpoint
- **Name**: meta-circular fixpoint via self-extension.
- **Statement**: The grammar describes its own parser; `apply` of the
  parser-rule on grammar-text is the fixpoint that closes L₅.
- **Introduced**: M11.
- **Evidence**: [cotype-free-self-extending-grammar.md:655-713].
- **Status**: live; second M11 (line 714) restates it operationally
  using DBE on itself.

### C-operational-meta-circularity
- **Name**: operational meta-circularity via decompose-by-entailment.
- **Statement**: The DBE skill applied to the grammar produces, as
  shadows, exactly the rules the grammar uses to extend itself; the
  skill's own operation is reproducible as grammar-rule application.
- **Introduced**: M11 (second instance at line 714).
- **Evidence**: [cotype-free-self-extending-grammar.md:714-839].
- **Status**: live.

## Tier-2 regroup (M12–M14)

### C-K-marker-variables
- **Name**: K-marker variables.
- **Statement**: Variables ranging over K_n associahedron vertices;
  function as gauge choices that index re-associations of rule trees.
- **Introduced**: M14 (regroup M11 under M13's vertex).
- **Evidence**: [cotype-free-self-extending-grammar.md:1071-1185].
- **Status**: live.

### C-K-rule-gauge
- **Name**: K-rule variable assignments / gauge structure.
- **Statement**: Variable assignments for K-rules form a gauge group;
  table₂'s minimal realization is up to this gauge.
- **Introduced**: M16, M17.
- **Evidence**: [cotype-free-self-extending-grammar.md:1284-1410].
- **Status**: live.

## Coding-theoretic layer (M18–M22)

### C-RM-1-3
- **Name**: Reed-Muller code RM(1, 3) inside `default_table`.
- **Statement**: The 8 length-8 codewords of RM(1, m=3) appear as the
  tier-1 instruction table; the parity check on RM(1, 3) is the rule's
  axis-signature.
- **Introduced**: M18 (enumeration), M19 (identification).
- **Evidence**: [cotype-free-self-extending-grammar.md:1411-1580].
- **Status**: live.

### C-parity-basins
- **Name**: parity basins; rotational transitions on RM codewords.
- **Statement**: Codewords of [C-RM-1-3] partition into basins under a
  rotation action; transitions between basins are guarded by parity.
- **Introduced**: M20.
- **Evidence**: [cotype-free-self-extending-grammar.md:1581-1667].
- **Status**: live.

### C-hamming-7-4
- **Name**: Hamming(7, 4) content/parity reading.
- **Statement**: Puncturing [C-RM-1-3] by one coordinate gives the
  perfect Hamming(7, 4) code; the 4 content bits ↔ the rule body, the
  3 parity bits ↔ the axis-signature.
- **Introduced**: M21.
- **Evidence**: [cotype-free-self-extending-grammar.md:1668-1751].
- **Status**: live.

### C-walsh-hadamard-quotient
- **Name**: Walsh-Hadamard quotient algebra (data, compute, state).
- **Statement**: Axis-signatures index Walsh rows of WHT_8; rule
  composition is computed by Hadamard multiplication and quotiented
  by the parity-basin equivalence.
- **Introduced**: M22 (first instance, line 1752).
- **Evidence**: [cotype-free-self-extending-grammar.md:1752-1873],
  [cotype-free-self-extending-grammar.md:1801] (axes↔Walsh-row table).
- **Status**: live.

### C-hamming-scaling
- **Name**: Hamming scaling hierarchy.
- **Statement**: The Hamming family with parameters (n=2^m−1, k=n−m,
  d=3) extends [C-hamming-7-4] to all m; symmetry group is GL(m, F₂);
  block ambient is the projective space PG(m−1, F₂).
- **Introduced**: M23 (first instance, line 1874).
- **Evidence**: [cotype-free-self-extending-grammar.md:1874-2026].
- **Status**: live.

### C-stasheff-at-hadamard
- **Name**: Stasheff polytope at each Hadamard level.
- **Statement**: At each m, the K_{n=2^m-1} associahedron governs the
  composition tradeoff between Hadamard-mixed operations and direct
  rule application.
- **Introduced**: M24 (first instance, line 2027).
- **Evidence**: [cotype-free-self-extending-grammar.md:2027-2220].
- **Status**: live.

## F₂³ gauge / 8-frame (M22-bis – M24-bis)

### C-eight-puncturings
- **Name**: eight puncturings of [C-RM-1-3] / [C-hamming-7-4].
- **Statement**: The 8 coordinate-puncturings of RM(1,3) form an F₂³
  torsor; the orbit is a single Walsh-Hadamard core acted on by an F₂³
  translation gauge.
- **Introduced**: M22-bis (line 2221).
- **Evidence**: [cotype-free-self-extending-grammar.md:2221-2331].
- **Status**: live. Note: re-uses move number M22 — see drift.

### C-S-gauge-pivot
- **Name**: S as gauge-invariant pivot of the 8-frame rotation.
- **Statement**: The "state" axis S is fixed by the F₂³ translation;
  the 8 frames rotate (D, C, W) around it.
- **Introduced**: M23-bis (line 2332).
- **Evidence**: [cotype-free-self-extending-grammar.md:2332-2454].
- **Status**: live.

### C-DCSW-axes
- **Name**: the four axes D, C, S, W (data / compute / state /
  witness).
- **Statement**: A 4-element set indexed by these labels; S_4 acts on it.
- **Introduced**: M22-bis–M24-bis; canonical in
  [../s4_structure.py:1-21](../s4_structure.py).
- **Evidence**: [cotype-free-self-extending-grammar.md:2221-2582],
  [../s4_structure.py:1-21](../s4_structure.py).
- **Status**: live. The 4-axis label set is the working surface for all
  V₄/S₄/A₄ structure from M28 onward.

### C-triadic-decomposition
- **Name**: triadic decomposition (data × compute × state).
- **Statement**: Computation factors as a product over three axes;
  witness W is the "fourth" axis that emerges via Hodge ★ in dim 4.
- **Introduced**: M24-bis (line 2455).
- **Evidence**: [cotype-free-self-extending-grammar.md:2455-2582],
  [../s4_structure.py:14-21](../s4_structure.py) (Hodge ★ in dim 4).
- **Status**: live.

## V₄ / S₄ algebraic structure (M28–M37)

### C-V4-Klein
- **Name**: V₄ — Klein four-group of axis swaps.
- **Statement**: Normal subgroup of S_4 generated by the three double-
  transpositions; acts on the 4 axes as the [C-eight-puncturings]
  translation gauge.
- **Introduced**: M28 (coverage analysis names it explicitly).
- **Evidence**: [cotype-free-self-extending-grammar.md:3037-3177],
  [../s4_structure.py:7-21](../s4_structure.py).
- **Status**: live.

### C-V4-twins
- **Name**: V₄-twins.
- **Statement**: Pairs of states related by a V₄ element; intended
  cells of a state classification.
- **Introduced**: M30 (constructed), M32 (operationalised).
- **Evidence**: [cotype-free-self-extending-grammar.md:3305-3547].
- **Status**: live, but **partially refuted** by [K-v4-twins-fail-cells]
  and the final M33.

### C-S4-A4-chirality
- **Name**: chirality as the parity bit of S_4 / A_4.
- **Statement**: The two-element quotient S_4 / A_4 ≅ Z_2 is the
  chirality flag of a directed witnessed-pair; even permutations have
  chirality +1, odd have −1.
- **Introduced**: M34.
- **Evidence**: [cotype-free-self-extending-grammar.md:3783-3920].
- **Status**: live.

### C-Z3-A4-V4
- **Name**: Z₃ = A₄ / V₄ — the 3-cycle quotient.
- **Statement**: A₄ / V₄ ≅ Z₃, generator of "4-axis chained operations".
- **Introduced**: M37.
- **Evidence**: [cotype-free-self-extending-grammar.md:4112-4228].
- **Status**: live.

### C-V4-semidirect-S3
- **Name**: V₄ ⋊ S₃ — primary formal foundation of M41's address space.
- **Statement**: S_4 ≅ V_4 ⋊ S_3 where S_3 is realised as Stab(D), the
  stabilizer of the anchor axis D. Every σ ∈ S_4 factors uniquely as
  σ = v · s with v ∈ V_4, s ∈ Stab(D).
- **Introduced**: M41 v19.
- **Evidence**: [cotype-free-self-extending-grammar.md:5752-5904],
  [../s4_structure.py:5-21](../s4_structure.py),
  [../s4_structure.py:42-205](../s4_structure.py).
- **Status**: live — designated **primary** by v19; the selection-sort
  descent S_4 → S_3 → S_2 → S_1 is the **derived** enumeration.

### C-hodge-star-dim4
- **Name**: Hodge star ★: Λ^3 → Λ^1 in dim 4.
- **Statement**: 32 = |S_4| + 2·dim(Λ^1) = 24 + 8: 24 ordered triples
  (valid codewords) plus 8 signed singletons (forbidden codewords);
  the dim-4 Hodge isomorphism pairs them.
- **Introduced**: M41 v19 (formalised); s4_structure.py header.
- **Evidence**: [../s4_structure.py:14-21](../s4_structure.py),
  [../s4_structure.py:271-292](../s4_structure.py) (`hodge_star_signature`),
  [../s4_structure.py:340-475](../s4_structure.py) (Q_5 / P_4 / Hodge
  partition verifiers).
- **Status**: live.

### C-cayley-dickson-seam
- **Name**: Cayley-Dickson seam at level 4.
- **Statement**: |S_n| vs 2^n is (1,1,2,6,24,120) vs (1,2,4,8,16,32);
  at n=4, S_4 sits inside 2^5 = 32 with the parity-sieve ratio 24/32 =
  3/4 and Hodge-complement of 8.
- **Introduced**: M41 v16.
- **Evidence**: [cotype-free-self-extending-grammar.md:6411-6593],
  [../s4_structure.py:659+](../s4_structure.py) (`sn_cayley_dickson_table`).
- **Status**: live.

## Hadamard-mixing principle (M38–M40)

### C-unified-hamming-address
- **Name**: unified Hamming-coded address space.
- **Statement**: A single address space encoded as a Hamming codeword,
  with parity bits as guardrails for level transitions.
- **Introduced**: M38.
- **Evidence**: [cotype-free-self-extending-grammar.md:4229-4359].
- **Status**: live; intended implementation
  `unified_address.{encode_op, UnifiedCodeword}` —
  **referenced but absent** ([../applied_grammar.py:176](../applied_grammar.py)).

### C-symmetry-governed-mixing
- **Name**: symmetry-governed Hadamard-basis mixing.
- **Statement**: The architecture's principal operation is multiplication
  by a Hadamard matrix in a basis chosen by the symmetry group at the
  current level.
- **Introduced**: M39.
- **Evidence**: [cotype-free-self-extending-grammar.md:4360-4485].
- **Status**: live.

### C-architecture-WHT
- **Name**: architecture = WHT (Walsh-Hadamard Transform) system —
  Fourier identification.
- **Statement**: The architectural primitives' closure under composition
  is the Fourier-domain view of WHT_8 modulo parity.
- **Introduced**: M40 v3 (initial), refined v4–v6.
- **Evidence**: [cotype-free-self-extending-grammar.md:4486-5323].
- **Status**: live; implementation module `spectral_view.fwht` —
  **referenced but absent** ([../applied_grammar.py:177](../applied_grammar.py)),
  though [../applied_grammar.py:31-32](../applied_grammar.py) names
  `spectral_view.py — M40 (v6)` as the artefact.

### C-A4-Z2-group
- **Name**: A₄ × Z₂ as the architectural symmetry group.
- **Statement**: The closure of admissible generators {V₄ translations
  T₁,T₂,T₃; Z₃ cycle Z; chirality} under composition has order 24 and
  is isomorphic to A₄ × Z₂, **not** S_4. Distinguished by center
  order: |Z(A₄ × Z₂)| = 2 vs |Z(S_4)| = 1.
- **Introduced**: M40 v3.
- **Evidence**: [cotype-free-self-extending-grammar.md:4504-4534],
  [cotype-free-self-extending-grammar.md:4536-4549].
- **Status**: live. This is the load-bearing M40 theorem; v6 packages
  it as a single aggregator
  `verify_m40_group_is_a4z2_not_s4`.

### C-oriented-affine-even-vs-full-affine
- **Name**: oriented affine-EVEN closure + external chirality vs full
  affine closure.
- **Statement**: Option A (M40): V_4 ⋊ A_3 (A_3 = Z_3 even subgroup of
  S_3) PLUS central Z_2 chirality. Option B (S_4): V_4 ⋊ GL_2(F_2) =
  V_4 ⋊ S_3, no separate chirality. Both order 24, non-isomorphic.
- **Introduced**: M40 v6 (refined framing from audit).
- **Evidence**: [cotype-free-self-extending-grammar.md:4536-4549].
- **Status**: live.

## M41 stack — structural address and verification

### C-structural-address
- **Name**: `StructuralAddress` — object-first identity of an operation.
- **Statement**: A tuple (sign, m, j) (or equivalent) that uniquely
  identifies an operation's place in the M40 algebra; the codeword is
  one chart on this address manifold.
- **Introduced**: M41 v20.
- **Evidence**: [cotype-free-self-extending-grammar.md:5630-5751],
  [../applied_grammar.py:632-696](../applied_grammar.py) (codeword↔address
  bijection).
- **Status**: live.

### C-codeword-address-bijection
- **Name**: codeword ↔ structural-address bijection.
- **Statement**: Functions `codeword_to_address` and `address_to_codeword`
  are mutual inverses on the valid set.
- **Introduced**: M41 v13 (stream merge with M40); v17 (purified).
- **Evidence**: [../applied_grammar.py:632-696](../applied_grammar.py),
  verifier `verify_codeword_address_bijection`.
- **Status**: shown (verifier passes when chart available).

### C-orbit-canonical-decomposition
- **Name**: orbit-canonical decomposition of signatures.
- **Statement**: Every valid signature decomposes as (orbit_key,
  v4_delta); orbits indexed by Stab(D)-representatives; v4_delta ∈ V_4.
- **Introduced**: M41 v16.
- **Evidence**: [cotype-free-self-extending-grammar.md:6411-6593],
  [../applied_grammar.py:861-956](../applied_grammar.py).
- **Status**: live.

### C-addressed-op
- **Name**: `AddressedOp` — canonical (op_name, StructuralAddress)
  bundle.
- **Statement**: The single object accepted by all three receipt
  constructors (term / state / observation); construction paths
  commute.
- **Introduced**: M41 v22.0.
- **Evidence**: [cotype-free-self-extending-grammar.md:5324-5428],
  [../applied_grammar.py:1734-1765](../applied_grammar.py)
  (verifiers).
- **Status**: live.

### C-registry-domain
- **Name**: REGISTRY_DOMAIN separator on digests.
- **Statement**: A caller-supplied namespace included in the digest of a
  structural address, so digests of identical (op_name, address) under
  different registries differ.
- **Introduced**: M41 v22.0.
- **Evidence**: [cotype-free-self-extending-grammar.md:5324-5428],
  [../applied_grammar.py:489-548](../applied_grammar.py).
- **Status**: live.

### C-receipt-sumtype
- **Name**: sum-type receipts (TermReceipt / StateReceipt /
  ObservationReceipt).
- **Statement**: Three disjoint constructors for verification receipts;
  each enforces an obligation appropriate to its op kind.
- **Introduced**: M41 v12 (tuple/list split → sum-type).
- **Evidence**: [../applied_grammar.py header v1-v12 chronicle]
  (cotype-free-self-extending-grammar.md preserves earlier v's are
  outside this doc; see applied_grammar.py docstring),
  [../verify_applied_grammar.py:16-50](../verify_applied_grammar.py).
- **Status**: live.

### C-transactional-verification
- **Name**: transactional verification (observationally pure).
- **Statement**: Verification's effect on chart state is reverted after
  observation; the bridge between codeword and signature is enforced
  inside the transaction.
- **Introduced**: M41 v18.
- **Evidence**: [cotype-free-self-extending-grammar.md:5905-6145].
- **Status**: live.

### C-grade-meet-monoid
- **Name**: Grade lattice as a meet-monoid.
- **Statement**: Verification grades form a meet-monoid with identity
  `GRADE_IDENTITY` and absorbing `GRADE_STRONGEST_EVIDENCE`; meet on
  grades transports through composition of verifications.
- **Introduced**: M41 v15.
- **Evidence**: [cotype-free-self-extending-grammar.md:6594-6801],
  [../applied_grammar.py:320-400](../applied_grammar.py).
- **Status**: live.

### C-parity-sieve
- **Name**: parity sieve characterising the valid 24.
- **Statement**: The 24 valid codewords are exactly those passing the
  3-bit parity sieve on the 32-element raw codeword space.
- **Introduced**: M41 v17 / v19.
- **Evidence**: [../applied_grammar.py:1021+](../applied_grammar.py)
  (`verify_parity_sieve_characterization`).
- **Status**: shown (verifier).

## Coverage gaps in this first-pass concept ledger

- M3's structural-choice resolutions (5 enumerated open questions);
  noted but not given individual concept records.
- M11 second-instance's explicit shadow list (the operational DBE
  application).
- M15's closure audit specifics.
- M26's Level-3 tesseract orbit enumeration mechanics.
- The earlier v1–v12 of M41 (annotation → sum-type) are listed but not
  given individual records — see [../applied_grammar.py docstring
  chronicle](../applied_grammar.py).
