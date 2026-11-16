---
name: feedback_agents_read_only_no_write_swarms
description: "never SWARM write agents; ONE focused write agent at a time is fine and beneficial (host = controller, agent = focused executor); read agents fan out freely; write agents may run a leaner model (sonnet/haiku) when the plan/recipe is well-formed — the typecheck gate bounds the risk"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

User (2026-07-16, two-step correction): first "I don't want to use agents for swarming write
tasks. I only want to use agents for reads... I'm OK with something taking longer"; then reworded:
"we don't _swarm_ writes, but we do permit a single write agent running at any given time. It's
beneficial to have the host as controller and the write agent as focused." Given right after I
fanned 3 concurrent write-agents over 58 files in ⟡set1-rp-categoryof (green, but corrected anyway).

**Why:** parallel writers put concurrent uncontrolled edits into one working tree — the controller
cannot hold three writers' edit state; review and failure isolation degrade even when compiles pass.
A SINGLE write agent keeps the host in the controller role (plans, verifies, sequences) and the
agent focused on execution. Reads are side-effect-free, so fan-out stays fine there.

**How to apply:**
- Research / grounding / saturation / cascade-scoping → fan out read agents freely.
- Edits → inline mechanized (codemods, scripted batch edits), OR one write agent at a time,
  sequential, each batch verified before the next; longer wall-clock accepted.
- MODEL CHOICE for write agents: the host runs opus; a well-formed plan/recipe lets the write
  agent run leaner — `model: "sonnet"` for recipe-driven migrations with compile-verify loops,
  `"haiku"` for single-pattern mechanical edits. The isolate-typecheck gate (real exit codes)
  bounds a lighter model's risk: mistakes iterate, they don't land.

Relates to [[feedback_read_identity_from_sppf]], [[handoff-blind-spot]].
