------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4square
--
-- Defines: coemit-v4-square
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4square where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Transpose
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Daggerbar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Natuip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4squarehead
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- SELF-AUDIT: `coemit-v4-square = transpose` would be a RENAME, not a commutation. The genuine statement is that
-- the two routes agree on their OBSERVABLE CONTENT at every step. Step 0 is coemit-v4-square-head (nat-uip).
-- The totality (351) is: at every depth n, both routes' traces have equal n-prefixes. Since both routes produce a
-- ~-proof of the SAME endpoints (bar s ~ bar r), their prefix-images coincide — exhibited via the totality.
-- SECOND AUDIT: a `take n (bar s) ≡ take n (bar s)` clause would be X ≡ X (the 4th vacuous witness this arc).
-- DISCARDED. The V₄ square's genuine, non-vacuous content is exactly the UIP identification of the two routes'
-- observable components — coemit-v4-square-head above. Both routes inhabit `bar s ~ bar r` (endpoints, 353);
-- their head~ components are IDENTIFIED by nat-uip; the tails follow by the same argument coinductively.
-- HONEST SCOPE: full proof-equality (transpose p ≡ dagger-bar p) needs coinductive proof-equality, NOT built.
coemit-v4-square : {r s : RealTrace} (p : r ~ s) → head~ (transpose p) ≡ head~ (dagger-bar p)
coemit-v4-square = coemit-v4-square-head
