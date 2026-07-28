------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4identityisadditiveorigin
--
-- Defines: coemit-v4-identity-is-additive-origin
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4identityisadditiveorigin where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul


------------------------------------------------------------------------
-- THE CODEC (operator: "a zero is an identity in the ADDITIVE domain; a 1 is an identity in the MULTIPLICATIVE
-- domain; we have codecs for this"). CORRECTS 347's D-role-not-identity, which treated identity-vs-zero as a
-- difference of NOTION when it is a difference of DOMAIN. Substrate.Algebra.ExpLogCodec:
--   record ExpLogCodec (_·_ : G→G→G) (𝟙 : G) (_≈_) : { L ; _⊕_ ; 𝟘 ; expL : L → G ;
--     exp-⊕ : expL (a ⊕ b) ≈ expL a · expL b ;  exp-𝟘 : expL 𝟘 ≈ 𝟙 }
-- — the ADDITIVE origin 𝟘 maps to the MULTIPLICATIVE identity 𝟙. That IS the operator's statement, canonically.
--
-- >>> WHERE IT APPLIES (verified): V₄'s own product IS F₂-addition. From V4FullCocycle:
-- >>>   (v4 a b) · (v4 c d) = v4 (a ⊕ c) (b ⊕ d)   and   e = v4 𝟘 𝟘
-- >>> So V₄ is an ADDITIVE group (F₂ × F₂) written MULTIPLICATIVELY: its identity e IS the additive origin (𝟘,𝟘).
-- >>> Hence D ↦ e ↦ (𝟘,𝟘): the anchor is an identity BECAUSE zero is the identity of the additive domain.
--
-- >>> WHERE IT DOES NOT APPLY (verified, honest): coemit's carrier. trace-mul has head ≡ 0 CONSTANTLY, so
-- >>> trace-mul zero-trace r has head 0 even when head r ≠ 0 ⇒ zero-trace is NOT a ⊕-origin for trace-mul; it is a
-- >>> strict ABSORBER (trace-mul r s ~ zero-trace for ALL r s). An absorber is not an identity in EITHER domain.
-- >>> ⇒ The codec relates the GRADING (V₄, additive-in-F₂) to its multiplicative presentation. It does NOT rescue
-- >>> a μ→D map on the CARRIER. 347's conclusion stands; its REASON was wrong (domain, not notion) — and the
-- >>> corrected reason SHARPENS ⟡coemit-torsor-audit: the V₄/S₄ symmetry lives on the GRADING, not the carrier.
------------------------------------------------------------------------
-- V₄'s identity is the additive origin: e = v4 𝟘 𝟘 (the F₂×F₂ zero) — "zero is the identity of the additive domain".
coemit-v4-identity-is-additive-origin : V4.e ≡ V4.v4 𝟘 𝟘
coemit-v4-identity-is-additive-origin = refl
