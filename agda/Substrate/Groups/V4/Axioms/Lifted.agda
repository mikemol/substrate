------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.Lifted
--
-- V₄ group axioms derived by CONJUGATION through the Coxeter
-- bijection (to-c / from-c), rather than per-ctor refl enumeration.
--
-- Each V₄-level axiom is a 1-to-5-line trans-chain that lifts a
-- generic Coxeter-Word-level fact (++-assoc, ++-identity-{left,right},
-- normalize-{idem,append,append-right}, canonical-is-fixed-V4) through
-- the V₄ ↔ Word bijection. No 4/16/64-case refl block at the V₄ level.
--
-- Pattern (per [[feedback-categorical-name-first]]):
--
--   ε-left x = trans (cong from-c <Coxeter-side-theorem>) (from-to x)
--
-- This is "F1 conjugated by F2":
--   F1 = the Word-level theorem (one generic proof).
--   F2 = the bijection to-c / from-c (`from-to` closes the trip).
--
-- Word-level helpers needed for the full surface:
--   * to-c-·                — bridge to-c (x · y) ≡ to-c x C.· to-c y
--   * ·-assoc-Word          — generic Coxeter normalize associativity
--   * ·-self-inverse-Word   — V₄-specific 4-case at Word level
--   * ·-comm-Word           — V₄-specific 16-case at Word level
--                              (still enumeration, but DONE ONCE at the
--                              Word side; V₄ lift is 1 line)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.Lifted where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; sym-trans; cong-trans)
open import Substrate.Foundation.Product using (_×_; _,_)

-- The polymorphic n-refls primitive lives in Coxeter.CanonicalCover —
-- shared across every Coxeter group instance, the same way
-- `same-canonical-via-Gen` lives in Coxeter.SameCanonical.
open import Substrate.Groups.Coxeter.CanonicalCover using (n-refls)

------------------------------------------------------------------------
-- Canonical-cover combinator with explicit predicate, so the broadcast
-- works.
------------------------------------------------------------------------

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
  using ([]; _∷_; _++_;
         ++-assoc; ++-identity-left; ++-identity-right)

open import Substrate.Groups.V4.Operations public
open import Substrate.Groups.V4.Bijection
  using (to-c; from-c; to-c-canonical; from-to; to-from-canonical)

------------------------------------------------------------------------
-- Helpers
------------------------------------------------------------------------

-- The canonical-fixed-point fact for any V₄ value.
to-c-fixed : (x : V₄) → C.normalize (to-c x) ≡ to-c x
to-c-fixed x = C.canonical-is-fixed-V4 (to-c-canonical x)

-- Bridge: to-c is a (semi)homomorphism of _·_.
-- Promoted from FourProduct.agda's private block.
to-c-· : (a b : V₄) → to-c (a · b) ≡ to-c a C.· to-c b
to-c-· a b =
  trans (to-from-canonical (C.normalize-canonical (to-c a C.· to-c b)))
        (C.normalize-idem (to-c a ++ to-c b))

