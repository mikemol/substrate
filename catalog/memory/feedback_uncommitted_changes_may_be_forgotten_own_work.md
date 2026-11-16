---
name: feedback_uncommitted_changes_may_be_forgotten_own_work
description: "Unrecognized tracked modifications in the working tree — especially after a context compaction — may be your OWN forgotten work, not someone else's. git diff them and JUDGE vs the mission before dismissing as incidental; a compaction erases authorship provenance, not the changes."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (the rig-cat arc, just after a `/compact`). git status showed four modified
tracked files (`Algebra/Wedge/Registry.agda`, `RegistryHetQBridges.agda`, +2 generated). I read the
diff, saw a coherent refactor, and reported it as *"not my work this session … I'll leave it for
you"* — treating it as an incidental other-authored change to route around. The user corrected:
*"you likely forgot the refactor during a context compaction. You'll have to judge it in comparison
to the mission."* It WAS my own pre-compaction work — a ⟡set1-paydown dissolving the ObjCode/El
code-universe (−56 Set₁ cores, the mission's core metric), green and consumer-clean. I nearly
orphaned a landed mission deliverable.

**Why:** a context compaction drops the *episodic* memory of what I edited, but the working-tree
changes persist. So post-compaction, my own uncommitted work looks like a stranger's. "I didn't
create this" is a FALSE inference from absence-of-memory — the CLAUDE.md rule "if you didn't create
it, surface it" was written for genuinely-foreign changes and misfires here, because after a
compaction I can't tell what I created. Dismissing-as-incidental is the same collapse-to-a-thin-proxy
the mission fights: treating "I don't remember it" as "it isn't mine."

**How to apply:** when git status shows tracked modifications you don't recognize — ESPECIALLY at
session start or right after a compaction — do NOT label them incidental/foreign and route around.
`git diff` them, and JUDGE them against the mission (is this a paydown? a measured metric change like
`set1_baseline_cores.txt`? a coherent arc-consistent refactor? a rename that matches other in-flight
work?). If mission-aligned and green, it is almost certainly your own forgotten work — verify it
(recompile, check consumers) and commit it. Only after that judgment may you set it aside. The tell
that it's yours: it advances the current mission and its shape matches this arc's other moves (here,
the `Wedge⟦9e8d371e⟧` hash rename matched the residue arc's rename exactly). Sibling of
[[feedback_verify_commit_landed_not_exit_code]] (both: verify state directly, don't infer it from a
proxy — there, an exit code; here, my own missing memory).
