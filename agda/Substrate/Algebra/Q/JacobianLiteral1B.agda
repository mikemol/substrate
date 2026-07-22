{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianLiteral1B — the y²·u·v summand of γ₁, alone.
-- γ₁A = homAgree e₁B : E (encode e₁B) ≋ evalDirect e₁B. Kept in its own module
-- so the y²·u·v summand dominates ONE file (cf. AES KAT.RoundN).
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------
module Substrate.Algebra.Q.JacobianLiteral1B where
open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.JacobianEncodingGen
open import Substrate.Algebra.Q.JacobianEncodingHom
open import Substrate.Algebra.Q.JacobianExpr using (e₁B; encode)
module _ (x y z : ℚ) where
  open Point  x y z
  open Point2 x y z
  γ₁B : E (encode e₁B) ≋ evalDirect e₁B
  γ₁B = homAgree e₁B
