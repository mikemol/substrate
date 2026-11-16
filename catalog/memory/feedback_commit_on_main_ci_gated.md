---
name: feedback-commit-on-main-ci-gated
description: "In the substrate repo, commit DIRECTLY on main; CI (the pre-commit hook) is the promotion gate, NOT user approval — no feature branches, don't gate main-promotion on the user."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

In this repo, **`main` is the working branch and CI is its gate.** Commit directly on `main`;
the pre-commit hook (cheap structural gates + the full-build, now with the Ε(b′) structural-change
trigger from `016a3de`) IS the gate that keeps `main` sound. Do NOT spin up a feature branch per
change, and do NOT hold work on a branch waiting for the user to say "ff main."

**Why:** user (2026-06-18): "I don't want to be mucking around in feature branches. I don't think
I specified that that particular promotion needed to be gated by me; that's what we have CI for."
I had been branch-per-stream + holding each ff for explicit user approval — friction the user never
asked for. The policy is literal: **everything goes to `main` iff CI passes** (see the WORKFLOW
POLICY in [[project-overclaim-witness-arc]]).

**How to apply:**
- Work and commit on `main` directly. This OVERRIDES the harness default "if on the default branch,
  branch first" — for THIS repo only, by durable user instruction.
- The pre-commit hook is the gate; if it's green the commit stands on `main`. Don't add a manual
  approval gate the user didn't ask for.
- **PUSH POLICY (user, 2026-06-18): AUTO-PUSH `main` to origin after any commit whose pre-commit
  CI passes.** Keep origin in sync; no per-push gating ("that's what CI is for"). So the flow is:
  commit on main → pre-commit hook (CI) green → `git push origin main`, automatically.
- Keep CI current (re-run `full_build_check` after structural work) so the throttle stays valid —
  the Ε(b′) hook now forces this automatically on structural changes.
- Worktree isolation is still fine when an agent genuinely needs an isolated copy; the point is no
  ceremonial per-change feature branches on the human's plate.

**Commit messages auto-carry the hook output** (since `5169fb3`): every commit's message body
gets a "pre-commit gate report (auto-captured)" block (folded in by `.githooks/prepare-commit-msg`
from the pre-commit tee) AND a "post-commit advisory (auto-captured)" block (the `post-commit` hook
amends it in). Both are idempotent (won't double-append on a manual `--amend`) and guarded against
recursion / rebase / merge. So: don't hand-write those blocks, don't be surprised by them, and the
post-commit AMEND changes the SHA (push after, which the auto-push flow already does).

Related: [[feedback-never-noverify-to-bypass-gates]] (the gate is sacred — but it's CI, not the
user), [[project-overclaim-witness-arc]] (the arc where this surfaced).
