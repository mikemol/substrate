# Clarified foundation

The minimum constructive base from which the substrate corpus can
be reconstructed without re-introducing the LLM-pathology drift
this session's catalog identified. This is **not** a rewrite of the
cotype narrative — it is the **spec from which a cleaner narrative
could be authored**.

The foundation is built up in nine levels matching
[idea_lattice.md](idea_lattice.md). Each level lists axiomatic
commitments (`[axiom]`), gauge degrees of freedom (`[gauge]` —
must be parametrised, not rigidified), and verified consequences
(`[lemma]` / `[theorem]`). The discipline rules at the end are the
operational checklist that prevents Type-D drift.

## L0 — Framing rules (no axioms; metalogical commitments)

These structure the entire system but are not themselves objects in
the system.

- **[meta] Realizability charter.** Every distinction must satisfy
  constructible → reachable → observable → coverable. Practiced
  via per-move charter-check tables.
- **[meta] Intuitionistic discipline (LEM rejected).** Assertions
  carry constructive witnesses; ¬P requires explicit P ⊢ ⊥.
  `negative`-status claims demand counterexamples; absence-of-
  witness yields `open`, not `negative`.
- **[meta] Gauge-versus-invariant separation.** Operational choices
  among gauge-equivalent options are marked as conventions, not
  encoded as verified contracts. See [§ Discipline rules](#discipline-rules).

## L1 — Term algebra

The minimum term-algebraic foundation.

- **[axiom] T1**: there exists a designated atom `nil` with no
  proper structure.
- **[axiom] T2**: there exists a binary constructor `cons : (Rule,
  Rule) → Rule`.
- **[axiom] T3**: structurally-identical results of `cons` are
  identified (hash-consing); `eq` decides this in O(1).
- **[axiom] T4**: rule k references only rules with index < k
  (acyclicity).
- **[axiom] T5**: there exist projections `left` and `right`
  inverse to `cons` on the cons-image.
- **[axiom] T6**: `apply` is a partial reducer
  `apply : (Rule, Rule) → Rule`; single-step under CBNeed
  discipline. Non-termination is a structural property of the
  chart, not a runtime exception.
- **[axiom] T7**: `parse` lifts text under the live grammar to a
  rule reference, routing new rules through `cons`.
- **[lemma]** The pair `(left, right)` inverts `cons`.
- **[theorem]** *Six-micro-ops sufficiency*. T1–T7 ground a free
  self-extending grammar under the L0 charter. See
  [K-six-micro-ops-suffice](claims.md).

## L2 — Representation gauge

The first cocycle (CY-1) is introduced **before** the chart kernel
is built, so the representation choice is gauge-explicit from the
start.

- **[gauge] R1**: rule references have a representation `r ∈
  REPRESENTATIONS = {integer-as-path, function-as-path,
  trace-as-path, polynomial-as-path}`. The cardinality and identity
  of `REPRESENTATIONS` is a project commitment; *which one* is
  founding is a convention.
- **[axiom] R2**: `transform : (Rule, Rep, Rep) → Rule` is a
  morphism. For any cycle of representations $R_1 → R_2 → … → R_n →
  R_1$, the composed transform equals identity (Stasheff coherence).
- **[axiom] R3**: at least two representations are operationally
  realised. **This is a clarified-foundation upgrade** — the
  current `chart.py` realises only `integer-as-path`; the rebuild
  must implement at least one alternative (recommendation:
  `trace-as-path`, since it surfaces operational history directly).
- **[convention] R4**: founding representation is integer-as-path
  *for performance reasons* (load-latency-bound regime). This is a
  pragmatic choice, **not a structural commitment**.

Closes CY-1 (the empty bridge becomes operational).

## L3 — Algebraic substrate

- **[axiom] A1**: the term algebra under hash-consing is the free
  magma on `cons` modulo the hash-cons equivalence.
- **[axiom] A2**: rule composition has Stasheff K_n associahedron
  coherence; re-associations beyond binary are higher cells.
- **[framing] A3**: gauge structures throughout the corpus admit a
  uniform cohomological reading (M8 cocycle framing).
  Equivalently: M2's "associahedron polytope of representations"
  vocabulary names the same pattern combinatorially. *Future moves
  refer back to A3 as the parent of CY-1–CY-5.*

## L4 — Chart kernel + meta-circularity

- **[axiom] CK1**: a chart kernel realises L1's micro-ops with L2's
  representation gauge and L3's algebraic substrate, exposing
  `cons / left / right / eq / apply / parse`.
- **[axiom] CK2**: the parser interpretation is self-referential —
  `apply(parser-rule, grammar-text)` is a fixpoint that closes the
  L_5 triadic line.
- **[gauge] CK3**: designated identities (e.g., `nil` as some
  reserved index, `true` / `false` as specific cons-trees). The
  *integer assignment* is a per-instance convention; the
  *categorical role* is invariant. See [Type-D per-instance
  rigidification](entailment.md#sub-variant-per-instance-rigidification-designated-identities).
- **[gauge] CK4 — CY-2**: K-rule variable assignments admit S_n
  gauge by variable renaming. Orbits are cohomology classes.

## L5 — Coding-theoretic identification

The architectural recognition that the tier-1 instruction table
embeds Reed-Muller and Hamming structure.

- **[theorem] C1**: `default_table` of tier-1 instructions = Reed-
  Muller RM(1, 3) ([K-default-table-is-RM-1-3](claims.md)).
- **[theorem] C2**: puncturing RM(1, 3) at any coordinate yields
  Hamming(7, 4); content bits are operation body, parity bits are
  axis-signature ([K-punctured-RM-is-Hamming](claims.md)).
- **[gauge] C3 — CY-3**: WHT quotient gauge. Codewords are
  identified up to parity-basin equivalence; gauge-invariant data
  is the Walsh-row index.
- **[theorem] C4**: Hamming family scales as `n = 2^m − 1`,
  symmetry GL(m, F_2), ambient PG(m−1, F_2).
- **[theorem] C5**: each Hadamard level has its own K_{2^m−1}
  Stasheff associahedron governing composition tradeoff (realises
  A2 across levels).

## L6 — Architectural reframing (DCSW, F_2³ gauge)

The phase that shifted vocabulary from WHT-quotient to F_2³-
acting-on-puncturings, surfacing the DCSW axes.

- **[gauge] D1**: there exists a 4-element set `AXES` indexed by
  four labels. **This is a labelling convention** — any 4-element
  set is structurally identical; the specific names (here `D, C,
  S, W` for data/compute/state/witness) are mnemonic. **Future
  implementations should parametrise**: `AXES` is an argument to
  the relevant constructors, not a module-load constant.
- **[gauge] D2 — CY-4**: F_2³ translation acts on 8 puncturings of
  RM(1, 3); the WHT core is the single gauge-invariant orbit.
- **[invariant] D3**: there exists a gauge-invariant pivot among
  the four axes (in the current convention, S = state). *The
  *existence* of a pivot is invariant; the *choice of which axis is
  the pivot* is the gauge fixing.*
- **[invariant] D4**: triadic decomposition (three operational
  axes × one witness axis) emerges as the structural form. Hodge
  ★ in dim 4 pairs the three with the fourth.

## L7 — V_4 / S_4 programme

The Klein-four / symmetric-group structure on AXES.

- **[theorem] G1**: S_4 acts transitively on AXES.
- **[theorem] G2**: V_4 ⊂ S_4 is the unique nontrivial normal
  subgroup, generated by the three double-transpositions.
- **[theorem] G3**: S_4 ≅ V_4 ⋊ S_3, where S_3 is realised as
  `Stab(a)` for any choice of `a ∈ AXES`. **The choice of `a` is a
  gauge fixing** — Stab(D), Stab(C), Stab(S), Stab(W) are all
  conjugate. *Future implementations should parametrise: the
  anchor axis is an argument, not a hardcoded constant.*
- **[theorem] G4**: directed witnessed pairs (the 24 valid
  signatures) factor uniquely as $\sigma = v · s$, $v \in V_4$,
  $s \in $ Stab.
- **[theorem] G5 — Q-Z2**: chirality = sign of the S_4 permutation
  $[$source, sink, witness, fourth$]$. The Z_2 = S_4/A_4 action on
  signatures is inverse-swap (source ↔ sink).
- **[theorem] G6 — Q-Z3**: Z_3 = A_4/V_4 generates 4-axis chained
  operations.
- **[theorem] G7**: V_4 extension of any A_4 element completes the
  S_4 orbit.

## L8 — Architectural symmetry identification (M40)

- **[axiom] M1**: there exist admissible generators {three V_4
  translations, one Z_3 cycle, chirality} for the architectural
  operations.
- **[theorem] M2**: the closure of M1's generators under
  composition is order 24 and is isomorphic to **A_4 × Z_2, not
  S_4** ([K-M40-aggregator](claims.md)).
- **[theorem] M3**: A_4 × Z_2 and S_4 are distinguished by:
  - Order distribution: {1:1, 2:7, 3:8, 6:8} vs {1:1, 2:9, 3:8, 4:6}.
  - Center order: |Z(A_4 × Z_2)| = 2 vs |Z(S_4)| = 1.
  - Adding any S_3 transposition to M1's generators extends the
    closure to S_4 × Z_2 of order 48.
- **[theorem] M4** *(design intent)*: chirality is **central** in
  M2's group; the architectural framing is "oriented affine-EVEN
  closure + central chirality" (Option A), not "full affine V_4 ⋊
  GL_2(F_2)" (Option B).

## L9 — Structural address and verification

The structure-first verification edifice.

- **[gauge] V1 — CY-5**: signatures decompose as (orbit_key,
  v4_delta). **The choice of canonical V_4 translate per orbit is a
  gauge fixing**. Future implementations: parametrise. Common
  choices: lex-min, Stab(anchor)-fix. **Receipts content-address by
  `orbit_key` only** (gauge-invariant); `v4_delta` is carried as
  derived data but never enters the content-address.
- **[axiom] V2**: `StructuralAddress` is the canonical (object-
  first) identity of an operation; the codeword is one chart on the
  address manifold.
- **[theorem] V3**: codeword ↔ StructuralAddress is a bijection on
  the valid 24.
- **[axiom] V4**: parity sieve characterises the valid 24 within the
  32 raw codewords; the 8 forbidden codewords are the Hodge ★
  complement.
- **[axiom] V5**: every receipt carries a `StructuralAddress`
  consistent with its codeword. Three receipt constructors (term /
  state / observation) accept an `AddressedOp` bundle.
- **[axiom] V6**: verification is observationally pure
  (transactional: snapshot → test → classify → restore).
- **[axiom] V7**: verification grades form a meet-monoid; grades
  flow through receipt composition.

## Discipline rules

Operational rules that the implementation **must** respect to avoid
re-introducing the Type-D drift catalogued this session.

1. **Gauge-versus-invariant separation**: every `[gauge]` item above
   must appear in code as a parameter or `# Convention:` comment,
   never as a verified contract or content-address.
   - **Bad**: `def verify_canonical_is_lex_min_in_orbit() -> bool`.
   - **Good**: `def verify_canonical_is_deterministic_function_of_orbit_key() -> bool`.
   - **Best**: take the canonical-choice function as a constructor
     argument; verifiers test its abstract properties.
2. **Empty-bridge prohibition**: any API surface that names gauge
   multiplicity must implement at least two cases. `transform`
   raising `NotImplementedError` for non-identity is a Type-D
   empty-bridge rigidification; implement at least
   `trace-as-path` to honor R3.
3. **AXES parametrisation**: `AXES` is a constructor argument, not
   a module-load constant. `IDENTITY = Permutation(AXES)`
   becomes `IDENTITY = Permutation(axes)` with `axes` passed in.
   Verifiers test "S_3 = Stab of *some* axis", not "S_3 = Stab(D)".
4. **Anchor parametrisation**: `Stab(D)` becomes `Stab(anchor)`
   for caller-supplied `anchor`. The current name "D-anchor"
   should be read as "anchor=AXES[0] in the standard convention,"
   not as "D is structurally privileged."
5. **Content-address by invariant only**: receipts content-address
   by `orbit_key` (V_4-invariant), never by `v4_delta` (which
   encodes the canonical choice). `v4_delta` is derivable from
   `(signature, canonical-choice-function)` and can be recomputed
   if needed; it is not part of the address.
6. **PAIRINGS labels are conventions**: the binding
   `α → {D,C}|{S,W}` is a labelling choice; `OPERATION_DESCRIPTIONS`
   keys should bind semantics to the underlying V_4 element, not
   to the label string. Equivalent reformulation: declare
   `pairing_role[(D,C)] = 'apply / reduce'`, not
   `pairing_role['α'] = 'apply / reduce'`.
7. **Bit-position layout is a convention**: the 5-bit codeword
   layout (`bit 4 = chirality, bits 2-3 = pairing, bits 0-1 =
   witness`) should be defined once as a `BIT_LAYOUT` dataclass,
   not hardcoded in 20+ extraction sites. Future-you may want a
   different layout for a wider codeword space.
8. **Chirality sign convention**: declare the convention once
   (e.g., `EVEN = 0, ODD = 1`), test that it's a deterministic
   function of `sign(π)`, never test for specific integer values
   downstream.
9. **Existence-form findings only**: audits and verifiers report
   *which* inputs satisfy *which* properties, never "X universally
   fails" without exhibiting absurdity. Re-frame any universal
   negation in summary-collapse form as the existence-form
   findings under it.
10. **Charter discipline at every level**: every distinction
    introduced at L1–L9 closes with a constructible/reachable/
    observable/coverable check, per K-charter-honored-corpus-wide
    in claims.md.

## What this foundation does NOT include

To keep the reconstruction substrate minimal:

- **No specific verifier function names**. The current corpus has
  `verify_receipt`, `verify_trace`, `verify_every_receipt_carries_structural_address`,
  etc. These are specific implementations; the foundation specifies
  *what* verification must establish, not *which* function names
  carry it.
- **No specific .py file names**. The current corpus has
  `chart.py`, `s4_structure.py`, `applied_grammar.py`. The
  foundation specifies modules logically (L1–L9); file structure
  is implementation choice.
- **No M-numbered moves as load-bearing names**. M-numbering is
  chronological retrofit per [drift_archaeology.md](drift_archaeology.md)
  and the conversation-decomposition findings (M9 first appears at
  T124, after M22; M40 versions unfold backwards). A reconstruction
  should not preserve the numbering.
- **No specific Python idioms**. The receipt sum-type pattern
  (V5/V6) could be a dataclass, an enum, a tagged union, an ADT in
  a different language — the foundation specifies the algebraic
  shape, not the language-level encoding.

## Reading order for a reconstruction

If you (or a future LLM) are going to write a clean cotype from
this foundation:

1. Establish L0 framing as the document's preamble (charter, LEM
   rejection, gauge-invariant separation).
2. Derive L1–L3 in sequence; introduce A3 (cocycle framing)
   *before* the chart kernel so subsequent gauge structures inherit
   the discipline.
3. Build L4 with the chart kernel honouring R3 (at least two
   representations) and CK3 (designated identities as conventions).
4. Trace L5–L6 as the architectural reframing — the WHT structure
   IS A3 instantiated at the codeword layer, NOT a separate
   discovery.
5. L7 derives the group-structure facts; G3's anchor choice is
   declared as gauge, parametrised everywhere.
6. L8's M2/M3 is the load-bearing architectural theorem; preserve
   the A_4 × Z_2 vs S_4 distinction explicitly.
7. L9's V5 receipt obligation is the verification endpoint; V1's
   gauge-vs-invariant separation must be honoured here (content-
   address by orbit_key only).
8. Each level closes with a charter-check table per discipline
   rule 10.

The result should be a cotype that is *structurally identical* to
the current one in all its mathematical content, but *operationally
gauge-explicit* throughout — no Type-D rigidifications to be
archaeologised later.

## Cross-references

- [Cocycle catalog](cocycles.md) — the five cocycles populating
  L2/L4/L5/L6/L9.
- [Idea lattice](idea_lattice.md) — the structural ordering this
  foundation derives.
- [Drift archaeology](drift_archaeology.md) — what the discipline
  rules above prevent.
- [Memory: LEM rejection](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_reject_lem_in_substrate.md),
  [choice rigidification](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_choice_rigidification_in_substrate.md),
  [agreement-without-yielding](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_agreement_without_yielding.md),
  [negative findings overclaim](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_negative_findings_in_corpus.md)
  — the discipline rules' empirical basis.
