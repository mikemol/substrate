# Substrate.Algebra.Wedge.Graded — the graded wedge

THE GRADED WEDGE — the indexed lift of `Algebra.Wedge.DivStr`. The plain
`DivStr` has an UN-indexed carrier `C : Set` and a non-dependent
`recon : C → C → C → C`; that is exactly what blocked founding the
`WitnessTower` as a single `DivStr` (`WitnessTower.Wedge.Action`'s
obstruction note): the rung step's base is a `Perm n` and its remainder a
`Fin (suc n)`, both indexed by the SAME grade `n` — a link an un-indexed
carrier cannot hold.

The fix is to make THE INDEX THE GRADE: a ℕ-graded carrier `C : ℕ → Set`,
a per-grade remainder/digit type `R : ℕ → Set`, and a grade-RAISING
reconstruction `recon n : C n → R n → C (suc n)`. Then the rung step is a
single graded wedge, not a per-rung family — and the grade index is the
handle the grading conjectures (#2/#3/#4) hang on.

NOT "plain `DivStr` ⊂ `GradedWedge`" (a former overclaim — there is no such
degenerate embedding; the plain `recon C→C→C→C` and the grade-raising
`recon C n → R n → C (suc n)` are different shapes). The relation between
the plain and graded wedges is the FORMAL ALLEGORY: graded descent is the
Φ-chain refinement of `Category.Allegory.Refinement` (ALG-7), as
`F2.Polynomial.Wedge.TraceDescent` realises it for F₂[x]. The allegory, not
an embedding, is the bridge between the two grades.

⟡set1-paydown: the ℕ-graded carrier family `C : ℕ → Set` and the remainder
family `R : ℕ → Set` are Set-VALUED families, so — per the substrate stance
(families are module params, never fields,
[[set1-carrier-always-parameterize]]) — they are module parameters, not
record fields. `GradedDivStr` is `Set`, not `Set₁`; consumers write
`GradedDivStr C R`, and `C`/`R` are parameters, not projections
(`recon` stays a field projection).

Zero postulates, `--safe --without-K`, throughout this directory.

## Leaves

- `DivStr.agda` — `record GradedDivStr` (§1: the graded div-structure
  interface).
- `Wedge.agda` — `record GradedWedge` (§2: a grade-`(n+1)` element decomposed
  against a grade-`n` base by a remainder, with the witness equation).
- `Forget.agda` — `gforget` (§3, FORGETFUL read: evaluate the witness back to
  the grade-`(n+1)` element).
- `ForgetCorrect.agda` — `gforget-correct` (§3: `gforget` recovers `a`).
- `Cell.agda` — `gcell` (§3, PRESENTED read: the remainder is the digit).
