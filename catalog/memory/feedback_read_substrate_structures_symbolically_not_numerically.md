---
name: feedback_read_substrate_structures_symbolically_not_numerically
description: "The project reads its algebra SYMBOLICALLY / term-algebraically, not numerically. ℚ, quotients, bridges, CF are symbolic-quotienting structures — don't default to the numeric reading when assessing."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

Recurring this arc (2026-06): when I assess a substrate structure I default to its **numeric** reading; the project means it **symbolically — quotienting under a term algebra**. Corrections: (1) "ℚ is a setoid, not propositional ≡" ([[reference_Q_is_a_setoid_not_propositional]]); (2) on generalizing continued fractions to HetQ I wrote a long assessment about ring-law closure / arithmetic carriers — user: *"I don't really care about radix. And I don't really care about numbers; I think of this all as symbolic quotienting under a term algebra."*; (3) the bridging machinery is about *cross-homogeneity compatibility over arbitrary expression* (codecs/bridges between symbolic languages), not number-crunching.

Concretely: HetQ A B is the field-of-fractions / **localization of a term algebra**, the cross-multiply ⊗ is a term **constructor** (always closed — no arithmetic-closure question), and the "laws" are the **congruence** you quotient by (CrossEq's ≈R parameter), not ring axioms. The CF convergent ℕ×ℕ is a HetQ — symbolic, not a computed number. `recon` (Wedge), the SPPF intern key (OneForest), and ∘ (Functor) are the *term-combining operations* each bridge preserves.

**Why:** the numeric reading produces false "blockers" (e.g. "arithmetic doesn't close / laws aren't refl") that dissolve under the symbolic reading, and it misses that the real machinery is bridges/codecs between symbolic languages.

**How to apply:** before assessing effort/feasibility of anything touching ℚ / quotient / fraction / bridge / continued-fraction, ASK "what is this *as a symbolic/term-algebra structure*?" first; treat carriers as term algebras with congruences, operations as constructors, equalities as quotients. The numeric instance (ℚ over ℤ) is ONE instance; the general thing is symbolic. Sibling of [[reference_Q_is_a_setoid_not_propositional]] and the [[construct-dont-classify]] reflex. See the bridge taxonomy in [[project_open_threads]] (Ⓗ family).
