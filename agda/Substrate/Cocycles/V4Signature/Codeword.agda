------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword
--
-- The 24+8 = 32 = 2⁵ codeword ambient — the catalog's "raw codeword
-- space" reading of CY-5's signature structure, formalised under the
-- multi-reading ambient discipline.
--
-- Discipline (applied here, see catalog clarification 2026-05-15):
--
--   * The ambient is the largest natural cardinality: 32 codewords
--     as Bool⁵.
--   * The load-bearing structural commitment is a decidable
--     predicate IsReserved : Codeword → Set carving out the 8.
--   * "Live" (the 24) is Σ Codeword (¬ ∘ IsReserved); "Reserved"
--     (the 8) is Σ Codeword IsReserved. Both are derived.
--   * Each "reading" of the 32+8 structure is a separate
--     equivalence: Reserved ↔ Axis × Bool (signed singletons,
--     this module), Live ↔ Permutation (= S_4, follow-on),
--     Hodge swap at dim 4 (follow-on). None is privileged.
--
-- This module provides:
--   * The ambient (Codeword, IsReserved, Live, Reserved).
--   * Decidability of IsReserved.
--   * The FIRST reading: Reserved ↔ Axis × Bool — the signed-
--     singletons / Hodge 1-form layer.
--
-- Bit encoding (a CONVENTION — multiple equivalent encodings exist):
--
--   b₀ b₁  | axis (4 options)            D = (false, false)
--                                        C = (true,  false)
--                                        S = (false, true)
--                                        W = (true,  true)
--
--   b₂     | reserved: sign (2 options)
--          | live: contributes to ordering selector
--
--   b₃ b₄  | (false, false) = reserved   (IsReserved cw)
--          | otherwise      = live
--
-- See:
--   * catalog/cocycles.md § CY-5 — 24+8 reading
--   * [[feedback-multi-reading-ambient-discipline]] — the discipline
--     rule this slice applies (no privileged definition)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword where

open import Level using (0ℓ)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂; Σ; Σ-syntax)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Bijection using (_↔_; mk↔ₛ′)

open import Substrate.Axes using (Axis; D; C; S; W)

------------------------------------------------------------------------
-- Ambient: 32 codewords as Bool⁵.
------------------------------------------------------------------------

Codeword : Set
Codeword = Bool × Bool × Bool × Bool × Bool

-- Bit accessors.
bit₀ bit₁ bit₂ bit₃ bit₄ : Codeword → Bool
bit₀ (x , _ , _ , _ , _) = x
bit₁ (_ , x , _ , _ , _) = x
bit₂ (_ , _ , x , _ , _) = x
bit₃ (_ , _ , _ , x , _) = x
bit₄ (_ , _ , _ , _ , x) = x

------------------------------------------------------------------------
-- IsReserved — the load-bearing decidable predicate.
--
-- Reserved iff the high-two bits are both zero. Equivalent to "the
-- codeword's ordering-selector is in the {signed-singleton}
-- subspace rather than the {ordered-triple} subspace."
------------------------------------------------------------------------

IsReserved : Codeword → Set
IsReserved cw = (bit₃ cw ≡ false) × (bit₄ cw ≡ false)

isReserved? : (cw : Codeword) → Dec (IsReserved cw)
isReserved? (_ , _ , _ , false , false) = yes (refl , refl)
isReserved? (_ , _ , _ , true  , false) = no (λ { (() , _) })
isReserved? (_ , _ , _ , false , true)  = no (λ { (_ , ()) })
isReserved? (_ , _ , _ , true  , true)  = no (λ { (() , _) })

------------------------------------------------------------------------
-- Derived subtypes: Reserved (8) and Live (24).
--
-- These are NOT primary data types — they are Σ-type wrappers around
-- the ambient. Per discipline, no constructor-based enumeration is
-- introduced for either; the ambient + predicate is the structural
-- commitment.
------------------------------------------------------------------------

Reserved : Set
Reserved = Σ Codeword IsReserved

Live : Set
Live = Σ Codeword (λ cw → ¬ IsReserved cw)

------------------------------------------------------------------------
-- First reading: Reserved ↔ Axis × Bool.
--
-- The 8 reserved codewords correspond bijectively to (axis, sign)
-- pairs — the "signed singletons" or "Hodge 1-form basis × sign"
-- at dim 4. (Bits b₀b₁ encode the axis; bit b₂ encodes the sign;
-- bits b₃b₄ are the reserved-marker = (false, false).)
------------------------------------------------------------------------

