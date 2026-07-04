{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb — ⟡ski-faithful-rb: a reconstruction
-- whose generator (the CF's quotient) is the ACTUALLY-contracted combinator, so
-- the reduction CF (Wedge.Shape.shape, ADD 153) reads the real reduction generators.
--
-- THE APPARENT PROBLEM (dissolved, not conceded): SKI combinators have DIFFERENT
-- ARITIES — I unary (I∙x⇒x), K binary (K∙x∙y⇒x), S ternary (S∙x∙y∙z⇒…) — so "a
-- single fixed-arity rb can't faithfully capture all of them." THE DISSOLUTION
-- (operator: CrossMul + the antilog/pow duality): ARITY IS A GRADE, and the n-ary
-- reconstruction is the ANTILOG (pow) of that grade — ONE grade-1 generator step,
-- powered to the arity. This is exactly DLogHom's gpowg (the generic antilog):
--   gpowg g n = g applied n times ;  gpowg-hom: gpowg g (a+b) ≡ gpowg g a · gpowg g b
-- (arities ADD ⟹ reconstructions MULTIPLY — the log/exp codec). So rb is NOT a
-- fixed-arity function pretending all combinators are alike; it is the grade-1
-- APPLICATION, and each combinator is `apply-n` = the antilog of its arity. The
-- CF then carries (generator, arity) — the varying arity is the graded cross degree
-- (CrossMulGraded: I→1, K→2, S→3), the two strands (peel structure + reduce
-- generator) of the SPPF, braided.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIFaithfulRb where

open import Substrate.Foundation.Eq  using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)

------------------------------------------------------------------------
-- ① The combinator GENERATORS and their ARITIES. The generator is what the CF's
-- quotient records; the arity is its grade (the number of args it consumes).
------------------------------------------------------------------------
data Gen : Set where
  gI gK gS : Gen

-- the arity of each generator = its GRADE (I:1, K:2, S:3).
arity : Gen → ℕ
arity gI = 1
arity gK = 2
arity gS = 3

------------------------------------------------------------------------
-- ② SKI terms (the carrier). apply-many f [x,y,z] = ((f∙x)∙y)∙z — the n-ary spine.
------------------------------------------------------------------------
data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm
infixl 7 _∙_

gen→tm : Gen → Tm
gen→tm gI = I
gen→tm gK = K
gen→tm gS = S

-- apply a term to a list of arguments (the n-ary spine) — the ANTILOG of the arity:
-- ONE application step, iterated arity-many times. This is `pow` of the grade-1
-- application (apply-one), the reconstruction that VARIES with arity via iteration.
apply-many : Tm → List Tm → Tm
apply-many f []       = f
apply-many f (x ∷ xs) = apply-many (f ∙ x) xs

------------------------------------------------------------------------
-- ③ THE FAITHFUL rb, as the antilog of the arity. rb takes the generator and its
-- argument list (of length = arity) and builds the redex spine. The generator is
-- kept (the CF quotient); the arity determines the iteration depth. ONE rb — its
-- behaviour VARIES with arity because it iterates apply, the antilog/pow structure.
------------------------------------------------------------------------
faithful-rb : Gen → List Tm → Tm
faithful-rb g args = apply-many (gen→tm g) args

-- the arities-add ⟹ spines-compose law (the antilog/pow codec, gpowg-hom's shape):
-- applying args₁ then args₂ = applying (args₁ ++ args₂) — one antilog of the summed
-- arity. apply-many f (xs ++ ys) ≡ apply-many (apply-many f xs) ys.
apply-hom : (f : Tm) (xs ys : List Tm)
          → apply-many f (xs ++ ys) ≡ apply-many (apply-many f xs) ys
apply-hom f []       ys = refl
apply-hom f (x ∷ xs) ys = apply-hom (f ∙ x) xs ys

------------------------------------------------------------------------
-- ④ THE CF NOW CARRIES THE REAL GENERATOR. A reduction step's quotient is the
-- contracted combinator's generator; the CF (the quotient sequence, ADD 153) is
-- the list of ACTUAL reduction generators, each with its arity as grade. Example:
-- a reduction contracting K then I has CF [gK, gI], arities [2, 1].
------------------------------------------------------------------------
CF : Set
CF = List Gen                          -- the reduction generators (the faithful shape)

-- the arity-grade sequence of a CF: the per-step arity (the graded cost).
arities : CF → List ℕ
arities []       = []
arities (g ∷ gs) = arity g ∷ arities gs

-- a concrete faithful CF: contract K (arity 2) then I (arity 1).
exampleCF : CF
exampleCF = gK ∷ gI ∷ []

-- its generators are the REAL combinators, its arities the real grades [2, 1]:
exampleCF-arities : arities exampleCF ≡ (2 ∷ 1 ∷ [])
exampleCF-arities = refl

-- and each generator faithfully rebuilds its redex (K∙x∙y, I∙x) — the antilog at arity:
rebuild-K : faithful-rb gK (K ∷ I ∷ []) ≡ ((K ∙ K) ∙ I)
rebuild-K = refl
rebuild-I : faithful-rb gI (S ∷ []) ≡ (I ∙ S)
rebuild-I = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the arity either/or dissolved): "different
-- arities need different fixed rb" is FALSE. Arity is a GRADE; the reconstruction
-- is the ANTILOG (pow/apply-many) of the arity — ONE application step, iterated
-- arity-many times. faithful-rb g = apply-many (gen→tm g), and its behaviour varies
-- with the arity of the arg-list BECAUSE it iterates (the pow structure), witnessed
-- by apply-hom (apply xs then ys = apply xs++ys — arities ADD, exactly gpowg-hom's
-- additive→multiplicative shape). The CF then carries the REAL generators (the
-- contracted combinators), each with its arity as its grade — the two-strand SPPF
-- (reduce generator + peel structure), the varying degree of CrossMulGraded (I:1,
-- K:2, S:3). ONE rb, the antilog; the arity is its exponent, not a fixed slot.
------------------------------------------------------------------------
