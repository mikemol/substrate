------------------------------------------------------------------------
-- Substrate.Geometry.HodgeDim3.V4Plane
--
-- N-1 of M-11.dim3. The V₄-plane in F₂³ as a structural F₂-linear
-- subspace: the kernel of the "project chirality bit" linear map.
--
-- Structural identification:
--   V₄-plane = ⟨e₁, e₂⟩ = {v ∈ F₂³ : lookup v 2 ≡ 𝟘}
--           = the 4-element 2-dim subspace {𝟎ⱽ, e₁, e₂, e₁+e₂}
--
-- Two views, with a bridge between them:
--   * KernelCode form: V₄-plane = ker (V4Plane-Selector : Linear 3 1)
--     where V4Plane-Selector projects to the chirality bit.
--   * Predicate form:  V₄-plane-Pred v = lookup v ₂ ≡ 𝟘
--     (direct bit constraint; easier for computational arguments).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.HodgeDim3.V4Plane where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₄)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)

open import Substrate.Algebra.F2.AbsorbL
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2Cases
open import Substrate.Algebra.F2.Idempotent
open import Substrate.Algebra.F2.IdentityL
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.InvOfOne
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Op2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusInverseL
open import Substrate.Algebra.F2.PlusInverseR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.ZeroNeqOne
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.CompLAssoc
open import Substrate.Algebra.F2.Linear.CompLIdentityL
open import Substrate.Algebra.F2.Linear.CompLIdentityR
open import Substrate.Algebra.F2.Linear.IdL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Preserves
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.Algebra.F2.Linear.KernelPredBridge
  using (pred-at-i→kernel-at-i; kernel-at-i→pred-at-i)
open import Substrate.Algebra.F2.Code
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.SymTrans

------------------------------------------------------------------------
-- Basis-images of the "project chirality bit" linear map.
--
-- Maps F₂³'s 3 basis vectors to F₂¹:
--   e₀ ↦ 𝟎ⱽ        (V₄ bit 0 doesn't contribute to chirality)
--   e₁ ↦ 𝟎ⱽ        (V₄ bit 1 doesn't contribute)
--   e₂ ↦ 𝟙 ∷ []   (chirality bit is the output)
------------------------------------------------------------------------

chirality-bit-images : Fin 3 → Vector 1
chirality-bit-images zero          = 𝟎ⱽ
chirality-bit-images (suc zero)    = 𝟎ⱽ
chirality-bit-images ₂ = 𝟙 ∷ []

------------------------------------------------------------------------
-- The F₂-linear projection itself.
------------------------------------------------------------------------

V4Plane-Selector : Linear 3 1
V4Plane-Selector = linear-from-images chirality-bit-images

------------------------------------------------------------------------
-- The V₄-plane as a KernelCode: membership = kernel of the selector.
------------------------------------------------------------------------

V4-Plane : KernelCode 3 1
V4-Plane = record { parity-check = V4Plane-Selector }

------------------------------------------------------------------------
-- Predicate form: direct bit-constraint.
--
-- A vector v ∈ V₄-plane iff its chirality bit (index 2) is 𝟘.
------------------------------------------------------------------------

V4-Plane-Pred : Vector 3 → Set
V4-Plane-Pred v = lookup v ₂ ≡ 𝟘

------------------------------------------------------------------------
-- Application of V4Plane-Selector reduces to the chirality bit.
--
-- The key computational fact: apply V4Plane-Selector v ≡ lookup v 2 ∷ [].
-- Proved by ≡-from-lookup +F lookup-sum +F componentwise reduction.
------------------------------------------------------------------------

apply-V4Plane-Selector-lookup :
  (v : Vector 3) →
  lookup (apply V4Plane-Selector v) zero ≡ lookup v ₂
apply-V4Plane-Selector-lookup (a ∷ b ∷ c ∷ []) =
  -- `linear-from-images` is opaque, so we reach the dense sum via its
  -- characterising lemma (not by reduction); the sum a · 𝟘 +F (b · 𝟘 +F (c · 𝟙 +F 𝟘))
  -- then collapses through the identities to c.
  trans (apply-linear-from-images-lookup chirality-bit-images (a ∷ b ∷ c ∷ []) zero)
  (cong-trans (_+ (b · 𝟘 +F (c · 𝟙 +F 𝟘))) (·-absorbʳ a)
  (trans (+-identityˡ _)
  (cong-trans (_+ (c · 𝟙 +F 𝟘)) (·-absorbʳ b)
  (trans (+-identityˡ _)
  (cong-trans (_+ 𝟘) (·-identityʳ c)
         (+-identityʳ c))))))

------------------------------------------------------------------------
-- Bridges between KernelCode membership and predicate form.
------------------------------------------------------------------------

pred→kernel : (v : Vector 3) → V4-Plane-Pred v → In-Kernel V4-Plane v
pred→kernel v pred = ≡-from-lookup _ _ goal
  where
    goal : (j : Fin 1) →
           lookup (apply V4Plane-Selector v) j ≡ lookup (𝟎ⱽ {1}) j
    goal zero = pred-at-i→kernel-at-i V4Plane-Selector v zero (apply-V4Plane-Selector-lookup v) pred

kernel→pred : (v : Vector 3) → In-Kernel V4-Plane v → V4-Plane-Pred v
kernel→pred v ker =
  kernel-at-i→pred-at-i V4Plane-Selector v zero (apply-V4Plane-Selector-lookup v) ker
