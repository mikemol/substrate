------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Compose.Laws
--
-- ℕ-div SATISFIES the wedge-category laws — the concrete witness that the
-- recon-linearity identity (already identified in the arrow-category
-- analysis) holds, assembled from the existing Foundation.Nat ring lemmas:
--
--   recon-linear:  q·(q'·c + r') + r ≡ (q·q')·c + (q·r' + r)
--                  via *-distribˡ-+, *-assoc, +-assoc.
--   recon-unit:    1·x + 0 ≡ x       via +-identityʳ, *-identityˡ.
--
-- def/proof separation: this is the proof side (imports Foundation.Nat
-- *.Properties); Compose.agda is the carrier-neutral definition side.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Compose.Laws where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-identityˡ; *-distribˡ-+; *-assoc)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-assoc)
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Algebra.Wedge.Compose using (ReconLinear; ReconUnit)

ℕ-recon-linear : ReconLinear ℕ-div
ℕ-recon-linear q q′ c r′ r =
  trans (cong (_+ r) (*-distribˡ-+ q (q′ * c) r′))
  (trans (cong (λ w → w + q * r′ + r) (sym (*-assoc q q′ c)))
         (+-assoc ((q * q′) * c) (q * r′) r))

ℕ-recon-unit : ReconUnit ℕ-div
ℕ-recon-unit x = trans (+-identityʳ (suc zero * x)) (*-identityˡ x)
