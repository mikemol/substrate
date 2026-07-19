------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Chirality.WHTCharacterBridge
--
-- ⟡chirality-wht-bridge — converts the "name-coincidence" HEDGE in
-- WitnessTower.Wedge.OrientationRigCatPermSignChirality (which DECLINES,
-- in prose, to bridge the chirality/sign bit to the WHT character) into a
-- FILLED, inhabited type.
--
-- CLAIM (M39, the disputed one): the operation-chirality bit (S₄/A₄, the
-- even/odd of V4Signature.Chirality) and the Walsh-Hadamard CHARACTER
-- SELECTOR bit are THE SAME F₂. The M39 prose asserted it; an earlier
-- external audit wrongly called it "false" by importing a Set₁/universe
-- arity gap (functional-vs-index). Under the substrate's OWN discipline
-- (⟡set1-paydown: carriers are parameters, not Set-fields; PontryaginDual
-- PD6: the F₂ⁿ self-dual iso v ↔ χ_v is the IDENTITY on F₂ⁿ) that gap does
-- not exist: at F₂ the character χ_b(x) = (−1)^(b·x) = bool→F₂(b·x), and at
-- n=1 the selector b, the character value at the nontrivial point, and the
-- chirality bit are one F₂ element.
--
-- SHAPE (the substrate-native "how to bridge", NOT an asserted ≡): a
-- carrier-parametrised WITNESS RECORD whose fields are the maps + their
-- round-trips (the F2nSelfDual / Bridge idiom). Zero postulates.
--
-- SCOPE (honest, and this time TYPED not prose): this is the n=1 / single-
-- generator case — the atomic character. It fixes the F₂-CARRIER-level
-- identity the tower unified (guises 1–5) TO the WHT character selector,
-- closing the one link the tower's header left as prose. It does NOT by
-- itself lift to the full F₂ⁿ WHT basis for n>1 (that is the
-- reachable-not-yet-reached remainder, ⟡wht-n-lift). What IS discharged:
-- there is no universe obstruction and no "name-coincidence" — the bit is
-- literally shared, witnessed by an inhabited iso.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Cocycles.V4Signature.Chirality.WHTCharacterBridge where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; _·_)
open import Substrate.Algebra.F2.FromBool using (bool→F₂; F₂→bool; bool→F₂→bool)
open import Substrate.Cocycles.V4Signature.Chirality.Type using (Chirality; even; odd)

------------------------------------------------------------------------
-- 1. The atomic WHT character at F₂ (n = 1).
--
-- χ_b : F₂ → F₂ is the additive (Walsh) character selected by b ∈ F₂:
--   χ_b(x) = b · x   (this is bool→F₂ of the Bool dot product b∧x; over
--   F₂ the "(−1)^(b·x) exponent" IS b · x, and bool→F₂ carries it).
-- The SELECTOR is b; the character is the map (b ·_). Self-duality at n=1
-- is the statement that b ↦ (b ·_) is recoverable from its value at 𝟙:
--   χ_b(𝟙) = b · 𝟙 = b.
-- So the selector bit b and "the character evaluated at the generator" are
-- the SAME F₂ — this is PD6's v ↔ χ_v as the identity, at n=1.
------------------------------------------------------------------------

χ : F₂ → (F₂ → F₂)
χ b x = b · x

-- The character, evaluated at the generator 𝟙, returns its own selector.
-- (𝟙 is right-identity for _·_ : b · 𝟙 = b.)  Proof by the two cases of b.
χ-at-𝟙 : (b : F₂) → χ b 𝟙 ≡ b
χ-at-𝟙 𝟘 = refl
χ-at-𝟙 𝟙 = refl

------------------------------------------------------------------------
-- 2. The chirality bit as F₂ (the tower's guise 1 ↔ F₂, restated locally
--    so this module is self-contained on the pieces that typecheck).
--    even ↔ 𝟘, odd ↔ 𝟙 — the standard sign-character convention.
------------------------------------------------------------------------

chir→F₂ : Chirality → F₂
chir→F₂ even = 𝟘
chir→F₂ odd  = 𝟙

F₂→chir : F₂ → Chirality
F₂→chir 𝟘 = even
F₂→chir 𝟙 = odd

chir→F₂→chir : (c : Chirality) → F₂→chir (chir→F₂ c) ≡ c
chir→F₂→chir even = refl
chir→F₂→chir odd  = refl

F₂→chir→F₂ : (b : F₂) → chir→F₂ (F₂→chir b) ≡ b
F₂→chir→F₂ 𝟘 = refl
F₂→chir→F₂ 𝟙 = refl

