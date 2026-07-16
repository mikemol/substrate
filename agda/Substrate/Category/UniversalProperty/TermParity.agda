------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.TermParity
--
-- THE UNIVERSAL ℤ/2 COCHAIN on the free term algebra (user, 2026-06-13: "before
-- you assert all of this is heterogeneous, you need to trace to the foundations for
-- each of those bridge shapes"). Traced: EVERY bridge `.Term` (Markov, Lens, Poly,
-- Conj, DFT, Cascade, Char) is the identical foundation — `data XxxTerm : Obj → Obj
-- → Set` with `[]` (identity) and `_∷_ : XxxGen → XxxTerm → XxxTerm` (cons). A typed
-- cons-list of generators = a free category on its generator graph. They are NOT
-- heterogeneous; they share this foundation. `UPTerm` is the substrate's canonical
-- such free term algebra.
--
-- So the morphism-side ℤ/2 is UNIFORM across all of them: word-length parity. Each
-- generator (`_∷_`) flips it — the categorical form of the CF determinant sign
-- (`Algebra.R.Trace.DetSign`, where each Euclidean step flips). And it is a ℤ/2
-- COCYCLE: a homomorphism for composition (`upterm-parity-++`). So "the trace is a
-- continually-evolving ℤ/2" is not special to continued fractions — it is the
-- length-parity of ANY free-term word, and every bridge `.Term` carries it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.TermParity where

open import Substrate.Foundation.Bool using (Bool; true; false; not; _xor_)
open import Substrate.Foundation.Eq   using (_≡_; refl; cong; trans)

-- ⟡ta-upterm: the parity cochain flipped onto the Set₀ O-forms (UPTerm).
open import Substrate.Category.UniversalProperty.Term using (UPTerm; []; _∷_; _++ᵤ_)

not-xorˡ : (a b : Bool) → not (a xor b) ≡ (not a) xor b
not-xorˡ true  true  = refl
not-xorˡ true  false = refl
not-xorˡ false true  = refl
not-xorˡ false false = refl

module _ {O : Set} {Hom : O → O → Set} where

  ----------------------------------------------------------------------
  -- The ℤ/2 cochain: word-length parity. `[]` is even; each `_∷_` flips.
  ----------------------------------------------------------------------

  upterm-parity : {X Y : O} → UPTerm O Hom X Y → Bool
  upterm-parity []      = false
  upterm-parity (_ ∷ t) = not (upterm-parity t)

  ----------------------------------------------------------------------
  -- It is a ℤ/2 cocycle: parity of a composite is the xor of the parities — so the
  -- "continually evolving ℤ/2" composes (the discriminator's morphism-side law).
  ----------------------------------------------------------------------

  upterm-parity-++ :
    {X Y Z : O} (s : UPTerm O Hom X Y) (t : UPTerm O Hom Y Z) →
    upterm-parity (s ++ᵤ t) ≡ (upterm-parity s xor upterm-parity t)
  upterm-parity-++ []      t = refl
  upterm-parity-++ (g ∷ s) t =
    trans (cong not (upterm-parity-++ s t))
          (not-xorˡ (upterm-parity s) (upterm-parity t))
