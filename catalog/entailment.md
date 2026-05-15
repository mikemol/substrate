# Entailment graph

Typed edges between [concepts.md](concepts.md) and [claims.md](claims.md)
records, capturing motivation and dependence. Drift is annotated as a
separate edge type and given a prominent section.

## Edge legend

| Relation | Meaning |
|----------|---------|
| `motivates` | the source created the need or audit obligation that pulled the target into existence |
| `depends_on` | the target's statement uses the source as a substantive component (definition, lemma, primitive) |
| `refines` | the target is a more precise version of the source, both still live |
| `generalizes` | the target subsumes the source as a special case |
| `supersedes` | the target replaces the source; source is dormant |
| `drift_into` | the target reuses the source's name/number for substantively different content (loss of intent-vector pointer) |
| `witnesses` | the target is a code/verifier artefact for the source claim |
| `refutes` | the target contradicts the source via a constructive `P ⊢ ⊥` (counterexample, explicit absurdity). Under this repo's [LEM-rejection rule](README.md#epistemic-discipline-lem-is-rejected), an audit that "failed to verify" is NOT a `refutes` edge. |
| `realizes` | the target is a concrete construction that makes good on the source's abstract framing (the source was a placeholder; the target fills it in) |

## Primary motivation chain (the spine)

This is the "intact intent vector" that the project was on when each
move landed. It follows the entailment from M1 to M41 v22.0, ignoring
the version stacks and renumbering noise:

```text
K-six-micro-ops-suffice              (M1: ground the grammar)
   │ motivates
   ▼
K-representations-associahedron      (M2: representations are not unique;
   │ motivates                        coherence is associahedral)
   ▼
K-apply-single-step-terminates-structurally
   │ motivates                        (M4: divergence handled structurally)
   ▼
K-chart-is-memoization               (M5: the chart is the memo)
   │ depends_on
   ▼
K-formal-system-algebraic            (M6: commit to free magma + hash-cons)
   │ motivates
   ▼
K-K_n-coherence-for-composition      (M7: composition has Stasheff structure)
   │ generalizes (via cohomology)
   ▼
K-cocycle-unifies-formal-systems     (M8: cohomological framing)
   │ motivates
   ▼
K-chart-kernel-implements-micro-ops  (M9: build the kernel)
   │ depends_on
   ▼
K-self-extension-closes-L5           (M11: the fixpoint of apply on its
   │ refines                          own grammar text)
   ▼
K-DBE-applied-to-itself              (M11-second: operational DBE on itself)
   │ motivates
   ▼
K-tier2-regroup-well-formed          (M12–M14)
   │ motivates                        (audit obligation pulls in M15)
   ▼
K-meta-principle-lifted              (M15: closure audit at meta level)
   │ motivates                        (audit identifies search problem)
   ▼
K-table2-minimal + K-K-rule-gauge-structure
   │ motivates                        (M16–M17 find table₂; v17 sees gauge)
   ▼
K-default-table-is-RM-1-3            (M19: tier-1 table = RM(1,3))
   │ depends_on
   ▼
K-parity-basins-rotational           (M20: parity structure on RM)
   │ refines
   ▼
K-punctured-RM-is-Hamming            (M21: punctured RM = Hamming(7,4))
   │ generalizes (across m)
   ▼
K-WHT-quotient-algebra               (M22: WHT quotient = data×compute×state)
   │ refines
   ▼
K-hamming-family-scales              (M23: n=2^m-1, GL(m,F₂), PG(m-1,F₂))
   │ depends_on
   ▼
K-stasheff-per-hadamard-level        (M24: K_n at each level)
   │ refines via gauge identification
   ▼
K-F2-3-gauge-on-puncturings          (M22-bis: F₂³ gauge)
   │ refines
   ▼
K-S-is-pivot + K-triadic-with-witness (M23-bis, M24-bis)
   │ motivates
   ▼
K-v4-under-explored                  (M28: V₄ coverage identifies gap)
   │ motivates
   ▼
K-state-machine-verified             (M29) → K-F-populated (M30–M31)
   │ (no refutation edge — see drift §Type-A and the LEM-rejection
   │  note below; K-v4-twins-fail-cells is disaffirmed-by-non-
   │  constructive-audit, not a constructive `P ⊢ ⊥`)
   │ motivates the reframe at
   ▼
K-chirality-is-parity                (M34: chirality = S₄/A₄ parity)
   │ depends_on
   ▼
K-inverse-pair-completes-via-Z2 + K-V4-extension-completes-S4-orbit
   │ + K-Z3-is-4axis-generator        (M35–M37: S₄ structure constructively)
   ▼
K-unified-address-guardrails         (M38: unified Hamming address space)
   │ motivates
   ▼
K-architecture-is-hadamard-mixing    (M39: principle)
   │ motivates
   ▼
K-M40-aggregator                     (M40 v3-v6: architectural group = A₄×Z₂)
   │ depends_on
   ▼
K-V4-semidirect-S3-is-primary        (M41 v19: S₄ ≅ V₄ ⋊ S₃ is primary)
   │ depends_on
   ▼
K-hodge-32-24-8 + K-cayley-dickson-level4  (M41 v19, v16)
   │ depends_on
   ▼
K-orbit-canonical-bijection + K-v17-v19-agree (M41 v16, v17)
   │ refines
   ▼
K-codeword-address-bijection         (M41 v13: stream merge with M40)
   │ depends_on
   ▼
K-receipt-carries-address            (M41 v21)
   │ refines
   ▼
K-structural-address-obligation-closed (M41 v21.1)
   │ refines
   ▼
K-addressed-op-paths-commute + K-registry-domain  (M41 v22.0)
```

The spine bottoms out at v22.0 — the latest landing. Everything else is
either lateral support, an audit-driven correction, or drift.

## Lateral support edges

- C-axis-signature `witnesses` K-DBE-applied-to-itself (the 3-bit code
  IS the lift/regroup/audit direction tracker)
- C-realizability-charter `motivates` every "Charter check" table at
  the bottom of major moves
- C-hashcons `depends_on` ← {K-chart-is-memoization, K-formal-system-
  algebraic, K-six-micro-ops-suffice}
- C-DCSW-axes `depends_on` ← {K-F2-3-gauge-on-puncturings, K-chirality-
  is-parity, K-V4-semidirect-S3-is-primary, K-M40-aggregator}
