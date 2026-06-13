------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.WedgeUP
--
-- The WEDGE, connected through `UPArrow` (user, 2026-06-13: "Look for UPArrow…
-- you'll want to connect through there, too"). The substrate's universal-property
-- registry is the proper home for the wedge / Euclidean-division UP that the R-arc
-- (`RationalAdjunction`) and the wedge layer (`Algebra.Wedge.Adjunction`) both
-- realise. Here it is one object of Arr(Span):
--
--   Source  (Spec) = a value and a divisor   (a , b)
--   Target  (Inst) = a quotient and remainder (q , r)
--   Witness        = the decomposition  a ≡ recon q b r   (= a ≡ q·b + r over ℕ-div)
--
-- This is a RecognizedUP — it carries its non-vacuity certificate (not every (q,r)
-- decomposes every a). And it is UNIVERSAL in the strong sense: on BOUNDED targets
-- (r < b) the solution is UNIQUE — the "no-gauge certificate" `Algebra.Wedge`
-- flagged, proved in `Wedge.BoundedIso.recon-bounded-unique` (← `divmod-unique`).
-- So the full chain is wired: UPArrow ← uniqueness ← BoundedIso ← divmod-unique,
-- and `RationalAdjunction`'s qStep/reconStep are its coalgebra-dynamics facade.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.WedgeUP where

open import Substrate.Foundation.Nat      using (ℕ; suc; _<_)
open import Substrate.Foundation.Eq       using (_≡_; sym; trans)
open import Substrate.Foundation.Product  using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Negation using (¬_)

open import Substrate.Algebra.Wedge             using (recon; ℕ-div)
open import Substrate.Algebra.Wedge.BoundedIso  using (recon-bounded-unique)
open import Substrate.Category.UniversalProperty          using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity  using (Contentful)
open import Substrate.Category.UniversalProperty.Recognized using (RecognizedUP)

------------------------------------------------------------------------
-- The wedge as a UPArrow.
------------------------------------------------------------------------

wedge-UP : UPArrow
wedge-UP = record
  { Source  = ℕ × ℕ                                                   -- (value a , divisor b)
  ; Target  = ℕ × ℕ                                                   -- (quotient q , remainder r)
  ; Witness = λ ab qr → proj₁ ab ≡ recon ℕ-div (proj₁ qr) (proj₂ ab) (proj₂ qr)
  }

------------------------------------------------------------------------
-- It is CONTENTFUL: (q,r)=(0,1) does NOT decompose a=0 against b=1 (0 ≢ 0·1+1=1).
-- So the relation imposes something — a real UP, not the vacuous one.
------------------------------------------------------------------------

wedge-contentful : Contentful wedge-UP
wedge-contentful = (0 , 1) , (0 , 1) , λ ()

wedge-recognized : RecognizedUP
wedge-recognized = record { arrow = wedge-UP ; content = wedge-contentful }

------------------------------------------------------------------------
-- UNIVERSALITY (unique solution) on bounded targets — the no-gauge certificate.
-- Two bounded (q,r) solving the same (a, suc b) coincide. Via BoundedIso.
------------------------------------------------------------------------

wedge-unique : (a b q₁ r₁ q₂ r₂ : ℕ) → r₁ < suc b → r₂ < suc b
             → Witness wedge-UP (a , suc b) (q₁ , r₁)
             → Witness wedge-UP (a , suc b) (q₂ , r₂)
             → (q₁ ≡ q₂) × (r₁ ≡ r₂)
wedge-unique a b q₁ r₁ q₂ r₂ lt₁ lt₂ w₁ w₂ =
  recon-bounded-unique q₁ q₂ b r₁ r₂ lt₁ lt₂ (trans (sym w₁) w₂)
