#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""procstruct.py — structural questions about THE PROCESS TREE: what substrate work is
running, what is ORPHANED, what it costs, and who holds a membudget lease.

⚑⚑⚑ WHY THIS EXISTS, AND IT IS FOUR MEASURED INCIDENTS IN ONE DAY (2026-08-24).
`ps` and `/proc` are STRUCTURED — pid, ppid, state, cmdline, utime+stime, starttime — and
this repo had no reader for them, so every question about running work was asked with a
shell pattern. The standing rule says a toolkit gap is WORK, not grounds for a pipeline;
this is that work. The incidents, each of which this file has a mode for:

  1. A FORK BOMB. `run_selftests` runs a 96-suite roster; `worklist_gate --selftest` is a
     member that also INVOKES the roster. Six generations, **load 54.93 on 10 cores, 68
     processes**. `ratchet.check_cycle` now refuses re-entry (⟡worklist-gate-recursion).
  2. THREE ORPHANS AT 66, 66 AND 48 CPU-MINUTES, `R` state, ~100% CPU, three cores pinned
     for over an hour — **found only because the operator asked**. A `pkill` pass had
     killed the LAUNCHERS and the children reparented to init. `pkill -f "membudget run
     192 selftest:"` cannot reach a worker whose wrapper is already dead. **This is the
     question no existing tool answers**, and it is `--orphans`.
  3. FORTY MORE ORPHANS from ONE legitimate `worklist_gate --selftest`. Load 6→29 in 90
     seconds. ⚑ The cycle guard bounds RE-ENTRY, not FAN-OUT WIDTH (gate-F13) — a correct
     single pass still forks 40 workers, and killing the launcher orphans all 40. That is
     `--tree`: one launcher with 40 children is a different fact from 40 launchers.
  4. ⚑⚑ THE INSTRUMENT ITSELF LIED. `pgrep -cf selftest` read **46** where the honest
     count was **40** — the harness's own `bash -c` wrapper CONTAINS the query string and
     matches itself. An agent hit this and so did the dispatcher, twice. A census that
     counts itself is `census-green-is-a-fact-about-the-census` arriving through the
     instrument built to prevent it. See `_excluded_pids`.

  5. ⚑⚑ THE FIX FOR (2) COULD NOT SEE THE QUIET HALF — Ⓟ8, and it is a CORRECTNESS gap,
     not a convenience one. After `--kill --apply` cleared two orphan subtrees at 534s and
     470s of CPU, `--running` still showed **six** processes: `query_registry` and
     `reconstruct` at **0.8s and 0.4s of CPU across 163 seconds elapsed**. Orphaned,
     blocked rather than burning, each holding a `membudget` lease nothing will release —
     and `--orphans`' cost floor called them "below the floor", which is true about their
     CPU and false about their status. A CPU floor is ANTI-CORRELATED with abandonment:
     the quieter the leak, the more invisible. That is `--abandoned`, a second predicate
     on the AGE axis, and it is deliberately NOT a lower floor on the first — see
     `IDLE_CPU_S`, `ABANDONED_AGE_S`, and the `--kill --abandoned` opt.

⚑ WHAT IS REUSED AND NOT REBUILT. `scripts/ratchet.py` already owns the `/proc` walk —
`ancestry(pid)` (bounded 64 hops, dead pid ends the walk, splits after the LAST `)`
because a comm field may contain spaces) and `is_interpreter_wrapper` (the process-KIND
test whose substring predecessor is gate-F8). Writing a second `/proc` parser here would
be a shared NAME without a shared authority, which is the defect `check_argv` and
`mutating_argv` were both consolidated to remove. This module imports them.

    procstruct.py --running                 substrate work running now, with cost
    procstruct.py --orphans                 reparented to init and still burning CPU
    procstruct.py --stranded                the EDGE census: reparented OR harness-rooted
    procstruct.py --chain PID               the ppid walk, so a verdict can be AUDITED
    procstruct.py --abandoned               orphaned AT ALL — burning or merely holding
    procstruct.py --tree                    launcher → workers, so fan-out WIDTH is visible
    procstruct.py --leases                  membudget ledger against the live tree
    procstruct.py --cost [N]                the N most expensive, by CPU seconds
    procstruct.py --kill [--abandoned] {--dry-run|--apply}   SIGTERM orphan subtrees,
                                            then RE-READ and report what is still there
    procstruct.py --selftest                the guarded cases

  7. ⚑⚑⚑ EVERY CLASSIFIER ABOVE ASKS ABOUT ONE NODE, AND ABANDONMENT IS AN EDGE — the
     defect this file's own concept names, live in this file. MEASURED 2026-08-25:
     `check_clause_audit.py --quiet` (pid 902955) burned **3224 CPU-seconds at 83% of a
     core for 65 minutes** while BOTH `--orphans` AND `--abandoned` reported ZERO. Both
     test `p.orphaned` — *is my parent in the reaper set* — and the answer was honestly
     NO: its parent (a `bash -c`) was alive throughout. The chain tells the story the node
     cannot: `902955 -> 902932 (harness shell) -> 3216402`, a task that was STOPPED. **When
     a per-item predicate cannot express the distinction, the discriminator is the
     RELATION.** That is `--stranded`, and `--chain` prints the evidence.

     ⚑⚑ AND THE EDGE IS NECESSARY WITHOUT BEING SUFFICIENT — my first cut overreached.
     The stale runaway and a LIVE `run_selftests` tree produce IDENTICAL chains (same
     harness-shell shape, same root, both burning CPU), so labelling both "stranded" would
     have reported a sibling agent's in-flight work as abandoned. Task state is simply not
     in `/proc`. The second ground is therefore `harness-rooted` — a CANDIDACY that narrows
     the field for an operator who knows which tasks run — and `--kill`'s population is
     deliberately unchanged.

  6. ⚑⚑ THE KILLER WAS INSTRUMENTED ON ITSELF — Ⓝ9. `--kill --apply`'s last line was
     `SIGTERM sent to N`, which is a fact about the SENDER. Incident 2 is exactly what a
     sender-side report cannot see: the signal WAS delivered, successfully, to a process
     that was not the one burning the core. The thing that HOLDS the outcome (the process
     tree) and the thing that DID the work (the `os.kill` loop) are different objects, and
     every instrument that names one is silent about the other. `kill_census` re-reads
     `/proc` after the sweep and reports four verdicts — and `absent` is deliberately NOT
     called "reaped", because nothing here can distinguish reaped from self-exited from
     never-really-in-the-subtree.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import ratchet                                                    # noqa: E402
from climode import Mode, Selftest, contract_rows                 # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: ⚑ SECONDS OF CPU BELOW WHICH AN ORPHAN IS NOT YET A RUNAWAY. An orphan is not by
#: itself a defect — a detached editor is fine. The incident-2 population was 66, 66 and
#: 48 CPU-MINUTES at ~100%. This is a REPORTING floor for `--orphans`, printed in the
#: header so a reader can see what the census excluded rather than inferring a clean tree.
#:
#: ⚑⚑⚑ AND IT IS THE RIGHT FLOOR FOR ONE QUESTION AND THE WRONG ONE FOR THE OTHER — Ⓟ8,
#: MEASURED 2026-08-24. After `--kill --apply` cleared the burning orphans, `--running`
#: still showed SIX processes: `query_registry` and `reconstruct` subtrees at **0.8s and
#: 0.4s of CPU over 163 seconds of elapsed time**. Blocked on I/O or a lock, not burning —
#: and therefore invisible to `--orphans` and to the `--kill` built on it.
#:
#: ⚑⚑ THE FLOOR ANSWERS "WHAT IS COSTING ME CPU". IT DOES NOT ANSWER "WHAT IS ABANDONED",
#: AND THOSE ARE DIFFERENT RESOURCES. A blocked orphan holds a `membudget` LEASE and will
#: never release it, because the process that would release it has no launcher left to
#: reap it — so the resource it wastes is precisely the one the whole semaphore exists to
#: ration, while contributing nothing to the metric the census sorts on. A CPU floor is
#: structurally blind to it: the quieter the leak, the more invisible.
#:
#: ⚑ SO THE ANSWER IS A SECOND PREDICATE, NOT A LOWER FLOOR. Lowering `IDLE_CPU_S` toward
#: zero would make `--orphans` report every detached shell and every editor — the census
#: that reports everything is as useless as the one that reports nothing, and it would
#: ALSO silently widen `--kill`, which is the one change a killer must never make by
#: accident. `abandoned()` is the separate reading; see it and `--kill --abandoned`.
IDLE_CPU_S = 5.0

#: ⚑⚑⚑ SECONDS THE KILLER WAITS BEFORE RE-READING THE TREE — Ⓝ9. SIGTERM is ASYNCHRONOUS:
#: `os.kill` returns as soon as the signal is QUEUED, not when the target has acted on it,
#: so a re-read taken immediately reports every target still alive and would read as a
#: total failure of a kill that in fact worked. This is a settle interval, and it is
#: deliberately SHORT: it is not a deadline the processes must meet, it is the point at
#: which the census is TAKEN, and whatever is still there is REPORTED as still there
#: rather than waited for. A killer that blocks until its targets die is a different tool
#: (and one that can hang forever on a `D`-state process); this one measures and says so.
KILL_SETTLE_S = 0.5

#: ⚑ ELAPSED SECONDS BELOW WHICH AN ORPHAN IS NOT YET *ABANDONED*, ONLY *NEW*.
#: `--abandoned` drops the CPU floor, so it needs a different guard against reporting
#: noise, and AGE is the honest one: a process orphaned two seconds ago may be a normal
#: double-fork daemonisation still setting itself up. The measured population had been
#: running **163 seconds**. This is deliberately well under that — the floor exists to
#: exclude the just-detached, not to re-introduce a threshold that hides the quiet leak.
#: Printed in the header, like `IDLE_CPU_S`, for the same reason.
ABANDONED_AGE_S = 30.0

MODES = {
    "--running": Mode(scans=True, why="substrate work running now, with its CPU cost"),
    "--orphans": Mode(scans=True,
                      why="reparented to init (ppid 1) while still holding CPU — the "
                          "question no existing tool answers (incident 2)"),
    # ⚑ A SECOND PREDICATE OVER THE SAME POPULATION, NOT A LOWER FLOOR ON THE FIRST —
    # Ⓟ8. `--orphans` answers "what is costing me CPU"; this answers "what is
    # ABANDONED", and a blocked orphan holding a membudget lease is the second without
    # being the first. See `ABANDONED_AGE_S`.
    "--abandoned": Mode(scans=True,
                        why="orphaned at all — burning OR merely holding a lease. The "
                            "quiet leak `--orphans`' CPU floor is structurally blind to"),
    # ⚑⚑⚑ THE EDGE PREDICATE — incident 7. `--orphans`/`--abandoned` both classify on ONE
    # NODE's parent; this classifies on the PATH TO THE ROOT, and it is the only one of the
    # three that can see a process whose parent is alive but whose chain is dead.
    "--stranded": Mode(scans=True,
                       why="the EDGE census: parent-is-a-reaper (a conclusion) OR the "
                           "ancestor chain roots in a harness shell (a CANDIDACY — live "
                           "and stale are indistinguishable from /proc). Incident 7"),
    "--chain": Mode(operand="PID",
                    why="the ppid walk for one pid, so a verdict can be AUDITED rather "
                        "than trusted — the edge this whole class turns on"),
    "--tree": Mode(scans=True,
                   why="launcher → workers, so fan-out WIDTH is visible (incident 3)"),
    "--leases": Mode(scans=True,
                     why="the membudget ledger cross-referenced against the live tree"),
    "--cost": Mode(operand="[N]", scans=True,
                   why="the N most expensive processes by CPU seconds"),
    # ⚑⚑ `--abandoned` IS AN OPT ON THE KILLER, NEVER A WIDENING OF ITS DEFAULT. A killer
    # that starts reaping more than it did yesterday, without the caller asking, is worse
    # than one that reaps too little: the under-reaping is VISIBLE (the process is still
    # there) while the over-reaping is a thing that silently stopped existing. So the
    # default population is unchanged — burning orphans — and the wider one is opt-in.
    "--kill": Mode(opts=("--dry-run", "--apply", "--abandoned"), scans=True,
                   writes=("process",),
                   why="SIGTERM the orphan WORKERS — the omission that made incident 2. "
                       "`--abandoned` widens to the quiet ones, EXPLICITLY. Re-reads the "
                       "tree afterwards and reports the DESCENDANT census, not its own "
                       "signal count (Ⓝ9)"),
    "--reapers": Mode(why="which pids ADOPT orphans here — pid 1 is NOT the answer on "
                          "this box, and assuming it was made --orphans read zero"),
    "--selftest": Mode(why="the guarded cases, including a CONSTRUCTED orphan"),
}

