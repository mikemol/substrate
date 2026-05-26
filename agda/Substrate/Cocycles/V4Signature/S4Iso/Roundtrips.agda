------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso.Roundtrips
--
-- The three round-trip theorems closing the bijection:
--   stab-round-trip   — orbit-key-to-stab-d ∘ stab-d-to-orbit-key ≈ id
--                       on Stab(D)
--   σ-round-trip      — total-to-s4 ∘ s4-to-total ≈ id on Permutation
--   total-round-trip  — s4-to-total ∘ total-to-s4 ≡ id on TotalSpace
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso.Roundtrips where

open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂; trans-sym)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.S4
  using (Permutation; _≈_)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding
  using (act-axis-involutive)
open import Substrate.Groups.SemidirectProduct
  using (Stab; v-of-axis; v-of-axis-unique; v-for; s-for; s-for-fixes-anchor)

open import Substrate.Cocycles.V4Signature.S4Iso.Injective
open import Substrate.Cocycles.V4Signature.S4Iso.StabElements
open import Substrate.Cocycles.V4Signature.S4Iso.Classify
open import Substrate.Cocycles.V4Signature.S4Iso.Cases

------------------------------------------------------------------------
-- Stab(D)-side round-trip.
------------------------------------------------------------------------

stab-round-trip :
  (σ : Permutation) (σ-stab : Stab D σ) →
  orbit-key-to-stab-d (stab-d-to-orbit-key σ σ-stab) ≈ σ
stab-round-trip σ σ-stab z
  with applyₛ σ C in pC | applyₛ σ S in pS
... | D | _ = ⊥-elim (C≢D (σ-injective σ C D (trans-sym pC σ-stab)))
... | C | D = ⊥-elim (S≢D (σ-injective σ S D (trans-sym pS σ-stab)))
... | S | D = ⊥-elim (S≢D (σ-injective σ S D (trans-sym pS σ-stab)))
... | W | D = ⊥-elim (S≢D (σ-injective σ S D (trans-sym pS σ-stab)))
... | C | C = ⊥-elim (S≢C (σ-injective σ S C (trans-sym pS pC)))
... | C | S = sym (case-α-even σ σ-stab pC pS z)
... | C | W = sym (case-α-odd  σ σ-stab pC pS z)
... | S | C = sym (case-β-odd  σ σ-stab pC pS z)
... | S | S = ⊥-elim (C≢S (σ-injective σ C S (trans-sym pC pS)))
... | S | W = sym (case-β-even σ σ-stab pC pS z)
... | W | C = sym (case-γ-even σ σ-stab pC pS z)
... | W | S = sym (case-γ-odd  σ σ-stab pC pS z)
... | W | W = ⊥-elim (C≢S (σ-injective σ C S (trans-sym pC pS)))

------------------------------------------------------------------------
-- S₄-side round-trip.
------------------------------------------------------------------------

σ-round-trip :
  (σ : Permutation) → total-to-s4 (s4-to-total σ) ≈ σ
σ-round-trip σ z =
  trans (cong (act-axis (v-for σ))
              (stab-round-trip (s-for σ) (s-for-fixes-anchor D σ) z))
        (act-axis-involutive (v-for σ) (applyₛ σ z))

------------------------------------------------------------------------
-- TotalSpace-side round-trip.
------------------------------------------------------------------------

total-round-trip :
  (tot : TotalSpace) → s4-to-total (total-to-s4 tot) ≡ tot
total-round-trip (ok , v) = cong₂ _,_ ok-eq v-eq
  where
    σ′ : Permutation
    σ′ = total-to-s4 (ok , v)

    σD : applyₛ σ′ D ≡ act-axis v D
    σD = cong (act-axis v) (orbit-key-to-stab-d-fixes-D ok)

    v-eq : v-for σ′ ≡ v
    v-eq = sym (v-of-axis-unique v (applyₛ σ′ D) (sym σD))

    s≈orb : (z : Axis) →
            applyₛ (s-for σ′) z ≡ applyₛ (orbit-key-to-stab-d ok) z
    s≈orb z =
      trans (cong (λ w → act-axis w (act-axis v
                          (applyₛ (orbit-key-to-stab-d ok) z))) v-eq)
            (act-axis-involutive v (applyₛ (orbit-key-to-stab-d ok) z))

    ok-eq : classify-CS (applyₛ (s-for σ′) C) (applyₛ (s-for σ′) S) ≡ ok
    ok-eq =
      trans (cong₂ classify-CS (s≈orb C) (s≈orb S))
            (ok-round-trip ok)
