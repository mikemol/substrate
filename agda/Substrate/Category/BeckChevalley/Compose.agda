------------------------------------------------------------------------
-- Substrate.Category.BeckChevalley.Compose
--
-- Vertical pasting of Beck-Chevalley squares: two BC squares sharing
-- a horizontal edge (= the bottom of one matches the top of the
-- other) compose to a single BC square.
--
-- Square 1:                Square 2:               Pasted:
--      f1                       f2                       f1
--  A1 ───> B1               A2 ───> B2              A1 ────> B1
--  │        │               │        │              │         │
-- g1│       │h1            g2│       │h2          g2∘g1     h2∘h1
--  v        v               v        v              v         v
--  C1 ───> D1               C2 ───> D2              C2 ────> D2
--      k1                       k2                       k2
--
-- Sharing requirement: C1 = A2, D1 = B2, k1 = f2.
--
-- Per [[project-3plus1-is-cone-instance]]: BC squares compose under
-- the usual 2-categorical 2-cell calculus. This module names the
-- vertical pasting; horizontal pasting is the sibling module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.BeckChevalley.Compose where

open import Level using (Level)
open import Relation.Binary.PropositionalEquality
  using (_≡_; trans; cong)

open import Substrate.Category.BeckChevalley using (BCSquare; bc-trivial; cell)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- Vertical pasting.
--
-- Given:
--   Square 1: BCSquare f1 g1 h1 k1 over (A1, B1, C1, D1)
--   Square 2: BCSquare k1 g2 h2 k2 over (C1, D1, C2, D2)
-- (note: square 2's top edge IS square 1's bottom k1)
--
-- Produces:
--   Pasted: BCSquare f1 (g2 ∘ g1) (h2 ∘ h1) k2
--           over (A1, B1, C2, D2)
--
-- Cell proof chain:
--   h2 (h1 (f1 a))
--     ≡ h2 (k1 (g1 a))       [cong h2 (cell square-1 a)]
--     ≡ k2 (g2 (g1 a))       [cell square-2 (g1 a)]
------------------------------------------------------------------------

vertical-paste :
  {A1 B1 C1 D1 C2 D2 : Set ℓ}
  {f1 : A1 → B1}
  {g1 : A1 → C1}
  {h1 : B1 → D1}
  {k1 : C1 → D1}
  {g2 : C1 → C2}
  {h2 : D1 → D2}
  {k2 : C2 → D2} →
  BCSquare f1 g1 h1 k1 →
  BCSquare k1 g2 h2 k2 →
  BCSquare f1 (λ a → g2 (g1 a)) (λ b → h2 (h1 b)) k2
vertical-paste {f1 = f1} {g1 = g1} {h1 = h1} {k1 = k1}
               {g2 = g2} {h2 = h2} {k2 = k2}
               sq1 sq2 = record
  { cell = λ a →
      trans (cong h2 (cell sq1 a))
            (cell sq2 (g1 a))
  }

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: BC squares can compose vertically. The pasting
-- preserves the BC structure (the resulting square is still a BC
-- square with a coherent cell).
--
-- This is the substrate's first 2-cell-calculus operation on BC
-- squares. Horizontal pasting (sibling module) handles the other
-- direction.
--
-- Per [[feedback-categorical-name-first]]: "vertical pasting" is
-- the standard 2-categorical name for this operation on 2-cells.
------------------------------------------------------------------------
