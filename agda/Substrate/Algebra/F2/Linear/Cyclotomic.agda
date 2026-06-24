------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Cyclotomic
--
-- Ⓕ.spectral (brick 1) — the cyclotomic polynomial Φ_p EVALUATED AT A
-- LINEAR OPERATOR. This grounds the JEA-Pi cotype's "Φ_p multiplicity"
-- input one level deeper: the cotype probe-verified that mult2/2 counts
-- the Φ_p-isotypic dimension of a cycle-space operator; this module
-- CONSTRUCTS the operator Φ_p(T) : Linear n n and machine-checks the two
-- algebraic relations the count rests on — the factor identity and, on a
-- p-orbit, the eigenvalue-1 / kernel relation x·Φ_p = Φ_p.
--
-- WHAT IS PROVED (no overclaim — these two, not the dimension count):
--   • ΦL-factor      : 𝟙 + T·Φ_p(T)  ≡  Φ_p(T) + Tᵖ   (pointwise on v;
--                       the subtraction-free (x−𝟙)·Φ_p = xᵖ−𝟙)
--   • ΦL-orbit-fixed : if Tᵖ v ≡ v then T(Φ_p(T) v) ≡ Φ_p(T) v
--                       (im Φ_p(T) ⊆ fix T — the kernel relation f090_2 counts)
--
-- METHOD (read-structure-dont-rebuild): the generic factor identity is
-- ALREADY proved over any commutative semiring in Algebra.Polynomial.
-- Cyclotomic (`geom-factor`). End(V) = Linear n n is such a structure
-- under (+L, ∘L, 𝟘L, id-L) and satisfies exactly its five laws
-- (⊕-assoc/idˡ/idʳ, ⊗-distribˡ — which holds BECAUSE the maps are linear,
-- preserves-+ — and ⊗-zeroʳ — preserves-𝟎). It is NOT instantiated
-- verbatim only because `Over` needs propositional ≡ at the carrier and
-- Linear-record equality needs funext (absent, --safe --without-K); so
-- `geom-factor`'s chain is mirrored at the operator-APPLY level (the form
-- the downstream kernel needs anyway). A matrix carrier (Vec (Vector n) n,
-- data-≡) that instantiates `Over` verbatim is the deferred alternative.
--
-- NEXT BRICK (NOT here): dim (ker Φ_p(T)) ≡ mult2 p n / 2 — the isotypic
-- dimension count. Needs kernel-as-subspace + dimension.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Cyclotomic where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
-- *ₛ-zeroʳ (c *ₛ 𝟎ⱽ ≡ 𝟎ⱽ) already lives in FromImages — reuse, don't redefine.
-- (Its carrier-locality home is F2.Vector; collapsing the FromImages/GF256 copies
--  there is a separate cleanup, out of scope here.)
open import Substrate.Algebra.F2.Linear.FromImages using (*ₛ-zeroʳ)

------------------------------------------------------------------------
-- One small vector lemma not in F2.Vector.
------------------------------------------------------------------------

-- Middle-four interchange for the commutative +ⱽ-monoid.
+ⱽ-interchange : ∀ {n} (a b c d : Vector n) →
                 ((a +ⱽ b) +ⱽ (c +ⱽ d)) ≡ ((a +ⱽ c) +ⱽ (b +ⱽ d))
+ⱽ-interchange a b c d =
  trans (+ⱽ-assoc a b (c +ⱽ d))
  (trans (cong (a +ⱽ_) (sym (+ⱽ-assoc b c d)))
  (trans (cong (λ z → a +ⱽ (z +ⱽ d)) (+ⱽ-comm b c))
  (trans (cong (a +ⱽ_) (+ⱽ-assoc c b d))
         (sym (+ⱽ-assoc a c (b +ⱽ d))))))

------------------------------------------------------------------------
-- The endomorphism structure on Linear: pointwise sum and zero map.
-- (Composition ∘L, identity id-L, preserves-𝟎 are in F2.Linear.)
------------------------------------------------------------------------

infixl 6 _+L_

-- Pointwise sum of linear maps; linear because +ⱽ is a bilinear-friendly
-- commutative monoid (preserves-+ via interchange, preserves-*ₛ via *ₛ-distrib).
_+L_ : ∀ {n m} → Linear n m → Linear n m → Linear n m
L +L M = record
  { apply        = λ v → apply L v +ⱽ apply M v
  ; preserves-+  = λ u v →
      trans (cong₂ _+ⱽ_ (preserves-+ L u v) (preserves-+ M u v))
            (+ⱽ-interchange (apply L u) (apply L v) (apply M u) (apply M v))
  ; preserves-*ₛ = λ c v →
      trans (cong₂ _+ⱽ_ (preserves-*ₛ L c v) (preserves-*ₛ M c v))
            (sym (*ₛ-distribˡ-+ⱽ c (apply L v) (apply M v)))
  }

