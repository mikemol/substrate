------------------------------------------------------------------------
-- Substrate.Category.PresentedUniversalProperty.CyclicZ2
--
-- The architecture test on the QUOTIENT half, with a REAL (nonempty)
-- relation: the cyclic group Z₂ = ⟨ a | a² = ε ⟩ as a content-bearing
-- PresentedUP. Every prior PresentedUP instance was the empty presentation
-- (R = ⊥, trivial); this one has an actual relation and proves the full
-- coequalizer universal property.
--
--   free monoid Word ⊤  ──quotient (parity)──▶  Z₂ = F₂
--
-- Carrier of the presented object is F₂ (whose +/assoc/identity ARE proved
-- in Algebra.F2), quotient = parity = the free extension foldW into (F₂,𝟘,+)
-- sending a ↦ 𝟙 (so quotient-hom is literally the free monoid's
-- extend-preserves — reuse, not reproof). The relation a² = ε is
-- LOAD-BEARING: the 𝟙·𝟙 case of factor-preservation is exactly where
-- h(a²) ≡ h(ε) is used. A vacuous instance could not need it — so the
-- quotient half passes the same test the free F₂-module passed.
--
-- This is the Z₂ proof-of-concept for the cyclic family. GENERIC Z_m needs
-- the Fin mod-group-laws + power-periodicity + mod-addition-homomorphism
-- (the EEA/CRT/Totient substrate), a number-theory arc not yet in-tree
-- (Sites.Zn has add-mod but its laws are unproven). Z₂ works here because
-- its carrier F₂ already has proven group structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PresentedUniversalProperty.CyclicZ2 where

open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; +-assoc; +-identityˡ; +-identityʳ)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid
  using (MonoidOn; MonoidHom; monoid-class; word-monoid; foldW;
         word-extend-preserves)
open import Substrate.Category.PresentedUniversalProperty using (PresentedUP)

------------------------------------------------------------------------
-- 1. The presentation data.
------------------------------------------------------------------------

a a² : Word ⊤
a  = tt ∷ []
a² = tt ∷ tt ∷ []

-- Z₂'s carrier is F₂ with its (proven) additive group structure.
z2-monoid : MonoidOn F₂
z2-monoid = record
  { ε = 𝟘 ; _∙_ = _+_
  ; ∙-assoc = +-assoc ; ε-left = +-identityˡ ; ε-right = +-identityʳ
  }

-- the quotient = parity = the free extension sending a ↦ 𝟙.
quotient : Word ⊤ → F₂
quotient = foldW ⊤ z2-monoid (λ _ → 𝟙)

-- quotient is a monoid hom — REUSE the free monoid's universal property.
quotient-hom : MonoidHom (word-monoid ⊤) z2-monoid quotient
quotient-hom = word-extend-preserves ⊤ z2-monoid (λ _ → 𝟙)

------------------------------------------------------------------------
-- 2. The factorization, for a relation-respecting monoid hom h.
------------------------------------------------------------------------

module _ {M : Set} (hM : MonoidOn M) (h : Word ⊤ → M)
         (h-hom : MonoidHom (word-monoid ⊤) hM h)
         (h-resp : (r : ⊤) → h a² ≡ h []) where

  open MonoidOn hM renaming (ε to εM; _∙_ to _∙M_; ε-left to ε-lM; ε-right to ε-rM)

  fac : F₂ → M
  fac 𝟘 = h []
  fac 𝟙 = h a

  -- fac is a monoid hom Z₂ → M. The 𝟙·𝟙 case USES the relation a² = ε.
  fac-pres : MonoidHom z2-monoid hM fac
  fac-pres = proj₁ h-hom , dist
    where
      dist : (x y : F₂) → fac (x + y) ≡ (fac x ∙M fac y)
      dist 𝟘 𝟘 = proj₂ h-hom [] []
      dist 𝟘 𝟙 = proj₂ h-hom [] a
      dist 𝟙 𝟘 = proj₂ h-hom a []
      dist 𝟙 𝟙 = trans (sym (h-resp tt)) (proj₂ h-hom a a)

  -- fac ∘ quotient ≡ h (the factorization).
  fac-factors : (w : Word ⊤) → fac (quotient w) ≡ h w
  fac-factors []        = refl
  fac-factors (tt ∷ w) =
    trans (proj₂ fac-pres 𝟙 (quotient w))
      (trans (cong (fac 𝟙 ∙M_) (fac-factors w))
             (sym (proj₂ h-hom a w)))

  -- uniqueness: any hom k with k ∘ quotient ≡ h equals fac (F₂ has 2 pts).
  fac-unique :
    (k : F₂ → M) → MonoidHom z2-monoid hM k →
    ((w : Word ⊤) → k (quotient w) ≡ h w) →
    (y : F₂) → k y ≡ fac y
  fac-unique k k-hom k-ext 𝟘 = k-ext []
  fac-unique k k-hom k-ext 𝟙 = k-ext a

------------------------------------------------------------------------
-- 3. THE INSTANCE: Z₂ as a nonempty presentation.
------------------------------------------------------------------------

cyclic-Z2 :
  PresentedUP monoid-class (Word ⊤) (word-monoid ⊤) ⊤ (λ _ → a²) (λ _ → []) F₂
    quotient z2-monoid fac fac-pres fac-factors fac-unique
cyclic-Z2 = record
  { quotient-hom      = quotient-hom
  ; quotient-respects = λ _ → refl
  }
