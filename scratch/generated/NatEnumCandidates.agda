-- ⟡nat-enum CANDIDATES — numpy-verified naturality facts, proofs pending (synthesis hand-off).
-- Each holds on ALL instances up to grade 5; `?` is the by-hand/LLM proof step.
{-# OPTIONS --without-K #-}

module NatEnumCandidates where

open import Substrate.Foundation.Bool
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Nat
open import Substrate.WitnessTower.LehmerPath
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationSum
open import Substrate.WitnessTower.Wedge.PyAstRewriteSemantics

sign-⊕ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
  sign (decode (_⊕_ l₁ l₂)) ≡ _xor_ (sign (decode l₁)) (sign (decode l₂))
sign-⊕ l₁ l₂ = ?

len-⊕ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
  pyLength (_⊕_ l₁ l₂) ≡ _+_ (pyLength l₁) (pyLength l₂)
len-⊕ l₁ l₂ = ?