-- The zero endomorphism (additive identity for +L).
𝟘L : ∀ {n m} → Linear n m
𝟘L = record
  { apply        = λ _ → 𝟎ⱽ
  ; preserves-+  = λ _ _ → sym (+ⱽ-identityˡ 𝟎ⱽ)
  ; preserves-*ₛ = λ c _ → sym (*ₛ-zeroʳ c)
  }

------------------------------------------------------------------------
-- Operator powers and the cyclotomic operator Φ_p(T) = Σ_{i<p} Tⁱ.
-- (Mirrors Algebra.Polynomial.Cyclotomic's `_^_`, `geomSum`, `Φ` with
--  ⊗ = ∘L, ⊕ = +L, 𝟙 = id-L, 𝟘 = 𝟘L.)
------------------------------------------------------------------------

-- powL p T = Tᵖ.
powL : ∀ {n} → ℕ → Linear n n → Linear n n
powL zero    T = id-L
powL (suc i) T = T ∘L powL i T

-- geomSumL T p = Σ_{i<p} Tⁱ.
geomSumL : ∀ {n} → Linear n n → ℕ → Linear n n
geomSumL T zero    = 𝟘L
geomSumL T (suc k) = geomSumL T k +L powL k T

-- Φ_p(T) (exactly the cyclotomic Φ_p evaluated at T when p is prime).
ΦL : ∀ {n} → Linear n n → ℕ → Linear n n
ΦL T p = geomSumL T p

------------------------------------------------------------------------
-- The factor identity, pointwise: 𝟙 + T·Φ_p(T) ≡ Φ_p(T) + Tᵖ.
-- Mirrors Cyclotomic.geom-factor; base uses preserves-𝟎, step uses
-- preserves-+ (the ⊗-distribˡ that holds because T is linear).
------------------------------------------------------------------------

ΦL-factor : ∀ {n} (T : Linear n n) (p : ℕ) (v : Vector n) →
            apply (id-L +L (T ∘L geomSumL T p)) v
              ≡ apply (geomSumL T p +L powL p T) v
ΦL-factor T zero v =
  trans (cong (v +ⱽ_) (preserves-𝟎 T))
  (trans (+ⱽ-identityʳ v)
         (sym (+ⱽ-identityˡ v)))
ΦL-factor T (suc k) v =
  trans (cong (v +ⱽ_)
              (preserves-+ T (apply (geomSumL T k) v) (apply (powL k T) v)))
  (trans (sym (+ⱽ-assoc v (apply T (apply (geomSumL T k) v))
                          (apply T (apply (powL k T) v))))
         (cong (_+ⱽ apply T (apply (powL k T) v)) (ΦL-factor T k v)))

------------------------------------------------------------------------
-- Orbit specialization — the kernel relation. On a p-orbit (Tᵖ v ≡ v),
-- (x−𝟙)·Φ_p = xᵖ−𝟙 collapses to x·Φ_p = Φ_p: every Φ_p(T)-image is
-- T-fixed (im Φ_p(T) ⊆ fix T), the eigenvalue-1 component f090_2 counts.
------------------------------------------------------------------------

ΦL-orbit-fixed : ∀ {n} (T : Linear n n) (p : ℕ) (v : Vector n) →
                 apply (powL p T) v ≡ v →
                 apply T (apply (ΦL T p) v) ≡ apply (ΦL T p) v
ΦL-orbit-fixed T p v hyp =
  trans (sym (+ⱽ-identityˡ tΦv))
  (trans (cong (_+ⱽ tΦv) (sym (+ⱽ-self-inverse v)))
  (trans (+ⱽ-assoc v v tΦv)
  (trans (cong (v +ⱽ_) eq)
  (trans (cong (v +ⱽ_) (+ⱽ-comm Φv v))
  (trans (sym (+ⱽ-assoc v v Φv))
  (trans (cong (_+ⱽ Φv) (+ⱽ-self-inverse v))
         (+ⱽ-identityˡ Φv)))))))
  where
    Φv  = apply (ΦL T p) v
    tΦv = apply T Φv
    eq : (v +ⱽ tΦv) ≡ (Φv +ⱽ v)
    eq = trans (ΦL-factor T p v) (cong (Φv +ⱽ_) hyp)
