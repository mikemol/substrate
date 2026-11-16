---
name: feedback_never_noverify_to_bypass_gates
description: "never --no-verify (or otherwise bypass a pre-commit/CI gate) on the theory that the blocker is unrelated to your change; you can't prove your change didn't ALSO trip a gate, and bypass skips the gates protecting everyone — coordinate instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

NEVER use `git commit --no-verify` (or any gate bypass) because you've diagnosed the *visible*
blocker as unrelated to your change. The bypass disables **every** gate, not just the one you
diagnosed — so you lose the proof that your change didn't *also* trip a different gate. "The
blocker I know is unrelated" ≠ "I know there's nothing else." (User, 2026-06-15, on a jea
scripts-only commit blocked by a stale `Q/Makefile` from ANOTHER agent's untracked WIP `.agda`.)

**Why:** integrity gates on a shared worktree protect all agents; bypassing them to land your own
work silently removes that protection from everyone, and you can't distinguish "unrelated blocker"
from "two problems, one masking the other."

**How to apply:** when a repo-global gate (e.g. `gen_build_makefiles --check`) blocks your commit
for a reason you believe belongs to another agent's in-flight work:
1. Do NOT `--no-verify`. Do NOT "fix" the other agent's artifact yourself (e.g. regenerating a
   Makefile that would bake in their untracked half-written file).
2. Clear YOUR files from the **shared index** (`git reset HEAD <your paths>`) so the other agent's
   `git add`/commit can't sweep them in (the index is shared across agents in one worktree).
3. Leave an untracked coordination note next to the other agent's work proposing a git-integrity
   protocol: own-your-subtree, stage **by explicit path** (never `git add -A`), whoever owns the
   staleness clears it (commit+regenerate, or `git stash`/move-out so the tree is consistent),
   ping when green. Then HOLD your commit until the gate is honestly green.
See the realized note pattern (jea↔Q-layer) and [[feedback_silo_sprawl_orphans_fixes]] (multi-agent
shared state). Related: this is the commit-time face of "ground claims on the real current state,
not on what you assume."
