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
