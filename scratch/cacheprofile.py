#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Which functions would a cache actually help? — measured, not argued.

⚑ WHY THIS EXISTS.  Picking cache sites by reading a wall-clock profile is
judgement in the turn: a `cProfile` run says where time goes, never whether the
same call RECURS, and recurrence is the whole question.  A function can be 30s of
a run and be uncacheable (every call distinct); a cheap one called 10,000 times
with 12 distinct arguments is the candidate a time-ranked profile buries.  This
measures the three columns that actually decide it — hit rate, function RTT,
payload size — and ranks by expected saving, so the selection is a query.

    cacheprofile.py --probe                  # is the store reachable, and what is it
    cacheprofile.py --run <script> [args]    # profile a program, ranked candidates
    cacheprofile.py --selftest

⚑ OBSERVE-ONLY BY DEFAULT, AND THAT IS NOT TIMIDITY.  The interceptor computes the
key and records whether it was seen, then ALWAYS calls through.  Serving a cached
value changes behaviour for any impure function, and we cannot prove purity of 85
tools by inspection.  Observe-only produces the full ranking dataset with zero
behavioural risk; `--serve` proves a saving for a chosen few AFTER the dataset
says which are worth proving.

## The key

    profile:<session-uuid>:<sha1(module.qualname + pickle(args))>

