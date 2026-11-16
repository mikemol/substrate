#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Store-and-forward for measurements, PRODUCER-SIDE and daemon-free.

⚑ WHY A BUFFER AT ALL.  A measurement that moves between runs is only readable as
a SERIES, and the series lives in cassian's TSDB (180d retention, someone else's
storage).  But a suite run finishing while that store is unreachable would drop
its sample silently, and a dropped sample is exactly the gap that makes `873` vs
`885` unreadable -- the defect the series exists to close.

⚑ THE BUFFER CANNOT LIVE ON THE STORE'S HOST.  It exists for the case where
cassian is down; a queue there shares that outage.  So it is producer-side, in
this repo, next to the thing being measured.

⚑ AND IT MUST NOT REQUIRE A DAEMON (user, 2026-08-02: *"your broker shouldn't be
always-on; it's something that shouldn't require an active daemon"*).  That
retired RabbitMQ/`pika`, which I proposed and withdrew: a broker that must be
RUNNING to buffer against an outage inverts the dependency -- the buffer would
need more availability than the store it protects.

⚑ THE SHAPE IS GLUSTER'S, NOT A BROKER'S (user: *"nothing like how gluster
distributed management responsibilities among clients over a common store?"*):
arbitration in the CLIENTS, state in a COMMON STORE, no process in between.
`persist-queue`'s `SQLiteAckQueue` is that, with AMQP's vocabulary --
`ack`/`nack`/`ack_failed` leases over a SQLite file.

⚑ WHY A DEPENDENCY AND NOT A TABLE I WRITE.  Read from its source, not its
README: `SQLiteAckQueue(path, auto_resume=True)` calls `resume_unack_tasks()` in
`__init__`, so a process that dies mid-drain has its leased-but-unacked rows
returned to `ready` on the next open.  That crash case is precisely what a
hand-rolled queue loses silently, and it is the reason to adopt rather than
build.  (⚑ I nearly wired `resume_unack_tasks` as a method call I would have had
to remember: `--in persistqueue --calls resume_unack_tasks` reported **0 defs, 1
call** -- in the package's own tests -- which is what sent me to the constructor.
Reading the contract beat inferring it, again.)

⚑ THE SPOOL IS A BUFFER, NEVER A SECOND STORE (user: *"the point behind the TSDB
is that someone else owns storage"*).  Depth is bounded by DELIVERY LAG, not by
history: acked rows are cleared, and the queue is capped so a week-long outage
drops oldest-first rather than growing without bound.  A spool that keeps
everything is the storage we explicitly do not own -- and my first design said
"append-only, survives the drain", which was OBS's own defect smuggled back in.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPOOL_DIR = os.path.join(ROOT, ".spool")

# ⚑ BOUNDED, AND THE BOUND IS STATED.  ~1 row per suite run; 512 is weeks of
# outage.  Past it the OLDEST are dropped and the drop is COUNTED -- a silent
# truncation would make the spool lie about what it holds, which is worse than
# losing the sample.
MAX_DEPTH = 512


def _queue(name):
    """The ack queue, or None when the library is absent.

    ⚑ ABSENCE IS NOT AN ERROR HERE.  Telemetry is an OBSERVATION of a run, never
    part of it: a suite must not fail because a buffer is unavailable.  The
    caller reports the degradation and carries on.
    """
    try:
        from persistqueue import SQLiteAckQueue
        from persistqueue.serializers import json as json_ser
    except ImportError:
        return None
    os.makedirs(SPOOL_DIR, exist_ok=True)
    # ⚑ JSON, NOT THE DEFAULT PICKLE.  A durable file of pickles is a
    # deserialization surface with no upside for a dict of numbers.
    return SQLiteAckQueue(os.path.join(SPOOL_DIR, name),
                          auto_resume=True, serializer=json_ser)


def enqueue(name, sample):
    """Buffer one sample. Returns (depth, dropped)."""
    q = _queue(name)
    if q is None:
        return (0, 0)
    dropped = 0
    # ⚑ DROP OLDEST, NOT NEWEST.  A monitoring series wants the RECENT end; an
    # outage that discards today's sample to keep last month's has the priority
    # backwards.
    while q.size >= MAX_DEPTH:
        try:
            old = q.get(block=False)
            q.ack(old)
            dropped += 1
        except Exception:
            break
    q.put(sample)
    return (q.size, dropped)


def drain(name, deliver):
    """Hand each buffered sample to `deliver(sample) -> bool`. Returns a report.

    ⚑ THE DELIVERY IS A PARAMETER, so this module knows nothing about OTLP,
    cassian, or metrics -- the same reason `dagcone` takes a successor function
    and `routing.closure(seed, rev)` takes its graph.  A spool that imported the
    exporter would be a second place the endpoint lives.

    ⚑ AND A FAILED DELIVERY IS `nack`, NOT `ack_failed`.  `nack` returns the row
    to `ready` for the next run; `ack_failed` dead-letters it.  A store that is
    merely DOWN is the first case -- treating it as the second would discard the
    sample the buffer exists to preserve.
    """
    q = _queue(name)
    if q is None:
        return {"delivered": 0, "kept": 0, "absent": True}
    sent = kept = 0
    # snapshot the depth first: rows nacked back to `ready` inside this loop
    # would otherwise be retried forever within one drain.
    for _ in range(q.size):
        try:
            item = q.get(block=False)
        except Exception:
            break
        try:
            ok = deliver(item)
        except Exception:
            ok = False
        if ok:
            q.ack(item)
            sent += 1
        else:
            q.nack(item)
            kept += 1
    # ⚑ `clear_acked_data` MUST BE CALLED -- acked rows persist otherwise, and a
    # buffer that keeps its history has become the store we do not own.
    if sent:
        try:
            q.clear_acked_data(keep_latest=0)
        except Exception:
            pass
    return {"delivered": sent, "kept": kept, "absent": False}


def depth(name):
    """How many samples are waiting — the honest 'how far behind am I'."""
    q = _queue(name)
    return 0 if q is None else q.size


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    import tempfile
    global SPOOL_DIR
    _saved = SPOOL_DIR
    try:
        SPOOL_DIR = tempfile.mkdtemp(prefix="spool-selftest-")
        if _queue("t") is None:
            # ⚑ THE PROSE SAID "UNRUN, NOT PASSED" AND THE RETURN VALUE SAID
            # PASSED.  `spool.py:203` is `sys.exit(0 if _selftest() else 1)`, so
            # `return True` here made a missing `persist-queue` exit 0 — and
            # `.githooks/pre-commit` wires `run_selftests.py` as a BLOCKING gate
            # whose `RESULT = re.compile(r"selftest:\s*(\d+)\s*/\s*(\d+)")`
            # MATCHES `0/0`, then computes `bad = ok != all_` → `0 != 0` → False.
            # Green, on both sides, with zero cases executed.
            #
            # ⚑ MEASURED, NOT HYPOTHETICAL: `pycodemod --available persistqueue`
            # reports ABSENT on this machine, so the eight assertions below —
            # including the bounded-depth cap whose own comment calls it "the
            # second store this must not become" — have never run here, and every
            # "N suites green" reported from this tree included a vacuous one.
            #
            # An UNMEASURED suite is not a passing suite (Guard (2)'s rule, which
            # this repo already applies to an incomplete census and to a `stale`
            # build log).  Emitting NO counted line is the honest signal: the
            # runner's own comment says "a silent selftest is indistinguishable
            # from a passing one" and treats a missing count as a FAILURE, which
            # is exactly the verdict owed here.
            print("spool selftest: SKIPPED — persist-queue absent, 0 cases run "
                  "(UNRUN is not a pass)")
            return False

        enqueue("t", {"n": 1})
        enqueue("t", {"n": 2})
        check("a buffered sample raises the depth", depth("t"), 2)

        # ⚑ THE CASE THAT PINS THE POINT: a FAILED delivery keeps the sample.
        # An implementation that acked regardless would pass a "drain runs"
        # check and lose every sample during an outage.
        r = drain("t", lambda s: False)
        check("a failed delivery keeps every sample", r["kept"], 2)
        check("and delivers none", r["delivered"], 0)
        check("so the depth survives the outage", depth("t"), 2)

        seen = []
        r2 = drain("t", lambda s: (seen.append(s), True)[1])
        check("a successful drain delivers all", r2["delivered"], 2)
        check("the spool empties on success", depth("t"), 0)
        check("and the payload round-trips", sorted(x["n"] for x in seen), [1, 2])

        # ⚑ THE BOUND IS REAL AND THE DROP IS COUNTED.  A spool that grows
        # without limit is the second store this must not become.
        SPOOL_DIR = tempfile.mkdtemp(prefix="spool-cap-")
        for i in range(MAX_DEPTH + 3):
            _d, _dropped = enqueue("cap", {"i": i})
        check("depth is capped", depth("cap") <= MAX_DEPTH, True)
        # the OLDEST go: the recent end is what a series needs
        got = []
        drain("cap", lambda s: (got.append(s["i"]), True)[1])
        check("the newest sample survives the cap", MAX_DEPTH + 2 in got, True)
        check("the oldest was dropped", 0 in got, False)
    finally:
        SPOOL_DIR = _saved

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print("  FAIL %s: got %r want %r" % (n, got, want))
    print("selftest: %d/%d" % (ok, len(cases)))
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    if "--depth" in sys.argv:
        i = sys.argv.index("--depth")
        name = sys.argv[i + 1] if i + 1 < len(sys.argv) else "selftest"
        print("%s: %d sample(s) waiting" % (name, depth(name)))
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
