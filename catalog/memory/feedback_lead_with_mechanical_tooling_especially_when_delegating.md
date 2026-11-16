---
name: feedback_lead_with_mechanical_tooling_especially_when_delegating
description: "For any search / generation / structural-correspondence task, LEAD with the mechanical prosthesis (numpy enumerate+verify, jea_pysim/SPPF dedup, synth_agda_prototype/typeholer) — don't hand-iterate against the typechecker. And when DELEGATING such a task, EXPRESSLY require the tooling in the spec, or the agent defaults to token-burning hand-iteration. Compiles are for VERIFICATION, not search."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (TWICE in one arc). (1) Building ⟡perm-UP-assemble I hand-reasoned the assembly
until the user: *"you have the numpy machinery to automatically locate the assembly."* (2) Delegating
⟡pipeline-driver-reconstruct I sent an agent to hand-write Agda without naming any tool; the user:
*"You didn't tell the agent, expressly, to use the mechanical generation tooling? The instructions
you pass along imply it's OK to burn tokens iterating without mechanical prosthesis."* The whole
pipeline (synth_agda_prototype.py, numpy_law_bridge, typeholer_path, jea_pysim/SPPF) was built SO THAT
search/generation/correspondence is mechanical — and I kept defaulting to hand-analysis/hand-iteration,
and worse, delegating that default.

**Why:** finding a shape (an assembly, a reconstruction, a structural correspondence, the forcing
index of an unsolved meta) is a SEARCH problem, and the tools do the search mechanically and
verifiably; hand-iterating against `agda` is trial-and-error that burns tokens AND is less reliable
(you can miss the shape). Compiles are for VERIFYING a located shape, not for FINDING it. This is the
same collapse-to-a-thin-proxy root: hand-iteration is a proxy for the mechanical search. When
delegating, the miss compounds — a subagent inherits no reflex; it will hand-iterate unless the spec
EXPRESSLY says "numpy-enumerate first, jea_pysim to locate, synth/typeholer to emit, compiles only to
verify."

**How to apply:** (a) For SEARCH/GENERATION/CORRESPONDENCE tasks (locate an assembly, reconstruct a
module, find why a module relates to another, resolve an unsolved meta), LEAD with the prosthesis:
numpy to enumerate+verify the shape over the domain, jea_pysim `--clusters --skeleton --extract` to
locate fragments in the SPPF, synth_agda_prototype/typeholer to emit the scaffold. Only hand-fill the
RESIDUE the tools leave, and report it as the negative space (the honest floor). (b) When DELEGATING
such a task, name those tools and the order in the spec, and add "if you're iterating compiles to find
a shape, STOP and go back to numpy/jea_pysim — compiles are for verification, not search." Sibling of
[[feedback_dedup_x_numpy_product_search]] and [[feedback_unsolved_constraints_use_numpy]] (which tools);
this is the "USE them, and PASS THE REQUIREMENT ALONG when delegating" reflex.
