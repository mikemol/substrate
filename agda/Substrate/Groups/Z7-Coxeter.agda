------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter
--
-- ℤ/7ℤ as a Coxeter-style presentation: ⟨a | a⁷ = ε⟩.
--
-- Mirror of Substrate.Groups.Z3/Z4/Z5-Coxeter at n=7: explicit
-- Canonical constructors c-ε through c-a⁶ (7 in total), insert wraps
-- at length 7, seventh-power-identity replaces the lower-n versions.
--
-- Built as the Sylow-7 carrier for the GL(3, F₂) ≅ PSL(2, 7) work
-- (per [[multi-route-equivariance-recovery]] +
-- [[klein-quartic-kinematic-anatomy]]): the 168-tower-as-fanout
-- decomposes as 2³ · 3 · 7, and the order-7 cyclic component (Singer
-- cyclic on the Fano plane) lives here.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: fourth concrete
-- instance in the Zₙ-Coxeter family (n=2, 3, 4, 5, now 7); the pattern
-- continues to scale mechanically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter where

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; _≢_)

------------------------------------------------------------------------
-- 1. Z/7-specific data.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

data Canonical : Word Gen → Set where
  c-ε      : Canonical []
  c-a      : Canonical (a ∷ [])
  c-aa     : Canonical (a ∷ a ∷ [])
  c-aaa    : Canonical (a ∷ a ∷ a ∷ [])
  c-aaaa   : Canonical (a ∷ a ∷ a ∷ a ∷ [])
  c-aaaaa  : Canonical (a ∷ a ∷ a ∷ a ∷ a ∷ [])
  c-aaaaaa : Canonical (a ∷ a ∷ a ∷ a ∷ a ∷ a ∷ [])

------------------------------------------------------------------------
-- 2. The insert step: encodes a⁷ = ε as a 7-cyclic wrap on canonical
-- forms — [] → [a] → [a,a] → … → [a,a,a,a,a,a] → [].
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert a []                           = a ∷ []
insert a (a ∷ [])                     = a ∷ a ∷ []
insert a (a ∷ a ∷ [])                 = a ∷ a ∷ a ∷ []
insert a (a ∷ a ∷ a ∷ [])             = a ∷ a ∷ a ∷ a ∷ []
insert a (a ∷ a ∷ a ∷ a ∷ [])         = a ∷ a ∷ a ∷ a ∷ a ∷ []
insert a (a ∷ a ∷ a ∷ a ∷ a ∷ [])     = a ∷ a ∷ a ∷ a ∷ a ∷ a ∷ []
insert a (a ∷ a ∷ a ∷ a ∷ a ∷ a ∷ []) = []
insert g w                            = g ∷ w  -- fallback (unreachable for Canonical inputs)

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical a c-ε      = c-a
insert-canonical a c-a      = c-aa
insert-canonical a c-aa     = c-aaa
insert-canonical a c-aaa    = c-aaaa
insert-canonical a c-aaaa   = c-aaaaa
insert-canonical a c-aaaaa  = c-aaaaaa
insert-canonical a c-aaaaaa = c-ε

------------------------------------------------------------------------
-- Canonical-cover for Z₇: dispatches a 7-tuple of per-position
-- proofs onto any `Canonical w`. Heterogeneous-output via each
-- refl's own implicit {x}.
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (_×_; _,_)

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa × P c-aaa × P c-aaaa × P c-aaaaa × P c-aaaaaa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _ , _ , _ , _ , _) c-ε      = p
canonical-cover _ (_ , p , _ , _ , _ , _ , _) c-a      = p
canonical-cover _ (_ , _ , p , _ , _ , _ , _) c-aa     = p
canonical-cover _ (_ , _ , _ , p , _ , _ , _) c-aaa    = p
canonical-cover _ (_ , _ , _ , _ , p , _ , _) c-aaaa   = p
canonical-cover _ (_ , _ , _ , _ , _ , p , _) c-aaaaa  = p
canonical-cover _ (_ , _ , _ , _ , _ , _ , p) c-aaaaaa = p

------------------------------------------------------------------------
-- 3. Open ListPresentation with Z/7's atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 4. Per-relation obligations.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover (λ {w} _ → normalize w ≡ w)
    (refl , refl , refl , refl , refl , refl , refl)

insert-cycle-id : (g : Gen) {w : Word Gen} → Canonical w →
                       insert g (insert g (insert g (insert g
                              (insert g (insert g (insert g w)))))) ≡ w
insert-cycle-id a = canonical-cover
  (λ {w} _ → insert a (insert a (insert a (insert a
              (insert a (insert a (insert a w)))))) ≡ w)
  (refl , refl , refl , refl , refl , refl , refl)

insert-append-lemma :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma a {[]}                           w₂ c-ε      = refl
insert-append-lemma a {a ∷ []}                       w₂ c-a      = refl
insert-append-lemma a {a ∷ a ∷ []}                   w₂ c-aa     = refl
insert-append-lemma a {a ∷ a ∷ a ∷ []}               w₂ c-aaa    = refl
insert-append-lemma a {a ∷ a ∷ a ∷ a ∷ []}           w₂ c-aaaa   = refl
insert-append-lemma a {a ∷ a ∷ a ∷ a ∷ a ∷ []}       w₂ c-aaaaa  = refl
insert-append-lemma a {a ∷ a ∷ a ∷ a ∷ a ∷ a ∷ []}   w₂ c-aaaaaa =
  sym (insert-cycle-id a (normalize-canonical w₂))

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed insert-append-lemma public

