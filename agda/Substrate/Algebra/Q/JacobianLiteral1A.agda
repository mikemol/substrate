{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianLiteral1A — the z·u³ summand of γ₁, alone.
-- γ₁A = homAgree e₁A : E (encode e₁A) ≋ evalDirect e₁A. Kept in its own module
-- so the (1+xy)³ cube's degree-9 evaluation dominates ONE file (cf. AES KAT.RoundN).
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------
module Substrate.Algebra.Q.JacobianLiteral1A where
open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.JacobianEncodingGen
open import Substrate.Algebra.Q.JacobianEncodingHom
open import Substrate.Algebra.Q.JacobianExpr using (e₁A; encode)
module _ (x y z : ℚ) where
  open Point  x y z
  open Point2 x y z
  γ₁A : E (encode e₁A) ≋ evalDirect e₁A
  γ₁A = homAgree e₁A
