---
name: feedback_probe_wall_try_alternate_encoding
description: "A probe walling on ONE proof approach is not evidence the lemma is hard — try the alternate ENCODING (e.g. toℕ linear-index view for Fin combinatorics) before declaring research-grade. The wall is the approach's, not the theorem's."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

The G8 "execute the probe, show it fails" discipline is necessary but has a trap: a probe walls on
the FIRST approach you try, and it's easy to over-read that as "the lemma is hard / research-grade /
needs new infrastructure." The wall belongs to the APPROACH, not the theorem. Before declaring a
deep residue, try the alternate ENCODING of the same object.

**Caught 2026-07-10 (⟡rig-8 assoc, the graded-Lehmer-rig arc).** I executed-probed `combine-assoc`
(`subst Fin (*-assoc m n p) (combine (combine a b) c) ≡ combine a (combine b c)`) via the STRUCTURAL
route — induction on `combine` — and it genuinely walled: `combine (combine zero b) c` forces
`combine` to match on an `inject+` output, needing combine-over-inject+ distribution lemmas +
`*-assoc`'s non-structural (trans-of-distrib) subst threading. I then wrote it up as "research-grade,
a dedicated arc, NOT a tail-of-session grind." **WRONG.** The `toℕ` encoding sidesteps the wall
entirely: `combine i j` IS the linear index `i·n + j` (`toℕ-combine`, three trivial toℕ bridges), so
both sides have `toℕ = a·n·p + b·p + c`, and `toℕ-injective` closes it via pure ℕ arithmetic — no
`combine` induction, no distribution lemmas. The whole thing was ~40 lines and closed first try.
Same over-estimate on ⟡rig-7: I said "needs a punchIn∘inject+ chain that doesn't exist" — it was two
3-line structural lemmas (`punchIn-inject+`, `punchIn-inject+-raise`).

**Why:** finite-object lemmas usually have TWO views — the structural/constructor view (induct on the
data) and the semantic/measure view (`toℕ` for Fin, `lookup` for Vec/Perm, the universal property for
free structures). When the constructor view walls on a coherence/transport, the measure view often
turns it into arithmetic or extensionality. The wall on one is not a floor on the other.

**WIDER (2026-07-10, third strike): survey the APPROACH SPACE, not just one encoding; include
COMPUTATION.** This over-estimate recurred THREE times in one session — (1) combine-assoc "research-
grade" → toℕ arithmetic; (2) ⟡rig-7 "needs a punchIn∘inject+ chain that doesn't exist" → two 3-line
lemmas; (3) ⟡rig-13c "Laplaza's ~24 coherence diagrams, deep categorified residue" → the USER's idea:
since every structural iso is a finite PERMUTATION (its toℕ-action), the coherences are DECIDABLE by
computation — a ~100-line numpy script (`scripts/rig_coherence.py`) path-composed all 225 diagram-
instances and confirmed they commute, settling "do they hold?" in minutes; then each Agda formalization
closed FIRST-TRY as a toℕ/lookup identity (the numpy handed over the exact form). Root cause across all
three: I estimate difficulty from the FIRST approach that comes to mind (the direct structural Agda
proof) and never survey alternatives. **Difficulty is the MINIMUM over approaches, not the first one.**
Before writing "deep / research-grade / large residue / optional-only," enumerate the approach space:
{structural proof · measure-encoding (toℕ/lookup/β) · COMPUTATION (finite ⇒ decidable — numpy/brute
force to DISCOVER + de-risk, then formalize) · reuse of existing framework · appeal to a theorem}. For
anything FINITE, computation both settles the math question and de-risks the formal proof (compute-then-
formalize is a reusable pipeline). See [[reference_catalog_db_reuse_query]] (the reuse-tool instance of
the same "survey before concluding" discipline).

**How to apply:** before writing "X is research-grade / needs new infrastructure / a dedicated arc"
because a probe walled, ask: *is there an alternate encoding of the objects in X?* For Fin: `toℕ` +
`toℕ-injective`. For Vec/Perm: `lookup` + `lookup-ext`. For free/graded structures: the β/universal-
property interface ([[feedback_opacity_blowup_routearound_freeup]]). Try it; the residue is real only
if BOTH views wall. Sibling of [[feedback_reuse_search_before_feasibility_conclusions]] (this is the
proof-route analog: survey approaches, not just existing machinery) and the wall-can-wear-a-negative-
theorem discipline — here the wall wore a FALSE difficulty-estimate.