⚑ SESSION-SCOPED BY A FRESH UUID, WHICH RETIRES INVALIDATION ENTIRELY (user,
2026-08-04: *"So long as the session is uuid, then the namespace is invalidated by
construction, and valkey will evict old"*).  A prior session's entries are not
merely stale, they are UNREACHABLE — no tree-stamp, no mutation hook, no expiry.
This matches cassian's stated contract for the store: **no TTL, no DELETE**;
entries are immutable and LFU eviction reclaims.

⚑ AND A SESSION IS NOT A PROCESS (user).  `_per_file` spawns a process pool; if the
id were `os.getpid()` every worker would mint its own namespace, hit rate would
read ~0 across every fan-out, and the profiler would report the parallel sites as
uncacheable — precisely the ones where sharing pays.  The id is therefore MINTED
ONCE and INHERITED through the environment, never derived.

⚑ PICKLE, NOT `repr(args)`.  `repr` was the first design and it is unsound as key
material — a census over this repo + mat230/mat260 found the failure in both
directions:

  * `UnifiedCodeword` (`scratch/unified_address.py:170`) defines `__str__` and NO
    `__repr__`, so `repr()` falls back to `<... object at 0x7f...>` — an ADDRESS.
    Two identical objects get different keys; a RECYCLED address makes two
    different objects collide.  It looks instrumented and is not, which is the
    shape a `def __repr__` census cannot find.
  * `RSBPF` (`aspf_rsbpf_ref.py:108`) renders `rank()` and `len(addr2())` while its
    own `__eq__` names `forest` — LOSSY against its own equality, so unequal
    objects produce one key.  It also embeds `dict(self.sigma)` whose order comes
    from a frozenset, i.e. NON-DETERMINISTIC ACROSS PROCESSES — it would break at
    exactly the pool boundary the session id exists to span.
  * `Compound` (`aspf_segment_ref.py:54`) renders every cycle as `<CYCLE lenN>`, so
    all distinct N-edge cycles collide — and it IS an argument type (`composable`).
  * `LogicNode` (`mat230-1-4-3b.py:21`) raises `NotImplementedError` from the base
    `__repr__`, and its subclasses recurse over the whole formula tree.

Pickle decomposes the object graph structurally, so none of those apply: it reads
FIELDS rather than a rendering, it is total over cycles (MEMOIZE/BINGET
back-references rather than a depth bound — so there is no capability bound to
record), and it cannot raise a user `__repr__`.  It is FINER than `__eq__` rather
than coarser, which under-reports hit rate — the safe direction, never a wrong
value.  We only ever `dumps`; nothing is ever `loads`-ed from an untrusted source,
so pickle's security caveat does not apply.

## Scope

Any in-repo `.py` file, by ORIGIN PATH — a discovered predicate, not a module list
that rots.  Library code is deliberately out: 816k `libcst` visitor calls per
`--next` run would dominate the interceptor's own cost, and a candidate we cannot
modify is not a candidate.

## Injection

An import hook (`sys.meta_path`) whose loader parses the source, decorates every
`FunctionDef`, compiles, and execs — the codemod under test, applied
NON-DESTRUCTIVELY.  Nothing is written to disk.

⚑ `ast` IS CORRECT HERE AND `libcst` IS NOT, WHICH INVERTS `pycodemod`'s RULE.
That module gates on losslessness because it emits SOURCE, and `ast` discards
comments — this corpus is its own incident log, so dropping commentary destroys
the more valuable half.  This path never emits source: it goes tree -> `compile()`
-> code object, and comments are not in the bytecode path at all.  A real
source-to-source apply MUST still be `libcst` under `--roundtrip`; do not grow an
`--apply` through this module.
"""

import ast
import hashlib
import os
import pickle
import socket
import sys
import time
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENDPOINT = ("127.0.0.1", 6379)
SESSION_ENV = "SUBSTRATE_PROFILE_SESSION"
NS = "profile"

# ⚑ THE INTERCEPTOR'S OWN COST IS SUBTRACTED, NOT IGNORED.  Wrapping every call
# inflates `fn_rtt` for cheap functions, biasing the ranking toward exactly the
# functions where the interceptor cost matters most.  Calibrated at startup.
_OVERHEAD = 0.0


def session_id():
    """The namespace UUID — MINTED ONCE, INHERITED THEREAFTER.

    ⚑ Read from the environment before generating, because a pool child must join
    its parent's namespace rather than mint a disjoint one."""
    sid = os.environ.get(SESSION_ENV)
    if not sid:
        sid = str(uuid.uuid4())
        os.environ[SESSION_ENV] = sid
    return sid


# --------------------------------------------------------------------------
# RESP — stdlib, no client dependency
# --------------------------------------------------------------------------

class Store:
    """Valkey over raw RESP — GET / SET / PING and nothing else.

    ⚑ STDLIB RESP RATHER THAN A CLIENT DEP, matching cassian's own collector
    (`scripts/collectors/cache-metrics`, "stdlib RESP, no client dep").  Neither
    `redis` nor `valkey` is importable here, and the profiler must run in pool
    children and bare environments — a dependency whose absence silently disables
    instrumentation is worse than thirty lines of wire protocol.

    ⚑ BEST-EFFORT, NEVER FATAL — cassian's stated contract.  Any failure
    (refused, timeout, store down) degrades to `None`, which the caller records as
    UNKNOWN rather than as a miss.  A cache problem must not fail a query, and it
    must not silently become a measurement either."""

    def __init__(self, endpoint=ENDPOINT, timeout=2.0):
        self.endpoint = endpoint
        self.timeout = timeout
        self.sock = None
        self.errors = 0

    def _connect(self):
        if self.sock is None:
            self.sock = socket.create_connection(self.endpoint, timeout=self.timeout)
        return self.sock

    def _cmd(self, *parts):
        out = [b"*%d\r\n" % len(parts)]
        for p in parts:
            if isinstance(p, str):
                p = p.encode()
            out.append(b"$%d\r\n" % len(p))
            out.append(p)
            out.append(b"\r\n")
        return b"".join(out)

    def _read_line(self, sock):
        buf = b""
        while not buf.endswith(b"\r\n"):
            ch = sock.recv(1)
            if not ch:
                raise OSError("connection closed")
            buf += ch
        return buf[:-2]

    def _read_reply(self, sock):
        line = self._read_line(sock)
        tag, rest = line[:1], line[1:]
        if tag == b"+":
            return rest
        if tag == b"-":
            raise OSError(rest.decode("utf-8", "replace"))
        if tag == b":":
            return int(rest)
        if tag == b"$":
            n = int(rest)
            if n == -1:
                return None                      # nil — a MISS, distinct from an error
            data = b""
            while len(data) < n + 2:
                chunk = sock.recv(n + 2 - len(data))
                if not chunk:
                    raise OSError("connection closed")
                data += chunk
            return data[:-2]
        raise OSError("unexpected RESP tag %r" % tag)

    def call(self, *parts):
        """-> reply, or None on nil; raises OSError on a transport problem."""
        sock = self._connect()
        sock.sendall(self._cmd(*parts))
        return self._read_reply(sock)

    def ping(self):
        try:
            return self.call("PING") == b"PONG"
        except (OSError, socket.timeout):
            return False

    def get(self, key):
        """-> (found, value) — or None when the STORE could not answer.

        ⚑ THREE OUTCOMES, NOT TWO.  nil is a genuine miss; an exception is the
        store failing to answer, which is NOT evidence of absence.  Collapsing
        them would report a broken cache as a 0% hit rate — a fact about the
        method reported as a fact about the workload."""
        try:
            v = self.call("GET", key)
        except (OSError, socket.timeout):
            self.errors += 1
            self.sock = None
            return None
        return (v is not None, v)

    def set(self, key, value):
        try:
            self.call("SET", key, value)
            return True
        except (OSError, socket.timeout):
            self.errors += 1
            self.sock = None
            return False

    def info(self):
        try:
            raw = self.call("INFO")
        except (OSError, socket.timeout):
            return {}
        out = {}
        for line in (raw or b"").decode("utf-8", "replace").splitlines():
            if ":" in line and not line.startswith("#"):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
        return out


# --------------------------------------------------------------------------
# keying
# --------------------------------------------------------------------------

class Unkeyable(Exception):
    """The arguments could not be serialised — recorded, never fatal."""


def key_material(args, kwargs):
    """pickle the call's arguments -> bytes, or raise Unkeyable.

    ⚑ kwargs ARE SORTED.  `f(a=1, b=2)` and `f(b=2, a=1)` are the same call, and a
    dict preserves insertion order — leaving it unsorted would report two distinct
    keys for one call and under-report the hit rate."""
    payload = (args, tuple(sorted(kwargs.items())))
    try:
        return pickle.dumps(payload, protocol=5)
    except Exception as exc:                    # unpicklable: a file, a socket, a lock
        raise Unkeyable(type(exc).__name__)


def call_key(qualname, args, kwargs, sid=None):
    h = hashlib.sha1(qualname.encode() + b"\0" + key_material(args, kwargs))
    return "%s:%s:%s" % (NS, sid or session_id(), h.hexdigest())


# --------------------------------------------------------------------------
# the ledger
# --------------------------------------------------------------------------

class Ledger:
    """Per-function counters.  This is the dataset the ranking reads."""

    def __init__(self):
        self.rows = {}

    def row(self, qualname):
        return self.rows.setdefault(qualname, {
            "ncalls": 0, "hits": 0, "misses": 0,
            "unknown": 0, "unkeyable": 0,
            "total_s": 0.0, "payload_bytes": 0, "payload_n": 0,
        })

    def record(self, qualname, outcome, elapsed, payload=None):
        r = self.row(qualname)
        r["ncalls"] += 1
        r[outcome] += 1
        r["total_s"] += elapsed
        if payload is not None:
            r["payload_bytes"] += payload
            r["payload_n"] += 1

    def ranked(self, overhead=0.0, backend_rtt=0.0):
        """Expected saving per function, best first.

        ⚑ THE RANKING IS A PRODUCT OF MEASURED FACTORS, NOT A TIME SORT.

            saving = hits x (fn_rtt - overhead - backend_rtt)

        A slow function whose arguments never repeat has `hits == 0` and ranks at
        zero however expensive it is — which is the whole reason this instrument
        exists, since a wall-clock profile cannot see recurrence.  Conversely a
        cheap function can rank NEGATIVE: if serving costs more than deriving, a
        cache there is a regression, and the sign says so rather than a reader
        having to reason it out."""
        out = []
        for qn, r in self.rows.items():
            keyed = r["hits"] + r["misses"]
            if not r["ncalls"]:
                continue
            fn_rtt = r["total_s"] / r["ncalls"]
            net = fn_rtt - overhead - backend_rtt
            hit_rate = (r["hits"] / keyed) if keyed else 0.0
            out.append({
                "qualname": qn,
                "ncalls": r["ncalls"],
                "hits": r["hits"],
                "hit_rate": hit_rate,
                "fn_rtt": fn_rtt,
                "total_s": r["total_s"],
                "unkeyable": r["unkeyable"],
                "unknown": r["unknown"],
                "avg_payload": (r["payload_bytes"] / r["payload_n"]) if r["payload_n"] else 0,
                "saving_s": r["hits"] * net,
            })
        out.sort(key=lambda d: -d["saving_s"])
        return out


LEDGER = Ledger()
STORE = None


def _interceptor(fn, qualname):
    """Wrap one function — OBSERVE-ONLY: key, record, always call through."""
    def wrapper(*args, **kwargs):
        try:
            k = call_key(qualname, args, kwargs)
        except Unkeyable:
            t0 = time.perf_counter()
            result = fn(*args, **kwargs)
            LEDGER.record(qualname, "unkeyable", time.perf_counter() - t0)
            return result
        seen = STORE.get(k) if STORE else None
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        if seen is None:
            LEDGER.record(qualname, "unknown", elapsed)
            return result
        found, _ = seen
        payload = None
        if not found and STORE:
            # ⚑ THE VALUE IS STORED EVEN THOUGH OBSERVE-ONLY NEVER READS IT — its
            # SIZE is the missing term in the backend cost.  A 200-byte return and
            # a 2MB return have very different `cache_rtt`, and measuring it here
            # is what keeps the ranking from resting on a guessed constant.
            try:
                blob = pickle.dumps(result, protocol=5)
                payload = len(blob)
                STORE.set(k, blob)
            except Exception:
                payload = None                  # unpicklable RESULT: cacheable key,
                                                # uncacheable value — a real finding
        LEDGER.record(qualname, "hits" if found else "misses", elapsed, payload)
        return result
    wrapper.__name__ = getattr(fn, "__name__", "wrapped")
    wrapper.__qualname__ = qualname
    wrapper.__wrapped__ = fn
    return wrapper


# --------------------------------------------------------------------------
# the AST transform
# --------------------------------------------------------------------------

_HOOK_MODULE = "_cacheprofile_rt"


class Injector(ast.NodeTransformer):
    """Decorate every `FunctionDef` with the interceptor.

    ⚑ THE SIMPLE FORM, DELIBERATELY (user, 2026-08-04).  I began designing around
    what a wrapper does to `functools.partial(...)` pickling across
    `pycodemod._per_file`'s process pool — letting one call site in one tool shape
    a corpus-wide instrument.  If pickling of a wrapped callable breaks under
    profiling, that is a limitation to RECORD, not a constraint to design around.

    ⚑ ASYNC AND NESTED DEFS ARE INCLUDED; `lambda` IS NOT — a lambda has no
    `FunctionDef` node to decorate and no stable qualname to key on."""

    def __init__(self, modname):
        self.modname = modname
        self.stack = []

    def _decorate(self, node):
        self.stack.append(node.name)
        qualname = "%s.%s" % (self.modname, ".".join(self.stack))
        self.generic_visit(node)
        self.stack.pop()
        deco = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=_HOOK_MODULE, ctx=ast.Load()),
                attr="_interceptor_for", ctx=ast.Load()),
            args=[ast.Constant(value=qualname)], keywords=[])
        node.decorator_list.insert(0, deco)
        return node

    def visit_FunctionDef(self, node):
        return self._decorate(node)

    def visit_AsyncFunctionDef(self, node):
        return self._decorate(node)

    def visit_ClassDef(self, node):
        """⚑ THE CLASS MUST ENTER THE QUALNAME, and my first draft omitted it.

        Tracking only `FunctionDef` names keyed `C.m` as `mod.m`, so two methods
        named `m` in one module collapse into ONE ledger row and the ranking sums
        unrelated work under a name that belongs to neither.  That is the
        bare-name collision `pycodemod --discards` already records (360 of 362
        rows one collision), reproduced in new code and caught only because the
        case asserted the qualname rather than the decoration count."""
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()
        return node