axis-from-bits : Bool → Bool → Axis
axis-from-bits false false = D
axis-from-bits true  false = C
axis-from-bits false true  = S
axis-from-bits true  true  = W

axis-to-bits : Axis → Bool × Bool
axis-to-bits D = false , false
axis-to-bits C = true  , false
axis-to-bits S = false , true
axis-to-bits W = true  , true

-- axis-bits round-trip lemmas.
axis-bits-id :
  (a : Axis) →
  axis-from-bits (proj₁ (axis-to-bits a)) (proj₂ (axis-to-bits a)) ≡ a
axis-bits-id D = refl
axis-bits-id C = refl
axis-bits-id S = refl
axis-bits-id W = refl

bits-axis-id :
  (b₀v b₁v : Bool) →
  axis-to-bits (axis-from-bits b₀v b₁v) ≡ (b₀v , b₁v)
bits-axis-id false false = refl
bits-axis-id true  false = refl
bits-axis-id false true  = refl
bits-axis-id true  true  = refl

------------------------------------------------------------------------
-- The bidirectional maps.
------------------------------------------------------------------------

reserved-to-signed : Reserved → Axis × Bool
reserved-to-signed ((b₀v , b₁v , b₂v , _ , _) , _) =
  axis-from-bits b₀v b₁v , b₂v

signed-to-reserved : Axis × Bool → Reserved
signed-to-reserved (a , sign) =
  (proj₁ (axis-to-bits a) , proj₂ (axis-to-bits a) , sign , false , false)
  , (refl , refl)

------------------------------------------------------------------------
-- Round-trip proofs.
--
-- The forward round-trip is by case analysis on Axis (4 cases).
-- The reverse round-trip is by case analysis on the bit pattern
-- (4 × 1 = 4 cases) plus pinning b₃ and b₄ to false via dot-patterns
-- matching the IsReserved proof.
------------------------------------------------------------------------

signed-reserved-leftinv :
  (xy : Axis × Bool) →
  reserved-to-signed (signed-to-reserved xy) ≡ xy
signed-reserved-leftinv (D , _) = refl
signed-reserved-leftinv (C , _) = refl
signed-reserved-leftinv (S , _) = refl
signed-reserved-leftinv (W , _) = refl

reserved-signed-rightinv :
  (r : Reserved) →
  signed-to-reserved (reserved-to-signed r) ≡ r
reserved-signed-rightinv
  ((false , false , _ , .false , .false) , (refl , refl)) = refl
reserved-signed-rightinv
  ((true  , false , _ , .false , .false) , (refl , refl)) = refl
reserved-signed-rightinv
  ((false , true  , _ , .false , .false) , (refl , refl)) = refl
reserved-signed-rightinv
  ((true  , true  , _ , .false , .false) , (refl , refl)) = refl

------------------------------------------------------------------------
-- The equivalence as a stdlib Iso.
------------------------------------------------------------------------

Reserved↔SignedAxis : Reserved ↔ (Axis × Bool)
Reserved↔SignedAxis = mk↔ₛ′
  reserved-to-signed
  signed-to-reserved
  signed-reserved-leftinv
  reserved-signed-rightinv

------------------------------------------------------------------------
-- Notes — follow-on readings (deferred)
--
-- 1. Live ↔ Permutation: composes the Codeword encoding of the 24
--    live codewords with the existing TotalSpace ≃ S_4 chain
--    (Substrate.Cocycles.V4Signature.S4Iso). Will require a specific
--    encoding of (axis-to-exclude × ordering-of-three) on the live
--    bit patterns; the ordering uses the 6 selector values of
--    {b₂, b₃, b₄} excluding b₃ = b₄ = false.
--
-- 2. Hodge ★ at dim 4: Reserved ↔ Λ¹(V⁴) × sign on one side; the
--    8 oriented 3-form basis vectors on the other. The Reserved ↔
--    Axis × Bool reading above identifies the 1-form side; the
--    3-form side is a derived equivalence via "complement axis"
--    (which axis is the SINGLE one NOT in the unordered triple).
--
-- 3. Each subsequent reading is a separate lemma per
--    [[feedback-multi-reading-ambient-discipline]]; the ambient
--    above is the structural commitment, the readings are
--    catalog-driven derived equivalences.
--
-- 4. Cardinality lemmas (|Reserved| = 8, |Live| = 24) — derivable
--    from the Iso here (transports |Axis × Bool| = 8 to
--    |Reserved| = 8) plus an analogous Iso for Live. Deferred
--    until a downstream theorem needs them numerically.
------------------------------------------------------------------------
