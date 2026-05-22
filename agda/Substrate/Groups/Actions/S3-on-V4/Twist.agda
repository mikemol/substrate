------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Twist
--
-- The dihedral generator-level twist relations:
--   act-equals-pow      — bridge act-on-canonical ↔ rot-pow ∘ swap-pow
--   swap-rotate-twist   — swap-αβ ∘ rotate ≡ rotate² ∘ swap-αβ
--   rot-pow-swap-twist  — lifted twist on canonical n
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Generators public

------------------------------------------------------------------------
-- act-equals-pow: bridge act-on-canonical ↔ rot-pow ∘ swap-pow on
-- canonical inputs (24 refl).
------------------------------------------------------------------------

act-equals-pow : ∀ {n h} → Z₃.Canonical n → Z₂.Canonical h → ∀ v →
                 act-on-canonical n h v ≡ rot-pow n (swap-pow h v)
act-equals-pow Z₃.c-ε  Z₂.c-ε = v4-cover _ (refl , refl , refl , refl)
act-equals-pow Z₃.c-a  Z₂.c-ε = v4-cover _ (refl , refl , refl , refl)
act-equals-pow Z₃.c-aa Z₂.c-ε = v4-cover _ (refl , refl , refl , refl)
act-equals-pow Z₃.c-ε  Z₂.c-a = v4-cover _ (refl , refl , refl , refl)
act-equals-pow Z₃.c-a  Z₂.c-a = v4-cover _ (refl , refl , refl , refl)
act-equals-pow Z₃.c-aa Z₂.c-a = v4-cover _ (refl , refl , refl , refl)

------------------------------------------------------------------------
-- Dihedral generator-level relation.
------------------------------------------------------------------------

swap-rotate-twist : (v : V₄) → swap-αβ (rotate v) ≡ rotate (rotate (swap-αβ v))
swap-rotate-twist = v4-cover _ (refl , refl , refl , refl)

------------------------------------------------------------------------
-- rot-pow ↔ swap twist on canonical n.
------------------------------------------------------------------------

rot-pow-swap-twist : ∀ {n} → Z₃.Canonical n → (v : V₄) →
                     swap-αβ (rot-pow n v) ≡ rot-pow (Z₃.inv n) (swap-αβ v)
rot-pow-swap-twist Z₃.c-ε  = v4-cover _ (refl , refl , refl , refl)
rot-pow-swap-twist Z₃.c-a  = v4-cover _ (refl , refl , refl , refl)
rot-pow-swap-twist Z₃.c-aa = v4-cover _ (refl , refl , refl , refl)
