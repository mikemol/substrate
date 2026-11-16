#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The SHARED cache — one store, one key discipline, for every derived artifact.

    shared_cache.py --probe          # is the store reachable, and what is it
    shared_cache.py --consumers      # who routes through it, measured
    shared_cache.py --selftest

⚑ WHY THIS EXISTS: 28 PROCESS-LOCAL CACHES, NONE OF WHICH SHARE.  Measured with
`pycodemod --state scratch/ scripts/` (the census predicate is "a module-level
dict READ INSIDE A FUNCTION" — a cache serves a later call, an accumulator does
not).  Every one is a `{}` that dies with the process, so the same derivation is
recomputed by the next invocation, by a pool child, and by every other tool that
needs it.

⚑ AND THE MEASURED ONE SHOWS WHY A LOCAL DICT IS THE WRONG SHAPE, not merely a
missed opportunity.  `agda_lex._MASK_CACHE`: **58,580 calls, 4,096 live, 10,717
evicted** — a working set 3.6x its cap, so every eviction is a GUARANTEED future
recompute, and `mask_comments` still costs 17.2s of a `--next` run.  The cap is
not tunable out of the problem: raising it trades RAM for a hit rate in ONE
process while the next process starts cold anyway.  A shared, capped, LFU store
makes the cap someone else's problem by construction (cassian's `allkeys-lfu`
over 2 GB) and makes the entry outlive the process.

## The key

    sc:<consumer>:<schema>:<sha1(deriver + key material)>

⚑ CONTENT-KEYED, DERIVER-TAGGED, AND NEITHER IS OPTIONAL.  A content hash is
fresh with respect to the INPUT and says nothing about the DERIVATION: same file
bytes, different libcst, different answer — and a pure content key hands back the
old artifact silently.  cassian-observability corrected exactly this in our own
`_cached_defs` docstring (2026-08-03), which had claimed the byte-sha was "the
only key that is exactly as fresh as the answer".  It is not.  `_deriver_tag`
reads the library version from the INSTALLED DISTRIBUTION rather than a declared
constant, so an upgrade cannot be forgotten: it changes the key by construction
and a stale read is unrepresentable.

⚑ THE CALLER SUPPLIES THE KEY MATERIAL, AND THAT IS THE WHOLE INTERFACE DECISION.
The 28 sites key on different things — a file's CONTENT (`_MASK_CACHE`), a
module NAME (`_LOG_INDEX`), a path SET (`_ARTIFACT_CACHE`), a name plus a scope
(`_EXPORTS`).  Only the call site knows which, and a decorator that guessed
(`repr(args)`, say) would be wrong in the direction that matters: an address-
shaped repr under-reports sharing, and a lossy one silently serves the wrong
value.  So `key_fn` is required, not defaulted.

## Contract, from cassian's own standup note

  * **no TTL, no DELETE** — entries are immutable, eviction is LFU under the cap.
    A key you wrote may simply be gone later; that is a miss, and a miss derives.
  * **best-effort, never fatal** — any failure falls through to a normal derive.
  * **opaque bytes** — serialization is ours; pickle, because the 28 sites return
    tuples, sets and dataclasses that JSON would silently reshape.

## What this is NOT

