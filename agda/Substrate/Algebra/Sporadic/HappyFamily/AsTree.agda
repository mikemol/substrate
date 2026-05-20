------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.HappyFamily.AsTree
--
-- The Happy Family as a single CentralizerDescent.Tree instance —
-- 20 sporadic groups + 19 descent edges with M as root, replacing
-- the previous representation as 20 disconnected parametric modules.
--
-- Z8 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on.
--
-- KEY STRUCTURAL CONTENT:
--
--   Nodes = Fin 20 (one per Happy Family member)
--   Root  = the Monster (index 0)
--   parent = each node's direct descent-parent in the HF hierarchy
--   CCA-at = each node's ConjugationCoalgebra (supplied per-node
--            via module parameters)
--   descent-at = each node's CentralizerDescent witness (similar)
--
--   The descent topology (= parent function) is fixed by mathematical
--   structure; the per-node group data is parametric.
--
-- After Z8, the substrate has the Happy Family as a SINGLE OBJECT
-- (DescentTree value), not 20 disconnected modules. Closes Gap #3
-- from the Grothendieck-closure audit constructively.
--
-- Substrate-pragmatic scope: descent topology is documented; per-node
-- groups + descent witnesses come from the user. Concrete consumer
-- supplies the 20 CCAs (from T8/V2/V3/V4/V5) + descent witnesses
-- (from V1 CentralizerDescent instances).
--
-- Per [[expose-generator-not-orbit]] at the descent-hierarchy level:
-- 1 tree with 20 nodes + 19 edges + Monster root replaces 20
-- disconnected parametric modules.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Data.Fin using (Fin; zero; suc)
open import Data.Nat using (ℕ)
open import Level using (Level)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra)
open import Substrate.Category.CentralizerDescent
  using (CentralizerDescent)
open import Substrate.Category.CentralizerDescent.Tree
  using (DescentTree; mkDescentTree)

module Substrate.Algebra.Sporadic.HappyFamily.AsTree
  -- The 20 Happy Family CCAs, supplied per-node.
  -- Indexing convention (ATLAS-style ordering):
  --   0  = Monster (M)
  --   1  = Baby Monster (B)
  --   2  = Conway Co₁
  --   3  = Conway Co₂
  --   4  = Conway Co₃
  --   5  = Fischer Fi₂₄'
  --   6  = Fischer Fi₂₃
  --   7  = Fischer Fi₂₂
  --   8  = Thompson Th
  --   9  = Harada-Norton HN
  --   10 = Held He
  --   11 = Suzuki Suz
  --   12 = McLaughlin McL
  --   13 = Higman-Sims HS
  --   14 = Janko J₂
  --   15 = Mathieu M₂₄
  --   16 = Mathieu M₂₃
  --   17 = Mathieu M₂₂
  --   18 = Mathieu M₁₂
  --   19 = Mathieu M₁₁
  (HF-CCA : Fin 20 → ConjugationCoalgebra {Level.zero})
  -- Per-node centralizer-descent witness (from V1).
  (HF-descent : Fin 20 → CentralizerDescent {Level.zero})
  where

------------------------------------------------------------------------
-- 1. The Happy Family descent topology (parent function).
--
-- Each non-Monster HF member is descended from somewhere in the
-- tree. The topology below reflects the standard ATLAS descent
-- structure (commonly used conventions; some HF members have
-- multiple valid descent paths).
------------------------------------------------------------------------

-- Helper Fin 20 pattern synonyms (named for readability + paren safety).
pattern i0  = zero
pattern i1  = suc i0
pattern i2  = suc i1
pattern i3  = suc i2
pattern i4  = suc i3
pattern i5  = suc i4
pattern i6  = suc i5
pattern i7  = suc i6
pattern i8  = suc i7
pattern i9  = suc i8
pattern i10 = suc i9
pattern i11 = suc i10
pattern i12 = suc i11
pattern i13 = suc i12
pattern i14 = suc i13
pattern i15 = suc i14
pattern i16 = suc i15
pattern i17 = suc i16
pattern i18 = suc i17
pattern i19 = suc i18

HF-parent : Fin 20 → Fin 20
HF-parent i0  = i0    -- Monster (root)
HF-parent i1  = i0    -- BabyMonster ← Monster (via 2A)
HF-parent i2  = i0    -- Co₁ ← Monster (via 2B)
HF-parent i3  = i2    -- Co₂ ← Co₁
HF-parent i4  = i2    -- Co₃ ← Co₁
HF-parent i5  = i0    -- Fi₂₄' ← Monster (via 3A)
HF-parent i6  = i5    -- Fi₂₃ ← Fi₂₄'
HF-parent i7  = i6    -- Fi₂₂ ← Fi₂₃
HF-parent i8  = i0    -- Th ← Monster (via 3C)
HF-parent i9  = i0    -- HN ← Monster (via 5A)
HF-parent i10 = i0    -- He ← Monster (via 7A)
HF-parent i11 = i2    -- Suz ← Co₁
HF-parent i12 = i2    -- McL ← Co₁
HF-parent i13 = i2    -- HS ← Co₁
HF-parent i14 = i11   -- J₂ ← Suz
HF-parent i15 = i2    -- M₂₄ ← Co₁
HF-parent i16 = i15   -- M₂₃ ← M₂₄
HF-parent i17 = i16   -- M₂₂ ← M₂₃
HF-parent i18 = i15   -- M₁₂ ← M₂₄
HF-parent i19 = i18   -- M₁₁ ← M₁₂

HF-parent-of-root : HF-parent i0 ≡ i0
HF-parent-of-root = refl

------------------------------------------------------------------------
-- 2. The Happy Family as a DescentTree.
------------------------------------------------------------------------

HappyFamily-DescentTree : DescentTree
HappyFamily-DescentTree = mkDescentTree
  (Fin 20)
  i0                    -- Root = Monster
  HF-CCA
  HF-parent
  HF-parent-of-root
  HF-descent

------------------------------------------------------------------------
-- 3. Capstone — Happy Family as a single substrate object.
--
-- Z8 of the 10-slice Z-arc. Closes Gap #3 from the Grothendieck-
-- closure audit constructively: the 20-member Happy Family is now
-- a SINGLE substrate object (HappyFamily-DescentTree) rather than
-- 20 disconnected parametric modules.
--
-- The descent topology (= HF-parent function) is hardcoded per
-- ATLAS-standard conventions. The per-node CCAs and descent
-- witnesses are module parameters supplied by downstream consumers
-- citing CFSG + ATLAS.
--
-- Per [[expose-generator-not-orbit]]: 1 tree + 20 nodes + 19 edges
-- replaces 20 disconnected modules.
--
-- Per [[homology-cohomology-recursion]]: HappyFamily-DescentTree IS
-- the substrate's recursive cataloging at the sporadic-group level
-- — Monster's structure cohomology cascades through the tree.
--
-- Next: Z9 (GriessAlgebra.Aut — Monster as Aut(GriessAlgebra) via Z2).
------------------------------------------------------------------------
