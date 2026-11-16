------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuanalambek
--
-- Defines: coemit-mu-ana-lambek
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuanalambek where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Final.Into
open import Substrate.Algebra.R.Trace.Final.LambekIntoOut
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Final.Into
open import Substrate.Algebra.R.Trace.Final.Out
  renaming (out to trace-out)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- THE S₃-BRAIDING (operator KEY, added to the already-built mu-ana/mu-initial/colim-bridge-bisim): coinductive
-- RIGIDITY (cons 0 zero-trace ~ zero-trace but NOT ≡, D-guarded-not-mutual) is AT THE GROUP ORBIT — NOT in the
-- groupoid (up-to-iso → always another move, no rigidity). It pins at the FINITE S₃-orbit. Braid the S₃ group
-- structure THROUGH the coinductive process: the orbit move is available at EVERY coinductive depth (the finite
-- orbit closes), and THAT is where ~ becomes rigid (a bounded set of moves, not the groupoid's unbounded ones).
------------------------------------------------------------------------

-- the coinductive rigidity witness (Lambek): into (out x) ~ x — the ~ (not ≡) direction, the rigidity itself.
coemit-mu-ana-lambek : (x : RealTrace) → into (trace-out x) ~ x
coemit-mu-ana-lambek = lambek-into-out
