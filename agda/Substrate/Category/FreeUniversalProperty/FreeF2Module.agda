------------------------------------------------------------------------
-- Substrate.Category.FreeUniversalProperty.FreeF2Module
--
-- The flagship architecture-TEST instance: the free F₂-module on a finite
-- basis Fin k IS Vector k, proved as a content-bearing FreeUP for a NEW
-- signature (F₂-module: commutative, self-inverse) into an ARBITRARY F₂-
-- module M — not the concrete-target shortcut linear-from-images takes.
--
-- This is the "real catch" flagged earlier: linear-from-images only maps
-- into Vector n, so the generic free-module universal property had to be
-- PROVED, not wired. extend = the sum over the basis; uniqueness = linear-
-- extensionality, by induction through the (𝟘 ∷_) embedding.
--
-- The point of the test (per the user: "if reducibility keeps giving false
-- positives, we have an architecture problem"): this instance carries real
-- content and does NOT collapse to ⊤. The F₂ self-inverse axiom is LOAD-
-- BEARING — additivity of extend genuinely uses m ⊕ m ≡ 𝟎 (the a=b=𝟙 case
-- of scalar distribution). A vacuous "instance" could not need it. So the
-- center (FreeUP) passes the test on a second, genuinely different signature.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeUniversalProperty.FreeF2Module where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; sym; trans)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; +-identityʳ)
open import Substrate.Algebra.F2.Vector
  using (Vector; 𝟎ⱽ; _+ⱽ_; basis;
         +ⱽ-identityˡ; +ⱽ-identityʳ; +ⱽ-assoc; +ⱽ-comm; +ⱽ-self-inverse)
open import Substrate.Category.FreeOverBasis using (AlgebraClass; mkAlgebraClass)
open import Substrate.Category.FreeUniversalProperty using (FreeUP)
open import Substrate.Algebra.Medial using (medial)

------------------------------------------------------------------------
-- 1. The F₂-module structure (= F₂-vector space: abelian, self-inverse).
------------------------------------------------------------------------

record F2Mod (M : Set) : Set where
  field
    𝟎       : M
    _⊕_     : M → M → M
    ⊕-assoc : (a b c : M) → ((a ⊕ b) ⊕ c) ≡ (a ⊕ (b ⊕ c))
    ⊕-comm  : (a b : M) → (a ⊕ b) ≡ (b ⊕ a)
    ⊕-idˡ   : (a : M) → (𝟎 ⊕ a) ≡ a
    ⊕-idʳ   : (a : M) → (a ⊕ 𝟎) ≡ a
    ⊕-self  : (a : M) → (a ⊕ a) ≡ 𝟎

F2ModHom : {M N : Set} → F2Mod M → F2Mod N → (M → N) → Set
F2ModHom mM mN g =
  (g (F2Mod.𝟎 mM) ≡ F2Mod.𝟎 mN) ×
  ((a b : _) → g (F2Mod._⊕_ mM a b) ≡ F2Mod._⊕_ mN (g a) (g b))

f2mod-class : AlgebraClass
f2mod-class = mkAlgebraClass F2Mod F2ModHom

-- Vector k is an F₂-module (the free carrier).
vector-F2Mod : (k : ℕ) → F2Mod (Vector k)
vector-F2Mod k = record
  { 𝟎 = 𝟎ⱽ ; _⊕_ = _+ⱽ_
  ; ⊕-assoc = +ⱽ-assoc ; ⊕-comm = +ⱽ-comm
  ; ⊕-idˡ = +ⱽ-identityˡ ; ⊕-idʳ = +ⱽ-identityʳ ; ⊕-self = +ⱽ-self-inverse
  }

------------------------------------------------------------------------
-- 2. The free-module universal property, for a fixed target module M.
------------------------------------------------------------------------

