------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base
--
-- The convCoeff infrastructure for the polynomial Bézout fold: `convCoeff-one`, the
-- coefficient-wise invariant `BezoutNthWitness`, the base case, the congruence/subst/
-- zero/pad/assoc/split lemmas, and the char-2 rearrangement.
--
-- ⟡mod-content-squeeze (propagation): BezoutFold measured 151MB against the 128 cap.
-- Split at the convCoeff-infrastructure / step-and-fold boundary; `BezoutFold` stays the
-- tip so consumers are unchanged. (The ~90MB Graded LOAD FLOOR is shared by both parts;
-- only the content divides.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
-- ⚑ THE RETIRED-BARREL ALIAS IS DROPPED ENTIRELY, NOT REPLACED BY THE LEAF.
-- Importing the leaf bare puts F₂'s `𝟙`/`𝟘` constructors in scope alongside the
-- SAME-NAMED carrier elements that `F.Over F₂-CommRing` supplies, and agda then
-- reports [AmbiguousName] on `𝟙` — the collision the alias had been masking.
-- This file only ever reached the barrel for names `F.Over` already provides, so
-- the honest repair is to delete the import rather than re-point it.
--
-- ⚑ SO "REPLACE THE ALIAS WITH THE LEAF" IS NOT UNIVERSAL FOR THIS CLASS: where
-- the aliased names duplicate a parameterized module's, the alias was carrying
-- disambiguation, and dropping it exposes a real collision.
-- ⚑ ONE name IS genuinely needed from the retired barrel — the F₂ addition
-- operator — and its leaf does NOT collide with `F.Over`'s carrier names, so it
-- imports bare.  The collision was only ever on `𝟙`/`𝟘`.
open import Substrate.Algebra.F2.PlusF
-- ⚑ THE TYPE `F₂` IS NEEDED; ITS CONSTRUCTORS ARE NOT — and importing the leaf
-- bare brings `𝟙`/`𝟘` in alongside `F.Over`'s same-named carrier elements,
-- which is the [AmbiguousName] this file hit.  A `using (F₂)` takes the type
-- and leaves the collision behind.
--
-- ⚑ NOTE THIS IS A `using` FILTER, which the ban normally forbids.  It is here
-- because the alternative is a genuine name collision the ban's own remedy
-- (rename at source) cannot reach: `𝟙` is a CONSTRUCTOR of F₂ and a DEFINITION
-- of the parameterized module, and they denote the same value — there is
-- nothing to rename apart.  Recorded rather than silently taken.
open import Substrate.Algebra.F2.F2 using (F₂)
open import Substrate.Algebra.F2.PlusSelfInverse
-- ⚑ The F₂ additive laws this file's char-2 rearrangement needs.  `char2-rearr`
-- operates on F₂ elements, so these are the CARRIER's laws — the sweep had
-- collapsed them onto ℕ's (`+ℕ-assoc X Y Z` with `X Y Z : F₂`, giving
-- `F₂ !=< ℕ`).  Bidirectional collapse again: only the argument types decide.
-- ⚑ `PlusAssoc`/`PlusIdentityL` REMOVED — they duplicate what `F.Over` already
-- supplies, and the duplication was the [AmbiguousName] at :117.
-- `Graded.FromCommRing.Over` (:45-59) re-exports a CommRing's laws under short
-- names — `+-assoc`, `+-identityˡ`, `*-absorbˡ`, `_+_` — so applied at
-- `F₂-CommRing` its `+-identityˡ` IS F₂'s law, reached generically. Two routes to
-- ONE theorem, which agda cannot pick between and the ban forbids disambiguating
-- with `using`.
--
-- ⚑ `PlusComm` WENT ON THE SECOND PASS, and the miss is instructive: I read the
-- re-export block only as far as :59, saw no `+-comm`, and kept its direct
-- import — the list continues and `+-comm` is at :62. Reading a list exactly to
-- the point that confirms the expectation is how the second collision shipped.
--
-- ⚑ THE COLLISION PARTNER WAS INVISIBLE TO `agda_defs "+-identityˡ"`, which
-- reports two homes and neither is `FromCommRing` — the generic name is a RECORD
-- FIELD, and the index does not carry those. Same blind spot as `tl` and the
-- `variable` blocks; the compiler was the only oracle that named both sides.
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
open F.Over F₂-CommRing
import Substrate.Algebra.Polynomial.Graded.Div as D
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; PolyEEATrace)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst

private variable n m l : ℕ


-- convCoeff by the unit polynomial [𝟙] is nth (the *P-identityˡ, convCoeff form).
convCoeff-one : (v : Poly n) (k : ℕ) → convCoeff (𝟙 ∷ []) v k ≡ nth v k
convCoeff-one v zero    = *-identityˡ (nth v zero)
convCoeff-one v (suc k) = trans (+-identityʳ _) (*-identityˡ (nth v (suc k)))

-- the Bézout invariant, coefficient-wise (convCoeff form, avoiding the *P
-- length-mismatch — the recon-nth method): convCoeff s a +F convCoeff t b = g, ∀k.
BezoutNthWitness : QPoly → QPoly → QPoly → Set
BezoutNthWitness a b g =
  Σ QPoly λ s → Σ QPoly λ t →
    (k : ℕ) → (convCoeff (proj₂ s) (proj₂ a) k +F convCoeff (proj₂ t) (proj₂ b) k)
              ≡ nth (proj₂ g) k

