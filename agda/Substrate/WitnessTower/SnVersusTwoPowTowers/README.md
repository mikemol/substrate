# `SnVersusTwoPowTowers` — the two towers, and the sweep's two columns as their rungs

Column 1 (|Sₙ|) is Ⓣ₁'s rung-count (`perms-length`, via `SnVersusTwoPow.|S|-is-tower-count`).
Column 2's rung at level n is the Ⓣ₂ index type `Vec Bool n`, whose cardinality is 2ⁿ
(`T2RungCount` = `VecBoolCardinality.card-VecBool`, ◆AI-1d discharged).

```
Substrate.WitnessTower.SnVersusTwoPowTowers

◆AI-1e — the COVERING co-apex over SnVersusTwoPow's four co-apexes. The
|Sₙ|-vs-2ⁿ sweep is not four separate links to four separate homes; the four
co-apexes are readings of ONE structure the repo already names: the family
of WITNESSING TOWERS (Ⓣ₁, Ⓣ₂), each a GradedDivStr built by the witnessing
step rung(suc n) = (rung n, increment), with a fold back down.

The repo's own naming (verified):
  Ⓣ₁ = Sₙ    — WitnessTower.LehmerPath: "Sₙ is BUILT OF the witnessing step";
               the increment is an insertion choice (Fin (suc n)).
  Ⓣ₂ = ℚ / Cayley-Dickson — WitnessTower.EEATower: "ℚ is BUILT OF the
               witnessing step"; Algebra.CayleyDickson.Carrier zero = ℚ,
               Carrier (suc n) = Carrier n × Carrier n (the doubling); the
               increment is a Wedge / a doubling.
  Ⓣ₃ = the algebra ladder — WitnessTower.AlgebraLadder (increment = a LAW).

BOTH towers are GradedDivStr instances (the tight common structure):
  Ⓣ₁ : WitnessTower.Wedge.Graded.tower-graded
           : GradedDivStr Perm      (λ n → Fin (suc n))
  Ⓣ₂ : Algebra.CayleyDickson.Grade.F₂-length-grading
           : GradedDivStr (Vec Bool) (λ _ → Bool)
These are re-exported together HERE so the covering structure is one import,
not a prose observation.

The four SnVersusTwoPow co-apexes, as readings of this covering apex:
  (1) |Sₙ| = factorial n = |perms n|   is the RUNG-COUNT of Ⓣ₁ (perms-length).
  (2) 2ⁿ = |Carrier n basis|           is the RUNG-DIMENSION of Ⓣ₂
                                       (Cocycle.e : Vec Bool n → Carrier n).
  (3) ceil-exp = μsearch               is an EXTRUDER (a fixpoint tower, the
                                       same suc-step-to-fixpoint idiom).
  (4) complement / 8 = HodgeDim4       is the rung-3 SEAM where the two
                                       towers meet (24 + 8 = 32 = 2⁵).

THE DEEPER SHARED STRUCTURE (why this covering apex is load-bearing, not a
filing cabinet): BOTH towers carry a SIGN COCYCLE.
  Ⓣ₁: sign = stab-parity (this session — SignStabTotal: sign factors through
       the Stab retraction; the V₄-coset is the kernel).
  Ⓣ₂: sign = ε, the Cayley-Dickson cocycle (Cocycle.ε : Vec Bool n →
       Vec Bool n → Bool, eᵢ·eⱼ = ε(i,j)·e_{i⊕j}).
So |Sₙ|-vs-2ⁿ is the comparison of two SIGN-CARRYING GradedDivStr towers, and
the n=4 seam is where the permutation-sign side (24 = |S₄|) and the
Cayley-Dickson-sign side (32 = 2⁵) coincide up to the Hodge-8 completion.
That is the content of K-cayley-dickson-level4 the sweep formalises.

--safe --without-K. Verified on Agda 2.8.0.
```
