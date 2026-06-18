------------------------------------------------------------------------
-- Substrate.WitnessTower.AlgebraLadder  (Ⓣ₃ — the algebraic ladder is a
-- witnessing tower IN THEORY-SPACE: extend by one LAW, carry the rung below)
--
-- The third tower-reduction, the theory-space-flavoured orbit-element. Ⓣ₁
-- (Sₙ) and Ⓣ₂ (ℚ) carry a DATA increment per rung (an insertion choice / a
-- Wedge). Here the increment is a LAW (a proof obligation), and the rungs are
-- ALGEBRAIC THEORIES:
--
--   Magma ⊏ Semigroup ⊏ Monoid ⊏ Group ⊏ AbelianGroup
--    (·)     +assoc      +ε,id    +inv      +comm
--
-- Each record literally CARRIES the one below as a field (`Semigroup.magma`,
-- `Monoid.semigroup`, `Group.monoid`, `AbelianGroup.group`) plus its new
-- law(s). So "presupposes everything below" is structural: an AbelianGroup
-- contains a Group contains a Monoid … contains a Magma — the whole tower.
--
-- This DISSOLVES the "axiom-accretion is NOT the witnessing step (no residual,
-- no fold)" reading. There IS a residual: the rung below, carried as a field —
-- and by record-η the rung IS exactly (below , increment) (`*-carries-*`
-- below, all refl). There IS a fold: the forgetful walk down to the base op
-- (`forget-to-magma`). Accretion IS the witnessing step, with a law-payload
-- instead of a data-payload.
--
-- (The increment is heterogeneous: Semigroup adds 1 law; Monoid adds an op + 2
-- laws; Group an op + 2 laws; AbelianGroup 1 law. And `Ring` carries TWO rungs
-- below — `semiring` AND `+-abelian` — with a coherence law: the fan-in / DAG
-- case of `WitnessTower.FamilyWitness` ("witnessing a FAMILY"), not a linear
-- rung. So the ladder is the linear tower here plus that one DAG node.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.AlgebraLadder where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Magma        using (Magma)
open import Substrate.Algebra.Semigroup    using (Semigroup; magma; ·-assoc)
open import Substrate.Algebra.Monoid       using (Monoid; semigroup; ε; ε-left; ε-right)
open import Substrate.Algebra.Group        using (Group; monoid; inv; inv-left; inv-right)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup; group; ·-comm)

open import Substrate.WitnessTower.Core using (Path; walk; steps; steps-walk)

private variable A : Set

------------------------------------------------------------------------
-- 1. The forgetful steps: each rung → the one below, = the carried-below
--    field projection (the witnessing step's forgetful direction).
------------------------------------------------------------------------

Sg→Mg : Semigroup A → Magma A
Sg→Mg = magma

Mn→Sg : Monoid A → Semigroup A
Mn→Sg = semigroup

Gp→Mn : Group A → Monoid A
Gp→Mn = monoid

Ab→Gp : AbelianGroup A → Group A
Ab→Gp = group

-- the full forgetful WALK down the tower to the base op (the fold the
-- "no fold" reading said was absent): AbelianGroup ⤳ … ⤳ Magma.
forget-to-magma : AbelianGroup A → Magma A
forget-to-magma ag = Sg→Mg (Mn→Sg (Gp→Mn (Ab→Gp ag)))

------------------------------------------------------------------------
-- 2. Each rung IS (rung-below , witnessing-increment) — the residual the
--    "no residual" reading said was absent. By record-η, refl. The
--    increment is shown heterogeneous: one law, or an op + laws.
------------------------------------------------------------------------

-- Semigroup = Magma + (assoc).
Sg-carries-Mg : (s : Semigroup A) → s ≡ record { magma = magma s ; ·-assoc = ·-assoc s }
Sg-carries-Mg s = refl

-- Group = Monoid + (inv , inv-left , inv-right) — an OP plus two laws.
Gp-carries-Mn : (g : Group A) →
  g ≡ record { monoid = monoid g ; inv = inv g
             ; inv-left = inv-left g ; inv-right = inv-right g }
Gp-carries-Mn g = refl

-- AbelianGroup = Group + (comm).
Ab-carries-Gp : (ag : AbelianGroup A) →
  ag ≡ record { group = group ag ; ·-comm = ·-comm ag }
Ab-carries-Gp ag = refl

------------------------------------------------------------------------
-- 3. The Core shape: the ladder is a Core witness path. Its depth is the
--    CONSTANT ladder height (4 steps, Magma=rung 0 … AbelianGroup=rung 4) —
--    unlike Sₙ/ℚ where depth is data — but the SHAPE is identical: a chain
--    where each rung witnesses (carries) the one below.
------------------------------------------------------------------------

ladder-path : Path 4
ladder-path = walk 4

ladder-steps : steps ladder-path ≡ 4
ladder-steps = steps-walk 4
