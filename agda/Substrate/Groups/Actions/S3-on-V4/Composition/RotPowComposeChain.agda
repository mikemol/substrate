------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.RotPowComposeChain
--
-- The 4-step rot-pow tail-chain common to every Block in the
-- act-∙-canonical-{00,01,10,11} grid. After `act-equals-pow` bridges
-- `act → act-on-canonical → rot-pow ∘ swap-pow`, all four Blocks
-- traverse the same four rewrites to land at
-- `rot-pow n₁ (rot-pow n₂' v')`:
--
--   1. cong (rot-pow _) over Z₃.normalize-idem        — undo the
--      outer normalize-canonical
--   2. sym rot-pow-normalize-eq                       — lift rot-pow
--      out of the normalize
--   3. rot-pow-append                                 — split the
--      ++ into a composition
--   4. sym (cong (rot-pow n₁) (rot-pow-normalize-eq)) — strip the
--      inner normalize off n₂'
--
-- Parametrised over both the inner n₂' (which varies as `Z₃.normalize
-- n₂` for h₁=[] cases vs `Z₃.inv (Z₃.normalize n₂)` for h₁=Z₂.a∷[]
-- cases — the swap-twist delta) and the carried value v' (= v in
-- Block00/Block10, swap-αβ v in Block01/Block11).
--
-- The chain operates on the N₁ side only — no normalize-idem
-- obstacle on the H side. The H-side normalization is handled by
-- act-equals-pow itself, which each Block calls separately with its
-- own (h₂, c-h₂) pair, then chains the rot-pow side via this helper.
--
-- This file names a substrate-level *micropattern*: the structural
-- shadow underneath the 4-way Block grid. The deltas (swap-pow-h₂
-- on the right, rot-pow-swap-twist on the left, swap-αβ²-id on both)
-- are already named primitives; until now this common chain was the
-- ONLY load-bearing pattern in the S₃-action composition proofs
-- without a substrate-level name.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.RotPowComposeChain where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; _++_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Groups.Actions.S3-on-V4.Generators
  using (rot-pow; rot-pow-append; rot-pow-normalize-eq)

-- Signature starts at the DOUBLY-normalized form produced by
-- `act-equals-pow` applied to `Z₃.normalize-canonical (Z₃.normalize
-- (n₁ ++ n₂'))`. The chain undoes that double normalize and unpacks
-- the ++ into the rot-pow composition. Three steps:
--   1. cong (rot-pow _) over normalize-idem (n₁ ++ n₂')
--   2. sym rot-pow-normalize-eq (n₁ ++ n₂')
--   3. rot-pow-append n₁ n₂'
--
-- The final per-callsite normalize-strip on the *inner* rot-pow (the
-- one carrying the rotational-argument w₂, where Block instances
-- convert between `Z₃.normalize n₂` and raw `n₂`, or between
-- `Z₃.inv (Z₃.normalize n₂)` and `Z₃.inv n₂`) is left to the
-- callsite — that's where the symmetry-breaking deltas (raw vs inv)
-- actually live.
rot-pow-compose-chain :
  ∀ (n₁ n₂' : Word Z₃.Gen) (v' : V₄) →
  rot-pow (Z₃.normalize (Z₃.normalize (n₁ ++ n₂'))) v' ≡
    rot-pow n₁ (rot-pow n₂' v')
rot-pow-compose-chain n₁ n₂' v' =
  trans (cong (λ w → rot-pow w v') (Z₃.normalize-idem (n₁ ++ n₂')))
  (trans (sym (rot-pow-normalize-eq (n₁ ++ n₂') v'))
         (rot-pow-append n₁ n₂' v'))
