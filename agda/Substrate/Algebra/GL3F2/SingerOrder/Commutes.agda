------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.SingerOrder.Commutes
--
-- singer-commutes : the Singer linear map commutes with point-to-vec,
--   apply singer-Linear (point-to-vec p) ≡ point-to-vec (singer p)
-- for every Fano Point p.
--
-- Basis points (e₁,e₂,e₃ = basis 0,1,2): the sealed-safe basis lemma
-- apply-linear-from-images-basis gives apply L (basis i) ≡ singer-basis i,
-- and singer-basis i is definitionally point-to-vec (singer eᵢ). Compound
-- points: point-to-vec is a +ⱽ of basis points, so additivity
-- (preserves-+) reduces them to the basis cases. Never reduces the dense
-- apply on a general vector — robust under the linear-from-images seal.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.SingerOrder.Commutes where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; trans)

open import Substrate.Algebra.F2.Vector using (Vector; basis; _+ⱽ_)
open import Substrate.Algebra.F2.Linear using (apply; preserves-+)
open import Substrate.Algebra.F2.Linear.FromImages
  using (apply-linear-from-images-basis)
open import Substrate.Algebra.F2.FanoPlane
  using (Point; e₁; e₂; e₃; e₁₂; e₁₃; e₂₃; e₁₂₃;
         point-to-vec; singer; singer-basis; singer-Linear)

-- +ⱽ is a congruence, used to recombine summands.
cong₂-+ⱽ : ∀ {a b c d : Vector 3} → a ≡ c → b ≡ d → (a +ⱽ b) ≡ (c +ⱽ d)
cong₂-+ⱽ refl refl = refl

-- Basis points, standalone so the compound cases reference them WITHOUT
-- self-recursion (Point has no structural descent; a self-recursive
-- singer-commutes would not pass the termination checker).
sc-e₁ : apply singer-Linear (point-to-vec e₁) ≡ point-to-vec (singer e₁)
sc-e₁ = apply-linear-from-images-basis singer-basis zero
sc-e₂ : apply singer-Linear (point-to-vec e₂) ≡ point-to-vec (singer e₂)
sc-e₂ = apply-linear-from-images-basis singer-basis (suc zero)
sc-e₃ : apply singer-Linear (point-to-vec e₃) ≡ point-to-vec (singer e₃)
sc-e₃ = apply-linear-from-images-basis singer-basis (suc (suc zero))

-- e₂₃ split (needed by e₁₂₃); standalone for the same reason.
sc-e₂₃ : apply singer-Linear (point-to-vec e₂₃) ≡ point-to-vec (singer e₂₃)
sc-e₂₃ =
  trans (preserves-+ singer-Linear (basis (suc zero)) (basis (suc (suc zero))))
        (cong₂-+ⱽ sc-e₂ sc-e₃)

singer-commutes : (p : Point) →
  apply singer-Linear (point-to-vec p) ≡ point-to-vec (singer p)
singer-commutes e₁  = sc-e₁
singer-commutes e₂  = sc-e₂
singer-commutes e₃  = sc-e₃
singer-commutes e₂₃ = sc-e₂₃
singer-commutes e₁₂ =
  trans (preserves-+ singer-Linear (basis zero) (basis (suc zero)))
        (cong₂-+ⱽ sc-e₁ sc-e₂)
singer-commutes e₁₃ =
  trans (preserves-+ singer-Linear (basis zero) (basis (suc (suc zero))))
        (cong₂-+ⱽ sc-e₁ sc-e₃)
singer-commutes e₁₂₃ =
  trans (preserves-+ singer-Linear (basis zero)
                     (basis (suc zero) +ⱽ basis (suc (suc zero))))
        (cong₂-+ⱽ sc-e₁ sc-e₂₃)