def instrument(src, modname):
    """source -> a code object with every function wrapped.  Non-destructive."""
    tree = ast.parse(src)
    tree = Injector(modname).visit(tree)
    # ⚑ THE IMPORT IS PREPENDED, NOT ASSUMED.  The decorator names a module that
    # must be bound in the module's own namespace before any def executes.
    tree.body.insert(0, ast.Import(names=[ast.alias(name=_HOOK_MODULE, asname=None)]))
    ast.fix_missing_locations(tree)
    return tree


def _interceptor_for(qualname):
    """The decorator the injected AST calls."""
    def deco(fn):
        return _interceptor(fn, qualname)
    return deco


def in_repo(path):
    """Is this file ours to instrument?  A PATH predicate — discovered, not listed.

    ⚑ `.venv` IS UNDER `ROOT` AND IS NOT OURS.  Site-packages inside the repo would
    otherwise pass a naive prefix test and drag `libcst`'s 816k per-run visitor
    calls into the census."""
    if not path:
        return False
    p = os.path.abspath(path)
    if not p.startswith(ROOT + os.sep) or not p.endswith(".py"):
        return False
    rel = p[len(ROOT) + 1:]
    parts = rel.split(os.sep)
    return not any(seg in (".venv", "site-packages", "_build", "node_modules")
                   for seg in parts)


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def calibrate(n=2000):
    """Measure the interceptor's own per-call cost, to subtract from `fn_rtt`.

    ⚑ WITHOUT THIS THE RANKING IS BIASED WHERE IT MATTERS MOST.  Wrapping inflates
    every measured `fn_rtt` by a constant; for a millisecond function that is
    noise, for a microsecond function it is most of the reading — so the
    un-calibrated instrument systematically overstates cheap functions, which are
    exactly the ones whose true saving may be negative."""
    def noop():
        return None
    wrapped = _interceptor(noop, "calibrate.noop")
    t0 = time.perf_counter()
    for _ in range(n):
        noop()
    bare = (time.perf_counter() - t0) / n
    t0 = time.perf_counter()
    for _ in range(n):
        wrapped()
    hooked = (time.perf_counter() - t0) / n
    return max(0.0, hooked - bare)


