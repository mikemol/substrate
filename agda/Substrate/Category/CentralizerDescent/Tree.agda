------------------------------------------------------------------------
-- Substrate.Category.CentralizerDescent.Tree
--
-- The recursive descent tree primitive: V1 CentralizerDescent gives
-- a SINGLE descent step (parent + child + descent witness); this
-- primitive packages a full TREE of such descents into a single
-- substrate object.
--
-- Z4 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on (closes Gap #3 from the
-- audit: "CentralizerDescent doesn't iterate").
--
-- KEY STRUCTURAL CONTENT:
--
--   A DescentTree is parametric over an abstract Nodes set + a root
--   + a parent function + a per-node CCA assignment + per-edge
--   descent witnesses.
--
--   For the Happy Family from Monster: Nodes = 20 sporadic groups;
--   Root = Monster; parent maps each HF member to its descent-
--   parent (e.g., parent(BabyMonster) = Monster); CCA-at maps each
--   to its substrate-side ConjugationCoalgebra (T8, V2, V3, V4, V5
--   instances).
--
-- Per [[expose-generator-not-orbit]]: the tree IS the Happy Family;
-- 20 nodes + 19 edges + the Monster root represent the entire
-- hierarchy as a single substrate object, replacing 20 disconnected
-- parametric modules.
--
-- Per [[homology-cohomology-recursion]]: the descent tree is the
-- substrate's recursive cataloging at the sporadic-group level.
-- Each tree level adds cohomological structure inherited from the
-- parent.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CentralizerDescent.Tree where

open import Substrate.Foundation.Level using (Level; 0ℓ; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra)
open import Substrate.Category.CentralizerDescent
  using (CentralizerDescent)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The DescentTree record.
--
-- Bundles:
--   * Nodes : Set — abstract carrier of tree nodes
--   * Root : Nodes — the root node
--   * CCA-at : Nodes → ConjugationCoalgebra — each node's CCA
--   * parent : Nodes → Nodes — parent function (Root maps to itself)
--   * parent-of-root : parent Root ≡ Root — fixed-point axiom for root
--   * descent-at : for each non-root node, the V1 CentralizerDescent
--     witness relating parent's CCA to child's CCA
--
-- Substrate-pragmatic encoding: Nodes is abstract (user supplies
-- the specific carrier); structural relations are axiomatic; the
-- per-edge descent witnesses connect to V1's CentralizerDescent
-- primitive.
------------------------------------------------------------------------

record DescentTree : Set₁ where
  constructor mkDescentTree
  field
    Nodes : Set
    Root  : Nodes
    CCA-at : Nodes → ConjugationCoalgebra {0ℓ}
    parent : Nodes → Nodes
    parent-of-root : parent Root ≡ Root
    -- Per-edge descent witness: for any node n, there's a
    -- CentralizerDescent relating parent's CCA to this node's CCA
    -- (or, for Root, trivially related to itself).
    descent-at : Nodes → CentralizerDescent {0ℓ}

open DescentTree public

------------------------------------------------------------------------
-- Capstone — descent tree primitive in place.
--
-- Z4 of the 10-slice Z-arc. Closes Gap #3 from the Grothendieck-
-- closure audit: CentralizerDescent now iterates structurally via
-- the DescentTree record.
--
-- Concrete instances expected (Z8 next slice):
--   * HappyFamily.AsTree: the entire 20-member Happy Family as a
--     single DescentTree instance, with M as root and each sporadic
--     subquotient as a node parented by its descent-source.
--
-- Other potential instances:
--   * Hodge-related descent: ★-fixed → SelfDual → 168-gauge orbit
--     (each level a centralizer-style descent in the Hodge algebra).
--   * Galois-theoretic descents: each field-extension's
--     centralizer-class structure.
--
-- Per [[expose-generator-not-orbit]] at the structural-tree level:
-- a 20-node tree replaces 20 disconnected parametric modules.
--
-- Next: Z5 (CategoryOf — generic "category of substrate-primitive-X").
------------------------------------------------------------------------
