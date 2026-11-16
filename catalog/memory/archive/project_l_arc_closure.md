---
name: project-l-arc-closure
description: "L-arc 10-slice closure — Substrate.Groups.Coxeter.{SameCanonical,CanonicalCover,Lifted} land, Z2/Z3/Z4/V4-Coxeter same-canonical migrated. Discovered: n-refls applies only to uniform-output Cayley tables."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20608575-0873-42b7-b664-8addeb8207d9
---

The L-arc ("Lifted axioms") landed two complementary primitives for
eliminating Cayley-table enumerations in the substrate's Coxeter
group instances:

**Module: [[Substrate.Groups.Coxeter.SameCanonical]]**
- Generic `Word-≡-Dec : DecEq Gen → DecEq (Word Gen)` lifter.
- Insight: `same-canonical` for ZN-Coxeter groups ignores its
  Canonical witnesses; decision depends only on Word equality.
- Migrated: Z2-Coxeter, Z3-Coxeter, Z4-Coxeter, V4-Coxeter
  (collapses 4 + 9 + 16 + 16 = 45 refl lines to ~12 lines total).

**Module: [[Substrate.Groups.Coxeter.CanonicalCover]]**
- Polymorphic `n-refls : (X : Set) → (X ≡ X) × ... × (X ≡ X)` (n
  copies) for n = 2, 3, 4, 5, 6, 7, 8, 16, 24.
- Used by `Substrate.Groups.V4.Axioms.Lifted`'s
  `·-self-inverse-Word = canonical-cover (predicate) 4-refls`.
- The "named Cayley-table refl payload" primitive.

**Sharp boundary discovered:** the n-refls pattern requires UNIFORM
outputs (all Cayley cases reduce to the same `X ≡ X` shape).
HETEROGENEOUS Cayley tables (where each case has its own
LHS=RHS pair, like `bivector-to-tensor-symmetric` /
`Cardinality.from-to` / S3-on-V4 homomorphism proofs) cannot use
the polymorphic n-refls — they require explicit per-case
enumeration. Captured at [[feedback-expose-generator-not-orbit-applies]].

**Capstone re-export:** [[Substrate.Groups.Coxeter.Lifted]].

**Substrate-wide implication:** future Coxeter group instances
(Z5-Coxeter, Z7-Coxeter, ZN-Coxeter for any N) should derive their
same-canonical via `same-canonical-via-Gen gen-≟`, not by n²-case
enumeration.
