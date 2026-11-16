------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Compose.Laws
--
-- ℕ-div SATISFIES the wedge-category laws — the concrete witness that the
-- recon-linearity identity (already identified in the arrow-category
-- analysis) holds, assembled from the existing Foundation.Nat ring lemmas:
--
--   recon-linear:  q·(q'·c ℕ+ r') ℕ+ r ≡ (q·q')·c ℕ+ (q·r' ℕ+ r)
--                  via *-distribˡ-+, *-assoc, +-assoc.
--   recon-unit:    1·x ℕ+ 0 ≡ x       via +ℕ-identityʳ, *-identityˡ.
--
-- def/proof separation: this is the proof side (imports Foundation.Nat
-- *.Properties); Compose.agda is the carrier-neutral definition side.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Compose.Laws where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-identityˡ; *-distribˡ-+; *-assoc)
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Algebra.Wedge.Compose using (ReconLinear; ReconUnit)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

ℕ-recon-linear : ReconLinear ℕ-div _*_
ℕ-recon-linear q q′ c r′ r =
  trans (cong (_ℕ+ r) (*-distribˡ-+ q (q′ * c) r′))
  (trans (cong (λ w → w ℕ+ q * r′ ℕ+ r) (sym (*-assoc q q′ c)))
         (+ℕ-assoc ((q * q′) * c) (q * r′) r))

ℕ-recon-unit : ReconUnit ℕ-div (suc zero)
ℕ-recon-unit x = trans (+ℕ-identityʳ (suc zero * x)) (*-identityˡ x)
