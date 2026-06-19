------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterIsStarProjective  (Ξ★.ℙ)
--
-- The PROJECTIVE center↔periphery EXCHANGE — the §5 radial fold, the residual
-- Ξ★.2/Ξ★.3 flagged. There the affine ℚ recip FIXES the open circuit
-- (recip 0ℚ ≡ 0ℚ, the total junk clause), so ★ could not EXCHANGE centre and
-- periphery: affine ℚ has no point at infinity to swap 0 with.
--
-- The fix is to stop collapsing the G-value to an affine ℚ and keep it as the
-- HOMOGENEOUS PAIR [n : d] it actually is (POINT_CLOUD §0: "a G-value is the
-- class of a formal-quotient pair (n,d), class G = n/d") — i.e. work on ℙ¹.
-- There ★ = G_NOT = the swap genuinely EXCHANGES the two ends:
--   centre [0:1] = G→0 (open circuit, witness)  ↔  inf [1:0] = G→∞ (short
--   circuit, periphery),   fixing bal [1:1] = G=1.
--
-- This RESOLVES the tension: GValueAsQ.recip is the AFFINE chart (it sees 0 but
-- not ∞, so it fixes 0); ★p here is the PROJECTIVE fold (it sees both ends and
-- swaps them). The centre and periphery are DISTINCT projective points
-- (centre ≉ℙ inf : 0 ≢ 1), so the exchange is non-trivial — the §5 "★ is the
-- radial fold exchanging centre and periphery" is now witnessed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterIsStarProjective where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Empty using (⊥)

------------------------------------------------------------------------
-- ℙ¹ over the G-value pairs: homogeneous coords [n : d], up to cross-mult.
------------------------------------------------------------------------

GP : Set
GP = ℕ × ℕ                                   -- [n : d]

_≈ℙ_ : GP → GP → Set
(n , d) ≈ℙ (n' , d') = n * d' ≡ n' * d        -- [n:d] = [n':d'] iff n·d' = n'·d
infix 4 _≈ℙ_

-- ★ = G_NOT = the swap (conductance↔resistance, series↔parallel).
★p : GP → GP
★p (n , d) = (d , n)

-- the three distinguished points: centre (witness), periphery (∞), balance.
centre inf bal : GP
centre = (0 , 1)        -- G → 0 : open circuit, the witness / centre
inf    = (1 , 0)        -- G → ∞ : short circuit, the periphery
bal    = (1 , 1)        -- G = 1 : the self-dual balance

------------------------------------------------------------------------
-- ★ is an involution and is well-defined on ℙ¹ (respects ≈ℙ).
------------------------------------------------------------------------

★p-involution : (p : GP) → ★p (★p p) ≡ p
★p-involution (n , d) = refl

★p-respects-≈ℙ : (p q : GP) → p ≈ℙ q → ★p p ≈ℙ ★p q
★p-respects-≈ℙ (n , d) (n' , d') h =
  trans (*-comm d n') (trans (sym h) (*-comm n d'))

------------------------------------------------------------------------
-- §5 — THE RADIAL FOLD: ★ EXCHANGES centre (G→0, witness) and periphery
-- (G→∞), and fixes the balance. The exchange is non-trivial: the two ends are
-- DISTINCT projective points.
------------------------------------------------------------------------

★p-exchanges-centre-periphery : (★p centre ≡ inf) × (★p inf ≡ centre)
★p-exchanges-centre-periphery = refl , refl

★p-fixes-balance : ★p bal ≡ bal
★p-fixes-balance = refl

centre-≉ℙ-inf : centre ≈ℙ inf → ⊥        -- 0·0 ≡ 1·1 i.e. 0 ≡ 1 : impossible
centre-≉ℙ-inf ()
