# The Nedge decomposition (begun)

Status: first pass, corpus-grounded. Grades: [O] observed in source documents;
[S] structural identification (both sides constructed); [C] candidate reading
(stated, not yet instrumented). Sources: Drive folders "Nedge KR Foundational
Principles", "Nedge v4.0 Conceptualization" (+ "Philosophical Extensions",
"v3.1 Historical Specification", "Architectural Synthesis (Nedge/DREN)" —
listed, largely unread); "Nedge Foundation: Adversarial Justification Summary"
(read in full); "Nedge 4 Base.docx" / "N4.docx" / "Toulmin Analysis" (snippets).

## 1. The observed core [O]

**Principles** (per the AJ summary, verbatim-close): Mention Demands Existence
(`NodeName{}` asserts the node); Meaning Derives from Structure (positional
roles only; no inherent types; "verbing nouns"; no Subject/Predicate sugar);
Identity is Structural with the **identity-collapse principle** (identical
structural connectivity patterns ⇒ same identity; bare nodes initially
collapse, differentiate as participation grows); Compositional Structure via
Nesting (sole assertion form `Outer{Inner}`; sequences as right-nested chains;
role from depth); Self-Containment as goal; Minimalism/Necessity enforced by
**Adversarial Justification** (propose → adversarial critique on necessity,
minimality, identity-impact → survive ⇒ admitted).

