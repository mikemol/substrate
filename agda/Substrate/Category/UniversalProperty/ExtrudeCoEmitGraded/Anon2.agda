------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
--
-- Defines: Anon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2 where

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
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon


------------------------------------------------------------------------
-- coemit-nu-via-general: re-derive the ~-conditioned uniqueness FROM the general ~-coind-up-to (ExtrudeBisimUpTo,
-- 322), retiring the bespoke mix (D-both-proven-equivalent: both give h c ~ coemit-trace c). The relation
-- R x y = Σ c, (x ~ h c) × (y ≡ coemit-trace c); head/tail conditions discharge via head~/hh and ~-trans/ht.
------------------------------------------------------------------------

module _ (h : CoEmit ℕ → RealTrace)
         (hh : (c : CoEmit ℕ) → RealTrace.head (h c) ≡ proj₁ (coemit-coalg c))
         (ht : (c : CoEmit ℕ) → RealTrace.tail (h c) ~ h (proj₂ (coemit-coalg c))) where

  Rrel : RealTrace → RealTrace → Set
  Rrel x y = Σ (CoEmit ℕ) (λ c → (x ~ h c) × (y ≡ coemit-trace c))

  Rrel-head : {x y : RealTrace} → Rrel x y → RealTrace.head x ≡ RealTrace.head y
  Rrel-head (c , x~hc , y≡ct) = ≡tr (≡tr (bhead~ x~hc) (hh c)) (sym (cong RealTrace.head y≡ct))

  Rrel-tail : {x y : RealTrace} → Rrel x y → Σ RealTrace (λ z → (RealTrace.tail x ~ z) × Rrel z (RealTrace.tail y))
  Rrel-tail (c , x~hc , y≡ct) =
    h (proj₂ (coemit-coalg c))
    , ~-trans (btail~ x~hc) (ht c)
    , (proj₂ (coemit-coalg c) , ~-refl (h (proj₂ (coemit-coalg c))) , cong RealTrace.tail y≡ct)

  coemit-trace-unique-~-via : (c : CoEmit ℕ) → h c ~ coemit-trace c
  coemit-trace-unique-~-via c =
    ~-coind-up-to Rrel Rrel-head Rrel-tail (c , ~-refl (h c) , refl)
