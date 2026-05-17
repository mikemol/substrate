------------------------------------------------------------------------
-- Substrate.Algebra.F2.Code.Universal
--
-- M-4.5 of the Cocycles structural-migration plan. The universal
-- characterisation of code equality: two ImageCodes describe the same
-- subspace iff their generators agree as linear maps, which (by
-- linear-extensionality) reduces to agreement on n basis vectors.
--
-- This is small — most of the work was done by M-3.5
-- (linear-extensionality). The slice exists to NAME the bridge
-- explicitly so downstream code can cite "same-image-by-basis" as a
-- single inference rule, rather than reconstructing the chain.
--
-- More-substantial code-equality bridges (image-form ↔ kernel-form
-- via dual-code; subspace equality across codes of different
-- ambient dimension via puncturing) go in their own slices when
-- consumers need them.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Code.Universal where

open import Data.Nat using (ℕ)
open import Data.Fin using (Fin)
open import Data.Product using (_,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong)

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.Universal
open import Substrate.Algebra.F2.Code

------------------------------------------------------------------------
-- Same-image via basis.
--
-- Two ImageCodes describe the same subspace if their generators agree
-- on basis vectors (and thereby on every vector, via
-- linear-extensionality).
--
-- The bidirectional statement (same image ⇔ generators agree on
-- basis) — only the forward direction is provable structurally; the
-- reverse needs rank/dim machinery and is deferred.
------------------------------------------------------------------------

same-generator-from-basis :
  ∀ {k n} (C₁ C₂ : ImageCode k n) →
  ((i : Fin k) → apply (generator C₁) (basis i) ≡ apply (generator C₂) (basis i)) →
  (u : Vector k) → apply (generator C₁) u ≡ apply (generator C₂) u
same-generator-from-basis C₁ C₂ agree =
  linear-extensionality (generator C₁) (generator C₂) agree

------------------------------------------------------------------------
-- Same-image-membership: if generators agree on basis, any codeword
-- of C₁ is a codeword of C₂ (and vice versa, by symmetry of the
-- hypothesis).
--
-- Forward direction:
--   v ∈ In-Image C₁  ⇒  v ∈ In-Image C₂.
--
-- Witness: the same coordinate vector u works for both codes; the
-- equation apply (generator C₂) u ≡ v is obtained by transporting
-- through `same-generator-from-basis`.
------------------------------------------------------------------------

in-image-transport :
  ∀ {k n} (C₁ C₂ : ImageCode k n) →
  ((i : Fin k) → apply (generator C₁) (basis i) ≡ apply (generator C₂) (basis i)) →
  (v : Vector n) → In-Image C₁ v → In-Image C₂ v
in-image-transport C₁ C₂ agree v (u , eq₁) =
  u , trans (sym (same-generator-from-basis C₁ C₂ agree u)) eq₁

------------------------------------------------------------------------
-- Code-equivalence: a pair of ImageCodes with the same coordinate
-- dimension k and ambient n is "equivalent" (i.e., describe the
-- same subspace) if their generators agree on the basis.
--
-- This is the universal-property record. Downstream code bridges
-- (RM(r,m) via poly-eval = RM(r,m) via generator matrix) instantiate
-- this once and equality propagates via in-image-transport.
------------------------------------------------------------------------

record Image-Equivalent {k n : ℕ} (C₁ C₂ : ImageCode k n) : Set where
  field
    basis-agree :
      (i : Fin k) →
      apply (generator C₁) (basis i) ≡ apply (generator C₂) (basis i)

  -- Derived: codewords transport in both directions.
  to-C₂ : (v : Vector n) → In-Image C₁ v → In-Image C₂ v
  to-C₂ = in-image-transport C₁ C₂ basis-agree

  to-C₁ : (v : Vector n) → In-Image C₂ v → In-Image C₁ v
  to-C₁ = in-image-transport C₂ C₁ (λ i → sym (basis-agree i))
