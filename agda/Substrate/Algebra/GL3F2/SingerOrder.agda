------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.SingerOrder
--
-- HasOrder-singer : the Sylow-7 generator singer-Linear has order 7 as
-- a linear endomap of Vector 3.
--
-- STRUCTURAL PROOF (the Point-bridge — pays down the tech debt the
-- previous enumeration version flagged as "to land in a follow-on slice
-- if needed"). The earlier version proved order-7 by `refl` on the 8
-- concrete vectors, silently banking TRANSPARENT REDUCTION through
-- singer-Linear = linear-from-images singer-basis. When linear-from-
-- images was sealed `opaque` (the dense-matrix OOM fix), that reduction
-- vanished and the refls broke. This version never reduces the dense
-- apply on a general vector; it routes through:
--
--   * apply-linear-from-images-basis  (sealed-safe: apply L (basis i) ≡
--                                       singer-basis i),
--   * preserves-+                      (apply is additive),
--   * the Fano Point 7-cycle singer⁷-id (singer⁷ p ≡ p),
--   * linear-extensionality           (lift basis-vector agreement to
--                                       all vectors — basis-only, never
--                                       touches the dense form).
--
-- So order-7 follows from the COMBINATORICS of the 7-cycle on Points,
-- not the evaluator grinding a 7-fold dense matrix power. Robust under
-- the opacity boundary.
--
-- Per [[expose-generator-not-orbit]] / [[multi-route-equivariance-
-- recovery]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.SingerOrder where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector; basis; _+ⱽ_)
open import Substrate.Algebra.F2.Linear using (Linear; apply; preserves-+)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.FanoPlane
  using (Point; e₁; e₂; e₃; e₁₂; e₁₃; e₂₃; e₁₂₃;
         point-to-vec; singer; singer⁷; singer⁷-id;
         singer-basis; singer-Linear)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; HasOrder)

------------------------------------------------------------------------
-- 1. The Singer action commutes with point-to-vec.
--
--   apply singer-Linear (point-to-vec p) ≡ point-to-vec (singer p)
--
-- Basis points (e₁,e₂,e₃ = basis 0,1,2): the sealed-safe basis lemma
-- gives apply singer-Linear (basis i) ≡ singer-basis i, and singer-basis
-- i is definitionally point-to-vec (singer eᵢ) (both are the same
-- concrete F₂ vector). Compound points: point-to-vec is a +ⱽ of basis
-- points, so additivity (preserves-+) reduces to the basis cases.
------------------------------------------------------------------------

-- helper: +ⱽ is a congruence, used to recombine summands.
cong₂-+ⱽ : ∀ {a b c d : Vector 3} → a ≡ c → b ≡ d → (a +ⱽ b) ≡ (c +ⱽ d)
cong₂-+ⱽ refl refl = refl

-- basis points, via the sealed-safe basis lemma (singer-basis i is the
-- concrete image vector = point-to-vec (singer eᵢ)). Standalone so the
-- compound cases reference them WITHOUT self-recursion (Point has no
-- structural descent; a self-recursive singer-commutes would not pass
-- the termination checker).
sc-e₁ : apply singer-Linear (point-to-vec e₁) ≡ point-to-vec (singer e₁)
sc-e₁ = apply-linear-from-images-basis singer-basis zero
sc-e₂ : apply singer-Linear (point-to-vec e₂) ≡ point-to-vec (singer e₂)
sc-e₂ = apply-linear-from-images-basis singer-basis (suc zero)
sc-e₃ : apply singer-Linear (point-to-vec e₃) ≡ point-to-vec (singer e₃)
sc-e₃ = apply-linear-from-images-basis singer-basis (suc (suc zero))

-- e₂₃ split (needed by e₁₂₃); also standalone.
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
-- compound points: additivity (preserves-+) splits apply over the +ⱽ of
-- basis vectors; each summand is a standalone basis case above.
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

------------------------------------------------------------------------
-- 2. Iterating the commutation k times tracks singer^k on the Point.
--
--   iterate k (apply singer-Linear) (point-to-vec p)
--     ≡ point-to-vec (singer^k p)
------------------------------------------------------------------------

singer^ : ℕ → Point → Point
singer^ zero    p = p
singer^ (suc k) p = singer (singer^ k p)

iterate-commutes : (k : ℕ) (p : Point) →
  iterate k (apply singer-Linear) (point-to-vec p)
    ≡ point-to-vec (singer^ k p)
iterate-commutes zero    p = refl
iterate-commutes (suc k) p =
  trans (cong (apply singer-Linear) (iterate-commutes k p))
        (singer-commutes (singer^ k p))

-- singer^ 7 = singer⁷ (pointwise; both are 7-fold singer).
singer^7≡singer⁷ : (p : Point) → singer^ 7 p ≡ singer⁷ p
singer^7≡singer⁷ p = refl

------------------------------------------------------------------------
-- 3. Order-7 on the three basis vectors (= basis points), via the
--    Point 7-cycle. No dense reduction.
------------------------------------------------------------------------

basis-point : Fin 3 → Point
basis-point zero          = e₁
basis-point (suc zero)    = e₂
basis-point (suc (suc _)) = e₃

basis≡point-to-vec : (i : Fin 3) → basis i ≡ point-to-vec (basis-point i)
basis≡point-to-vec zero             = refl
basis≡point-to-vec (suc zero)       = refl
basis≡point-to-vec (suc (suc zero)) = refl
basis≡point-to-vec (suc (suc (suc ())))

order-on-basis : (i : Fin 3) →
  iterate 7 (apply singer-Linear) (basis i) ≡ basis i
order-on-basis i =
  trans (cong (iterate 7 (apply singer-Linear)) (basis≡point-to-vec i))
  (trans (iterate-commutes 7 (basis-point i))
  (trans (cong point-to-vec (singer⁷-id (basis-point i)))
         (sym (basis≡point-to-vec i))))

------------------------------------------------------------------------
-- 4. HasOrder-singer: lift the basis-vector agreement to ALL vectors
--    via linear-extensionality (basis-only; never reduces the dense
--    apply on a general vector — robust under the opacity seal).
------------------------------------------------------------------------

open import Substrate.Algebra.F2.Linear using (id-L)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order
  using (L-iterate; iterate-apply-as-L-iterate)

HasOrder-singer : HasOrder (apply singer-Linear) 7
HasOrder-singer v =
  trans (iterate-apply-as-L-iterate singer-Linear 7 v)
        (linear-extensionality
          (L-iterate 7 singer-Linear) id-L
          (λ i → trans (sym (iterate-apply-as-L-iterate singer-Linear 7 (basis i)))
                       (order-on-basis i))
          v)
