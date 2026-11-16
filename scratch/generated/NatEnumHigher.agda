-- ⟡nat-enum-higher — the DISTRIBUTOR (J₃) coherence for maps, as a --safe PARAMETERIZED module.
{-# OPTIONS --safe --without-K #-}

module NatEnumHigher where

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
  (sign-δ : ∀ {m p q} (l₁ : LehmerPath m) (l₂ : LehmerPath p) (l₃ : LehmerPath q) → bool→F₂ (sign (decode (_⊗ˢ_ l₁ (_⊕_ l₂ l₃)))) ≡ bool→F₂ (sign (decode (_⊕_ (_⊗ˢ_ l₁ l₂) (_⊗ˢ_ l₁ l₃)))))
  (len-δ : ∀ {m p q} (l₁ : LehmerPath m) (l₂ : LehmerPath p) (l₃ : LehmerPath q) → pyLength (_⊗ˢ_ l₁ (_⊕_ l₂ l₃)) ≡ pyLength (_⊕_ (_⊗ˢ_ l₁ l₂) (_⊗ˢ_ l₁ l₃)) + 2 * p * q * (pyLength l₁))
  where