**Bootstrap**: the single step `is { is }` — introduces the primitive,
instantiates `Outer{Inner}`, gives `is` non-null structure (prevents collapse
into the void state), and demonstrates the **First Distinction: the same node
in two positional roles**. Subsequent steps: `Nedge{}` + `Nedge{is}`;
reflection primitives (`IdentityTrace`, `SequenceFromStructure`,
`ReificationOfSequence`) and logic primitives, each minimally stabilized as
`X{is}`; the Positional Reflection Axiom (identity = reification of the
node's connectivity sequence).

**v4 layer** (snippets): the **PBF — Primitive Binary Framing Trace** =
`(OuterSymID, InnerSymID_or_PBF_ID)`: the atom is an ordered pair, nesting is
a binary tree, identity is a canonical string (hash) over nested frames. The
**4VL**: CC / UC / UI / CI = confidence × consistency, two independent bits.
The **G-Value Calculus** (Master Spec, Artifact B): G-values with G_NOT /
G_AND / G_OR, an **L-space isomorphism**, implication forms (G_res, G_mat),
conditional G(Q|P)_belief, network dynamics. Epistemology: "contextual
grounding over fixed axioms; emergent meaning from connectivity over rigid
type distinctions; consistency/confidence over internalized true/false."
OSI layering: L1 algebra/geometry/topology; L2 set theory/FOL; L3 Nedge NUs.

## 2. The decomposition map

| Nedge component | Atlas structure | Grade |
|---|---|---|
| `Outer{Inner}` sole assertion form; First Distinction = positional role | The 2-pin frame; meaning begins at the pair, not the point (Lemma 2.5 family: the single channel is identity-anchored; distinction requires the second pin) | [S] |
| `A{B}` vs `B{A}` chirality; the corpus's Möbius/deck-transformation reading (H1) used this syntax | The swap involution S; order-sensitivity = the swap-visible axis; pair = double cover, swap = deck transformation | [S] |
| PBF trace (Outer, Inner-or-PBF): atom = ordered pair, nesting = binary tree, identity = canonical string | **The doubling interface's untwisted shell** (§5.9): the free binary tree on ordered pairs, cocycle not yet chosen; canonical-string identity = the Walsh-side canonical form. Whether GRC transformation contexts introduce a twist class is the open cocycle question | [S] structure / [C] cocycle |
| Identity-collapse principle: identical connectivity ⇒ same identity; differentiation grows with participation | **The indexed-verdict / separator discipline**: identity = unseparated-in-S, where S is the current space of structural probes; extending the space (new participation) can separate previously-identical nodes. Nedge states as ontology what the harness practices as method — "resistance to separation as evidence of identity" is the Positional Reflection Axiom operationalized | [S] |
| Adversarial Justification (necessity / minimality / identity-impact critique) | The break-and-separate loop at design level: necessity = dependency-edge detection; identity-impact = does admission separate collapsed nodes; AJ's admission rule = the knob-admission rule | [S] |
| `is{is}` diagonal seed; minimal stabilization `X{is}`; collapse-to-void prevention | The carrier origin (0,0) as the unique total-ignorance point where all bare nodes coincide; one quantum of structural participation = mass moving a node off the origin; identity-collapse at zero structure = N-corner degeneracy | [C] |
| 4VL: CC/UC/UI/CI = confidence × consistency | A **P2-G gate on (mass-threshold, conflict-threshold)** — both Nedge bits are encoding-level functions of the pair (confidence ≈ mass, consistency ≈ conflict-absence), unlike Belnap's (bias-sign × mass-rail) chart. **Two four-valued logics = two corner-charts of one carrier**; neither refines the other | [C] → candidate claim NVL |
| G-values with L-space isomorphism, G_NOT/G_AND/G_OR, network dynamics | **The evidence carrier with the log codec**: the atlas as the rigorization of Nedge's Layer-2 / G-value semantics; lineage Nedge → BK4VL → Evidence–Differential cluster → atlas (extends Appendix B.0) | [S] iso / **[W] lift** (see §6 addendum) |
| Consistency/confidence over internalized true/false; contextual grounding over fixed axioms | The prohibition + the classical section: truth values are not carried, they are read at a section; classicality is a locus, not a foundation | [S] |
| GRC tetrahedron: three roles + self | Corner representation: four corners with one anchored (the self = perspective), S₃ = Aut(V₄) as the frame group (Theorem 5.4 corner half; tetrahedron algebra grounding §11.4) | [C] — inherited from G2, re-verification queued |
| OSI L1/L2/L3 | The atlas's strata (algebraic interface / carrier-codec claims / catalog) | [C] loose |

## 3. What each side buys

**Nedge → atlas**: the KR application; the AJ archive as a pre-run separator
search over design space; the 4VL as a second, independently-invented corner
gate (evidence that the carrier's gate-plurality is real); the bootstrap as a
worked example of identity-from-zero-mass.

**Atlas → Nedge**: operational semantics for the identity-collapse principle
(indexed verdicts; SEP(·|S); space-extension as differentiation events);
Theorem 5.4's frame-invisibility for the chirality question (the swap is
invisible to in-chart linear reads — Nedge's positional distinction needs the
reading relation declared, per the ladder law); the doubling interface giving
the PBF tree its cocycle parameter (untwisted today; the twist is available
structure, not an obligation); the prohibition protecting G-values from
quotient-to-probability.

## 4. Candidate harness claims (not yet implemented)

- **NVL**: the Nedge gate (mass × conflict thresholds) and the Belnap chart
  (bias-sign × rail) are distinct partitions of the carrier; their common
  refinement is strictly finer than each. Knobs: gate thresholds.
- **IDC**: identity-collapse as unseparated-in-S; a designated node pair
  collapses in a small probe space and separates under a declared extension —
  the dynamic-identity schedule as a testable claim.

## 5. Residue ledger

N4 read COMPLETE (§6 addendum); the "is a G-value the pair?" question is
closed — it is the class of a pair. Still unread: the v3.1 historical spec
folder; Philosophical Extensions; Nedge/DREN synthesis; Toulmin analysis
beyond snippet. Unverified: the GRC tetrahedron's exact role structure (G2
inheritance). Open: the cocycle question for GRC transformation contexts;
whether `is{is}` as diagonal seed survives a careful reading of the
multi-element block semantics (`{E1; E2; ...}` formalization is listed as
open in the source itself).

## 6. Addendum — the N4 read: the G-Value Calculus in atlas coordinates

### Observed core [O] (Master Specification, Artifact B, Sections IV–IX)