------------------------------------------------------------------------
-- 6. Inversion on canonical forms — Z/7 (prime-order cyclic):
--   inv []              = []
--   inv [a]             = [a,a,a,a,a,a]   (a⁻¹ = a⁶)
--   inv [a,a]           = [a,a,a,a,a]     ((a²)⁻¹ = a⁵)
--   inv [a,a,a]         = [a,a,a,a]       ((a³)⁻¹ = a⁴)
--   inv [a,a,a,a]       = [a,a,a]         ((a⁴)⁻¹ = a³)
--   inv [a,a,a,a,a]     = [a,a]           ((a⁵)⁻¹ = a²)
--   inv [a,a,a,a,a,a]   = [a]             ((a⁶)⁻¹ = a)
-- Z/7 has no non-trivial subgroups (prime order); every non-identity
-- element generates the full group.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv []                           = []
inv (a ∷ [])                     = a ∷ a ∷ a ∷ a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ [])                 = a ∷ a ∷ a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ [])             = a ∷ a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ a ∷ [])         = a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ a ∷ a ∷ [])     = a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ a ∷ a ∷ a ∷ []) = a ∷ []
inv w                            = w  -- fallback

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical c-ε      = c-ε
inv-canonical c-a      = c-aaaaaa
inv-canonical c-aa     = c-aaaaa
inv-canonical c-aaa    = c-aaaa
inv-canonical c-aaaa   = c-aaa
inv-canonical c-aaaaa  = c-aa
inv-canonical c-aaaaaa = c-a

------------------------------------------------------------------------
-- 7. Z/7-specific theorem: every element to the seventh equals ε.
------------------------------------------------------------------------

private
  flatten-sept-self-product :
    (w : Word Gen) →
    normalize ((((((w · w) · w) · w) · w) · w) · w) ≡
    normalize (normalize w ++ (normalize w ++
               (normalize w ++ (normalize w ++
                (normalize w ++ (normalize w ++ normalize w))))))
  flatten-sept-self-product w =
    trans (normalize-idem ((normalize ((normalize ((normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) ++ w)) ++ w)) ++ w))
    (trans (sym (normalize-append ((normalize ((normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) ++ w)) ++ w) w))
    (trans (cong normalize (++-assoc (normalize ((normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) ++ w)) w w))
    (trans (sym (normalize-append (normalize ((normalize ((normalize (w ++ w) ++ w)) ++ w)) ++ w) (w ++ w)))
    (trans (cong normalize (++-assoc (normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) w (w ++ w)))
    (trans (sym (normalize-append ((normalize (normalize (w ++ w) ++ w)) ++ w) (w ++ (w ++ w))))
    (trans (cong normalize (++-assoc (normalize (normalize (w ++ w) ++ w)) w (w ++ (w ++ w))))
    (trans (sym (normalize-append (normalize (w ++ w) ++ w) (w ++ (w ++ (w ++ w)))))
    (trans (cong normalize (++-assoc (normalize (w ++ w)) w (w ++ (w ++ (w ++ w)))))
    (trans (sym (normalize-append (w ++ w) (w ++ (w ++ (w ++ (w ++ w))))))
    (trans (cong normalize (++-assoc w w (w ++ (w ++ (w ++ (w ++ w))))))
           (normalize-sept w w w w w w w)))))))))))

  seventh-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ (w ++ (w ++ (w ++ (w ++ (w ++ w)))))) ≡ []
  seventh-canonical = canonical-cover
    (λ {w} _ → normalize (w ++ (w ++ (w ++ (w ++ (w ++ (w ++ w)))))) ≡ [])
    (refl , refl , refl , refl , refl , refl , refl)

seventh-power-identity : (w : Word Gen) → ((((((w · w) · w) · w) · w) · w) · w) ≈ ε
seventh-power-identity w =
  trans (flatten-sept-self-product w)
        (seventh-canonical (normalize-canonical w))

------------------------------------------------------------------------
-- 8. Inverse-composition theorems on canonical forms.
------------------------------------------------------------------------

inv-left-canonical : {w : Word Gen} → Canonical w →
                     normalize (inv w ++ w) ≡ []
inv-left-canonical = canonical-cover
  (λ {w} _ → normalize (inv w ++ w) ≡ [])
  (refl , refl , refl , refl , refl , refl , refl)

inv-right-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ inv w) ≡ []
inv-right-canonical = canonical-cover
  (λ {w} _ → normalize (w ++ inv w) ≡ [])
  (refl , refl , refl , refl , refl , refl , refl)

------------------------------------------------------------------------
-- 9. inv is involutive on canonical forms.
------------------------------------------------------------------------

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical = canonical-cover
  (λ {w} _ → inv (inv w) ≡ w)
  (refl , refl , refl , refl , refl , refl , refl)
