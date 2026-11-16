-- ⟡nat-enum — numpy-synthesized naturality laws (holding + residue) as a PARAMETERIZED module.
-- --safe: the laws are module PARAMETERS (interface); the consumer discharges each by
-- instantiation with a proof. No ? holes, no postulates. (decode-⊕ / decode-⊗ˢ already PROVEN
-- in the tree — reused, not re-stated.)
{-# OPTIONS --safe --without-K #-}

module NatEnumLaws where

open import Substrate.Algebra.F2.FromBool
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Foundation.Bool
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Nat
open import Substrate.WitnessTower.LehmerPath
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationSum
open import Substrate.WitnessTower.Wedge.PyAstRewriteSemantics
open import Substrate.Algebra.F2 using (F₂) renaming (_+_ to _+₂_; _·_ to _·₂_)

module Laws
  (sign-⊕ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) → bool→F₂ (sign (decode (_⊕_ l₁ l₂))) ≡ (bool→F₂ (sign (decode l₁))) +₂ (bool→F₂ (sign (decode l₂))))
  (sign-⊗ˢ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) → bool→F₂ (sign (decode (_⊗ˢ_ l₁ l₂))) ≡ (parity n ·₂ (bool→F₂ (sign (decode l₁)))) +₂ (parity m ·₂ (bool→F₂ (sign (decode l₂)))))
  (len-⊕ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) → pyLength (_⊕_ l₁ l₂) ≡ (pyLength l₁) + (pyLength l₂))
  (len-⊗ˢ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) → pyLength (_⊗ˢ_ l₁ l₂) ≡ n * n * (pyLength l₁) + m * (pyLength l₂))
  where

  -- consequences of the synthesized laws are derived here; instantiate to discharge.