- C-line-discipline `witnesses` K-self-extension-closes-L5
- C-parity-sieve `depends_on` ← K-parity-sieve-characterises-24
- C-grade-meet-monoid `depends_on` ← K-bridge-content-addressed,
  K-receipt-carries-address (verification grades flow through these)

## Realisation edges

The corpus contains M-era abstract framings that were stated as
placeholders and later realised concretely. The `realizes` relation
captures these. Empirically, **M8's cocycle / cohomology framing is
the most realised placeholder in the corpus** — three parallel
realisations at three different levels share it as a common source.

### M8 cocycle → three parallel realisations

K-cocycle-unifies-formal-systems (M8,
[../cotype-free-self-extending-grammar.md:472-537](../cotype-free-self-extending-grammar.md))
abstracts a cohomological pattern: "orbits as cohomology classes;
gauge-invariant data as the quotient." Three later moves realise this
pattern at different operational levels:

- **K-K-rule-gauge-structure (M17) `realizes` K-cocycle-unifies-formal-systems (M8)**.
  - **Level**: K-rule variable assignments (tier-2 search).
  - **Gauge group**: S_n acting on variable renaming.
  - **Orbits**: off-diagonal `{(vx, vy) : vx ≠ vy}` and diagonal
    `{(v, v)}` — distinct cohomology classes with structurally
    different operator shapes.
  - **Source's own framing**: M17 explicitly says
    "M8's cocycle structure becomes directly observable: Orbits are
    the cohomology classes; entries within an orbit are connected by
    gauge transformations (renamings); entries across orbits are
    NOT."
  - **Evidence**: [../cotype-free-self-extending-grammar.md:1376-1407](../cotype-free-self-extending-grammar.md);
    [../scratch/search_k_variants.py](../scratch/search_k_variants.py).
- **K-WHT-quotient-algebra (M22) `realizes` K-cocycle-unifies-formal-systems (M8)**.
  - **Level**: Walsh-Hadamard codewords (architectural symmetry).
  - **Gauge**: parity-basin equivalence (the WH projection factors
    out parity).
  - **Orbits**: the equivalence classes mod parity that the WH
    quotient algebra factors out.
  - **Evidence**: [../cotype-free-self-extending-grammar.md:1752-1873](../cotype-free-self-extending-grammar.md);
    [../scratch/walsh_hadamard_readings.py](../scratch/walsh_hadamard_readings.py).
- **K-orbit-canonical-bijection (M41 v16+v19) `realizes` K-cocycle-unifies-formal-systems (M8)**.
  - **Level**: directed witnessed-pair signatures (the address-space
    layer).
  - **Gauge group**: V_4 (Klein-four axis swaps).
  - **Orbits**: indexed by Stab(D)-representatives ("orbit_key");
    every valid signature decomposes uniquely as
    (orbit_key, v4_delta ∈ V_4).
  - **Cohomology class**: the orbit_key; the v4_delta is the
    gauge degree of freedom.
  - **Evidence**: [../cotype-free-self-extending-grammar.md:6411-6593](../cotype-free-self-extending-grammar.md)
    (v16 introducing the seam), [../applied_grammar.py:861-956](../applied_grammar.py)
    (the bijection implementation), [../applied_grammar.py:969+](../applied_grammar.py)
    (`verify_signature_decomposition_bijection`).

**Joint reading**: the M8 abstract framing is now realised at three
nested levels — the K-rule variable layer (M17), the codeword layer
(M22), and the signature/address layer (M41 v16). Each realisation
exhibits the same cohomological pattern with a different specific
gauge group. The catalog promotes K-cocycle-unifies-formal-systems
from status `open` → `shown via three parallel realisations`.

### M39 principle → M40 specific identification

- **K-M40-aggregator (M40 v3-v6) `realizes` K-architecture-is-hadamard-mixing (M39)**.
  - **The identification**: M39 states the principle "the
    architecture's principal operation is symmetry-governed
    Hadamard-basis mixing," but does not specify *which* symmetry.
    M40 fills in the placeholder: the symmetry is A_4 × Z_2
    (Option A: V_4 ⋊ A_3 + external central chirality), distinct
    from S_4 (Option B: V_4 ⋊ GL_2(F_2)) at the level of center
    order (|Z(A_4 × Z_2)| = 2 vs |Z(S_4)| = 1).
  - **Evidence**: [../cotype-free-self-extending-grammar.md:4360-4485](../cotype-free-self-extending-grammar.md)
    (M39 principle), [../cotype-free-self-extending-grammar.md:4486-4605](../cotype-free-self-extending-grammar.md)
    (M40 v6 specification with `verify_m40_group_is_a4z2_not_s4`
    aggregator); [../scratch/spectral_view.py](../scratch/spectral_view.py)
    and [../scratch/verify_spectral.py](../scratch/verify_spectral.py).
  - **Consequence**: the M39 principle is no longer
    abstract — its "some symmetry" placeholder is filled in
    concretely. The principle and its specific instantiation are
    both load-bearing.

### Charter-check practice → M1 realizability charter

- **K-charter-honored-corpus-wide (new) `realizes` C-realizability-charter (M1 / Context)**.
  - **Pattern**: every major move from M26 onward closes with a
    "Charter check" table that exhibits the four predicates
    (Constructible / Reachable / Observable / Coverable) with
    line-anchored ✓ marks for each distinction the move introduces.
    The charter is not asserted as a free-floating discipline — it
    is constructively re-applied at each scale.
  - **Witnessing tables**: M26 ([../cotype-free-self-extending-grammar.md:2847](../cotype-free-self-extending-grammar.md)),
    M27 ([line 3011](../cotype-free-self-extending-grammar.md)),
    M29 ([line 3155](../cotype-free-self-extending-grammar.md)),
    M30 ([line 3278](../cotype-free-self-extending-grammar.md)),
    M31 ([line 3401](../cotype-free-self-extending-grammar.md)),
    M31-post ([line 3525](../cotype-free-self-extending-grammar.md)),
    M32 ([line 3628](../cotype-free-self-extending-grammar.md)),
    M33 ([line 3758](../cotype-free-self-extending-grammar.md)),
    M34 ([line 3896](../cotype-free-self-extending-grammar.md)),
    M35 ([line 3995](../cotype-free-self-extending-grammar.md)),
    M36 ([line 4089](../cotype-free-self-extending-grammar.md)),
    M37 ([line 4203](../cotype-free-self-extending-grammar.md)),
    M38 ([line 4330](../cotype-free-self-extending-grammar.md)),
    M40 v6 ([line 4585](../cotype-free-self-extending-grammar.md)).
  - **Consequence**: the M1 realizability charter is a *practiced
    discipline*, not a manifesto. The four-stage admission test is
    constructively verifiable for every distinction the corpus
    introduces from M26 onward. Earlier moves rely on the discipline
    implicitly via their probe-state and cumulative-status tables;
    the explicit charter-check ritual stabilises around M26.

