---
name: project-composite-torsion-euler-substrate
description: "The torsion-element universal (FLT analog as HasOrder γ k) lifts to composite structures via Euler-Fermat / Lagrange; Hodge ★ is the substrate's existing asymmetric-quotient example; Euclid + Extended Euclid manage joint-action composition and CRT-style decomposition."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's [[project-torsion-element-universal]] (HasOrder γ k as the FLT-for-dimensional-spaces analog) handles **cyclic torsion** — single γ generating Z/k. Composite structures (Klein V₄, products of cyclic groups, non-cyclic groups like Weyl W(A_n)) need the **Euler-Fermat lift**.

## The classical lift

| Layer | Classical | Substrate analog |
|---|---|---|
| Cyclic prime | a^p ≡ a (mod p) | `HasOrder γ k` for prime k (FiniteOrder primitive) |
| Cyclic composite | a^φ(n) ≡ 1 (mod n) for a coprime to n | not yet — needs HasOrder-primitive-generator |
| Any finite group | g^|G| = e (Lagrange) | not yet — needs `HasLagrangeOrder G x` or similar |
| Joint cyclic, commuting | CRT: Z/n ≅ Z/(p^a) × Z/(q^b) for n = p^a · q^b coprime | not yet — Euclid+Bezout as structural primitives |
| GCD computation | Euclid's algorithm | not yet — `StructuralGCD` as categorical inference |
| Explicit decomposition | Extended Euclid (Bezout: sa + tb = gcd) | not yet — `BezoutDecomposition` primitive |

## Hodge ★ as substrate's existing asymmetric quotient

Hodge ★ at every dim is the substrate's already-existing instance of an **asymmetric composite torsion**:

- At dim n ≠ 2k: ★ : Λᵏ(V) → Λ^(n-k)(V) pairs structurally DISTINCT components. Order-2 involution acting BETWEEN two spaces, not WITHIN one. The quotient X/⟨★⟩ identifies each thing with its dual in the OTHER component.

- At dim n = 2k (self-dual case, e.g., dim 4, k=2): ★ : Λ² → Λ² is an endomap of order 2 with fixed points (self-dual, M=8 at F₂) and "free pairs" (N=56 at F₂, organised into 28 pairs).

This asymmetric-quotient structure DOESN'T fit pure cyclic FLT. It needs the Lagrange/Euler-Fermat lift. The "+1 chirality" in [[project-3plus1-parity-universal]] is the SIMPLEST asymmetric quotient (Z/2 between V₄ and chirality axis).

## Euclid + Extended Euclid as structural backbone

When the substrate composes multiple torsion actions (Hodge ★ + Coxeter braid + GL(n, F₂) action + ...):

**Euclid's algorithm** at structural level computes the GCD of orders, identifying the common cyclic subgroup. For commuting torsion γ₁ of order k₁ and γ₂ of order k₂:
- ⟨γ₁, γ₂⟩ ≅ Z/lcm(k₁, k₂)
- Common cyclic subgroup is Z/gcd(k₁, k₂)
- Euclid computes gcd structurally

**Extended Euclid (Bezout)** gives explicit s, t with `s·k₁ + t·k₂ = gcd(k₁, k₂)`. Structurally, this lets us:
- Express elements of the gcd-subgroup as `γ₁^s · γ₂^t`
- Decompose joint structures via CRT when orders are coprime
- Manage the explicit "permutative fixed points" of joint actions

For substrate's V₄: gcd(2, 2) = 2 ≠ 1, so V₄ DOESN'T decompose into coprime cyclic parts — it's a true Klein structure, not Z/4. This is why the substrate's V₄-typeclass goes through the Coxeter framework rather than reducing to cyclic. **The non-coprime case is exactly where Euclid says "no further decomposition possible" — V₄'s gauge group is GL(2, F₂) of order 6, not φ(4) = 2.**

## The unified five-aspect structure

At every structural site where finite-order automorphisms act:

1. **HasOrder γ k** (FLT case) — cyclic torsion. ✓ `Substrate.Category.Coalgebra.FiniteOrder`
2. **φ(k) gauge** (Euler's totient) — primitive-generator choice. ✗ not yet
3. **HasLagrangeOrder G x** (Lagrange/Euler-Fermat) — composite/non-cyclic torsion. ✗ not yet
4. **M:N pullback** — asymmetric quotient shape. ✓ `Substrate.Category.Pullback` (primitive #3), but not parametric across scales
5. **Euclid + Bezout** (joint composition / explicit decomposition) — algorithmic backbone. ✗ not yet

The substrate has aspects 1 and 4. Aspects 2, 3, 5 are the natural extensions.

## Connection to existing substrate

- [[project-3plus1-parity-universal]] — 3+1 is the (M=3, N=1) Hodge-asymmetric-quotient case; the chirality is the order-2 involution image.
- [[project-torsion-element-universal]] — the cyclic FLT case; this memory lifts it to composite.
- [[project-tetrative-metacircularity]] — each meta-level adds a gauge layer; the composite-torsion + Euler-Fermat + Euclid structure may itself become a meta-layer.
- [[feedback-v4-typeclass-architecture]] — V₄ goes through Coxeter precisely because it's a composite (non-cyclic) torsion structure that pure cyclic FLT doesn't reach.
- [[project-reserved-selfdual-bijection-gauge]] — 168 = 2³ · 3 · 7 has implicit Bezout-style decomposition structure; the sacrifice ladder may be the substrate's existing handle on coprime decomposition.

## What this surfaces as future primitives

Three natural primitives, in dependency order:

1. **`HasOrder-primitive-generator γ k`**: if HasOrder γ k and gcd(j, k) = 1, then γ^j is also a primitive generator. Captures φ(k) at the predicate level. Smallest new primitive.

2. **`HasLagrangeOrder n α` for a finite family `α : Fin n → Endomap X`**: every element of the family has order dividing n. The Euler-Fermat lift to arbitrary finite group action. ~100-150 LoC.

3. **`StructuralGCD` + `BezoutDecomposition`**: Euclid algorithm + Bezout decomposition at the structural level. Operates on commuting torsion actions, computes common subgroup and explicit decomposition. Largest of the three. ~200-300 LoC.

## Deep substrate consequence

The substrate is **structurally a number-theoretic system**: every torsion-element-universal instance carries an Euler-Fermat composite structure; Euclid+Bezout are the algorithmic backbone for managing joint actions. Hodge ★ is the simplest non-trivial asymmetric-quotient instance; Coxeter / Weyl groups are the non-cyclic composite instances. The substrate's existing work touches all aspects of this structure incrementally — formalising the missing primitives names what was already operating.