def report(rows, overhead, backend_rtt, store):
    if not rows:
        print("no instrumented calls recorded.")
        return
    print("%-52s %7s %7s %6s %9s %9s %8s" %
          ("function", "ncalls", "hits", "hit%", "fn_rtt", "saving", "payload"))
    for r in rows[:40]:
        print("%-52s %7d %7d %5.0f%% %8.4fs %8.3fs %7s" % (
            r["qualname"][:52], r["ncalls"], r["hits"], 100 * r["hit_rate"],
            r["fn_rtt"], r["saving_s"],
            _human(r["avg_payload"]) if r["avg_payload"] else "-"))
    tot = sum(r["saving_s"] for r in rows)
    unkeyable = sum(r["unkeyable"] for r in rows)
    unknown = sum(r["unknown"] for r in rows)
    print()
    print("%d function(s) instrumented; predicted saving %.2fs" % (len(rows), tot))
    print("interceptor overhead %.6fs/call (subtracted); backend rtt %.6fs/call"
          % (overhead, backend_rtt))
    # ⚑ `n of m`, ALWAYS — an unkeyable or store-unknown call is NOT a miss, and
    # collapsing them would report a fact about the METHOD as a fact about the
    # workload.  Both are printed even at zero, so their absence is a measurement.
    print("unkeyable calls: %d (arguments could not be pickled)" % unkeyable)
    print("store-unknown calls: %d (the cache could not answer; NOT misses)" % unknown)
    if store and store.errors:
        print("⚠ %d store error(s) — the unknown rows above are those calls"
              % store.errors)


