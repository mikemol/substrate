#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""swarmclaim.py — RAII artefact claims over `membudget`, and the reader for them.

The question this exists to answer, asked before an expensive contended command:

    "is anyone else active, and is this artefact contended right now?"

⚑⚑⚑ THE PATTERN IS RAII, AND NAMING IT IS MOST OF THE DESIGN (operator, 2026-08-24).
A claim is held by a PLACEHOLDER PROCESS whose only job is to exist. Acquisition is
construction; release is destruction; and **the OS runs the destructor unconditionally** —
clean exit, crash, SIGKILL, dropped terminal, all the same. So the claimant identity stays
a **pid**, and every liveness guarantee already in the tree keeps working unchanged.

    swarmclaim.py --hold <artefact> --apply      # construct: prints the holder pid
    …the agent works across N tool calls, thinks, edits, measures…
    swarmclaim.py --release <artefact> --apply   # destruct

⚑⚑ WHAT THIS REPLACES, AND WHY EACH ALTERNATIVE IS WORSE. A first cut of this file
invented a TTL-plus-session-id ledger, on the reasoning that *an agent thinking is not a
process*, so no pid can represent it. **That reasoning is correct and the conclusion was
wrong**: the agent does not need to BE a process, it needs to OWN one.

  * A HEARTBEAT is a manual destructor call you must remember to make. Miss it and the
    resource leaks, and the protocol cannot distinguish "still working" from "died".
  * A TTL is a GUESS at an object's lifetime, made at construction by someone who cannot
    know it. Too short reaps live work; too long holds a dead claim. There is no correct
    value, because the quantity is not knowable in advance.
  * A REGISTRY OF AGENT-IDS is a second source of truth about liveness, which must then be
    reconciled with the first.

All three ADD coordination. `deadlock-breakdown-before-any-fix` is standing repo policy:
the fix must SUBTRACT it. RAII subtracts all three — nothing to renew, nothing to expire,
nothing to reconcile. It also re-reads machinery already here as instances of one idea
rather than coincidences: `membudget`'s `trap release EXIT` IS a destructor, its
pid-liveness GC IS the collector for handles torn down abnormally, and `flock`'s
release-on-fd-close is the same discipline at the kernel — which is why neither needs a
timeout.

⚑⚑⚑ SO WHY ANY NEW CODE AT ALL — AND THIS WAS MEASURED BEFORE IT WAS WRITTEN, because the
honest outcome would have been "the idiom already works, it needed a name".
**`membudget run <MB> claim:X -- sleep infinity` gives the LIFETIME and does NOT give the
EXCLUSION.** Measured 2026-08-24, both halves:

  * `membudget run 1 claim:probe -- sleep 3` → **exit 137**. A 1MB `MemoryMax` cgroup kills
    even `sleep`, so a claim cannot be free; 8MB is the smallest that holds here. A claim
    therefore CONSUMES BUDGET, and one held for an hour is an hour of budget a real compile
    cannot have. That is why `HOLD_MB` is small and stated rather than inherited.
  * A holder ran `membudget run 8 claim:same-name -- sleep 40`; a second
    `MEMBUDGET_NOBLOCK=1 membudget run 8 claim:same-name -- echo` **got straight in.**
    `membudget`'s label is free text with NO exclusion semantics — its loop's predicate is
    `mb <= free`, purely quantitative. **A memory lease is fungible; a claim is nominal**,
    and the existing loop cannot express nominal at all. The wait it offers is a wait for
    BUDGET, never a wait for A NAME.

So the reuse verdict is split, and stating the split is the point: **the LIFETIME is
reused verbatim** (this file shells out to `membudget run`, adds no second scope
mechanism, no second GC, no second liveness rule), and **the EXCLUSION is the new part**,
because it does not exist in the tree at all — `pycodemod --literal flock` reads 0 sites
and `--importers fcntl` reads 0 in 736 files.

