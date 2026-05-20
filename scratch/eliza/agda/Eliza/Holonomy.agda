------------------------------------------------------------------------
-- Eliza.Holonomy
--
-- The G→C→S→G round-trip 2-cell from readme-4.md §3-4, formalised as
-- a Beck-Chevalley square per `Substrate.Category.BeckChevalley`.
--
-- For each chamber x:
--   * The "direct" path:  x ───────────────────→ φ(x)         (G→S)
--   * The "via image":    x ─→ neighbours ─→ centroid(x) in φ (G→C→S)
--
-- The two paths produce two points in spectral space; the curvature κ
-- is their distance. BC condition HOLDS at x iff κ = 0; FAILS with
-- structural 2-cell otherwise. The shadow chamber ℋ(x) = arg min over
-- y of ‖φ(y) − centroid(x)‖ is the reprojection of the via-image to
-- the chamber set.
--
-- The skeleton postulates ℝ (the spectral codomain) and the metric;
-- the structural shape of the BCSquare is fully expressed.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Holonomy where

open import Eliza.Prelude   using (_≡_; ℕ)
open import Eliza.Alphabets using (Chamber; Gen; s₁; s₂; s₃)
open import Eliza.Manifold  using (apply)

------------------------------------------------------------------------
-- 1. Spectral coordinates. Postulated as an abstract codomain with
-- a norm. In Python this is ℝ² for the (Fiedler, turbulence) macro
-- embedding.
------------------------------------------------------------------------

postulate
  Spec : Set
  φ    : Chamber → Spec

  -- Pointwise averaging (the "centroid"). Postulated as an operation
  -- on triples of Specs.
  centroid₃ : Spec → Spec → Spec → Spec

------------------------------------------------------------------------
-- 2. The neighbour-centroid in spectral space.
--
--   centroid(x) = mean over g ∈ {s₁,s₂,s₃} of φ(apply g x)
--
-- The "via-image" leg of the BC square.
------------------------------------------------------------------------

centroid : Chamber → Spec
centroid x = centroid₃ (φ (apply s₁ x)) (φ (apply s₂ x)) (φ (apply s₃ x))

------------------------------------------------------------------------
-- 3. The BC-square cell at x: a witness that the direct and via-image
-- legs agree. When equal, BC condition HOLDS; the structural failure
-- when they differ IS the substrate's 3+1 parity universal expressed
-- at this level.
--
-- Per `Substrate.Category.BeckChevalley.BCSquare`, the cell is a
-- pointwise equality. Here we structurally name it.
------------------------------------------------------------------------

record BC-Cell (x : Chamber) : Set where
  field
    cell : φ x ≡ centroid x

------------------------------------------------------------------------
-- 4. The shadow chamber: the nearest chamber to centroid(x). The
-- reprojection step `∇_{S→G}` from readme-4.md, modulo nearest-
-- chamber lookup (postulated as `nearest-spec`).
------------------------------------------------------------------------

postulate
  nearest-spec : Spec → Chamber
  -- Property: nearest-spec maps `φ x` to x. Postulated.
  nearest-self : (x : Chamber) → nearest-spec (φ x) ≡ x

shadow : Chamber → Chamber
shadow x = nearest-spec (centroid x)

------------------------------------------------------------------------
-- 5. The closure / drift dichotomy. ℋ closes at x when the shadow
-- equals x itself; drifts otherwise. The Python's `holonomy.closes`
-- field is this predicate.
------------------------------------------------------------------------

ℋ-closes : Chamber → Set
ℋ-closes x = shadow x ≡ x

------------------------------------------------------------------------
-- 6. Curvature κ. Postulated as a ℕ-valued band proxy (in Python it's
-- a real number partitioned into low/mid/high). The structural fact
-- is that κ(x) = 0 iff BC-Cell holds at x.
------------------------------------------------------------------------

postulate
  κ-band : Chamber → ℕ
  -- κ-band x = 0 iff BC-Cell holds at x. Stated by the equivalence
  -- κ-band-iff-cell, deferred to a future slice.
