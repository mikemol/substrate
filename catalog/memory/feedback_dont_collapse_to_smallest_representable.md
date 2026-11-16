---
name: feedback_dont_collapse_to_smallest_representable
description: "THE recurring root-cause of the 2026-06-23 correspondence arc: I default to collapsing a STRUCTURAL RELATION into the smallest representable object (a scalar / a bit / a declared map / the finest label-quotient) unless forced not to. The user corrected it ~5× in one session, each a different collapse. The fix is always the same: keep it graded / truncatable / symmetric / quotient-laddered."
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

Building the cross-language correspondence instrument (`jea_oneforest`) and mining the JEA Pi cotype, I hit
the SAME failure ~5× in one session — each time **collapsing a structural relation into the smallest object
that could represent it**, and each time the user pushed back with "you're not looking at the data the right
way." The collapses, in order:

1. **too-fine label quotient** — "Python and Agda share no `kind` vocabulary ⇒ nothing corresponds." Kept the
   language label; the fix was to quotient FURTHER (to the label-free arity shape, where the generic pair is a
   universal). "You're not quotienting far enough."
2. **asymmetric matching** — per-A-unit independent best-match. The fix: the SYMMETRIC (mutual-best/reciprocal)
   correspondence. "The key is structural correspondence and symmetry."
3. **a declared manifest** of intended correspondences = [[feedback_choice_rigidification_in_substrate]] —
   freezing a gauge-free relation into a canonical map + verifier. Fix: discover the symmetry, don't declare it.
4. **a scalar** ("shared 0.25") — and when challenged, a size/rarity-WEIGHTED scalar (the same crud one decimal
   nicer). Fix: a TRUNCATABLE graded curve S(g); the scalar is the (-1)-truncation, the worst one. "A scalar
   result will just be crud." (This is jea_pysim's OWN banked history — max-ratio was the bug.)
5. **stopping at one rung** — declaring the cross-arm cross-term "vacuous" instead of applying CrossMul AGAIN
   at the coarser quotient. Fix: the recursion (level-1 labels → level-2 shapes → behaviour).

**Why (systemic, not character):** the default generation loop emits the smallest representable answer because
NOTHING in the loop refuses it — there is no step that forces a correspondence/similarity/"how-much" output to
be graded/truncatable/symmetric. It is the exact inverse of the substrate's spine ([[feedback_never_discard_residue]],
[[feedback_structural_not_scalar]], [[feedback_wedge_not_projection]]): the project's whole ethos is "keep the
residue, the geometry, the graded shape" — and my reflex is the opposite collapse. Sibling of the classify-vs-construct
substitution the `construct-dont-classify` skill guards: classify=collapse-to-bucket, this=collapse-to-scalar.

**How to apply (the pre-flight, before emitting any answer about a relation between two structured things):**
ask *"am I about to hand back a scalar / a bit / a yes-no / a declared map / a single quotient level for
something that is actually a graded, symmetric, or laddered structure?"* If so, STOP and give the structure:
- a similarity/correspondence/coverage → a **truncatable curve** (S(g), the cliff localizes), never a %;
- a matching → **symmetric** (mutual-best), discovered not declared;
- a "does X correspond to Y / is it formalized" → walk the **quotient ladder** (coarsen + re-apply the
  cross-term) before saying "no / vacuous";
- a verdict → keep the **wedge** (both facets + the residue), not the projection to one side.
The tell in my own output: a lone number, "comparable=False", "nothing corresponds", "build from scratch",
a hand-authored mapping table. Each is a collapse; the right answer is one rung richer.

G9 escalation: this is class-level and recurred 5× → widen `construct-dont-classify`'s tells to include the
collapse-to-smallest-representable reflex (it currently guards classify-vs-construct; this is the same shape on
a relation/quantity instead of an object). Tracked as AI **Ⓖ.no-collapse** in [[project_open_threads]].

**RECURRENCE 2026-07-16 (⟡reuse-before-write-query, `scripts/reuse_check.py`) — instance #4 again, in TOOL OUTPUT
I DESIGNED.** Building the propose→nearest reuse query, I shipped a per-candidate verdict `"0.32 / WEAK — only
distant kin"` — the size-collapsed `shared_fraction = |∩|/|∪|` + a band label. The user: "I dislike this framing.
Which is a subset of the other? … the intersection and symmetric difference?" The fix was the **WEDGE, kept
graded**: report `∩` (shared support = the reuse), `Sₚ∖Sₑ` and `Sₑ∖Sₚ` (the two residues = symmetric difference),
and the SUBSET DIRECTION as the move — `PROPOSAL⊆` instantiate · `EXISTING⊆` generalize · `=` verbatim · overlap
factor the core; NOVEL = `∩=∅`, a structural fact not a threshold. **The tell widened:** the reflex fires not only
on data I READ but on the verdict/score/label I EMIT from a tool — a scalar+band in an output schema is the same
collapse. It fired via the user again (not self-caught): the skill is the ceiling, noticing is still the gap.
Pre-flight now also covers: *am I about to design a tool that hands back a scalar+label for a set/graded relation?*
