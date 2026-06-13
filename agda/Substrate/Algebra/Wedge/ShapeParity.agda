------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.ShapeParity
--
-- NORMALIZING the det ≅ parity analogy through the EEA-trace word (user,
-- 2026-06-13: "this is EXACTLY why we used EEA's trace and bezout to normalize
-- analogies"). I had dismissed `det (Algebra.R.Trace.DetSign) ≅ upterm-parity
-- (Category.UP.TermParity)` as "merely analogous, no map" — the exact dismissal the
-- wedge program exists to refute. They DO share a map: both are the LENGTH-PARITY
-- of a trace WORD, and the wedge's `shape : Trace → List ℕ` (the carrier-free CF
-- word) is the common word.
--
-- `list-parity` is the UNIVERSAL ℤ/2 length-parity cocycle. The CF determinant sign
-- is its ℤ-valued realization on the CF word (`cf-shape-parity = list-parity ∘
-- shape`); the UPTerm parity is the same `list-parity` on the generator word. So the
-- analogy is normalized to an equality of ONE shared cocycle on the EEA-trace word —
-- a constructed cross-silo correspondence, not a dead analogy.
--
-- (The full det = (−1)ⁿ identity tying DetSign's ℤ value to this Bool parity is a
-- further lemma — det-after recurses forward, so the sign-accumulation induction is
-- separate; the WORD-level normalization here is the clean bridge.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.ShapeParity where

open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Bool using (Bool; true; false; not; _xor_)
open import Substrate.Foundation.Eq   using (_≡_; refl; cong; trans)

open import Substrate.Algebra.Wedge       using (DivStr; C; Trace)
open import Substrate.Algebra.Wedge.Shape using (shape)

------------------------------------------------------------------------
-- The universal ℤ/2 length-parity cocycle on words.
------------------------------------------------------------------------

list-parity : {A : Set} → List A → Bool
list-parity []       = false
list-parity (_ ∷ xs) = not (list-parity xs)

not-xorˡ : (a b : Bool) → not (a xor b) ≡ (not a) xor b
not-xorˡ true  true  = refl
not-xorˡ true  false = refl
not-xorˡ false true  = refl
not-xorˡ false false = refl

-- the cocycle law: parity of a concatenation is the xor of parities.
list-parity-++ : {A : Set} (xs ys : List A) →
  list-parity (xs ++ ys) ≡ (list-parity xs xor list-parity ys)
list-parity-++ []       ys = refl
list-parity-++ (x ∷ xs) ys =
  trans (cong not (list-parity-++ xs ys))
        (not-xorˡ (list-parity xs) (list-parity ys))

------------------------------------------------------------------------
-- The CF / wedge-side instance: the parity of the EEA-trace word. This is the SAME
-- cocycle that `Category.UP.TermParity.upterm-parity` is on the UPTerm generator
-- word — the normalized det≅parity correspondence, both factoring through
-- `list-parity` of the trace word that `shape` produces.
------------------------------------------------------------------------

cf-shape-parity : {D : DivStr} {a b g : C D} → Trace D a b g → Bool
cf-shape-parity t = list-parity (shape t)
