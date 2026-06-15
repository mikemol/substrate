------------------------------------------------------------------------
-- Substrate.Algebra.Monoid.InverseRetract
--
-- The free, ring-agnostic heart of every "decrypt ∘ encrypt ≡ id" that is
-- built from a unit and its inverse: multiplying by a left-inverse RETRACTS
-- multiplication. Over any `Monoid`, from `d · c ≡ ε` conclude
-- `d · (c · v) ≡ v` — by associativity and the left-identity law, nothing more.
--
-- AES MixColumns/InvMixColumns is exactly this lemma at the multiplicative
-- monoid of the "column ring" R[y]/(yᴺ−1): `mix = c ·_`, `inv = d ·_`, and
-- `inv (mix v) ≡ v` is `left-inverse-retract` with the witness `d · c ≡ ε`
-- (the only domain-specific content — for AES, the 4 collapse facts). The
-- circulant / Cₙ-equivariant / coordinate-rotation presentation is the shadow
-- of this one line when the monoid is written in the basis {1, y, …, yᴺ⁻¹}.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Monoid.InverseRetract where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)

module _ {A : Set} (M : Monoid A) where
  private
    _·_ : A → A → A
    _·_ = Magma._·_ (Semigroup.magma (Monoid.semigroup M))

  -- left-multiplication by `d` retracts left-multiplication by `c`, given `d · c ≡ ε`.
  left-inverse-retract : (c d v : A) → (d · c) ≡ Monoid.ε M → d · (c · v) ≡ v
  left-inverse-retract c d v dc≡ε =
    trans (sym (Semigroup.·-assoc (Monoid.semigroup M) d c v))
          (trans (cong (_· v) dc≡ε) (Monoid.ε-left M v))
