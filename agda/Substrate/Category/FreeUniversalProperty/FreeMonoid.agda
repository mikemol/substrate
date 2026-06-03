------------------------------------------------------------------------
-- Substrate.Category.FreeUniversalProperty.FreeMonoid
--
-- The flagship instance of the center: Coxeter.Word Gen IS the free
-- monoid on Gen — a content-bearing FreeUP for the monoid AlgebraClass.
-- This is what makes "Coxeter is an instance of the center" a THEOREM
-- rather than a docstring: the universal property (any map Gen → M into a
-- monoid extends UNIQUELY to a monoid homomorphism Word Gen → M, namely
-- the fold) is proved, with extend = Eval, unit = the singleton word.
--
-- So the substrate's word-algebra (Coxeter.Word, the cons-list = the free
-- term algebra for the monoid signature) is literally Free ⊣ Forgetful at
-- the monoid AlgebraClass — one instance of FreeUniversalProperty.FreeUP,
-- a sibling of the (to-wire) FreeLinearization (free module) and UPTerm
-- (free term algebra) instances.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeUniversalProperty.FreeMonoid where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; sym; trans)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-assoc; ++-identity-left; ++-identity-right)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Category.FreeOverBasis
  using (AlgebraClass; mkAlgebraClass)
open import Substrate.Category.FreeUniversalProperty using (FreeUP)
open import Substrate.Category.PresentedUniversalProperty
  using (PresentedUP; Free-as-Presented)

------------------------------------------------------------------------
-- 1. The monoid structure as an AlgebraClass.
------------------------------------------------------------------------

record MonoidOn (M : Set) : Set where
  field
    ε       : M
    _∙_     : M → M → M
    ∙-assoc : (a b c : M) → ((a ∙ b) ∙ c) ≡ (a ∙ (b ∙ c))
    ε-left  : (a : M) → (ε ∙ a) ≡ a
    ε-right : (a : M) → (a ∙ ε) ≡ a

open MonoidOn

-- monoid homomorphism: preserves ε and ∙.
MonoidHom : {M N : Set} → MonoidOn M → MonoidOn N → (M → N) → Set
MonoidHom mM mN g =
  (g (ε mM) ≡ ε mN) × ((a b : _) → g (_∙_ mM a b) ≡ _∙_ mN (g a) (g b))

monoid-class : AlgebraClass
monoid-class = mkAlgebraClass MonoidOn MonoidHom

------------------------------------------------------------------------
-- 2. Word Gen is a monoid (ε = [], ∙ = ++).
------------------------------------------------------------------------

word-monoid : (Gen : Set) → MonoidOn (Word Gen)
word-monoid Gen = record
  { ε = [] ; _∙_ = _++_
  ; ∙-assoc = ++-assoc ; ε-left = ++-identity-left ; ε-right = ++-identity-right
  }

------------------------------------------------------------------------
-- 3. The free-monoid universal property. extend = fold; the rest is the
--    classic free-monoid theorem.
------------------------------------------------------------------------

module _ (Gen : Set) where

  -- the fold: Word Gen → M for any monoid M and basis map f.
  foldW : {M : Set} → MonoidOn M → (Gen → M) → Word Gen → M
  foldW mM f []      = ε mM
  foldW mM f (g ∷ w) = _∙_ mM (f g) (foldW mM f w)

  -- the fold preserves ∙ (= ++): foldW (w₁ ++ w₂) ≡ foldW w₁ ∙ foldW w₂.
  fold-++ :
    {M : Set} (mM : MonoidOn M) (f : Gen → M) (w₁ w₂ : Word Gen) →
    foldW mM f (w₁ ++ w₂) ≡ _∙_ mM (foldW mM f w₁) (foldW mM f w₂)
  fold-++ mM f []        w₂ = sym (ε-left mM (foldW mM f w₂))
  fold-++ mM f (g ∷ w₁) w₂ =
    trans (cong (_∙_ mM (f g)) (fold-++ mM f w₁ w₂))
          (sym (∙-assoc mM (f g) (foldW mM f w₁) (foldW mM f w₂)))

  free-monoid : FreeUP monoid-class Gen (Word Gen)
  free-monoid = record
    { unit             = λ g → g ∷ []
    ; free-has         = word-monoid Gen
    ; extend           = foldW
    ; extend-preserves = λ mM f → refl , fold-++ mM f
    ; extend-extends   = λ mM f g → ε-right mM (f g)
    ; extend-unique    = uniq
    }
    where
      uniq :
        {M : Set} (mM : MonoidOn M) (f : Gen → M)
        (g : Word Gen → M) → MonoidHom (word-monoid Gen) mM g →
        ((b : Gen) → g (b ∷ []) ≡ f b) →
        (x : Word Gen) → g x ≡ foldW mM f x
      uniq mM f g (g-ε , g-∙) g-sing []      = g-ε
      uniq mM f g (g-ε , g-∙) g-sing (a ∷ w) =
        trans (g-∙ (a ∷ []) w)
              (cong₂ (_∙_ mM) (g-sing a) (uniq mM f g (g-ε , g-∙) g-sing w))

------------------------------------------------------------------------
-- 4. Coxeter.Word in the QUOTIENT half too: the free monoid is the EMPTY
--    presentation (no relations), connecting it to PresentedUP. id is the
--    quotient map and a monoid hom (refl, refl). This makes Coxeter.Word a
--    visible instance of BOTH halves of the center.
------------------------------------------------------------------------

word-as-presented :
  (Gen : Set) →
  PresentedUP monoid-class (Word Gen) (word-monoid Gen) ⊥ (λ ()) (λ ()) (Word Gen)
word-as-presented Gen =
  Free-as-Presented {monoid-class} {Word Gen} (word-monoid Gen) (refl , λ _ _ → refl)
