------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetCrossMix
--
-- Ⓗ.crossmix-wire — the keystone: HetQ's cross-multiply ⊗ is LITERALLY the
-- substrate's `Wedge.CrossMul.cross` for a cospan of genuine `Bridge`s, and
-- ℚ's equality `_≈ℚ_` IS that cospan's cross-equality. Machine-checked, not
-- narrated.
--
-- The cospan:   ℤ-div  →(id)  ℤ  ←(ℕ↪ℤ)  ℕ-div
--   • numerator carrier A = ℤ-div, embedded by the IDENTITY bridge (num is
--     already in ℤ);
--   • denominator carrier B = ℕ-div, embedded by the pre-existing inclusion
--     bridge `include-ℕℤ` (ℕ ↪ ℤ, the non-negative coercion — a real Bridge,
--     respects recon definitionally);
--   • common carrier R = ℤ-mul (ℤ with *ℤ).
-- Then `cross ℚ-crossmix a d = a *ℤ (+ d)` — and with d the ACTUAL denominator
-- (suc den-1) this is exactly the ℚ cross-multiplication. The two codec legs
-- ARE Bridges; ⊗ IS their `cross`; and HetBasis's `viaBridges` factorization is
-- `cross` itself (refl). This grounds the 4-layer bridge map's central claim —
-- "the codec legs are Bridges and ⊗ is their cross" — in one certified instance.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetCrossMix where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Z.Wedge using (ℤ-div)
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; base; mul)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; translate; id-bridge)
open import Substrate.Algebra.Wedge.InclusionBridge using (include-ℕℤ)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; embA; embB)
open import Substrate.Algebra.Q using (ℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.Q.HetBasis

------------------------------------------------------------------------
-- 1. ℤ as the common multiplicative carrier R of the cospan.
------------------------------------------------------------------------

ℤ-mul : MulDivStr ℤ
ℤ-mul = record { base = ℤ-div ; mul = _*ℤ_ }

------------------------------------------------------------------------
-- 2. The cospan ℤ-div →(id) ℤ ←(ℕ↪ℤ) ℕ-div, as an actual CrossMix of two
--    pre-existing Bridges. THIS is "differently-basised num/denom" in the
--    repo's own bridging vocabulary.
------------------------------------------------------------------------

ℚ-crossmix : CrossMix ℤ-div ℕ-div ℤ-mul
ℚ-crossmix = record { embA = id-bridge ℤ-div ; embB = include-ℕℤ }

-- cross ℚ-crossmix a d  =  a *ℤ (+ d)   (definitional).
⊗-crossmix : ℤ → ℕ → ℤ
⊗-crossmix = cross ℚ-crossmix

------------------------------------------------------------------------
-- 3. CrossMul.cross IS HetBasis.viaBridges at the two codec legs (refl):
--    ⊗ = mul R ∘ (codecA × codecB), with codecA/codecB the Bridges' translates.
------------------------------------------------------------------------

cross-is-viaBridges : (a : ℤ) (d : ℕ) →
  cross ℚ-crossmix a d
    ≡ viaBridges (translate (embA ℚ-crossmix)) (translate (embB ℚ-crossmix)) (mul ℤ-mul) a d
cross-is-viaBridges a d = refl

------------------------------------------------------------------------
-- 4. ℚ as HetQ ℤ ℕ using the ACTUAL denominator (suc den-1), so the plain
--    inclusion codec applies. (The stored den-1 would need a +suc shift, which
--    is NOT a recon-respecting Bridge — the actual denominator is the honest
--    numerator-basis-over-denominator-basis split.)
------------------------------------------------------------------------

toHetQ-den : ℚ → HetQ ℤ ℕ
toHetQ-den q = num q // denominator q

open CrossEq ⊗-crossmix _≡_ refl sym renaming (_≈H_ to _≈cx_)

------------------------------------------------------------------------
-- 5. THE KEYSTONE: ℚ's equality _≈ℚ_ IS the cross-equality of this cospan —
--    both directly (cross-form) and through the HetQ/CrossEq layer. By refl:
--    _≈ℚ_ unfolds to num p *ℤ (+ suc den-1 q) ≡ num q *ℤ (+ suc den-1 p), and
--    cross ℚ-crossmix (num p) (denominator q) reduces to the same.
------------------------------------------------------------------------

≈ℚ-is-crossmix : (p q : ℚ) →
  (p ≈ℚ q) ≡ (cross ℚ-crossmix (num p) (denominator q)
                ≡ cross ℚ-crossmix (num q) (denominator p))
≈ℚ-is-crossmix p q = refl

≈ℚ-via-HetQ : (p q : ℚ) → (p ≈ℚ q) ≡ (toHetQ-den p ≈cx toHetQ-den q)
≈ℚ-via-HetQ p q = refl
