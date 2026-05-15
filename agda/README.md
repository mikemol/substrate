# Substrate — Agda formalisation

Constructive proof-out of the clarified foundation
([../catalog/clarified_foundation.md](../catalog/clarified_foundation.md))
before any executable rewrite. Each cocycle catalogued in
[../catalog/cocycles.md](../catalog/cocycles.md) is realised as an
instance of a generic `CocycleStructure` record; the discipline rules
in clarified_foundation.md become type-level constraints that Agda
mechanically checks.

## Scope (this session — Tier B)

- **S1** `Substrate.Cocycle` — generic `CocycleStructure` record.
  The repeatable form across all 5 substrate cocycles.
- **S2** Group prereqs — thin wrappers around `Algebra.Group` from
  agda-stdlib where needed; otherwise use stdlib directly.
- **S3** `Substrate.Groups.V4` — Klein four-group construction
  with decidable equality and Cayley-table proof. Smallest
  interesting concrete group; foundation for CY-5.
- **S4** `Substrate.Cocycles.V4Signature` — the CY-5 V_4-signature
  cocycle as a `CocycleStructure` instance. Bijection between the
  24 valid (source, sink, witness) signatures and S_4 elements;
  V_4 action partitioning into 6 orbits.

Deferred to subsequent sessions:

- **S5** Isomorphic-storage variant — requires cubical Agda for
  paths-as-equalities; needs `agda/cubical` library cloned.
- **S6** CY-2 K-rule cocycle instance — second cocycle to validate
  the abstraction generalises.
- **Other cocycles** — CY-1, CY-3, CY-4, CY-6, CY-7, CY-8, CY-9.
- **SP-1 metacircular fixpoint** — likely needs W-types / coalgebras
  / cubical for the loop-closing identification.

## Foundations chosen

- **Agda 2.6.4.3** (apt-distributed; ubuntu-packaged stdlib at
  `/usr/share/agda-stdlib`).
- **`--safe --without-K`** — strict MLTT, compatible with cubical
  reasoning. No axiom-K, no LEM. Aligns with the corpus's
  LEM-rejection discipline at type level: the type system itself
  refuses to admit double-negation elimination.
- **agda-stdlib** for groups, finite sets, decidable equality,
  setoids.
- **cubical Agda** (future) for the isomorphic-storage variant
  (S5). When we add it, the cubical library lives at
  `agda/cubical/` (git submodule from
  `https://github.com/agda/cubical`).

## How to type-check

```bash
cd agda
agda Substrate.agda
```

(or `agda --safe Substrate.agda` to verify the `--safe` discipline.)

## Discipline rules expressed at type level

The clarified foundation's 11 discipline rules
([../catalog/clarified_foundation.md § Discipline rules](../catalog/clarified_foundation.md))
become Agda obligations:

- **Rule 1** (gauge-vs-invariant separation): `CocycleStructure`'s
  `Base` and `Invariant` are separate fields; mixing them produces a
  type error.
- **Rule 5** (content-address by invariant only): functions whose
  contracts mention only the invariant type cannot accept a
  gauge-relative coordinate as input. Confused encoding is a type
  error.
- **Rule 11 (strong)**: `IsomorphicStorage` (S5, deferred): the
  base type IS the invariant type via a definitional or
  propositional equality. Storing v4_delta-style coordinates is
  expressible only in the weak variant; in the strong variant the
  type system rejects it.

Rules that *aren't* easily type-encoded (charter discipline,
existence-form findings, parametrisation of selection functions)
become documentation conventions inside Agda modules but are
mechanically enforced where possible.

## Cross-references

- [../catalog/cocycles.md](../catalog/cocycles.md) — cocycle records
  the Agda modules realise.
- [../catalog/idea_lattice.md](../catalog/idea_lattice.md) — the
  9-level structural ordering this formalisation follows.
- [../catalog/clarified_foundation.md](../catalog/clarified_foundation.md)
  — discipline rules the type system mechanically checks.
- [../catalog/drift_archaeology.md](../catalog/drift_archaeology.md)
  — the LLM pathologies these proofs are designed to make
  structurally impossible (Type-D rigidifications cannot survive
  type-checking under the strong rule 11).