module _ {M : Set} (Mod : F2Mod M) where
  open F2Mod Mod

  -- F₂ scalar action: 𝟙·m = m, 𝟘·m = 𝟎.
  _·?_ : F₂ → M → M
  𝟘 ·? m = 𝟎
  𝟙 ·? m = m

  -- extend = the sum over the basis (recursion on the vector).
  ext : {k : ℕ} → (Fin k → M) → Vector k → M
  ext {zero}  f []      = 𝟎
  ext {suc k} f (b ∷ v) = (b ·? f zero) ⊕ ext (λ i → f (suc i)) v

  -- abelian rearrangement (a⊕b)⊕(c⊕d) ≡ (a⊕c)⊕(b⊕d).
  -- Ⓜ: the 4-term rearrange = the medial law (Algebra.Medial) at M's `⊕`.
  rearrange : (a b c d : M) → ((a ⊕ b) ⊕ (c ⊕ d)) ≡ ((a ⊕ c) ⊕ (b ⊕ d))
  rearrange = medial _⊕_ ⊕-assoc ⊕-comm

  -- scalar distributes over F₂ addition — the a=b=𝟙 case USES ⊕-self.
  scalar-dist : (a b : F₂) (m : M) → ((a + b) ·? m) ≡ ((a ·? m) ⊕ (b ·? m))
  scalar-dist 𝟘 𝟘 m = sym (⊕-idˡ 𝟎)
  scalar-dist 𝟘 𝟙 m = sym (⊕-idˡ m)
  scalar-dist 𝟙 𝟘 m = sym (⊕-idʳ m)
  scalar-dist 𝟙 𝟙 m = sym (⊕-self m)

  -- ext sends the zero vector to 𝟎.
  ext-zero : {k : ℕ} (f : Fin k → M) → ext f 𝟎ⱽ ≡ 𝟎
  ext-zero {zero}  f = refl
  ext-zero {suc k} f = trans (⊕-idˡ _) (ext-zero (λ i → f (suc i)))

  -- ext is additive (preserves +ⱽ ↦ ⊕).
  ext-+ : {k : ℕ} (f : Fin k → M) (u v : Vector k) →
          ext f (u +ⱽ v) ≡ (ext f u ⊕ ext f v)
  ext-+ {zero}  f [] [] = sym (⊕-idˡ 𝟎)
  ext-+ {suc k} f (a ∷ u) (b ∷ v) =
    trans (cong₂ _⊕_ (scalar-dist a b (f zero)) (ext-+ (λ i → f (suc i)) u v))
          (rearrange (a ·? f zero) (b ·? f zero)
                     (ext (λ i → f (suc i)) u) (ext (λ i → f (suc i)) v))

  -- ext agrees with f on basis vectors.
  ext-basis : {k : ℕ} (f : Fin k → M) (i : Fin k) → ext f (basis i) ≡ f i
  ext-basis f zero    = trans (cong (f zero ⊕_) (ext-zero (λ i → f (suc i))))
                              (⊕-idʳ (f zero))
  ext-basis f (suc i) = trans (⊕-idˡ _) (ext-basis (λ j → f (suc j)) i)

  -- UNIQUENESS (linear-extensionality): any module-hom g agreeing with f
  -- on basis equals ext. Induction via the (𝟘 ∷_) embedding.
  ext-unique :
    {k : ℕ} (f : Fin k → M) (g : Vector k → M) →
    (g 𝟎ⱽ ≡ 𝟎) → ((u v : Vector k) → g (u +ⱽ v) ≡ (g u ⊕ g v)) →
    ((i : Fin k) → g (basis i) ≡ f i) →
    (x : Vector k) → g x ≡ ext f x
  ext-unique {zero}  f g g-𝟎 g-+ g-sing []      = g-𝟎
  ext-unique {suc k} f g g-𝟎 g-+ g-sing (b ∷ v) =
    trans (cong g split)
      (trans (g-+ (b ∷ 𝟎ⱽ) (𝟘 ∷ v))
        (cong₂ _⊕_ (g-head b)
          (ext-unique (λ i → f (suc i)) (λ w → g (𝟘 ∷ w))
            g-𝟎 (λ u w → g-+ (𝟘 ∷ u) (𝟘 ∷ w)) (λ i → g-sing (suc i)) v)))
    where
      split : (b ∷ v) ≡ ((b ∷ 𝟎ⱽ) +ⱽ (𝟘 ∷ v))
      split = sym (cong₂ _∷_ (+-identityʳ b) (+ⱽ-identityˡ v))
      g-head : (b' : F₂) → g (b' ∷ 𝟎ⱽ) ≡ (b' ·? f zero)
      g-head 𝟘 = g-𝟎
      g-head 𝟙 = g-sing zero

------------------------------------------------------------------------
-- 3. THE INSTANCE: Vector k is the free F₂-module on Fin k.
------------------------------------------------------------------------

free-F2Module : (k : ℕ) → FreeUP f2mod-class (Fin k) (Vector k)
free-F2Module k = record
  { unit             = basis
  ; free-has         = vector-F2Mod k
  ; extend           = λ hM f → ext hM f
  ; extend-preserves = λ hM f → ext-zero hM f , ext-+ hM f
  ; extend-extends   = λ hM f i → ext-basis hM f i
  ; extend-unique    =
      λ hM f g g-hom g-sing x →
        ext-unique hM f g (proj₁ g-hom) (proj₂ g-hom) g-sing x
  }
  where open import Substrate.Foundation.Product using (proj₁; proj₂)
