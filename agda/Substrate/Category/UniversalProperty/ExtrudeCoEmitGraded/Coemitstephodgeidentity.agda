------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstephodgeidentity
--
-- Defines: coemit-step-hodge-identity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstephodgeidentity where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flipinvolutive
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- ≡ IS CONSTRUCTED OF THE TOTALITY OF THE ORBIT'S GROUP ACTIONS — least-fixed-point-as-Hodge-identity.
-- (operator, correcting my "conj-conj will likely hold only up to ~, not ≡" — that framing is BACKWARDS.)
--
-- CANONICAL (Substrate.WitnessTower.FaceSet, verbatim):
--   universe n = replicate (suc n) 𝟙                        -- THE TOTALITY
--   ★ S = universe +ⱽ S                                     -- the dual is the totality WEDGED with S
--   "wedge-recon proves S +ⱽ ★ S ≡ universe — S and its residue reconstruct the universe — so ★ S is literally
--    'what S is missing to be everything', COMPUTED, NOT NEGATED. The involution ★★ = id ... follow from the
--    F₂-vector ADDITIVE GROUP LAWS already proved in Algebra.F2.Vector — reused, not re-proved."
--   ★-involution : (S : Face n) → ★ (★ S) ≡ S              -- a GENUINE ≡, engine: +ⱽ-self-inverse (v +ⱽ v ≡ 𝟎ⱽ)
--   ★-universe   : ★ (universe n) ≡ nothing-face n          -- the totality's dual is nothing
--
-- >>> THE CORRECTION. I treated ≡ as primitive-and-strong and ~ as a weaker settling-for ("holds only up to ~").
-- >>> Backwards. ≡ is BUILT: ★★ = id is proven from the ADDITIVE GROUP LAWS over the TOTALITY (universe). The
-- >>> identity is the closure of the group action, not a prior notion the action approximates.
-- >>> On a COINDUCTIVE carrier the totality is not a finite `universe` vector but the ORBIT of all finite
-- >>> perspectives — and `~` is exactly their conjunction: t ~ r ⟺ (∀ n) take n t ≡ take n r
-- >>> (coemit-final-eq-composed, 335; prefix-separates/bisim→prefix, 331). So **~ IS the totality-construction
-- >>> of ≡ on the trace carrier** — the least fixed point μ (the finite perspectives) closing into the Hodge
-- >>> identity. `conj-conj up to ~` is not a weakening: it IS conj-conj, constructed.
------------------------------------------------------------------------
-- the STEP-LEVEL Hodge identity: the chirality flip is its own dual — ≡ at each step, by the additive group law.
-- (F₂: 𝟙 +F (𝟙 +F b) ≡ b, i.e. x ⊕ x = 𝟘 — the SAME engine as FaceSet's +ⱽ-self-inverse.)
coemit-step-hodge-identity : (b : F₂) → f2-flip (f2-flip b) ≡ b
coemit-step-hodge-identity = f2-flip-involutive
