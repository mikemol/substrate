------------------------------------------------------------------------
-- Substrate.Category.PresentedUniversalProperty.SnAbelianizationZ2
--
-- ◆ip-cap-categorical (Route C) — the categorical headline Sₙ^ab ≅ Z/2,
-- computed SYNTACTICALLY from the abelianised Coxeter presentation, as a
-- content-bearing PresentedUP (like CyclicZ2, but MULTI-generator).
--
--   Free(s₀..sₙ)  ──quotient (parity)──▶  Presented = Sₙ^ab = F₂ = Z/2
--
-- The presentation (n+1 generators = the Coxeter generators of Sₙ₊₂):
--   generators  : Fin (suc n)                    (the sᵢ, abstract tokens)
--   involution  : sᵢ² = ε
--   commute     : sᵢ sⱼ = sⱼ sᵢ    (ALL pairs — this is the abelianising R)
--   braid       : sᵢ sᵢ₊₁ sᵢ = sᵢ₊₁ sᵢ sᵢ₊₁      (adjacent, via weaken/suc)
-- The presented object is F₂ with quotient = parity (word length mod 2) =
-- the free extension sending every generator ↦ 𝟙.
--
-- THE NET-NEW MATHEMATICAL CONTENT (`gen-eq`/`collapse`): in ANY monoid
-- image respecting these relations, braid + commute + involution FORCE
-- every h(sᵢ) equal to a common g with g² = ε — so h factors through
-- parity : Fin(suc n)* → F₂. Without braid the abelianisation would be
-- (Z/2)ⁿ⁺¹; braid (chained along the adjacency path) is exactly what
-- collapses it to one bit. That collapse IS the whole theorem.
--
-- DESIGN (deviates from the plan's Route C, which specified a
-- `comm-monoid-class` + `word-commmonoid`): `CommMonoidOn (Word Gen)` is
-- NOT constructible — word concatenation is not commutative. So instead
-- the target class stays the PLAIN `monoid-class` (F = Word Gen, already
-- built) and commutativity lives in R as the `commute` relations. This
-- reuses CyclicZ2's imports verbatim, needs no new AlgebraClass and no
-- funext (which the free-commutative-monoid alternative would demand).
--
-- HONEST CEILING: this is Sₙ^ab ≅ Z/2 for the PRESENTED group. It does
-- NOT certify that the presented monoid ≅ the concrete `Perm n` Sₙ (that
-- = word-completeness / Matsumoto, or ◆ip-cap-reverse's R4′) — the sole
-- remaining genuinely-new residue, ◆ip-cap-concrete-bridge.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PresentedUniversalProperty.SnAbelianizationZ2 where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; suc-injective)
open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fzero; suc to fsuc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; +-assoc; +-identityˡ; +-identityʳ)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid
  using (MonoidOn; MonoidHom; monoid-class; word-monoid; foldW; word-extend-preserves)
open import Substrate.Category.PresentedUniversalProperty using (PresentedUP)

------------------------------------------------------------------------
-- 0. weaken (inject₁): the position-preserving Fin n → Fin (suc n).
--    `braid j` (j : Fin n) relates the adjacent generators `weaken j`
--    (position j) and `fsuc j` (position j+1), both in Fin (suc n).
------------------------------------------------------------------------

weaken : {m : ℕ} → Fin m → Fin (suc m)
weaken fzero    = fzero
weaken (fsuc i) = fsuc (weaken i)

weaken-toℕ : {m : ℕ} (i : Fin m) → toℕ (weaken i) ≡ toℕ i
weaken-toℕ fzero    = refl
weaken-toℕ (fsuc i) = cong suc (weaken-toℕ i)

