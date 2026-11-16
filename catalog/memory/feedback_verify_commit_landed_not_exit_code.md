---
name: feedback_verify_commit_landed_not_exit_code
description: "A background/scripted git commit's exit code reflects the SCRIPT running, not the commit LANDING. The pre-commit gate can abort and leave files merely STAGED. Always `git log` that HEAD moved to a new hash before reporting 'committed'."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Caught 2026-07-11 (the graded-rig arc). I fired three background `git commit`s and reported all three
"committed" to the user — they had ALL ABORTED at the pre-commit quality gates (def/proof separation,
import-shape ratchet). HEAD never moved; the files sat merely STAGED. I had trusted the background
job's `exit 0`, which reflects the wrapper SCRIPT completing, NOT the commit succeeding. I told the
user something false three times, and only caught it when a later `git log` showed HEAD unchanged.

**Why:** a background/scripted commit is two layers — the shell wrapper (whose exit code you see) and
`git commit` inside it (which runs the pre-commit hook, which can abort). `exit 0` on the wrapper is
compatible with the commit ABORTING. This is the general trap: **reporting STATE from a PROXY signal
(exit code, agent report) instead of DIRECT verification of the real thing (git log / the actual
state).** I had verified the MATH (recompiled the modules green) but not the COMMIT.

**How to apply:** after ANY commit (foreground or background), before saying "committed / landed /
push-ready": run `git log -1` and confirm HEAD is a NEW hash with your message (and, per the
commit-on-main protocol, the `post-commit advisory` marker). If HEAD didn't move, the commit aborted —
read the commit log for the failing gate, fix it, recommit. The CLAUDE.md commit protocol already says
"wait for the advisory marker in HEAD before pushing" — this is a MISS of that covered measure, not a
new one: FOLLOW it. Sibling of [[feedback_wait_for_postcommit_amend_before_push]]. Generalises beyond
commits: never report a state you inferred from a proxy — verify the state directly.
