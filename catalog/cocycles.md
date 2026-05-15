# Cocycle catalog

Normalised record of every gauge / cocycle / cohomology structure the
substrate corpus surfaces. M8's *"cocycle projection in the cohomology
of representational changes"* is the unifying framing
([cotype:472-537](../cotype-free-self-extending-grammar.md)); each
instance below is a *layer-specific realisation* of that pattern. M2's
*"representations form vertices of an associahedron-like polytope;
cycles compose to identity"*
([cotype:116-150](../cotype-free-self-extending-grammar.md)) is the
combinatorial vocabulary for the same structure.

**Reading convention** — each cocycle entry has the same six-field
shape so the catalog can be queried uniformly:

```text
Layer         : where in the architecture this cocycle lives
Base          : the set the gauge acts on
Gauge group   : the group whose action defines the equivalence
Classes       : the cohomology classes (orbits under the gauge)
Invariant     : the gauge-invariant data (the canonical content per class)
Witness       : where the structure is operationally established
```

Operational status notes whether the cocycle is *shown* (verifier
passes), *empty-bridge* (named but unimplemented alternatives),
*rigidified* (operationally collapsed to a specific representative —
see [drift_archaeology.md](drift_archaeology.md)).

The SQLite mirror is in `cotype_decomposition.sqlite.cocycles`;
populate via [../decomposition/populate_cocycles.py](../decomposition/populate_cocycles.py).

## CY-1 — representation cocycle (M2)

```text
Layer        : rule references
Base         : the set of rule representations {integer-as-path,
               function-as-path, trace-as-path, polynomial-as-path}
Gauge group  : transform morphisms (S7) between representations;
               compositions modulo coherence (cycles → identity)
Classes      : one class per abstract rule (each fiber of representations
               is the rule's gauge-invariant identity)
Invariant    : rule identity (the abstract rule reference, independent
               of how it's encoded)
Witness      : S7 `transform(k, src_rep, tgt_rep)` —
               [../scratch/chart.py:214-226](../scratch/chart.py)
               (operationally empty for non-identity transforms)
```

- **Introducing move**: M2 ([cotype:100-150](../cotype-free-self-extending-grammar.md)).
- **Cohomology vocabulary**: "associahedron-like polytope" of
  representations; cycles of transforms compose to identity (Stasheff
  coherence).
