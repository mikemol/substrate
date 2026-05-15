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
- **The 24 + 8 structure as 3-of-4 quotienting** (per user
  clarification, 2026-05-15): the 8 "forbidden" codewords are NOT
  noise to be sieved out — they are the **parity space that
  encodes the three-from-four quotienting** which makes the 24
  meaningful as directed-witnessed-pair signatures. The
  combinatorial derivation:

  ```text
  Choose 3 of 4 axes for (source, sink, witness):  C(4,3) = 4
  Permute the chosen 3 into a directed tuple:      3! = 6
  Directed labels:                                 4 × 6 = 24

  Complement (parity space):
    "which one axis is excluded" × chirality
    of the excluded singleton:                     4 × 2 = 8

  Total raw codeword space:                        24 + 8 = 32 = 2^5
  ```

  Equivalently via parity: 12 spatial combinations (unordered)
  × 2 orientations (chiralities) = 24. The 8 are the signed
  singletons (one per axis × ± sign) that form the structural
  anchor. The relationship is reciprocal: the 8 define what an
  "axis" and a "directed triple" mean in this architecture; the
  24 are then exactly the configurations where the 3-of-4 selection
  applies.

- **The 24 ARE S_4** (not "things S_4 acts on"). Per
  [../s4_structure.py:14-21](../s4_structure.py): *"The 24 valid
  (source, sink, witness) signatures are precisely the elements of
  S_4 via σ ∈ S_4 ↔ (σ(D), σ(C), σ(S)) with σ(W) implicit as the
  'fourth' axis."* The CY-5 base **is** the symmetric group itself.
  Under M40's identification this group is operationally the
  architectural symmetry group A_4 × Z_2 — meaning the 24
  signatures are simultaneously the *base* of CY-5's gauge action
  AND the *elements of the group* M40 identifies. The cocycle is
  reflexive at the group-element layer: the gauge acts on what
  IS the group, partitioning it into 6 V_4-orbits via the V_4 ⋊ S_3
  factorisation.

- **Hodge-dual reading** (compatible with the parity-space reading
  above): in dim 4, ★ : Λ^3 → Λ^1 pairs ordered 3-tuples with
  signed 1-tuples. The 24 ordered triples Hodge-dual to the 8
  signed singletons. *Same structure, two vocabularies* — the
  3-of-4 quotienting is the combinatorial reading; the Hodge ★
  is the categorical reading. See `C-hodge-star-dim4` in
  [concepts.md](concepts.md) and the verifiers in
  [../s4_structure.py](../s4_structure.py)
  (`verify_8_oriented_unordered_triples`,
  `verify_hodge_complement_is_8_oriented_triples`).

## CY-6 — parse-derivation cocycle (grammar / SPPF / parsing)

```text
Layer        : grammars, parses, and the syntactic surface
Base         : derivations of input strings under a grammar
Gauge group  : parse-tree equivalence — multiple derivations of the
               same input span are gauge-equivalent
Classes      : packed nodes in the SPPF (Shared Packed Parse Forest)
               — each class is a span with all its alternative
               derivations grouped
Invariant    : the language-reading of the input (the meaning, modulo
               which derivation produced it)
Witness      : the founding SPPF design discussion in the original
               conversation (the MHTML's title is literally
               "Numpy-backed SPPF datastructure design");
               S6 `parse(grammar, input) → k` as the operation
               returning the gauge-invariant rule reference
```

- **Introducing move**: pre-M1 (the SPPF design is what motivated
  the chart structure at all). M1's S6 `parse` is the operation
  that yields the gauge-invariant content.
- **Cohomology vocabulary**: in parsing theory, the packed-node
  structure of an SPPF IS the cohomology of derivation-equivalence
  on parse trees. Two derivations of the same span are in the same
  packed node iff they produce equivalent abstract structure;
  packed nodes are equivalence classes.