def _human(n):
    for unit in ("B", "K", "M", "G"):
        if n < 1024:
            return "%.0f%s" % (n, unit)
        n /= 1024.0
    return "%.0fT" % n


def measure_backend_rtt(store, n=50, size=4096):
    """One GET+SET round trip, measured — never a quoted constant.

    ⚑ 0.07ms WAS A BARE PING, AND THE COST THAT MATTERS INCLUDES THE PAYLOAD.  A
    ranking that subtracts a remembered number is a hardcoded scalar; this is
    stamped at the moment the run happens, on this box, at this size."""
    if not store or not store.ping():
        return 0.0
    blob = b"x" * size
    sid = session_id()
    t0 = time.perf_counter()
    for i in range(n):
        k = "%s:%s:rtt%d" % (NS, sid, i)
        store.set(k, blob)
        store.get(k)
    return (time.perf_counter() - t0) / n


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def cmd_probe():
    store = Store()
    ok = store.ping()
    print("endpoint      %s:%d" % ENDPOINT)
    print("reachable     %s" % ("yes (PONG)" if ok else "NO"))
    if not ok:
        print()
        print("⚑ NOT REACHABLE IS NOT NOT-CONFIGURED.  A refused connection, a")
        print("  stopped quadlet and a wrong endpoint are three causes and this")
        print("  probe distinguishes none of them; cassian publishes")
        print("  `cassian_cache_up` for the authoritative answer.")
        return 1
    info = store.info()
    for k in ("valkey_version", "redis_version", "used_memory_human",
              "maxmemory_human", "maxmemory_policy", "evicted_keys",
              "keyspace_hits", "keyspace_misses"):
        if k in info:
            print("%-13s %s" % (k, info[k]))
    rtt = measure_backend_rtt(store)
    print("rtt           %.6fs per GET+SET (4K payload, measured now)" % rtt)
    print("session       %s" % session_id())
    return 0


