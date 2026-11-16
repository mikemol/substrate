# `SKIFaithfulOnGraded` — the faithful SKI reconstruction, on the arity-graded carrier

```
{-# OPTIONS --safe --without-K #-}

Substrate.Algebra.R.Trace.SKIFaithfulOnGraded — ⟡ski-faithful-on-graded: wire
the faithful reconstruction (ADD 154, the antilog apply-many) onto a GRADED
DivStr where GRADE = ARITY, bridging the fixed-3 flat recon (ADD 153) and the
arity-varying antilog. The named center is Wedge.VecGraded: "recon IS cons,
building a vector = consing heads = the graded free construction, grade = length"
— which is EXACTLY arity-as-grade. The argument list of a combinator is a graded
vector; its length is the arity; recon conses one argument (grade-RAISING by 1).

So the arity-varying antilog IS the graded chain: apply-many f args = the fold of
the grade-raising recon over the arg-vector. One grade-1 step (apply/cons); the
combinator's arity is the grade it is reconstructed at. This DISSOLVES the fixed-3
vs varying-arity tension: the flat fixed-arity recon is the grade-COLLAPSED shadow;
the graded (VecGraded) recon is the faithful form where the grade IS the arity.
```

## The invariant (bottoming out)

```
THE INVARIANT (bottoming out): the faithful reconstruction lives on a GRADED
DivStr where grade = arity — Wedge.VecGraded (recon = cons, grade = length). A
combinator's arg-list is a graded Vec, its length the arity; the reconstruction
is the graded fold (eval-args = the antilog apply-many); the generator is kept as
the CF quotient. The fixed-3-vs-varying-arity either/or dissolves: the flat recon
(ADD 153) is the grade-COLLAPSED shadow frozen at one shape (flat-is-graded-at-2
shows (q∙b)∙r is the grade-2 fold); the graded VecGraded recon is the faithful
form where the grade IS the arity, and each combinator reconstructs at its own
grade (I:1/K:2/S:3). Same dissolution as the flat-vs-graded shedding (ADD 147):
the flat is the grade-0-collapsed projection of the graded original.
```
