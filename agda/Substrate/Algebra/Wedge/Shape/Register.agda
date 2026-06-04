------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Register
--
-- THE INTERNED REGISTER — the type-theory-native heap. The exterior (von
-- Neumann) view: a flat register of observed shapes; an "address" is a
-- membership index into it; structural equality becomes index comparison.
-- Here that exterior picture is made FIRST-CLASS and VERIFIED, so the
-- coincidence "equal value ⟺ equal address" is a theorem, not a runtime hope:
--
--   * Register  = List WedgeShape — the heap, made data.
--   * x ∈ᴿ reg  = a membership; `idx` reads off its position = the address.
--   * idx-inj   = SOUNDNESS of the fast path: equal index ⟹ equal shape
--                 (so comparing addresses decides structural equality).
--   * intern    = hash-cons: look the shape up (decidable `_≟ˢ_`); reuse its
--                 address if present, append a new node if not. Equal-by-value
--                 shapes collapse to one node — copies minimized by construction.
--
-- value-equality (`_≡_` on WedgeShape) is the SPEC; index-equality is the
-- IMPLEMENTATION; `idx-inj` is the refinement proof connecting them — the
-- exterior heap as a verified realization of the interior semantics.
--
-- SCOPE: this dedups WHOLE shapes (one node per shape). Suffix-sharing (the
-- DAG: nodes referencing tail-indices, so sub-shapes are shared too) is the
-- further memory refinement, with the same spec. The (→) direction (a shape
-- always interns to one address) is the no-duplicate invariant `intern`
-- maintains by appending only when absent.
--
-- The membership relation is named `_∈ᴿ_` (register membership) — its shape,
-- not the bare `_∈_`, to avoid manufacturing a collision (names-vacuous rule).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Register where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; suc-injective) renaming (_≟_ to _≟ⁿ_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge.Shape using (WedgeShape)

------------------------------------------------------------------------
-- 1. Decidable equality on shapes (the CMP loop) — built from ℕ's.
------------------------------------------------------------------------

_≟ˢ_ : (xs ys : WedgeShape) → Dec (xs ≡ ys)
[]       ≟ˢ []       = yes refl
[]       ≟ˢ (_ ∷ _)  = no (λ ())
(_ ∷ _)  ≟ˢ []       = no (λ ())
(x ∷ xs) ≟ˢ (y ∷ ys) with x ≟ⁿ y | xs ≟ˢ ys
... | yes refl | yes refl = yes refl
... | no  x≢y  | _        = no (λ { refl → x≢y refl })
... | _        | no xs≢ys = no (λ { refl → xs≢ys refl })

------------------------------------------------------------------------
-- 2. The heap: register, membership (= address), index.
------------------------------------------------------------------------

Register : Set
Register = List WedgeShape

data _∈ᴿ_ (x : WedgeShape) : Register → Set where
  here  : {reg : Register} → x ∈ᴿ (x ∷ reg)
  there : {y : WedgeShape} {reg : Register} → x ∈ᴿ reg → x ∈ᴿ (y ∷ reg)

-- the address: the position of a membership in the register.
idx : {x : WedgeShape} {reg : Register} → x ∈ᴿ reg → ℕ
idx here      = zero
idx (there p) = suc (idx p)

------------------------------------------------------------------------
-- 3. SOUNDNESS — equal address ⟹ equal value (the fast path is correct).
------------------------------------------------------------------------

idx-inj : {x y : WedgeShape} {reg : Register}
          (p : x ∈ᴿ reg) (q : y ∈ᴿ reg) → idx p ≡ idx q → x ≡ y
idx-inj here      here      _ = refl
idx-inj here      (there _) ()
idx-inj (there _) here      ()
idx-inj (there p) (there q) e = idx-inj p q (suc-injective e)

------------------------------------------------------------------------
-- 4. Hash-cons: decidable membership + append-when-absent.
------------------------------------------------------------------------

find : (x : WedgeShape) (reg : Register) → Dec (x ∈ᴿ reg)
find x []        = no (λ ())
find x (y ∷ reg) with x ≟ˢ y
... | yes refl = yes here
... | no  x≢y  with find x reg
...   | yes p     = yes (there p)
...   | no  x∉reg = no (λ { here → x≢y refl ; (there p) → x∉reg p })

-- a shape appended to the end is a member there.
∈ᴿ-snoc : (x : WedgeShape) (reg : Register) → x ∈ᴿ (reg ++ (x ∷ []))
∈ᴿ-snoc x []        = here
∈ᴿ-snoc x (y ∷ reg) = there (∈ᴿ-snoc x reg)

-- intern: reuse the address if present, append a new node if not. Returns the
-- register with x guaranteed present, and its membership (the canonical
-- address). Equal-by-value shapes resolve to the same node.
intern : (x : WedgeShape) (reg : Register) → Σ Register (λ reg′ → x ∈ᴿ reg′)
intern x reg with find x reg
... | yes p = reg , p
... | no  _ = (reg ++ (x ∷ [])) , ∈ᴿ-snoc x reg