### Subsidiary realisation: M7 → M24

- **K-stasheff-per-hadamard-level (M24) `realizes` K-K_n-coherence-for-composition (M7)**.
  - **The identification**: M7 frames Stasheff K_n associahedron
    coherence over formal systems abstractly; M24 instantiates it
    at each Hadamard level (K_{n=2^m-1} governing composition
    tradeoff at scale m).
  - **Evidence**: [../cotype-free-self-extending-grammar.md:403-471](../cotype-free-self-extending-grammar.md)
    (M7), [../cotype-free-self-extending-grammar.md:2027-2220](../cotype-free-self-extending-grammar.md)
    (M24); [../scratch/stasheff_per_hadamard_level.py](../scratch/stasheff_per_hadamard_level.py).

### M2 representational multiplicity ≈ M8 cocycle: same pattern, different vocabulary

K-representations-associahedron (M2,
[../cotype-free-self-extending-grammar.md:100-150](../cotype-free-self-extending-grammar.md))
and K-cocycle-unifies-formal-systems (M8,
[../cotype-free-self-extending-grammar.md:472-537](../cotype-free-self-extending-grammar.md))
are alternative framings of the *same* categorical pattern: a gauge
structure where representations / formal-systems are equivalent up
to a coherence (M2: cycles compose to identity; M8: cocycle modulo
coboundary), and gauge-invariant data is the quotient. M2 phrases
this in associahedron / polytope vocabulary; M8 phrases it in
cohomology / cocycle vocabulary; the structure is the same.

Consequence: **the three parallel realisations of M8 listed above
ALSO realise M2**, because both sources name the same pattern. The
specific gauge groups (S_n at M17, parity-basin at M22, V_4 at M41
v16+v19) are different at each layer; the pattern is uniform.

The "topos's freedom" in M2's structural commitment #4 ("any vertex
could have been chosen") is precisely what each realisation
exercises: M17 picks an off-diagonal canonical; M22 picks a parity-
basin representative; M41 v16+v19 picks lex-min over V_4 translates
as canonical signature.

- **K-K-rule-gauge-structure (M17) `realizes` K-representations-associahedron (M2)**.
  - **The "representations"** at this layer are variable-name
    assignments to K-rule positions; transforms are S_n renamings;
    the polytope structure is the partition refinement on slot
    indices.
- **K-WHT-quotient-algebra (M22) `realizes` K-representations-associahedron (M2)**.
  - **The "representations"** at this layer are codewords; transforms
    are parity-basin moves; the polytope structure is the Walsh-
    Hadamard character lattice.
