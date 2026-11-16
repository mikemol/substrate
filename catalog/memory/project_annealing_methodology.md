---
name: project-annealing-methodology
description: "The substrate refactor methodology — small, predictable, mechanical, monotonic-asymmetry-decreasing steps verified by graph-similarity scripts between each step. Not clever leaps."
metadata: 
  node_type: memory
  type: project
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

The substrate's refactor methodology (articulated by user, 2026-05-16):

**Anneal, don't leap.** Work like a torsor on local neighborhoods, like slime mold consolidating at edges. Remove one degree of freedom per step. Use mechanical scripts (Jaccard, reachability, percentile-gap detectors in `scratch/`) to identify the smallest current asymmetry. Patch it. Re-run scripts. Repeat.

**Why:** clever multi-step refactors burn context AND introduce new asymmetries in axes the leap didn't account for. They look elegant in the moment but cost more tokens AND make the asymmetry-budget harder to track. The annealing alternative is monotonic in total asymmetry: each step CLOSES an asymmetry without opening new ones, verified mechanically by re-running the same scripts.

Concrete protocol:

1. Run the structural-gap detector (`scratch/percentile_gaps.py` or successors) — identifies all current high-similarity-with-gap pairs.
2. Pick the SMALLEST patchable gap (gap size 1–2, P90+ Jaccard).
3. Apply the most LOCAL patch that closes it (add a single edge, a few refls, etc.).
4. Type-check the patched module + downstream.
5. Re-run the detector — verify the gap closed AND no new asymmetries emerged.
6. Commit.
7. Repeat.

**How to apply:**

- **Scripts propose the next step. We don't.** After landing a small mechanical patch, run the detectors and let them surface the next asymmetry candidate. Do not pre-propose structural collapses, parameterizations, or "the deeper refactor" from our own observation. If the script can't see it yet, the script needs improvement — improve the script, then let it surface the finding.
- Resist the urge to propose multi-step refactors when a one-step patch will close the immediate gap. The clever structural insight should come from a SCRIPT, not from us.
- After a clever multi-step refactor lands (failure mode), look back and improve the scripts so they would have surfaced step 1 first.
- Build the mechanical tooling FIRST (gap detectors, refl-clause detectors, structural-symmetry detectors, asymmetry trackers, contraction helpers). Refactors after.
- Each step's commit message should name the SINGLE asymmetry closed.
- When tempted to combine steps "since they're related", DON'T. Separate commits make the monotonic-decrease verifiable.
- Sister rule to [[feedback-two-path-commutativity]] (the meta-pattern those steps reveal); [[feedback-hough-resolution]] (the scripts that drive the annealing); [[project-homology-cohomology-recursion]] (the recursive applicability of the methodology at every level).

**Detectors the project needs (running list):**

- Module-level Jaccard / percentile gaps — DONE (`scratch/percentile_gaps.py`).
- Reachability-Jaccard — DONE (`scratch/reachability_dual.py`).
- Simplicial-shape (Delaunay-dual) — DONE (`scratch/simplicial_shape.py`).
- **All-refl-clauses detector** — NOT YET. Should scan Agda definitions for "all clauses RHS = refl" and report parameterization candidates.
- **Structural-symmetry detector** — NOT YET. Should find pairs of functions whose clause-shapes are identical modulo one substitution.
- **Asymmetry-delta tracker** — NOT YET. Should diff Jaccard/reach output across commits to verify monotonic decrease.

**Anti-pattern (recognized):** "I can see N steps ahead, let me do them all at once." This is the leap. It costs tokens AND obscures which step closed which asymmetry. Replace with: "Run the detector. Apply the smallest patch the detector recommends. Re-run."
