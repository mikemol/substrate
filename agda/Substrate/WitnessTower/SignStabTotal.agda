------------------------------------------------------------------------
-- Substrate.WitnessTower.SignStabTotal
--
-- ⟡sign-stab-total — the CAPSTONE of the sign/Stab arc. Wires the two hard
-- pieces (both now done) into the fully-general orientation-anchored sign:
--
--   * factorisation (Groups.SemidirectProduct.Factorisation):
--       σ ≈ embed (v-for σ) · s-for σ   — every S₄ elt = V₄ part · Stab part.
--   * sign-embed-v-even (WitnessTower.SignEmbedVEven):
--       sign (perm4 (embed v · s)) ≡ sign (perm4 s) — V₄ contributes nothing.
--
-- TOGETHER: sign σ depends ONLY on the orientation-anchored Stab component:
--
--   sign (perm4 σ) ≡ sign (perm4 (s-for σ))     (for ALL σ : Permutation)
--
-- This is the honest total sign morphism the raw carrier denied (non-perms
-- broke the digit) — Stab-anchoring reconciles it, and it now holds on ALL of
-- S₄, not just the 24 codeword cases. sign is a function of the Stab part
-- alone: the V₄ freedom is exactly the kernel.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SignStabTotal where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (tabulate)
open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.SnGroup using (apply-injective)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign)
open import Substrate.Axes using (Axis)
open import Substrate.Axes.Punctured using (a→f; f→a)
open import Substrate.Groups.S4 using (Permutation; _≈_; _·_; apply)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.SemidirectProduct.V using (v-for)
open import Substrate.Groups.SemidirectProduct.S using (s-for)
open import Substrate.Groups.SemidirectProduct.Factorisation using (factorisation)
open import Substrate.WitnessTower.SignEmbedVEven using (perm4; sign-embed-v-even)

------------------------------------------------------------------------
-- perm4 respects the setoid ≈ (it reads apply pointwise). So ≈-equal
-- permutations have ≡-equal transports, and sign transports through ≈.
------------------------------------------------------------------------

perm4-resp-≈ : {σ τ : Permutation} → σ ≈ τ → perm4 σ ≡ perm4 τ
perm4-resp-≈ {σ} {τ} eq = apply-injective λ i →
  trans (lookup∘tabulate (λ j → a→f (apply σ (f→a j))) i)
        (trans (cong a→f (eq (f→a i)))
               (sym (lookup∘tabulate (λ j → a→f (apply τ (f→a j))) i)))

------------------------------------------------------------------------
-- THE CAPSTONE: sign depends only on the Stab component. Chain:
--   sign(perm4 σ)
--     ≡ sign(perm4 (embed(v-for σ) · s-for σ))   [factorisation, via perm4-resp-≈]
--     ≡ sign(perm4 (s-for σ))                     [sign-embed-v-even]
------------------------------------------------------------------------

sign-stab-total : (σ : Permutation) → sign (perm4 σ) ≡ sign (perm4 (s-for σ))
sign-stab-total σ =
  trans (cong sign (perm4-resp-≈ {σ} {embed (v-for σ) · s-for σ} (factorisation σ)))
        (sign-embed-v-even (v-for σ) (s-for σ))

------------------------------------------------------------------------
-- The morphism reading: sign FACTORS THROUGH the Stab retraction s-for.
-- Define sign-of = sign ∘ perm4 : Permutation → Bool. Then sign-stab-total
-- is exactly sign-of ≡ sign-of ∘ s-for — sign is invariant under stripping
-- the V₄ part, i.e. it factors through the orientation-anchored Stab
-- component. This is the total sign morphism (all of S₄), the honest form
-- the raw non-perm carrier could not carry.
------------------------------------------------------------------------

sign-of : Permutation → Bool
sign-of σ = sign (perm4 σ)

sign-factors-through-s-for : (σ : Permutation) → sign-of σ ≡ sign-of (s-for σ)
sign-factors-through-s-for = sign-stab-total

-- s-for is idempotent-on-sign: applying it again does not change the sign
-- (s-for σ already has trivial V₄ part). So sign-of is constant on each
-- V₄-coset — the coset being the fibre of the Stab retraction.
sign-of-stable : (σ : Permutation) → sign-of (s-for σ) ≡ sign-of (s-for (s-for σ))
sign-of-stable σ = sign-stab-total (s-for σ)
