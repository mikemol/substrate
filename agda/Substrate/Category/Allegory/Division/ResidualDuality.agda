------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division.ResidualDuality
--
-- Defines: residual-duality
--
-- THE GEM — root and log without the either/or.  Left and right division
-- are ONE operation conjugated by the converse †:
--     (R ∖ T) †  ≈  (R † ／ T †)        (DEFINITIONALLY — both ⊆-refl).
-- "Divide on the left" and "divide on the right" are not two choices but
-- the same residual seen through †.  Root and log are the two residuals
-- of the exponentiation arrow `pow` (given power+exponent ⇒ base = root;
-- given power+base ⇒ exponent = log); this duality says they are
-- †-conjugate, a single structure, not an either/or.  `pow` itself is
-- greenfield — the concrete root/log instance lands once pow is presented
-- in `Rel`; the STRUCTURE that unifies them (the residual pair + the †
-- duality) is here.
--
-- ⟡alg6-restore: recovered from efe21483^ (ALG-6).  Four modules cite
-- this term in prose as though proved — StencilModular:13,64,
-- StencilDedekind:13,65, StencilDedekindDagger:55,
-- StencilDedekindCollapse:14,33,49 — and it had no definer between the
-- ALG-6 deletion and this restore.  One lemma, one elaboration unit; no
-- barrel re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division.ResidualDuality where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Division.Backslash
open import Substrate.Category.Allegory.Division.Slash


residual-duality : {A B C : Set} (R : A → B → Set) (T : A → C → Set)
                 → ((R ∖ T) †) ≈ ((R †) ／ (T †))
residual-duality R T = ⊆-refl , ⊆-refl
