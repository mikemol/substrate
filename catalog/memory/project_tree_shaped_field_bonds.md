---
name: project-tree-shaped-field-bonds
description: "The substrate's multi-field bond infrastructure has two shapes — FieldTower (chains) and FieldFanOut (fan-out trees). For a composite count c = ∏ pᵢ^kᵢ, fan-out gives CRT-style parallel decomposition; chains give sequential prime-by-prime extraction. The gauge choice between shapes IS a structural decision."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's multi-field bond infrastructure now has TWO
complementary shapes:

* **FieldTower n** (chain) — sequence of n+1 host fields with n
  oriented bonds, each from field i to field i+1. Captures
  sequential prime-by-prime extraction (Z/30 → Z/6 → Z/2, etc.).

* **FieldFanOut n** (fan-out tree) — one source field with n target
  fields, each connected via an oriented bond from source. Captures
  CRT-style parallel decomposition (Z/30 → Z/2 × Z/3 × Z/5 via
  three parallel bonds).

**Same composite count, different shapes:**

For c = ∏ pᵢ^kᵢ:

* **Chain (FieldTower)**: extract one prime at a time. Z/(p₁·p₂·p₃)
  → Z/(p₂·p₃) → Z/p₃ → Z/1. The intermediate fields are quotients;
  the bonds are mod operations.

* **Fan-out (FieldFanOut)**: project to each prime in parallel.
  Z/(p₁·p₂·p₃) → (Z/p₁, Z/p₂, Z/p₃). The CRT iso says these
  determine the source completely.

Both are valid structural realizations of the same count. The CHOICE
between them is a gauge — neither is "more correct."

**Substrate examples:**

| Count | Chain (FieldTower) | Fan-out (FieldFanOut) |
|---|---|---|
| Z/6 = 2·3 | Z/6 → Z/2 (1 bond) | Z/6 → (Z/2, Z/3) (2 bonds) |
| Z/30 = 2·3·5 | Z/30 → Z/6 → Z/2 (2 bonds) | Z/30 → (Z/2, Z/3, Z/5) (3 bonds) |
| 168 = 2³·3·7 | F₂³ → F₃ → F₇ via chained mods | F₂³ × F₃ × F₇ via parallel |

**Connection to sacrifice ladders:**

Per [[project-reserved-selfdual-bijection-gauge]]: the
168-Reserved↔SelfDual gauge IS the choice between bond shapes. The
"sacrifice" at each ladder rung corresponds to picking a different
bond shape / chain order for the F₂³·F₃·F₇ decomposition.

**Combining chain + fan-out:**

Composite trees (chain with fan-out branches, fan-out with chain
sub-branches) capture more elaborate decompositions. For example:

* Z/60 = Z/4 × Z/15 = Z/4 × (Z/3 × Z/5): fan-out at top (Z/60 →
  Z/4, Z/15), then fan-out at Z/15 (→ Z/3, Z/5). Or chain top
  (Z/60 → Z/12 → Z/3) with fan-out at intermediate (Z/12 → Z/4,
  Z/3).

Each tree shape encodes a specific way of seeing the composite.

**How to apply:**

When the substrate observes a composite count c:

1. Factor c into prime powers.
2. Identify whether the natural USE is sequential extraction (chain)
   or parallel decomposition (fan-out).
3. Pick the corresponding primitive (FieldTower or FieldFanOut).
4. For elaborate cases, compose primitives into a tree.

**Connections:**

* [[project-multi-field-tower-architecture]]: chain (FieldTower)
  reading.
* [[project-3plus1-is-cone-instance]] bond extension: the
  cone-completion via bonds when M+N isn't a prime power.
* [[project-composite-torsion-euler-substrate]]: composite-order
  Euler-Fermat composes across the tree.

**Status:** primitive landed (FieldFanOut). Concrete instances
(Z/30 fan-out with full mod functions; composite trees) deferred.
A generic `FieldTree` (arbitrary DAG) is the next consolidation.
