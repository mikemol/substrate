{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianExpr — the DEFINITION module for ◆jac-gamma.
--
-- The free commutative-ring term `Expr` on {x,y,z,+,·,−}, its MPoly encoding
-- `encode`, and the three C-component trees `eᵢ`. Point-independent syntax;
-- `eᵢ` mirrors C.fᵢ's OWN grouping, so `encode eᵢ` reduces to `Cᴹfᵢ` on the nose.
--
-- Definition-only (def/proof separation policy): declares `data Expr` and imports
-- NO proof module. The ≈ℚ homomorphism proof lives in `JacobianEncodingLiteral`.
--
-- --safe --without-K.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianExpr where

open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
import Substrate.Algebra.Z.JacobianResidue as R
open R using (MPoly; _*P_; _+P_)

data Expr : Set where
  eX eY eZ : Expr
  eK       : ℤ → Expr
  _⊕E_ _⊗E_ _⊖E_ : Expr → Expr → Expr

infixl 6 _⊕E_ _⊖E_
infixl 7 _⊗E_

encode : Expr → MPoly
encode eX        = R.X
encode eY        = R.Y
encode eZ        = R.Z₁
encode (eK k)    = R.kP k
encode (a ⊕E b)  = encode a +P encode b
encode (a ⊗E b)  = encode a *P encode b
encode (a ⊖E b)  = encode a +P (R.kP (-suc 0) *P encode b)   -- a − b = a + (−1)·b

-- C's where-bound locals u,v, as syntax.
uE vE : Expr
uE = eK (+ 1) ⊕E (eX ⊗E eY)                       -- u = 1 + xy
vE = eK (+ 4) ⊕E (eK (+ 3) ⊗E (eX ⊗E eY))         -- v = 4 + 3xy

-- ⚑ e₁'s two summands, NAMED so γ₁ = homAgree e₁ can be proved per-summand in
-- SEPARATE modules (z·u³ and y²·u·v each dominate a file) and recomposed by the
-- AES-Full anti-explosion pattern (abstract Assemble + open-not-redeclare), so no
-- module ever forces `E (encode e₁A +P encode e₁B)` (the top +-hom over the sum).
e₁A e₁B : Expr
e₁A = eZ ⊗E (uE ⊗E (uE ⊗E uE))                    -- z · u³
e₁B = ((eY ⊗E eY) ⊗E uE) ⊗E vE                     -- y² · u · v

-- The three components of F, transcribing C.fᵢ's exact tree.
e₁ e₂ e₃ : Expr
e₁ = e₁A ⊕E e₁B
e₂ = (eY ⊕E ((eK (+ 3) ⊗E (eX ⊗E (uE ⊗E uE))) ⊗E eZ))
     ⊕E ((eK (+ 3) ⊗E (eX ⊗E (eY ⊗E eY))) ⊗E vE)
e₃ = ((eK (+ 2) ⊗E eX) ⊖E ((eK (+ 3) ⊗E (eX ⊗E eX)) ⊗E eY))
     ⊖E (((eX ⊗E eX) ⊗E eX) ⊗E eZ)
