---
name: feedback_wait_for_postcommit_amend_before_push
description: "this repo's post-commit hook AMENDS the commit (advisory) — wait for it to settle before pushing, or local HEAD diverges from what you pushed"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

This repo's `.githooks/post-commit` AMENDS the just-made commit (`git commit --amend --no-verify`) to append the categorical-grounding advisory, ending with the marker line `post-commit advisory (auto-captured):`. The amend changes the commit HASH **after** `git commit` returns.

**The bug (hit on Ⓟ.2):** I backgrounded `git commit`, then pushed in a later step. The push raced the amend — I pushed the PRE-amend hash, then the amend moved local HEAD to the post-amend hash → local and origin diverged → next push rejected (non-fast-forward), forcing a rebase.

**Why:** push the pre-amend commit ≠ the amended commit your local HEAD ends at. Same content, different hash, divergent history.

**The discipline — before EVERY push:**
1. Wait until the post-commit amend has SETTLED: `git log -1 --format=%B | grep -q 'post-commit advisory (auto-captured)'` is true (the marker is present). Only then is HEAD's hash final.
2. Then `git fetch` and confirm local is a fast-forward of origin (a sibling agent may also have pushed). If not, `git rebase origin/main` (new-file commits rebase cleanly).
3. Then push.

Do NOT push immediately after a backgrounded commit completes — the task completing is not the amend settling. (Pre-commit gate report is folded by `prepare-commit-msg` DURING the commit; the advisory is folded by `post-commit` AFTER, via the amend — that second fold is the one that moves the hash.) See [[feedback_commit_on_main_ci_gated]].