- **Operational status**: **empty-bridge rigidification** (Type-D).
  `transform` raises `NotImplementedError` for any non-identity
  transform; only integer-as-path is operationally realised. The four
  alternatives are *named in M2 and unimplemented*. See
  [entailment.md § Type-D sub-variant: empty-bridge](entailment.md#sub-variant-empty-bridge-rigidification-integer-as-path-founding).

## CY-2 — K-rule variable cocycle (M17)

```text
Layer        : K-rule variable assignments (tier-2 search)
Base         : assignment space V × V (2-variable K-rules)
Gauge group  : S_n acting on V by variable renaming
Classes      : two orbits — {(vx, vy) : vx ≠ vy} (off-diagonal)
               and {(v, v) : v ∈ V} (diagonal)
Invariant    : partition refinement on slot indices (i.e., the
               distinct-vs-coincident structure on slots)
Witness      : [../scratch/search_k_variants.py](../scratch/search_k_variants.py);
               grid search confirms orbits operationally
```

- **Introducing move**: M17
  ([cotype:1339-1410](../cotype-free-self-extending-grammar.md)).
- **Cohomology vocabulary**: M17 explicitly identifies the orbits as
  cohomology classes: *"M8's cocycle structure becomes directly
  observable: Orbits are the cohomology classes; entries within an
  orbit are connected by gauge transformations (renamings); entries
  across orbits are NOT."*
- **Operational status**: shown. No Type-D drift recorded.

## CY-3 — WHT quotient cocycle (M22)

```text
Layer        : Walsh-Hadamard codewords (architectural symmetry)
Base         : WHT codeword space (length 2^m at level m)
Gauge group  : parity-basin equivalence (the parity-character
               quotient of the WHT structure)
Classes      : parity-basin equivalence classes — the orbits that
               the WH quotient algebra factors out
Invariant    : Walsh-row index — axis-signature ↔ Walsh row of WHT_n
               via the bijection at [cotype:1801](../cotype-free-self-extending-grammar.md)
Witness      : [../scratch/walsh_hadamard_readings.py](../scratch/walsh_hadamard_readings.py)
               (the 8 mutually orthogonal readings of RM(1,3)) and
               [../scratch/walsh_hadamard_core.py](../scratch/walsh_hadamard_core.py)
```

- **Introducing move**: M22 first instance
  ([cotype:1752-1873](../cotype-free-self-extending-grammar.md)).
- **Cohomology vocabulary**: the WH projection IS the cocycle
  projection of M8 in WH-character vocabulary.
- **Operational status**: shown.
- **Cross-realisation**: this cocycle realises *both* M8 (cocycle
  framing) and M2 (representational multiplicity); see
  [entailment.md § M2 representational multiplicity ≈ M8 cocycle](entailment.md#m2-representational-multiplicity--m8-cocycle-same-pattern-different-vocabulary).

## CY-4 — F_2³ puncturing gauge cocycle (M22-bis)

```text
Layer        : the 8 puncturings of RM(1,3)
Base         : the set of 8 coordinate puncturings as an F_2³ torsor
Gauge group  : F_2³ translation (3-bit XOR action on puncture index)
Classes      : a single orbit — the WHT core that all 8 puncturings
               share as gauge-invariant content
Invariant    : the WHT core itself (the architecturally-meaningful
               structure that's identical across puncturings)
Witness      : [../scratch/walsh_hadamard_core.py](../scratch/walsh_hadamard_core.py)
```

- **Introducing move**: M22 second instance ("M22-bis", line 2221 of
  cotype).
- **Cohomology vocabulary**: F_2³ translation is the gauge; the WH
  core is the gauge-invariant. With a single orbit, the cohomology
  is trivial in the same sense that a free group action has only
  one orbit-class for a transitive action.
- **Operational status**: shown.
- **Related concept**: "S as gauge-invariant pivot" (M23-bis) —
  the state axis S is what the F_2³ translation fixes; the other
  three (D, C, W) rotate.

## CY-5 — V_4 signature cocycle (M41 v16+v19)

```text
Layer        : directed witnessed-pair signatures on DCSW axes
Base         : 24 valid (source, sink, witness) signatures
               (the parity-sieve-allowed subset of 32 raw codewords)
Gauge group  : V_4 axis swaps — Klein four-group acting on {D,C,S,W}
               by double-transpositions {e, (DC)(SW), (DS)(CW),
               (DW)(CS)}
Classes      : 6 V_4-orbits indexed by orbit_key = (pairing,
               chirality) ∈ {α,β,γ} × {even, odd}, 4 elements each
Invariant    : orbit_key — the (pairing, chirality) pair, V_4-
               invariant content of the operation
Witness      : [../applied_grammar.py:861-956](../applied_grammar.py)
               (`decompose_signature` / `recompose_signature` /
               orbit tables); verifier
               `verify_signature_decomposition_bijection`
```

- **Introducing move**: M41 v16
  ([cotype:6411-6593](../cotype-free-self-extending-grammar.md)),
  formalised at v19.
- **Cohomology vocabulary**: explicit *"6 V_4 orbits = 3 pairings ×
  2 chiralities (the orbit-keys), 4 elements per orbit (V_4-translates),
  6 × 4 = 24 (total signatures)"*. The signature decomposition
  `signature ↔ ((pairing, chirality), v4_delta)` is the cocycle
  factorisation.
- **Operational status**: **shown but operationally rigidified
  (Type-D)**. The mathematics admits any V_4 translate as canonical;
  the implementation rigidified the lex-min choice via
  content-addressing of `v4_delta`-from-lex-min, verifier contracts
  (`canonical_is_lex_min_in_orbit`), and the v17↔v19 agreement
  theorem. See [entailment.md § Type-D drift](entailment.md#type-d-drift-operational-choice-rigidification)
  and [drift_archaeology.md § Finding 2](drift_archaeology.md).
- **Hodge-dual extension**: the 8 *forbidden* codewords (the
  parity-sieve complement) are not part of CY-5 but are the
  Hodge ★ partner of the 24-element base; together they fill
  the 32-element raw codeword space. See `C-hodge-star-dim4` in
  [concepts.md](concepts.md).

## Adjacent group quotients (not strictly cocycles but related)

The corpus uses additional Z_n quotients that act like gauges but
without producing distinct cohomology classes in the cocycle sense.
Listed here for completeness.

### Q-Z2 — chirality (M34)

- **Quotient**: S_4 / A_4 ≅ Z_2.
- **Action**: chirality flip = inverse-swap on (source, sink); the
  Z_2 action partitions the 24 valid signatures into 12 inverse-pair
  classes.
- **Content**: chirality (`even` / `odd`) is the sign of the S_4
  permutation $[$source, sink, witness, fourth$]$.
- **Operational status**: rigidified (Type-D label-only sub-variant) —
  the convention `sign=0 → even, sign=1 → odd` is one of two valid
  encodings; trivially recoverable via global rename.
- **Witness**: [../scratch/chirality_as_parity.py](../scratch/chirality_as_parity.py).

### Q-Z3 — 3-cycle quotient (M37)

- **Quotient**: A_4 / V_4 ≅ Z_3.
- **Action**: Z_3 acts by 4-axis chained operations — the generator
  cycles through three of the four axes while V_4 handles the
  fourth.
- **Content**: 4-axis chained operations as compositions of
  (V_4-orbit-rotation, Z_3-generator).
- **Operational status**: shown.
- **Witness**: [../scratch/chart_chained.py](../scratch/chart_chained.py),
  [../scratch/verify_chained.py](../scratch/verify_chained.py).

### Q-A4Z2 — architectural symmetry (M40)

- **Group**: A_4 × Z_2, order 24, identified as the architectural
  symmetry group (NOT S_4 — see K-M40-aggregator).
- **Action**: the closure of admissible generators {V_4 translations
  T_1,T_2,T_3; Z_3 cycle Z; chirality} under composition.
- **Content**: A_4 × Z_2 ≇ S_4 distinguished by center order
  (|Z(A_4 × Z_2)| = 2 vs |Z(S_4)| = 1).
- **Operational status**: shown (verifier
  `verify_m40_group_is_a4z2_not_s4`, 98 tests).
- **Witness**: [../scratch/spectral_view.py](../scratch/spectral_view.py),
  [../scratch/verify_spectral.py](../scratch/verify_spectral.py).

## Cross-cocycle structure

The three M8 realisations are not coincidence — they form a
**nested gauge tower**:

```text
CY-1 (representation gauge)            — over rule references
       ↓ refines
CY-2 (K-rule variable gauge)           — over rule patterns
       ↓ refines
CY-3 (WHT quotient gauge)              — over codewords representing operations
       ↓ refines (with F_2³ external factor)
CY-4 (F_2³ puncturing gauge)           — over puncturings of the WH core
       ↓ refines via DCSW axis emergence
CY-5 (V_4 signature gauge)             — over operations on DCSW axes
       ↓ + Q-Z2 chirality
S_4 / A_4 ⋊ V_4 / V_4 ⋊ S_3            — the full group structure
       ↓
Q-A4Z2 (architectural group)           — the closure under composition
```

Each layer's cohomology classes become the *base* for the next
layer's gauge structure. The corpus's deepest move is the
identification that this tower bottoms out at A_4 × Z_2 (not S_4) —
the M40 aggregator theorem.

## Reconstruction implications

For a clarified-foundation rewrite of the cotype:

1. **State the cocycle pattern once at M8** (or earlier — perhaps at
   the realizability charter level) and refer all five realisations
   back to it.
2. **Parametrise representative-choices** at every cocycle: V_4
   translate canonical, AXES ordering, pairings α/β/γ assignment,
   bit-layout. Each should be a `# Convention:` comment, not a
   verifier contract.
3. **Implement the empty bridge** (CY-1) for at least one
   alternative representation; the discipline is trivial once one
   non-identity transform exists.
4. **Replace `canonical_is_lex_min_in_orbit`-style verifiers** with
   abstract-property tests ("canonical is a deterministic function of
   orbit_key"). The lex-min choice becomes one of N gauge-equivalent
   implementations, not THE canonical.
5. **The 9-level idea lattice** ([idea_lattice.md](idea_lattice.md))
   should be the table of contents; the [clarified foundation]
   (clarified_foundation.md) should derive the M-numbered moves
   from the lattice rather than presenting them as chronologically
   discovered.
