------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.IdemCanonical
--
-- Defines: idem-Canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.IdemCanonical where

open import Agda.Primitive
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Realizability.Charter



-- An IDEMPOTENT e (e∘e ≡ e) is, even more directly, a Canonical form for its OWN
-- kernel — the most elementary section-based quotient (split-Canonical is the special
-- case e = s∘F). `canonical-respects-≈` is the identity, since ker e IS "e x ≡ e y".
-- The apex of the idempotent law-motif f(f x)≡f x (normalize-idem, q-idempotent, …).
idem-Canonical :
  {a : Level} {A : Set a}
  (e : A → A) (idem : (x : A) → e (e x) ≡ e x) →
  Canonical (ker-Quotient e)
idem-Canonical e idem = record
  { canonical            = e
  ; canonical-idempotent = idem
  ; canonical-respects-≈ = λ p → p
  ; ≈-canonical          = λ a → sym (idem a)
  }

------------------------------------------------------------------------
-- 4. Capstone for QU1.
--
-- Quotient + Canonical landed. QU2 lifts the base Quotient into a
-- UPArrow; surreals attach (Canonical-free) at QU7, and the other
-- four substrate instances attach with a Canonical witness at QU5,
-- QU6, QU8, QU9.
------------------------------------------------------------------------
