---
name: project-168-tower-as-fanout
description: "The substrate's |PSL(2,7)| = 168-gauge family (the Reserved↔SelfDual bijection's 168 F₂-linear choices) is structurally a FieldFanOut 3 over Z/168 → (F₂³, F₃, F₇). Sketched in Substrate.Algebra.PrimeFactor-168-FieldFanOut; concrete bond computations deferred."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

The substrate's 168-gauge family (per
[[project-reserved-selfdual-bijection-gauge]]) has 168 F₂-linear
choices for the Reserved↔SelfDual bijection at HodgeDim4. Since
168 = 2³·3·7 is NOT a prime power, the structural decomposition is
a multi-field bond tower (per
[[project-multi-field-tower-architecture]]) — specifically, a
FieldFanOut 3 with three host fields F₂³, F₃, F₇.

**Realized in:** `Substrate.Algebra.PrimeFactor-168-FieldFanOut`
(sketch — bond functions are placeholders; concrete mod-168
computations deferred).

**The fan-out shape:**

```
            Z/168 (source)
              /  |  \
       mod-8  mod-3  mod-7
            /    |    \
          F₂³   F₃   F₇
        (=Z/8)
```

**Connection to sacrifice ladder:**

The substrate's Cayley-Dickson-style sacrifice ladder for the
168-gauge (per
[[project-reserved-selfdual-bijection-gauge]])
is the GAUGE CHOICE for how to use the fan-out:

* Choose whether to flatten the fan-out into a chain (different
  chain orders → different sacrifice paths).
* Choose which F_p component to drop for a specific computation
  (= sacrificing F₂-linearity, V₄-subgroup-choice, bijectivity,
  cardinality).
* Each rung of the ladder = a different way to access the FanOut
  structure.

**Per [[project-3plus1-is-cone-instance]] bond extension:**

168 is the substrate's canonical example of "count NOT fitting a
single prime power, requires bonds." The FanOut shape (3 parallel
bonds) is the natural CRT-style decomposition; alternative chain
shapes (FieldTower variants) are gauge-equivalent representations.

**Concrete computation deferred:**

For substantive 168 work (computing CRT iso, validating gauge
choices, etc.), the placeholder bonds need replacement with real
mod functions. Each requires 168-case pattern matching. Per
[[feedback-roll-our-own-via-word-algebra]] discipline: structural
per-case enumeration; no stdlib mod.

The 168-FanOut sketch is sufficient for STRUCTURAL anchoring;
computational use is a follow-on.

**Connections:**

* [[project-reserved-selfdual-bijection-gauge]] — the original
  168-gauge framing.
* [[project-multi-field-tower-architecture]] — chain version
  (FieldTower).
* [[project-tree-shaped-field-bonds]] — fan-out vs chain gauge
  choice.
* [[project-tetrative-metacircularity]] — the 168-gauge sits at a
  meta-level of substrate's structural recursion.
