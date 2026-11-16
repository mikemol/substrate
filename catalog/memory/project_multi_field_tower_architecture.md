---
name: project-multi-field-tower-architecture
description: "When a structurally observed count factors into multiple prime powers, the substrate's host-field structure is a TOWER of FieldBonds (FieldTower n in Substrate.Category.MultiFieldBond). Z/6 → Z/3 → Z/1 demonstrates FieldTower 2; |PSL(2,7)| = 2³·3·7 would be FieldTower 2 with three host fields."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

When a structurally observed count `c` factors into multiple prime
powers (c = p₁^k₁ · p₂^k₂ · ... · pₙ^kₙ for n > 1), the substrate's
host-field structure is a **tower of FieldBonds** — a sequence of
n+1 host fields connected by n oriented bonds.

**The primitive:** `Substrate.Category.MultiFieldBond.FieldTower n`
packages this as a record with:

* `Field : Fin (suc n) → Set` — the n+1 host fields.
* `Bond : (i : Fin n) → Field i → Field (suc i)` — n oriented bonds
  going from each field to the next.

**Substrate examples:**

* **FieldTower 1** (2 fields, 1 bond): the plain `FieldBond` case
  from `Substrate.Category.FieldBond`. Z/6 = F₂ × F₃ via CRT is the
  canonical instance.

* **FieldTower 2** (3 fields, 2 bonds): the next level. Realized in
  `Substrate.Algebra.Z6-FieldTower` as Z/6 → Z/3 → Z/1 (chain of
  quotients).

* **FieldTower n** for arbitrary n: the substrate's structural
  realization of n-prime-factor counts.

**Connection to specific substrate counts:**

* **|S₃| = 6 = 2·3**: FieldTower 1 (CRT-style F₂ × F₃).
* **Z/30 = 30 = 2·3·5**: FieldTower 2 (three primes).
* **|S₄| = 24 = 2³·3**: FieldTower 1 (F₂³ × F₃).
* **|PSL(2,7)| = 168 = 2³·3·7**: FieldTower 2 (three primes, three
  host fields). This is the substrate's
  [[project-reserved-selfdual-bijection-gauge]] 168-family.

**Chain vs fan-out:**

The FieldTower primitive captures a CHAIN of host fields (each bond
goes to the next field). For COMPOSITE counts with parallel-projection
structure (e.g., Z/30 projects to Z/2, Z/3, Z/5 simultaneously), the
chain interpretation requires picking an order (Z/30 → Z/6 → Z/2 vs
Z/30 → Z/10 → Z/2 vs Z/30 → Z/15 → Z/3 vs ...).

The chain order IS a gauge choice. Different chains realize the same
composite count with different intermediate fields. The substrate's
"sacrifice ladder" (per [[project-reserved-selfdual-bijection-gauge]])
is the chain-order choice for the 168 = 2³·3·7 tower.

**Future arc — Tree-shaped FieldBond:**

A `FieldTree` primitive (deferred) would generalize from chains to
arbitrary directed acyclic tree structures, capturing parallel
projection cleanly. The substrate's CRT iso Z/30 ≅ Z/2 × Z/3 × Z/5
is naturally a fan-out tree (Z/30 at root, three primes at leaves).

**How to apply:**

When the substrate observes a composite count c = ∏ pᵢ^kᵢ:

1. Compute the prime factorization.
2. Choose a chain order (sacrifice/gauge choice).
3. Instantiate FieldTower (n-1) for the n-prime case.
4. Each bond is an oriented mod operation between adjacent fields.

**Connections:**

* [[project-3plus1-is-cone-instance]] bond extension — multi-field
  bonds are the structural response to non-prime-power totals.
* [[project-composite-torsion-euler-substrate]] — composite-order
  Lagrange via Euler-Fermat decomposes across the tower.
* [[project-reserved-selfdual-bijection-gauge]] — the 168-family's
  sacrifice ladder IS the FieldTower's chain-order gauge choice.

**Status:** primitive landed, FieldTower 1 (Z6-FieldBond) and
FieldTower 2 (Z6-FieldTower) instances exist. Tree-shape and
generic CRT decomposition deferred.