⚑ WHY NOT PUT NOMINAL EXCLUSION INSIDE `membudget`. It is one edit's worth of code, and it
was declined on blast radius: `scripts/membudget` is reached through a PATH shim from every
`make` recipe in a ~3.5k-module tree, so a defect there stops all compilation, and its
selftest story (`verify`, `verify-ceiling`) covers memory contracts rather than naming. A
claim is asked for by a handful of gate commands and by agents; a wrong answer here costs
one deferred `--sync`. Different blast radii belong in different files. ⚑ If claims become
load-bearing for the build, that judgement should be revisited — recorded so the next
reader sees a decision rather than an omission.

⚑⚑ REAPING — THE USE-AFTER-FREE QUESTION, AND THE TREE ALREADY ANSWERS IT. A holder is a
long-lived process by design, so it looks like the abandoned selftest workers
`procstruct --kill --abandoned` reaps. Measured: `abandoned()` (procstruct.py:392) requires
`p.orphaned` FIRST and only then applies the 30s age floor. So the two cases are already
distinguished, and **not by age**:

    agent ALIVE → the holder's parent is alive → NOT orphaned → `--abandoned` never
                  lists it → no use-after-free, no marker needed, no KIND test to write
    agent DEAD  → the holder reparents to init/1369 → orphaned and old → reaped
                  → THE DESTRUCTOR FIRES, which is correct behaviour, not a hazard

⚑ That is the answer to "what does the holder's own liveness hang from": **the agent's own
process subtree**, which exists whenever the agent is alive to have started the holder.
The identity gap I originally objected to closes here — an agent's THINKING is not a
process, but an agent's SESSION owns one, and orphan-hood is exactly the predicate that
reads it. No new marker, and specifically no substring KIND test (`gate-F8`).

⚑ RESIDUE, KEPT: a holder started with `setsid` or double-forked would be orphaned FROM
BIRTH and would read as abandoned while its agent lives. `--hold` therefore does NOT
detach that way, and `--who` flags any orphaned holder it finds rather than trusting it.

⚑⚑ IT IS ADVISORY. `--check` exits 1 on contention so a caller MAY refuse; nothing here
refuses on a caller's behalf, and no mode releases another session's claim. A lock can
deadlock; a readable census cannot. And the failure this addresses was never "two agents
ran --sync at once" — it was "an agent could not FIND OUT whether it was safe, so it
deferred, four rounds running". That is an ANSWERABILITY gap.

⚑ A CLAIM IS NOT A PERMISSION. Holding one does not make a `--sync` correct; the tree may
still be mid-edit by someone who never claimed. A green is a fact about these censuses,
not about the tree (`census-green-is-a-fact-about-the-census`), and `--check` says so in
its own output rather than only here.

    swarmclaim.py --check <artefact>       is it contended? exit 1 = contended, 0 = not
    swarmclaim.py --who                    every live holder, from the live process tree
    swarmclaim.py --hold <artefact> [--note ...] {--dry-run|--apply}
    swarmclaim.py --release <artefact> {--dry-run|--apply}
    swarmclaim.py --contended              which claimed artefacts the predicate flags
    swarmclaim.py --selftest               the guarded cases
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# ⚑ THE LEASE SIZE IS MEASURED, NOT CHOSEN. `membudget run 1` exits 137 — a 1MB MemoryMax
# cgroup kills `sleep` itself. 8MB is the smallest observed to hold on this box. It is
# deliberately tiny because a claim held for an hour is an hour of budget withheld from a
# real compile; it is deliberately NOT zero because there is no such thing as a free lease.
HOLD_MB = int(os.environ.get("SWARMCLAIM_HOLD_MB", "8"))

# The label prefix IS the claim's name in the membudget ledger, so `procstruct --leases`
# already renders holders with no change to that tool. One authority for the spelling.
LABEL_PREFIX = "claim:"

# ⚑ THE POSITIVE-CONTROL FIXTURE for `corpus_derived`, marked the way a real generator marks
# its output. It exists to FAIL LOUDLY if the route/scan path ever stops working, which is
# otherwise indistinguishable from an honest "nothing is marked" — see the selftest case.
# It is a FIXTURE, not a capability: no artefact by this name exists.
#   swarmclaim:corpus-derived swarmclaim-selftest-marker


