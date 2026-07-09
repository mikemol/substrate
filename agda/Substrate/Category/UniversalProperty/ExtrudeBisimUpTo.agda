{-# OPTIONS --safe --without-K --guardedness #-}
------------------------------------------------------------------------
-- ExtrudeBisimUpTo — the general ~-COINDUCTION-UP-TO principle (extracting the mix trick, ADD 321). A relation R
-- is a bisimulation-up-to-~ if R x y gives head-agreement and a tail related up to ~ (∃ z, tail x ~ z × R z (tail
-- y)). Then R ⊆ ~. Proven by the GO-THREADING (mix generalized): thread x ~ w as a DATA argument, the corecursive
-- call sits guarded under tail~, the ~-trans lives in its argument (D-mix-trick / D-guarded-not-mutual). Reusable
-- ~-level uniqueness that lets up-to-~ morphisms (Lambek, reassociation) through.
------------------------------------------------------------------------
module Substrate.Category.UniversalProperty.ExtrudeBisimUpTo where

open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl; ~-trans)
open import Substrate.Foundation.Eq using (_≡_) renaming (trans to ≡-trans)
open import Substrate.Foundation.Product using (Σ; _×_; _,_; proj₁; proj₂)

module _ (R : RealTrace → RealTrace → Set)
         (head-cond : {x y : RealTrace} → R x y → head x ≡ head y)
         (tail-cond : {x y : RealTrace} → R x y → Σ RealTrace (λ z → (tail x ~ z) × R z (tail y))) where

  -- go threads (x ~ w) as data; the corecursive call is guarded under tail~, the ~-trans is in its argument.
  go : {x y : RealTrace} → Σ RealTrace (λ w → (x ~ w) × R w y) → x ~ y
  head~ (go (w , x~w , Rwy)) = ≡-trans (head~ x~w) (head-cond Rwy)
  tail~ (go {x} {y} (w , x~w , Rwy)) with tail-cond Rwy
  ... | (z , tw~z , Rz-ty) = go (z , ~-trans (tail~ x~w) tw~z , Rz-ty)

  -- the principle: any bisimulation-up-to-~ is contained in ~.
  ~-coind-up-to : {x y : RealTrace} → R x y → x ~ y
  ~-coind-up-to {x} Rxy = go (x , ~-refl x , Rxy)