- **K-orbit-canonical-bijection (M41 v16+v19) `realizes` K-representations-associahedron (M2)**.
  - **The "representations"** at this layer are (source, sink,
    witness) signatures on DCSW axes; transforms are V_4 axis
    swaps; the polytope structure is the Cayley-Dickson ladder
    (32 = 24 + 8 with parity sieve giving 32 × 3/4).
  - **The "topos's freedom" — mathematical only**: the math admits
    any V_4 translate in an orbit as canonical
    ([../applied_grammar.py:923-931](../applied_grammar.py) picks
    lex-min, but the structure permits any choice). Operationally,
    however, the lex-min was treated as permanent by the prior LLM
    session — see [§ Type-D drift](#type-d-drift-operational-choice-rigidification).
    Receipts content-address `v4_delta` relative to lex-min;
    verifiers test `canonical == lex-min` as a contract; the v19
    → Stab(D) framing required a translation theorem rather than
    a substitution. So the realisation is mathematically clean but
    operationally rigidified. M2's structural commitment #4 is
    technically respected by the math and not respected by the
    code.

Consequence: K-representations-associahedron is promoted from
status `partial` (vertices/edges enumerated; higher cells stated
as obligation) → `shown via three parallel realisations at three
operational layers`. Higher-cell coherence is still abstract in M2's
sense but the gauge structure that the polytope encodes is fully
operational.

### M6 algebraic commitment realised as a term-algebra / symmetry-algebra pair

- **(applied_grammar.py + s4_structure.py + chart_chained.py + meta_protocol.py) collectively `realize` K-formal-system-algebraic (M6)**.
  - **M6's commitment**: "the substrate is the free magma on the
    binary constructor modulo hash-consing"
    ([../cotype-free-self-extending-grammar.md:310-402](../cotype-free-self-extending-grammar.md))
    — an abstract algebraic identity; M6 does not specify *which*
    symmetries the operation set has.
  - **The realisation lands as a pair**, because M6's commitment was
    necessary-but-not-sufficient: the corpus eventually grounds the
    formal system in TWO algebraic structures that mutually
    constrain one another:
    - **Term-algebra side**: cons-tree free magma mod hash-cons.
      Implementation: [../scratch/chart_chained.py](../scratch/chart_chained.py)
      (chart kernel + hash-consing + apply reducer) +
      [../applied_grammar.py](../applied_grammar.py) (operations
      layered on chart).
    - **Symmetry-algebra side**: V_4 ⋊ S_3 ≅ S_4 acting on the 4
      axes, with Hodge ★ in dim 4 giving 32 = 24 + 8 = |S_4| +
      2·dim(Λ¹) and the Cayley-Dickson seam at level 4.
      Implementation: [../scratch/meta_protocol.py](../scratch/meta_protocol.py)
      (declarative protocol) + [../s4_structure.py](../s4_structure.py)
      (formal group structure).
  - **Spokesperson claim**: K-V4-semidirect-S3-is-primary (M41 v19)
    is the single best-located point of the realisation — it names
    the specific algebraic identity (S_4 ≅ V_4 ⋊ S_3 as primary
    formal foundation) that ties the symmetry side to the term
    side via the AddressedOp / StructuralAddress chain.
  - **Evidence chain**: [../cotype-free-self-extending-grammar.md:5752-5904](../cotype-free-self-extending-grammar.md)
    (v19 establishes V_4 ⋊ S_3 as primary);
    [../s4_structure.py:5-21](../s4_structure.py) (the claim made
    operational); [../scratch/verify_s4_structure.py](../scratch/verify_s4_structure.py)
    (62/62 checks pass; verifies the algebraic identity end-to-end);
    [../applied_grammar.py:861-956](../applied_grammar.py) (the
    AddressedOp / orbit-canonical bridge that ties term-algebra
    receipts to symmetry-algebra signatures).
  - **Consequence**: K-formal-system-algebraic promoted from
    `shown (commitment)` to `shown via pair-realisation` — the
    commitment is now concretely embodied. The realisation also
    *strengthens* M6: the formal system isn't just a free magma
    mod hash-cons; it is a free magma mod hash-cons whose operation
    set carries an S_4 ≅ V_4 ⋊ S_3 symmetry encoded by
    StructuralAddress and verified by the umbrella
    `verify_every_receipt_carries_structural_address`.
  - **Reading aid**: M6 was the *promise* of algebraic
    commitment; the M41 stack is what the commitment turned out
    to require. The 22+ version chain on M41 is the audit-walk that
    pulled the symmetry-algebra side into the same algebraic
    discipline as the term-algebra side.

## Drift {#drift}

This section is the user's primary deliverable. The corpus shows two
distinct kinds of intent-vector drift; we annotate each.

### Type-A drift: move-ordinal collision (the LLM lost its place)

The retrospective in [../decomposition/cotype_retrospective.md](../decomposition/cotype_retrospective.md)
lists 65 moves but the move numbers (M1, M2, …) are reused. Pairs:

| Number | First instance | Second instance | Drift kind |
|--------|----------------|-----------------|------------|
| M11 | line 655: meta-circular fixpoint via self-extension | line 714: operational meta-circularity via DBE | **Coherent restatement.** The second instance applies DBE to the same target the first instance described abstractly. Not really drift; the LLM reused M11 deliberately to mark "same move, operational view." Edge: `refines`. |
| M22 | line 1752: WHT quotient algebra (data, compute, state) | line 2221: eight puncturings, F₂³ gauge | **Numbering drift.** Substantively different content; the second is a refinement of the WHT structure into a gauge action. LLM lost track of the ordinal. Edge: `refines` conceptually, `drift_into` ordinally. |
| M23 | line 1874: Hamming scaling hierarchy | line 2332: S as gauge-invariant pivot | **Numbering drift.** Same pattern as M22-pair. Edge: `refines` conceptually, `drift_into` ordinally. |
| M24 | line 2027: Stasheff polytope per Hadamard level | line 2455: triadic decomposition (data×compute×state) | **Numbering drift.** Same pattern. Edge: `refines` conceptually, `drift_into` ordinally. |
| M33 | line 3653: V₄-twin claims fail structurally (audit) | line 8029: implementations don't fully honor their claimed V₄ cells (final audit) | **Coherent callback.** Both are NEGATIVE inhabitation audits of the same target. The final M33 (4400 lines later, after the entire M40/M41 build) returns to find the issue *still* unaddressed. Edge: `restates` (a new sub-relation we promote here). |

The pattern: when the conversation re-entered a topic after several
thousand lines, the LLM reset its move counter. The reuse of M22-24 in
the F₂³-gauge phase is the most consequential drift: it concealed that
the project had genuinely advanced from WHT-quotient (first triplet) to
F₂³-gauge-action (second triplet) under the same labels. **Reading aid
for future sessions:** treat the second M22-24 triplet as M22'-M24' or
M25a-M25c.

### Type-B drift: version-stacking under M40 and M41

The M40 and M41 entries preserve multiple versions explicitly. This is
**not the usual drift** — it is intentional accretion that the moves
themselves audit. The shapes:

#### M40 chain (v3 → v4 → v5 → v6)

```text
v3: distinguish A₄ × Z₂ from S₄ (both order 24)
 │ refines
v4: algebraic proof spine + architectural derivation
 │ refines
v5: closure-equals-algebraic; exhaustive associativity over all 24³
 │ refines
v6: theorem aggregator + refined framing
     (oriented affine-EVEN + chirality vs full affine)
```

All four versions are preserved in the markdown. v6's docstring
explicitly lists v1–v6 in [cotype-free-self-extending-grammar.md:4555-4574].

**Drift signal**: low — this is constructive refinement, each version
strictly strengthens the previous. The "audit"-style framing is
explicit at v6.

**Drift cost**: present but absorbed — v3 and v4 are preserved as
"previous wording" rather than active claims. Only v6 is load-bearing.

#### M41 chain (v13 → v22.0, eleven preserved versions)

```text
v13: stream merge with M40; codeword↔address bijection
 │ depends_on (rebase)
v14: kernel-honesty pass on v13 merge
 │ depends_on
v15: honesty refinements; state cursor seam; Grade meet-monoid
 │ depends_on
v16: orbit-canonical decomposition; Cayley-Dickson seam
 │ depends_on
v17: audit fixes; codeword↔signature bridge; parity sieve
 │ depends_on
v18: transactional verification; observational purity;
      ContentAddressedReceiptFields
 │ depends_on
v19: V_4 ⋊ S_3 as primary formal foundation (s4_structure.py created)
 │ depends_on
v20: StructuralAddress dataclass (object first, codeword last)
 │ depends_on
v21: receipt-level address obligation
 │ depends_on
v21.1: structural-address obligation closed end-to-end
 │ depends_on
v22.0: AddressedOp + registry domain + scope tightening
```

Plus the earlier v1–v12 chain summarised in
[../applied_grammar.py:23-31](../applied_grammar.py) as:
annotation → endogenous codewords → verify_trace → pure replay →
VerificationResult → three axes → cells_allocated → audited kernel →
semantic replay → Grade lattice → tuple/list split → sum-type receipts.

That's **22 versions** of M41 in total.

**Drift signal**: medium. This is the longest chain of "audit-and-fix"
in the corpus. Each version adds a verifier or refines an obligation;
no version was abandoned. But the sheer length suggests the target
("structural-address obligation closed") was the result of audit-walk
rather than a forward derivation. v13's "stream merge with M40" tells
the story: the M41 work had drifted away from M40's algebra and needed
a rebase. After the rebase, audit pressure produced 9 more versions.

**Drift cost**: large in token-budget but contained — the trajectory
landed cleanly at v22.0 with the audit chain closed. Future sessions
should read v22.0 and v19 first; v13–v18 are correction passes.

### Type-C drift: artefact-narrative gap (RESOLVED — material in scratch/)

This finding is now resolved. The narrative names Python modules that
were not in the committed tree at catalog-build time; the user has
since placed all historical material in [../scratch/](../scratch/),
which is now tracked across 10 thematic commits. The four modules
required by the committed code:

| Module | Referenced from | Narrative source | Location |
|--------|----------------|------------------|----------|
| `chart_chained` | [../applied_grammar.py:175](../applied_grammar.py), [../verify_applied_grammar.py:15](../verify_applied_grammar.py) | M37 (4-axis chained ops), built on M11→M14→M34→M35→M36 evolution | [../scratch/chart_chained.py](../scratch/chart_chained.py) |
| `meta_protocol` | [../s4_structure.py:29](../s4_structure.py), [../applied_grammar.py:795](../applied_grammar.py) | declarative protocol foundation (M22-bis onward) | [../scratch/meta_protocol.py](../scratch/meta_protocol.py) |
| `unified_address` | [../applied_grammar.py:176](../applied_grammar.py), [../applied_grammar.py:799](../applied_grammar.py) | M38 (`encode_op`, `UnifiedCodeword`) | [../scratch/unified_address.py](../scratch/unified_address.py) |
| `spectral_view` | [../applied_grammar.py:177](../applied_grammar.py) (`fwht`) | M40 v6 (`spectral_view.py — M40 (v6)`) | [../scratch/spectral_view.py](../scratch/spectral_view.py) |

Per-move implementation files for nearly every move are in scratch/
and bound to specific K-claims in [claims.md](claims.md). A verifier
suite is also present — see `verify_*.py` files in scratch/.

**Drift signal (reproducibility)**: now LOW. The verifier suite can be
run by adding [../scratch/](../scratch/) to PYTHONPATH.

**Drift signal (design fidelity)**: low; the committed code matches
the narrative at API level.

**Findings from scratch/ inspection (revised)**:

1. **The "chart variants" are kernel evolution, not parallel forks.**
   The five files `chart (6).py`, `chart_meta.py`,
   `chart_with_inverses (1).py`, `chart_full_v4 (1).py`,
   `chart_chained.py` are the chronological build-out of the chart
   across M11+M14 → M34 → M35 → M36 → M37, each adding the next
   layer of operations to the previous. Only the last
   (`chart_chained`) is the import target of the committed code; the
   others are reference snapshots of earlier states.
2. **Browser-download artefact naming.** Files with `(N)` suffixes
   indicate cross-session-LLM provenance — successive saves of
   regenerated code across many separate LLM conversations.
3. **The "older narrative" is identical, not older.**
   `cotype-free-self-extending-grammar (16).md` is byte-identical
   (md5 f1c2fc03b5d69e8ce839dd1b1baa50f3) to the committed
   [../cotype-free-self-extending-grammar.md](../cotype-free-self-extending-grammar.md).
   It is a duplicate download, not a prior iteration. Same applies to
   `scratch/applied_grammar (1).py` (identical to committed
   applied_grammar.py), `scratch/s4_structure.py` (identical to
   committed), and `scratch/verify_applied_grammar.py` (identical
   to committed). These four duplicates are intentionally left
   untracked.
4. **Pre-rebase M41 is genuinely older.**
   `applied_grammar_v12_backup.py` (48 KB) captures M41 v12 —
   "sum-type receipts, StateOpSpec registry, fail-closed verification,
   strict_replay_context manager" — before v13's stream merge brought
   M41 onto M40's algebra. The diff between v12 and committed v22.0
   (189 KB) is the most legible record of what the v13→v22.0 audit
   chain produced.

**No outstanding Type-C drift.** Catalog claims that cited absent
modules are now bound to located files; verifier-witnessed claims have
runnable witnesses available.

### Type-D drift: operational choice-rigidification

A gauge-free choice the mathematics permits is treated by an LLM as
permanent, built into the operational substrate (verified-as-contract,
content-addressed-against, depended-on by downstream digests), and
becomes immovable. When a later move wants a different choice (the
formally cleaner one), the system can't substitute — a translation /
agreement layer gets grafted on. The bridge is the residue of the
rigidification. Structurally related to Type-B drift but distinct: a
Type-B version chain is multiple-versions-preserved; a Type-D
rigidification is one-version-frozen-and-unmovable.

**Instance: the lex-min canonical V_4 translate (M41 v16 → v19).**

The mathematics of K-orbit-canonical-bijection (M41 v16) permits any
V_4 translate in an orbit as the canonical representative — the
"topos's freedom" M2 named as commitment #4. The prior LLM session
chose lex-min and:

- Gave it a structural-sounding justification:
  *"Canonical signature within an orbit = lex-min over the 4
  V_4-translates (the 'left-choice' of the Cayley-Dickson framing)"*
  ([../cotype-free-self-extending-grammar.md:6469](../cotype-free-self-extending-grammar.md)).
  Wrapping a choice in a structural rationale obscures that it was
  a choice.
- Built `_ORBIT_TABLE` at module load with the lex-min as the 'e'
  entry ([../applied_grammar.py:861-905](../applied_grammar.py)) —
  the **fixed reference frame** for the rest of M41.
- Content-addressed `ContentAddressedReceiptFields.v4_delta`
  **relative to the lex-min canonical**
  ([../applied_grammar.py:1212-1255](../applied_grammar.py)). Every
  receipt now encodes the choice.
- Wrote `canonical_at_delta_e_in_cache` and
  `canonical_is_lex_min_in_orbit` verifiers
  ([../cotype-free-self-extending-grammar.md:6359, 6534, 6550](../cotype-free-self-extending-grammar.md))
  — verifying the *specific* choice as a contract, not the *abstract
  property* (a canonical is a deterministic function of orbit_key).
  The choice is now load-bearing.

At v19, the formal V_4 ⋊ S_3 framing identified Stab(D)-representative
as the natural canonical (the unique permutation in each orbit that
fixes the anchor axis D). The lex-min could not be displaced — the
content-addressing and verifier contracts had frozen it. The residue:

- `v17_to_v4_s3` ([../applied_grammar.py:1289-1310](../applied_grammar.py))
  — a function that translates from one canonical to the other.
- `verify_v17_v19_decomposition_agreement` ([../applied_grammar.py:1313-1326](../applied_grammar.py))
  — the agreement theorem proving they're inter-derivable.
- `verify_canonical_offset_consistent_per_orbit` ([../applied_grammar.py:1329-1346](../applied_grammar.py))
  — proves the per-orbit δ between the two canonicals is well-defined.
- The narrative names the tension as the *"alphabetical-vs-anchor
  choice"* ([../cotype-free-self-extending-grammar.md:5864](../cotype-free-self-extending-grammar.md))
  — the LLM saw the conflict but resolved it by bridging, not by
  re-choosing.

**Why this matters for K-orbit-canonical-bijection's realisation of M2.**
The realisation is *mathematical* but not *operational*. The math
admits any V_4 translate as canonical; the implementation admits only
lex-min as canonical. M2's "topos's freedom" is technically present
in the math and structurally absent in the code. This is the same
LLM-pathology family as the negation-overclaim case
([drift Type-A K-v4-twins-fail-cells](#type-a-drift-move-ordinal-collision-the-llm-lost-its-place)
and the [LEM-rejection rule](README.md#epistemic-discipline-lem-is-rejected)):
the LLM commits operationally to more than the math requires.

**Recovery action available**: refactor the v17-canonical reference
out of the content-addressing layer; have receipts content-address by
orbit_key only (gauge-invariant) with v4_delta carried as additional
data that needn't be reproducible from the codeword. This would
restore the topos's freedom operationally. Listed as deferred work.
Until then, `canonical_signature_in_orbit` returning lex-min should
be read as "lex-min was picked among gauge-equivalent options," not
"lex-min is THE canonical."

**Instance: AXES = ('D', 'C', 'S', 'W') — the upstream axis-tuple choice.**

The substrate has 4 axes; the math admits any 4-element set with any
ordering. [../scratch/meta_protocol.py:26](../scratch/meta_protocol.py)
declares `AXES = ('D', 'C', 'S', 'W')` as a module-load constant.
This single choice cascades:

- [../s4_structure.py:84](../s4_structure.py): `IDENTITY = Permutation(AXES)`
  — the group identity is *literally* the tuple `('D','C','S','W')`.
- [../s4_structure.py:91](../s4_structure.py): `S4_ELEMENTS = [Permutation(p) for p in permutations(AXES)]`
  — every group element enumerated in AXES-permutation order.
- [../s4_structure.py:73](../s4_structure.py): `is_identity` is
  `self.image == AXES` — identity-check is literal tuple comparison
  with this specific ordering, not abstract.
- Lex-min canonicality (the prior instance above) is Python tuple
  comparison on signatures whose components are AXES strings. Since
  'C' < 'D' < 'S' < 'W' alphabetically, lex-min signatures start
  with 'C'. **Rename AXES to ('A','B','C','D') in alphabetical order
  and lex-min picks different signatures.** The lex-min rigidification
  is downstream of the AXES rigidification.
- "Anchor axis D" is "the first AXES element"; Stab(D) is "the
  stabilizer of AXES[0]." Reorder AXES and the anchor moves with it.

The choice has no bridge layer because no later move ever attempted
to substitute it. The rigidification is so deep it became
unquestioned — never appeared as a choice point in the corpus once
made.

**Instance: Stab(D) as the specific S_3 complement.**

The math: S_4 / V_4 ≅ S_3. The S_3 complement to V_4 in S_4 is
realised concretely as the stabilizer of *some* axis — there are 4
gauge-equivalent choices (Stab(D) / Stab(C) / Stab(S) / Stab(W)),
all conjugate under V_4 since V_4 acts transitively on the 4 axes.
The corpus chose Stab(D) and:

- [../s4_structure.py:204](../s4_structure.py): `stab_d_to_orbit_key`
  function — keyed by the choice.
- [../s4_structure.py:702-717](../s4_structure.py): verifiers
  `verify_stab_d_size`, `verify_stab_d_is_subgroup`,
  `verify_stab_d_complements_v4` — test the *specific* choice as a
  contract, not "S_3 = stabilizer of some axis."
- M41 v22.0 builds AddressedOp / StructuralAddress around
  `(orbit_key, v4_delta)` where orbit_key ∈ Stab(D)-representatives.
  Every receipt encodes Stab(D) implicitly.

Cascade: this is downstream of AXES (D is AXES[0]) and adjacent to
the lex-min instance (lex-min's `'α' = (DC)(SW)` is precisely the V_4
element that exchanges anchor D with lex-min-letter C — see
[../cotype-free-self-extending-grammar.md:5864](../cotype-free-self-extending-grammar.md)).

**Instance: PAIRINGS α / β / γ ↦ specific V_4 elements.**

The math: three non-trivial V_4 elements (three double-transpositions
in S_4); three labels {α, β, γ}; bijection between them is a choice
(S_3 acts on the labels permuting them; 6 valid label-assignments).
The corpus chose at [../scratch/meta_protocol.py:29-33](../scratch/meta_protocol.py):

```text
PAIRINGS = {
    'α': (frozenset({'D', 'C'}), frozenset({'S', 'W'})),
    'β': (frozenset({'D', 'S'}), frozenset({'C', 'W'})),
    'γ': (frozenset({'D', 'W'}), frozenset({'C', 'S'})),
}
```

Rigidification:

- [../scratch/meta_protocol.py:226-231](../scratch/meta_protocol.py):
  `OPERATION_DESCRIPTIONS` is keyed by `(label, chirality)` with
  semantic content per label — `('α', 'even'): 'apply / reduce'`,
  `('γ', 'even'): 'compute-validated store'`, etc. Re-labelling
  α↔β at the dictionary level would re-shuffle which V_4 element
  is called "apply" — and the labels appear as string literals
  throughout downstream code, so the choice can't be substituted
  cleanly.
- All `signatures_in_orbit` enumerations iterate `('e', 'α', 'β',
  'γ')` ([../applied_grammar.py:961](../applied_grammar.py)) —
  the label ordering is baked into iteration order, so any
  position-dependent code (e.g., "delta='e' is canonical") depends
  on which element is named 'e' (= identity).

Cascade: this is downstream of AXES (the PAIRINGS reference the
strings 'D','C','S','W'). Also adjacent to the lex-min cascade
(lex-min orbit enumeration uses the same label ordering).

### The Type-D cascade

These four instances are not independent; they cascade from a single
upstream choice.

```text
AXES = ('D', 'C', 'S', 'W')                  [meta_protocol.py:26]
    ├── determines string-comparison order
    │       ↓
    │       lex-min canonical V_4 translate     [Type-D primary instance]
    │       ↓
    │       v17 content-address chain
    │       ↓
    │       v17 ↔ v19 agreement theorem        [the residue]
    │
    ├── AXES[0] = 'D' (the first axis)
    │       ↓
    │       Stab(D) as S_3 complement           [Type-D, axis-anchor]
    │       ↓
    │       AddressedOp / StructuralAddress     [downstream]
    │
    └── String literals 'D','C','S','W'
            ↓
            PAIRINGS bijection α/β/γ → V_4      [Type-D, label-choice]
            ↓
            OPERATION_DESCRIPTIONS              [downstream]
```

The cascade has *no internal bridges* — every layer depends on the
layers above with no translation theorem. The lex-min ↔ Stab(D)
bridge (`verify_v17_v19_decomposition_agreement`) exists at one
specific seam (when v19 introduced Stab(D)-canonical alongside v17's
already-rigidified lex-min); no analogous bridge exists for AXES
reordering or PAIRINGS relabelling because the corpus never tried.

This is the structural signature of how an apparent "discovered
foundation" is actually a stack of choices. **The user-facing risk**:
a future LLM reading the corpus may treat AXES = ('D','C','S','W')
as a mathematical primitive rather than as a labelling convention.
The catalog records here that it is *not* a primitive.

**Recovery action available (deferred for the whole cascade)**:
parametrise the AXES tuple as an argument to the relevant constructors
(at minimum: Permutation, the orbit tables, the PAIRINGS dictionary).
Verifiers should test abstract properties (e.g., "S_3 = Stab of some
axis," "canonical is a deterministic function of orbit_key") rather
than literal AXES-dependent values. This is a larger refactor than
the lex-min recovery and may be best deferred until a concrete
motivation arises (e.g., extending to a 5-axis system at higher
Hadamard levels).

### Type-D sub-variants (rigidification mechanism varies)

The hunt surfaces three additional Type-D instances with different
rigidification mechanisms — not all Type-D rigidifications work the
same way. Distinguishing them sharpens what to look for in future
audits.

#### Sub-variant: empty-bridge rigidification (integer-as-path founding)

**The most dramatic find of the second-round hunt.** M2's narrative
explicitly admitted four representations as first-class:
*"Function-as-path / Trace-as-path / Polynomial-as-path (GF(2^k))"*
([../cotype-free-self-extending-grammar.md:112-114](../cotype-free-self-extending-grammar.md)),
with integer-as-path as the locally-pragmatic founding choice and the
others "reachable via S7" — the `transform(k, src_rep, tgt_rep)`
operation. M2 even flagged the lex-min recovery for itself:
*"any vertex could have been chosen; the founding is a free choice
respecting the structure"*
([line 141](../cotype-free-self-extending-grammar.md)).

The rigidification mechanism is unlike the lex-min case. There is no
verifier-as-contract, no content-addressing dependency, no
agreement theorem. Instead:

- [../scratch/chart.py:214-226](../scratch/chart.py): the `transform`
  method exists as API surface, but its body is `NotImplementedError`
  for any non-identity transform:

  ```python
  def transform(self, k: Any, src_rep: str, tgt_rep: str) -> Any:
      if src_rep == tgt_rep:
          return k
      rot = (src_rep, tgt_rep)
      ...
      raise NotImplementedError(f"transform {src_rep} -> {tgt_rep}")
  ```

- No `function-as-path`, `trace-as-path`, or `polynomial-as-path`
  implementations exist anywhere in the corpus. The alternative
  representations are *named* and *unimplemented*.

The rigidification IS the absence: M2 promised first-class
multiplicity; the corpus delivered one operational representation
and a placeholder API for the others. The placeholder API is the
**empty bridge** — its presence affirms the promise; its body
defeats it.

**Why this is the most consequential Type-D find**: the lex-min and
AXES rigidifications constrain *which choice* is operational among
gauge-equivalent options. The integer-as-path empty-bridge eliminates
the *existence* of operational alternatives. M2's "topos's freedom of
representation choice" is operationally nil.

**Recovery action available**: implement `transform` for at least one
alternative representation (`trace-as-path` is the most testable —
it would unfold an apply-chain as a path) so the API is operationally
non-empty. The empty-bridge pattern is recoverable; the AXES cascade
is not (without a refactor).

#### Sub-variant: per-instance rigidification (designated identities)

M3 explicitly enumerated the designated-identity choices as "open
structural choices" the founding set leaves underdetermined
([../cotype-free-self-extending-grammar.md:88-94](../cotype-free-self-extending-grammar.md)),
then committed them at M3-resolution:
`nil = 0, true = 1, false = 2, failure = 3` (M3's C2).

The rigidification at [../scratch/chart.py:40-46](../scratch/chart.py):

```python
self.NIL     = 0
self.TRUE    = self.cons(0, 0)   # 1
self.FALSE   = self.cons(0, 1)   # 2
self.FAILURE = self.cons(1, 0)   # 3
self.S       = self.cons(3, 3)   # 4
self.K       = self.cons(3, 0)   # 5
self.I       = self.cons(0, 3)   # 6
```

This is per-instance rigidification: each `Chart` instance has its
own NIL/TRUE/FALSE/FAILURE/S/K/I as instance attributes, NOT module-
level constants. The integers (0, 1, 2, 3, ...) are determined by
the hash-consing order at instance construction. Two `Chart`
instances built identically will have the same indices; two with
different construction histories may not.

**Implication**: receipts emitted by one chart and replayed against
another require the cons-order to match. The integers are
operationally local to a chart instance but structurally local to
the M3 commitment. M3 said *which* commitment was made; chart.py
implements that specific commitment as the construction recipe.

**Strength**: weaker Type-D than AXES because re-ordering would only
affect cross-chart receipt portability, not the algebraic structure
itself. But the choice is real, and the integers do appear as
literals in atom_map ([../scratch/chart.py:186-190](../scratch/chart.py))
and likely elsewhere.

#### Sub-variant: structurally-partially-motivated rigidification (codeword bit layout)

The 5-bit codeword layout used throughout M38–M41 is
([../applied_grammar.py:623-672](../applied_grammar.py),
[../scratch/unified_address.py:88-103](../scratch/unified_address.py)):

```text
bit 4    : chirality   (0=even, 1=odd)        [1 bit]
bits 2-3 : pairing                             [2 bits]
bits 0-1 : witness                             [2 bits]
```

20+ hardcoded extractions: `(code >> 4) & 1`, `(code >> 2) & 0b11`,
`code & 0b11`, and recompositions
`(chir_bit << 4) | (pairing_bits << 2) | witness_bits`.

**The math admits any bit permutation as a valid layout**. The
chirality bit could be at any position; the pairing and witness
blocks could swap; non-contiguous layouts are also valid.

**Partial structural motivation**: putting chirality at the MSB
aligns with the parity-sieve / codeword-distance / inverse-pair
structure — chirality flip (M35 Z_2 inverse-pair completion) is
literally `code XOR 0b10000`. That's a structural argument FOR
this layout. But it is not the unique valid layout — chirality at
the LSB (with everything shifted up) would have the same distance
properties.

**Rigidification mechanism**: bit-level operations hardcoded
throughout codec functions; no `BIT_LAYOUT` abstraction; no
verifiers test "chirality occupies one bit at some position" —
they test "chirality is bit 4."

**Strength**: moderate. Partial structural motivation pulls toward
this layout but doesn't determine it. Recovery would require
parametrising the bit positions; not motivated by current scope.

#### Sub-variant: label-only rigidification (chirality even/odd convention)

The sign homomorphism S_4 → Z_2 is the unique non-trivial
homomorphism (mathematically canonical). The choice that remains is
**which Z_2 element gets which label**:

- [../scratch/chirality_as_parity.py:34](../scratch/chirality_as_parity.py):
  `def sign(perm)` returns `0` (even) or `1` (odd).
- "even" maps to A_4 (the kernel of the sign homomorphism); "odd"
  maps to S_4 \\ A_4 (the non-identity coset).
- "0=even, 1=odd" is the integer-encoding convention.

There are 2 valid sign conventions and 2 valid integer-encodings
(0/1 vs 1/0), so 4 valid combinations total. The corpus picked one.

**Rigidification mechanism**: pure label-binding. No
verifier-as-contract, no content-addressing dependency beyond what
the bit-layout already encodes. Re-labelling (e.g., "even=1,
odd=0") would flip every chirality bit but produce a structurally
identical system.

**Strength**: weak. This is the cleanest case of "trivially
recoverable label choice" — a future reader who needs the opposite
convention can swap globally with no other consequences. Calling it
out is mostly so the catalog records that the convention IS a
choice and not a discovered structure.

### Type-D taxonomy after the second-round hunt

| Sub-variant | Mechanism | Recoverability | Bridge layer? |
|------|-----------|----------------|---------------|
| Verifier-contract (lex-min) | Choice tested as contract; content-addressed against | Hard — receipts encode the choice | Yes (v17↔v19 agreement theorem) |
| Unsubstituted-foundation (AXES) | Choice cascades unquestioned through entire module-load chain | Hard — touches almost everything | None |
| Empty-bridge (integer-as-path) | API placeholder + `NotImplementedError` body | Medium — fill in the bridge bodies | The API surface IS the bridge — empty |
| Per-instance (designated identities) | Construction recipe assigns specific indices | Easy per-chart, hard cross-chart | None |
| Partially-motivated (bit layout) | Bit-level hardcoding with partial structural argument | Medium — parametrise positions | None |
| Label-only (chirality convention) | Pure naming choice | Trivial — global rename | None |

The taxonomy is now load-bearing for future audits: when a Type-D
candidate is found, classify it by mechanism to estimate recovery
cost. Verifier-contract and unsubstituted-foundation are the
expensive ones; label-only is free.

## Open questions surfaced by the catalog

These are not in the corpus explicitly; they emerge from cataloguing.

1. **What was v1–v12 of M40?** v6's preserved-version chain explicitly
   names v1 (Hadamard substrate) through v6, but the source markdown
   only preserves v3 onwards as full sections. v1, v2 are mentioned in
   docstrings but never given a top-level move section. Did they
   correspond to earlier M-numbered moves we haven't connected?
2. **What was v1–v12 of M41?** The applied_grammar.py docstring lists
   the chronicle but the source markdown only preserves v13 onwards.
   Same question: do earlier-numbered M-moves cover these?
3. **Does the final M33 audit (line 8029) point to a specific
   implementation bug, or is it a re-statement of the open finding?**
   The status is "negative — still open" but the corpus may have a
   resolution that the catalog missed.
4. ~~K-cocycle-unifies-formal-systems (M8) is stated then never
   reused directly.~~ **Resolved** (user-confirmed, 2026-05-15):
   the M22 Walsh-Hadamard quotient algebra realises the M8 cocycle
   projection. Edge drawn in
   [§ Realisation edges](#realisation-edges); K-cocycle-unifies-
   formal-systems promoted from `open` to `shown via realisation`
   in [claims.md](claims.md).

## Coverage gaps

- Edges from claims to specific verifier function names in
  [../applied_grammar.py](../applied_grammar.py) are partial; only
  load-bearing verifiers are linked.
- Most lateral edges within the M28–M37 V₄/S₄ phase are summarised at
  the level of the move; finer edges (e.g., between Z₂ inverse-pair
  paths and V₄ extension geometry) are not drawn.
- The (constructible, reachable, observable, coverable) charter-check
  tables at the bottom of major moves could each become an edge
  cluster. Not done in this first pass.