# ⚑ THE KEYING FIXTURES ARE MODULE-LEVEL, AND THE REASON IS A REAL LIMIT.  My
# first draft defined them inside `_selftest`, and every one raised `Unkeyable`:
# **pickle stores a class BY QUALIFIED-NAME REFERENCE, not by structure**, so a
# class defined in a function body cannot be serialised at all.  The fixture was
# wrong — but the finding is not, and it bounds the instrument: an argument whose
# TYPE is locally defined (a class in a factory, a closure-scoped record) is
# unkeyable however simple its fields.  Pinned by `local class is unkeyable` below
# so this is a measured property rather than a surprise at injection time.

class _NoRepr:
    """No `__repr__` — `repr()` falls back to an ADDRESS.  `UnifiedCodeword`'s shape
    (`scratch/unified_address.py:170` defines `__str__` only)."""

    def __init__(self, v):
        self.v = v


class _LossyRepr:
    """Renders a SUBSET of the fields its identity depends on — `RSBPF`/`Compound`."""

    def __init__(self, shown, hidden):
        self.shown = shown
        self.hidden = hidden

    def __repr__(self):
        return "Lossy(%s)" % self.shown          # `hidden` never rendered


class _RaisingRepr:
    """`__repr__` raises — `LogicNode`'s base (`mat230-1-4-3b.py:21`)."""

    def __init__(self, v):
        self.v = v

    def __repr__(self):
        raise NotImplementedError("base class")


