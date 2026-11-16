---
name: skeleton-as-pullback
description: "When agda_similarity reveals an orbit, factor out a single parametric skeleton — specializations become thin renamings/projections of its outputs."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c0656668-5986-42eb-b0c2-6df0ba57346b
---

When `scripts/agda_similarity.py` surfaces an orbit cluster — N files with
high cosine similarity at char3/token/line/block scales — the right
refactor is **not** "swap aliases" or "deduplicate boilerplate". It is:

  1. Identify the parametric core that all N files instantiate.
  2. Write that core *once* as a skeleton module (the **witness**).
  3. Re-present each specialization as a thin renaming / `open … public`
     of the skeleton applied to per-instance parameters.

**Why:** the user framed this categorically — the skeleton is *literally
the pullback* of the orbit's base. The N specializations are the
projections; one parametric witness covers all of them. This is what
makes the orbit absorption stable: future orbit members fall in as
new instantiations rather than as new files needing further
deduplication.

**How to apply:**
- When a `--score` run prints STRONG (≥0.75) or PARTIAL (0.55-0.75)
  orbit verdicts, treat that as a signal to look for the skeleton.
- For duality orbits (1:2 cone) the skeleton typically lives on
  `Opposite` — e.g. `Comonad C = Monad (Opposite C)`,
  `opposite-Functor : Functor C D → Functor (Opposite C) (Opposite D)`.
- For 1:N cones (EM/Kleisli/category-of-algebras), the skeleton is
  parametric over the per-instance choice and N adapter files become
  one-record-projection or one-record-application shims.
- The script is the *detector*; the skeleton is the *witness*; the
  thin specializations are the *projections*. All three stay in tree.
- See [[v4-coxeter-f2graded-from-homomorphism]] and
  [[category-opposite-comonad-as-monad]] for landed examples.
- See also [[file-size-one-pass-rewrite]] — skeletons that fit in one
  Write call typically also fit the rewrite discipline.
