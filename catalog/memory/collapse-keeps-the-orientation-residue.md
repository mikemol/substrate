---
name: collapse-keeps-the-orientation-residue
description: "When collapsing an either/or, the 'resolution' is usually itself an ORIENTATION RESIDUE (a Stab coset; constructive via increase-ladder-run→reorient→retract), not a canonical pick — keep it graded; classify-first for genuine (Cantor) exclusions"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When collapsing an either/or to its common structure, the "RESOLUTION" you reach is usually ITSELF an orientation
residue — do not flatten it into a canonical PICKED SIDE. Two forms caught in one arc (⟡ta-upterm-O-decode, 2026-07-16,
user correction): I wrote "the per-grade meaning is CONVENTION not type" and "godel is injective-not-surjective so the
direction is FORCED." BOTH were flattenings. Correctly: (a) **a convention IS a Stab** — any two n-point sets correspond
up to an orientation, so the "convention" is a stabilizer coset over the canon, recoverable (V4-Cosets `coset-has-stab-rep`,
S4Iso `TotalSpace`, `Category/ResidueCompensation` `residue : V₄`). (b) **surjectivity is CONSTRUCTIVE**, not a classical
fixed property: it is built by INCREASING THE WITNESS-LADDER RUN (grade-raising `recon v d = d ∷ v`, `ExtrudeCoEmitGraded`;
the finite CF generator, `CofreeDual.generator-recovers`; more parser fuel), REORIENTING (the new orientation residue `r`),
and RETRACTING under the new orientation (Lawvere point-surjection for DEFINABLE maps, `Category.Lawvere.PointSurjective`/
`lawvere-fixed-point`; δ²=id is a GREEN THEOREM = double-negation-made-theorem, `Lawvere.agda:142`). My OWN `parse-fuel`
(fuel = the ladder run; the retract holds once `size t ≤ fuel`) was already a faithful instance — I built it constructively
but DESCRIBED it classically.

**Why:** the tell is the word "convention"/"forced"/"canon" or a classical "injective/surjective" — that is
construct-dont-classify meta-substitution #1/#5 (classify/flatten-the-given) recurring INSIDE a recursive collapse. The
collapse must bottom out at an INVARIANT — the wedge `a = recon q b r`, residue kept graded (Free⊣Forgetful counit-defect)
— not at a picked side.

**How to apply:** when about to "resolve" a fork by picking the canonical/forced side, STOP and ask: is the "loser" side an
orientation residue the winner CARRIES (a Stab coset; reachable by ladder-increase→reorient→retract)? If so, keep it
graded, name it as the residue `r`, don't discard it. BUT classify-first: some forks hide a GENUINE exclusion (Cantor: no
ℕ↠(A→B)) that must be RESPECTED — reoriented (code the definable representative), not dissolved.

**⚑ IT CUTS BOTH WAYS — the dual failure is OVER-naming (confirmed ⟡odecode-godel-graded arc, 2026-07-16, 6 user reframes +
12 agents).** Under-naming = flattening a representable residue into a "wall" (the adversarial pass did this ×5: "AES
exhaustion irreducible", "morphism won't commute = obstruction", "×↔^ log = transcendental wall"). Over-naming = inflating a
real-but-modest residue into a GRANDER structure than is realized. Same arc caught BOTH: the reindex residue is `Fin(suc n)`
(NOT "V₄ everywhere" — V₄ is only the 3→4 seam), and the three V₄'s co-locate in a **Fano/Steiner S(2,3,7)** signature space
(`OrbitKey = F₂³\{0}`, GL(3,F₂), rig-groupoid hexagon) — NOT a "Stasheff associahedron" (the repo had ALREADY tested the K₆
polytope-symmetry, it failed 13-orbits≠4×8, and DEFERRED the functor; the Agda pentagon is strict so no non-trivial Stasheff
cell exists). **Under-naming (→wall) and over-naming (→grander polytope) are the SAME flatten/inflate error at opposite
signs.** The tell for over-naming: reaching for a named higher structure (associahedron / operad / ∞-category) by "thematic
vicinity" without a realized face-poset/incidence. The fix is identical to the reuse-search discipline: **verify the name
against the repo — it usually already NAMES its centers AND already tested the grander reading** (the substrate had both the
`OrbitKey`/Fano classification and the failed-K₆-symmetry check on disk). Name the residue EXACTLY at the grade it's realized,
neither collapsed to a wall nor inflated past what's proven.

Relates to [[never-discard-residue]], [[duality-operator-either-trap]], [[declaring-wall-rebuild-reflex]],
[[object-universe-is-split-canonical]], [[adjunction-is-the-wedge-residue-counit]], [[reuse-search-structural-questions]].