#: ⚑ A `suite`, and it constructs a real orphan rather than a `/proc` fixture. See
#: `_selftest`: a fabricated tree tests the MATCHER, not the INSTRUMENT (sql-F13).
SELFTEST = Selftest(state="suite")

CLK = os.sysconf("SC_CLK_TCK")


def _read(path):
    """File contents, or None. ⚑ A DEAD PID IS NOT AN ERROR — the tree moves under a
    census by construction, and raising on a racing exit would make the instrument fail
    exactly when the tree is busiest, which is when it is asked."""
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except (OSError, ValueError):
        return None


def _uptime():
    b = _read("/proc/uptime")
    return float(b.split()[0]) if b else 0.0


_REAPERS = None


def reapers():
    """{pid} that ADOPT orphans on this box — pid 1 and every child-subreaper.

    ⚑⚑⚑ THIS SET IS WHY `--orphans` WORKS HERE AT ALL, AND IT IS DERIVED, NEVER ASSUMED.
    Under a systemd user session the orphan of a session process is adopted by
    `systemd --user` (pid 1369 on this box), NOT by init — `PR_SET_CHILD_SUBREAPER`. A
    census hardcoding `ppid == 1` therefore reads ZERO on a tree full of orphans, which is
    exactly what my first cut did while three orphaned `membudget run` launchers sat in
    front of it.

    ⚑ DERIVED FROM `/proc/<self>/status`'s `NSpid`-free ancestry, not a name match. The
    honest question is "which pid would MY orphan be handed to", and the answer is
    obtained by walking self's own ancestry: the session manager is on it, above every
    process this repo launches. Matching on the string `systemd --user` would be a
    name test standing in for a kind test — the gate-F8 shape — and would miss a box
    running a different session manager, or a container's init.

    ⚑ SO THE SET IS: pid 1, plus every ANCESTOR OF SELF that is a direct child of pid 1.
    That is the session-root layer, which is what adopts. Cached: the answer cannot
    change within one census, and re-walking per process would make the scan quadratic.
    """
    global _REAPERS
    if _REAPERS is None:
        out = {1}
        for pid, _cmd in ratchet.ancestry():
            p = read_proc(pid)
            # ⚑ A DIRECT CHILD OF INIT ON SELF'S OWN CHAIN is the session root — the
            # layer an orphan of this session is handed to. Reading it off self's
            # ancestry means the answer is about THIS process's session, which is the
            # only session whose orphans this tool is scoped to.
            if p and p.ppid == 1:
                out.add(pid)
        _REAPERS = out
    return _REAPERS


class Proc:
    """One process, read from `/proc/<pid>`. Fields the incidents needed and no more."""

    __slots__ = ("pid", "ppid", "state", "cmd", "cpu_s", "elapsed_s")

    def __init__(self, pid, ppid, state, cmd, cpu_s, elapsed_s):
        self.pid, self.ppid, self.state, self.cmd = pid, ppid, state, cmd
        self.cpu_s, self.elapsed_s = cpu_s, elapsed_s

    @property
    def pcpu(self):
        """CPU seconds per elapsed second. ⚑ A RUNAWAY SHOWS ~1.0 — the incident-2 three
        were all ~100%, which is what separated them from a process merely sitting open."""
        return self.cpu_s / self.elapsed_s if self.elapsed_s > 0 else 0.0

    @property
    def orphaned(self):
        """Has this process lost its launcher? ⚑ ITS PARENT IS A REAPER — see `reapers()`.

        ⚑⚑ THE DISCRIMINATOR THAT MATTERS, AND `ppid == 1` IS THE WRONG SPELLING OF IT.
        A worker whose launcher was killed reparents and keeps running — that is what made
        three processes invisible to every `pkill -f <launcher pattern>` pass, since their
        own cmdline never contained the launcher's pattern. Not a property of the command
        line, which is why no pattern-matching tool can see it.

        ⚑⚑⚑ BUT ON THIS BOX ORPHANS DO NOT GO TO PID 1, AND MY FIRST CUT TESTED FOR PID 1.
        MEASURED 2026-08-24 by this file's own selftest: a CONSTRUCTED orphan reparented to
        **1369**, `/usr/lib/systemd/systemd --user`, which sets `PR_SET_CHILD_SUBREAPER`
        and adopts the orphans of every process in the user session. Three `membudget run`
        launchers were sitting at ppid 1369 on the live tree at that moment — genuinely
        orphaned, their `run_selftests` parent already gone — and a `ppid == 1` census
        reported **zero orphans** over them. A false ZERO gets banked while a false
        positive gets investigated: this is `census-green-is-a-fact-about-the-census`
        arriving inside the instrument written to prevent it, and it was caught ONLY
        because the suite constructs a real orphan instead of a `/proc` fixture (sql-F13).
        A fabricated tree would have asserted ppid 1 and passed.
        """
        return self.ppid in reapers()

    def __repr__(self):
        return "Proc(%d, ppid=%d, %s, %.1fs)" % (self.pid, self.ppid, self.state, self.cpu_s)


def read_proc(pid, uptime=None):
    """One `Proc`, or None if the pid died / is unreadable under us."""
    stat = _read("/proc/%d/stat" % pid)
    if not stat:
        return None
    stat = stat.decode("utf-8", "replace")
    # ⚑ SPLIT AFTER THE LAST `)` — the same rule `ratchet.ancestry` records: a comm field
    # may contain spaces and parens, so `stat.split()[3]` returns a state letter as a pid.
    try:
        rest = stat[stat.rindex(")") + 1:].split()
        state, ppid = rest[0], int(rest[1])
        utime, stime, starttime = int(rest[11]), int(rest[12]), int(rest[19])
    except (ValueError, IndexError):
        return None
    raw = _read("/proc/%d/cmdline" % pid)
    cmd = raw.replace(b"\0", b" ").decode("utf-8", "replace").strip() if raw else ""
    if uptime is None:
        uptime = _uptime()
    return Proc(pid, ppid, state, cmd, (utime + stime) / CLK,
                max(0.0, uptime - starttime / CLK))


def all_procs():
    """Every readable process. ⚑ A `/proc` SCAN IS A SAMPLE, and this reports what it
    could not read so the caller can say so (`scans=True` owes an incomplete-scan report —
    the whole reason `Mode.scans` is a declared field rather than an inferred one)."""
    procs, unreadable = [], 0
    up = _uptime()
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        p = read_proc(int(name), up)
        if p is None:
            unreadable += 1
        else:
            procs.append(p)
    return procs, unreadable


def _report_skipped(unreadable, what="process entries"):
    """⚑ THE INCOMPLETE-SCAN REPORT `Mode.scans` OWES. A census that silently drops what
    it could not read cannot distinguish a clean tree from a blind instrument."""
    if unreadable:
        print("  (%d %s vanished or were unreadable mid-scan — a /proc scan is a SAMPLE)"
              % (unreadable, what))


def _excluded_pids():
    """The pids a census must NOT count: self, and every ANCESTOR of self.

    ⚑⚑⚑ THIS IS THE DEFECT THAT MADE `pgrep -cf selftest` READ 46 WHERE THE TRUTH WAS 40.
    A shell wrapper's cmdline QUOTES the command it launched, so any pattern naming the
    work matches the harness's own `bash -c …`, the `python3 procstruct.py --orphans` that
    is asking, and every layer between. The over-count was 15%, silently, in the direction
    that manufactures work.

    ⚑⚑ AND THE EXCLUSION IS AN ANCESTRY SET, NOT A SUBSTRING TEST — gate-F8 exactly. The
    cycle guard's first cut compared `" ".join(sys.argv)` against each ancestor's command
    line under a comment claiming a process-KIND test, and it was MEASURED failing one
    argument apart: at generation 1 the process held `… cyc_inner.py 1` while its shell
    held `… cyc_inner.py 0`, so the launcher was not excluded. Any difference in spelling
    re-arms that, and it re-arms SILENTLY.

    ⚑ A PID SET HAS NO SUCH FAILURE MODE. `ratchet.ancestry` walks ppid links, which is
    what ACTUALLY happened rather than what a string happens to spell. Identity is by
    pid — exact, and immune to quoting, absolute-vs-relative paths and inserted flags.

    ⚑ NOTE WHAT IS DELIBERATELY *NOT* EXCLUDED: siblings and unrelated processes that
    merely mention the query. This census does not take a pattern at all (see
    `is_substrate`), so there is no query string to collide with in the first place —
    the self-match is closed by construction, and the ancestry set closes the residue.
    """
    return {p for p, _c in ratchet.ancestry()}


def is_substrate(p, repo=REPO):
    """Is this process substrate's OWN work?

    ⚑⚑ A PATH UNDER THE REPO ROOT, NEVER A WORD. "substrate" as a token matches an
    unrelated checkout, a browser tab's title in an argv, a grep for the word. The
    honest predicate is that the command line names a file under this repo — which is
    a fact about WHERE the code being executed lives, and is what "this repo's work"
    means. `paperkit/discriminate.py` running from a bazel execroot is NOT substrate's,
    and a word-match would claim it.

    ⚑ AND THIS IS WHY THERE IS NO `--pattern` MODE. Every incident here came from a
    pattern that matched more than it meant; adding a pattern flag would ship the
    defect back as a feature. The scope is structural.
    """
    return repo in p.cmd


def substrate_procs(procs=None, exclude=None):
    """[(Proc)] — substrate's own work, self and ancestors removed."""
    if procs is None:
        procs, _ = all_procs()
    ex = _excluded_pids() if exclude is None else exclude
    return sorted((p for p in procs if p.pid not in ex and is_substrate(p)),
                  key=lambda p: -p.cpu_s)


def subtree_cpu(root_pid, procs):
    """CPU seconds of `root_pid` AND every descendant.

    ⚑⚑⚑ THE COST OF AN ORPHAN IS ITS SUBTREE'S, NOT ITS OWN, AND MEASURING ITS OWN READ
    ZERO ON A LIVE INCIDENT. MEASURED 2026-08-24: three orphaned `membudget run` launchers
    sat at ppid 1369, each at **0.0 CPU seconds** — they are shell wrappers that do nothing
    but wait. Under a self-CPU floor `--orphans` reported **0** while `--tree` showed their
    children at 461 and 398 CPU-seconds and 90%+ of a core each. The launchers were the
    orphans; the burn was one and two layers below them.

    ⚑ THIS IS EXACTLY INCIDENT 2 SEEN FROM THE OTHER SIDE. There, a `pkill` reached the
    launcher and missed the worker; here, a census reached the launcher and missed the
    worker's COST. Same layer boundary, same blind spot, opposite operations — which is
    why the fix has to be structural (walk the tree) rather than a lower floor.
    """
    kids = {}
    for p in procs:
        kids.setdefault(p.ppid, []).append(p)
    total, stack, seen = 0.0, [root_pid], set()
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        for c in kids.get(pid, ()):
            total += c.cpu_s
            stack.append(c.pid)
    own = next((p.cpu_s for p in procs if p.pid == root_pid), 0.0)
    return total + own


