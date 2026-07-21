------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Double.InternedEffectivity
--
-- ⟡sppf-quotient-coapex (content half) — INTERNING IS AN EFFECTIVE QUOTIENT:
-- the shape-correspondence and address-equality are ONE relation, packaged as
-- a single biconditional.
--
--   corr⇔addr : Corr t₁ t₂ ⇔ (idx p₁ ≡ idx p₂)        (on a NoDupᴿ heap)
--
-- ⟹ is "no SPLITTING" (corresponding traces share one address — needs the
-- faithful heap); ⟸ is "no COLLAPSE" (a shared address forces correspondence
-- — sound on any register). Together: the address map identifies exactly the
-- corresponding traces and nothing else, which is what makes interning an
-- EFFECTIVE quotient rather than merely a sound hash.
--
-- HONEST SCOPE: both directions are `Interned`'s existing terms. The content
-- here is the IDENTIFICATION — naming the pair as effectivity, in one term,
-- so the property is findable as such — not a new proof.
--
-- ⚑ WHY NOT `KerRel`. The natural-looking framing is "ker addr = Corr", but
-- `KerRel F x y = F x ≡ F y` needs x and y at ONE type, and the membership
-- proofs `shape t₁ ∈ᴿ reg` / `shape t₂ ∈ᴿ reg` are DIFFERENT types (`idx`
-- compares across shapes only because its shape argument is implicit). Forcing
-- `KerRel` therefore requires Σ-packaging the heap into a total space
-- `Σ (WedgeShape ℕ-div) (_∈ᴿ reg)`. That was tried and REJECTED: Σ-packaging is
-- the collapse the substrate declines (see the ∃!-is-a-construction discipline)
-- — the kernel vocabulary would have been bought by flattening the indexed
-- family the statement is actually about. The biconditional below says the same
-- thing in the family's own terms, with no packaging.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Double.InternedEffectivity where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Iff using (_⇔_)
open import Substrate.Algebra.Wedge using (Trace; ℕ-div)
open import Substrate.Algebra.Wedge.Shape using (shape)
open import Substrate.Algebra.Wedge.Shape.Double using (Corr)
open import Substrate.Algebra.Wedge.Shape.Register using (Register; _∈ᴿ_; idx)
open import Substrate.Algebra.Wedge.Shape.Register.Properties using (NoDupᴿ)
open import Substrate.Algebra.Wedge.Shape.Double.Interned using (corr→addr; addr→corr)

------------------------------------------------------------------------
-- EFFECTIVITY — the interior reading (equal shapes) and the exterior reading
-- (equal addresses) are the same relation, as ONE term.
------------------------------------------------------------------------

corr⇔addr : {a₁ b₁ g₁ a₂ b₂ g₂ : ℕ}
            {t₁ : Trace ℕ-div a₁ b₁ g₁} {t₂ : Trace ℕ-div a₂ b₂ g₂} {reg : Register} →
            NoDupᴿ reg →
            (p₁ : shape t₁ ∈ᴿ reg) (p₂ : shape t₂ ∈ᴿ reg) →
            Corr t₁ t₂ ⇔ (idx p₁ ≡ idx p₂)
corr⇔addr nd p₁ p₂ = corr→addr nd p₁ p₂ , addr→corr p₁ p₂