def _selftest():
    cases = []

    def check(name, cond):
        cases.append((name, bool(cond)))

    # --- keying -----------------------------------------------------------
    sid = "fixed-session"
    k1 = call_key("m.f", ("a",), {}, sid)
    k2 = call_key("m.f", ("a",), {}, sid)
    check("same args -> same key", k1 == k2)
    check("different args -> different key",
          k1 != call_key("m.f", ("b",), {}, sid))
    check("different qualname -> different key",
          k1 != call_key("m.g", ("a",), {}, sid))
    check("different session -> different key",
          k1 != call_key("m.f", ("a",), {}, "other-session"))
    check("key is namespaced", k1.startswith(NS + ":"))

    # ⚑ kwargs ORDER MUST NOT MATTER — a dict preserves insertion order, so an
    # unsorted key reports one call as two and under-reports the hit rate.
    check("kwarg order does not change the key",
          call_key("m.f", (), {"a": 1, "b": 2}, sid) ==
          call_key("m.f", (), {"b": 2, "a": 1}, sid))

    # ⚑ THE CASE THE `repr` DESIGN GOT WRONG.  A class with NO `__repr__` renders
    # as an ADDRESS, so two structurally-identical instances would key differently
    # (and a recycled address would collide two different ones).  This is
    # `UnifiedCodeword`'s exact shape.  Pickle reads the FIELDS, so it is faithful.
    check("address-repr class keys structurally (the UnifiedCodeword case)",
          call_key("m.f", (_NoRepr(1),), {}, sid) ==
          call_key("m.f", (_NoRepr(1),), {}, sid))
    check("address-repr class still distinguishes values",
          call_key("m.f", (_NoRepr(1),), {}, sid) !=
          call_key("m.f", (_NoRepr(2),), {}, sid))
    # ⚑ AND THE DEMONSTRATION THAT `repr` WOULD HAVE FAILED — without it this case
    # asserts only that the fix works, never that the hazard was real.
    check("...where repr() itself is address-shaped (the hazard)",
          "object at 0x" in repr(_NoRepr(1)))

    # ⚑ THE LOSSY-REPR CASE.  `RSBPF`/`Compound` render a SUBSET of the fields
    # their own `__eq__` names, so unequal objects produce one repr — a silent key
    # collision.  Under pickle the hidden field is part of the key.
    a, b = _LossyRepr(1, "x"), _LossyRepr(1, "y")
    check("lossy-repr objects render identically (the hazard)", repr(a) == repr(b))
    check("...but key differently under pickle (the fix)",
          call_key("m.f", (a,), {}, sid) != call_key("m.f", (b,), {}, sid))

    # ⚑ A `__repr__` THAT RAISES MUST NOT REACH THE INTERCEPTOR — `LogicNode`'s
    # base raises `NotImplementedError`.  Pickle never calls it.
    try:
        call_key("m.f", (_RaisingRepr(1),), {}, sid)
        raised = False
    except Exception:
        raised = True
    check("raising __repr__ does not break keying (the LogicNode case)", not raised)

    # ⚑ THE LIMIT THE FIRST FIXTURE FOUND BY BEING WRONG.  Pickle references a
    # class by qualified name, so a LOCALLY-DEFINED type is unkeyable whatever its
    # fields — recorded as a measured bound rather than discovered at injection.
    class _Local:
        def __init__(self, v):
            self.v = v

    try:
        call_key("m.f", (_Local(1),), {}, sid)
        local_keyed = True
    except Unkeyable:
        local_keyed = False
    check("locally-defined class is unkeyable (a bound, not a defect)",
          not local_keyed)

    # ⚑ CYCLES ARE TOTAL, NOT BOUNDED (user: *"We decompose to totality over
    # cycles"*).  Pickle emits MEMOIZE/BINGET back-references, so a self-
    # referential structure keys without a depth limit — there is no capability
    # bound to record.
    cyc = {}
    cyc["self"] = cyc
    try:
        call_key("m.f", (cyc,), {}, sid)
        cyclic_ok = True
    except Exception:
        cyclic_ok = False
    check("cyclic argument keys without a depth bound", cyclic_ok)

    # ⚑ UNPICKLABLE IS A RECORDED OUTCOME, NOT A CRASH.
    try:
        call_key("m.f", (lambda: 1,), {}, sid)
        unkeyable = False
    except Unkeyable:
        unkeyable = True
    except Exception:
        unkeyable = False
    check("unpicklable argument raises Unkeyable specifically", unkeyable)

    # --- scope ------------------------------------------------------------
    check("in-repo file is instrumented",
          in_repo(os.path.join(ROOT, "scratch", "pycodemod.py")))
    check("out-of-repo file is not", not in_repo("/usr/lib/python3.13/os.py"))
    # ⚑ `.venv` SITS UNDER `ROOT` — a naive prefix test would drag libcst's 816k
    # per-run visitor calls into the census.
    check("venv under ROOT is excluded",
          not in_repo(os.path.join(ROOT, ".venv", "lib", "x", "libcst", "_nodes",
                                   "base.py")))
    check("non-.py in repo is excluded",
          not in_repo(os.path.join(ROOT, "README.md")))

    # --- the AST transform ------------------------------------------------
    src = "def f(x):\n    return x + 1\n\nclass C:\n    def m(self):\n        return 2\n"
    tree = instrument(src, "mod")
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names[node.name] = len(node.decorator_list)
    check("module-level def is decorated", names.get("f") == 1)
    check("method is decorated", names.get("m") == 1)

    # ⚑ THE QUALNAME MUST CARRY THE CLASS, or two `m`s in one module collide into
    # one ledger row and the ranking sums unrelated work.
    quals = [d.args[0].value
             for node in ast.walk(tree)
             if isinstance(node, ast.FunctionDef)
             for d in node.decorator_list
             if isinstance(d, ast.Call)]
    check("method qualname includes the class", "mod.C.m" in quals)
    check("function qualname is module-scoped", "mod.f" in quals)

    # ⚑ THE INSTRUMENTED TREE MUST ACTUALLY COMPILE AND RUN — a transform that
    # produces an unexecutable tree would fail at import time in every consumer,
    # and `fix_missing_locations` is the step most likely to be silently omitted.
    sys.modules.setdefault(_HOOK_MODULE, sys.modules[__name__])
    ns = {}
    try:
        exec(compile(tree, "<test>", "exec"), ns)
        ran = ns["f"](1) == 2
    except Exception:
        ran = False
    check("instrumented module compiles and runs", ran)

    # ⚑ AND THE WRAPPER MUST RECORD.  A decorator that compiles but never reaches
    # the ledger is the guard-that-measures-nothing shape.
    before = LEDGER.row("mod.f")["ncalls"]
    ns["f"](5)
    check("a call reaches the ledger", LEDGER.row("mod.f")["ncalls"] > before)

    # --- the ranking ------------------------------------------------------
    led = Ledger()
    for _ in range(10):
        led.record("hot", "hits", 0.010)
    led.record("hot", "misses", 0.010)
    for _ in range(10):
        led.record("cold", "misses", 0.010)
    ranked = {r["qualname"]: r for r in led.ranked()}
    # ⚑ THE COLUMN A WALL-CLOCK PROFILE CANNOT SHOW.  Both functions cost the same
    # total time; only the repeat rate separates them, and that separation IS the
    # instrument's reason to exist.
    check("equal-cost functions rank by recurrence",
          ranked["hot"]["saving_s"] > ranked["cold"]["saving_s"])
    check("a never-repeating function has zero predicted saving",
          ranked["cold"]["saving_s"] == 0)
    check("hit rate excludes unknown/unkeyable from its denominator",
          abs(ranked["hot"]["hit_rate"] - 10 / 11) < 1e-9)

    # ⚑ A NEGATIVE SAVING MUST BE REPRESENTABLE.  If serving costs more than
    # deriving, a cache is a REGRESSION; a ranking that clamps at zero would
    # silently recommend it.
    led2 = Ledger()
    for _ in range(10):
        led2.record("cheap", "hits", 0.000001)
    check("a function cheaper than the backend ranks negative",
          led2.ranked(overhead=0.0, backend_rtt=0.001)[0]["saving_s"] < 0)

    # --- RESP -------------------------------------------------------------
    st = Store()
    check("RESP encodes a command", st._cmd("GET", "k") == b"*2\r\n$3\r\nGET\r\n$1\r\nk\r\n")

    # ⚑ nil AND AN ERROR ARE DIFFERENT OUTCOMES.  A store that cannot answer is
    # not a miss; collapsing them reports a broken cache as a 0% hit rate.
    class _Dead:
        def recv(self, n):
            raise OSError("refused")

        def sendall(self, b):
            raise OSError("refused")
    st.sock = _Dead()
    check("an unreachable store returns None, not a miss", st.get("k") is None)
    check("store errors are counted", st.errors == 1)

    ok = sum(1 for _, c in cases if c)
    for name, c in cases:
        if not c:
            print("  FAIL %s" % name)
    print("selftest: %d/%d" % (ok, len(cases)))
    return ok == len(cases)


def main(argv):
    known = {"--probe", "--selftest", "--run"}
    if not argv or argv[0] not in known:
        print(__doc__)
        return 2
    mode = argv[0]
    if mode == "--selftest":
        return 0 if _selftest() else 1
    if mode == "--probe":
        return cmd_probe()
    if mode == "--run":
        print("--run is not yet wired; --probe and --selftest are.")
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