def orphans(procs=None, exclude=None, idle_cpu_s=IDLE_CPU_S):
    """[(Proc, subtree_cpu_s)] — substrate work that lost its launcher and is still burning.

    ⚑ COST IS THE SUBTREE'S — see `subtree_cpu`. A wrapper's own CPU is ~0 by construction,
    so a self-CPU floor hides precisely the launcher-with-a-hot-worker shape that both
    incident 2 and incident 3 produced.

    ⚑ THE CPU FLOOR IS A REPORTING CHOICE AND IS PRINTED, NOT HIDDEN. An orphan at 0.1s is
    a detached shell; the incident population was 66, 66 and 48 CPU-MINUTES. A threshold
    that is not stated turns "nothing above the floor" into "no orphans", which is
    `census-green-is-a-fact-about-the-census`.
    """
    if procs is None:
        procs, _ = all_procs()
    out = []
    for p in substrate_procs(procs, exclude):
        if not p.orphaned:
            continue
        cpu = subtree_cpu(p.pid, procs)
        if cpu >= idle_cpu_s:
            out.append((p, cpu))
    return sorted(out, key=lambda pc: -pc[1])


def abandoned(procs=None, exclude=None, min_age_s=ABANDONED_AGE_S):
    """[(Proc, subtree_cpu_s)] — substrate work that lost its launcher, BURNING OR NOT.

    ⚑⚑⚑ Ⓟ8, AND IT IS A CORRECTNESS GAP RATHER THAN A CONVENIENCE ONE. MEASURED
    2026-08-24: after `--kill --apply` cleared two orphan subtrees at 534s and 470s of
    CPU, `--running` still reported SIX processes — `query_registry` and `reconstruct`
    subtrees at **0.8s and 0.4s of CPU across 163 seconds of elapsed time**. Every one
    of them was orphaned. `--orphans` reported them as *below the floor*, which is a
    true statement about their CPU and a false one about their status.

    ⚑⚑ THE FLOOR IS NOT WRONG — IT IS ANSWERING A DIFFERENT QUESTION, and merging the two
    questions under one threshold is what made the second unanswerable. "What is costing
    me a core" is a COST reading and wants a CPU floor. "What has been abandoned" is a
    LIFECYCLE reading and a CPU floor is actively anti-correlated with it: a blocked
    process burns nothing, so the quieter the leak the more invisible it is to the
    instrument. Two readings, two predicates, one population.

    ⚑ AND THE RESOURCE AT STAKE IS THE ONE THE WHOLE SEMAPHORE EXISTS TO RATION. An
    orphaned worker under `membudget run` holds its lease until it exits; its launcher is
    already dead, so nothing will reap it and nothing will release the lease. The ledger's
    GC covers a lease whose OWNER pid is gone — this population's owner pid is very much
    alive, just parentless. `--leases` already prints `⚑ ORPHANED` against exactly this
    row; what did not exist was a way to ENUMERATE the population without a live lease to
    look it up by, which is why the predicate is keyed on the process and not the ledger.

    ⚑ THE AGE FLOOR REPLACES THE CPU FLOOR RATHER THAN JOINING IT — see
    `ABANDONED_AGE_S`. Dropping to no floor at all would report every double-forked
    daemon in its first instants of setup; keeping the CPU floor would reproduce the
    blindness. Age is the axis on which "abandoned" and "just detached" actually differ.

    ⚑ THE SUBTREE COST IS STILL REPORTED, because a reader needs to know which half of
    this population is also a runaway. It is not a filter here; it is a column.
    """
    if procs is None:
        procs, _ = all_procs()
    out = []
    for p in substrate_procs(procs, exclude):
        if not p.orphaned:
            continue
        # ⚑ THE ELAPSED TIME OF THE ROOT, NOT OF THE SUBTREE. A launcher orphaned long ago
        # may have forked a fresh child a second back; the abandonment happened at the
        # root, and reading age off the youngest descendant would let a busy subtree keep
        # resetting its own clock and never qualify.
        if p.elapsed_s < min_age_s:
            continue
        out.append((p, subtree_cpu(p.pid, procs)))
    return sorted(out, key=lambda pc: -pc[1])


#: The GROUNDS on which a process can be judged abandoned — a CLOSED set, and there are
#: TWO because they have different causes, different next actions, and CRUCIALLY different
#: STRENGTHS.
#:
#: ⚑⚑⚑ `reparented` IS A PROPERTY OF ONE NODE; `harness-rooted` IS A PROPERTY OF THE PATH
#: TO THE ROOT. Collapsing them into one verdict is what hid incident 7 — see
#: `strand_ground`.
#:
#: ⚑⚑⚑ AND THEY ARE NOT EQUALLY CONCLUSIVE, WHICH IS WHY THE SECOND IS NOT NAMED
#: "stranded". MEASURED 2026-08-25, and it falsified my own first cut: the stale witness
#: (902955, a 65-minute runaway) and a LEGITIMATE live `run_selftests` tree (1343845,
#: census-sync work in flight) produce **structurally identical chains** — same harness
#: shell shape, same root, both actively burning CPU. The walk cannot tell them apart, and
#: a first cut that called both "stranded" reported healthy work as abandoned.
#:
#: ⚑⚑ SO THE SECOND GROUND IS A CANDIDACY, NOT A VERDICT. `harness-rooted` says only
#: *this chain roots in a harness shell whose task I cannot observe* — which is TRUE of
#: every task-launched process in this repo, live or dead. It NARROWS the field for an
#: operator who knows which tasks are running; it does not decide. Naming it "stranded"
#: would be the false-positive-into-a-ratchet hazard, in a tool whose sibling mode KILLS.
ABANDON_GROUNDS = ("reparented", "harness-rooted")

#: ⚑ The command substrings that mark a shell the HARNESS created for a task. A chain
#: rooted in one of these, whose task has since been stopped, is a STRANDED chain.
#: ⚑⚑ THIS IS A NAME TEST AND IT IS THE WEAK LINK — gate-F8, stated rather than hidden.
#: Every other discriminator in this file is structural (a pid set, a ppid edge, a repo
#: path) precisely because name tests rot. There is no structural marker for "the harness
#: made this shell": the kernel records a `bash -c` and nothing about who asked for it.
#: So the honest move is to match the string, DECLARE that it is a string match, and
#: report the population it cannot see rather than implying completeness.
HARNESS_SHELL_MARKS = ("/.claude/shell-snapshots/", "shell-snapshot")


def chain(pid, procs=None):
    """[(pid, cmd)] from `pid` up to the session root — THE EDGE, not the node.

    ⚑⚑⚑ REUSES `ratchet.ancestry` RATHER THAN RE-WALKING /proc, and the reuse is the
    point. `ancestry` already splits after the LAST `)` (a comm field may contain spaces
    and parens, so `stat.split()[3]` returns a state letter as a pid), already ends the
    walk on a dead pid instead of raising, and is already bounded at 64 hops. This module
    imports it exactly as `reapers()` does. Writing a second walker here would be a shared
    NAME without a shared authority — the `agda_files()`-in-four-bodies shape this whole
    toolkit exists to retire, committed inside the tool that reports it.

    ⚑ IT WAS REUSABLE AS-IS: `ancestry(pid)` already takes the pid as a parameter
    (defaulting to self), which is precisely the widening this needed and did not require.
    """
    return ratchet.ancestry(pid)


def strand_ground(p, procs=None):
    """(ground, chain, why) — WHY this process is abandoned, or (None, chain, why).

    ⚑⚑⚑ INCIDENT 7, AND IT IS `the-fact-may-be-an-edge-not-a-property` LIVE IN THE TOOL
    WRITTEN AGAINST THAT CLASS. MEASURED 2026-08-25: `check_clause_audit.py --quiet`
    (pid 902955) burned **3224 CPU-seconds at 83% of a core for 65 minutes**, and BOTH
    `--orphans` AND `--abandoned` reported it clean. Both classify on `p.orphaned`, which
    asks ONE question about ONE node — *is my parent in the reaper set?* — and the answer
    was honestly NO: its parent (902932, a `bash -c`) was alive the whole time.

    ⚑⚑ THE PARENT WAS ALIVE AND THE CHAIN WAS DEAD, AND ONLY THE CHAIN CAN SAY SO. Walk
    it: `902955 -> 902932 (bash -c … shell-snapshots …) -> 3216402`, a harness shell whose
    TASK WAS STOPPED. Nothing about node 902955, and nothing about its parent edge,
    distinguishes that from healthy work. Abandonment here is a property of the PATH TO
    THE ROOT — which is the interned concept exactly: *when a per-item predicate cannot
    express the distinction, the discriminator is the RELATION.*

    ⚑ SO THE TWO GROUNDS ARE REPORTED APART, NEVER MERGED (see `ABANDON_GROUNDS`):

      reparented     the parent IS a reaper — the launcher died and the kernel re-homed
                     this process. A CONCLUSION. `--orphans`/`--abandoned` already find
                     these. Next action: the subtree is unowned, kill it.
      harness-rooted the parent is ALIVE, and the chain above it passes through a harness
                     shell whose task state is NOT OBSERVABLE from /proc. A CANDIDACY, not
                     a conclusion. Next action: an operator who knows which tasks are live
                     reads the list; nothing here may be reaped on this ground alone.

    Merging them would make a zero mean two different things and would silently widen the
    killer, which is the one change a killer must never make by accident.

    ⚑⚑⚑ THE SECOND GROUND CANNOT SEPARATE LIVE FROM STALE, MEASURED. Chain for the stale
    runaway 902955 and chain for the LIVE `run_selftests` 1343845 differ in no field this
    walk reads: both are `<work> -> [bash .githooks/pre-commit] -> bash -c …shell-snapshots…
    -> code -> konsole -> systemd --user`, and both were burning CPU at the time. My first
    cut labelled both "stranded" and would have reported a sibling agent's in-flight work
    as abandoned. The chain is the right DISCRIMINATOR for incident 7 and is still not a
    SUFFICIENT one — reporting it as candidacy is what keeps that honest.
    """
    ch = chain(p.pid, procs)
    if p.orphaned:
        return "reparented", ch, "parent %d is a reaper" % p.ppid
    # ⚑ SELF-EXCLUSION IS LOAD-BEARING HERE IN A WAY IT IS NOT ELSEWHERE. THIS censusing
    # process is ITSELF run from a harness shell, so every chain it walks that passes
    # through its own ancestry would match the marker and the census would report its own
    # siblings — and itself — as stranded. The 46-vs-40 defect, one layer up: a census that
    # matches the harness it runs under counts the harness.
    mine = {q for q, _c in ratchet.ancestry()}
    for anc_pid, anc_cmd in ch:
        if anc_pid == p.pid or anc_pid in mine:
            continue
        if any(m in anc_cmd for m in HARNESS_SHELL_MARKS):
            # ⚑ THE SHELL BEING ALIVE IS NOT EVIDENCE THE TASK IS. A harness `bash -c`
            # outlives the task that made it — that is exactly the shape of incident 7,
            # where 902932 sat at 0.0s CPU for 65 minutes holding a dead task's child.
            return ("harness-rooted", ch,
                    "ancestor %d is a harness shell (%s) — task state NOT observable "
                    "from /proc; live and stale look identical here"
                    % (anc_pid, anc_cmd[:48]))
    return None, ch, "chain reaches the session root through live, non-harness ancestors"


