------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NComplex
--
-- The degree-3 abstract nilpotent carrier — the N-complex `d² ≠ 0, d³ = 0`,
-- the next witness after Mul's square-zero `two-mul` (degree-2, the ordinary
-- differential d²=0). Mul's header names exactly this as the deferred case:
-- "degree n > 2 is an N-complex (d² ≠ 0), the boundary-of-a-boundary that
-- doesn't vanish — the degree the structural WHY the wedge reads off the
-- residue." Abstract (no numerals), in two-mul's style.
--
-- Three = {𝟘, η, sq} with η the differential d: η² = sq ≠ 𝟘 (so η is NOT
-- square-zero — d² ≠ 0, genuinely an N-complex), and η³ = 𝟘 (degree 3). sq is
-- itself square-zero (sq² = 𝟘, degree 2). So the carrier holds residues of
-- VARYING nilpotency degree — the substrate of GRADED coherence (the degree =
-- the cost), which CrossMul defers for lack of a richer common carrier.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.NComplex where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Mul
  using (MulDivStr; pow; Nilpotent; square-zero)

------------------------------------------------------------------------
-- The carrier: 𝟘, the differential η (= d), and its square sq (= d²).
------------------------------------------------------------------------

data Three : Set where
  𝟘 η sq : Three

-- multiplication: 𝟘 absorbs; η·η = sq (= d²); everything reaching grade 3
-- collapses to 𝟘 (η·sq = sq·η = sq·sq = 𝟘 = d³).
mul3 : Three → Three → Three
mul3 𝟘  _  = 𝟘
mul3 η  𝟘  = 𝟘
mul3 η  η  = sq
mul3 η  sq = 𝟘
mul3 sq 𝟘  = 𝟘
mul3 sq η  = 𝟘
mul3 sq sq = 𝟘

three-div : DivStr
three-div = record { C = Three ; z = 𝟘 ; recon = λ _ _ r → r }

three-mul : MulDivStr
three-mul = record { base = three-div ; mul = mul3 }

------------------------------------------------------------------------
-- η is the N-complex differential: d² = η² = sq ≠ 𝟘 (NOT square-zero), yet
-- d³ = η³ = 𝟘. sq is the ordinary square-zero differential (degree 2). The two
-- residues have DIFFERENT nilpotency degree — graded.
------------------------------------------------------------------------

η-not-square-zero : square-zero three-mul η → ⊥   -- d² ≠ 0 : the N-complex signature
η-not-square-zero ()

η-degree-3 : Nilpotent three-mul η                -- η³ = 𝟘 (pow index 2)
η-degree-3 = 2 , refl

sq-degree-2 : Nilpotent three-mul sq              -- sq² = 𝟘 (pow index 1)
sq-degree-2 = 1 , refl
