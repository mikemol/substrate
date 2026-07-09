------------------------------------------------------------------------
-- Substrate.Algebra.ExpLogCodec
--
-- The carrier-GENERIC exp⊣log codec: a monoid homomorphism from an additive
-- L-space (L, ⊕, 𝟘) into ANY multiplicative target (G, ·, 𝟙) up to ≈.
--
-- This is the STRUCTURAL content of g-calculus's additive→multiplicative
-- bridge ("exponents add when powers multiply" — `exp(a⊕b) = exp a · exp b`,
-- `exp 𝟘 = 𝟙`, base-independent), lifted OFF ℚ so that the `Algebra` tower
-- (a field's `mul-inv` as `exp∘neg∘log`; the Singer `GF(2ⁿ)*` codec) can be
-- GROUNDED on it by construction — the recurring "where does the multiplicative
-- structure come from" nexus made a first-class algebra citizen, not an
-- evidence-logic detail (`Logic.Evidence.GValueLSpace`, which now DERIVES its
-- ℚ codec as the instance `ExpLogCodec _*ℚ_ 1ℚ _≈ℚ_`).
--
-- No analytic value is referenced: the homomorphism laws ARE the codec; the
-- VALUE/log projection (the digits of ln) is the only transcendental part and
-- lives elsewhere (`Algebra.R.Trace.*`, deferred as the bisimulation `~`).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.ExpLogCodec where

open import Substrate.Foundation.Eq using (_≡_; cong)

-- An exp⊣log codec into the multiplicative target (G, _·_, 𝟙) measured by _≈_.
-- `expL` is the "exp" direction (L → G); the homomorphism laws are the content.
-- ⟡set1-paydown: parameterize L (the additive L-space carrier was a `L : Set`
-- field, forcing Set₁; taking it as the module parameter keeps the record in Set,
-- and the CONSUMER names it: `ExpLogCodec L _·_ 𝟙 _≈_`).
module _ (L : Set) where
  record ExpLogCodec {G : Set} (_·_ : G → G → G) (𝟙 : G)
                     (_≈_ : G → G → Set) : Set where
    field
      _⊕_   : L → L → L            -- L-space addition (the "log" side is additive)
      𝟘     : L                    -- L-space origin (log 𝟙 = 𝟘)
      expL  : L → G                -- exp : L-space → G-space
      -- ·↔+  : multiplication in G is addition in L
      exp-⊕ : (a b : L) → expL (a ⊕ b) ≈ (expL a · expL b)
      -- 𝟙↔𝟘  : the multiplicative unit is the L-space origin
      exp-𝟘 : expL 𝟘 ≈ 𝟙

------------------------------------------------------------------------
-- recip↔neg : the additive→multiplicative INVERSE grounding (el-atlas
-- Lemma 2.4). When the codec's L-space carries a negation with
-- `x ⊕ neg x ≡ 𝟘`, every image element `expL x` is a UNIT — its
-- multiplicative inverse is `expL (neg x)`. The reciprocal involution IS
-- the additive negation transported by exp; no multiplicative-inverse
-- axiom is needed, it is DERIVED. This is the structural source a field's
-- `mul-inv` grounds on (`a⁻¹ = exp(neg(log a))`); finite/exponent codecs
-- (L = ℤ, ℤ/n — propositional ≡) are the target (Ⓐ.gfinv-dlog).
------------------------------------------------------------------------

module Inverse
  {L : Set}
  {G : Set} {_·_ : G → G → G} {𝟙 : G} {_≈_ : G → G → Set}
  (≈-sym       : {a b : G} → a ≈ b → b ≈ a)
  (≈-trans     : {a b c : G} → a ≈ b → b ≈ c → a ≈ c)
  (≈-reflexive : {a b : G} → a ≡ b → a ≈ b)
  (C : ExpLogCodec L _·_ 𝟙 _≈_)
  (neg  : L → L)
  (invˡ : (x : L) →
          (ExpLogCodec._⊕_ C) x (neg x) ≡ ExpLogCodec.𝟘 C)
  where
  open ExpLogCodec C

  -- THE recip↔neg THEOREM: expL x is a unit, inverse expL(neg x).
  codec-inverse : (x : L) → (expL x · expL (neg x)) ≈ 𝟙
  codec-inverse x =
    ≈-trans (≈-sym (exp-⊕ x (neg x)))
            (≈-trans (≈-reflexive (cong expL (invˡ x))) exp-𝟘)
