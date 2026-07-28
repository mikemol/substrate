------------------------------------------------------------------------
-- Substrate.WitnessTower.SignUniqueCharacter
--
-- ◆ip-abel-γ — the sign is the UNIQUE ◂-respecting mod-2 character. This
-- upgrades the "F₂-terminal" COMMENT to a TERM: any map g : LehmerPath n → F₂
-- that (a) is 𝟘 at the empty path and (b) respects the insertion step by
-- adding the digit-parity finParity p EQUALS signF ∘ decode. It is the
-- Mac Lane RIGIDITY of the free ordering tower (fold-unique): sign IS the
-- fold of the parity-step algebra, so nothing among ◂-respecting maps is
-- finer than the sign.
--
--   · sign-alg              — the parity-step LehmerAlgebra (base 𝟘, step +finParity)
--   · sign-is-fold          — signF ∘ decode IS the fold (fold-unique + insertion-parity-B)
--   · sign-unique-◂-character — any ◂-respecting mod-2 character = signF ∘ decode
--
-- Pure assembly of already-green pieces: fold-unique (OrientationUniversal),
-- finParity (LehmerTowerMorphism), insertion-parity-B (InsertionParity —
-- which IS the g-step obligation, proven unconditionally), signF/decode.
-- Nothing new is proven; the uniqueness is fold-unique instantiated.
--
-- HONEST BOUNDARY: uniqueness among ◂-RESPECTING maps only, NOT "no abelian
-- character finer than Z/2" (that abelianisation ceiling = ◆ip-abel-cap; it
-- needs Aₙ = [Sₙ,Sₙ], not this fold uniqueness).
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SignUniqueCharacter where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Substrate.Algebra.F2 using (F₂; 𝟘; _+_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.WitnessTower.LehmerTowerMorphism using (finParity)
open import Substrate.WitnessTower.InsertionParity using (insertion-parity-B)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold; fold-unique)

------------------------------------------------------------------------
-- 1. THE PARITY-STEP ALGEBRA. Grade-constant carrier F₂; the step adds the
--    factoradic-digit parity finParity p — the sign cocycle read as a fold.
------------------------------------------------------------------------

sign-alg : LehmerAlgebra (λ _ → F₂)
sign-alg = record { base = 𝟘 ; step = λ {_} b p → finParity p + b }

------------------------------------------------------------------------
-- 2. sign IS THE FOLD. signF ∘ decode agrees with sign-alg on (start, ◂), so
--    by fold-unique it EQUALS fold sign-alg. insertion-parity-B is precisely
--    the g-step obligation (signF (decode (l ◂ p)) ≡ finParity p + signF (decode l)).
------------------------------------------------------------------------

sign-base : signF (decode start) ≡ 𝟘
sign-base = refl

sign-is-fold : ∀ {n} (l : LehmerPath n) → signF (decode l) ≡ fold sign-alg l
sign-is-fold = fold-unique sign-alg (λ l → signF (decode l)) sign-base insertion-parity-B

------------------------------------------------------------------------
-- 3. THE UNIQUENESS CHARACTER. Any g that is 𝟘 at start and respects ◂ by
--    +finParity is signF ∘ decode. (fold-unique on g, then sign-is-fold back.)
------------------------------------------------------------------------

sign-unique-◂-character :
  (g : ∀ {n} → LehmerPath n → F₂) → (g start ≡ 𝟘) →
  (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≡ (finParity p + g l)) →
  ∀ {n} (l : LehmerPath n) → g l ≡ signF (decode l)
sign-unique-◂-character g gb gs l =
  trans (fold-unique sign-alg g gb gs l) (sym (sign-is-fold l))
