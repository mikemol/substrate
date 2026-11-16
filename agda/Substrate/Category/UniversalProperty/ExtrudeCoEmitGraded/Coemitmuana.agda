------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuana
--
-- Defines: coemit-mu-ana
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuana where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitout
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-mu-ana + coemit-mu-initial + coemit-colim-bridge-bisim: the finality/anamorphism, the initial-algebra
-- dual, and the bridge lifted to ~ (338's continuations). Final: ana : Coalg S → S → RealTrace (the unfold);
-- ana-unique : any coalgebra morphism into RealTrace is ~ ana (finality). into (n , x) = cons n x (Lambek's algebra).
------------------------------------------------------------------------

-- (1) coemit-mu-ana: the unique coalgebra morphism into RealTrace from coemit-out (the F-coalgebra). ana coemit-out
--     is THE terminal-coalgebra map; ana-unique makes it unique — the finality clause on the μ-object's structure.
coemit-mu-ana : RealTrace → RealTrace
coemit-mu-ana = ana coemit-out