**A G-value is a scalar.** G(P) ∈ [0,∞]; primary graded domain (0,∞);
boundaries 0/∞ are the rails (⊤/⊥ — the document oscillates between cost and
strength labels for which rail is which, but the algebra is unambiguous).
Operators: G_NOT(G) = 1/G (involution; exactly odds negation);
G_AND(G₁,G₂) = G₁G₂/(G₁+G₂) (series conductance; n-ary 1/Σ(1/Gᵢ));
G_OR = Σ (parallel conductance). Commutative, associative, DeMorgan EXACT,
non-idempotent (AND(G,G)=G/2, OR(G,G)=2G), non-distributive. Self-classified
"Reciprocal DeMorgan Resource Algebra"; the spec links it to Torres's dual
positive semifields, log-semirings, substructural/linear logic (contraction
halves, weakening is free), and residuated lattices. L-space: L = ln G ∈
[−∞,∞]; L_NOT = −L; L_OR = LogSumExp; L_AND = −LogSumExp(−·); idempotence
failure = ±ln 2, read via Landauer. G_res(P⇒Q) = sup{X | AND(G(P),X) ≤ G(Q)}
= G(P)G(Q)/(G(P)−G(Q)) if G(P) > G(Q), else ∞; G_res(P⇒P) = ∞.
G(Q|P)_belief = AND(G(P),G(Q))/G(P) = G(Q)/(G(P)+G(Q)) ∈ (0,1). Local
consistency: G(P)·G(¬P) = 1. Network semantics: least-fixed-point
equilibrium, semantic-energy minimization, confidence topography
Conf(G) = G/(G+1) = sigmoid(L) with CMS peaks / ES valleys / US_v2 plateaus;
non-idempotence tames cycles (no self-amplification from tautological loops).

### Identifications

1. **L-space ≅ 𝔸, G-space ≅ 𝕄, and the L↔G isomorphism IS Lemma 2.5b's
   exp⊣log codec** — formula for formula, identity images included
   (G=1 ↔ L=0). Nedge's "L-space isomorphism" and the atlas's two-chart
   structure are the same object. [S, near-W]

2. **A G-value is the quotient shadow.** G = odds = the ratio the prohibition
   refuses. G(P)·G(¬P) = 1 is the antipode constraint of a balance channel
   with NO mass axis: G = 1 conflates massive conflict with total ignorance —
   a Lemma 3.2 instance sitting inside Nedge's own Layer 2, while Layer 3's
   4VL (confidence × consistency) demands exactly the mass/conflict
   information the scalar destroys. The atlas is Nedge Layer 2 repaired by
   un-quotienting. [S]

3. **THE LIFT THEOREM** [W — pilot, 2000 random trials, all checks pass]: on
   formal-quotient pairs (n,d) with class n/d,
   G_OR = fraction addition ((n₁d₂+n₂d₁, d₁d₂)); G_NOT = the swap ((d,n));
   G_AND = swap-conjugated fraction addition; DeMorgan exactness = the swap
   distributing. Non-idempotence is the mass-growth shadow:
   (n,d) ⊕ (n,d) = (2nd, d²) ~ 2n/d, and conjugation gives G/2 — the
   calculus's "resource sensitivity" is the quotient remembering the extruded
   magnitude axis in distorted form. **The entire G-Value Calculus =
   ⟨fraction-⊕, swap⟩ on formal-quotient pairs.** This is Remark 3.6's
   representation-as-rationals read backwards: Nedge G-values are the carrier
   quotiented by the diagonal (mass); representation-as-rationals works
   pre-quotient; the atlas refuses the quotient entirely.

4. **G_res is resistance-difference**: 1/G_res = 1/G(Q) − 1/G(P), adjointness
   exact (pilot-verified). The implication is a DIFFERENCE taken in the
   swap-dual chart — the differential/bridge reading. [S]

