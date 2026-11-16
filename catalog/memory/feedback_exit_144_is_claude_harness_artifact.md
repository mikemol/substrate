---
name: feedback_exit_144_is_claude_harness_artifact
description: "exit 144 = signal 16 = a Claude Code harness kill on a backgrounded/pipeline process during tool cleanup (issue #62297), NOT the box/membudget/systemd-scopes — measure the signal source before theorizing"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-23T18:57:06.089Z
---

Exit code **144 = 128 + 16 = signal 16**, and in this environment it is a **Claude Code HARNESS artifact**
(github anthropics/claude-code issue **#62297**): the harness emits an intentional exit 144 when a **backgrounded
or pipeline process is interrupted during tool cleanup**. It is NOT membudget, NOT `systemd-run --user --scope`
concurrency, NOT the box, NOT stale leases, NOT the sandbox.

**Why:** verified via `journalctl` — the systemd user manager (`systemd[1609]`) shows scopes **Starting cleanly**
even concurrently; the concurrent invocations that 144'd produce **no `Started …scope` entry at all** (killed at
the client before the D-Bus call), and there is no box-side SIGUSR1/OOM/D-Bus/Tasks error. `ulimit -n`=524288
(fds fine), `user-*.slice` TasksCurrent≪TasksMax. Even TWO concurrent membudget scopes 144, even through the
committed HEAD membudget (no sched-batch), foreground OR background, sandbox on OR off — the common factor is a
`( … ) & … & wait` subshell-pipeline or a `run_in_background` job, i.e. the harness's own cleanup.

**How to work with it:** run heavy builds **FOREGROUND, non-piped** (a serial foreground loop of `agda`/`membudget`
runs clean — the mid-integrate foreground commit landed while its background twin 144'd). For a job that exceeds
the **2-minute foreground limit** (which surfaces as exit 143/SIGTERM, a DIFFERENT signal), **background it with a
trailing `sleep`** so the wrap-up doesn't trip the 144 — the user's fix; a `git commit` backgrounded as
`( git commit …; echo rc=$? > marker; sleep 12 )` then landed exit 0.

**Why this is load-bearing:** I burned ~15 turns theorizing the 144 as a membudget/systemd-scope-concurrency/box
failure, building an elaborate "concurrent scopes fail" model from correlation (parallel→144, serial→works),
before the user's issue-link settled it. The tell — an unexplained exit ≥128 on a parallel/backgrounded command —
is the signal to **measure the signal source** (the box journal, the exact signal number, whether the OS logged
anything) BEFORE concluding a tool/box defect. Widens [[reread-meters-toctou]] and
[[feedback_measure_instrument_before_theorize]].