def stranded(procs=None, exclude=None, min_age_s=ABANDONED_AGE_S):
    """[(Proc, subtree_cpu, ground, why)] — abandoned on EITHER ground, labelled.

    ⚑ THE AGE FLOOR IS KEPT from `abandoned` for the same reason it exists there: a
    freshly-forked process under a shell that is mid-teardown is NEW, not stranded.

    ⚑⚑ THIS DOES NOT REPLACE `abandoned()`, IT WIDENS IT — and the widening is reported
    per row rather than folded into a total. A caller that wants only the unowned subtrees
    (the killable population) still asks `abandoned`; this answers "what has lost its
    requester", which is a strictly larger and strictly less actionable set.
    """
    if procs is None:
        procs, _ = all_procs()
    out = []
    for p in substrate_procs(procs, exclude):
        if p.elapsed_s < min_age_s:
            continue
        ground, _ch, why = strand_ground(p, procs)
        if ground is None:
            continue
        out.append((p, subtree_cpu(p.pid, procs), ground, why))
    return sorted(out, key=lambda r: -r[1])


#: The verdicts `kill_census` can return per target pid — a CLOSED set, and the point of
#: Ⓝ9 is that there are FOUR of them rather than the two a `--kill` naturally reports.
#: ⚑⚑ `absent` AND `survived` ARE NOT "success" AND "failure", and collapsing them to a
#: pass/fail bit is the whole defect. See `kill_census` for what each one does and does
#: NOT license a reader to conclude.
KILL_VERDICTS = ("absent", "survived", "reparented", "new-child")


def kill_census(targets, before, after):
    """[(pid, verdict, note)] — the POST-KILL descendant census. Ⓝ9.

    `targets` is what the killer aimed at, `before` the `/proc` sample it aimed with, and
    `after` a fresh sample taken once the signal has had a moment to land.

    ⚑⚑⚑ THE TOOL EXISTS BECAUSE OF THIS CONCEPT AND DID NOT CHECK FOR IT. `--kill`'s own
    branch carries three ⚑⚑⚑ comments about incident 2 — a `pkill` that killed LAUNCHERS
    while their workers reparented and kept three cores pinned for an hour — and then
    reported `SIGTERM sent to N` and exited. **`SIGTERM sent` is a fact about the SENDER.**
    It is the launcher-vs-worker split one layer up: the thing that HOLDS the outcome (the
    process tree) and the thing that DID the work (the `os.kill` loop) are different
    objects, and the killer was instrumented only on itself. Incident 2 is precisely what
    a sender-side report cannot see, because the signal was delivered successfully to a
    process that was not the one burning the core.

    ⚑⚑⚑ AND THE HONEST OUTPUT IS AN AMBIGUITY, NOT A VERDICT — WHICH IS WHY THE VERDICT
    SET HAS FOUR MEMBERS. A re-read that finds a pid absent CANNOT distinguish:

      * the process was reaped (what the killer wanted), from
      * the process exited on its own between the two samples, from
      * the pid was never really in the target subtree — the `before` sample was already
        stale when it was taken, since a /proc scan is a SAMPLE and the tree moves under
        it by construction.

    No predicate available here separates those, and `absent` therefore means EXACTLY
    "not readable at /proc/<pid> in the after-sample" — nothing about causation. This
    function names that rather than resolving it silently, because a killer reporting
    "reaped: 12" asserts a cause it did not measure. `census-green-is-a-fact-about-the-
    census`, in the one place where the census is also the actor.

    ⚑⚑ `reparented` IS THE INCIDENT-2 SHAPE, AND IT IS THE ROW THAT MATTERS. A target
    still alive whose ppid CHANGED between the samples has outlived its parent during the
    sweep: the kill reached a layer above it and handed it to a reaper, which is the exact
    event that made three processes invisible to three `pkill` passes. It is reported
    apart from `survived` (still alive, same parent — SIGTERM queued and not yet acted on,
    or ignored) because the two need different next actions: `survived` usually wants
    another moment or a SIGKILL, while `reparented` means the sweep's own tree walk is now
    WRONG and a second `--kill` pass is the honest response.

    ⚑ `new-child` IS THE POPULATION THE TARGET LIST COULD NOT CONTAIN. A process that
    appears in `after` under a target's pid, and was not in `before`, was forked DURING
    the sweep — the leaves-first walk cannot bound a tree that is still growing. Reported
    because a silent omission here reads as a complete sweep, and it is the direct
    descendant of incident 3: fan-out width is not bounded by anything this tool controls.
    """
    seen_before = {p.pid: p for p in before}
    seen_after = {p.pid: p for p in after}
    out = []
    tset = set(targets)
    for pid in targets:
        q = seen_after.get(pid)
        if q is None:
            out.append((pid, "absent",
                        "not readable in the after-sample — reaped, self-exited, or never "
                        "really in the subtree (the before-sample is a SAMPLE). NOT a "
                        "measurement of cause."))
            continue
        was = seen_before.get(pid)
        if was is not None and q.ppid != was.ppid:
            out.append((pid, "reparented",
                        "ALIVE, ppid %d -> %d — outlived its parent during the sweep. This "
                        "is the incident-2 shape: the walk that produced the target list "
                        "is now stale. Re-run --kill." % (was.ppid, q.ppid)))
        else:
            out.append((pid, "survived",
                        "ALIVE, same parent (%d), state %s — SIGTERM queued and not yet "
                        "acted on, or ignored." % (q.ppid, q.state)))
    # ⚑ FORKED DURING THE SWEEP — see `new-child` above. Keyed on a parent that WAS a
    # target, since a child of a target is what the sweep was supposed to have covered.
    for pid, q in sorted(seen_after.items()):
        if pid in seen_before or pid in tset:
            continue
        if q.ppid in tset:
            out.append((pid, "new-child",
                        "forked from target %d DURING the sweep — the leaves-first walk "
                        "cannot bound a tree that is still growing." % q.ppid))
    return out


def tree(procs=None, exclude=None):
    """{launcher_pid: [Proc]} — substrate work grouped by PARENT.

    ⚑ FAN-OUT WIDTH IS THE FACT INCIDENT 3 NEEDED AND A FLAT COUNT DESTROYS IT. "40
    processes" is compatible with 40 independent launches (nothing wrong) and with ONE
    correct pass forking 40 workers (the actual event, and the one where killing the
    parent orphans all 40). A total cannot tell those apart; the grouping is the answer.
    """
    out = {}
    for p in substrate_procs(procs, exclude):
        out.setdefault(p.ppid, []).append(p)
    return out


