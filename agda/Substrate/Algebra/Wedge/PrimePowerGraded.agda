------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.PrimePowerGraded
--
-- ⟡odecode-godel-graded (TIER A): the PRIME-DIGIT rung as an explicit graded
-- wedge-carrier (Algebra.Wedge.Graded) — the multiplicative-first reading of ℕ,
-- made a GradedDivStr next to the factoradic `tower-graded` (Perm/insert-at) and
-- `vec-graded` (Vec/cons). The grade is the number of prime digits; the shed
-- residue at each step is a PRIME (IsPrime-witnessed):
--   C n     = length-n prime-digit lists  (Σ (List ℕ) (AllPrime × length ≡ n))
--   R n     = a prime  (Σ ℕ IsPrime)       the digit to shed / prepend
--   recon n = cons the prime onto the grade-n tail (extend AllPrime + length)
--
-- THE SINGLE DIFFERENTIATOR from `vec-graded ℕ` (which this would otherwise BE,
-- verbatim) is the `AllPrime` refinement: each digit carries `IsPrime`. That
-- de-hollows the instance WITHOUT any forward `pₙ : ℕ→ℕ` (no nth-prime — the
-- repo is multiplicative-first: N is PRIMARY as a product ∏pᵢ = the ANTILOG;
-- the additive view is reached by LOG = factorize!). The antilog readout is
-- literally `Algebra.Nat.Prime.product`.
--
-- THE ROUND-TRIP + UNIFICATIONS ARE REUSE, not re-proven here (TIER A cites):
--   * log / antilog round-trip:  `factorize!` (the log, Prime.Properties:190),
--     `product` (the antilog, Prime:32), `factor-section`/`factor-retract`
--     (Prime.Properties:257,261) and the ℕ⁺≅prime-code split-idempotent
--     `factor-Canonical` (same apex as UPTerm-Canonical/TmDB-Canonical).
--     `pp-forget` (below) exhibits every graded prime-vector AS a `Factored` of
--     its value — the surjectivity target factorize! inhabits.
--   * the +↔× value hom:  `ExpLogCodec` instantiated at `ℤ-power-codec`
--     (Logic.Evidence.GValueLSpace.Primes:209).
--   * the structure-direction (Vec→Perm) morphism:  `PackedBridge.packed→witness`
--     (respects-recon = refl).
--   * the ×↔^ log:  CF/EEA/CRT — `RealTrace` CF stream, `EEAFoldTable`.
-- The hyperoperation ladder is centered at ×: + (below, via LOG) — × (this rung,
-- product) — ^ (above, exponents). SCOPED OUT of TIER A: nth-prime / the pₙ^r
-- Horner (the retired ^-rung); the coinductive exp∘log~x general case; a
-- MixedRadix apex (TIER B — the residue-carrying cross-radix morphism — is a
-- separate sub-arc, not built here).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.PrimePowerGraded where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.Nat.Prime
  using (IsPrime; AllPrime; []ᴾ; _∷ᴾ_; product; Factored)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr; recon)

------------------------------------------------------------------------
-- 1. The graded prime-digit carrier and the prime residue.
------------------------------------------------------------------------

-- C n = length-n lists of primes (the AllPrime refinement is the differentiator).
C : ℕ → Set
C n = Σ (List ℕ) (λ ps → AllPrime ps × (length ps ≡ n))

-- R n = a prime digit (grade-independent — the shed residue).
R : ℕ → Set
R _ = Σ ℕ IsPrime

------------------------------------------------------------------------
-- 2. pp-graded : GradedDivStr C R — recon IS cons (prepend the prime digit,
--    extend the AllPrime witness and the length index).
------------------------------------------------------------------------

pp-recon : (n : ℕ) → C n → R n → C (suc n)
pp-recon n (ps , ap , lp) (p , ip) = (p ∷ ps) , (ip ∷ᴾ ap) , cong suc lp

pp-graded : GradedDivStr C R
pp-graded = record { recon = pp-recon }

-- recon IS cons, definitionally.
pp-recon-is-cons : (n : ℕ) (c : C n) (r : R n) →
                   proj₁ (recon pp-graded n c r) ≡ (proj₁ r ∷ proj₁ c)
pp-recon-is-cons n (ps , _ , _) (p , _) = refl

------------------------------------------------------------------------
-- 3. The antilog readout = Prime.product, and its multiplicative bridge.
------------------------------------------------------------------------

-- pp-value = the ANTILOG: the product of the prime digits (= Prime.product).
pp-value : {n : ℕ} → C n → ℕ
pp-value (ps , _ , _) = product ps

-- the value bridge: reconstructing shed-digit p multiplies the value by p.
-- (product (p ∷ ps) = p * product ps, definitionally — the antilog is a ×-hom.)
pp-recon-value : (n : ℕ) (c : C n) (r : R n) →
                 pp-value (recon pp-graded n c r) ≡ (proj₁ r * pp-value c)
pp-recon-value n (ps , _ , _) (p , _) = refl

------------------------------------------------------------------------
-- 4. Every graded prime-vector IS a `Factored` of its value — the surjectivity
--    target `factorize!` inhabits (the round-trip is REUSE via factor-Canonical).
------------------------------------------------------------------------

pp-forget : {n : ℕ} (c : C n) → Factored (pp-value c)
pp-forget (ps , ap , _) = ps , ap , refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the prime-power rung is the SAME graded wedge
-- `a = recon q b r` as the factoradic tower and the Vec carrier — recon = cons,
-- residue = a prime digit, antilog = product. The multiplicative-first ℕ
-- (product PRIMARY, log = factorize!) is one point on the hyperoperation ladder
-- centered at ×; the round-trip and the +↔×/×↔^ unifications ALREADY EXIST
-- (factor-Canonical, ℤ-power-codec, EEAFoldTable, PackedBridge) — TIER A makes
-- the graded prime rung explicit and cites them; it does NOT re-prove them, does
-- NOT build nth-prime, and does NOT build the TIER-B cross-radix morphism.
------------------------------------------------------------------------
