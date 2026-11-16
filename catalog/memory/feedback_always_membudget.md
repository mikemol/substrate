---
name: feedback_always_membudget
description: "run heavy Python (and any hog) under scripts/membudget by default — don't qualify with 'it's safe'; the cgroup cap turns a memory regression into a clean diagnostic, and membudget is now lossless (stderr fix)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Run heavy Python — and any potentially-hungry command — under `scripts/membudget run <MB> <label> -- <cmd>`
**by default**. Do NOT reason "it's safe to run this one directly" (memory was already confirmed bounded,
etc.). User, 2026-07-13: *"Safe until it isn't. Stay in the habit of memory binding."* and *"Don't qualify
that. Fix the problem for the general case. Make it cheap to do the right thing. I don't want any motivation
to route around the preferred tooling."*

**Why it's strictly better, not just cautious:**
- The cgroup `MemoryMax` + `MemorySwapMax=0` makes a memory blowup a **clean, immediate diagnostic** (the
  kernel OOM-kills only that scope; the machine stays up; no swap → no MAJFLT thrash). Set the cap at the
  *diagnostic threshold* — e.g. a de-inlined run peaks ~600 MB, so a 2 GiB cap means "exceeding this = a
  regression." It caught the ⟡orbit-def-by-reference base64-id regression the moment it blew (journal:
  `scope: The kernel OOM killer killed … 2G memory peak`). See [[feedback_reference_is_a_handle_not_inlined]].
- membudget also captures per-run **time + maxRSS** (`/usr/bin/time -v`), the Python analogue of the Agda
  proof-cost-ledger — informative perf data, free.

**The friction was a real bug, now fixed (do not route around — fix the tool).** membudget's `unlock()` did
`exec {LKFD}>&- 2>/dev/null` — an `exec`+redirect with **no command makes the `2>/dev/null` PERMANENT**,
silently pointing the whole script's fd 2 at /dev/null for the rest of the run. It swallowed membudget's own
messages, the wrapped child's stderr, AND Python tracebacks (agda, stdout-heavy, was unaffected — why it went
unnoticed). Fixed to `{ exec {LKFD}>&-; } 2>/dev/null` (brace-group scopes the redirect); verified lossless
(committed 6714614). So there is now **no error-data cost** to running under membudget.

**How to apply:** default to `scripts/membudget run <MB> <label> -- python3 …` (or `bash -c '…'`) for any
non-trivial run; harness-track it (`run_in_background`) so the exit code is captured; pick `<MB>` as the
diagnostic ceiling. To read a scope's output when systemd routes it to the journal, use
`journalctl --user -u run-pNNNN-iNNNN.scope` (the transient scope name from the `Started run-…scope` line).
The correct-by-construction next step is a **python-membudget PATH shim** like the agda shim (⟡python-membudget-shim
— makes it automatic). Relates to [[feedback_measure_instrument_before_theorize]], [[gen-build-makefiles]].
