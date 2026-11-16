---
name: feedback_exists-unique_is_a_construction_not_a_sigma
description: "A 'there exists a unique X' (∃!) is a CONSTRUCTION not yet searched for — do NOT Σ-package it. Search (numpy/mechanically) for the explicit construction, EXPOSE it (like fold), then a separate uniqueness lemma. Σ/∃ is the same collapse the mission fights."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (the graded-rig-CATEGORY UP). Building the functor universal property, I specced it
as `Σ (F : RigFunctor free T) (uniqueness)` — an ∃!-existential. The user: *"You might benefit from
having numpy do the search for you? I see you fell back to using Σ."* Both halves land: (1) the Σ is a
COLLAPSE — the exact anti-pattern the arc spent 6 dissolutions eliminating (Σ ℕ C = grade-collapse),
now reappearing as ∃-collapse; (2) I reached for Σ because I ANALYSED ("there exists a functor")
instead of SEARCHING for the explicit construction. numpy (which had discovered every other
construction this session) settled it in one script: objects = grade-fold of the generator, morphisms
= braiding-word (every perm is a braiding-word), so the functor is DETERMINED by F(generator) — a
CONSTRUCTION, not an existential.

**Why:** every universal property in this arc EXPOSES its construction — `fold`, `foldF` (foldF-free-
unique), `foldR` — as `theMap : … → Target` + a separate `unique : g respects-structure → g ≡ theMap`.
NONE use Σ/∃. A `Σ (X) uniqueness` HOLDS the construction as an opaque existential instead of BUILDING
it. That is the same "collapse a rich thing into a thin proxy" as the grade-collapse (Σ ℕ C) and even
as reporting-a-commit-by-exit-code ([[feedback_verify_commit_landed_not_exit_code]]) — one invariant:
EXPOSE, DON'T COLLAPSE.

**How to apply:** when you're about to write `Σ`/`∃`/`∃!` for "there is a (unique) map/object with
property P" — STOP. That is a construction you haven't found yet. SEARCH for it (numpy: is it
determined by the generators? is it a fold/word-image?), then EXPOSE it as a named construction +
prove uniqueness as a separate lemma (mirror foldF-free-unique). Reserve Σ for genuine data-pairing
(a dependent pair you actually carry), never for packaging an existence-uniqueness claim whose witness
is canonical. The tell: any `Σ (f : Hom/Functor/Map …) (λ f → … unique …)` — the witness is a fold,
build it. Sibling of [[set1-is-grade-collapse]] and [[center-free-universal-property]] /
[[feedback_categorical_superlative_needs_universal_property]] (a UP is a construction + uniqueness).
