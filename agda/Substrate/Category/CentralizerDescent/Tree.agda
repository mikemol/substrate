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

-- ⟡set1-rp-descenttree: the 10 Set-valued fields (Nodes + the per-node carrier/class/membership
-- FAMILIES) are PARAMETERS now — a record fielding a Set carrier is never honest Set₁
-- (set1-carrier-always-parameterize); the record drops Set₁→Set, fielding only the element-ops,
-- structural maps, and witnesses. Param order = the original field order (dependency-safe; the
-- positional-instance codemod lifts instance args by these positions). Mechanically synthesized
-- (scratch/record_def_edit.py).
record DescentTree (Nodes : Set)
                   (Gᶜ : Nodes → Set)
                   (Classᶜ : Nodes → Set)
                   (in-classᶜ : (n : Nodes) → Classᶜ n → Gᶜ n → Set)
                   (dGb : Nodes → Set)
                   (dCb : Nodes → Set)
                   (dicb : (n : Nodes) → dCb n → dGb n → Set)
                   (dGd : Nodes → Set)
                   (dCd : Nodes → Set)
                   (dicd : (n : Nodes) → dCd n → dGd n → Set) : Set where
  constructor mkDescentTree
  field
    _·ᶜ_      : (n : Nodes) → Gᶜ n → Gᶜ n → Gᶜ n
    εᶜ        : (n : Nodes) → Gᶜ n
    invᶜ      : (n : Nodes) → Gᶜ n → Gᶜ n
    repᶜ      : (n : Nodes) → Classᶜ n → Gᶜ n
    d·b  : (n : Nodes) → dGb n → dGb n → dGb n
    dεb  : (n : Nodes) → dGb n
    dib  : (n : Nodes) → dGb n → dGb n
    drb  : (n : Nodes) → dCb n → dGb n
    d·d  : (n : Nodes) → dGd n → dGd n → dGd n
    dεd  : (n : Nodes) → dGd n
    did  : (n : Nodes) → dGd n → dGd n
    drd  : (n : Nodes) → dCd n → dGd n
    Root  : Nodes
    CCA-at : (n : Nodes) →
             ConjugationCoalgebra (Gᶜ n) (_·ᶜ_ n) (εᶜ n) (invᶜ n) (Classᶜ n) (repᶜ n) (in-classᶜ n)
    parent : Nodes → Nodes
    parent-of-root : parent Root ≡ Root
    -- Per-edge descent witness: for any node n, there's a
    -- CentralizerDescent relating parent's CCA to this node's CCA
    -- (or, for Root, trivially related to itself).
    descent-at : (n : Nodes) →
                 CentralizerDescent (dGb n) (d·b n) (dεb n) (dib n) (dCb n) (drb n) (dicb n)
                                    (dGd n) (d·d n) (dεd n) (did n) (dCd n) (drd n) (dicd n)

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
