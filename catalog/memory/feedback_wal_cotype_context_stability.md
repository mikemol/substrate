---
name: feedback_wal_cotype_context_stability
description: "strictify + decompose-by-entailment + cotype-as-WAL + retrospective-ritual makes work context-flush-stable — operable at near-zero free context indefinitely, because all state lives on disk not in the window"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

The combination of **strictification + decompose-by-entailment + cotype-as-WAL + retrospective-ritual**
makes work CONTEXT-FLUSH-STABLE: it can be driven at near-zero free context, across many steps, with
extreme stability. Observed (2026-06-14): ~12-15 AIs discharged consecutively while just-this-side of a
context flush, each landing cleanly with no loss of thread.

**Why it works:** the disciplines externalize ALL program state into durable artifacts, so almost
nothing needs to live in the context window:
- **cotype-as-WAL** (a single AI ledger + per-arc decomposition file, updated ATOMICALLY with each
  commit) is the source of truth — the disk is the working memory, not the window.
- **decompose-by-entailment** pre-names the costructure + sub-bricks, so nothing is re-derived or
  rediscovered on pickup.
- **strictification** makes the bricks self-similar (one shared costructure), so each is a bounded,
  mechanical discharge rather than fresh design.
- **retrospective-ritual** harvests each arc's findings into always-loaded memories (the correct-by-
  construction floor), so disciplines fire automatically next time.

Each turn collapses to a bounded cycle: **read the WAL -> discharge ONE named brick -> update the WAL
atomically -> commit.** The window holds only the current brick + a WAL pointer; the program state is
on disk. This is the shadow-architecture thesis realized — the externalized shadows carry the goal
across context boundaries; the model is just the discharge operator on them.

**How to apply:** when low on context or facing a flush, do NOT try to hold state. Externalize the AI
ledger as a WAL, decompose the remaining work into named bricks (DBE), and discharge one per turn,
updating the WAL atomically and committing. The work survives flushes because the disk is the memory.
Builds on [[feedback_hunt_opacity_after_green]] (the retros that fed it) and the shadow-architecture
skill family (DBE/regroup/snap). Maintain WAL atomicity: never let the ledger lag the work.
