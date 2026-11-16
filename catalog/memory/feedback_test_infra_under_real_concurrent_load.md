---
name: feedback_test_infra_under_real_concurrent_load
description: "Concurrency/infra changes must be tested under their REAL parallel load before shipping — a single-subdir 'fresh-shell OK' is not a make -j test. The membudget make-routing (c2def4b) passed a one-dir check but DEADLOCKED a wide make -j; the lock bug only manifests under concurrency."
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

**2026-06-26.** I shipped the agda-shim make-routing (commit c2def4b, "tested fresh-shell") having only
built ONE small subdir through it. The user then ran a real wide `make -j` and it **deadlocked**. Root
cause was a latent concurrency bug in `scripts/membudget`'s lock that ONLY appears under parallel load:
`with_lock()` opened a fresh fd per call (two open-file-descriptions to the same lock → the EXIT-trap
`release` could flock against the lock the acquire-loop held → self-deadlock), plus `ensure()` outside
the lock (cold first-wave `cat >` race). Fixed in 1b45f53 (single re-entrant lock fd + ensure-under-lock
+ same-dir atomic gc rename); verified with a 3-case concurrency stress harness (cold-race, oversubscription
block-and-proceed, SIGTERM-mid-hold).

**Why:** a deadlock/race is invisible to a serial smoke test by construction — the very property under
test (mutual exclusion, init serialization) requires ≥2 concurrent actors to exercise. "Fresh-shell OK on
one module" tests the PATH wiring, not the SEMAPHORE.

**How to apply:** when a change touches a lock/semaphore/budget/shared-file or the build's parallel path,
the acceptance test MUST be concurrent (N simultaneous actors, oversubscribe the resource, kill a holder
mid-section) BEFORE committing — and ideally a standing self-test (e.g. `membudget selftest`) the pre-commit
runs, so the regression is caught by construction not by the user.

**DEEPER LESSON (2026-06-26, user correction after I shipped TWO bad lock fixes — deadlock, then cross-repo
STARVATION).** For a LOCK, don't iterate on symptoms (gc-churn, herd, backoff). Go to the hygiene INVARIANTS
first, because a lock's whole job is correctness under concurrency + disruption:
  1. **Bounded acquire** — every `flock` uses `-w TIMEOUT`; NEVER block forever (no-timeout = the starvation).
  2. **Death-release by construction** — the lock fd must NEVER cross a fork (open in with_lock, close in
     unlock; section never forks) so NO child inherits it → the KERNEL releases on the holder's death by ANY
     signal (SIGKILL/OOM/cgroup-teardown). A persistent fd inherited by the long-lived child is exactly how a
     killed holder left the lock stuck → cross-repo deadlock. There must be no userspace cleanup to skip.
  3. **PID-reuse-proof liveness** — identify owners by `pid:starttime` (/proc/pid/stat field 22), not bare pid.
  4. Critical sections are pure file-IO (never hold the lock across a compile/wait); the hot path is lock-free
     (optimistic snapshot) + backoff so other repos see the lock free.
membudget is modeled on a recursive WaitForSingleObject; disruption (OOM-kills) is NORMAL operation for it, so
the locking kernel must be immune to disruption BY CONSTRUCTION — not patched per-symptom. Fixed in 7c61738.
Connects [[feedback_budget_concurrent_compiles]] and retrospective-ritual G9 (escalate the recurring class to
a non-skippable layer — here, a `membudget selftest` the pre-commit runs).