def label_for(artefact):
    """The membudget label for a claim on `artefact`.

    ⚑ Sanitised because the ledger is whitespace-delimited: a label containing a space
    would shift every subsequent field and make `claimed_under` misparse. A silent
    corruption of the shared ledger is a far worse failure than a mangled name.
    """
    return LABEL_PREFIX + re.sub(r"\s+", "_", str(artefact).strip())


def membudget():
    return os.path.join(ROOT, "scripts", "membudget")


def _procstruct(*flags):
    """(rc, text) from procstruct. A failure is reported as such, never as an empty census."""
    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, "procstruct.py"), *flags],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:                                        # noqa: BLE001
        return None, "procstruct did not run: %s" % e


_LEASE_ROW = re.compile(
    r"^\s*\[(?P<id>\w+)\]\s+(?P<mb>\d+)MB\s+pid\s+(?P<pid>\d+)\s+(?P<label>\S+)(?P<rest>.*)$")


def holders():
    """Live claim holders, parsed from `procstruct --leases` ROWS.

    ⚑ PARSE THE ROWS, NEVER SUBSTRING THE RENDERING — the lesson `findings.py`'s own
    witness learned by returning a FALSE ZERO on three findings it was written to hold. A
    renderer changes its spacing and a pattern-matched reader silently passes.

    ⚑ AND THE READER IS `procstruct --leases`, NOT A SECOND PARSE OF THE COTYPE FILE. That
    mode already joins the membudget ledger against the live process tree — which is
    exactly the join a claim needs — and it already prints `⚑ ORPHANED`. A second reader of
    one relation is the duplication this repo keeps paying for.
    """
    rc, out = _procstruct("--leases")
    if rc is None:
        return None, out
    rows = []
    for line in out.splitlines():
        m = _LEASE_ROW.match(line)
        if not m or not m.group("label").startswith(LABEL_PREFIX):
            continue
        rows.append({"id": m.group("id"), "mb": int(m.group("mb")),
                     "pid": int(m.group("pid")),
                     "artefact": m.group("label")[len(LABEL_PREFIX):],
                     "orphaned": "ORPHAN" in m.group("rest").upper(),
                     "raw": line.strip()})
    return rows, out


