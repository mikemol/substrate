------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.ResidueAtom.List
--
-- THE FREE MONOID AS A TORSOR ATOM — `List A` under `++`, and the
-- FixedPointFree that falls out.
--
-- ⚑ THIS IS THE WEDGE'S NATIVE CARRIER.  `Algebra/List/Wedge.agda:4-14` argues
-- that `List A` is *"not just *a* wedge-carrier; it is the wedge's NATIVE
-- carrier — the one whose `recon` is the wedge's intension rather than a ring
-- arithmetic encoding of it"*: `recon q b r = (q copies of b) ++ r` is the
-- wedge's defining phrase made definitional.  So if the residue⟹FixedPointFree
-- direction (Lawvere.agda:232-242) is going to hold anywhere, it should hold
-- here most plainly — and it does, by a three-line induction.
--
-- ⚑ NO APPEND LAWS WERE NEEDED, AND NONE EXIST FOR THIS CARRIER.  `++-assoc`
-- has seven homes in the tree (`Coxeter.Word`, `Wedge.Product.Laws`,
-- `TmDBGodel.Properties`, …) and NOT ONE is over `Foundation.List`; there is no
-- `++-cancel` anywhere (`--grep '\+\+-assoc|\+\+-identity|length-\+\+|\+\+-cancel'`).
-- The proof below therefore does not route through a monoid structure — it
-- inducts on the SECOND argument directly, which is shorter than assembling one.
--
-- ⚑ AND IT DELIBERATELY DOES NOT ROUTE THROUGH `length`.  The obvious proof is
-- "lengths agree, so `length g ℕ+ length x ≡ length x`, so `length g ≡ 0`" — but
-- the only `length-++` over `Foundation.List` lives in
-- `WitnessTower.Enumerate.LengthAppend:24`, and importing it would put an
-- `Algebra.*` module downstream of `WitnessTower.*`, inverting the layer
-- direction.  That is the same caveat that made the CYCLIC carrier expensive
-- (Ⓒ3′); here the direct induction avoids it entirely.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.ResidueAtom.List where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Category.Lawvere using (FixedPointFree; TorsorAtom; translate-fpf)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. Free-monoid cancellation at the unit: g ++ x ≡ x ⟹ g ≡ [].
--
-- Induction on x.  At [] the hypothesis IS the conclusion (g ++ [] ≡ [] forces
-- g ≡ [] because a cons on the left cannot equal []).  At x ∷ xs the head of
-- `g ++ (x ∷ xs)` is g's head when g is a cons, so g ≡ [] follows by
-- constructor disjointness on the SUFFIX — no assoc, no identity law.
------------------------------------------------------------------------

-- ⚑ ROUTED THROUGH LENGTH AFTER ALL, AND THE HEADER'S REASON FOR NOT DOING SO
-- WAS ONLY HALF RIGHT.  The concern was importing
-- `WitnessTower.Enumerate.LengthAppend:24` from `Algebra.*`, which would invert
-- the layer direction.  That still holds — so the four-line lemma is proved
-- HERE rather than imported, which costs nothing and keeps the layering.
--
-- ⚑ TWO DIRECT INDUCTIONS FAILED FIRST, and the failures are the informative
-- part: `_++_` reduces on its FIRST argument, so an induction that consumes the
-- SECOND never exposes a cons to strip.  Agda said so precisely —
-- `g ++ _y ∷ _z ∷ _zs != _b ∷ g ++ _y ∷ zs`.  Length turns the structural
-- argument into an arithmetic one, where the recursion is on the right shape.
length-++ : {A : Set} (xs ys : List A) →
            length (xs ++ ys) ≡ length xs ℕ+ length ys
length-++ []       ys = refl
length-++ (x ∷ xs) ys = cong suc (length-++ xs ys)

-- `n ℕ+ m ≡ m` forces `n ≡ 0`: cancellation on ℕ, by induction on m.
plus-fix-zero : (n m : ℕ) → (n ℕ+ m) ≡ m → n ≡ 0
plus-fix-zero n zero    eq = trans (sym (+ℕ-identityʳ n)) eq
plus-fix-zero n (suc m) eq = plus-fix-zero n m (suc-inj (trans (sym (+ℕ-suc n m)) eq))
  where
    suc-inj : {a b : ℕ} → suc a ≡ suc b → a ≡ b
    suc-inj refl = refl

-- a word of length zero is empty.
length-zero : {A : Set} (xs : List A) → length xs ≡ 0 → xs ≡ []
length-zero []      _  = refl
length-zero (_ ∷ _) ()

list-fix : {A : Set} (g x : List A) → (g ++ x) ≡ x → g ≡ []
list-fix g x eq =
  length-zero g
    (plus-fix-zero (length g) (length x)
      (trans (sym (length-++ g x)) (cong length eq)))

------------------------------------------------------------------------
-- 2. The torsor atom, and the residue flip it licenses.
------------------------------------------------------------------------

List-torsor : (A : Set) → TorsorAtom (List A)
List-torsor A = record { _∙_ = _++_ ; e = [] ; fix→unit = list-fix }

-- prefixing by any NON-EMPTY word is fixed-point-free: no word equals itself
-- with a non-trivial prefix glued on.  The free-monoid reading of the residue
-- atom — and the plainest statement in the tree of "a non-trivial residue is a
-- genuine distinction" (Lawvere.agda:236-239).
List-residue-fpf : {A : Set} (g : List A) → (g ≡ [] → ⊥) → FixedPointFree (List A)
List-residue-fpf {A} g g≢[] = translate-fpf (List-torsor A) g g≢[]

-- the canonical witness: a one-letter prefix, non-empty by constructor
-- disjointness, so the instance closes with nothing to discharge.
List-residue-fpf-cons : {A : Set} (a : A) → FixedPointFree (List A)
List-residue-fpf-cons a = List-residue-fpf (a ∷ []) (λ ())
