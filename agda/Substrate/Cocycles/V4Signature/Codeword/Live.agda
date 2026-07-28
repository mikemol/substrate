------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.Live
--
-- First piece of slice 11: decompose Live (24 codewords) into the
-- factored form (Axis × Selector) where Selector is a 6-element type
-- corresponding to the 6 live bit-patterns of (b₂, b₃, b₄).
--
-- This module gives:
--   * Decidable equality on Axis.
--   * Selector : Set (6 constructors, one per live (b₂,b₃,b₄) pattern).
--   * Live ↔ (Axis × Selector) — the structural decoding of a Live
--     codeword into "axis-to-exclude × ordering-selector".
--
-- The follow-on module composes (Axis × Selector) with a Permutation
-- builder to give Live ↔ Permutation — the catalog's "24 ARE S_4"
-- reading at the codeword layer.
--
-- See: catalog/cocycles.md § CY-5 — "24 ARE S_4" claim;
--      Substrate.Cocycles.V4Signature.Codeword — the ambient.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.Live where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂; Σ; Σ-syntax)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Bijection using (_↔_; mk↔ₛ′)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Cocycles.V4Signature.Codeword.AxisBits using (axis-from-bits; axis-to-bits; axis-bits-id; bits-axis-id)
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved using (IsReserved)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved; Live)
open import Substrate.Cocycles.V4Signature.Codeword.Type using (Codeword)

------------------------------------------------------------------------
-- Decidable equality on Axis.
------------------------------------------------------------------------

_≟ₐ_ : (x y : Axis) → Dec (x ≡ y)
D ≟ₐ D = yes refl
D ≟ₐ C = no (λ ())
D ≟ₐ S = no (λ ())
D ≟ₐ W = no (λ ())
C ≟ₐ D = no (λ ())
C ≟ₐ C = yes refl
C ≟ₐ S = no (λ ())
C ≟ₐ W = no (λ ())
S ≟ₐ D = no (λ ())
S ≟ₐ C = no (λ ())
S ≟ₐ S = yes refl
S ≟ₐ W = no (λ ())
W ≟ₐ D = no (λ ())
W ≟ₐ C = no (λ ())
W ≟ₐ S = no (λ ())
W ≟ₐ W = yes refl

------------------------------------------------------------------------
-- Selector — the 6 live bit-patterns of (b₂, b₃, b₄).
--
-- A live codeword has (b₃, b₄) ≠ (false, false), giving 6 valid
-- (b₂, b₃, b₄) patterns. Each names one of the 6 orderings of 3
-- axes (≅ S₃).
--
-- Naming convention: sel-XYZ where X, Y, Z are the bit values.
------------------------------------------------------------------------

data Selector : Set where
  sel-fft : Selector   -- (b₂=false, b₃=false, b₄=true)
  sel-tft : Selector   -- (b₂=true,  b₃=false, b₄=true)
  sel-ftf : Selector   -- (b₂=false, b₃=true,  b₄=false)
  sel-ttf : Selector   -- (b₂=true,  b₃=true,  b₄=false)
  sel-ftt : Selector   -- (b₂=false, b₃=true,  b₄=true)
  sel-ttt : Selector   -- (b₂=true,  b₃=true,  b₄=true)

------------------------------------------------------------------------
-- Bijection between Selector and the 6 live (b₂, b₃, b₄) patterns.
------------------------------------------------------------------------

selector-to-bits : Selector → Bool × Bool × Bool
selector-to-bits sel-fft = false , false , true
selector-to-bits sel-tft = true  , false , true
selector-to-bits sel-ftf = false , true  , false
selector-to-bits sel-ttf = true  , true  , false
selector-to-bits sel-ftt = false , true  , true
selector-to-bits sel-ttt = true  , true  , true

------------------------------------------------------------------------
-- Decoding a Live codeword into (Axis × Selector).
--
-- The Live proof guarantees (b₃, b₄) ≠ (false, false), so only the
-- 6 live patterns are possible. The 2 reserved (b₃ = false ∧ b₄ =
-- false) patterns are ruled out by the IsReserved-negation proof.
------------------------------------------------------------------------

live-to-axis-selector : Live → Axis × Selector
live-to-axis-selector ((b₀v , b₁v , b₂v , false , false) , ¬res) =
  ⊥-elim (¬res (refl , refl))
live-to-axis-selector ((b₀v , b₁v , b₂v , false , true)  , _) =
  axis-from-bits b₀v b₁v , (if-b₂ b₂v sel-tft sel-fft)
  where
    -- inline helper to avoid Bool elimination clutter
    if-b₂ : Bool → Selector → Selector → Selector
    if-b₂ true  t _ = t
    if-b₂ false _ f = f
live-to-axis-selector ((b₀v , b₁v , b₂v , true , false)  , _) =
  axis-from-bits b₀v b₁v , (if-b₂ b₂v sel-ttf sel-ftf)
  where
    if-b₂ : Bool → Selector → Selector → Selector
    if-b₂ true  t _ = t
    if-b₂ false _ f = f
live-to-axis-selector ((b₀v , b₁v , b₂v , true , true)   , _) =
  axis-from-bits b₀v b₁v , (if-b₂ b₂v sel-ttt sel-ftt)
  where
    if-b₂ : Bool → Selector → Selector → Selector
    if-b₂ true  t _ = t
    if-b₂ false _ f = f

------------------------------------------------------------------------
-- Encoding (Axis × Selector) back into a Live codeword.
------------------------------------------------------------------------

axis-selector-to-live : Axis × Selector → Live
axis-selector-to-live (a , sel) =
  (proj₁ (axis-to-bits a) , proj₂ (axis-to-bits a) ,
   proj₁ s , proj₁ (proj₂ s) , proj₂ (proj₂ s)) ,
  ¬-reserved sel
  where
    s : Bool × Bool × Bool
    s = selector-to-bits sel

    -- Each selector gives (b₃, b₄) ≠ (false, false), so IsReserved
    -- (which demands b₃ ≡ false ∧ b₄ ≡ false) is false.
    ¬-reserved : (sel : Selector) → ¬ IsReserved
      ((proj₁ (axis-to-bits a) , proj₂ (axis-to-bits a) ,
        proj₁ (selector-to-bits sel) ,
        proj₁ (proj₂ (selector-to-bits sel)) ,
        proj₂ (proj₂ (selector-to-bits sel))))
    ¬-reserved sel-fft (_ , ())
    ¬-reserved sel-tft (_ , ())
    ¬-reserved sel-ftf (())
    ¬-reserved sel-ttf (())
    ¬-reserved sel-ftt (())
    ¬-reserved sel-ttt (())

------------------------------------------------------------------------
-- Notes
--
-- 1. The decoding/encoding here is the structural half of the
--    Live ↔ Permutation reading. The next piece composes (Axis ×
--    Selector) with a Permutation builder: given (X, sel),
--    construct σ ∈ S_4 with σW = X and (σD, σC, σS) determined by
--    the selector applied to the 3 axes {D,C,S,W} \ {X}.
--
-- 2. The Permutation builder requires choosing a CONVENTION for how
--    each of the 6 selectors maps to one of the 6 orderings. That's
--    the load-bearing decision deferred to the next slice.
--
-- 3. Round-trip proofs (Live ↔ Axis × Selector as an Iso) are
--    deferred; they require case analysis on (b₃, b₄, b₂) and
--    feature similar mechanical structure to slice 10's
--    `reserved-signed-rightinv`.
------------------------------------------------------------------------