def leases():
    """[(lease_id, mb, pid, label)] from `membudget status`.

    ⚑ THE LEDGER IS `scripts/membudget`'s AND IS NOT REIMPLEMENTED HERE. It owns the
    lease file's format, its GC and its locking; a second reader would be a second
    authority over one fact, which is the `agda_files()`-in-four-bodies shape. This
    parses the tool's own reported output and cross-references pids — nothing more.
    """
    import subprocess
    try:
        r = subprocess.run([os.path.join(REPO, "scripts", "membudget"), "status"],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    out = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line.startswith("["):
            continue
        try:
            lid = line[1:line.index("]")]
            rest = line[line.index("]") + 1:].split()
            mb = int(rest[0].rstrip("MB"))
            pid = int(rest[1].split("=")[1].split(":")[0])
            label = rest[-1]
        except (ValueError, IndexError):
            continue
        out.append((lid, mb, pid, label))
    return out


#: ⚑⚑⚑ THE INVARIANCE LEGEND — Ⓝ26, AND IT IS PRINTED BECAUSE THE PREMISE IT RETIRES WAS
#: HELD FOR SIX ROUNDS. Operator, 2026-08-25: *"The box will never be quiet. You cannot
#: measure a gate in wall time, only cputime."* Every timing figure this session was
#: labelled "a lower bound due to contention" and set aside pending a quiet box that will
#: never come — while the CPU column beside it was already the answer. Contention changes
#: how long a thing TAKES; it does not change how much work it DID.
#:
#: ⚑⚑ AND THE TWO COLUMNS ARE NOT REDUNDANT, WHICH IS WHY NEITHER IS DROPPED. They answer
#: different questions and only one survives co-tenancy:
#:   cpu      WHAT DID THIS COST. Invariant under load. The number to compare across runs.
#:   elapsed  DID THIS WEDGE. NOT invariant — but it is the ONLY column that can answer
#:            it, because a hung process consumes no CPU while its elapsed climbs.
#:   %        THE DISCRIMINATOR BETWEEN THEM (cpu/elapsed). High-and-steady = progressing;
#:            near-zero with climbing elapsed = blocked or wedged.
#:
#: ⚑⚑⚑ AND THE FLOOR, MEASURED THE HARD WAY THIS SESSION: **CPU% CANNOT DISTINGUISH
#: PRODUCTIVE WORK FROM A TIGHT SPIN.** An infinite loop reads 94% exactly like a correct
#: scan does. A 2061-second run was killed on precisely that gap — the reasoning *"if it's
#: not emitting progress, kill it, because we can't tell if it's hung or not"* was CORRECT,
#: and no column here could have answered it. Only per-unit progress output can
#: (`check_clause_audit --progress`). So: % separates BLOCKED from RUNNING, and says
#: nothing whatever about whether the running is going anywhere.
_INVARIANCE_LEGEND = (
    "  ⚑ cpu = WORK DONE, invariant under co-tenancy — compare runs on THIS.\n"
    "    elapsed = wall, NOT invariant (this box is never quiet), but the only column\n"
    "    that can show a WEDGE: a hung process burns 0 cpu while elapsed climbs.\n"
    # ⚑ A LITERAL `%`, NOT `%%` — this constant is PRINTED, never interpolated, so the
    # doubled form leaked `%%` into the output on its first run. A legend that misrenders
    # the very symbol it is explaining is worse than none.
    "    % = cpu/elapsed, the discriminator: high+steady = running, ~0+climbing = blocked.\n"
    "    ⚑ it CANNOT tell productive work from a tight spin — a spin reads ~100% too.\n"
    "      only per-unit progress output can; a 2061s run was killed on exactly that gap.")


def _fmt(p, subtree=None):
    """One process row. ⚑ `subtree` is the SUBTREE cpu when the caller has computed it —
    see `_STCOL`. A launcher's own cpu is ~0 by construction, so self-cpu alone is the
    blindness this file's header records twice."""
    st = "" if subtree is None else "  subtree %8.1fs" % subtree
    return ("  pid %-8d ppid %-8d %s  cpu %8.1fs  elapsed %8.1fs  %5.0f%%%s  %s"
            % (p.pid, p.ppid, p.state, p.cpu_s, p.elapsed_s, 100 * p.pcpu, st,
               p.cmd[:90]))


def main(argv):
    # ⚑ `--abandoned` IS ALREADY IN `MODES` AS A MODE, so it needs no second listing here
    # — but `--dry-run`/`--apply` are `--kill`'s opts and are modes nowhere.
    known = tuple(MODES) + ("--dry-run", "--apply")
    # ⚑⚑ `mutates` IS COMPUTED OFF THE ROSTER, NOT SPELLED AGAIN. My first cut wrote a
    # ternary `… mutates=True if "--kill" in argv else …`, which was wrong twice over:
    # it restated in the dispatch a fact `Mode.writes` already declares (two spellings
    # of one fact, free to drift), and `branch_bounds` located THAT line as `--kill`'s
    # branch — so the real branch, with its `--apply` guard, was never read and the gate
    # reported a correctly-guarded mutator as a silent-default writer. The declaration
    # is the authority; ask it.
    mutates = any(MODES[f].mutates for f in MODES if f in argv)
    rc = ratchet.check_argv(argv, known, "procstruct", mutates=mutates)
    if rc is not None:
        return rc

    if "--selftest" in argv:
        return _selftest()

    procs, unreadable = all_procs()
    ex = _excluded_pids()

    if "--running" in argv:
        rows = substrate_procs(procs, ex)
        print("substrate work running: %d of %d process(es) on this box" % (len(rows), len(procs)))
        for p in rows:
            # ⚑ Ⓝ27: THE SUBTREE COST IS SHOWN HERE TOO, and its absence was a real
            # blindness rather than a missing nicety. The orphan reaped this session
            # presented as `run_selftests` at 0.4s CPU — while its two children burned
            # 3720s and 3664s beneath it. A reader scanning `--running` by self-cpu sorts
            # that launcher to the BOTTOM. Only the three orphan predicates computed this;
            # the two modes a reader reaches for FIRST did not.
            print(_fmt(p, subtree_cpu(p.pid, procs)))
        _report_skipped(unreadable)
        print(_INVARIANCE_LEGEND)
        # ⚑ THE EXCLUSION IS REPORTED, so a reader can see the census did not count
        # itself rather than trusting that it did not. The 46-vs-40 read was invisible.
        print("  (excluded %d pid(s): self and its ancestors — see _excluded_pids)" % len(ex))
        return 0

    if "--orphans" in argv:
        rows = orphans(procs, ex)
        # ⚑ THE HEADER NAMES THE REAPERS IT USED, not a literal "ppid 1" — the reader
        # must be able to see WHICH adopting set produced this verdict, because the
        # wrong set is how this census read zero over three live orphans.
        print("ORPHANED substrate work: %d (parent in %s, subtree cpu >= %.0fs)"
              % (len(rows), sorted(reapers()), IDLE_CPU_S))
        for p, cpu in rows:
            print(_fmt(p))
            print("        subtree cpu %.1fs across %d descendant(s)"
                  % (cpu, sum(1 for q in procs if q.ppid == p.pid)))
        if not rows:
            # ⚑ A ZERO NAMES ITS OWN BOUNDARY. "no orphans above the floor" and "no
            # orphans" are different facts, and only one of them is what was measured.
            low = [p for p in substrate_procs(procs, ex) if p.orphaned]
            print("  none above the floor. %d orphan(s) below it (idle/detached, not "
                  "runaways)." % len(low))
        _report_skipped(unreadable)
        print(_INVARIANCE_LEGEND)
        return 0

    if "--abandoned" in argv and "--kill" not in argv:
        # ⚑ `and "--kill" not in argv` — `--abandoned` is BOTH a mode and `--kill`'s opt,
        # and without this guard the widened kill would be swallowed by the read mode and
        # silently do nothing. A killer that exits 0 having killed nothing, because
        # another branch claimed its flag, is the worst possible failure here.
        rows = abandoned(procs, ex)
        print("ABANDONED substrate work: %d (parent in %s, elapsed >= %.0fs, NO cpu floor)"
              % (len(rows), sorted(reapers()), ABANDONED_AGE_S))
        for p, cpu in rows:
            print(_fmt(p))
            # ⚑ THE COST IS A COLUMN, NOT A FILTER — and naming the quiet ones as quiet is
            # the whole finding: `--orphans` calls this row "below the floor", which is
            # true about its CPU and false about its status.
            print("        subtree cpu %.1fs across %d descendant(s)%s"
                  % (cpu, sum(1 for q in procs if q.ppid == p.pid),
                     "" if cpu >= IDLE_CPU_S
                     else "  ⚑ QUIET — invisible to --orphans, still holds its lease"))
        if not rows:
            # ⚑ A ZERO NAMES ITS OWN BOUNDARY, same rule as `--orphans`. Here the boundary
            # is AGE, not cost, so the residue it excluded is a different population and
            # must be counted separately rather than reusing the other mode's sentence.
            young = [p for p in substrate_procs(procs, ex)
                     if p.orphaned and p.elapsed_s < ABANDONED_AGE_S]
            print("  none. %d orphan(s) younger than the age floor (possibly still "
                  "daemonising, not yet abandoned)." % len(young))
        _report_skipped(unreadable)
        return 0

    if "--stranded" in argv:
        rows = stranded(procs, ex)
        n_rep = sum(1 for _p, _c, g, _w in rows if g == "reparented")
        n_str = sum(1 for _p, _c, g, _w in rows if g == "harness-rooted")
        # ⚑ THE TWO GROUNDS ARE COUNTED APART IN THE HEADER, not summed — they are not
        # the same STRENGTH of claim, so a single total would overstate the weaker half.
        print("EDGE census: %d row(s) — %d REPARENTED (unowned: a conclusion), "
              "%d HARNESS-ROOTED (a CANDIDACY, not\n  a verdict: live and stale chains "
              "are identical from /proc). elapsed >= %.0fs, NO cpu floor."
              % (len(rows), n_rep, n_str, ABANDONED_AGE_S))
        for p, cpu, ground, why in rows:
            print(_fmt(p))
            print("        %-11s %s" % (ground.upper(), why))
            print("        subtree cpu %.1fs across %d descendant(s)%s"
                  % (cpu, sum(1 for q in procs if q.ppid == p.pid),
                     "" if cpu >= IDLE_CPU_S
                     else "  ⚑ QUIET — invisible to --orphans, still holds its lease"))
        if not rows:
            young = [p for p in substrate_procs(procs, ex)
                     if p.elapsed_s < ABANDONED_AGE_S]
            print("  none. %d process(es) younger than the age floor." % len(young))
        _report_skipped(unreadable)
        # ⚑⚑⚑ THE FLOOR THE WALK CANNOT CLOSE, PRINTED EVERY TIME — the same discipline
        # `--kill`'s `absent` verdict follows, and for the same reason: this is the
        # majority-quiet mode, so a caveat shown only on interesting runs would leave the
        # quiet runs as the misleading ones. Four things this cannot distinguish:
        print("  ⚑ FLOOR — what this walk CANNOT see, none of it closable here:")
        print("    1. AN ANCESTOR THAT WAS ITSELF REPARENTED looks identical to a "
              "legitimate daemon.\n       The chain records who the parent IS, never who "
              "it WAS.")
        print("    2. A PID THAT EXITS MID-WALK truncates the chain, and a truncated "
              "chain is\n       indistinguishable from one that legitimately reached the "
              "root. /proc is a SAMPLE.")
        print("    3. THE HARNESS MARKER IS A STRING TEST (see HARNESS_SHELL_MARKS) — "
              "gate-F8. A shell\n       the harness spells differently is invisible; "
              "there is no structural marker for it.")
        print("    4. ⚑⚑ TASK STATE IS NOT IN /proc AT ALL, AND THIS IS THE BIG ONE — "
              "MEASURED: the stale\n       runaway 902955 and a LIVE run_selftests tree "
              "produced IDENTICAL chains, both burning\n       CPU. A first cut called "
              "both 'stranded' and would have reported a sibling's work\n       as "
              "abandoned. `harness-rooted` is TRUE of every task-launched process here, "
              "live or dead.")
        print("  ⚑ so HARNESS-ROOTED means REQUESTER NOT OBSERVABLE FROM HERE — it "
              "NARROWS the field for an\n    operator who knows which tasks are running; "
              "it never decides. Only REPARENTED is a verdict.")
        print("  ⚑ a REPORT, not a kill list: --kill's population is deliberately "
              "UNCHANGED (still burning\n    orphans, or --abandoned). Nothing may be "
              "reaped on the harness-rooted ground alone.")
        return 0

    if "--chain" in argv:
        # ⚑ THE AUDIT MODE, AND IT EXISTS BECAUSE THE VERDICT IS AN EDGE. A node verdict
        # can be spot-checked by looking at the node; a PATH verdict cannot be checked
        # without the path. Shipping the classifier without a way to print its evidence
        # would be asking a reader to trust exactly the reasoning that was wrong before.
        i = argv.index("--chain")
        if i + 1 >= len(argv) or not argv[i + 1].isdigit():
            print("usage: procstruct.py --chain <PID>")
            return 2
        target = int(argv[i + 1])
        ch = chain(target)
        if not ch:
            print("pid %d: no chain — the pid is gone or unreadable (a /proc read is a "
                  "SAMPLE; this is not proof it never existed)." % target)
            return 0
        print("ppid chain for %d (leaf first, bounded 64 hops by ratchet.ancestry):" % target)
        for pid, cmd in ch:
            tag = ""
            if pid in reapers():
                tag = "  ⚑ REAPER"
            elif any(m in cmd for m in HARNESS_SHELL_MARKS):
                tag = "  ⚑ HARNESS SHELL"
            print("  pid %-8d %s%s" % (pid, cmd[:80] or "<no cmdline>", tag))
        p = read_proc(target)
        if p:
            ground, _ch, why = strand_ground(p, None)
            print("  verdict: %s — %s" % (ground or "not abandoned", why))
        return 0

    if "--tree" in argv:
        groups = tree(procs, ex)
        print("substrate fan-out: %d launcher(s), %d worker(s)"
              % (len(groups), sum(len(v) for v in groups.values())))
        for ppid, kids in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            par = read_proc(ppid)
            tag = "init" if ppid == 1 else (par.cmd[:70] if par else "<gone>")
            # ⚑ ppid 1 IS NOT A LAUNCHER, it is the ABSENCE of one — naming it as a
            # parent would read as 'init forked these', inverting the finding.
            print("  ppid %-8d x%-3d  %s" % (ppid, len(kids), tag))
            for p in kids:
                print("  " + _fmt(p))
        _report_skipped(unreadable)
        return 0

    if "--leases" in argv:
        ls = leases()
        if ls is None:
            print(ratchet.withheld("procstruct --leases",
                                   "which live processes hold a membudget lease",
                                   "`membudget status` did not return successfully",
                                   "the ledger tool is the authority and it did not answer"))
            return 1
        live = {p.pid: p for p in procs}
        print("membudget leases: %d" % len(ls))
        for lid, mb, pid, label in ls:
            p = live.get(pid)
            if p is None:
                # ⚑ A LEASE WHOSE OWNER IS GONE is the ledger's own GC population — a
                # fact worth printing, not an error: it is the trace of the launcher-kill.
                print("  [%s] %4dMB pid %-8d %-30s ⚑ OWNER GONE (leaked lease)"
                      % (lid, mb, pid, label))
            else:
                print("  [%s] %4dMB pid %-8d %-30s %s cpu %.1fs%s"
                      % (lid, mb, pid, label, p.state, p.cpu_s,
                         "  ⚑ ORPHANED" if p.orphaned else ""))
        _report_skipped(unreadable)
        return 0

    if "--cost" in argv:
        i = argv.index("--cost")
        n = 20
        if i + 1 < len(argv) and argv[i + 1].isdigit():
            n = int(argv[i + 1])
        # ⚑⚑ RANKED BY SUBTREE CPU, NOT SELF — Ⓝ27, and the old ranking answered the
        # wrong question in the one case that matters. `substrate_procs` sorts by SELF
        # cpu, so the orphan reaped this session (`run_selftests`, 0.4s of its own,
        # 7402s beneath it) sorted to the BOTTOM of "most expensive". A cost mode whose
        # ranking hides the most expensive thing on the box is the launcher-vs-worker
        # blindness this file's header records, in the mode named for cost.
        #
        # ⚑ SELF CPU IS STILL PRINTED beside it — the two together are what distinguish
        # a hot leaf (self ≈ subtree) from a launcher over hot children (self ≈ 0).
        _all = substrate_procs(procs, ex)
        _ranked = sorted(((p, subtree_cpu(p.pid, procs)) for p in _all),
                         key=lambda pc: -pc[1])
        print("most expensive substrate work (of %d), by SUBTREE CPU seconds:" % len(_all))
        for p, st in _ranked[:n]:
            print(_fmt(p, st))
        _report_skipped(unreadable)
        print(_INVARIANCE_LEGEND)
        return 0

    if "--reapers" in argv:
        # ⚑ THE MODE EXISTS BECAUSE THE ANSWER SURPRISED ITS OWN AUTHOR. Printing the
        # adopting set is what turns "--orphans found nothing" from a verdict into a
        # checkable claim: if this set is wrong, the orphan census is silently zero.
        print("pids that ADOPT orphans in this session:")
        for pid in sorted(reapers()):
            p = read_proc(pid)
            print("  pid %-8d %s" % (pid, p.cmd[:90] if p and p.cmd else "<init>"))
        print("  ⚑ orphans here reparent to the SESSION MANAGER, not pid 1 — a "
              "`ppid == 1` census reads zero over a tree full of them.")
        return 0

    if "--kill" in argv:
        # ⚑⚑⚑ THE DEFAULT POPULATION IS UNCHANGED, AND THAT IS THE POINT OF Ⓟ8's SECOND
        # HALF. Adding `abandoned()` to the killer's default set would mean this command
        # silently starts reaping processes it did not reap yesterday — including the
        # blocked-but-legitimate. Under-reaping leaves EVIDENCE (the process is still
        # there to be found); over-reaping destroys it. So the widening is a flag the
        # caller types, and the header says which population it is about to act on.
        wide = "--abandoned" in argv
        rows = abandoned(procs, ex) if wide else orphans(procs, ex)
        print("  population: %s"
              % ("ABANDONED (orphaned, elapsed >= %.0fs, NO cpu floor) — WIDENED by "
                 "--abandoned" % ABANDONED_AGE_S if wide else
                 "burning orphans (subtree cpu >= %.0fs) — the DEFAULT. Pass --abandoned "
                 "to include the quiet ones." % IDLE_CPU_S))
        # ⚑⚑⚑ THE TARGET IS THE ORPHAN WORKER ITSELF, AND THAT OMISSION *IS* INCIDENT 2.
        # Three `pkill -f "membudget run 192 selftest:"` passes killed LAUNCHERS; the
        # children reparented to init and kept three cores pinned for over an hour,
        # invisible to the pattern because their own cmdline never contained it. A kill
        # mode that targets launchers reproduces the incident it exists to clean up.
        # An orphan HAS no launcher — ppid is 1 — so there is nothing else to target.
        # ⚑⚑⚑ THE WHOLE SUBTREE, LEAVES FIRST — AND ANYTHING ELSE REPRODUCES INCIDENT 2.
        # An orphaned launcher's worker is a SEPARATE process whose own cmdline never
        # names the launcher. Killing only the root hands the worker to the reaper and it
        # keeps its core; that is precisely how three processes survived three `pkill`
        # passes and pinned three cores for an hour. Leaves first so no intermediate is
        # orphaned even momentarily during the sweep.
        targets = []
        for p, _cpu in rows:
            order = []
            stack, seen = [p.pid], set()
            while stack:
                pid = stack.pop()
                if pid in seen:
                    continue
                seen.add(pid)
                order.append(pid)
                stack.extend(q.pid for q in procs if q.ppid == pid)
            targets.extend(reversed(order))          # deepest first
        live = {q.pid: q for q in procs}
        print("orphan subtrees to SIGTERM: %d root(s), %d process(es) total"
              % (len(rows), len(targets)))
        for pid in targets:
            q = live.get(pid)
            if q:
                print(_fmt(q))
        _report_skipped(unreadable)
        if "--apply" not in argv:
            print("  (dry run — pass --apply to send SIGTERM, leaves first)")
            return 0
        killed, failed = 0, 0
        for pid in targets:
            try:
                os.kill(pid, 15)
                killed += 1
            except OSError:
                # ⚑ ALREADY GONE IS NOT A FAILURE TO REPORT AS ONE — the process may have
                # exited between the scan and the signal. Counted apart so a reader can
                # tell 'nothing to do' from 'not permitted'.
                failed += 1
        # ⚑ AND THIS LINE IS A FACT ABOUT THE SENDER, WHICH IS WHY IT IS NO LONGER THE
        # LAST ONE PRINTED — Ⓝ9. See `kill_census`.
        print("  SIGTERM sent to %d; %d already gone or not permitted" % (killed, failed))
        import time as _time
        _time.sleep(KILL_SETTLE_S)
        after, unreadable2 = all_procs()
        rows = kill_census(targets, procs, after)
        counts = {v: 0 for v in KILL_VERDICTS}
        for _pid, v, _n in rows:
            counts[v] = counts.get(v, 0) + 1
        print("  post-kill descendant census (re-read after %.1fs): %s"
              % (KILL_SETTLE_S,
                 ", ".join("%s %d" % (v, counts[v]) for v in KILL_VERDICTS)))
        for pid, v, note in rows:
            if v == "absent":
                continue
            print("    pid %-8d %-11s %s" % (pid, v, note))
        # ⚑⚑ THE AMBIGUITY IS PRINTED EVERY TIME, NOT ONLY WHEN IT BITES. `absent` is the
        # majority verdict on a successful sweep, and a reader who sees "absent 12" with no
        # caveat will read it as "reaped 12" — a cause this census did not measure and
        # cannot. Stating it only on the interesting runs would make the quiet runs the
        # ones that mislead, which is the wrong way round.
        print("    ⚑ `absent` means NOT READABLE in the after-sample — reaped, "
              "self-exited, or never in the subtree (the pre-kill walk is a SAMPLE).")
        print("    ⚑ it does NOT distinguish reaped from reparented-away-from-the-tree "
              "I was watching; no predicate here can.")
        _report_skipped(unreadable2, "process entries in the post-kill re-read")
        # ⚑ A NONZERO EXIT WHEN SOMETHING SURVIVED — the sweep did not do what it was asked
        # and a caller scripting this must be able to tell. `absent`/`new-child` do not
        # bear on that: the first is the intended outcome and the second is not a failure
        # of THIS sweep, only a fact about a tree that kept growing.
        return 1 if (counts["survived"] or counts["reparented"]) else 0

    print(__doc__)
    return 0


def _selftest():
    """The guarded cases.

    ⚑⚑⚑ THE ORPHAN CASE CONSTRUCTS A REAL ORPHAN — sql-F13 IS WHY. An agent asserted a
    guard worked over a fixture whose premise was wrong and nearly banked "returned True"
    as evidence. A fabricated `/proc` tree here would test the MATCHER and say nothing
    about the INSTRUMENT: whether `ppid` really becomes 1, whether the reparent is visible
    to this reader, whether the timing is racy. So: fork a grandchild, kill the middle
    process, and watch the kernel reparent it.
    """
    import subprocess
    import time
    fails = []

    def check(what, got, want):
        if got != want:
            fails.append("  FAIL %s\n       got %r want %r" % (what, got, want))

    # ── the /proc reader ────────────────────────────────────────────────────────
    me = read_proc(os.getpid())
    check("self is readable", me is not None, True)
    check("self's ppid matches os.getppid()", me.ppid, os.getppid())
    check("self is running", me.state in ("R", "S"), True)
    check("a dead/absent pid reads None, never raises", read_proc(2 ** 22 - 1), None)
    # ⚑ THE COMM-FIELD RULE: a name with a space and a paren shifts every positional
    # field, and `stat.split()[3]` then returns a state letter as a pid. ratchet.ancestry
    # records the same rule; this pins that THIS reader honours it too.
    _fake = "999 (my prog (x)) S 1234 1 1 0 -1 0 0 0 0 0 " + " ".join(["0"] * 12)
    _rest = _fake[_fake.rindex(")") + 1:].split()
    check("ppid is read after the LAST paren", int(_rest[1]), 1234)

    # ── the self-match exclusion (gate-F8) ──────────────────────────────────────
    ex = _excluded_pids()
    check("self is excluded", os.getpid() in ex, True)
    check("the launching parent is excluded", os.getppid() in ex, True)
    # ⚑ THE EXCLUSION IS BY PID, NOT BY STRING — so a spelling change cannot silently
    # disarm it, which is precisely how the substring form failed one argument apart.
    check("the exclusion set holds pids, not strings",
          all(isinstance(p, int) for p in ex), True)

    # ⚑⚑ THE 46-vs-40 CASE, EXECUTABLE. A process whose cmdline QUOTES the query (a
    # `bash -c` wrapper) must not be counted. Here the running interpreter's own argv
    # contains "procstruct.py", so a substring census over the whole tree would count
    # self and its shell; the pid-set census must not.
    _all, _ = all_procs()
    _naive = [p for p in _all if "procstruct" in p.cmd]
    _honest = [p for p in _naive if p.pid not in ex]
    check("a naive cmdline match DOES count self (the defect, reproduced)",
          any(p.pid == os.getpid() for p in _naive), True)
    check("...and the pid-set exclusion removes it",
          any(p.pid == os.getpid() for p in _honest), False)

    # ── scoping: a path under the repo, never a word ────────────────────────────
    check("a repo path is substrate's work",
          is_substrate(Proc(1, 1, "R", "python3 %s/scratch/x.py" % REPO, 1.0, 1.0)), True)
    # ⚑ THE WORD-MATCH TRAP: `paperkit/discriminate.py` from a bazel execroot was live on
    # the box during this build and a token census would have claimed it.
    check("a mere mention of the word is NOT",
          is_substrate(Proc(1, 1, "R", "vim notes-about-substrate.md", 1.0, 1.0)), False)
    check("an unrelated checkout is NOT",
          is_substrate(Proc(1, 1, "R", "/execroot/_main/paperkit/discriminate.py", 1.0, 1.0)),
          False)

    # ── cost ────────────────────────────────────────────────────────────────────
    check("a runaway reads ~100%", round(Proc(1, 1, "R", "", 60.0, 61.0).pcpu, 1), 1.0)
    check("an idle process reads ~0%", round(Proc(1, 1, "S", "", 0.5, 600.0).pcpu, 2), 0.0)
    # ⚑ A ZERO-ELAPSED PROCESS MUST NOT DIVIDE BY ZERO — a process sampled in the same
    # tick it started, which a census over a busy tree will hit.
    check("zero elapsed does not raise", Proc(1, 1, "R", "", 0.0, 0.0).pcpu, 0.0)

    # ── subtree cost: the launcher-with-a-hot-worker shape ──────────────────────
    # ⚑⚑ THE LIVE DEFECT, PINNED. Three orphaned `membudget run` launchers each had 0.0
    # CPU of their own while their children burned 461 and 398 CPU-seconds at 90% of a
    # core. A self-CPU floor reported ZERO orphans over them. The wrapper is always ~0
    # by construction, so the cost of an orphan is only ever its SUBTREE's.
    _fam = [Proc(100, 1, "S", "%s/scripts/membudget run" % REPO, 0.0, 500.0),
            Proc(101, 100, "S", "/usr/bin/time -v", 0.0, 500.0),
            Proc(102, 101, "R", "%s/scratch/hot.py" % REPO, 461.0, 500.0)]
    check("a wrapper's OWN cpu is ~zero (why the self floor failed)",
          _fam[0].cpu_s < 1.0, True)
    check("...but its subtree's is not", subtree_cpu(100, _fam), 461.0)
    check("...so the orphaned launcher IS reported",
          [p.pid for p, _c in orphans(_fam, exclude=set())], [100])
    # ⚑ AND THE FLOOR STILL BITES ON A GENUINELY IDLE ORPHAN — a census that reports
    # every detached shell is as useless as one that reports none.
    _idle = [Proc(200, 1, "S", "%s/scratch/idle.py" % REPO, 0.1, 900.0)]
    check("a genuinely idle orphan stays below the floor",
          orphans(_idle, exclude=set()), [])

    # ── Ⓟ8: the QUIET orphan, which the cost floor is structurally blind to ─────
    # ⚑⚑ THE MEASURED POPULATION, PINNED. After `--kill --apply` cleared the burning
    # orphans, six processes remained: `query_registry` and `reconstruct` at 0.8s and
    # 0.4s of CPU across 163 SECONDS elapsed. Orphaned, holding membudget leases, and
    # reported by `--orphans` as "below the floor" — true about their CPU, false about
    # their status. These two cases are the same shape at the same magnitudes.
    _quiet = [Proc(300, 1, "S", "%s/jea/metalanguage/query_registry.py" % REPO, 0.8, 163.0),
              Proc(301, 1, "S", "%s/jea/metalanguage/reconstruct.py" % REPO, 0.4, 163.0)]
    check("the CPU floor hides the quiet orphan (the defect, reproduced)",
          orphans(_quiet, exclude=set()), [])
    check("...and `abandoned` sees both of them",
          sorted(p.pid for p, _c in abandoned(_quiet, exclude=set())), [300, 301])
    # ⚑ THE AGE FLOOR IS WHAT REPLACES THE COST FLOOR, and it must actually bite —
    # otherwise `--abandoned` reports every double-forked daemon mid-setup and the mode
    # is noise. A CPU floor would let this one through too (it burns nothing), which is
    # precisely why the two floors are on different axes rather than one being lower.
    _new = [Proc(302, 1, "S", "%s/scratch/justforked.py" % REPO, 0.0, 2.0)]
    check("a just-detached process is NEW, not abandoned",
          abandoned(_new, exclude=set()), [])
    # ⚑ AND A BURNING ORPHAN IS IN *BOTH* POPULATIONS — `abandoned` widens, it does not
    # substitute. A predicate that traded one blind spot for another would be no gain.
    check("the burning orphan is in the wider population too",
          [p.pid for p, _c in abandoned(_fam, exclude=set())], [100])
    # ⚑ AGE IS READ OFF THE ROOT, NOT THE YOUNGEST DESCENDANT. A launcher orphaned an
    # hour ago that forked a child a second back is still abandoned; reading the subtree
    # would let a busy orphan reset its own clock forever and never qualify.
    _fresh_kid = [Proc(400, 1, "S", "%s/scripts/membudget run" % REPO, 0.0, 900.0),
                  Proc(401, 400, "R", "%s/scratch/x.py" % REPO, 0.1, 1.0)]
    check("an old orphan with a fresh child is still abandoned",
          [p.pid for p, _c in abandoned(_fresh_kid, exclude=set())], [400])

    # ── ⚑⚑⚑ A CONSTRUCTED ORPHAN — not a fabricated /proc tree (sql-F13) ────────
    # A middle process forks a grandchild that sleeps, then EXITS. The kernel reparents
    # the grandchild; `--orphans` must see ppid become 1. This tests the reparent itself.
    # ⚑ THE GRANDCHILD CLOSES ITS INHERITED stdout/stderr, AND OMITTING THAT HUNG THE
    # SUITE FOR THE FULL TIMEOUT. `capture_output` gives the middle process a PIPE; the
    # fork duplicates the write end, so `communicate()` waits for EOF that the sleeping
    # grandchild holds open — 30s, read as a broken orphan test rather than a fixture
    # bug. The defect was in how the specimen was BUILT, which is exactly the class a
    # fabricated /proc tree could never have surfaced.
    _mk = ("import os, sys, time\n"
           "pid = os.fork()\n"
           "if pid == 0:\n"
           "    os.close(1); os.close(2)\n"
           "    time.sleep(30)\n"          # the grandchild: outlives its parent
           "    os._exit(0)\n"
           "sys.stdout.write(str(pid)); sys.stdout.flush()\n"
           "os._exit(0)\n")                # the middle process dies at once
    # ⚑⚑ THE SPECIMEN IS RUN FROM A REAL FILE UNDER THE REPO, NOT `python -c`, AND THAT
    # IS NOT COSMETIC. `is_substrate` scopes on a repo PATH in the cmdline; a `-c` child's
    # cmdline is `python3 -c import os...`, which the predicate correctly refuses. So the
    # `-c` specimen could only ever be tested against `orphaned` in isolation — the
    # PIPELINE (scope → exclude → age → cost) was never driven end-to-end on a live
    # process, and Ⓟ8's whole finding is that the pipeline, not the predicate, was wrong.
    # Writing the file makes the orphan substrate's own work in the same way a real one is.
    import tempfile
    _fd, _spec = tempfile.mkstemp(suffix="_procstruct_orphan_spec.py",
                                  dir=os.path.join(REPO, "scratch"))
    with os.fdopen(_fd, "w") as _fh:
        _fh.write(_mk)
    try:
        _r = subprocess.run([sys.executable, _spec], capture_output=True, text=True,
                            timeout=30)
        gpid = int(_r.stdout.strip())
    finally:
        # ⚑ UNLINKED IMMEDIATELY — the cmdline is already captured in the kernel, so the
        # scoping still works, and a suite that leaves files in `scratch/` on every run
        # would grow the tree it is measuring.
        try:
            os.unlink(_spec)
        except OSError:
            pass
    # ⚑ THE REPARENT IS NOT INSTANT — poll rather than sleeping a guessed interval. A
    # fixed sleep is a race that passes on a quiet box and fails under the load this
    # tool exists to measure, which is the one condition it must work in.
    reparented = False
    for _ in range(100):
        gp = read_proc(gpid)
        if gp is None:
            break
        # ⚑ POLL ON THE REAPER SET, NOT ON `ppid == 1` — the same defect one layer down.
        # This loop kept its literal 1 after the discriminator was corrected, so the
        # flag read False while the three cases below it (which DO use the set) all
        # passed. A stale second spelling of one fact, in the suite that found the first.
        if gp.ppid in reapers():
            reparented = True
            break
        time.sleep(0.05)
    check("a CONSTRUCTED orphan really reparents to a reaper", reparented, True)
    gp = read_proc(gpid)
    # ⚑⚑ THE CASE THAT FALSIFIED MY OWN FIRST DISCRIMINATOR. This asserted `ppid == 1`
    # and MEASURED 1369 — `systemd --user`, a child subreaper. A fabricated /proc tree
    # would have been built asserting 1 and would have passed forever.
    check("...and the reaper is NOT pid 1 on this box (a subreaper adopted it)",
          gp.ppid != 1 if gp else None, True)
    check("...and the reaper is on self's own session chain",
          gp.ppid in reapers() if gp else None, True)
    check("...and `orphaned` is True on it", gp.orphaned if gp else None, True)
    # ⚑ THE INSTRUMENT ON THE REAL SPECIMEN, not just the predicate: the orphan must
    # survive the whole substrate-scoping + exclusion pipeline, which is where a census
    # actually loses things. Scoped in by giving it a repo-path cmdline is impossible for
    # a `-c` child, so scope explicitly and assert the pipeline keeps it.
    _procs, _ = all_procs()
    _found = [p for p in _procs if p.pid == gpid and p.orphaned]
    check("...and a full /proc scan finds it as an orphan", len(_found), 1)
    # ⚑ AND IT IS NOT SILENTLY DROPPED BY THE EXCLUSION — it is neither self nor an
    # ancestor, so a census must keep it. This is the half that would have caught a
    # too-wide exclusion, the failure mode opposite to the 46-vs-40 over-count.
    check("...and the self-exclusion does not swallow it", gpid in _excluded_pids(), False)

    # ⚑⚑⚑ Ⓟ8 ON THE REAL SPECIMEN, AND THE SPECIMEN WAS ALREADY THE RIGHT KIND. The
    # constructed orphan above `time.sleep`s — it is BLOCKED, burning ~0 CPU, which is
    # exactly the quiet population `--orphans` cannot see. So the two predicates can be
    # driven against a live reparented process rather than a `Proc(...)` I typed, which
    # is the sql-F13 distinction: a fabricated tree tests the MATCHER, and what is in
    # doubt here is the INSTRUMENT — whether a blocked orphan's `/proc` cost really reads
    # near zero, whether `elapsed_s` is populated at all on a freshly reparented process.
    _gp = read_proc(gpid)
    # ⚑ THE SPECIMEN IS SUBSTRATE-SCOPED ON ITS MERITS, not by being waved through. If
    # this fails the four cases below it are vacuous — they would be testing an empty
    # population and reporting green, which is `census-green-is-a-fact-about-the-census`
    # inside the suite written against that exact error.
    check("the constructed orphan scopes as substrate's own work",
          is_substrate(_gp) if _gp else None, True)
    check("the CONSTRUCTED orphan is genuinely quiet, not burning",
          _gp.cpu_s < IDLE_CPU_S if _gp else None, True)
    # ⚑ THE COST FLOOR REJECTS IT — measured on a real process, not asserted about one.
    check("...so the cost floor would reject it as 'below the floor'",
          subtree_cpu(gpid, all_procs()[0]) < IDLE_CPU_S, True)
    # ⚑ AND THE AGE PREDICATE ACCEPTS IT once its age is the only thing asked about. It
    # is seconds old, so the live floor legitimately excludes it; drive the predicate at
    # `min_age_s=0` to test the DISCRIMINATOR rather than waiting 30 seconds in a suite.
    # ⚑ Scoped in explicitly: a `python -c` child has no repo path in its cmdline, so
    # `is_substrate` correctly refuses it and the pipeline must be entered at `abandoned`.
    _live = [p for p in all_procs()[0] if p.pid == gpid]
    check("the real orphan is visible to the abandoned predicate at age 0",
          [p.pid for p, _c in abandoned(_live, exclude=set(), min_age_s=0.0)],
          [gpid])
    # ⚑ AND IT IS EXCLUDED AT THE LIVE FLOOR — the age guard biting on a REAL process,
    # not on a fabricated elapsed_s. This is the half that proves the floor is not
    # decorative.
    check("...and excluded at the live age floor, being seconds old",
          [p.pid for p, _c in abandoned(_live, exclude=set())], [])
    os.kill(gpid, 9)

    # ── Ⓝ9: the POST-KILL descendant census ─────────────────────────────────────
    # ⚑⚑ THE KILLER REPORTED ON ITSELF. `SIGTERM sent to N` is a fact about the sender,
    # and incident 2 is precisely what a sender-side report cannot see. These cases pin
    # each verdict AND — more importantly — pin that `absent` never claims a cause.
    _before = [Proc(500, 400, "R", "%s/scratch/hot.py" % REPO, 400.0, 500.0),
               Proc(501, 400, "S", "%s/scratch/mid.py" % REPO, 1.0, 500.0),
               Proc(502, 400, "S", "%s/scratch/stub.py" % REPO, 1.0, 500.0)]
    # 500 vanished; 501 survives under the same parent; 502 reparented to a reaper.
    _after = [Proc(501, 400, "S", "%s/scratch/mid.py" % REPO, 1.0, 501.0),
              Proc(502, 1, "S", "%s/scratch/stub.py" % REPO, 1.0, 501.0)]
    _cen = {pid: (v, note) for pid, v, note in
            kill_census([500, 501, 502], _before, _after)}
    check("a target missing from the after-sample reads absent", _cen[500][0], "absent")
    # ⚑⚑⚑ THE LOAD-BEARING CASE OF THE WHOLE MODE. `absent` is the majority verdict on a
    # successful sweep, so if it is allowed to spell itself "reaped" the common run is the
    # misleading one. It must state the three causes it cannot separate.
    check("...and absent NEVER claims it was reaped",
          "reaped" in _cen[500][1] and "NOT a measurement of cause" in _cen[500][1], True)
    check("a target still alive under the same parent reads survived",
          _cen[501][0], "survived")
    # ⚑ THE INCIDENT-2 SHAPE, AS A VERDICT. A target whose ppid moved outlived its parent
    # mid-sweep, so the walk that built the target list is now wrong.
    check("a target whose ppid MOVED reads reparented, not survived",
          _cen[502][0], "reparented")
    check("...and says the target list is now stale", "stale" in _cen[502][1], True)
    # ⚑ THE TWO ARE NOT ONE VERDICT: `survived` wants another moment or a SIGKILL,
    # `reparented` wants a second --kill pass. Collapsing them loses the next action.
    check("survived and reparented are distinct verdicts",
          _cen[501][0] != _cen[502][0], True)
    # ⚑ FORKED DURING THE SWEEP — incident 3's descendant. The leaves-first walk cannot
    # bound a tree that is still growing, and omitting this reads as a complete sweep.
    _grow = _after + [Proc(503, 501, "R", "%s/scratch/fresh.py" % REPO, 0.1, 1.0)]
    _cen2 = {pid: v for pid, v, _n in kill_census([500, 501, 502], _before, _grow)}
    check("a process forked from a target DURING the sweep is reported",
          _cen2.get(503), "new-child")
    # ⚑ AND A PROCESS UNRELATED TO ANY TARGET IS NOT — a census that swept in every new
    # process on the box would manufacture findings out of ordinary activity.
    _noise = _after + [Proc(504, 999, "R", "%s/scratch/other.py" % REPO, 0.1, 1.0)]
    check("...but an unrelated new process is NOT",
          504 in {pid for pid, _v, _n in kill_census([500, 501, 502], _before, _noise)},
          False)
    # ⚑ EVERY VERDICT PRODUCED IS IN THE CLOSED SET — an unlisted verdict would be
    # invisible to the counter in the dispatch, which iterates KILL_VERDICTS.
    check("every verdict is in the declared closed set",
          {v for _p, v, _n in kill_census([500, 501, 502], _before, _grow)}
          - set(KILL_VERDICTS), set())
    # ⚑ A CLEAN SWEEP REPORTS ONLY `absent` — the discriminator must not fire on success,
    # or the nonzero exit would be permanent and unreadable.
    check("a fully-cleared sweep is all absent",
          {v for _p, v, _n in kill_census([500, 501], _before, [])}, {"absent"})

    # ⚑⚑ THE CENSUS ON A REAL PROCESS, not only on `Proc(...)` rows I typed — the sql-F13
    # distinction the orphan case above is built on. What is in doubt is whether a pid
    # really becomes unreadable promptly after a signal, which no fixture can answer.
    _sp = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    _pre = [read_proc(_sp.pid)]
    check("a live constructed process reads as present", _pre[0] is not None, True)
    _sp.kill()
    _sp.wait(timeout=10)
    _post, _ = all_procs()
    _live_cen = {pid: v for pid, v, _n in kill_census([_sp.pid], _pre, _post)}
    # ⚑ A REAPED CHILD IS `absent` — and this case is the reason the verdict is named for
    # what was OBSERVED (not readable) rather than what happened (reaped). Here it really
    # was reaped and the census still only says `absent`, which is the honest reading.
    check("a genuinely reaped process reads absent (observation, not cause)",
          _live_cen.get(_sp.pid), "absent")

    # ── incident 7: the EDGE predicate (the-fact-may-be-an-edge-not-a-property) ─
    # ⚑⚑⚑ THE DEFECT, REPRODUCED. A node predicate asks "is my parent a reaper"; this
    # process's parent is ALIVE, so both --orphans and --abandoned reported clean while it
    # burned 3224 CPU-seconds at 83% of a core for 65 minutes. The discriminator is the
    # PATH TO THE ROOT, which no per-node test can express.
    _live_parent = Proc(902932, 3216402, "S", "/bin/bash -c source "
                        "/home/x/.claude/shell-snapshots/snapshot-bash-1.sh", 0.0, 3833.0)
    _strand = Proc(902955, 902932, "R", "%s/scripts/check_clause_audit.py" % REPO,
                   3176.9, 3833.0)
    check("the runaway's parent is NOT a reaper (why the node test read clean)",
          _strand.orphaned, False)
    check("...so `orphans` misses it entirely (the defect, reproduced)",
          orphans([_strand, _live_parent], exclude=set()), [])
    check("...and so does `abandoned` — the same node test, one floor over",
          abandoned([_strand, _live_parent], exclude=set()), [])
    # ⚑ THE MARKER TEST IS A STRING TEST AND IS DECLARED AS ONE — gate-F8. Pinned here so
    # a future edit cannot quietly turn it into a claim of structural detection.
    check("the harness marker is matched on the ancestor's COMMAND TEXT",
          any(m in _live_parent.cmd for m in HARNESS_SHELL_MARKS), True)
    # ⚑⚑ THE GROUND SET IS CLOSED, AND THE SECOND MEMBER IS NAMED FOR ITS STRENGTH. It is
    # `harness-rooted`, NOT `stranded`: the chain cannot separate a live task from a dead
    # one, so the weaker word is the honest one. A rename back to a verdict-sounding
    # spelling must fail HERE rather than in an operator's kill decision.
    check("the grounds are a closed pair", ABANDON_GROUNDS,
          ("reparented", "harness-rooted"))
    check("...and the chain-based ground is NOT named as a conclusion",
          "stranded" in ABANDON_GROUNDS, False)
    # ⚑ A REPARENTED PROCESS STILL READS AS THE STRONGER GROUND — the widening must not
    # relabel what the node test already decided correctly.
    _rep = Proc(700, 1, "R", "%s/scratch/hot.py" % REPO, 400.0, 500.0)
    check("a reparented process keeps the CONCLUSION ground",
          strand_ground(_rep, [_rep])[0], "reparented")
    # ⚑ AND THE WALK IS THE REUSED ONE, not a second /proc parser in this file.
    check("chain() delegates to ratchet.ancestry",
          chain(os.getpid())[0][0], os.getpid())
    check("...and a dead pid yields an empty chain rather than raising",
          chain(2 ** 22 - 1), [])
    # ⚑⚑ THE FALSE POSITIVE THAT FALSIFIED MY FIRST CUT, PINNED AS A CASE. Self and its
    # own ancestors run from a harness shell too, so a census that did not exclude them
    # would report ITSELF as abandoned — the 46-vs-40 defect one layer up.
    _me = read_proc(os.getpid())
    check("the census does not report its own process as harness-rooted",
          strand_ground(_me, None)[0] if _me else None, None)

    # ── Ⓝ26/Ⓝ27: the invariance legend and the subtree column ──────────────────
    # ⚑⚑ THE PREMISE THIS RETIRES WAS HELD FOR SIX ROUNDS. Operator: *"The box will never
    # be quiet. You cannot measure a gate in wall time, only cputime."* Timing figures were
    # repeatedly set aside as "lower bounds pending a quiet box" while the CPU column beside
    # them was already the answer. The legend must SAY that at the point of reading.
    check("the legend names cpu as the invariant column",
          "invariant under co-tenancy" in _INVARIANCE_LEGEND, True)
    # ⚑ AND IT MUST NOT COLLAPSE THE TWO — elapsed is the ONLY column that can show a
    # wedge, because a hung process burns no CPU while its elapsed climbs.
    check("...and keeps elapsed as the wedge detector",
          "WEDGE" in _INVARIANCE_LEGEND and "0 cpu" in _INVARIANCE_LEGEND, True)
    # ⚑⚑⚑ THE FLOOR, AND IT IS THE CASE THAT MATTERS MOST. A 2061-second run was killed
    # because nobody could tell a scan from a spin, and NO column here can. A future edit
    # that trims this sentence would restore a legend implying the % answers a question it
    # cannot — the precise over-claim this session paid for.
    check("...and states that % cannot separate work from a spin",
          "tight spin" in _INVARIANCE_LEGEND, True)
    # ⚑ A LITERAL `%`, not `%%`: the constant is PRINTED, never interpolated, and the
    # doubled form leaked into the first run's output.
    check("...with a literal percent, not a format escape",
          "%%" in _INVARIANCE_LEGEND, False)
    # ⚑⚑ THE SUBTREE COLUMN IS THE ORPHAN-COST FIX (Ⓝ27). The reaped orphan presented as
    # 0.4s of self CPU over 7402s of children; a row without this column sorts it LAST in
    # the mode named for cost.
    _lnch = Proc(900, 1, "S", "%s/scripts/membudget run" % REPO, 0.0, 500.0)
    check("a row omits the subtree column when none is given",
          "subtree" in _fmt(_lnch), False)
    check("...and shows it when the caller computed one",
          "subtree" in _fmt(_lnch, 461.0), True)
    # ⚑ SELF CPU SURVIVES BESIDE IT — the two together are what distinguish a hot LEAF
    # (self ≈ subtree) from a LAUNCHER over hot children (self ≈ 0).
    check("...without dropping self cpu", "cpu      0.0s" in _fmt(_lnch, 461.0), True)

    # ── the mode roster against the dispatch (climode) ──────────────────────────
    # ⚑ gate-F14: A DECLARATION THAT CANNOT FAIL IS NOT A DECLARATION. `contract_rows`
    # is the discriminator — it bites on an undeclared mode, a phantom row, a scanning
    # mode that never reports skips, and a writer with no --apply guard. Running it over
    # THIS file's own source is what makes the roster above falsifiable.
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        _src = fh.read()
    _rows = [(f, ok, why) for f, ok, why in contract_rows(_src, MODES) if ok is not True]
    check("the mode roster agrees with the dispatch", _rows, [])
    check("the selftest declaration satisfies its contract", SELFTEST.contract()[0], True)
    # ⚑ --kill IS THE ONLY MUTATOR AND MUST SAY SO — a writes=() on it would exempt it
    # from the --apply discriminator entirely.
    check("--kill declares it writes", MODES["--kill"].mutates, True)
    check("...and no read mode does",
          [f for f, m in MODES.items() if m.mutates and f != "--kill"], [])
    # ⚑⚑ `--abandoned` IS DECLARED AS `--kill`'S OPT AS WELL AS A MODE — Ⓟ8. Without the
    # opt declaration `contract_rows` reads the flag inside the kill branch as a
    # DISPATCHED-undeclared mode; with it, the widening is a modifier OWNED by the mutator,
    # which is what it is. The two declarations are one fact and this pins them together.
    check("--abandoned is a mode", "--abandoned" in MODES, True)
    check("...and is declared as --kill's opt, so the widening is owned",
          "--abandoned" in MODES["--kill"].opts, True)
    # ⚑⚑⚑ THE DEFAULT MUST NOT HAVE WIDENED. A killer that starts reaping more than it did
    # is worse than one that reaps too little: under-reaping leaves the process there to be
    # found, over-reaping destroys the evidence. This case is the guard on that promise —
    # `--kill` without `--abandoned` must call `orphans`, and a future edit swapping the
    # default fails HERE rather than in someone's process tree.
    import inspect as _insp
    _ksrc = _insp.getsource(main)
    _kbody = _ksrc[_ksrc.index('if "--kill" in argv:'):]
    check("--kill's population is conditional on --abandoned, not widened by default",
          'abandoned(procs, ex) if wide else orphans(procs, ex)' in _kbody, True)
    check("...and the branch names which population it is about to act on",
          "population:" in _kbody, True)
    # ⚑⚑⚑ Ⓝ9's GUARD ON ITSELF. The whole finding is that the killer measured its own
    # sending rather than the tree's state, so a future edit that drops the re-read would
    # restore exactly the blindness this mode exists to remove — and it would do so
    # SILENTLY, since `SIGTERM sent to N` still prints and still exits 0.
    check("--kill re-reads the tree after signalling", "kill_census(targets" in _kbody, True)
    check("...from a FRESH sample, not the pre-kill one",
          "after, unreadable2 = all_procs()" in _kbody, True)
    check("...and prints the reaped-vs-reparented ambiguity unconditionally",
          "does NOT distinguish reaped from reparented" in _kbody, True)
    # ⚑ THE SETTLE IS BEFORE THE RE-READ, NOT AFTER. Reading /proc the instant os.kill
    # returns reports every target alive — SIGTERM is asynchronous — and would read as a
    # total failure of a kill that worked.
    check("...after a settle interval, since SIGTERM is asynchronous",
          _kbody.index("_time.sleep(KILL_SETTLE_S)") < _kbody.index("after, unreadable2"),
          True)

    _N = 75
    for line in fails:
        print(line)
    print("procstruct selftest: %d/%d" % (_N - len(fails), _N))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
