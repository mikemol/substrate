------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Chain
--
-- The GENERIC arity lemma: normalize distributes over a right-nested
-- ++-chain of ANY length, in one induction. Subsumes the former
-- file-per-arity ladder (Triple/Quad/Quint/Sext/Sept), each of which was
-- `normalize-cons a (previous-arity ...)` unrolled by hand — an
-- open-ended ladder (every new arity = a new file). This replaces it
-- with a single inductive proof over Vec Word (suc n); any arity is free.
--
-- chain (a₀ ∷ a₁ ∷ … ∷ aₙ ∷ []) = a₀ ++ (a₁ ++ (… ++ aₙ))   (right-nested)
-- normalize-chain : normalize (chain ws) ≡ normalize (chain (map normalize ws))
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}


-- ⚑ A NAME USED IN THE TELESCOPE MUST BE IMPORTED BEFORE THE MODULE HEADER.
-- A parameter list is scope-checked before anything inside `where`, so an
-- import placed after the header is too late.  The splitter emits the
-- prelude after the header (right for a body, wrong for a telescope), so
-- every leaf whose PARAMETERS mention the name inherited this.
-- MEASURED: 11 sites tree-wide.
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Quotient.Canonical

module Substrate.Groups.Coxeter.Core.HigherArity.Chain
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map)

open import Substrate.Groups.Coxeter.Core.HigherArity.Step
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym

-- Right-nested ++-fold of a non-empty Vec of Words.
chain : {n : ℕ} → Vec Word (suc n) → Word
chain (a ∷ [])           = a
chain (a ∷ (b ∷ rest))   = a ++ chain (b ∷ rest)

-- The generic arity lemma, by induction on the Vec.
--   * singleton: normalize a ≡ normalize (normalize a) — canonical-is-fixed
--     on normalize-canonical (the normalize-idempotence the ladder's base
--     implicitly used).
--   * cons: normalize-cons a (IH on the tail).
normalize-chain : {n : ℕ} (ws : Vec Word (suc n)) →
                  normalize (chain ws) ≡ normalize (chain (map normalize ws))
normalize-chain (a ∷ []) =
  -- goal: normalize a ≡ normalize (normalize a) (idempotence, this
  -- direction); canonical-is-fixed gives the reverse, so sym.
  sym (canonical-is-fixed (normalize-canonical a))
normalize-chain (a ∷ (b ∷ rest)) =
  normalize-cons a (normalize-chain (b ∷ rest))