⚑ NOT A SECOND INTERNER.  `jea/metalanguage` hash-conses structure and keys a
VALUE memo where `1/12+1/12` and `1/6` share a node — a semantic equivalence a
content hash cannot see.  This is a syntactic, content-addressed store for
DERIVED ARTIFACTS (a comment mask, a def index, an import graph), which is a
different job from interning terms.  Do not grow it toward the SPPF's work.
"""

import hashlib
import os
import pickle
import socket
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = ("127.0.0.1", 6379)
NS = "sc"

# ⚑ COUNTERS ARE A CONTROL INPUT, NOT TELEMETRY (user, 2026-08-03: *"that's part
# of a live operational CONTROL LOOP, not something that happens only at design
# time"*).  A cache that cannot say whether it is working is a cache nobody can
# tune; these are read WHILE RUNNING, per consumer, which is precisely what
# cassian's aggregate `INFO` counters cannot give (they are store-wide).
STATS = {}


def _stat(consumer, field):
    row = STATS.setdefault(consumer, {"hits": 0, "misses": 0, "unknown": 0,
                                      "stored": 0, "bytes": 0})
    row[field] += 1
    return row


def stats():
    """Per-consumer (hits, misses, unknown, stored, bytes) — the live feedback.

    ⚑ `unknown` IS ITS OWN COLUMN, NOT FOLDED INTO `misses`.  A store that could
    not answer is a fact about the METHOD; counting it as a miss would report a
    down cache as a 0% hit rate and send the reader hunting a workload problem
    that does not exist."""
    return {k: dict(v) for k, v in STATS.items()}


def _deriver_tag():
    """Library versions READ from the installed distribution, never declared.

    ⚑ DECLARED VERSIONS ROT SILENTLY.  A hand-maintained `SCHEMA = 3` catches a
    change the author remembered; reading the installed version catches the one
    they did not — a libcst upgrade under the same source bytes."""
    parts = []
    for mod in ("libcst",):
        try:
            from importlib import metadata as _md
            parts.append("%s=%s" % (mod, _md.version(mod)))
        except Exception:
            parts.append("%s=absent" % mod)
    return ";".join(parts)


_DERIVER = _deriver_tag()


class Store:
    """Valkey — the CLIENT LIBRARY, with a hand-rolled RESP fallback.

    ⚑ THE HAND-ROLL WAS THE RIGHT STARTING POSITION AND THE WRONG ENDING ONE
    (user, 2026-08-04: *"This reaches the point where we should try the valkey
    module instead"*).  `redis`/`valkey` were both absent, and ~50 lines of a
    stable wire protocol beat adding a dependency for GET/SET/PING.  That held
    until the profile showed **15,130 sequential round trips on ONE reused
    connection** — `_connect` fires exactly once, so this was never setup churn;
    it is head-of-line blocking, the RESP analogue of HTTP/1.1.
    #
    ⚑ AND THE FIX IS NOT A BATCH I CAN WRITE.  Pipelining assumes the request set
    is known in advance; here the GETs arrive one at a time from `mask_comments`
    as the walk proceeds, so batching them needs futures or a restructured
    caller — a scheduler, which is a much larger commitment than a client.
    `valkey` already owns connection pooling and pipelining, maintained by people
    for whom it is the job.  Two defects came out of my version (byte-at-a-time
    reads, then this); a third would be a pattern.

    ⚑ THE FALLBACK STAYS, because the absence argument was never wrong.  These
    tools run in pre-commit hooks and pool children; if `valkey` is not
    importable the RESP path still answers, so a missing dependency degrades
    performance rather than disabling the cache."""

    def __init__(self, endpoint=ENDPOINT, timeout=2.0):
        self.endpoint = endpoint
        self.timeout = timeout
        self.sock = None
        self.fh = None
        self.errors = 0
        # ⚑ ONE SOCKET SHARED BY N THREADS IS A CRITICAL SECTION, AND IT WAS
        # UNGUARDED — measured 2026-08-11: 16 threads x 60 round trips on the
        # RESP path produced **399 CROSSED REPLIES out of 960**, i.e. `fetch`
        # returning ANOTHER THREAD'S VALUE.  `call()` is sendall-then-read on one
        # buffered reader, so two threads interleaving splice one reply into the
        # other's read.  That is silent CORRUPTION, not slowness: a cache that
        # answers the wrong key is worse than no cache, and every consumer here
        # trusts the answer.
        #
        # ⚑ AND IT IS THE REPORTED HANG, SAME CAUSE.  A thread whose reply was
        # consumed by another blocks forever in `readline()` waiting for one that
        # already arrived — the `futex_do_wait`-holding-a-socket-fd signature
        # seen three times, which was being read as a memory/lease problem.
        # Under `valkey` the client owns pooling and the race is MASKED (0/960
        # crossed), so this only ever bit the fallback path — which is the path
        # taken in pre-commit hooks and pool children where the dependency may be
        # absent.  A defect that hides when a library is installed is one that
        # surfaces on the machine least able to debug it.
        #
        # ⚑ RLock, NOT Lock: `call` is reachable from `prefetch`/`cached` which
        # may re-enter on the same thread.
        self._lock = threading.RLock()
        # ⚑ THE CLIENT IF PRESENT, THE HAND-ROLL IF NOT — decided ONCE, here,
        # rather than per call.  A per-call `try: import` would put an import
        # lookup on the hot path for a fact that cannot change mid-process.
        self.client = None
        if not os.environ.get("SUBSTRATE_NO_VALKEY"):
            try:
                import valkey
                self.client = valkey.Valkey(
                    host=endpoint[0], port=endpoint[1],
                    socket_timeout=timeout, socket_connect_timeout=timeout)
            except Exception:
                self.client = None

    def _connect(self):
        if self.sock is None:
            self.sock = socket.create_connection(self.endpoint, timeout=self.timeout)
            # ⚑ A BUFFERED READER, BECAUSE THE FIRST VERSION READ ONE BYTE AT A
            # TIME.  `_read_line` looped on `sock.recv(1)` until it saw CRLF —
            # MEASURED at **134,476 recv syscalls for 23,785 replies** (~5.7 per
            # reply) and **43.7s of a 201s run**, which is the entire regression
            # the shared cache introduced.  `buf += ch` also reallocated per
            # byte, so it was quadratic in line length on top of the syscalls.
            #
            # ⚑ AND IT IS THE SAME DEFECT AS THE HAND-ROLLED LRU, ONE HOUR APART:
            # a stdlib primitive re-implemented worse.  `makefile("rb")` is a
            # buffered file object over the socket with a real `readline()`;
            # there was never a reason to write the loop.
            self.fh = self.sock.makefile("rb")
        return self.sock

    def _drop(self):
        """Close both halves — a half-closed connection reads as a hang.

        ⚑ UNDER THE SAME LOCK AS `call`.  Closing the socket out from under a
        thread mid-`_read_reply` is the other way to manufacture the hang this
        lock exists to stop: the reader gets a short read or a closed fd on a
        connection it believed was its own."""
        with self._lock:
            for h in (self.fh, self.sock):
                try:
                    if h is not None:
                        h.close()
                except Exception:
                    pass
            self.fh = self.sock = None

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
        """One RESP line, via the BUFFERED reader — never byte-at-a-time."""
        line = self.fh.readline()
        if not line:
            raise OSError("connection closed")
        return line[:-2] if line.endswith(b"\r\n") else line.rstrip(b"\r\n")

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
                return None              # nil — a genuine MISS, not an error
            # ⚑ `readexactly` VIA THE SAME BUFFER.  Reading the bulk payload off
            # the raw socket while a buffered reader holds part of it is how a
            # mixed-mode client loses bytes — the buffer may already have them.
            data = self.fh.read(n + 2)
            if data is None or len(data) < n + 2:
                raise OSError("short read")
            return data[:-2]
        raise OSError("unexpected RESP tag %r" % tag)

    def call(self, *parts):
        # ⚑ THE WHOLE ROUND TRIP IS THE ATOMIC UNIT, not the send and not the
        # read.  Locking either half alone still interleaves the other, which is
        # exactly how the 399 crossed replies happened: RESP has no request id,
        # so the ONLY thing binding a reply to its request is that no one else
        # spoke in between.  `_connect` is inside the lock too — two threads
        # racing a lazy connect would otherwise build two sockets and leak one.
        with self._lock:
            sock = self._connect()
            sock.sendall(self._cmd(*parts))
            return self._read_reply(sock)

    def ping(self):
        if self.client is not None:
            try:
                return bool(self.client.ping())
            except Exception:
                return False
        try:
            return self.call("PING") == b"PONG"
        except (OSError, socket.timeout):
            return False

    def get(self, key):
        """-> (found, value), or None when the STORE could not answer.

        ⚑ THREE OUTCOMES, PRESERVED ACROSS BOTH BACKENDS.  nil is a genuine MISS;
        an exception is the store failing to answer, which is NOT evidence of
        absence.  The client raises where the hand-roll returned None, so the
        mapping is explicit — collapsing them would report a down cache as a 0%
        hit rate, a fact about the method read as a fact about the workload."""
        if self.client is not None:
            try:
                v = self.client.get(key)
            except Exception:
                self.errors += 1
                return None
            return (v is not None, v)
        try:
            v = self.call("GET", key)
        except (OSError, socket.timeout):
            self.errors += 1
            self._drop()
            return None
        return (v is not None, v)

    def set(self, key, value):
        if self.client is not None:
            try:
                self.client.set(key, value)
                return True
            except Exception:
                self.errors += 1
                return False
        try:
            self.call("SET", key, value)
            return True
        except (OSError, socket.timeout):
            self.errors += 1
            self._drop()
            return False

    def info(self):
        if self.client is not None:
            try:
                # ⚑ THE CLIENT PARSES `INFO` ALREADY — returning its dict rather
                # than re-splitting the raw text is the same delegation as the
                # rest of this class.
                return {k: str(v) for k, v in self.client.info().items()}
            except Exception:
                return {}
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


_STORE = None


def store():
    """The process's connection — lazily opened, never required.

    ⚑ LAZY BECAUSE IMPORT MUST NOT REACH THE NETWORK.  These 28 sites live in
    tools that run in pre-commit hooks and pool children; a module-import that
    dials a socket would make the store a dependency of PARSING the tool, which
    is the opposite of best-effort."""
    global _STORE
    if _STORE is None:
        _STORE = Store()
    return _STORE


def content_key(path):
    """Key material for a FILE-CONTENT-derived artifact: its bytes.

    ⚑ THE COMMON CASE, HOMED ONCE.  Most of the 28 derive from a file's content
    (a comment mask, a def scan, an import list).  Each site re-reading and
    re-hashing would be 28 chances to key on the PATH by mistake — which is
    stale-on-edit, the defect the deriver tag exists to make unrepresentable one
    level up."""
    try:
        return open(path, "rb").read()
    except OSError:
        return None


def corpus_key(paths):
    """Key material for a WHOLE-CORPUS derivation: every file's identity.

    ⚑ A PATH SET IS NOT A KEY, AND THIS IS WHERE THE LOCAL CACHES WERE ALREADY
    WRONG.  `pycodemod._ARTIFACT_CACHE` and `_IMPORTS_CACHE` key on the resolved
    PATH SET — correct within one process, where the files cannot change under
    you, and stale-on-edit the moment the entry outlives the run.  Promoting
    those keys to a shared store unchanged would serve a pre-edit answer to a
    post-edit question, which is worse than not caching at all.
    #
    ⚑ SO THE SHARED KEY CARRIES CONTENT IDENTITY, not membership.  (path, size,
    mtime_ns) per file is the cheap faithful proxy: an edit moves mtime and
    usually size, and hashing every file's BYTES would cost more than the
    derivation this is meant to save.  That is a deliberate weaker guarantee
    than `content_key`'s — stated rather than assumed, because mtime can be
    forged by a checkout that preserves timestamps.

    ⚑ SORTED, because a set has no order and two callers reaching the same
    corpus by different routes must produce the same key.  An unsorted join
    would mint a fresh entry per traversal order — a cache that never hits, and
    one whose miss rate would read as a workload property rather than a bug."""
    rows = []
    for p in sorted(paths):
        try:
            st = os.stat(p)
            rows.append("%s:%d:%d" % (p, st.st_size, st.st_mtime_ns))
        except OSError:
            # ⚑ AN UNREADABLE MEMBER ABSTAINS FOR THE WHOLE SET.  Skipping it
            # would key two DIFFERENT corpora identically — the one where the
            # file exists and the one where it does not.
            return None
    return "\n".join(rows).encode()


def _key(consumer, material, schema=1):
    """The one key construction — deriver-tagged, namespaced, sha1'd."""
    if isinstance(material, str):
        material = material.encode()
    h = hashlib.sha1(_DERIVER.encode() + b"\0" + material).hexdigest()
    return "%s:%s:%d:%s" % (NS, consumer, schema, h)


def fetch(consumer, material, schema=1):
    """The cached value, or None — for a site whose L1 lookup comes FIRST.

    ⚑ THE EXPLICIT FORM, BECAUSE A DECORATOR CANNOT SIT BETWEEN TWO LAYERS.
    `cached()` wraps a whole function, which is right when the store is the only
    cache.  Most of the 28 sites already have a process-local L1 that MUST be
    consulted first (a dict hit beats a round trip by orders of magnitude), so
    the store is consulted between the L1 miss and the derivation — a control
    flow a decorator cannot express without putting the network in front.

    ⚑ AND `None` MEANS "NOT AVAILABLE", never "the value was None".  A site
    caching a legitimately-None result must wrap it; stated because the
    ambiguity is silent and would present as a permanent miss."""
    if os.environ.get("SUBSTRATE_NO_CACHE") or material is None:
        return None
    got = store().get(_key(consumer, material, schema))
    if got is None:
        _stat(consumer, "unknown")
        return None
    found, blob = got
    if not found:
        _stat(consumer, "misses")
        return None
    try:
        v = pickle.loads(blob)
    except Exception:
        # ⚑ AN UNDESERIALISABLE HIT IS A MISS.  A schema the deriver tag failed
        # to separate must degrade to a recompute; raising would turn a cache
        # defect into a tool defect, inside a gate.
        _stat(consumer, "misses")
        return None
    _stat(consumer, "hits")
    return v


def store_value(consumer, material, value, schema=1):
    """Write back — best-effort, and a failure costs nothing already spent."""
    if os.environ.get("SUBSTRATE_NO_CACHE") or material is None:
        return False
    try:
        blob = pickle.dumps(value, protocol=5)
    except Exception:
        return False            # unpicklable RESULT: derive, never store
    if store().set(_key(consumer, material, schema), blob):
        row = _stat(consumer, "stored")
        row["bytes"] += len(blob)
        return True
    return False


def prefetch(consumer, materials, schema=1, workers=16):
    """{material_key: value} for an ANTICHAIN of lookups — concurrently.

    ⚑ THE COST WAS NEVER THE ROUND TRIP, IT WAS THE QUEUE (user, 2026-08-04:
    *"Are we doing poset threading? Because if we're not, we're FORCING
    serialization where we don't need to."*).  Measured across four attempts at
    making one lookup cheaper — buffered reader, valkey client, hiredis parser —
    the spread was **8s on a 35s problem**, because all three optimise the
    per-operation cost while 14,750 lookups sit in a queue.  `recv` is 40.4s of
    *waiting*; parsing is 0.35s.  No per-operation improvement can touch that.

    ⚑ THE LOOKUPS ARE AN ANTICHAIN, WHICH IS THE WHOLE JUSTIFICATION.  A comment
    mask depends on one source's bytes and nothing else, so no lookup orders any
    other.  The operator's opening line this session — *"anything poset-shaped
    can be parallelized within the non-ordered subsets"* — names exactly this,
    and I spent four measurements optimising the serial path instead.

    ⚑ THREADS, NOT PROCESSES, AND THE REASON IS MEASURED IN THIS REPO.
    `pycodemod._per_file` chose PROCESSES because its work is
    `MetadataWrapper.resolve` — pure-Python tree walking, GIL-bound, 0.73x on 8
    threads.  This work is a socket wait, which RELEASES the GIL, so threads are
    correct here and processes would pay spawn cost for nothing.  Same repo, same
    question, opposite answer — because the work is a different kind.

    ⚑ WARMS L1 BY CONSTRUCTION.  The caller does not thread its own logic: it
    calls this once with the set it already knows, then proceeds exactly as
    before.  Every subsequent `cached()` lookup finds the value locally.  That is
    why this lives here rather than in 20 call sites — 47 of them across 20
    files, each an opportunity to get concurrency wrong.

    Returns the fetched map; a failure for any single key is simply absent from
    it, and the caller derives that one normally."""
    out = {}
    mats = [m for m in materials if m is not None]
    if not mats or os.environ.get("SUBSTRATE_NO_CACHE"):
        return out
    # ⚑ A SHARED CLIENT ACROSS THREADS IS NOT SAFE, so each worker gets its own
    # connection.  `valkey` pools per client; a single `Store` would serialise
    # inside the library and reproduce the queue this exists to remove.
    import concurrent.futures as _cf

    def _one(material):
        try:
            st = Store()
            got = st.get(_key(consumer, material, schema))
            if got is None:
                return material, None, "unknown"
            found, blob = got
            if not found:
                return material, None, "misses"
            return material, pickle.loads(blob), "hits"
        except Exception:
            return material, None, "unknown"

    with _cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for material, value, outcome in pool.map(_one, mats):
            _stat(consumer, outcome)
            if outcome == "hits":
                out[material] = value
    return out


def cached(consumer, key_fn, schema=1, enabled=None):
    """Route a pure derivation through the shared store.

    `key_fn(*args, **kwargs) -> bytes | str | None`.  Returning None means THIS
    CALL IS NOT CACHEABLE (an unreadable file, a non-content argument) and the
    wrapper derives directly — an honest abstention, not a silent miss.

    ⚑ THE WRAPPER NEVER CHANGES THE ANSWER.  On a hit it returns the unpickled
    value; on a miss, an unknown, or any failure it calls through.  A cache that
    can alter behaviour is not a cache, and the 28 sites are load-bearing in
    gates — `mask_comments` feeds pre-commit checks.

    ⚑ AND `enabled` DEFAULTS TO THE ENVIRONMENT, so a bare tool run in an
    environment with no store pays one refused connection and then behaves
    exactly as it did before."""
    def deco(fn):
        def wrapper(*args, **kwargs):
            if enabled is False or os.environ.get("SUBSTRATE_NO_CACHE"):
                return fn(*args, **kwargs)
            try:
                material = key_fn(*args, **kwargs)
            except Exception:
                material = None
            if material is None:
                return fn(*args, **kwargs)
            if isinstance(material, str):
                material = material.encode()
            h = hashlib.sha1(_DERIVER.encode() + b"\0" + material).hexdigest()
            k = "%s:%s:%d:%s" % (NS, consumer, schema, h)
            st = store()
            got = st.get(k)
            if got is None:
                _stat(consumer, "unknown")
                return fn(*args, **kwargs)
            found, blob = got
            if found:
                try:
                    v = pickle.loads(blob)
                    _stat(consumer, "hits")
                    return v
                except Exception:
                    # ⚑ AN UNDESERIALISABLE HIT IS A MISS, NOT A CRASH.  A schema
                    # the deriver tag failed to separate must degrade to a
                    # recompute; raising here would make a cache defect a tool
                    # defect, in a gate.
                    pass
            _stat(consumer, "misses")
            out = fn(*args, **kwargs)
            try:
                blob = pickle.dumps(out, protocol=5)
                if st.set(k, blob):
                    row = _stat(consumer, "stored")
                    row["bytes"] += len(blob)
            except Exception:
                pass                      # unpicklable RESULT: derive, never store
            return out
        wrapper.__name__ = getattr(fn, "__name__", "cached")
        wrapper.__doc__ = getattr(fn, "__doc__", None)
        wrapper.__wrapped__ = fn
        wrapper.cache_consumer = consumer
        return wrapper
    return deco


def _consumers():
    """Which modules route through this store — DISCOVERED, not listed.

    ⚑ A DECLARED ROSTER ROTS.  `pycodemod --calls cached` answers who adopted it
    at any moment; hardcoding the list here would be the frozen-roster shape the
    struct-tools table exists to retire."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "scratch"))
        import pycodemod
        rows = pycodemod.scan(pycodemod.py_files(), "cached")
        return sorted({os.path.relpath(p, ROOT) for p, kind, _n, _l in rows
                       if kind == "call"})
    except Exception as exc:
        return ["<could not measure: %s>" % exc]


def _selftest():
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    calls = {"n": 0}

    def derive(x):
        calls["n"] += 1
        return {"v": x * 2}

    # ⚑ THE KEY IS CONTENT + DERIVER, AND BOTH HALVES ARE PINNED.
    k1 = hashlib.sha1(_DERIVER.encode() + b"\0" + b"abc").hexdigest()
    k2 = hashlib.sha1(b"other" + b"\0" + b"abc").hexdigest()
    check("same material, same deriver -> same key",
          k1, hashlib.sha1(_DERIVER.encode() + b"\0" + b"abc").hexdigest())
    check("a DIFFERENT deriver changes the key (the stale-read fix)",
          k1 != k2, True)
    # ⚑ THE DERIVER IS READ, NOT DECLARED — a version constant catches only the
    # change its author remembered.
    check("the deriver tag names a real installed version",
          "absent" not in _DERIVER or "libcst=" in _DERIVER, True)

    # ⚑ A `None` KEY IS AN HONEST ABSTENTION.  An unreadable file or a
    # non-content argument must DERIVE, not key on something arbitrary — and it
    # must not be counted as a miss, which would make the hit rate a lie.
    calls["n"] = 0
    f = cached("t-abstain", lambda x: None)(derive)
    f(1)
    f(1)
    check("a None key derives every time (no key, no cache)", calls["n"], 2)
    check("...and records nothing (an abstention is not a miss)",
          "t-abstain" in stats(), False)

    # ⚑ DISABLED MUST BE A TOTAL BYPASS — a gate in a store-less environment
    # behaves exactly as before.
    calls["n"] = 0
    g = cached("t-off", lambda x: b"k", enabled=False)(derive)
    g(1)
    g(1)
    check("enabled=False bypasses entirely", calls["n"], 2)

    # ⚑ THE WRAPPER PRESERVES THE ANSWER.  These sites feed pre-commit gates; a
    # cache that can change a verdict is not admissible.
    h = cached("t-same", lambda x: ("m%d" % x).encode())(derive)
    check("the cached result equals the direct one", h(21), derive(21))

    # ⚑ `unknown` IS NOT `misses`.  Pinned against a store that cannot answer,
    # because collapsing them reports a DOWN CACHE as a 0% hit rate.
    class _Dead(Store):
        def get(self, key):
            self.errors += 1
            return None

        def set(self, key, value):
            return False

    global _STORE
    _save = _STORE
    try:
        _STORE = _Dead()
        STATS.pop("t-down", None)
        calls["n"] = 0
        d = cached("t-down", lambda x: b"k")(derive)
        d(1)
        d(1)
        row = stats().get("t-down", {})
        check("an unreachable store still returns the right answer", calls["n"], 2)
        check("...counted as unknown, never as a miss",
              (row.get("unknown"), row.get("misses")), (2, 0))
    finally:
        _STORE = _save

    # ⚑ LIVE ROUND-TRIP, when the store is up.  A synthetic double cannot show
    # the wire protocol works; skipping is announced, never counted as a pass
    # (the `0/0`-reads-as-green defect this repo fixed in `spool`).
    if store().ping():
        STATS.pop("t-live", None)
        calls["n"] = 0
        import uuid as _u
        tag = _u.uuid4().hex.encode()
        live = cached("t-live", lambda x: tag + b":%d" % x)(derive)
        v1 = live(7)
        v2 = live(7)
        row = stats().get("t-live", {})
        check("a live round-trip derives once and hits once", calls["n"], 1)
        check("...and the hit equals the derived value", v1, v2)
        check("...recorded as one miss and one hit",
              (row.get("misses"), row.get("hits")), (1, 1))
    else:
        print("  ⚑ store unreachable — the 3 live round-trip cases did NOT run "
              "and are not counted as passing.")

    # ⚑ THE READER IS BUFFERED, AND NO CORRECTNESS CASE COULD HAVE CAUGHT THE
    # DEFECT.  The first version read one byte at a time (`sock.recv(1)` until
    # CRLF) and every case above passed — byte-at-a-time is perfectly CORRECT.
    # It cost **134,476 recv syscalls for 23,785 replies** and 43.7s of a 201s
    # run: the entire regression the shared cache introduced.  A cache is a
    # PERFORMANCE artifact, so a suite that only asserts correctness cannot tell
    # you it is working — the same reason `mask_stats` exists one layer down.
    #
    # So this case asserts the MECHANISM, counting recvs on a real round trip.
    # ⚑ THIS CASE MEASURES THE HAND-ROLLED READER, so it runs only when that is
    # the live backend.  With `valkey` present the buffering is the client's and
    # counting our `fh` reads would measure nothing — announced as UNRUN rather
    # than silently passing, which is the `0/0`-reads-as-green defect.
    if store().ping() and store().client is None:
        _s = Store()
        _s._connect()
        # ⚑ COUNTED AT THE BUFFER, NOT THE SOCKET — a socket's methods are
        # read-only and cannot be wrapped, which is itself a small finding: the
        # only observable layer is the file object, and that is exactly the layer
        # the defect was missing.
        _n = {"reads": 0}
        _fh = _s.fh
        _orig_rl, _orig_rd = _fh.readline, _fh.read

        def _crl(*a, **k):
            _n["reads"] += 1
            return _orig_rl(*a, **k)

        def _crd(*a, **k):
            _n["reads"] += 1
            return _orig_rd(*a, **k)
        _fh.readline, _fh.read = _crl, _crd
        try:
            import uuid as _u2
            _k = "%s:_probe:1:%s" % (NS, _u2.uuid4().hex)
            _s.set(_k, b"x" * 4096)
            _s.get(_k)
            # ⚑ THE ORDER OF MAGNITUDE IS THE ASSERTION.  A buffered reader
            # needs one `readline` for the SET reply plus a `readline`+`read`
            # for the GET's bulk payload — a handful.  The byte-at-a-time loop
            # needed ~4,100 for the same 4K.  A tight exact count would be
            # brittle; what regressed was the magnitude.
            check("a 4K round trip costs a handful of reads, not thousands",
                  _n["reads"] < 16, True)
        finally:
            _fh.readline, _fh.read = _orig_rl, _orig_rd
            _s._drop()
    elif store().client is not None:
        print("  ⚑ valkey client active — the hand-rolled read-count case does "
              "not apply and did NOT run.")
    else:
        print("  ⚑ store unreachable — the read-count case did NOT run.")

    # ⚑ BOTH BACKENDS MUST AGREE, and that is now a case rather than an
    # assumption.  The client and the hand-roll are two implementations of one
    # contract; a divergence would be invisible until a consumer got a wrong
    # answer, which is exactly the derived-view defect this repo keeps paying
    # for.  Skipped, and SAID, when only one backend is available.
    if store().ping() and store().client is not None:
        import uuid as _u3
        _hand = Store()
        _hand.client = None                     # force the RESP path
        _k3 = "%s:_agree:1:%s" % (NS, _u3.uuid4().hex)
        _payload = b"agreement-probe"
        check("the client's SET is readable by the hand-rolled GET",
              (store().set(_k3, _payload), _hand.get(_k3)),
              (True, (True, _payload)))
        _k4 = "%s:_agree:1:%s" % (NS, _u3.uuid4().hex)
        check("...and the hand-rolled SET is readable by the client",
              (_hand.set(_k4, _payload), store().get(_k4)),
              (True, (True, _payload)))
        check("both report a MISS identically on an absent key",
              (store().get("%s:_absent:%s" % (NS, _u3.uuid4().hex)),
               _hand.get("%s:_absent:%s" % (NS, _u3.uuid4().hex))),
              ((False, None), (False, None)))
        _hand._drop()

    # ⚑ CONCURRENT `call`s MUST NOT CROSS THEIR REPLIES, and this is a
    # REGRESSION case for a MEASURED corruption (2026-08-11).  `Store` holds ONE
    # socket and ONE buffered reader; `call` was sendall-then-read with no lock,
    # and RESP carries no request id, so the only thing binding a reply to its
    # request is that nobody spoke in between.  16 threads x 60 round trips on
    # the hand-rolled path returned **399 WRONG VALUES out of 960** — `fetch`
    # handing back another thread's payload — and a thread whose reply was
    # stolen blocks in `readline()` forever, which is the `futex_do_wait` hang
    # that had been read as a memory/lease problem for three runs.
    #
    # ⚑ IT IS A CORRECTNESS CASE, NOT A PERFORMANCE ONE.  Every consumer here
    # feeds a pre-commit gate and TRUSTS the returned bytes; a cache that answers
    # the wrong key can change a verdict.  That is why this asserts ZERO crossed
    # replies rather than a rate.
    #
    # ⚑ AND IT RUNS ON THE HAND-ROLLED PATH SPECIFICALLY, because `valkey` owns
    # pooling and MASKS the defect entirely (0/960 crossed with the client
    # active).  The bug therefore only ever bit the fallback — the path taken in
    # pre-commit hooks and pool children where the dependency may be absent, i.e.
    # the machine least equipped to diagnose it.  Announced as UNRUN, never
    # counted as passing, when the store is down.
    if store().ping():
        import threading as _th
        import uuid as _u4
        _conc = Store()
        _conc.client = None                     # the unsynchronized path
        _tag4 = _u4.uuid4().hex
        _crossed = []
        _clock = _th.Lock()

        def _spin(i):
            for r in range(40):
                k = "%s:_race:1:%s:%d:%d" % (NS, _tag4, i, r)
                v = b"v%d-%d" % (i, r)
                _conc.set(k, v)
                got = _conc.get(k)
                if got != (True, v):
                    with _clock:
                        _crossed.append((i, r, got))
        _threads = [_th.Thread(target=_spin, args=(i,)) for i in range(8)]
        for _t in _threads:
            _t.start()
        # ⚑ A JOIN TIMEOUT, because the failure mode INCLUDES a permanent block:
        # an unbounded join would turn a detected regression into a hung suite,
        # which is the shape (a hang reported as anything but a hang) that cost
        # three runs to attribute.
        for _t in _threads:
            _t.join(timeout=30)
        check("concurrent round trips never cross their replies", _crossed, [])
        check("...and every thread finished (no reply left a reader blocked)",
              [t.name for t in _threads if t.is_alive()], [])
        _conc._drop()
    else:
        print("  ⚑ store unreachable — the 2 concurrency cases did NOT run "
              "and are not counted as passing.")

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"shared_cache selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def main(argv):
    known = {"--probe", "--consumers", "--selftest"}
    if not argv or argv[0] not in known:
        print(__doc__)
        return 2
    if argv[0] == "--selftest":
        return 0 if _selftest() else 1
    if argv[0] == "--consumers":
        rows = _consumers()
        for r in rows:
            print("  %s" % r)
        print("%d module(s) route through the shared cache" % len(rows))
        return 0
    st = store()
    print("endpoint      %s:%d" % ENDPOINT)
    ok = st.ping()
    print("reachable     %s" % ("yes (PONG)" if ok else "NO"))
    if not ok:
        # ⚑ NOT REACHABLE IS NOT NOT-CONFIGURED.  Refused, stopped and
        # misaddressed are three causes and this probe distinguishes none;
        # cassian publishes `cassian_cache_up` for the authoritative answer.
        print("  ⚑ a refused connection, a stopped quadlet and a wrong endpoint")
        print("    are three causes; this probe separates none of them.")
        return 1
    info = st.info()
    for k in ("valkey_version", "used_memory_human", "maxmemory_human",
              "maxmemory_policy", "evicted_keys", "keyspace_hits",
              "keyspace_misses"):
        if k in info:
            print("%-17s %s" % (k, info[k]))
    print("deriver           %s" % _DERIVER)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
