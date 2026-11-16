---
name: feedback_names_vacuous_shape_is_meaning
description: "names are vacuous handles; meaning is the shape they specialize to — \"structure is meaning\" at the primitive (reference) level; collisions are not bugs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

A NAME is vacuous on its own — it carries no meaning. You cannot use a name
unless you SPECIALIZE it by the shape it corresponds to. The shape IS the
meaning ("structure is meaning" at the most primitive level — the reference
level). (User, 2026-06-04, closing the session-long vacuity arc.)

**Why:** this is the bottom of the vacuity hunt — the arc went UPs → types →
fields → laws, and the floor is that *names themselves* are vacuous by default.
A bare name is the ⊤-collapse at the reference level: it distinguishes nothing.
Meaning enters only when the name is specialized to a shape (an SPPF node). So
the SPPF is the real namespace: shape-nodes are the identities; names are mere
aliases over them. To refer is to name a *node*, and a name alone doesn't — you
wedge the name against a shape to land on the node (bare name = unwedged =
vacuous). Agda already does a crude version: `R.f` = "the `f` of shape `R`";
module-qualification is a PROXY for shape (location standing in for structure),
and the typechecker refuses an unresolved bare name (this principle partially
enforced).

**How to apply:**
- Name COLLISIONS are NOT bugs to rename away. That is name-primary thinking
  (treating the name as the thing that must be unique). Shape is primary, so a
  name legitimately points at several distinct shape-nodes (`Line` = Fano vs
  grammar; `Section` = transfer vs discipline vs pedagogy; `Wedge` = generic vs
  ℕ-GCD). Do NOT rename to disambiguate; require shape-specialized USE.
- When labeling semantic SPPF nodes / building atlases: the node identity is
  the SHAPE, never the name. The `≃` bridges (the labels) are what prove two
  presentations are one node — not a shared name.
- Reverses an earlier (mine) instinct to "rename the collisions"; the
  collision-rename step DROPS OUT under this principle.

Connects: [[discipline/feedback_expose_generator_not_orbit]] (shape over name),
the session SPPF/realizability arc [[project_type_audit_sppf]] (shapes primary,
reactions primary, names vacuous — same lesson at three levels), and the
vacuity recognizer (a bare name is the ⊤-collapse of reference).
ENFORCEMENT SUITE (2026-06-04) — "lift shape-specialization somewhere visible to
the entity manipulating the code" (Agda resolves silently; readers/LLMs don't see
it). Three gates wired into .githooks/pre-commit + `make check`:
1. check-index — scripts/sppf_node_index.py --check keeps scratch/sppf_collision_index.md
   current (the visible name→shape map: 13 genuine-ambiguity names with per-member
   shape descriptors + ⟦hash⟧; 4 variants).
2. check-import — scripts/check_import_shape.py is a RATCHET (BASELINE=90): no NEW
   bare imports of genuinely-ambiguous names (must `renaming (Name to Name⟦shape⟧)`);
   90 existing (Linear 31/Axis 16/Action 11/Wedge 11/Section 7/…; ~half variants);
   excludes ⊤/⊥/⊤₁ (level-poly). Lower BASELINE as fixed.
3. check-decltag — scripts/decl_shape_tag.py tags every genuinely-ambiguous decl
   with a compile-safe `-- ⟦shape:HASH heads⟧` (25 decls/11 names); --fix/--check.
GOTCHA fixed: the tag comment added trailing whitespace to the decl line, which
(after comment-strip) perturbed the shape-hash → circularity. Fixed by
whitespace-normalising the hash (`" ".join(b.split())`) consistently across all
three tools. Genuine-ambiguity = name in >1 module with >1 distinct shape-hash.
