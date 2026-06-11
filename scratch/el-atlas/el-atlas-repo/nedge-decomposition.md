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
| G-values with L-space isomorphism, G_NOT/G_AND/G_OR, network dynamics | **The evidence carrier with the log codec**: the atlas as the rigorization of Nedge's Layer-2 / G-value semantics; lineage Nedge → BK4VL → Evidence–Differential cluster → atlas (extends Appendix B.0) | [S] lineage / [C] pending full G-value definition |
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

Unread: N4.docx full G-value definitions (is a G-value the pair itself? the
l-space iso suggests log coordinates of (E⁺,E⁻)); the v3.1 historical spec
folder; Philosophical Extensions; Nedge/DREN synthesis; Toulmin analysis
beyond snippet. Unverified: the GRC tetrahedron's exact role structure (G2
inheritance). Open: the cocycle question for GRC transformation contexts;
whether `is{is}` as diagonal seed survives a careful reading of the
multi-element block semantics (`{E1; E2; ...}` formalization is listed as
open in the source itself).