5. **G(Q|P)_belief is the L1-normalization of the pair (G(P), G(Q))** — a
   c-pinning instance: conditional belief = the simplex projection of a
   two-component magnitude vector; Conf(G) = sigmoid(L) is the same chart one
   level down. [S]

6. **Lineage sharpened** (extends Appendix B.0): Nedge L2 (the quotient) →
   BK4VL → the consolidation cluster → the atlas (the pre-quotient restored).
   The atlas is not adjacent to Nedge's semantic engine; it is that engine's
   pre-quotient. [S]

### Candidate harness claim

**NGL** (Nedge G-lift): the six lift identities as executable checks over
carrier knobs. Coeff scope: real only — fraction arithmetic degenerates over
GF(2) (denominator products collapse), so NGL takes a coeff-guard like
T53/PHS. Landed: v3.4 run **S_fd5ddbe7ac57** (110,592 models) — NGL/NVL/IDC
aboard; the two-gate theorem machine-found (NVL = F under BOTH pinnings,
P only free); {NGL,V4I} one structure; IDC orthogonal to every carrier
knob (co-movement 0.20 with NOE, lowest in the instrument). Spec import:
§5.7e (draft 19).

### Residue from this read

The ∨E (proof-by-cases) G-value transformation is flagged open in the source
itself ("a key area for precise axiomatic definition in Phase 4"). The
cost-vs-strength label oscillation (which rail is ⊤) is a reading-relation
ambiguity — a ladder-law instance: the algebra is fixed, the order
declaration is not; any spec import must declare it first. The
"Confidence Topography" = sigmoid(L) chart suggests Nedge's US_v2 plateaus
live where the carrier's c-axis information would disambiguate — connects to
the NVL claim but is not yet instrumented.

## 7. Addendum — the runtime bridge (review-prompted, R1)

An external LLM review asked how the static, correct-by-construction map
bridges to dynamic runtime allocation at the memory layer. The question is
legitimate (the no-runtime-story residue was already ledgered); three
pieces of it are checkable, and all three checked (tools/
runtime-bridge-pilot.py, output committed):

1. **The prohibition is already deployed at the memory layer.** Replicated
   evidence with join-merge: the diagonal quotient b = E⁺−E⁻ is NOT a
   congruence for merge — 2,376 small-grid witnesses of equal-bias states
   with unequal-bias merges (first: (0,0) vs (1,1) against (0,1)). This is
   the PN-counter CRDT design fact: production distributed counters keep
   the pair *because the evaluated difference does not merge*. The
   refusal-to-quotient is load-bearing for eventual consistency — the
   carrier's famous instance at the runtime layer. [W pilot / S framing]

2. **Per-channel convergence dissolves the divergence worry.** Under
   cyclic support (pair power-iteration, positive weights) mass diverges
   monotonically while G = E⁺/E⁻ converges (Perron): the scalar
   G-calculus's least-fixed-point equilibrium is the projective shadow of
   carrier dynamics. The quotient was doing normalization work; the codec
   localizes it — fixed-point queries read the balance coordinate, mass is
   a monotone ledger (iteration/provenance weight) for GC and compaction
   policy. [W pilot for the linear instance / C general]

3. **Source-indexing dissolves the double-count.** The runtime carrier is
   the source-indexed pair vector: within-source merge idempotent
   (re-merging the same evidence does not double), cross-source read
   additive. G_OR(G,G) = 2G — the calculus's "overcounting bias if sources
   are not truly independent" — is the scalar shadow of erased provenance;
   contraction-halving is its worst-case dual. [W pilot / S]

Held open, unattributed (the review imported parsing vocabulary — ASPF,
SPPF, content-addressed memory — that appears nowhere in the corpus): SPPF
*packed nodes* share structurally identical derivations, which is the
identity-collapse principle as a storage discipline (IDC as the
content-address). Plausible import edge, not a document claim. [C]

Honest remainder: operational complexity (space per edge = 2×|sources|
scalars; equilibrium scheduling; compaction safety against the lift) is
genuinely open — the review's core point stands and stays in the ledger.
