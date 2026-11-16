---
name: feedback_common_substructure_recursively
description: "faced with an either/or, find the common substructure that subsumes both, recursively — don't pick a side"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

When faced with an either/or, look for the common substructure, recursively.

**Why:** picking one side of a design dichotomy rigidifies a gauge-free
choice and often reintroduces the very friction it was meant to avoid. The
common substructure dissolves the dichotomy AND tends to fix incidental
problems (e.g. Agda metavariable inference) as a side effect.

**How to apply:** when you catch yourself choosing "A or B" (records vs
function-aliases, four bespoke cases vs one, Bool-test vs Set-witness,
gate-chain vs pipeline), name the structure both are instances of and
build on that instead; then re-apply the move to the result (the chain
turned out to itself be a gate; the order turned out to be the same
chain). Worked example: the Realizability Charter §4 collapsed four gates
to one typed cons-list `Chain` with two evaluations (`⟦_⟧?` / `Wit`)
bridged by one `sound` — the same cons-list as the substrate term-algebra
`UPTerm`. Making the realizer an inductive family (not a recursive
Set-function) also made every witnessed index inferable. See
[[project_realizability_charter_arc]].

This is the operational form of [[discipline/project_3plus1_is_cone_instance]],
[[project_cone_subsumes_equalizer_pullback]], and
[[feedback_composable_primitives_over_flat_enumeration]] — the merge-up /
cone reading applied as a turn-by-turn reflex, not just at architecture time.
Related: [[feedback_choice_rigidification_in_substrate]] (the failure this prevents).
