{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- ObsBisim — ⟡FU-sep, via CrossMul + CrossEquality (operator's pointer).
--
-- ADD 99 deferred ⟡FU-sep as "sig_d refines ≈, Böhm-hard / undecidable". That
-- framed separation as a FINITE-DEPTH DECISION — the wrong frame. The substrate
-- already frames it CO-inductively:
--
--   CFInvariance (shape-value-invariance): same VALUE ⟹ same leading QUOTIENT
--     AND a CROSS-EQUATION for the tails (divmod-cross → divmod-unique), recursing.
--   CrossMul: the cross-difference is a GRADED NILPOTENT residue — degree ≤ 1
--     clean (orthogonal), degree n>1 a graded obstruction (dⁿ=0), NEVER an
--     annihilator. The separation DEPTH is the nilpotency degree.
--
-- So the right behavioral equivalence is OBSERVATIONAL BISIMILARITY ≋ (the
-- cross-equation, CrossEquality-shaped = the RealTrace terminal-coalgebra ~,
-- ADD 92): head-observation matches + tails cross-equal, coinductively. This
-- module DEFINES ≋ in the CrossEquality shape and PROVES CONVERSION REFINES IT
-- (≈ ⟹ ≋) by GUARDED COINDUCTION — the exact coinductive form of
-- FUDepth.complete. The finite-probe sig_d is the d-UNFOLDING of ≋; separation
-- of ≉ terms is the nilpotency degree of the cross-difference (CrossMul),
-- finite for productive terms, the undecidable case being the ε-annihilator
-- limit (residue).
--
-- This SUPERSEDES "sig_d refines ≈": sig_d approximates ≋ (the terminal-
-- coalgebra equality, the correct notion), and ≈ ⊆ ≋ is PROVEN here.
------------------------------------------------------------------------

module Substrate.FUSep.ObsBisim where

open import Substrate.Foundation.Eq using (_≡_; refl)
import Substrate.FUSep.ConversionCongruence as ConversionCongruence
open ConversionCongruence using (ARS)

module _ (R : ARS) (Obs : Set) (obs : ARS.Carrier R → Obs)
         (obs-resp : ∀ {a b} → ConversionCongruence._≈_ R a b → obs a ≡ obs b) where
  open ARS R

  _≈_ : Carrier → Carrier → Set
  x ≈ y = ConversionCongruence._≈_ R x y
  ≈-congˡ : ∀ {a a' b} → a ≈ a' → (a · b) ≈ (a' · b)
  ≈-congˡ p = ConversionCongruence.≈-congˡ R p

  ----------------------------------------------------------------------
  -- OBSERVATIONAL BISIMILARITY ≋, in the CrossEquality shape: the HEAD
  -- observations match (obs-eq — the "same leading quotient") AND for EVERY
  -- probe the TAILS cross-equal (tail≋ — the "cross-equation for the tails"),
  -- coinductively. This IS the RealTrace terminal-coalgebra ~ (ADD 92) for the
  -- observation coalgebra t ↦ (obs t , λ p → t · p).
  ----------------------------------------------------------------------
  record _≋_ (a b : Carrier) : Set where
    coinductive
    field
      obs-eq : obs a ≡ obs b
      tail≋  : ∀ (p : Carrier) → (a · p) ≋ (b · p)
  open _≋_ public

  ----------------------------------------------------------------------
  -- THE THEOREM: CONVERSION REFINES OBSERVATIONAL BISIMILARITY (≈ ⟹ ≋), by
  -- GUARDED COINDUCTION. The head is obs-resp (obs is a ≈-invariant — the
  -- "same value ⟹ same quotient" head step); the tail is ≈-congˡ (a ≈ b ⟹
  -- a·p ≈ b·p — the "cross-equation for the tails" threading the value equality
  -- into the next window). This is FUDepth.complete promoted to ALL depths at
  -- once: the cross-equation CLOSES, certifying bisimilarity.
  ----------------------------------------------------------------------
  ≈⟹≋ : ∀ {a b} → a ≈ b → a ≋ b
  obs-eq (≈⟹≋ ab)   = obs-resp ab
  tail≋  (≈⟹≋ ab) p = ≈⟹≋ (≈-congˡ ab)

  ----------------------------------------------------------------------
  -- ≋ is an EQUIVALENCE (a congruence on the observation coalgebra) — the
  -- fold may quotient by it soundly. reflexive/symmetric/transitive, coinductive.
  ----------------------------------------------------------------------
  ≋-refl : ∀ {a} → a ≋ a
  obs-eq ≋-refl   = refl
  tail≋  ≋-refl p = ≋-refl

  ≋-sym : ∀ {a b} → a ≋ b → b ≋ a
  obs-eq (≋-sym r)   = symObs (obs-eq r)
    where symObs : ∀ {x y : Obs} → x ≡ y → y ≡ x
          symObs refl = refl
  tail≋  (≋-sym r) p = ≋-sym (tail≋ r p)

  ≋-trans : ∀ {a b c} → a ≋ b → b ≋ c → a ≋ c
  obs-eq (≋-trans r s)   = transObs (obs-eq r) (obs-eq s)
    where transObs : ∀ {x y z : Obs} → x ≡ y → y ≡ z → x ≡ z
          transObs refl q = q
  tail≋  (≋-trans r s) p = ≋-trans (tail≋ r p) (tail≋ s p)

  -- plain (non-mixfix) accessors (the HetQ lesson).
  bisim-rel : Carrier → Carrier → Set
  bisim-rel a b = a ≋ b
  bisim-obs : ∀ {a b} → bisim-rel a b → obs a ≡ obs b
  bisim-obs r = obs-eq r
  bisim-refl : ∀ {a} → bisim-rel a a
  bisim-refl = ≋-refl
  bisim-sym : ∀ {a b} → bisim-rel a b → bisim-rel b a
  bisim-sym = ≋-sym
  bisim-trans : ∀ {a b c} → bisim-rel a b → bisim-rel b c → bisim-rel a c
  bisim-trans = ≋-trans
  bisim-fwd : ∀ {a b} → ConversionCongruence._≈_ R a b → bisim-rel a b
  bisim-fwd = ≈⟹≋
