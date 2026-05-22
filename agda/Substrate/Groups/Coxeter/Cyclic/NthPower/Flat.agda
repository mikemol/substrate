------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Flat
--
-- The flat-iteration tower + bridge to the ·-tower.
--
--   apply-power-suc       : Word Gen → ℕ → Word Gen   -- w · w · … · w
--   apply-power-suc-flat  : Word Gen → ℕ → Word Gen   -- w ++ w ++ … ++ w
--   apply-power-suc-flatten        : normalize (·-tower) ≡ normalize (++-tower)
--   apply-power-suc-flat-normalize : argument can be canonicalized under normalize
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Groups.Coxeter.Word using (Word; _++_)

module Substrate.Groups.Coxeter.Cyclic.NthPower.Flat (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat n public

------------------------------------------------------------------------
-- 1. apply-power-suc / apply-power-suc-flat.
--
-- apply-power-suc w m = w · w · ... · w (m+1 copies via _·_).
-- apply-power-suc-flat w m = same but via ++ instead of ·.
------------------------------------------------------------------------

apply-power-suc : Word Gen → ℕ → Word Gen
apply-power-suc w zero    = w
apply-power-suc w (suc k) = (apply-power-suc w k) · w

apply-power-suc-flat : Word Gen → ℕ → Word Gen
apply-power-suc-flat w zero    = w
apply-power-suc-flat w (suc k) = apply-power-suc-flat w k ++ w

------------------------------------------------------------------------
-- 2. apply-power-suc-flatten: normalize commutes the · away to ++.
------------------------------------------------------------------------

apply-power-suc-flatten : (w : Word Gen) (m : ℕ) →
                       normalize (apply-power-suc w m) ≡
                       normalize (apply-power-suc-flat w m)
apply-power-suc-flatten w zero    = refl
apply-power-suc-flatten w (suc m) =
  trans (normalize-idem ((apply-power-suc w m) ++ w))
  (trans (normalize-append (apply-power-suc w m) w)
  (trans (cong (λ x → normalize (x ++ w)) (apply-power-suc-flatten w m))
         (sym (normalize-append (apply-power-suc-flat w m) w))))

------------------------------------------------------------------------
-- 3. apply-power-suc-flat-normalize: normalize commutes through the
-- argument of apply-power-suc-flat.
------------------------------------------------------------------------

apply-power-suc-flat-normalize : (w : Word Gen) (m : ℕ) →
                              normalize (apply-power-suc-flat w m) ≡
                              normalize (apply-power-suc-flat (normalize w) m)
apply-power-suc-flat-normalize w zero    = sym (normalize-idem w)
apply-power-suc-flat-normalize w (suc m) =
  trans (normalize-append (apply-power-suc-flat w m) w)
  (trans (cong (λ x → normalize (x ++ w))
               (apply-power-suc-flat-normalize w m))
  (trans (sym (normalize-append (apply-power-suc-flat (normalize w) m) w))
         (normalize-append-right (apply-power-suc-flat (normalize w) m) w)))