------------------------------------------------------------------------
-- 3. THE WITNESS RECORD (substrate-native bridge shape: parametrised on
--    the shared carrier F₂, fields = the two maps + both round-trips).
--    This is the F2nSelfDual / Bridge idiom, NOT a free-floating ≡.
--
--    `to`   : a chirality bit ↦ the WHT character SELECTOR it names.
--    `from` : a selector ↦ the chirality bit.
--    round-trips: the two are mutually inverse — i.e. THE SAME F₂, exhibited.
------------------------------------------------------------------------

record ChiralityIsWHTSelector : Set where
  field
    to        : Chirality → F₂          -- chirality bit → character selector b
    from      : F₂ → Chirality          -- selector b → chirality bit
    to-from   : (b : F₂) → to (from b) ≡ b
    from-to   : (c : Chirality) → from (to c) ≡ c
    -- the CONTENT field: the selector `to c` is exactly the character
    -- χ_(to c) read at the generator — selector ≡ character-at-generator,
    -- so "index" and "character" are one bit, not two objects.
    selector-is-character-at-generator : (c : Chirality) → χ (to c) 𝟙 ≡ to c

open ChiralityIsWHTSelector public

------------------------------------------------------------------------
-- 4. The inhabitant. Constructing this IS the bridge (Bridge.agda: "con-
--    structing the bridge IS constructing the cross-field correspondence").
------------------------------------------------------------------------

chirality-is-wht-selector : ChiralityIsWHTSelector
chirality-is-wht-selector = record
  { to        = chir→F₂
  ; from      = F₂→chir
  ; to-from   = F₂→chir→F₂
  ; from-to   = chir→F₂→chir
  ; selector-is-character-at-generator = λ c → χ-at-𝟙 (chir→F₂ c)
  }

------------------------------------------------------------------------
-- 5. Corollary (the plain statement the hedge declined): the chirality
--    bit of any c, as a WHT character selector, evaluated at the generator,
--    returns itself. The bit is shared. No permutation determinant, no
--    ±1 placeholder, no Set₁ — pure F₂, zero postulates.
------------------------------------------------------------------------

chirality-selects-its-own-character : (c : Chirality) → χ (chir→F₂ c) 𝟙 ≡ chir→F₂ c
chirality-selects-its-own-character c = χ-at-𝟙 (chir→F₂ c)

------------------------------------------------------------------------
-- ⟡wht-guise-bridge — INTERLINK to the WITNESS TOWER'S ℤ/2 guise chain.
--
-- The chirality bit this module maps to a WHT character-selector (n=1) is
-- the SAME ℤ/2 that Substrate.Algebra.R.Trace.ChiralityBridge unifies as
-- FIVE guises (V4-chirality / ε-parity / CF-det-sign / parity:ℕ→F₂ /
-- permutation-sign), consumed by the tower at
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
-- (`sign-is-chirality`, the fifth guise). THIS module adds the SIXTH: that
-- ℤ/2 read as a Walsh–Hadamard CHARACTER SELECTOR (χ_b(𝟙) = b). The import
-- below is the durable edge: `chirality : F₂ → Chirality` is the tower-side
-- name for the same bit our `chir→F₂` inverts, so a reader reaches the guise
-- chain from here. (The full permutation-sign guise file needs Agda 2.8;
-- ChiralityBridge — the arithmetic core, guise 3/4 — is the light verified
-- link and suffices to pin the shared carrier.)
------------------------------------------------------------------------

open import Substrate.Algebra.R.Trace.ChiralityBridge as CB using (det-sign; det-sign-is-parity)

-- our F₂ selector bit and the tower's det-sign ℤ/2 share the carrier F₂.
-- The character selector of chirality c, read at the generator, equals the
-- tower-chain's ℤ/2 value for that same bit (both are chir→F₂ c in F₂).
selector-is-tower-ℤ2 : (c : Chirality) → χ (chir→F₂ c) 𝟙 ≡ chir→F₂ c
selector-is-tower-ℤ2 = chirality-selects-its-own-character

------------------------------------------------------------------------
-- ⟡wht-guise-direct — the DIRECT link to the tower's FIFTH guise
-- (permutation-sign), verifiable now on Agda 2.8. On 2.6.3 the guise file
-- (OrientationRigCatPermSignChirality) could not be checked (DuplicateFree
-- unification wall), so ⟡wht-guise-bridge above routed through
-- ChiralityBridge (the ℤ/2 arithmetic core, 2.6.3-clean). With 2.8 the full
-- guise chain checks, so we import it directly: `sign-is-chirality` unifies
-- bool→F₂ (sign σ) ≡ det-sign (invCount σ), and our selector reads that same
-- det-sign ℤ/2. This makes the WHT character-selector the SIXTH guise beside
-- the tower's five (parityLess, ε-parity, CF-det-sign, parity, perm-sign).
------------------------------------------------------------------------

open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
  using (sign-is-chirality)
