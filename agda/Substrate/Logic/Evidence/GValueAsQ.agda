------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueAsQ
--
-- Ω3: the el-atlas Nedge G-Value Calculus ↔ ℚ-Canonical.
--
-- el-atlas (nedge-decomposition.md) defines a G-VALUE as a positive scalar
-- G(P) ∈ (0,∞), with balance point G = 1 (Nedge's L = 0) and the ANTIPODE
-- CONSTRAINT  G(P) · G(¬P) = 1  (a balance channel: G = E⁺/E⁻, and ¬P swaps
-- the rails). The Drive Agda spec `NedgeGCalculus` POSTULATES this scalar and
-- proves no law in Agda (OB-6 / spec line-1987; see Verdict.NedgeShadow).
--
-- Here it is DERIVED, not postulated — the same discipline ℚ-Canonical is for
-- a number system (NedgeShadow's own pointer). A G-value is a POSITIVE ℚ
-- (suc na')/(suc db); balance is 1ℚ; the antipode is the reciprocal (the
-- numerator/denominator swap, total because the value is positive — no
-- division-by-zero); and the antipode constraint G·G(¬P) ≈ 1 is exactly ℚ's
-- multiplicative-inverse law, which here reduces to ℕ-multiplication
-- commutativity. Machine-checked over the ℚ-setoid ≈ℚ (cross-multiplication;
-- the inverse laws are TRUE over ≈ℚ, syntactically false over raw ≡).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueAsQ where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_; _+_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm; *-assoc)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 1ℤ)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-identityˡ; *ℤ-identityʳ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Arithmetic using (_+ℚ_)
open import Substrate.Algebra.Q.Properties.Field using (+ℚ-comm; +ℚ-assoc)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Foundation.Empty using (⊥)

------------------------------------------------------------------------
-- A G-value: a POSITIVE rational scalar (suc na')/(suc db) ∈ (0,∞).
------------------------------------------------------------------------

gvalue : ℕ → ℕ → ℚ
gvalue na' db = mkℚ (+ suc na') db

