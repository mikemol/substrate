{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderMiscRealigned — ⟡tower-realign-misc: the LAST
-- realignment cluster. THREE clean instantiations + ONE genuine reframe.
--
-- Rosetta (ADD 123, judgment-marked ADD 127):
--   FoldUnfold  (#1) → WitnessTower.EEAFoldTable (eea-fold, the catamorphism)   [instantiate]
--   FUSepConv   (#5) → R.Trace.RationalAdjunction (ℚ⊣R, unit on finite image)   [instantiate]
--   FUSepQ      (#6) → Nat.GCD.CFInvariance.shape-value-invariance (bt-reflect)  [instantiate]
--   FUDepth     (#3) → RealTrace.take (the finite CF prefix = sig_d)             [REFRAME]
--
-- FUDepth is NOT an instance of a named lemma — it is a REFRAME: my sigOf/sig_d
-- (the depth-d probe signature) IS RealTrace.take (the depth-n CF prefix), and my
-- "sigOf-mono (deeper determines shallower)" is just that take yields a PREFIX
-- (definitional, no standalone lemma). sig_d = the d-unfolding of ≋ (Bisim), the
-- finite ana-prefix. Marked honestly: reframe, not reinvention-of-a-center.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderMiscRealigned where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)

------------------------------------------------------------------------
-- ① FoldUnfold IS the EEA fold-table. My free-unfold ⊣ aggressive-fold matched
-- pair (filter-sound, rep-closure) is eea-fold: ONE EEA trace read through its
-- folds (the catamorphism), the fold TARGET picking the structure. The ad-hoc
-- filter-soundness is the fold's own uniqueness (a fold over the universal EEA
-- generator). Referenced by center:
------------------------------------------------------------------------
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.Fold using (eea-fold)
-- (the ad-hoc FoldUnfold's fold IS eea-fold; the free/aggressive pair is the
--  catamorphism over the EEA trace, the universal generator. gcd-ℕ = a fold.)
fold-witness : gcd-ℕ 3 2 ≡ 1
fold-witness = refl

------------------------------------------------------------------------
-- ② FUSepConv IS the ℚ⊣R adjunction. My ≋⟹≈-on-finite-image (the adjunction
-- unit coinciding on the finite image, unit-id-on-finite) is RationalAdjunction:
-- ℚ→R = ana qStep (forced by ana-unique), R→ℚ = convergent, unit ℚ→R→ℚ = id (a
-- rational reconstructs from its CF prefix, refl). Referenced by center:
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.RationalAdjunction using (qToR; unit-3/2)
-- (the ad-hoc FUSepConv unit IS RationalAdjunction's unit ℚ→R→ℚ = id, WITNESSED by
--  unit-3/2 : convergent 2 (qToR 3 1) ≡ (3 , 2) — a rational reconstructs from its
--  CF prefix. ℚ→R = ana qStep, R→ℚ = convergent (Trace); the finite image is ℚ.)
-- unit-3/2 (imported) IS the adjunction unit witness; no re-statement needed.

------------------------------------------------------------------------
-- ③ FUSepQ IS bt-reflect = CFInvariance.shape-value-invariance. My "on finite
-- Böhm trees ≋ collapses to ≡ by structural induction" IS shape-value-invariance:
-- same value (a*d ≡ c*b) ⟹ same shape (ℕ-shape t₁ ≡ ℕ-shape t₂), over EEATrace,
-- by structural induction with the divmod-cross head step. Referenced by center:
------------------------------------------------------------------------
open import Substrate.Algebra.Nat.GCD.CFInvariance using (shape-value-invariance)
-- (the ad-hoc FUSepQ.bt-reflect IS shape-value-invariance — the CFInvariance
--  cross-equation shape I explicitly cited when building it, ADD 102.)

------------------------------------------------------------------------
-- ④ FUDepth — THE REFRAME. sig_d = RealTrace.take (the finite CF prefix). My
-- sigOf(t) at depth d IS take d (the first d CF digits / observations); my
-- sigOf-mono ("a deeper sig determines a shallower one") is that take yields a
-- PREFIX — take n is take (suc n) truncated. This is definitional on take, NOT a
-- named lemma. So FUDepth is a reframe: the law-depth machinery is the finite
-- ana-prefix of the terminal-coalgebra observation (Bisim/Final).
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail; take; convergent)

-- sigOf IS take: the depth-d signature is the depth-d CF prefix.
sigOf : ℕ → RealTrace → _
sigOf = take

-- sigOf-mono (deeper determines shallower), REFRAMED: take (suc n) begins with
-- take n's data — the shallower prefix is the head of the deeper. Definitional:
-- take (suc n) r = head r ∷ take n (tail r), so take n (tail r) is a sub-prefix.
sigOf-step : (n : ℕ) (r : RealTrace) → take (suc n) r ≡ head r ∷ take n (tail r)
sigOf-step n r = refl

------------------------------------------------------------------------
-- THE COLLAPSE (the LAST cluster): FoldUnfold = eea-fold, FUSepConv = ℚ⊣R,
-- FUSepQ = shape-value-invariance, FUDepth = take (reframe). 4 ad-hoc modules →
-- 3 named centers + 1 reframe (take). The tower's "fold soundness / finite
-- adjunction / bt-reflect / law-depth" IS the EEA fold-table + ℚ⊣R + CFInvariance
-- + the finite CF prefix — the substrate's rational-approximation machinery.
------------------------------------------------------------------------
