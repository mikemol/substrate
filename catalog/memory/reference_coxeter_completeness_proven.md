---
name: reference_coxeter_completeness_proven
description: "coxeter-completeness (every Perm n is a word in adjacent transpositions, ∀n) is PROVEN & committed (9dcdbb7) — NOT an open gap; stop re-flagging it"
metadata:
  node_type: memory
  type: reference
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

The general ∀n **Coxeter-completeness** theorem — every `Perm n` is a word in adjacent transpositions —
IS PROVEN, committed `9dcdbb7` (2026-07-11), `--safe --without-K`, zero holes/postulates:

  `coxeter-complete : {n} (σ : Perm n) → IsPerm σ → CoxGen σ`
  in `agda/Substrate/WitnessTower/Wedge/OrientationRigCatPermCoxeterGeneral/Properties.agda:220`
  (via `decode-CoxGen`: `insert-at` IS a bubble-run of adjacent transpositions, `idInsert-step`).

Consumed downstream by `OrientationRigCatSymUP`, `OrientationRigCatPermSign`, `PyAstRewrite`.

**Why this memory:** the header comments in `OrientationRigCatPermBifunctor.agda` /
`OrientationRigCatPermAdjClosure.agda` (and the plan file `radiant-weaving-dawn.md` "Honest boundaries" +
REGROUNDING #10) called it "NOT yet in the tree / unproven" — those were committed ONE commit before the
theorem landed and were STALE (corrected 2026-07-13). So "residue = an adjacent-transposition/braiding word"
is a PROVEN reading, not a labelled construction. `graded_orbit.to_coxeter_word` realizes the word concretely
(round-trip-verified). This is a [[reuse-search-before-feasibility-conclusions]] instance: a deferral/TODO
comment is a hypothesis to verify (search the witness tower), not a fact — it was already proven.
Relates to [[adjunction-is-the-wedge-residue-counit]], [[wedge-projection]], [[substrate-groups-coxeter]].
