------------------------------------------------------------------------
-- Substrate.Category.BeckChevalley.Horizontal
--
-- Horizontal pasting of Beck-Chevalley squares: two BC squares
-- sharing a vertical edge (= the right of one matches the left of
-- the other) compose to a single BC square.
--
-- Square 1:                 Square 2:                Pasted:
--      f1                        f2                       f2∘f1
--  A1 ───> B1               A2 ───> B2               A1 ─────> B2
--  │        │               │        │               │           │
-- g1│       │h1            g2│       │h2           g1│         h2│
--  v        v               v        v               v           v
--  C1 ───> D1               C2 ───> D2               C1 ─────> D2
--      k1                        k2                       k2∘k1
--
-- Sharing requirement: B1 = A2, D1 = C2, h1 = g2.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.BeckChevalley.Horizontal where

open import Level using (Level)
open import Substrate.Foundation.Eq
  using (_≡_; trans; cong)

open import Substrate.Category.BeckChevalley using (BCSquare; cell)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- Horizontal pasting.
--
-- Given:
--   Square 1: BCSquare f1 g1 h1 k1 over (A1, B1, C1, D1)
--   Square 2: BCSquare f2 h1 h2 k2 over (B1, B2, D1, D2)
-- (note: square 2's LEFT edge (g2 in BCSquare notation) IS square 1's
-- RIGHT edge (h1); we name the parameter h1 for clarity)
--
-- Produces:
--   Pasted: BCSquare (f2 ∘ f1) g1 h2 (k2 ∘ k1)
--           over (A1, B2, C1, D2)
--
-- Cell proof chain:
--   h2 (f2 (f1 a))
--     ≡ k2 (h1 (f1 a))      [cell sq2 (f1 a)]
--     ≡ k2 (k1 (g1 a))       [cong k2 (cell sq1 a)]
------------------------------------------------------------------------

horizontal-paste :
  {A1 B1 C1 D1 B2 D2 : Set ℓ}
  {f1 : A1 → B1}
  {g1 : A1 → C1}
  {h1 : B1 → D1}
  {k1 : C1 → D1}
  {f2 : B1 → B2}
  {h2 : B2 → D2}
  {k2 : D1 → D2} →
  BCSquare f1 g1 h1 k1 →
  BCSquare f2 h1 h2 k2 →
  BCSquare (λ a → f2 (f1 a)) g1 h2 (λ c → k2 (k1 c))
horizontal-paste {f1 = f1} {g1 = g1} {h1 = h1} {k1 = k1}
                 {f2 = f2} {h2 = h2} {k2 = k2}
                 sq1 sq2 = record
  { cell = λ a →
      trans (cell sq2 (f1 a))
            (cong k2 (cell sq1 a))
  }

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: BC squares can compose horizontally too. Combined
-- with vertical pasting (sibling Compose module), the substrate has
-- the full 2-cell-calculus operations for BC squares.
--
-- The two pastings (vertical + horizontal) are the foundational
-- operations of the 2-category of BC squares. Higher operations
-- (associators, interchange laws, etc.) follow but are deferred.
------------------------------------------------------------------------
