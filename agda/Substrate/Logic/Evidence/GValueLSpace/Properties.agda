------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace.Properties
--
-- Ω3-L theorems (the proof sibling of `GValueLSpace`):
--   * codec-antipode -- L-space additive inverse ↦ G-space multiplicative
--     antipode; EXHIBITS the el-atlas G·G(¬P)≈1 as the codec image of
--     a+(−a)=0 (recip↔neg).
--   * ℕ-power-codec  -- a concrete inhabiting witness (base powers gⁿ),
--     `exp-⊕` by induction; proves the codec interface is non-vacuous.
--   * balance-self-antipode -- a concrete firing of codec-antipode.
--
-- ℚ implicits are pinned throughout: `_≈ℚ_` is a transparent definition
-- (it unfolds to a ℤ `≡`), so the `≈ℚ-sym`/`≈ℚ-trans`/`*ℚ-cong` middle
-- terms are not inferable from their proof arguments and must be given.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.Q using (ℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Properties.Field using (*ℚ-assoc; *ℚ-identityˡ)
open import Substrate.Algebra.Q.Properties.Congruence using (*ℚ-cong)
open import Substrate.Logic.Evidence.GValueLSpace
  using (ExpLogCodec; powℚ)

------------------------------------------------------------------------
-- ≡ coerces into ≈ℚ (the codec law transports propositional equality of
-- L-space elements through `expL`).
------------------------------------------------------------------------

≡→≈ℚ : {a b : ℚ} → a ≡ b → a ≈ℚ b
≡→≈ℚ {a} refl = ≈ℚ-refl a

------------------------------------------------------------------------
-- DERIVED: the antipode.  Whenever an L-space element `a` has an additive
-- inverse `aⁱ` (a ⊕ aⁱ = 𝟘), its image `expL a` has a MULTIPLICATIVE
-- inverse `expL aⁱ` in G-space:  expL a · expL aⁱ ≈ 1.
--
-- This is exactly the el-atlas antipode constraint G(P)·G(¬P) ≈ 1
-- (`GValueAsQ.gvalue-antipode`), here EXHIBITED as the codec image of
-- L-space's additive inverse a + (−a) = 0 — the structural reason G_NOT is
-- a reciprocal. (recip↔neg.)
------------------------------------------------------------------------

module _ (C : ExpLogCodec) where
  open ExpLogCodec C

  codec-antipode : (a aⁱ : L) → (a ⊕ aⁱ) ≡ 𝟘 →
                   (expL a *ℚ expL aⁱ) ≈ℚ 1ℚ
  codec-antipode a aⁱ inv =
    ≈ℚ-trans {expL a *ℚ expL aⁱ} {expL (a ⊕ aⁱ)} {1ℚ}
      (≈ℚ-sym {expL (a ⊕ aⁱ)} {expL a *ℚ expL aⁱ} (exp-⊕ a aⁱ))
      (≈ℚ-trans {expL (a ⊕ aⁱ)} {expL 𝟘} {1ℚ}
        (≡→≈ℚ {expL (a ⊕ aⁱ)} {expL 𝟘} (cong expL inv))
        exp-𝟘)

------------------------------------------------------------------------
-- A CONCRETE WITNESS: the base-power codec.  For a fixed base g : ℚ,
-- expL n = gⁿ is a monoid hom (ℕ, +, 0) → (ℚ, *ℚ, 1ℚ).  This inhabits
-- `ExpLogCodec`, so the interface is non-vacuous: the structural codec is
-- not merely a proposal, it EXISTS and is machine-checked over ≈ℚ.
------------------------------------------------------------------------

-- exponents add when powers multiply:  g^(m+n) ≈ gᵐ · gⁿ.
pow-+ : (g : ℚ) (m n : ℕ) → powℚ g (m + n) ≈ℚ (powℚ g m *ℚ powℚ g n)
pow-+ g zero    n =
  ≈ℚ-sym {1ℚ *ℚ powℚ g n} {powℚ g n} (*ℚ-identityˡ (powℚ g n))
pow-+ g (suc m) n =
  ≈ℚ-trans {g *ℚ powℚ g (m + n)}
           {g *ℚ (powℚ g m *ℚ powℚ g n)}
           {(g *ℚ powℚ g m) *ℚ powℚ g n}
    (*ℚ-cong {g} {g} {powℚ g (m + n)} {powℚ g m *ℚ powℚ g n}
             (≈ℚ-refl g) (pow-+ g m n))
    (≈ℚ-sym {(g *ℚ powℚ g m) *ℚ powℚ g n}
            {g *ℚ (powℚ g m *ℚ powℚ g n)}
            (*ℚ-assoc g (powℚ g m) (powℚ g n)))

ℕ-power-codec : ℚ → ExpLogCodec
ℕ-power-codec g = record
  { L     = ℕ
  ; _⊕_   = _+_
  ; 𝟘     = zero
  ; expL  = powℚ g
  ; exp-⊕ = pow-+ g
  ; exp-𝟘 = ≈ℚ-refl 1ℚ
  }

-- The codec fires: the balance point is its own antipode (0 + 0 = 0 in L
-- ↦ 1 · 1 ≈ 1 in G).  A concrete, non-vacuous use of `codec-antipode`.
balance-self-antipode : (g : ℚ) →
  (powℚ g zero *ℚ powℚ g zero) ≈ℚ 1ℚ
balance-self-antipode g = codec-antipode (ℕ-power-codec g) zero zero refl

------------------------------------------------------------------------
-- SCOPE / status (proposal, not claim — the prose below names follow-ons,
-- it does not assert theorems this module proves):
--   * PROVEN here: the antipode as the codec image of L-additive-inverse
--     (recip↔neg, derived for ANY codec); and a concrete inhabiting witness
--     (base powers), exp-⊕ by induction.
--   * `codec-antipode` has the SAME shape as `GValueAsQ.gvalue-antipode`
--     (x *ℚ x⁻¹ ≈ 1ℚ). Ω3-L-primes GROUNDING (2026-06-20, test-the-wall +
--     crossmix-dual): the "needs unique factorisation, heavy" framing was wrong
--     twice over. The build splits into TWO layers, and the antipode core is
--     NOT raw ℚ-arithmetic — it is the Ⓖ★-DUAL of the cross-mixer:
--       (1) ANTIPODE CORE = the INVERTIBLE pole of `Wedge.CrossMul`. CrossMix
--           coherence is the cross term → z (the multiplicative ZERO), i.e.
--           NILPOTENT/orthogonal (CRT's e₁·e₂=0). The codec antipode is the
--           cross term → 1 (the multiplicative UNIT), i.e. INVERTIBLE — these
--           are the TWO species of the Ⓖ★ genus (`Algebra.Wedge.Species`:
--           idempotent/nilpotent ∪ invertible). So `expL a *ℚ expL aⁱ ≈ 1`
--           (a⊕aⁱ=𝟘) is the invertible-pole cross-coherence, the dual of
--           `CrossMul.Coherent` (= Nilpotent). The clean structure is therefore
--           a `MulDivStr` enriched with a UNIT+inverse (the group pole) — the
--           sideways twin of the nilpotent `MulDivStr` — with ℚ₊ as the
--           instance; recip-multiplicative + a·a⁻¹=1 are then its group laws,
--           NOT hand-proved over the den-1 ℚ rep, and NO factorisation. (L must
--           be a GROUP: the ℕ base-power codec above is a monoid, fires only at
--           0+0; the ℤ-power codec L=ℤ, expL n = gⁿ is the rank-1 group case.)
--       (2) SURJECTIVITY — "image = EXACTLY the positive gvalues" + the "log"
--           inverse (⇒ G_OR = +ℚ becomes L_OR = LogSumExp, expL⁻¹∘+ℚ∘expL) is
--           the only part that genuinely needs the free abelian group on primes
--           ℚ₊ ≅ ⊕ℤ + UNIQUE FACTORISATION (FTA). GROUNDED 2026-06-20: NO
--           factorisation-into-primes existence/uniqueness proof is present in
--           the tree (GCD/Bezout/Coprime exist; FTA does not) — it is a heavy
--           FROM-SCRATCH number-theory arc (prime enumeration + factor-by-strong-
--           induction + uniqueness), genuinely deferred (an EFFORT wall, not an
--           impossibility — Ω4 class (c)).
--     STATUS — layer (1) FULLY BUILT in `GValueLSpace.Primes`, NO FTA:
--       * rank-1 invertible pole: `gvalue-power-antipode` (gᵏ·(recip g)ᵏ≈1, the
--         el-atlas antipode on the cyclic subgroup ⟨g⟩);
--       * rank-n invertible pole: `prod-cancel` (∏gᵢ·∏hᵢ≈1, the free abelian
--         group on n G-value generators — each ∏gᵢ^kᵢ inverted by ∏hᵢ^kᵢ);
--       * the codec INTERFACE: `ZPow.ℤ-power-codec` — L=ℤ a GROUP via `_+ℤ_`,
--         expL z = gᶻ (negatives ↦ hⁿ), exp-⊕ over the mixed-sign `_⊖_`
--         cancellation (`mix`), so `codec-antipode` fires NON-trivially through
--         the ExpLogCodec interface (g¹·h¹≈1, `ZPow.ℤpow-antipode-fires`); and
--         `gvalue-ℤ-codec` is the el-atlas instance. (This is the GROUP twin of
--         the `ℕ-power-codec` MONOID above — the rank-1 group, vs the cyclic
--         monoid that fires only at 0.)
--     REMAINING — ONLY layer (2): the FTA surjectivity/LogSumExp tail (image =
--     EXACTLY ℚ₊ + the "log" inverse). GROUNDED 2026-06-20: FTA is ABSENT from
--     the tree, a HEAVY from-scratch number-theory arc (Ω4 class (c), effort wall
--     not impossibility). The rank-1 ℕ base-power codec above is exact and
--     complete at its scope, not an approximation of any of these.
------------------------------------------------------------------------
