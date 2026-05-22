# Naming: prefer existing categorical names

_(Substrate governance policy. Migrated from `memory/discipline/feedback_categorical_name_first.md`.)_

**Rule:** When surfacing an implicit construct in the substrate, check first whether category theory or universal algebra already has an established name for it. If so, use the established name — because its universal property IS the inference rule, already validated and composable with the rest of category theory. Don't invent substrate-local names when categorical names carry the inference rules with them.

**Why:** Sharpens [[feedback-expose-generator-not-orbit]] and [[feedback-continuous-via-discrete-inference-rules]] one level further. The earlier framings said "expose the generator" and "expose the constructor"; this says "the established categorical name *is* the generator/constructor, complete with its inference rule. Use it." Inventing substrate-local names duplicates work — you'd have to rederive the universal property as substrate axioms, and you'd lose composability with downstream categorical reasoning.

**How to apply:** When proposing a new substrate name (especially during [[shadow-architecture]] extractions):

1. Check whether the construct has a standard categorical name. Quick diagnostics:
   - "Failure of two quotients to commute" → **Beck–Chevalley failure** (or non-permutability of congruences, universal algebra side).
   - "Subset closed under a dynamic" → **subcoalgebra** (for general F-coalgebra) or **invariant subobject**.
   - "Triple intersection of orbits" → **wide pullback** in the subobject lattice.
   - "Refinement ordering on partitions" → **congruence lattice Eq(X)**.
   - "Eigenvector spec, construction-deferred" → **equalizer of (M·_) and (λ ⋆_)**.
   - "Graph linearization" → **free linearization functor** / path algebra.
   - "Cayley graph from generators" → **left adjoint to underlying-graph-of-presented-group**.

2. If a categorical name exists with a universal property, use it. The universal property IS the inference rule; no need to invent axioms.

3. If no categorical name exists, then invent a substrate-local name, but document explicitly that no established categorical handle was found. Future review may surface one.

**Diagnostic:** if a proposed substrate name's slice writes new axioms instead of citing a universal property, that's the warning sign — either a categorical name exists and was missed, or the construct is genuinely novel (rare).

**Tradeoff acknowledged:** sometimes the substrate's gauge-honesty discipline DOES require a substrate-local name that doesn't map to a standard categorical concept (e.g., "3+1 parity universal" is a substrate observation, not a standard name). The rule is "check first," not "always use categorical."

**Connection:** [[project-eliza-concept-orbit-catalog]] surfaced 5 candidate substrate names that all turned out to have categorical handles (Beck-Chevalley, subcoalgebra, wide pullback, congruence lattice, commutator of congruences). This memory generalizes the lesson.