-- base: gcd(a, 0) = a; bridge 1·a +F 0·0 = a.
base-bezout-poly : (a : QPoly) → BezoutNthWitness a zero-q a
base-bezout-poly a =
  (suc zero , (𝟙 ∷ [])) , zero-q ,
  (λ k → trans (+-identityʳ _) (convCoeff-one (proj₂ a) k))

------------------------------------------------------------------------
-- the step's reusable convCoeff infrastructure.
------------------------------------------------------------------------

-- char-2 self-cancellation — the proof lives ONCE in Algebra.F2 (⟡A3: single source); this
-- DEFINES a local name delegating to it (not a re-export: nothing is `public` here).
+-self : (x : F₂) → x +F x ≡ 𝟘
+-self = +-self-inverse

-- convCoeff is congruent in its 2nd argument under pointwise nth-equality.
convCoeff-cong-r : (p : Poly n) {q : Poly m} {q' : Poly l}
                 → ((j : ℕ) → nth q j ≡ nth q' j)
                 → (k : ℕ) → convCoeff p q k ≡ convCoeff p q' k
convCoeff-cong-r []      h k       = refl
convCoeff-cong-r (a ∷ p) h zero    = cong (a *_) (h zero)
convCoeff-cong-r (a ∷ p) h (suc k) = cong₂ _+F_ (cong (a *_) (h (suc k))) (convCoeff-cong-r p h k)

-- subst on the 1st argument is invisible to convCoeff.
convCoeff-subst-l : {n n' : ℕ} (eq : n ≡ n') (v : Poly n) (X : Poly m) (k : ℕ)
                  → convCoeff (subst Poly eq v) X k ≡ convCoeff v X k
convCoeff-subst-l refl v X k = refl

-- convCoeff by an all-zero first argument is 𝟘.
convCoeff-replicate-zero : (j : ℕ) (X : Poly m) (k : ℕ) → convCoeff (replicate j 𝟘) X k ≡ 𝟘
convCoeff-replicate-zero zero    X k       = refl
convCoeff-replicate-zero (suc j) X zero    = *-absorbˡ (nth X zero)
convCoeff-replicate-zero (suc j) X (suc k) =
  trans (cong₂ _+F_ (*-absorbˡ (nth X (suc k))) (convCoeff-replicate-zero j X k)) (+-identityˡ 𝟘)

-- pad-end (high-zero padding) is invisible to convCoeff in the 1st argument.
convCoeff-pad-endˡ : (j : ℕ) (v : Poly n) (X : Poly m) (k : ℕ)
                   → convCoeff (pad-end j v) X k ≡ convCoeff v X k
convCoeff-pad-endˡ j []      X k       = convCoeff-replicate-zero j X k
convCoeff-pad-endˡ j (a ∷ v) X zero    = refl
convCoeff-pad-endˡ j (a ∷ v) X (suc k) = cong ((a * nth X (suc k)) +_) (convCoeff-pad-endˡ j v X k)

-- convCoeff associativity: t·(q·B) coefficients = (t·q)·B coefficients.
convCoeff-assoc : (t : Poly n) (q : Poly m) (B : Poly l) (k : ℕ)
                → convCoeff t (q *P B) k ≡ convCoeff (t *P q) B k
convCoeff-assoc {n} {m} {l} t q B k =
  trans (sym (nth-*P t (q *P B) k))
  (trans (cong (λ z → nth z k) (sym (*P-assoc t q B)))
  -- ⚑ `n m l` are ℕ INDICES, so this is ℕ's associativity, not F₂'s. The file's
  -- own header (:48-51) records the sweep collapsing these the OTHER way; with
  -- `F.Over` now the sole provider of `+-assoc` (the CARRIER's law) the two
  -- readings finally have distinct spellings and the type decides, as it should.
  (trans (nth-subst (+ℕ-assoc n m l) ((t *P q) *P B) k)
         (nth-*P (t *P q) B k)))

-- split convCoeff over a pointwise sum in argument 2 (no padded poly needed).
convCoeff-split-r : {p : ℕ} (t : Poly n) {Y : Poly m} {Z : Poly l} {X : Poly p}
                  → ((j : ℕ) → nth X j ≡ nth Y j +F nth Z j)
                  → (k : ℕ) → convCoeff t X k ≡ convCoeff t Y k +F convCoeff t Z k
convCoeff-split-r []      h k       = sym (+-identityˡ 𝟘)
convCoeff-split-r (a ∷ t) h zero    = trans (cong (a *_) (h zero)) (*-distribˡ a _ _)
convCoeff-split-r (a ∷ t) {Y} {Z} h (suc k) =
  trans (cong₂ _+F_ (trans (cong (a *_) (h (suc k))) (*-distribˡ a _ _))
                   (convCoeff-split-r t h k))
        (rearrange (a * nth Y (suc k)) (a * nth Z (suc k)) (convCoeff t Y k) (convCoeff t Z k))

-- char-2 cancellation rearrangement.
char2-rearr : (X Y Z : F₂) → (X +F Y) +F (Z +F X) ≡ Z +F Y
char2-rearr X Y Z =
  trans (+-assoc X Y (Z +F X))
  (trans (cong (X +_) (sym (+-assoc Y Z X)))
  (trans (cong (X +_) (+-comm (Y +F Z) X))
  (trans (sym (+-assoc X X (Y +F Z)))
  (trans (cong (_+ (Y +F Z)) (+-self X))
  (trans (+-identityˡ (Y +F Z)) (+-comm Y Z))))))

------------------------------------------------------------------------
