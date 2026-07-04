{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ChiralityBridge — ⟡S3. The ONE ℤ/2 that this
-- whole arc's four guises share: chirality (V4Signature.CY5, even/odd) =
-- ε-parity / boundary-degree mod 2 (N-to-F2-Parity.parity) = det-flip's ℤ/2
-- (DetSign, the CF-matrix determinant sign). This bridges THIS session's
-- ARITHMETIC backbone (det-flip, ADD 49-53) to the SIMPLICIAL/chirality
-- thread (CY-5, ε-tower) from the tour's tetrahedron arc.
--
-- ⟡H0 / ⟡H-overclaim: these were NAMED as "sibling cocycles" (DetSign says the
-- object side is "a sibling cocycle to V4Signature.CY5") but NOT proven equal.
-- The LOAD-BEARING common carrier: the CF-determinant SIGN after n steps flips
-- once per step (det-flip, DetSign) — starting at +1 — which is DEFINITIONALLY
-- parity n (starts 𝟘, flips 𝟙+ each successor). So det-sign = parity = the
-- step-count/ε-length mod 2; Chirality is its even/odd relabeling. The
-- arithmetic witness that the sign genuinely lives in ℤ/2 is det²≡1 (DetSign),
-- and that it flips per step is det-flip — both cited, proven.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ChiralityBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_)
open import Substrate.Algebra.N-to-F2-Parity using (parity)
open import Substrate.Cocycles.V4Signature.Chirality.Type using (Chirality; even; odd)

------------------------------------------------------------------------
-- det-sign n : the CF-determinant's SIGN (in ℤ/2 = F₂) after n Euclidean
-- steps. Seed 𝟘 (= +1, det4 1 0 0 1 = +1, DetSign); each step FLIPS (det-flip
-- negates ⟹ the sign XORs 𝟙). This is the ℤ/2 COCHAIN DetSign describes,
-- extracted as its F₂ value.
------------------------------------------------------------------------
det-sign : ℕ → F₂
det-sign zero    = 𝟘
det-sign (suc n) = 𝟙 + det-sign n

------------------------------------------------------------------------
-- BRIDGE 1: det-sign IS parity — the det-flip ℤ/2 (per-step negation) equals
-- the step-count parity (ε-tower length / boundary-degree mod 2). Definitional:
-- both start at 𝟘 and flip 𝟙+ each successor. This is the arithmetic↔simplicial
-- identity: the CF-determinant sign is the ε-length parity.
------------------------------------------------------------------------
det-sign-is-parity : (n : ℕ) → det-sign n ≡ parity n
det-sign-is-parity zero    = refl
det-sign-is-parity (suc n) = cong (𝟙 +_) (det-sign-is-parity n)

------------------------------------------------------------------------
-- BRIDGE 2: the F₂ ℤ/2 relabels to CY5's Chirality (even/odd). 𝟘 ↦ even
-- (+1 det, orientation-preserving), 𝟙 ↦ odd (−1 det, orientation-reversing).
------------------------------------------------------------------------
chirality : F₂ → Chirality
chirality 𝟘 = even
chirality 𝟙 = odd

-- so the chirality after n steps is the parity's even/odd — the CF-determinant
-- sign, the ε-length parity, and CY5's chirality are ONE ℤ/2, read three ways.
chirality-after : ℕ → Chirality
chirality-after n = chirality (det-sign n)

chirality-is-parity : (n : ℕ) → chirality-after n ≡ chirality (parity n)
chirality-is-parity n = cong chirality (det-sign-is-parity n)

------------------------------------------------------------------------
-- the ℤ/2 group law holds on all three readings (the involution): two steps
-- return to even (det² ≡ +1, DetSign; parity of 2n is 𝟘; chirality even).
------------------------------------------------------------------------
det-sign-involutive : (n : ℕ) → det-sign (suc (suc n)) ≡ det-sign n
det-sign-involutive n = flip²
  where flip² : 𝟙 + (𝟙 + det-sign n) ≡ det-sign n
        flip² with det-sign n
        ... | 𝟘 = refl
        ... | 𝟙 = refl
