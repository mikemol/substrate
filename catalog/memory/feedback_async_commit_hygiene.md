---
name: feedback_async_commit_hygiene
description: "Structural commits force a full build that exceeds the 2-min foreground limit — run them in background; rely on the task-completion notification, not ad-hoc pgrep polls (which self-match and hang)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

Two operational hazards, one root — **long/async operations run through the harness, not by hand.**
Both bit during the Ⓓ discovery arc (2026-07-05):

1. **Background build-triggering commits.** A *structural* commit (a `.agda` add/rename/signature/
   import change — INCLUDING a comment appended to a `data`/`record` line, which the conservative
   signature-detector rounds up to structural) forces the pre-commit full build (~2.5min > the 2-min
   Bash foreground limit). Run in the FOREGROUND it gets SIGTERM'd mid-hook: the commit **aborts**,
   HEAD unchanged, files left staged, a stale `precommit-report.txt` behind. Fix: run every
   build-triggering `git commit` with `run_in_background: true`. Non-structural commits (scripts,
   markdown, hook edits) skip the build when the stamp is fresh (<7d) and are foreground-safe.

2. **Don't poll with a self-matching `pgrep`.** Waiting on the background build with
   `until ! pgrep -f full_build_check; do sleep; done` **never terminates**: the polling shell's own
   command line contains the string `full_build_check`, so `pgrep -f` matches ITSELF. The whole poll
   is unnecessary — the harness **notifies on background-task completion** (the `<task-notification>`
   event). Rely on that. If you must detect a process, match on something absent from your own
   command (e.g. `pgrep -af 'python3.*full_build'`) and eyeball the hit.

**Why.** Both waste a full build-cycle of wall-clock and leave confusing residue (an aborted commit
looks like a hung build; a self-matching poll looks like a build that never ends). The harness
already gives the two correct primitives — `run_in_background` for the long op, the task
notification for its completion. Reaching for foreground + hand-rolled pgrep re-implements them
worse. Related: [[feedback_wait_for_postcommit_amend_before_push]] (the post-commit amend must
settle before push), [[feedback_commit_on_main_ci_gated]] (the pre-commit build IS the gate).

**How to apply.** Structural commit → `run_in_background: true`, then wait for the task
notification, then verify HEAD advanced + `post-commit advisory (auto-captured)` marker before any
push. Never `until ! pgrep -f <string-in-my-own-command>`. And **verify push-state by `git fetch`
before asserting it** — `origin/main..HEAD` counts against the last-FETCHED ref, so "N ahead" /
"nothing pushed" is unverified until a fetch (this arc: I asserted "nothing pushed" while the
remote-tracking ref already held through catalog-db).
