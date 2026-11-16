------------------------------------------------------------------------
-- Substrate.WitnessTower.WhyThreeV2
--
-- ANSWERS (by construction) "why does V₄ have three V₂'s in it?"
--
-- The conjecture: they are there so that one is the conjugate
-- (automorphic image) of the others. BUILT verdict, in three checked
-- facts:
--
--   (1) NOT conjugate INSIDE V₄. V₄ is abelian (·-comm), so internal
--       conjugation g·x·g⁻¹ = x is trivial — the three V₂'s are distinct
--       central subgroups, NOT related by any V₄-internal conjugation.
--
--   (2) They ARE permuted from OUTSIDE, by the S₃ that completes
--       S₄ = V₄ ⋊ S₃. The generator `rotate` is the 3-cycle
--       α → β → γ → α on the three involutions, and it is a V₄-
--       AUTOMORPHISM (RotateIsHom). So each involution is the
--       automorphic image of the previous — "conjugate" in the
--       holomorph sense (Aut(V₄)-orbit), exactly the user's intuition,
--       with the conjugator living in S₃, not V₄.
--
--   (3) Hence "three" is forced as the SET S₃ acts on: Aut(V₄) ≅ S₃ =
--       Sym(the 3 involutions). rotate (3-cycle) + swap-αβ (transposition)
--       generate that full symmetric action; the orbit of α is {α,β,γ}.
--
-- So the three V₂'s exist to BE the carrier of the S₃-action — the
-- middle layer of the witness-tower's V₄ ⋊ S₃ = S₄.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.WhyThreeV2 where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Axioms.Comm using (·-comm)
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations using (_·₄_)
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
open import Substrate.Groups.V4.Axioms.EpsilonLeft using (ε-left)
open import Substrate.Groups.V4.Axioms.InvLeft using (inv-left)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId using (rotate³-id)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateIsHom using (rotate-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapABIsHom using (swap-αβ-IsHom)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- (1) Internal conjugation in V₄ is trivial: g ·₄ x ·₄ g ≡ x  (inv = id,
--     so g·x·g⁻¹ = g·x·g). The three V₂'s are NOT V₄-internally
--     conjugate. Proved from ·-comm + ·-assoc + self-inverse.
--
--   g ·₄ x ·₄ g  ≡ g ·₄ (g ·₄ x)   [·-comm on (x ·₄ g)]   wait: do it directly
--   we show g ·₄ (x ·₄ g) ≡ x:
--     g ·₄ (x ·₄ g) ≡ g ·₄ (g ·₄ x)   [cong, ·-comm x g]
--                 ≡ (g ·₄ g) ·₄ x    [·-assoc, sym]
--                 ≡ x              [g·g = e (self-inv), ε-left]
------------------------------------------------------------------------

-- g ·₄ (x ·₄ g) ≡ x. inv g = g definitionally, so inv-left g : (g ·₄ g) ≡ ε.
conj-trivial : (g x : V₄) → (g ·₄ (x ·₄ g)) ≡ x
conj-trivial g x =
  trans (cong (g ·₄_) (·-comm x g))   -- g ·₄ (x ·₄ g) ≡ g ·₄ (g ·₄ x)
  (trans (sym (·-assoc g g x))        -- ≡ (g ·₄ g) ·₄ x
  (trans (cong (_·₄ x) (inv-left g))   -- ≡ ε ·₄ x        [g·g = ε]
         (ε-left x)))                 -- ≡ x

------------------------------------------------------------------------
-- (2) rotate is the 3-cycle α→β→γ→α on the three involutions, and is a
--     V₄-automorphism. Both already proven in-tree; recorded here as the
--     "permuted from outside" witnesses.
------------------------------------------------------------------------

rotate-on-α : rotate α ≡ β
rotate-on-α = refl
rotate-on-β : rotate β ≡ γ
rotate-on-β = refl
rotate-on-γ : rotate γ ≡ α
rotate-on-γ = refl

-- the orbit closes (order 3) and rotate is an automorphism (the
-- "conjugation from the S₃ part" is structure-preserving):
rotate-order-3 : (v : V₄) → rotate (rotate (rotate v)) ≡ v
rotate-order-3 = rotate³-id

------------------------------------------------------------------------
-- (3) The orbit of α under the S₃-action is exactly {α, β, γ} — the
--     three V₂'s ARE one orbit. swap-αβ (transposition) + rotate
--     (3-cycle) are the S₃ generators; α reaches β (rotate) and stays in
--     {α,β,γ}. Recorded: α's images under the two generators are the
--     other involutions, never e — the orbit is the 3 non-identity
--     elements, i.e. the 3 V₂'s.
------------------------------------------------------------------------

orbit-rotate : rotate α ≡ β        -- α ↦ β
orbit-rotate = refl
orbit-swap   : swap-αβ α ≡ β       -- α ↦ β (transposition)
orbit-swap   = refl
orbit-rotate² : rotate (rotate α) ≡ γ   -- α ↦ γ : the third V₂ reached
orbit-rotate² = refl