module _ (n : ℕ) where

  Gen : Set
  Gen = Fin (suc n)

  ------------------------------------------------------------------------
  -- 1. The presentation data: relations + their two sides.
  ------------------------------------------------------------------------

  data Rel : Set where
    involution : Gen → Rel               -- sᵢ² = ε
    commute    : Gen → Gen → Rel         -- sᵢ sⱼ = sⱼ sᵢ  (all pairs)
    braid      : Fin n → Rel             -- sᵢ sᵢ₊₁ sᵢ = sᵢ₊₁ sᵢ sᵢ₊₁

  lhs rhs : Rel → Word Gen
  lhs (involution i) = i ∷ i ∷ []
  lhs (commute i j)  = i ∷ j ∷ []
  lhs (braid j)      = weaken j ∷ fsuc j ∷ weaken j ∷ []
  rhs (involution i) = []
  rhs (commute i j)  = j ∷ i ∷ []
  rhs (braid j)      = fsuc j ∷ weaken j ∷ fsuc j ∷ []

  ------------------------------------------------------------------------
  -- 2. The presented object F₂ with quotient = parity (gen ↦ 𝟙).
  --    Its carrier F₂ already has proven additive group structure.
  ------------------------------------------------------------------------

  z2-monoid : MonoidOn F₂
  z2-monoid = record
    { ε = 𝟘 ; _∙_ = _+_
    ; ∙-assoc = +-assoc ; ε-left = +-identityˡ ; ε-right = +-identityʳ
    }

  quotient : Word Gen → F₂
  quotient = foldW Gen z2-monoid (λ _ → 𝟙)

  quotient-hom : MonoidHom (word-monoid Gen) z2-monoid quotient
  quotient-hom = word-extend-preserves Gen z2-monoid (λ _ → 𝟙)

  -- parity of both sides of every relation agrees (all refl: even/even,
  -- 3/3 — F₂ computes). This is `quotient-respects`.
  quotient-respects : (r : Rel) → quotient (lhs r) ≡ quotient (rhs r)
  quotient-respects (involution i) = refl
  quotient-respects (commute i j)  = refl
  quotient-respects (braid j)      = refl

  ------------------------------------------------------------------------
  -- 3. The factorization, for a relation-respecting monoid hom h.
  ------------------------------------------------------------------------

  module _ {M : Set} (hM : MonoidOn M) (h : Word Gen → M)
           (h-hom : MonoidHom (word-monoid Gen) hM h)
           (hr : (r : Rel) → h (lhs r) ≡ h (rhs r)) where

    open MonoidOn hM renaming (ε to εM; _∙_ to _∙M_; ∙-assoc to assocM; ε-left to ε-lM)

    -- h on a single generator, and its computation on 2- and 3-letter words.
    hg : Gen → M
    hg i = h (i ∷ [])

    h2 : (a b : Gen) → h (a ∷ b ∷ []) ≡ (hg a ∙M hg b)
    h2 a b = proj₂ h-hom (a ∷ []) (b ∷ [])

    h3 : (a b c : Gen) → h (a ∷ b ∷ c ∷ []) ≡ (hg a ∙M (hg b ∙M hg c))
    h3 a b c = trans (proj₂ h-hom (a ∷ []) (b ∷ c ∷ []))
                     (cong (hg a ∙M_) (proj₂ h-hom (b ∷ []) (c ∷ [])))

    ------------------------------------------------------------------------
    -- 3a. THE COLLAPSE. braid + commute + involution ⟹ adjacent generators
    --     have equal image; chaining along the path ⟹ all equal to hg fzero.
    ------------------------------------------------------------------------

    -- one braid step: hg (fsuc j) ≡ hg (weaken j).
    -- x·y·x = y (x²=ε, xy=yx) and y·x·y = x, so h(braid-lhs)=h(braid-rhs)
    -- gives y = x directly.
    braid-eq : (j : Fin n) → hg (fsuc j) ≡ hg (weaken j)
    braid-eq j = trans (sym sx) (trans braid-raw sy)
      where
        x y : M
        x = hg (weaken j)
        y = hg (fsuc j)
        inv-x : (x ∙M x) ≡ εM
        inv-x = trans (sym (h2 (weaken j) (weaken j)))
                      (trans (hr (involution (weaken j))) (proj₁ h-hom))
        inv-y : (y ∙M y) ≡ εM
        inv-y = trans (sym (h2 (fsuc j) (fsuc j)))
                      (trans (hr (involution (fsuc j))) (proj₁ h-hom))
        comm-xy : (x ∙M y) ≡ (y ∙M x)
        comm-xy = trans (sym (h2 (weaken j) (fsuc j)))
                        (trans (hr (commute (weaken j) (fsuc j))) (h2 (fsuc j) (weaken j)))
        braid-raw : (x ∙M (y ∙M x)) ≡ (y ∙M (x ∙M y))
        braid-raw = trans (sym (h3 (weaken j) (fsuc j) (weaken j)))
                          (trans (hr (braid j)) (h3 (fsuc j) (weaken j) (fsuc j)))
        sx : (x ∙M (y ∙M x)) ≡ y
        sx = trans (cong (x ∙M_) (sym comm-xy))
                   (trans (sym (assocM x x y)) (trans (cong (_∙M y) inv-x) (ε-lM y)))
        sy : (y ∙M (x ∙M y)) ≡ x
        sy = trans (cong (y ∙M_) comm-xy)
                   (trans (sym (assocM y y x)) (trans (cong (_∙M x) inv-y) (ε-lM x)))

    -- all generators collapse to hg fzero (chain the braid steps along
    -- the adjacency path; recursion on toℕ i keeps it structural).
    collapse-at : (m : ℕ) (i : Gen) → toℕ i ≡ m → hg i ≡ hg fzero
    collapse-at zero    fzero    _  = refl
    collapse-at zero    (fsuc j) ()
    collapse-at (suc m) fzero    ()
    collapse-at (suc m) (fsuc j) eq =
      trans (braid-eq j)
            (collapse-at m (weaken j) (trans (weaken-toℕ j) (suc-injective eq)))

    collapse : (i : Gen) → hg i ≡ hg fzero
    collapse i = collapse-at (toℕ i) i refl

    ------------------------------------------------------------------------
    -- 3b. fac : F₂ → M and the universal-property witnesses (mirroring
    --     CyclicZ2, with the base generator fzero and the collapse).
    ------------------------------------------------------------------------

    fac : F₂ → M
    fac 𝟘 = h []
    fac 𝟙 = h (fzero ∷ [])

    -- fac is a monoid hom Z₂ → M. The 𝟙·𝟙 case USES involution (of fzero).
    fac-pres : MonoidHom z2-monoid hM fac
    fac-pres = proj₁ h-hom , dist
      where
        dist : (u v : F₂) → fac (u + v) ≡ (fac u ∙M fac v)
        dist 𝟘 𝟘 = proj₂ h-hom [] []
        dist 𝟘 𝟙 = proj₂ h-hom [] (fzero ∷ [])
        dist 𝟙 𝟘 = proj₂ h-hom (fzero ∷ []) []
        dist 𝟙 𝟙 = trans (sym (hr (involution fzero)))
                         (proj₂ h-hom (fzero ∷ []) (fzero ∷ []))

    -- fac ∘ quotient ≡ h. The (i ∷ w) step uses `collapse i` (hg i = hg fzero).
    fac-factors : (w : Word Gen) → fac (quotient w) ≡ h w
    fac-factors []       = refl
    fac-factors (i ∷ w) =
      trans (proj₂ fac-pres 𝟙 (quotient w))
        (trans (cong (fac 𝟙 ∙M_) (fac-factors w))
          (trans (cong (_∙M h w) (sym (collapse i)))
                 (sym (proj₂ h-hom (i ∷ []) w))))

    -- uniqueness: any hom k with k ∘ quotient ≡ h equals fac (F₂ has 2 pts).
    fac-unique :
      (k : F₂ → M) → MonoidHom z2-monoid hM k →
      ((w : Word Gen) → k (quotient w) ≡ h w) →
      (y : F₂) → k y ≡ fac y
    fac-unique k k-hom k-ext 𝟘 = k-ext []
    fac-unique k k-hom k-ext 𝟙 = k-ext (fzero ∷ [])

  ------------------------------------------------------------------------
  -- 4. THE INSTANCE: Sₙ^ab as the abelianised Coxeter presentation, ≅ Z/2.
  ------------------------------------------------------------------------

  Sₙ-ab-Z2 :
    PresentedUP monoid-class (Word Gen) (word-monoid Gen) Rel lhs rhs F₂
      quotient z2-monoid fac fac-pres fac-factors fac-unique
  Sₙ-ab-Z2 = record
    { quotient-hom      = quotient-hom
    ; quotient-respects = quotient-respects
    }
