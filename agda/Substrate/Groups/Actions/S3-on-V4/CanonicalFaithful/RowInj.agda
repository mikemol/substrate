{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.RowInj where

-- ROW-INJECTIVITY: agreeing at α and β ⇒ same row. 36 cases.

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.V4.Bijection using (α; β)
open import Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.Row
open import Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.ActRow using (act-row)

row-inj : (ρ σ : Row) →
          act-row ρ α ≡ act-row σ α →
          act-row ρ β ≡ act-row σ β →
          ρ ≡ σ
-- diagonal
row-inj id  id  _  _  = refl
row-inj r   r   _  _  = refl
row-inj r²  r²  _  _  = refl
row-inj s   s   _  _  = refl
row-inj sr  sr  _  _  = refl
row-inj sr² sr² _  _  = refl
-- off-diagonal: at least one of the α/β equations is between distinct V₄
-- constructors, so absurd. Agda finds the distinguishing coordinate.
row-inj id  r   () _
row-inj id  r²  () _
row-inj id  s   () _
row-inj id  sr  () _
row-inj id  sr² pα ()
row-inj r   id  () _
row-inj r   r²  () _
row-inj r   s   pα ()
row-inj r   sr  () _
row-inj r   sr² () _
row-inj r²  id  () _
row-inj r²  r   () _
row-inj r²  s   () _
row-inj r²  sr  pα ()
row-inj r²  sr² () _
row-inj s   id  () _
row-inj s   r   pα ()
row-inj s   r²  () _
row-inj s   sr  () _
row-inj s   sr² () _
row-inj sr  id  () _
row-inj sr  r   () _
row-inj sr  r²  pα ()
row-inj sr  s   () _
row-inj sr  sr² () _
row-inj sr² id  pα ()
row-inj sr² r   () _
row-inj sr² r²  () _
row-inj sr² s   () _
row-inj sr² sr  () _
