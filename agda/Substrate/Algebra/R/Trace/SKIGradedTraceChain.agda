{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain — ⟡ski-graded-trace-chain: the
-- SKI shedding chained into a GRADE-ACCUMULATING trace that KEEPS EVERY COST
-- (never collapses), by reskinning Wedge.Product's GradedProduct + WedgeTerm.
--
-- ADD 147 fixed the single shed (cost in the grade, structure in the remainder).
-- This chains sheds so the grade ACCUMULATES — and the substrate already holds the
-- accumulating-grade chain parametrically as WedgeTerm (P : GradedProduct) : ℕ →
-- Set, whose header states the exact anti-collapse property: "the term KEEPS EVERY
-- FACTOR — NEVER discards", and whose grade is "the sum of its leaves' grades".
-- Product.agda names my flat-trace bug precisely: "plain DivStr collapses all
-- grades to a point and the lost grade reappears as the count q in the residue."
--
-- So the SKI cost-carrying reduction sequence = a WedgeTerm over a SKI
-- GradedProduct: each leaf is a shed of a given cost-grade; _⊗_ chains two,
-- ADDING their grades (total cost = Σ leaf costs); eval evaluates the chain. A
-- reskin, not a hand-roll — "almost everything is a parameterization of something."
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIGradedTraceChain where

open import Substrate.Foundation.Eq  using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Algebra.Wedge.Product using (GradedProduct; gpower)
open import Substrate.Algebra.Wedge.Product.Term
  using (WedgeTerm; leaf; nil; _⊗_; eval; pow-term; eval-pow)

------------------------------------------------------------------------
-- 1. A SKI shed record at a fixed cost-grade: the shed subterm (structure) tagged
-- with its grade = the cost. C n = the sheds that cost n. (We carry the peeled
-- subterm and the grade; the grade is the reduce-cost, never dropped.)
------------------------------------------------------------------------
data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm
infixl 7 _∙_

-- a shed carrying cost n: its peeled subterm. Grade n = the cost this shed adds.
record Shed (n : ℕ) : Set where
  constructor shed⟨_⟩
  field peeled : Tm
open Shed public

------------------------------------------------------------------------
-- 2. THE SKI GradedProduct: C n = Shed n; u = the grade-0 shed (a normal form,
-- cost 0, peeled = a fixed nf marker); _∧_ = chain two sheds, grades ADDING (the
-- total cost accumulates). This IS the two-index braiding chained: grade = Σ cost.
------------------------------------------------------------------------
ski-product : GradedProduct
ski-product = record
  { C   = Shed
  ; u   = shed⟨ I ⟩                                   -- grade-0 unit: the trivial nf shed
  ; _∧_ = λ {i}{j} s t → shed⟨ peeled s ∙ peeled t ⟩  -- chain: grade i+j, rebuild structure
  }

------------------------------------------------------------------------
-- 3. THE COST-CARRYING REDUCTION SEQUENCE = a WedgeTerm over ski-product. Its
-- grade is the ACCUMULATED total cost (the sum of the leaf cost-grades) — KEPT by
-- construction (WedgeTerm keeps every factor). A concrete chain of three sheds of
-- costs 1, 1, 1 has total grade 1+(1+(1+0)) = 3 — the real total redex-cost.
------------------------------------------------------------------------
Chain : ℕ → Set                                       -- a SKI shedding chain of total cost n
Chain n = WedgeTerm ski-product n

-- a single shed of cost 1 (an I/K/S head-redex contraction), as a grade-1 leaf.
shed1 : Tm → Chain 1
shed1 t = leaf (shed⟨ t ⟩)

-- the empty chain (a normal form reached): total cost 0.
nf-chain : Chain 0
nf-chain = nil

-- chaining accumulates the grade: three cost-1 sheds ⟹ total cost 3 (NOT collapsed).
three-sheds : Chain (1 + (1 + (1 + 0)))
three-sheds = shed1 (I ∙ K) ⊗ (shed1 (I ∙ S) ⊗ (shed1 (K ∙ I) ⊗ nf-chain))

-- the total grade of three-sheds IS 3 — the accumulated cost, carried by the type.
total-cost-is-3 : Chain 3
total-cost-is-3 = three-sheds

------------------------------------------------------------------------
-- 4. THE ACCUMULATION IS REAL (not zero-collapsed): a q-fold chain of a fixed
-- cost-1 shed has total grade q — pow-term gives it, and eval factors through
-- (eval-pow), so the chained value is the q-fold ∧ of the shed. The grade q is
-- the accumulated cost, tracked in the type, recoverable by construction.
------------------------------------------------------------------------
q-fold-chain : (b : Shed 1) (q : ℕ) → Chain (q * 1)
q-fold-chain b q = pow-term {ski-product} b q

-- eval of a q-fold chain is the q-fold ∧ (the accumulated structure) — the reskin
-- of Product.gpower: the total cost q is carried, the structure rebuilt.
q-fold-eval : (b : Shed 1) (q : ℕ)
            → eval (q-fold-chain b q) ≡ gpower ski-product b q
q-fold-eval b q = eval-pow {ski-product} b q

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the accumulating-grade chain, reskinned): the
-- SKI cost-carrying reduction SEQUENCE is a WedgeTerm over a SKI GradedProduct.
-- The grade of the whole chain is the SUM of the leaf cost-grades — the total
-- redex-cost, KEPT by construction (WedgeTerm never discards a factor). This is
-- the chained form of ADD 147's single graded shed: one shed = one leaf (grade =
-- its cost); the chain = the ⊗ of leaves (grade = Σ costs). The flat Trace ℕ-shed
-- (ADD 146) was the grade-collapsed-to-a-point shadow — Product.agda's verbatim
-- "plain DivStr collapses all grades to a point"; the WedgeTerm is the faithful
-- form where the grade IS the accumulated cost. A reskin of the graded monoid,
-- the same shape as gpower / EEATrace's chained quotients. The either/or "chain
-- with accumulating cost vs the flat sequence" dissolves: the flat sequence is
-- the grade-collapsed projection; the WedgeTerm is the original that keeps it.
------------------------------------------------------------------------