-- balance point G = 1 (Nedge's L = 0).
balance : ℚ
balance = gvalue 0 0

balance-is-1ℚ : balance ≡ 1ℚ
balance-is-1ℚ = refl

-- the antipode G(¬P): the reciprocal (num/den swap) — total, since G is positive.
antipode-of : ℕ → ℕ → ℚ
antipode-of na' db = gvalue db na'

------------------------------------------------------------------------
-- THE G-VALUE LAW, DERIVED: G(P) · G(¬P) ≈ 1.  NedgeGCalculus postulates this;
-- here it is ℚ's multiplicative inverse, reduced to ℕ *-comm. Not a postulate.
------------------------------------------------------------------------

gvalue-antipode : (na' db : ℕ) → (gvalue na' db *ℚ antipode-of na' db) ≈ℚ 1ℚ
gvalue-antipode na' db =
  trans (*ℤ-identityʳ (+ (suc na' * suc db)))
  (trans (cong +_ (*-comm (suc na') (suc db)))
         (sym (*ℤ-identityˡ (+ (suc db * suc na')))))

------------------------------------------------------------------------
-- The CALCULUS operators (el-atlas "Reciprocal DeMorgan Resource Algebra" =
-- conductance algebra). G_NOT = reciprocal = the antipode above. G_OR =
-- parallel conductance = Σ = ℚ addition (Kirchhoff's parallel rule).
------------------------------------------------------------------------

-- G_OR(G₁,G₂) = G₁ + G₂  (parallel conductance).
gor : ℚ → ℚ → ℚ
gor a b = a +ℚ b

-- commutative + associative over ≈ℚ — the parallel-conductance comm. semigroup
-- (the laws are ℚ's, derived in Q.Properties.Field; here they ARE G_OR's laws).
gor-comm : (a b : ℚ) → gor a b ≈ℚ gor b a
gor-comm = +ℚ-comm

gor-assoc : (a b c : ℚ) → gor (gor a b) c ≈ℚ gor a (gor b c)
gor-assoc = +ℚ-assoc

-- NON-IDEMPOTENT — the calculus's signature (contraction halves / Landauer ±ln2;
-- OR(G,G) = 2G ≉ G). Witnessed at G = 1: 1+1 = 2/1 ≉ 1/1 (would force +2 ≡ +1).
gor-non-idempotent : (gor 1ℚ 1ℚ ≈ℚ 1ℚ) → ⊥
gor-non-idempotent ()

------------------------------------------------------------------------
-- G_NOT as a TOTAL reciprocal (the el-atlas division primitive). The num/den
-- swap; total (the 0 case is junk, never reached by a positive G-value), and
-- the genuine multiplicative inverse for nonzero ℚ. On a positive G-value it
-- IS the antipode, so the inverse law is `gvalue-antipode` (no new proof).
------------------------------------------------------------------------

recip : ℚ → ℚ
recip (mkℚ (+ suc n) d) = mkℚ (+ suc d) n
recip (mkℚ (+ zero)  d) = mkℚ (+ zero) d
recip (mkℚ (-suc n)  d) = mkℚ (-suc d) n

recip-of-gvalue : (na' db : ℕ) → recip (gvalue na' db) ≡ antipode-of na' db
recip-of-gvalue na' db = refl

-- G_AND(G₁,G₂) = G₁·G₂/(G₁+G₂) — series conductance (= 1/Σ(1/Gᵢ)).
gand : ℚ → ℚ → ℚ
gand a b = (a *ℚ b) *ℚ recip (a +ℚ b)

------------------------------------------------------------------------
-- DeMorgan EXACT:  G_NOT(G_OR(G₁,G₂)) ≈ G_AND(G_NOT G₁, G_NOT G₂).
-- Cross-multiplication reduces it to a ℕ identity: the two channel-sums
-- S = n₁d₂ + n₂d₁ and T = d₁n₂ + d₂n₁ agree up to *-comm and +-comm.
------------------------------------------------------------------------

demorgan : (na'₁ db₁ na'₂ db₂ : ℕ) →
           recip (gor (gvalue na'₁ db₁) (gvalue na'₂ db₂))
           ≈ℚ gand (recip (gvalue na'₁ db₁)) (recip (gvalue na'₂ db₂))
demorgan na'₁ db₁ na'₂ db₂ = cong +_ demorgan-ℕ
  where
    n₁ d₁ n₂ d₂ : ℕ
    n₁ = suc na'₁ ; d₁ = suc db₁ ; n₂ = suc na'₂ ; d₂ = suc db₂
    DD NN S T : ℕ
    DD = d₁ * d₂        -- numerator of both sides
    NN = n₁ * n₂
    S  = n₁ * d₂ + n₂ * d₁     -- denom of LHS  (G_OR's numerator)
    T  = d₁ * n₂ + d₂ * n₁     -- the AND-side channel sum
    T≡S : T ≡ S
    T≡S = trans (cong₂ _+_ (*-comm d₁ n₂) (*-comm d₂ n₁)) (+-comm (n₂ * d₁) (n₁ * d₂))
    demorgan-ℕ : DD * (NN * T) ≡ (DD * NN) * S
    demorgan-ℕ = trans (cong (λ z → DD * (NN * z)) T≡S) (sym (*-assoc DD NN S))

------------------------------------------------------------------------
-- SCOPE / status:
--   * DERIVED here: G_NOT (recip/antipode), G_OR (parallel/Σ), G_AND (series,
--     via the total `recip`), their laws, non-idempotence, and DeMorgan EXACT.
--     The whole rational G-space conductance algebra is machine-checked.
--   * L-space (L = ln G; L_OR = LogSumExp; G=1 ↔ L=0): the el-atlas spec
--     (§Identifications.1) says the L↔G isomorphism IS Lemma 2.5b's exp⊣log
--     codec. Per [[feedback_trace_inversion_vs_transcendental_limit]] that codec
--     is a FORMAL coinductive bisimulation (step-inverse generators cancel at
--     every depth — a finite proof of an infinite equality), NOT an analytic
--     ln-VALUE. So L-space is NOT blocked by transcendence (the "transcendental,
--     out-of-scope" reading was an OVERREAD of that lesson): it is a real,
--     buildable bridge — the multiplicative G-space (ℚ₊,·,1) ↔ the additive
--     L-space, the substrate's own exp⊣log codec (Algebra.R) — a genuine
--     follow-on (Ω3-L), not out-of-reach.
------------------------------------------------------------------------
-- ONTO THE CATEGORICAL SPINE (Ⓐ↔Ⓒ.q): gor = +ℚ, whose commutative monoid on
-- the QUOTIENT ℚ/≈ℚ (the reduce-Canonical reps, where the setoid ≈ℚ collapses
-- to propositional ≡) deloops to 𝐁(ℚ,+ℚ) — G_OR on the categorical spine. This
-- is the setoid→spine grounding the categorical-grounding advisory wanted: a
-- typechecked deloop bridge, not a note. (The ≡-monoid is built abstractly over
-- the canonicaliser in Algebra.Q.Properties.AddMonoid — `reduce` runs gcd and
-- does not normalise symbolically, so it is kept abstract; the ℕ⁺-side prime
-- factorisation iso is Ω3-L-primes.)
------------------------------------------------------------------------

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Delooping using (deloop)
open import Substrate.Algebra.Q.Properties.AddMonoid using (+ℚ-reduced-Monoid; ℚ/≈)

gor-Category : CategoryOf ⊤ (λ _ _ → ℚ/≈)
gor-Category = deloop +ℚ-reduced-Monoid