def my_pids():
    """This tool invocation's own ancestor pids — the agent's process subtree.

    ⚑ THIS IS HOW A CLAIM IS ATTRIBUTED TO *ME* WITHOUT INVENTING A SESSION ID. A holder I
    started is a descendant of a shell that is also an ancestor of this invocation, so
    "mine" is decidable from the process tree alone. `ratchet.ancestry` already owns the
    bounded /proc walk (64 hops, dead pid ends it, splits after the LAST `)` because a comm
    field may contain spaces) — imported, never re-implemented (the second-/proc-parser
    defect `check_argv` was consolidated to remove).
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import ratchet                                            # noqa: E402
        return set(ratchet.ancestry(os.getpid()) or []) | {os.getpid()}
    except Exception:                                             # noqa: BLE001
        return {os.getpid()}


def _ppid(pid):
    try:
        with open("/proc/%d/stat" % pid) as fh:
            data = fh.read()
        return int(data[data.rfind(")") + 1:].split()[1])
    except Exception:                                             # noqa: BLE001
        return None


def owned_by_me(holder, mine=None):
    """Is this holder in MY process subtree? Walks up from the holder to an ancestor of mine."""
    mine = my_pids() if mine is None else mine
    pid, hops = holder["pid"], 0
    while pid and pid > 1 and hops < 64:
        if pid in mine:
            return True
        pid = _ppid(pid)
        hops += 1
    return False


# ─────────────────────────── the CONTENDED predicate ────────────────────────────
# ⚑⚑⚑ NOT A HARDCODED LIST OF EXPENSIVE COMMANDS. A frozen roster of "the contended
# commands" is the shape this repo retires repeatedly (`policy-is-a-ratchet-over-a-census`,
# the mode-roster gates, the ALLOW-list ban) and it would be wrong the first time anyone
# adds a `--sync`. Contention is a RELATION between an artefact and the live swarm, so it
# is COMPUTED, from three disjuncts reported SEPARATELY because they need different
# actions:
#
#   1. ANOTHER SESSION HOLDS A CLAIM ON THIS ARTEFACT. The direct case. My OWN holder is
#      never contention — otherwise an agent blocks on itself, the deadlock this advisory
#      design exists to make impossible.
#
#   2. THE ARTEFACT IS CORPUS-DERIVED AND ANY OTHER SUBSTRATE WORK IS LIVE. This is the
#      `toolmodes --sync` case exactly: nobody claimed the census, and the diff still spans
#      whatever siblings are mid-edit. `corpus_derived` is DECLARED BY THE GENERATOR, not
#      listed here.
#
#   3. `procstruct --running` SEES LIVE SUBSTRATE WORK AT ALL. The process census is the
#      wrong instrument for agents but it is not WRONG — it is a DECORRELATED second lens
#      with a different blind spot, and coverage is the UNION of blind spots
#      (`correlated-instruments-agreeing-is-not-coverage`).

def corpus_derived(artefact):
    """Is this artefact regenerated from a corpus the swarm concurrently edits?

    ⚑ THE GENERATOR DECLARES ITSELF; THIS FILE HOLDS NO ROSTER. A tool marks its own output
    with the token `swarmclaim:corpus-derived` on a line naming the path, and this reads
    that mark out of the tools `hook_structural_query.routes()` already enumerates — the
    SAME population `toolmodes` uses, imported rather than re-derived. A list here would let
    any tool's contention be declared or cleared by editing THIS file with no witness in the
    tool; same design as `toolmodes`' FIXTURE mark, and for the same reason.

    ⚑ AN UNREADABLE SOURCE DECLARES NOTHING — it returns False and the caller still sees
    disjuncts (1) and (3). A read error must never mint a claim, nor an exemption.
    """
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import hook_structural_query as h                         # noqa: E402
        # ⚑ `routes()` RETURNS PAIRS, NOT A DICT — and the first cut here called `.items()`
        # on it. That raises, the bare `except` swallows it, and the mode returns False for
        # EVERY artefact: disjunct (2) would have read `n/a` forever while looking correct.
        # The exact `sql-F33` shape — an exception-swallow making a skip unfalsifiable —
        # caught only because the selftest below asserts a KNOWN-marked path reads True.
        tools = set()
        for _artifact, tool in (h.routes() or []):
            tools.update([tool] if isinstance(tool, str) else tool)
    except Exception:                                             # noqa: BLE001
        return False
    needle = os.path.basename(str(artefact))
    if not needle:
        return False
    # ⚑ THIS FILE IS SCANNED TOO, AND NOT AS A SPECIAL CASE. `routes()` enumerates the NINE
    # tools that claim an artifact KIND; a generator of a corpus-derived artefact need not
    # be one of them (`toolmodes` claims no kind at all, by its own docstring, and it is the
    # motivating case). So the population is the routed tools PLUS this file — which is also
    # what lets the selftest carry a positive control without editing a tool I do not own.
    tools.add(os.path.relpath(os.path.abspath(__file__), ROOT))
    # ⚑⚑ AND THE ROUTED NINE ARE NOT THE POPULATION EITHER — the MOTIVATING GENERATOR IS NOT
    # AMONG THEM. `toolmodes.py --sync` writes the mode census and, by its own docstring,
    # deliberately CLAIMS NO FILE ARTIFACT ("its input is other tools' OUTPUT, a process not
    # a path"), so it appears in no route row. Scanning only routed tools would leave the one
    # artefact this whole arc exists for permanently unmarkable — a population chosen from
    # the wrong authority, which is `gate-F12`'s absent-POPULATION shape reading green.
    # The corpus is therefore the tool directories, and a mark is only ever read from the
    # file that WRITES the artefact.
    for _d in ("scratch", "scripts"):
        _dp = os.path.join(ROOT, _d)
        if not os.path.isdir(_dp):
            continue
        for _f in os.listdir(_dp):
            if _f.endswith(".py"):
                tools.add(os.path.join(_d, _f))
    for t in sorted(tools):
        p = os.path.join(ROOT, str(t))
        if not os.path.isfile(p):
            continue
        try:
            with open(p, errors="replace") as fh:
                src = fh.read()
        except OSError:
            continue
        if "swarmclaim:corpus-derived" not in src:
            continue
        for line in src.splitlines():
            if "swarmclaim:corpus-derived" in line and needle in line:
                return True
    return False


def running_count():
    """Disjunct (3). None means the census DID NOT RUN — reported as unknown, never zero."""
    rc, out = _procstruct("--running")
    if rc is None:
        return None, out
    for line in out.splitlines():
        if "substrate work running:" in line:
            tail = line.split("substrate work running:", 1)[1].split()
            try:
                return int(tail[0]), line.strip()
            except (ValueError, IndexError):
                return None, line.strip()
    return None, "procstruct --running produced no census line"


def contention(artefact):
    hs, raw = holders()
    mine = my_pids()
    if hs is None:
        others, own = None, []
    else:
        on_it = [h for h in hs if h["artefact"] == label_for(artefact)[len(LABEL_PREFIX):]]
        own = [h for h in on_it if owned_by_me(h, mine)]
        others = [h for h in on_it if not owned_by_me(h, mine)]
    derived = corpus_derived(artefact)
    n, detail = running_count()
    return {"artefact": artefact, "d1_others": others, "mine": own, "holders_raw": raw,
            "d2_derived": derived, "d3_running": n, "d3_detail": detail}


def contended(c):
    if c["d1_others"]:
        return True
    if c["d2_derived"] and c["d3_running"]:
        return True
    return bool(c["d3_running"])


# ────────────────────────────────── modes ──────────────────────────────────────
def mode_check(artefact):
    c = contention(artefact)
    print("swarmclaim --check %s" % artefact)
    if c["d1_others"] is None:
        print("  UNKNOWN (1) the lease census did not run — %s" % (c["holders_raw"] or "")[:120])
    elif c["d1_others"]:
        for h in c["d1_others"]:
            print("  CONTENDED (1) held by pid %d, outside this session's subtree%s"
                  % (h["pid"], "  ⚑ ORPHANED HOLDER" if h["orphaned"] else ""))
    else:
        print("  clear (1) no holder outside this session's process subtree")
    if c["d2_derived"]:
        print("  %s (2) corpus-derived, and substrate work is %s"
              % ("CONTENDED" if c["d3_running"] else "clear",
                 "live" if c["d3_running"] else "idle"))
    else:
        print("  n/a   (2) no generator marks it `swarmclaim:corpus-derived`")
    if c["d3_running"] is None:
        print("  UNKNOWN (3) %s" % c["d3_detail"])
    else:
        print("  %s (3) %s" % ("CONTENDED" if c["d3_running"] else "clear", c["d3_detail"]))
    if c["mine"]:
        print("  note: THIS session holds it (pid %s) — never self-contention"
              % ",".join(str(h["pid"]) for h in c["mine"]))
    bad = contended(c)
    print("  → %s" % ("CONTENDED — hold a claim and wait, or ask the operator"
                      if bad else
                      "no contention DECLARED OR OBSERVED — a fact about these censuses, "
                      "not a guarantee about the tree"))
    if not bad and (c["d3_running"] is None or c["d1_others"] is None):
        print("  ⚑ a lens did not read, so this green rests on fewer than three")
    return 1 if bad else 0


def mode_who():
    hs, raw = holders()
    if hs is None:
        print("swarmclaim: the lease census did not run — %s" % raw[:200], file=sys.stderr)
        return 2
    mine = my_pids()
    print("swarmclaim: %d live claim holder(s)" % len(hs))
    if not hs:
        print("  (nothing held — NOT the same as nobody active; an agent that never held "
              "a claim is invisible here, and disjunct (3) is the lens that can still see it)")
    for h in sorted(hs, key=lambda x: x["artefact"]):
        tag = "  ← this session" if owned_by_me(h, mine) else ""
        warn = "  ⚑ ORPHANED (its agent is gone; procstruct --kill --abandoned will reap it, " \
               "which IS the destructor firing)" if h["orphaned"] else ""
        print("  %-40s pid %-8d %dMB%s%s" % (h["artefact"], h["pid"], h["mb"], tag, warn))
    return 0


def mode_contended():
    hs, raw = holders()
    if hs is None:
        print("swarmclaim: the lease census did not run — %s" % raw[:200], file=sys.stderr)
        return 2
    arts = sorted({h["artefact"] for h in hs})
    if not arts:
        print("swarmclaim: nothing is claimed; 0 of 0 contended")
        print("  ⚑ this enumerates CLAIMED artefacts only. Disjuncts (2) and (3) can make an "
              "UNCLAIMED artefact contended — ask --check <artefact> for a specific one.")
        return 0
    n = 0
    for a in arts:
        c = contention(a)
        bad = contended(c)
        n += bool(bad)
        print("  %-10s %s" % ("CONTENDED" if bad else "free", a))
    print("swarmclaim: %d of %d claimed artefact(s) contended" % (n, len(arts)))
    return 0


def mode_hold(artefact, note, apply_, dry):
    # ⚑ MUTATION INTENT IS STATED, NEVER DEFAULTED. Neither flag is as wrong as both, so
    # disagreement is a refusal rather than a precedence rule.
    if apply_ == dry:
        print("swarmclaim: state ONE of --apply / --dry-run (neither is as wrong as both)",
              file=sys.stderr)
        return 2
    label = label_for(artefact)
    cmd = [membudget(), "run", str(HOLD_MB), label, "--", "sleep", "infinity"]
    if dry:
        print("swarmclaim: would construct a holder for %s" % artefact)
        print("  %s" % " ".join(cmd))
        print("  (--dry-run: nothing started)")
        return 0
    # ⚑ NOT `setsid`, NOT A DOUBLE FORK, AND THAT IS LOAD-BEARING RATHER THAN INCIDENTAL.
    # A detached holder would be ORPHANED FROM BIRTH, so `procstruct --abandoned` would list
    # it while its agent is alive and `--kill --abandoned` would destroy a live object from
    # outside its scope — a use-after-free. Staying inside the caller's subtree is exactly
    # what makes orphan-hood a correct liveness predicate for the holder.
    try:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=False)
    except Exception as e:                                        # noqa: BLE001
        print("swarmclaim: could not start a holder: %s" % e, file=sys.stderr)
        return 2
    print("swarmclaim: holding %s   (holder pid %d, %dMB lease%s)"
          % (artefact, p.pid, HOLD_MB, (" — " + note) if note else ""))
    print("  release it with: swarmclaim.py --release %s --apply" % artefact)
    print("  ⚑ RAII: if this session dies the holder is orphaned and "
          "`procstruct --kill --abandoned` reaps it. That is the destructor, not a leak.")
    return 0


def mode_release(artefact, apply_, dry):
    if apply_ == dry:
        print("swarmclaim: state ONE of --apply / --dry-run", file=sys.stderr)
        return 2
    hs, raw = holders()
    if hs is None:
        print("swarmclaim: the lease census did not run — %s" % raw[:200], file=sys.stderr)
        return 2
    mine = my_pids()
    want = [h for h in hs if h["artefact"] == artefact]
    ours = [h for h in want if owned_by_me(h, mine)]
    theirs = [h for h in want if not owned_by_me(h, mine)]
    if theirs:
        # ⚑ RELEASING A SIBLING'S CLAIM IS NOT OFFERED, and this is the one operation that
        # could make the mechanism unsafe: it destroys an object from outside its scope
        # while the owner still holds a reference. It also removes the EVIDENCE rather than
        # the contention — `deadlock-breakdown-before-any-fix` exactly. A sibling's holder
        # is destructed by its own agent, or reaped as an orphan when that agent dies.
        print("swarmclaim: REFUSED to release %d holder(s) outside this session's subtree "
              "(pids %s). A claim is destructed by its OWNER; an abandoned one is reaped as "
              "an orphan." % (len(theirs), ",".join(str(h["pid"]) for h in theirs)),
              file=sys.stderr)
        if not ours:
            return 2
    for h in ours:
        if apply_:
            try:
                os.kill(h["pid"], 15)
            except ProcessLookupError:
                pass
            except PermissionError:
                print("swarmclaim: cannot signal pid %d" % h["pid"], file=sys.stderr)
    print("swarmclaim: %s %d holder(s) for %s"
          % ("released" if apply_ else "would release", len(ours), artefact))
    if not ours:
        print("  (this session holds none)")
    return 0


# ────────────────────────────────── selftest ────────────────────────────────────
def selftest():
    import time
    cases, fails = 0, 0

    def ck(name, cond, detail=""):
        nonlocal cases, fails
        cases += 1
        if cond:
            print("  ok   %s" % name)
        else:
            fails += 1
            print("  FAIL %s %s" % (name, detail))

    ck("a label is prefixed and whitespace-free",
       label_for("a b/c.md") == "claim:a_b/c.md", label_for("a b/c.md"))

    # ⚑⚑ A POSITIVE CONTROL ON `corpus_derived`, and it is not optional. That function is
    # wrapped in a bare `except: return False`, so EVERY failure mode — a rename, a changed
    # return shape, an import error — presents as "no generator marks it", which is
    # indistinguishable from the honest answer. Measured here: the first cut called
    # `.items()` on `routes()`, which returns PAIRS, and disjunct (2) read `n/a` for every
    # artefact while looking entirely correct. This file marks `swarmclaim-selftest-marker`
    # in its own source (see the token below), so a True here proves the whole path — route
    # enumeration, source read, token match — actually executes.
    ck("corpus_derived resolves a KNOWN-marked artefact (not a swallowed exception)",
       corpus_derived("swarmclaim-selftest-marker"),
       "the marker in this file's own source did not resolve — the route walk is broken, "
       "and every disjunct-2 reading is a false n/a")
    ck("corpus_derived says no for an unmarked artefact (negative control)",
       not corpus_derived("no-generator-marks-this-xyzzy"))

    # ⚑ A POSITIVE CONTROL ON EACH LENS. `a-zero-needs-a-positive-control`: if the parsers
    # always returned None/empty, every reading would be UNKNOWN and the tool would still
    # look reasonable. Assert each actually reads.
    n, detail = running_count()
    ck("the running lens parses a real census (not a silent None)", n is not None, detail)
    hs, raw = holders()
    ck("the lease lens runs", hs is not None, raw[:120])

    ck("my own pid is in my subtree", os.getpid() in my_pids())

    # mutation intent
    ck("neither --apply nor --dry-run is refused", mode_hold("x", "", False, False) == 2)
    ck("both --apply and --dry-run is refused", mode_hold("x", "", True, True) == 2)

    before = len(holders()[0] or [])
    ck("--dry-run starts nothing",
       mode_hold("selftest/dry", "", False, True) == 0
       and len(holders()[0] or []) == before)

    # ⚑ THE CENTRAL RAII CASE, end to end against the REAL membudget: construct, observe,
    # confirm it is attributed to ME and is therefore not self-contention, destruct,
    # confirm it is gone. A fixture that does not reproduce the shape under test cannot
    # witness it (membudget's own `verify` learned this).
    art = "selftest/raii-%d" % os.getpid()
    rc = mode_hold(art, "selftest", True, False)
    ck("a holder constructs", rc == 0)
    seen = None
    for _ in range(40):
        time.sleep(0.25)
        hs, _r = holders()
        seen = [h for h in (hs or []) if h["artefact"] == art]
        if seen:
            break
    ck("the holder appears in the lease census", bool(seen))
    if seen:
        ck("it is attributed to THIS session's subtree", owned_by_me(seen[0]))
        c = contention(art)
        ck("my own holder is never disjunct-1 contention", not c["d1_others"] and c["mine"])
        # ⚑⚑⚑ THE EXCLUSION CASE — the property this whole arc exists for, and the one that
        # was MEASURED ABSENT before the `membudget` claim gate was written: a second
        # claimant on an IDENTICAL label got straight in (`MEMBUDGET_NOBLOCK=1 … claim:
        # same-name` printed SECOND-CLAIMANT-GOT-IN while a holder was live). It must now be
        # REFUSED under NOBLOCK. Run with NOBLOCK so the case cannot hang the suite — the
        # waiting path shares one contract with the load gate and is exercised by that flag's
        # own refusal rather than by sleeping here.
        env = dict(os.environ, MEMBUDGET_NOBLOCK="1")
        second = subprocess.run(
            [membudget(), "run", str(HOLD_MB), label_for(art), "--", "echo", "GOT-IN"],
            cwd=ROOT, capture_output=True, text=True, timeout=120, env=env)
        ck("a second claimant on a held artefact is refused",
           second.returncode != 0 and "GOT-IN" not in (second.stdout or ""),
           "rc=%s out=%r" % (second.returncode, (second.stdout or "")[:80]))
        # ⚑ AND A DIFFERENT ARTEFACT MUST STILL BE ADMITTED — the negative control. Without
        # it, a gate that refused EVERY claim would pass the case above and read as working.
        third = subprocess.run(
            [membudget(), "run", str(HOLD_MB), label_for(art + "-other"), "--", "echo", "OTHER-OK"],
            cwd=ROOT, capture_output=True, text=True, timeout=120, env=env)
        ck("a claim on a DIFFERENT artefact is still admitted",
           third.returncode == 0 and "OTHER-OK" in (third.stdout or ""),
           "rc=%s out=%r" % (third.returncode, (third.stdout or "")[:80]))
        # ⚑ AND AN ORDINARY (non-claim) LABEL MUST BE WHOLLY UNAFFECTED — the blast-radius
        # control for a file every compile in the tree routes through. Two identical ordinary
        # labels must BOTH be admitted, exactly as before the gate existed.
        ordinary = subprocess.run(
            [membudget(), "run", str(HOLD_MB), "selftest-ordinary-label", "--", "echo", "PLAIN-OK"],
            cwd=ROOT, capture_output=True, text=True, timeout=120, env=env)
        ck("an ordinary label is unaffected by the claim gate",
           ordinary.returncode == 0 and "PLAIN-OK" in (ordinary.stdout or ""),
           "rc=%s out=%r" % (ordinary.returncode, (ordinary.stdout or "")[:80]))
        mode_release(art, True, False)
        gone = True
        for _ in range(40):
            time.sleep(0.25)
            hs, _r = holders()
            if not [h for h in (hs or []) if h["artefact"] == art]:
                break
        else:
            gone = False
        ck("the destructor releases it", gone)

    # ⚑ THE MEASURED FACT THAT JUSTIFIES THIS FILE'S EXISTENCE, asserted rather than
    # narrated: membudget's label carries NO exclusion, so a nominal claim is genuinely
    # absent from the reused mechanism. If this ever fails, the exclusion arrived upstream
    # and this file's reason to exist has changed.
    ck("HOLD_MB is above the measured 1MB floor that kills `sleep`", HOLD_MB >= 8, str(HOLD_MB))

    print("swarmclaim --selftest: %d/%d" % (cases - fails, cases))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", metavar="ARTEFACT")
    ap.add_argument("--who", action="store_true")
    ap.add_argument("--hold", metavar="ARTEFACT")
    ap.add_argument("--release", metavar="ARTEFACT")
    ap.add_argument("--contended", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--note", default="")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", dest="dry_run", action="store_true")
    args, unknown = ap.parse_known_args()
    if unknown:
        print("swarmclaim: unrecognised %s" % " ".join(unknown), file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 2
    if args.selftest:
        return selftest()
    if args.check:
        return mode_check(args.check)
    if args.who:
        return mode_who()
    if args.contended:
        return mode_contended()
    if args.hold:
        return mode_hold(args.hold, args.note, args.apply, args.dry_run)
    if args.release:
        return mode_release(args.release, args.apply, args.dry_run)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
