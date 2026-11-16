------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4embed
--
-- Defines: coemit-s4-embed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4embed where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitS4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisv4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- (2) coemit-s4-full-group: the canonical S₄ = V₄ ⋊ S₃ (Groups.S4-Composed.S₄-Group) IS the coemit braiding's group.
--     coemit's (axis,perm) pairs embed into it via axis→v4 × the S₃ component — the full group is the CANONICAL one
--     (D-graded-is-canonical: don't rebuild it). The SemidirectGroupObligation is discharged THERE, not here.
coemit-s4-embed : CoemitS4 → Σ V₄ (λ _ → (Fin 3 → Fin 3))
coemit-s4-embed (a , σ) = axis→v4 a , σ
