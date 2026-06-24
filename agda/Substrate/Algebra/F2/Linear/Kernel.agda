------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Kernel
--
-- Ⓕ.spectral (brick 2) — the (linear) KERNEL of an F₂-linear map as a
-- SUBSPACE. For the JEA-Pi cotype this is the carrier of the count:
-- ker (ΦL T p) is the Φ_p-ISOTYPIC component of the cycle-space operator,
-- and the cotype's mult2/2 is (the multiplicity factor of) its dimension.
--
-- WHAT IS PROVED (no overclaim): ker L = {v : L v ≡ 𝟎ⱽ} is closed under
-- the F₂-module operations — it is a subspace —
--   • ker-𝟎  : 𝟎ⱽ ∈ ker L                       (preserves-𝟎)
--   • ker-+ⱽ : u,v ∈ ker L → u +ⱽ v ∈ ker L      (preserves-+)
--   • ker-*ₛ : v ∈ ker L → c *ₛ v ∈ ker L         (preserves-*ₛ)
-- generic in ANY L : Linear n m (instantiate at ΦL T p for the isotypic).
-- Plus the kernel-as-QUOTIENT tie (reuse Algebra.Quotient.ker-Quotient).
--
-- METHOD (read-structure-dont-rebuild): closure is three one-liners off
-- the linearity proofs already in F2.Linear; *ₛ-zeroʳ is reused from
-- FromImages; the kernel-quotient is `ker-Quotient` verbatim. No new
-- machinery — this is the assembly of existing pieces.
--
-- NOTE — two distinct "kernels", both recorded:
--   • the LINEAR kernel {v : L v ≡ 𝟎ⱽ} (this file's subspace) — its
--     dimension is the NULLITY (what mult counts);
--   • `ker-quotient` = V / (x ~ y iff L x ≡ L y) ≅ im L (first iso) — its
--     size is the RANK; nullity = n − rank over the finite F₂ space.
--
-- NEXT BRICK (NOT here): dim (ker (ΦL T p)) ≡ mult2 p n / 2 · degΦ_p.
-- Generic "dimension of a subspace" (basis / rank / nullity) is ABSENT
-- from the tree; the bridge (Ⓕ.spectral-bridge) will instead EXHIBIT an
-- explicit basis of the cycle-operator kernel of that size.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Kernel where

open import Substrate.Foundation.Eq using (_≡_; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages using (*ₛ-zeroʳ)
open import Substrate.Algebra.Quotient using (Quotient; KerRel; ker-Quotient)

------------------------------------------------------------------------
-- Membership in the linear kernel.
------------------------------------------------------------------------

-- v ∈ ker L  iff  L sends it to the zero vector.
inKer : ∀ {n m} → Linear n m → Vector n → Set
inKer L v = apply L v ≡ 𝟎ⱽ

------------------------------------------------------------------------
-- ker L is a subspace: contains 𝟎ⱽ, closed under +ⱽ and under *ₛ.
------------------------------------------------------------------------

ker-𝟎 : ∀ {n m} (L : Linear n m) → inKer L 𝟎ⱽ
ker-𝟎 L = preserves-𝟎 L

ker-+ⱽ : ∀ {n m} (L : Linear n m) {u v : Vector n} →
         inKer L u → inKer L v → inKer L (u +ⱽ v)
ker-+ⱽ L {u} {v} pu pv =
  trans (preserves-+ L u v)
        (trans (cong₂ _+ⱽ_ pu pv) (+ⱽ-identityˡ 𝟎ⱽ))

ker-*ₛ : ∀ {n m} (L : Linear n m) (c : F₂) {v : Vector n} →
         inKer L v → inKer L (c *ₛ v)
ker-*ₛ L c {v} pv =
  trans (preserves-*ₛ L c v)
        (trans (cong (c *ₛ_) pv) (*ₛ-zeroʳ c))

------------------------------------------------------------------------
-- The kernel as a quotient (first-isomorphism side): V / (same image) ≅ im L.
-- Reused verbatim from Algebra.Quotient; the dimension brick takes the
-- rank from here and nullity = n − rank.
------------------------------------------------------------------------

ker-quotient : ∀ {n m} (L : Linear n m) → Quotient (Vector n) (KerRel (apply L))
ker-quotient L = ker-Quotient (apply L)
