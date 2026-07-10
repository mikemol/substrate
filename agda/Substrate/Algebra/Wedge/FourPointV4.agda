------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.FourPointV4
--
-- THE FOUR POINTS OF A WEDGE CARRY A V₄ — FOR FREE.
--
-- A wedge operation `a = recon q b r` has four points on it: a, q, b, r.
-- V₄ = ℤ/2 × ℤ/2, so it is not DERIVED from the wedge — it is the product of
-- two ℤ/2's, and the four points ARE that product (a 2×2 arrangement). Take the
-- four points as module parameters and the V₄ is constructed for you, for any
-- arrangement: the two ℤ/2's are the two axis-swaps of the 2×2 (rowSwap,
-- colSwap), they commute (the V₄-not-dihedral condition), and their composite
-- (the 180° Klein rotation) is the third involution — {id, row, col, rot} = V₄.
--
-- This is exactly Wedge.StarV4's arrangement-V₄ (rowSwap/colSwap/klein-rot),
-- freed from the *-involution gate: those swaps never touch `conj`; they are the
-- symmetry of the ARRANGEMENT, no multiplication needed (StarV4's own words). The
-- V₄ packaging is Category.Lawvere.CommutingInvolutions (two commuting
-- involutions ⇒ Klein four, δ₁₂-inv proven there).
--
-- The four V₄ elements ARE the group actions for rewriting any wedge: relabel the
-- four points by the arrangement symmetry.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.FourPointV4 where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Category.Lawvere using (CommutingInvolutions)

------------------------------------------------------------------------
-- 1. The four points, as a 2×2 arrangement over any carrier C.
------------------------------------------------------------------------

module _ {C : Set} where

  -- a 2×2 square of four points ((a , b) , (c , d)) — the shape a wedge's
  -- four points inhabit.
  Square : Set
  Square = (C × C) × (C × C)

  -- pass the four points in; get the arrangement.
  arrange : C → C → C → C → Square
  arrange a b c d = ((a , b) , (c , d))

  ------------------------------------------------------------------------
  -- 2. The two ℤ/2's — the axis-swaps of the arrangement. Pure permutations,
  --    no arithmetic, no conjugation. (= StarV4.rowSwap / StarV4.colSwap.)
  ------------------------------------------------------------------------

  rowSwap : Square → Square          -- ℤ/2 #1: swap the two rows
  rowSwap (r₁ , r₂) = (r₂ , r₁)

  colSwap : Square → Square          -- ℤ/2 #2: swap within each row (the columns)
  colSwap ((a , b) , (c , d)) = ((b , a) , (d , c))

  rowSwap-inv : (s : Square) → rowSwap (rowSwap s) ≡ s
  rowSwap-inv (r₁ , r₂) = refl

  colSwap-inv : (s : Square) → colSwap (colSwap s) ≡ s
  colSwap-inv ((a , b) , (c , d)) = refl

  -- THE V₄ CONDITION: the two ℤ/2's COMMUTE (abelian ⇒ Klein four, not dihedral).
  row-col-commute : (s : Square) → colSwap (rowSwap s) ≡ rowSwap (colSwap s)
  row-col-commute ((a , b) , (c , d)) = refl

  ------------------------------------------------------------------------
  -- 3. V₄ FOR FREE: package the two commuting involutions. CommutingInvolutions
  --    derives the composite δ₁₂ (the 180° Klein rotation) and proves it is an
  --    involution — so {id, rowSwap, colSwap, δ₁₂} closes to Klein four.
  ------------------------------------------------------------------------

  square-V4 : CommutingInvolutions Square
  square-V4 = record
    { δ₁      = rowSwap
    ; δ₂      = colSwap
    ; δ₁-inv  = rowSwap-inv
    ; δ₂-inv  = colSwap-inv
    ; commute = row-col-commute
    }

  -- the third involution, exposed: the Klein rotation (rowSwap ∘ colSwap) = the
  -- 180° turn (the diagonal double-transposition), an involution by construction.
  klein-rot : Square → Square
  klein-rot = CommutingInvolutions.δ₁₂ square-V4

  klein-rot-inv : (s : Square) → klein-rot (klein-rot s) ≡ s
  klein-rot-inv = CommutingInvolutions.δ₁₂-inv square-V4

------------------------------------------------------------------------
-- 4. The four wedge points, as a parameterized instance. Passing a, q, b, r
--    (any arrangement) yields their V₄ — the four rewrite actions on the wedge.
------------------------------------------------------------------------

module _ {C : Set} (a q b r : C) where

  -- arrange the four points of `a = recon q b r`: the factors (q , b) over the
  -- endpoints (a , r).
  wedge-square : Square
  wedge-square = arrange q b a r

  -- the four rewrites of this wedge = the V₄ orbit of its arrangement.
  rewrite-id  rewrite-row  rewrite-col  rewrite-rot : Square
  rewrite-id  = wedge-square
  rewrite-row = rowSwap wedge-square              -- (q b)(a r): factors ↕ endpoints
  rewrite-col = colSwap wedge-square              -- swap within each pair
  rewrite-rot = klein-rot wedge-square            -- the 180° turn (the diagonal)
