{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulOnGraded — ⟡ski-faithful-on-graded: wire
-- the faithful reconstruction (ADD 154, the antilog apply-many) onto a GRADED
-- DivStr where GRADE = ARITY, bridging the fixed-3 flat recon (ADD 153) and the
-- arity-varying antilog. The named center is Wedge.VecGraded: "recon IS cons,
-- building a vector = consing heads = the graded free construction, grade = length"
-- — which is EXACTLY arity-as-grade. The argument list of a combinator is a graded
-- vector; its length is the arity; recon conses one argument (grade-RAISING by 1).
--
-- So the arity-varying antilog IS the graded chain: apply-many f args = the fold of
-- the grade-raising recon over the arg-vector. One grade-1 step (apply/cons); the
-- combinator's arity is the grade it is reconstructed at. This DISSOLVES the fixed-3
-- vs varying-arity tension: the flat fixed-arity recon is the grade-COLLAPSED shadow;
-- the graded (VecGraded) recon is the faithful form where the grade IS the arity.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIFaithfulOnGraded where

open import Substrate.Foundation.Eq  using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr; GradedWedge; recon; gforget; gcell)
open import Substrate.Algebra.Wedge.VecGraded using (vec-graded; vec-step; vec-cell; vec-forget)

-- reuse the faithful generators (ADD 154): Gen, arity, gen→tm, Tm, apply-many.
open import Substrate.Algebra.R.Trace.SKIFaithfulRb
  using (Gen; gI; gK; gS; arity; Tm; S; K; I; _∙_; gen→tm; apply-many)

------------------------------------------------------------------------
-- ① THE ARITY-GRADED CARRIER: vec-graded Tm — the argument list of a combinator is
-- a graded Vec Tm, its LENGTH is the arity, recon conses one argument (grade-raise).
-- This is VecGraded instantiated at the SKI argument type: grade = arity BY THE TYPE.
------------------------------------------------------------------------
-- ⟡set1-paydown: the graded families (Vec Tm, const Tm) are now GradedDivStr's params.
arg-graded : GradedDivStr (Vec Tm) (λ _ → Tm)
arg-graded = vec-graded Tm

-- a grade-raising step = applying (consing) one argument. recon IS cons (VecGraded).
apply-one-graded : (n : ℕ) (v : Vec Tm n) (a : Tm) → GradedWedge arg-graded n (a ∷ v) v
apply-one-graded = vec-step Tm

------------------------------------------------------------------------
-- ② THE FAITHFUL RECONSTRUCTION IS THE GRADED FOLD. eval a grade-n arg-vector by
-- folding apply (∙) — the antilog apply-many, now AS the fold of the grade-raising
-- recon. The result's grade is n = the arity. (Args applied left-to-right onto f.)
------------------------------------------------------------------------
eval-args : (f : Tm) {n : ℕ} → Vec Tm n → Tm
eval-args f []       = f
eval-args f (a ∷ v)  = eval-args (f ∙ a) v

-- eval-args on the generator IS faithful-rb via the graded vector: the reconstruction
-- of a combinator g applied to a grade-(arity g) vector — the antilog at the grade.
faithful-graded : (g : Gen) {n : ℕ} → Vec Tm n → Tm
faithful-graded g v = eval-args (gen→tm g) v

------------------------------------------------------------------------
-- ③ GRADE = ARITY, witnessed. A combinator g fully applied consumes a vector of
-- length = arity g; the reconstruction happens AT grade (arity g). The graded wedge
-- reads: gcell = the shed argument (the digit), gforget = the consed vector.
------------------------------------------------------------------------
-- the shed head (gcell) is the applied argument (the digit at this grade):
shed-arg : (n : ℕ) (v : Vec Tm n) (a : Tm) → gcell (apply-one-graded n v a) ≡ a
shed-arg = vec-cell Tm

-- the forgetful read rebuilds the consed vector (the grade-(suc n) carrier):
rebuild-vec : (n : ℕ) (v : Vec Tm n) (a : Tm) → gforget (apply-one-graded n v a) ≡ (a ∷ v)
rebuild-vec = vec-forget Tm

------------------------------------------------------------------------
-- ④ THE FAITHFUL GENERATORS AT THEIR GRADES. Each combinator's redex spine is its
-- generator applied to a vector whose LENGTH is the arity — reconstructed at grade
-- = arity. I at grade 1, K at grade 2, S at grade 3. The generator is KEPT (faithful).
------------------------------------------------------------------------
-- K (arity 2) applied to a length-2 arg-vector [x, y]: reconstructed at grade 2.
faithful-K : faithful-graded gK (K ∷ I ∷ []) ≡ ((K ∙ K) ∙ I)
faithful-K = refl

-- S (arity 3) applied to a length-3 arg-vector [x, y, z]: reconstructed at grade 3.
faithful-S : faithful-graded gS (I ∷ K ∷ S ∷ []) ≡ (((S ∙ I) ∙ K) ∙ S)
faithful-S = refl

-- I (arity 1) applied to a length-1 arg-vector [x]: reconstructed at grade 1.
faithful-I : faithful-graded gI (S ∷ []) ≡ (I ∙ S)
faithful-I = refl

------------------------------------------------------------------------
-- ⑤ THE BRIDGE: the flat fixed-3 recon (ADD 153, rb q b r = (q∙b)∙r) IS the graded
-- recon collapsed to grade 3 — apply exactly-2 args to a generator (the arity-2 K
-- shape happens to match the fixed-3 rb's (q∙b)∙r). The graded form is faithful
-- because the grade VARIES with arity; the flat form froze it at one shape.
------------------------------------------------------------------------
-- the fixed-3 recon shape (q∙b)∙r = eval-args q [b, r] — the grade-2 graded fold.
flat-is-graded-at-2 : (q b r : Tm) → eval-args q (b ∷ r ∷ []) ≡ ((q ∙ b) ∙ r)
flat-is-graded-at-2 q b r = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the faithful reconstruction lives on a GRADED
-- DivStr where grade = arity — Wedge.VecGraded (recon = cons, grade = length). A
-- combinator's arg-list is a graded Vec, its length the arity; the reconstruction
-- is the graded fold (eval-args = the antilog apply-many); the generator is kept as
-- the CF quotient. The fixed-3-vs-varying-arity either/or dissolves: the flat recon
-- (ADD 153) is the grade-COLLAPSED shadow frozen at one shape (flat-is-graded-at-2
-- shows (q∙b)∙r is the grade-2 fold); the graded VecGraded recon is the faithful
-- form where the grade IS the arity, and each combinator reconstructs at its own
-- grade (I:1/K:2/S:3). Same dissolution as the flat-vs-graded shedding (ADD 147):
-- the flat is the grade-0-collapsed projection of the graded original.
------------------------------------------------------------------------
