------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Roundtrip
--
-- perm-roundtrip-≈: compositional-to-perm inverts perm-to-compositional.
-- embed-as-N-injection: V₄ embed ≈ compositional injection at (v, ε_S₃).
-- Plus small inv-distrib + embed-inv-≈ helpers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Roundtrip where

open import Substrate.Groups.SemidirectProduct.V.NonDSends
open import Substrate.Groups.SemidirectProduct.V.Private
open import Substrate.Groups.SemidirectProduct.V.SelfToD
open import Substrate.Groups.SemidirectProduct.V.VFor
open import Substrate.Groups.SemidirectProduct.V.VForAnchor
open import Substrate.Groups.SemidirectProduct.V.VForAnchorSends
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchorSends
open import Substrate.Groups.SemidirectProduct.V.VOfAxisUnique
open import Substrate.Groups.SemidirectProduct.V.VSendsD
open import Substrate.Axes.Axis using (Axis; D)
open import Substrate.Groups.V4.Bijection.FromC
open import Substrate.Groups.V4.Bijection.FromCCanonical
open import Substrate.Groups.V4.Bijection.FromTo
open import Substrate.Groups.V4.Bijection.Private
open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.ToCCanonical
open import Substrate.Groups.V4.Bijection.ToFromCanonical
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.V4-Embedding using (embed; embed-self-inverse)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.Symmetric.Permutation.Inverse Axis using (_⁻¹)
open import Substrate.Groups.SemidirectProduct
  using (v-for; s-for; s-for-fixes-anchor)

open import Substrate.Groups.S4-Iso.Embedding.CompositionalToPerm
open import Substrate.Groups.S4-Iso.Embedding.EmbedS3
open import Substrate.Groups.S4-Iso.Extract
  using (extract-s; perm-to-compositional)
open import Substrate.Groups.S4-Iso.Foundation using (embed-S₃-ε)
open import Substrate.Groups.S4-Iso.ExtractCorrect using (extract-s-correct)
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Product
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Groups.V4.Operations as V4
open V4 using (V₄)

------------------------------------------------------------------------
-- compositional-to-perm ∘ perm-to-compositional ≈ id.
------------------------------------------------------------------------

perm-roundtrip-≈ : (σ : Permutation) →
                   compositional-to-perm (perm-to-compositional σ) ≈ σ
perm-roundtrip-≈ σ x =
  trans (cong (apply (embed (v-for σ)))
              (extract-s-correct (s-for σ) (s-for-fixes-anchor D σ) x))
        (embed-self-inverse (v-for σ) (apply σ x))

------------------------------------------------------------------------
-- embed-as-N-injection: V₄ embed agrees with (v, ε_S₃) injection.
------------------------------------------------------------------------

module _ where
  open import Substrate.Foundation.Product using (_,_)

  embed-as-N-injection : (v : V₄) →
                         embed v ≈ compositional-to-perm (v , S₃.ε)
  embed-as-N-injection v x = sym (cong (apply (embed v)) (embed-S₃-ε x))

------------------------------------------------------------------------
-- Small permutation algebra lemmas.
------------------------------------------------------------------------

inv-distrib : (σ τ : Permutation) → ((σ · τ) ⁻¹) ≈ ((τ ⁻¹) · (σ ⁻¹))
inv-distrib σ τ x = refl

embed-inv-≈ : (v : V₄) → (embed v) ⁻¹ ≈ embed v
embed-inv-≈ v x = refl