- **Operational status**: **correct orbit-collapse with virtual
  recovery** (per user clarification, 2026-05-15). S6 `parse`
  returns the canonical representative of the orbit; alternative
  derivations are *virtually recoverable* from `(grammar, input,
  alternative-selection-rule)` by re-running the parser. This is
  **not lossy compression** — every member of the orbit maps to the
  exact same gauge-invariant content; canonical-only storage loses
  nothing of semantic value. See [§ Orbit collapse with virtual
  recovery](#orbit-collapse-with-virtual-recovery-methodology) for
  the principle.
- **Type-D status (revised)**: ~~silent-quotienting rigidification~~
  → **not rigidification under orbit-collapse discipline.** Earlier
  catalog reading reflexively applied the Type-D template here; the
  user's correction restored the correct framing. The substrate's
  canonical-only return is *exactly* what gauge-collapse requires;
  it just under-documents which selection rule produces the
  canonical. A clarified rewrite names the selection function
  (e.g., `parse(grammar, input, *, canonicalize=lex_min)`) — it
  does not need to expose alternative paths in storage.
- **Reconstruction implication (revised)**: the parser stays
  `parse → Rule` (canonical only). The discipline upgrade is to
  *name and parametrise* the canonicalization function rather than
  leave it implicit. Alternative derivations are accessible via
  an *out-of-band* tool (debugger / visualiser) that re-runs the
  parser with a different `canonicalize` argument — this respects
  metacircularity (storage stays the canonical) while making the
  gauge structure explicit. The triple identification
  (storage ≡ grammar ≡ ISA) is preserved precisely *because* the
  substrate stores only the canonical; storing alternatives in
  the substrate would break the metacircular collapse.
- **Why CY-6 is structurally identical to CY-5 under orbit-collapse**:
  - CY-5: store `orbit_key` (gauge-invariant); v4_delta is derivable
    from `(signature, V_4 group action)` virtually.
  - CY-6: store canonical `Rule` (gauge-invariant content); alternate
    derivations are derivable from `(grammar, input,
    alternative-selection-rule)` virtually.
  - In both cases the substrate stores **only the canonical
    representative** and the gauge structure makes alternatives
    *implicit*. CY-5's Type-D rigidification at lex-min is a
    *separate* problem (the content-address encodes WHICH canonical
    is privileged, not the existence of canonicalization) — see
    [§ Orbit collapse with virtual recovery](#orbit-collapse-with-virtual-recovery-methodology)
    for the distinction.

## CY-7 — combinator-reduction cocycle (SKI / λ)

```text
Layer        : computational semantics
Base         : λ-terms (or their combinator-encoded equivalents)
Gauge group  : β-η equivalence (with α-renaming as a sub-gauge);
               combinator-basis transformations (SK ↔ SKI ↔ BCKW
               ↔ λ-calculus proper) as a meta-gauge
Classes      : β-η equivalence classes (denotations / "real"
               functions)
Invariant    : the semantic function (the meaning of the term,
               independent of reduction path or basis encoding)
Witness      : M1 S5 `apply` (single-step reduction); M3's S/K/I
               designated as specific cons-trees in chart.py:40-46;
               M11 meta-circular interpreter operating on
               combinator terms
```

- **Introducing move**: M1 S5 (apply as the operational ground);
  M3 (S/K/I commitment); M11 (meta-circular interpreter).
- **Cohomology vocabulary**: β-equivalence is the canonical gauge
  on λ-terms; reduction paths through normal-form computation are
  cohomology cycles (the cocycle records that all paths yield the
  same normal form). The Church-Rosser theorem is the assertion
  that this cohomology is well-defined.
- **Operational status**: **shown but heavily rigidified**.
  - Reduction-path equivalence is implicit in CBNeed apply (single-
    step yields normal form regardless of evaluation order on
    terminating computations).
  - **Basis choice rigidified at M3**: `self.S = self.cons(3,3),
    self.K = self.cons(3,0), self.I = self.cons(0,3)`. The math
    admits many combinator bases (SK alone is Turing-complete);
    SKI is one of several valid choices. The integer indices are
    a per-instance rigidification (see Type-D per-instance
    sub-variant). The *combinator-basis* choice itself (SKI vs
    SK vs BCKW vs raw λ) is a Type-D unsubstituted-foundation
    sub-variant — the corpus never proposes an alternative basis.
- **Type-D status**: nested — per-instance (specific integer
  indices) plus unsubstituted-foundation (combinator-basis choice).
- **Reconstruction implication**: parametrise the combinator basis
  as a constructor argument. The chart should accept any complete
  combinator basis and operationalise it; SKI is one convention.

## SP-1 — metacircular fixed point (not a cocycle)

```text
Categorical kind : fixed point / terminal coalgebra, not a gauge
                   quotient — the canonical name is the
                   *metacircular fixpoint*
Layer            : meta-circular substrate
Base             : metacircular interpreter implementations
Generator        : "this grammar can describe itself" — apply on
                   the parser rule applied to grammar text
Fixed point      : the LFP (least fixed point) of the metacircular
                   function — the smallest grammar that contains
                   its own parser
Witness          : M11 meta-circular fixpoint
                   (C-meta-circular-fixpoint in concepts.md);
                   K-self-extension-closes-L5;
                   apply(parser-rule, grammar-text) as the
                   fixed-point operator
```

- **Why this is NOT a cocycle**: a cocycle structure has a gauge
  group acting on a base, producing equivalence classes.
  Metacircularity has no gauge — the LFP is a *unique terminal
  object* in the appropriate category, not a quotient of
  alternatives. Listed here because the user asked about
  self-hosting and because metacircularity is the structural
  pattern that *unifies* the cocycle tower (see § Metacircularity:
  storage ≡ grammar ≡ ISA above).
- **Interaction with cocycles**: SP-1's metacircular fixed point is
  *gauge-invariant content* across multiple cocycles — it survives
  all the gauge equivalences of CY-1 (representation), CY-7
  (combinator basis), CY-6 (parse derivation), and CY-8 (substrate).
  Different gauge fixings of those cocycles yield bootstrap-
  equivalent metacircular systems; the fixed point itself is what
  they all converge to.
- **Operational status**: shown (M11). No Type-D drift.
- **Reconstruction implication**: the LFP existence is the
  load-bearing claim of the entire project. A reconstruction
  should preserve M11's identification of the metacircular
  fixpoint as primary, and frame CY-1/CY-6/CY-7/CY-8 as gauge-
  equivalences that all meet at SP-1.

## CY-8 — substrate-implementation cocycle (micro-architecture)

```text
Layer        : operational substrate (where rules live)
Base         : substrate implementations satisfying the realizability
               charter (Morton-coded heap, sequential array,
               content-addressed memory, SIMD-packed fat nodes,
               etc.)
Gauge group  : substrate-equivalence — any two substrates that
               realise the same abstract chart semantics are
               gauge-equivalent
Classes      : implementations that satisfy the charter (every
               distinction constructible → reachable → observable
               → coverable in that substrate)
Invariant    : the abstract chart semantics (the operational
               commitment that survives substrate choice) AND
               the categorical decomposition of operations into
               (Compute, Data, State, Workspace) — the four
               architectural categories every substrate must
               provide
Witness      : M2's integer-as-path / function-as-path /
               trace-as-path / polynomial-as-path REPRESENTATIONS
               framing; M5 chart-as-memoization; M23
               Hamming-scaling-hardware (hardware acceleration
               boundary); pre-M1 SIMD-packed fat-node discussion
               in the founding conversation
```

**Origin of the four axes (per user clarification, 2026-05-15):**
The CDSW axis-labels — **Compute, Data, State, Workspace** — come
from this neighborhood. They are not group-theoretic labels chosen
to fit S_4 / V_4; they are *substrate-architectural categories*
naming what every operation engages with:

- **C (Compute)**: the transformation being performed.
- **D (Data)**: the input read.
- **S (State)**: the history advanced.
- **W (Workspace)**: the intermediate scratch.

The V_4 / S_4 algebraic structure on these labels (NB-A's
neighborhood, especially CY-5) is **downstream**: once the four
axes exist as substrate categories, S_4 acts on them transitively,
and the V_4 ⋊ S_3 decomposition follows. This is the natural
direction of dependency.

The catalog's earlier framing — treating AXES as a Level-6 gauge
emerging from F_2³ puncturings — gets the dependency partially
reversed. The substrate-architectural origin is *upstream* of the
coding-theoretic identification; the four axes existed (at least as
provisional categories) before the WHT/Hamming structure was named.
The retconned 15-turn argument (see
[drift_archaeology.md § Finding 3](drift_archaeology.md)) was, in
part, the user trying to get the architecture LLM to honor this
upstream/downstream ordering — to treat CDSW as substrate-given and
the group structure as derived, rather than rigidifying ('D','C',
'S','W') as a fixed tuple.

- **Introducing move**: distributed — appears at multiple levels.
  M2 names the representational substrate; M5 names hash-consing
  as the memoization mechanism; M23 names the hardware/software
  partition.
- **Cohomology vocabulary**: substrate-implementation classes are
  cohomologically equivalent iff they realise the same abstract
  chart semantics. The morphisms between substrates (which take
  one implementation to another while preserving semantics) are
  the gauge transformations.
- **Operational status**: closely related to CY-1 (representation
  gauge). CY-1 is the *representation of rules*; CY-8 is the
  *substrate that holds the chart*. They share a neighborhood (see
  below) but operate at different granularities — CY-1's gauge is
  on each rule's encoding; CY-8's gauge is on the chart structure
  as a whole.
- **Type-D status**: **partially rigidified**. The Morton-coded
  heap-relative addressing is treated as the natural substrate
  throughout the corpus; alternatives (function-as-path, polynomial-
  as-path, etc.) are not implemented (this is the same
  empty-bridge as CY-1, manifested at the substrate layer).
- **Reconstruction implication**: substrate choice should be a
  constructor argument to the chart kernel, not a module-load
  commitment. The discipline rules in [clarified_foundation.md](clarified_foundation.md)
  apply.

## CY-9 — memoization cocycle

```text
Layer        : computation traces / reduction paths
Base         : execution histories (sequences of operations
               producing results)
Gauge group  : result-equivalence — paths that compute the same
               value are gauge-equivalent
Classes      : equivalence classes of computations by result
Invariant    : the result (the normal form, the cached value, the
               fixed point at the end of reduction)
Witness      : M5 chart-as-memoization; hash-consing as the
               operational mechanism; M11's apply memoization
```

- **Introducing move**: M5 (chart-as-memoization recognition); M1
  S2 (cons's hash-consing requirement).
- **Cohomology vocabulary**: result-equivalence as the equivalence
  relation; the cached result is the canonical representative of
  its equivalence class.
- **Operational status**: shown. Hash-consing operationalises the
  cocycle at the term-algebra layer (CY-7's β-η equivalence is the
  proof that all reduction paths reach the same normal form;
  hash-consing is what *records* that fact so the second reduction
  doesn't have to be re-done).
- **Type-D status**: low. Memoization is well-behaved here because
  the equivalence (result equality) is a clean structural fact;
  the canonical (the cached value at the hash-cons reference) is
  the only natural choice.
- **Reconstruction implication**: memoization is what makes the
  cocycle tower computationally tractable — without result-
  equivalence collapsing, every gauge fixing would have to be
  re-derived per access. The discipline of "content-address by
  invariant only" (rule 5 in clarified_foundation.md) is what
  preserves memoization correctness across gauge fixings.

## Symmetry collapse (methodology, not a cocycle)

**Symmetry collapse** is the operational *mechanism* that turns
gauge equivalences into reusable canonical representatives. It is
not a cocycle in its own right — it is the *implementation
technology* that makes the cocycle tower run.

The corpus uses several specific symmetry-collapse mechanisms:

- **Hash-consing** (M1 S2 + S4): collapses structural equality
  among cons-tree references. Operationalises CY-7 (β-η yields
  identical normal forms, hash-cons identifies them) and CY-9
  (result-equivalence collapses to single cached reference).
- **Lex-min canonical selection** (M41 v16): collapses V_4 orbits
  to a single canonical signature. Operationalises CY-5 but with
  the Type-D rigidification noted — lex-min is one of many valid
  collapse functions; the catalog records that distinction.
- **Stab(D) canonical selection** (M41 v19): an *alternative*
  collapse for CY-5. The v17↔v19 agreement theorem is the
  *bridge between two collapse functions on the same cocycle*.
- **Parity sieve** (M41 v16): collapses 32 raw codewords to the 24
  valid (parity-passing). This is *not* a gauge collapse — it's a
  filter that defines the cocycle's base.

The methodological pattern: every cocycle in the catalog has at
least one symmetry-collapse mechanism that turns its equivalence
classes into accessible canonical content. The Type-D drift findings
are exactly the cases where the collapse function got rigidified
into a contract rather than acknowledged as one of several valid
choices.

**Reconstruction discipline**: symmetry-collapse functions should be
*explicitly named* and *parametrisable*. A clarified foundation
exposes the collapse as `canonical_in_orbit(orbit_key, *, method)`
rather than `canonical_in_orbit(orbit_key)` with method fixed.

## Orbit collapse with virtual recovery (methodology)

**The correct gauge-collapse discipline** (per user clarification,
2026-05-15): when a substrate operationalises a cocycle, it should
store **only the canonical representative** of each orbit. The
alternatives are not "lossy-compressed away" — they are *virtually
recoverable* from the canonical plus the gauge structure. By
definition, every member of an orbit maps to the same gauge-
invariant content, so canonical-only storage loses **nothing of
semantic value**.

The user's exact framing: *"choosing a canonical representative
from an orbit is **canonicalization**, not lossy compression,
because by definition, every member of the orbit maps to the exact
same gauge-invariant content. Nothing of semantic value is lost
when you collapse an orbit to its canonical representative; that
is the whole power of an invariant."*

The discipline has four distinguishable patterns; only one is
correct:

| Pattern | Storage shape | Recovery property | Type-D? |
|---------|---------------|---------------------|---------|
| **Orbit collapse + virtual recovery** | canonical only | alternatives regenerable from gauge + canonical + parametric inputs | **correct** — not rigidification |
| Lossy compression | canonical only | alternatives **not** regenerable (information genuinely lost) | would be drift, but doesn't apply when the gauge is a true equivalence — every orbit member produces the same invariant |
| Rigidified canonical | canonical only, with the **specific choice baked into the content-address** | alternative canonicals (different selection functions) cannot be substituted; the address encodes which canonical was chosen | Type-D verifier-contract sub-variant (CY-5 lex-min in v4_delta) |
| Empty bridge | only one alternative *operationally realised* | alternatives **named** but not implemented (no parser/transform exists for them) | Type-D empty-bridge sub-variant (CY-1, CY-8) |

The first three look superficially similar (all store only a
canonical) but differ in whether the canonical choice is recoverable
and whether the structure permits substitution. The reflexive
catalog-LLM reading at first applied the Type-D template to CY-6;
the correct reading is that CY-6 is **pattern 1** (correct orbit-
collapse), not pattern 3 or pattern 4.

**Why this discipline is metacircularity-consistent**: storing only
the canonical preserves the storage ≡ grammar ≡ ISA triple
identification. Storing alternatives in the substrate would split
the substrate into "canonical state" + "ambiguity sidecar," breaking
the metacircular collapse. The ambiguity, when needed, is
recovered by **re-running the gauge on the canonical** — for CY-6,
that's running the parser with a different selection rule; for
CY-9, that's recomputing a memoised value; for CY-5, that's
applying a different V_4 element to recover other orbit members.

**Reconstruction implication** for every cocycle:

1. Name the canonicalization function (`canonicalize_orbit(orbit_key,
   *, method)`).
2. Take `method` as a parameter at API surfaces; never hard-code.
3. Content-address by the **gauge-invariant** only (orbit_key,
   span+grammar, normal-form hash). Never content-address by the
   *canonical-choice-relative-data* (v4_delta-from-lex-min is the
   wrong shape; orbit_key alone is the right shape).
4. Provide an out-of-band tool for enumerating alternatives:
   debugger, visualiser, or audit pass that re-runs the gauge.
5. The substrate stays lean; ambiguity stays virtual.

This principle subsumes and refines the earlier discipline rules in
[clarified_foundation.md](clarified_foundation.md) — rule 1
(gauge-vs-invariant separation), rule 5 (content-address by
invariant only), and rule 9 (existence-form findings) all instantiate
orbit-collapse-with-virtual-recovery at their respective layers.

## Isomorphic storage: the deeper discipline

**The stronger framing** (per user clarification, 2026-05-15):
orbit-collapse-with-virtual-recovery is the *weaker* discipline.
The stronger one is **storage payload topology ≅ invariant space**:
the storage *is* the invariant space, not a container that *holds*
canonical representatives of it. The user's exact framing: *"I want
to collapse the distinction; I want the storage payload topology
to be isomorphic to the invariants."*

Under this discipline:

1. **There is no canonical representative.** The previous framing
   stored "the canonical V_4 translate" or "the canonical packed
   node"; isomorphic storage stores *the orbit*, with no
   representative selected. There is no `canonicalize(orbit, *,
   method)` function because there is no choice to make — every
   "canonical-choice" question dissolves because the storage
   structure has no extra degrees of freedom into which a choice
   could be made.
2. **Gauge actions become automorphisms of the storage topology
   itself**, not transformations of payloads inside containers.
   A V_4 axis-swap is *structural routing* — moving along an edge
   in the storage graph — not "reading an alternative data field."
   The gauge group acts on pointers, not on contents.
3. **A new element acts as a generator**. The user's framing:
   *"An element newly added to the forest entails its entire
   cocycle intrinsically; other orbit-members don't need to be
   observed in order to participate in the generative complement
   to the parse."* The orbit is *not recovered virtually* in the
   sense of "re-run the gauge to derive other members" — it is
   *tautologically present* by virtue of the group action being
   baked into the storage topology's automorphisms.

The two disciplines compared:

| Discipline | Storage shape | Gauge realised as | Where canonical choice lives |
|------------|----------------|---------------------|------------------------------|
| Orbit-collapse with virtual recovery (weaker) | canonical representative + gauge-invariant key | function parameter (`canonicalize=…`) | as a named, parametrised selection rule |
| **Isomorphic storage** (stronger) | the invariant *is* the storage topology | automorphism of the storage graph | **nowhere — the question doesn't arise** |

### What this does to CY-5

Under isomorphic storage, CY-5's lex-min Type-D rigidification
**doesn't get fixed — it dissolves**. There is no v4_delta in
storage because there is no canonical-relative coordinate to store.
The 6 V_4-orbits are 6 nodes in the storage topology; the 4
V_4-translates of each orbit are accessed by *moving along edges
between adjacent orbit-cells*, not by retrieving an offset from
some canonical baseline. Receipts carry the orbit's *structural
position*, which is the invariant; v4_delta and lex-min are not
just deprecated — they are *not expressible* in the isomorphic-
storage substrate, because there's no place for a coordinate-
dependent value to live.

This is the strongest version of the catalog's recovery rule for
CY-5: not "content-address by orbit_key only," but **"the
addressing-vs-payload distinction does not exist**." The Type-D
verifier-contract rigidification is structurally impossible in this
substrate because the structure has no place for the rigidified
choice to be encoded.

### What this does to CY-6

Under isomorphic storage, the SPPF's "packed nodes" stop being
*containers for alternative derivations*. Per user:

> *"The 'pack' of 'packed nodes' is done through group symmetry
> collapse. An element newly added to the forest entails its
> entire cocycle intrinsically; other orbit-members don't need to
> be observed in order to participate in the generative complement
> to the parse."*

The grammar's composition algebra is baked into the structural
adjacencies of the substrate. Adding one element to the forest
makes its entire cocycle operationally present *because the gauge
group's action is part of how the substrate is wired*, not because
the alternatives are stored anywhere. Ambiguity becomes
**topological path redundancy** — multiple paths through the
invariant network that satisfy the same boundary conditions —
rather than "alternative data shapes in a container."

The SPPF is no longer a *data structure* in the Earley-style
sense. It is a *projector*: a single element projects the whole
orbit through group action.

### What this does to the metacircular triple identification

Storage ≡ grammar ≡ ISA achieves *perfect* identification under
isomorphic storage:

- **Storage**: the physical configuration of nodes mirrors the
  algebraic invariants directly.
- **Grammar**: syntax rules are not string-matching tests; they are
  geometric instructions for *constructing paths through the
  storage topology*.
- **ISA**: the instruction set is the set of valid automorphisms
  over the invariant storage graph.

There is no "hidden implementation layer underneath the math"
because there is no implementation layer at all — the storage IS
the math. The data IS the grammar IS the execution.

This is the maximal form of the metacircularity commitment from
L0 ([clarified_foundation.md § L0](clarified_foundation.md#l0--framing-rules-no-axioms-metalogical-commitments)).
A clarified rewrite that takes metacircularity to its logical
limit produces an isomorphic-storage substrate by construction;
anything less leaves a residual storage-vs-invariant distinction
that the gauge structure has to police.

### Implementation note (aspirational)

The current substrate ([../applied_grammar.py](../applied_grammar.py),
[../scratch/chart_chained.py](../scratch/chart_chained.py),
[../s4_structure.py](../s4_structure.py)) does **not** satisfy
isomorphic storage — it stores signatures with v4_delta,
canonicalises with lex-min, treats storage and invariants as
separate concerns. Isomorphic storage is therefore aspirational
discipline for the clarified rewrite, not a description of what
exists. Sketch shape:

```python
class ForestElement:
    """A generator element in the isomorphic storage topology.
    Carries an invariant; alternative orbit-members are not stored
    here — they are reached by gauge automorphism over the
    storage graph."""
    invariant: OrbitInvariant
    # structural_adjacencies is the WIRING of the gauge group's
    # action into the topology — not a dictionary of alternative
    # values:
    structural_adjacencies: dict[GaugeAction, 'ForestElement']
```

`generative_complement(action)` returns the orbit-member reached by
applying `action` — but the call doesn't *retrieve* the member from
storage; it *moves along a structural edge* in the storage graph.
The edges *are* the gauge group; the orbit *is* the connected
component.

## Metacircularity: storage ≡ grammar ≡ ISA

**The corpus's central structural identification** (per user,
2026-05-15): *"the SPPF structure serves as both the storage and as
the grammar, the grammar is self-extending and is the compute ISA."*

The **canonical term for what makes this three-way identity
natural rather than incidental is *metacircularity***. The grammar
describes its own parser; the parser operates on grammar text; the
storage substrate IS the grammar's rule set. This is the classical
metacircular-evaluator pattern (LISP's meta-circular evaluator,
SICP Ch. 4, the Knot-tying construction in self-applicative
λ-calculus) — already named in the catalog as
`C-meta-circular-fixpoint` (M11) and as `K-self-extension-closes-L5`.

The triple identification is what metacircularity *gives you*. In a
non-metacircular system, storage / grammar / ISA are three distinct
artefacts that need translation layers between them. In the
substrate (and any metacircular system), they are **the same
artefact viewed through three layers of the cocycle tower**:

- **Storage layer** (NB-D substrate, CY-8): where rules live.
- **Grammar layer** (NB-B content syntax, CY-6): the rule set
  defining the language.
- **Compute ISA layer** (NB-A internal architectural, CY-2 through
  CY-5): the instruction set the architecture executes.

Under metacircularity (SP-1 fixed point), these three layers
**collapse to the same object**: the SPPF chart structure is
simultaneously the storage substrate, the grammar that describes
itself, and the instruction set that operates on grammar text.
M11's meta-circular fixpoint is the operational witness — apply
(parser-rule, grammar-text) is the operation that closes all three
identifications at once.

The triple identification + metacircularity are *together* what the
substrate corpus's M1 charter actually commits to. The cotype's
opening line — *"Construct the founding micro-operations for a free
self-extending grammar that is its own meta-grammar via LFP,
presents its grammar-image as a topos, and bootstraps a
self-extending ISA"* — is exactly this commitment with all four
keywords explicit (self-extending grammar = grammar layer, meta-
grammar via LFP = metacircular fixpoint, topos = the categorical
host, self-extending ISA = compute layer).

Cross-cocycle implication:

| Identification | Cocycle pair collapsed |
|----------------|-------------------------|
| storage ≡ grammar | CY-8 ≡ CY-6 (the substrate IS the rule set) |
| grammar ≡ ISA | CY-6 ≡ CY-{2,3,4,5} (the rules ARE the instructions) |
| storage ≡ ISA | CY-8 ≡ CY-{2,3,4,5} (the substrate's gauge structure IS the ISA's symmetry) |

The triple identification is *load-bearing* for the project's
charter: it is what makes "self-extending grammar + topos +
realizability + bootstrappable ISA" coherent. If any of the three
identifications fails, the project decomposes into a
storage-grammar-ISA tripartite system rather than a unified
substrate.

Operational consequence: **gauge structures must be consistent
across all three layers**. A CY-5 gauge fixing (lex-min canonical
for V_4 orbits) implicitly fixes the *same* canonical for:
- CY-6's packed-node representatives (parse-derivation gauge),
- CY-8's substrate addresses (storage gauge),
- and the M40 architectural-group representatives (ISA gauge).

This explains *why* the Type-D rigidification at CY-5 was so hard
to undo (per [drift_archaeology.md](drift_archaeology.md)): changing
lex-min canonical would propagate through all three layers
simultaneously. The triple identification is also what makes the
discipline rule "content-address by invariant only" (rule 5 of
clarified_foundation.md) load-bearing — content-addressing by the
gauge representative would break the identification across layers.

**Reconstruction implication**: the triple identification should be
stated at L0 (the framing rules), not derived at L4 (chart kernel).
A clarified rewrite would assert "storage ≡ grammar ≡ ISA" as a
charter commitment, then derive all subsequent cocycle layers as
gauge-equivalences within this identification.

## Cocycle neighborhoods

The eight cocycles + one fixedpoint cluster into five neighborhoods
by what they're gauges *of*. Neighborhoods are useful because items
within a neighborhood share recovery patterns — if one is rigidified,
the others typically are too in the same way.

### NB-A — Internal architectural gauge (the M8 nested tower)

**The cocycles operating on the architecture's internal symmetry
structure.** Already documented as the M8 nested gauge tower
([§ Cross-cocycle structure](#cross-cocycle-structure) above).

- **CY-2** K-rule variable cocycle
- **CY-3** WHT quotient cocycle
- **CY-4** F_2³ puncturing gauge cocycle
- **CY-5** V_4 signature cocycle (the deepest, where the lex-min
  rigidification lives)

Recovery pattern: gauge-vs-invariant separation enforced at every
layer; receipts content-address by invariant only.

### NB-B — Content syntax (parse-derivation)

**The cocycles operating on the syntactic surface — grammars and
their parses.**

- **CY-6** parse-derivation cocycle (the SPPF gauge)

Recovery pattern: surface alternative derivations as first-class;
do not silently quotient to a single canonical parse without
recording that the others exist.

### NB-C — Content semantics (combinator reduction)

**The cocycles operating on computational meaning — how terms
reduce and what bases they're encoded in.**

- **CY-7** combinator-reduction cocycle (SKI / λ)

Recovery pattern: parametrise the combinator basis; reduction-path
equivalence already operationalised by CBNeed apply.

### NB-D — Operational substrate

**The cocycles operating on how rules are represented and stored.**

- **CY-1** representation cocycle (the empty bridge)
- **CY-8** substrate-implementation cocycle (the micro-architecture
  gauge)

Recovery pattern: at least two representations / substrates must be
operationally realised so the API surface isn't a placeholder.

### NB-E — Meta-recursion (not a gauge structure)

**The fixed-point structure that survives all the above gauges.**

- **SP-1** self-hosting fixed point

Recovery pattern: identify the LFP as primary; the cocycle gauges
are all *equivalent ways of reaching* SP-1, not alternative SP-1s.

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
