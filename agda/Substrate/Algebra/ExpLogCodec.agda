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

-- An exp⊣log codec into the multiplicative target (G, _·_, 𝟙) measured by _≈_.
-- `expL` is the "exp" direction (L → G); the homomorphism laws are the content.
record ExpLogCodec {G : Set} (_·_ : G → G → G) (𝟙 : G)
                   (_≈_ : G → G → Set) : Set₁ where
  field
    L     : Set
    _⊕_   : L → L → L            -- L-space addition (the "log" side is additive)
    𝟘     : L                    -- L-space origin (log 𝟙 = 𝟘)
    expL  : L → G                -- exp : L-space → G-space
    -- ·↔+  : multiplication in G is addition in L
    exp-⊕ : (a b : L) → expL (a ⊕ b) ≈ (expL a · expL b)
    -- 𝟙↔𝟘  : the multiplicative unit is the L-space origin
    exp-𝟘 : expL 𝟘 ≈ 𝟙