------------------------------------------------------------------------
-- Word-level theorems (the F1's).
------------------------------------------------------------------------

-- Generic Coxeter associativity of `_·_ = normalize ∘ ++`.
·-assoc-Word :
  (w₁ w₂ w₃ : C.Word C.Gen) →
  (w₁ C.· w₂) C.· w₃ ≡ w₁ C.· (w₂ C.· w₃)
·-assoc-Word w₁ w₂ w₃ =
  sym-trans (C.normalize-append (w₁ ++ w₂) w₃)
  (cong-trans C.normalize (++-assoc w₁ w₂ w₃)
         (C.normalize-append-right w₁ (w₂ ++ w₃)))

canonical-cover :
  (P : ∀ {w} → C.Canonical w → Set) →
  P C.c-ε × P C.c-A × P C.c-B × P C.c-AB →
  ∀ {w} (c : C.Canonical w) → P c
canonical-cover P (pε , pA , pB , pAB) C.c-ε  = pε
canonical-cover P (pε , pA , pB , pAB) C.c-A  = pA
canonical-cover P (pε , pA , pB , pAB) C.c-B  = pB
canonical-cover P (pε , pA , pB , pAB) C.c-AB = pAB

-- V₄ self-inverse at the Word level — ALIASED FROM `4-refls`.
-- The four insert-involution reductions all converge to `[] ≡ []`, so
-- the named 4-refl table broadcasts.
·-self-inverse-Word :
  {w : C.Word C.Gen} → C.Canonical w → w C.· w ≡ []
·-self-inverse-Word = canonical-cover (λ {w} _ → w C.· w ≡ []) (n-refls 4)

-- V₄ commutativity, collapsed via insert-commute induction.
--
-- The 16-case Cayley butterfly was hiding TWO inductions:
--   * insert-shift: pushing `insert g` through a normalize-append.
--   * normalize-comm: arbitrary-Word commutativity by induction on the
--                      left argument, using IH + insert-shift.
--
-- Both reduce to V4-Coxeter's single generator-level relation
-- `insert-commute A B ≡ insert-commute B A`. The 16 refls at the
-- Cayley level are the orbit of THIS single fact.
--
-- Per [[feedback-expose-generator-not-orbit]]: catalogue the generator
-- (insert-commute), resist enumerating the orbit (16-case Cayley table).

-- insert-shift: insert g (normalize (a ++ b)) ≡ normalize (a ++ g ∷ b).
-- The "g floats from the outside to a specific position inside" lemma.
insert-shift :
  (g : C.Gen) (a b : C.Word C.Gen) →
  C.insert g (C.normalize (a ++ b)) ≡ C.normalize (a ++ (g ∷ b))
insert-shift g []        b = refl
insert-shift g (h ∷ a') b =
  trans (C.insert-commute g h (C.normalize-canonical (a' ++ b)))
        (cong (C.insert h) (insert-shift g a' b))

-- normalize-comm: ARBITRARY Words commute under normalize, no canonical
-- proofs needed — the abelianness is established by structural
-- induction on the left argument.
normalize-comm :
  (a b : C.Word C.Gen) →
  C.normalize (a ++ b) ≡ C.normalize (b ++ a)
normalize-comm []        b = cong C.normalize (sym (++-identity-right b))
normalize-comm (g ∷ a') b =
  trans (cong (C.insert g) (normalize-comm a' b))
        (insert-shift g b a')

-- ·-comm-Word: V₄ Word-level commutativity, no Canonical-proof
-- enumeration. Just normalize-comm.
·-comm-Word : (w₁ w₂ : C.Word C.Gen) → w₁ C.· w₂ ≡ w₂ C.· w₁
·-comm-Word w₁ w₂ = normalize-comm w₁ w₂

------------------------------------------------------------------------
-- V₄-level axioms (the lifted conjugations).
------------------------------------------------------------------------

-- ε · x ≡ x: F1 = canonical-is-fixed; F2 = bijection round-trip.
ε-left : (x : V₄) → (ε · x) ≡ x
ε-left x = trans (cong from-c (to-c-fixed x)) (from-to x)

-- x · ε ≡ x: same shape, with ++-identity-right.
ε-right : (x : V₄) → (x · ε) ≡ x
ε-right x =
  trans (cong from-c
              (trans (cong C.normalize (++-identity-right (to-c x)))
                     (to-c-fixed x)))
        (from-to x)

ε-identity : ((x : V₄) → (ε · x) ≡ x) × ((x : V₄) → (x · ε) ≡ x)
ε-identity = ε-left , ε-right

-- inv x · x ≡ ε: `inv x = x` in V₄; lift x C.· x ≡ [] from Word.
inv-left : (x : V₄) → (inv x · x) ≡ ε
inv-left x = cong from-c (·-self-inverse-Word (to-c-canonical x))

inv-right : (x : V₄) → (x · inv x) ≡ ε
inv-right x = cong from-c (·-self-inverse-Word (to-c-canonical x))

inv-inverse : ((x : V₄) → (inv x · x) ≡ ε) × ((x : V₄) → (x · inv x) ≡ ε)
inv-inverse = inv-left , inv-right

-- ·-cong: propositional equality is congruent over _·_.
·-cong : ∀ {x₁ x₂ y₁ y₂} → x₁ ≡ x₂ → y₁ ≡ y₂ → (x₁ · y₁) ≡ (x₂ · y₂)
·-cong refl refl = refl

-- ·-assoc: lift ·-assoc-Word through to-c-· (and its sym on the other side).
·-assoc : (x y z : V₄) → ((x · y) · z) ≡ (x · (y · z))
·-assoc x y z =
  trans (cong from-c (cong (C._· to-c z) (to-c-· x y)))
  (trans (cong from-c (·-assoc-Word (to-c x) (to-c y) (to-c z)))
         (cong from-c (cong (to-c x C.·_) (sym (to-c-· y z)))))

-- ·-comm: lift Word-level ·-comm-Word.
·-comm : (x y : V₄) → (x · y) ≡ (y · x)
·-comm x y = cong from-c (·-comm-Word (to-c x) (to-c y))

-- ·-right-cancel-ε: derived from group axioms (no V₄-enumeration).
-- a · b ≡ b ⟹ a ≡ a · (b · b) ⟹ a ≡ (a · b) · b ≡ b · b ≡ ε.
·-right-cancel-ε : (a b : V₄) → a · b ≡ b → a ≡ ε
·-right-cancel-ε a b a·b≡b =
  sym-trans (ε-right a)
  (cong-trans (a ·_) (sym (inv-right b))
  (sym-trans (·-assoc a b b)
  (cong-trans (_· b) a·b≡b
         (inv-right b))))
