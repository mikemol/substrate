#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""What does a cached CST artifact actually cost? — the footprint cassian asked for.

⚑ THIS IS A MEASUREMENT, NOT A CACHE.  cassian-observability's ask (2026-08-03)
was: *"measure your serialized artifact footprint once you've picked a format —
not as a spec, but as evidence to sanity-check the maxmemory cap."*  Picking a
format requires knowing what each candidate costs, and I had no numbers — only my
claim to them that "a MetadataWrapper is not JSON-able", which is true and turns
out to be beside the point.

⚑ AND THE CLAIM I SENT THEM WAS ASKING THE WRONG QUESTION.  I told them the
expensive artifact is "the parse tree plus resolved position metadata".  Reading
`scan()`'s own comment: *"MetadataWrapper resolves a position for EVERY node in
the file; over an 85-file corpus of 2000-line tools that exceeded a 120s budget"*
— so the cost is the POSITION RESOLUTION, and the parse is the cheaper half.
Nobody needs the tree back; what a mode needs is either its own small answer or
the position map.  Three candidates, measured here rather than argued:

    parse      cst.parse_module           — how much of the cost is parsing?
    positions  + MetadataWrapper.resolve  — how much is the position pass?
    answer     the mode's own rows        — what a derived-view cache would hold

Run:  python3 scratch/cache_probe.py [paths...]
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pycodemod as P

try:
    import libcst as cst
except Exception:
    cst = None


def rtt(n=200):
    """(ok, median_ms) for a Valkey GET round-trip — the WALL-TIME axis.

    ⚑ STORAGE IS NOT THE ONLY RESOURCE, AND IT IS NOT THE SCARCE ONE (user,
    2026-08-03: *"there is CPU time, there is wall time, there is task RAM, and
    there is cache storage. The cheapest is whichever resource is not the
    bottleneck"*).  My first reading collapsed four axes into the storage ratio
    (17.6 MB vs 201 KB, 90x) and called answers "cheaper" — against a 2 GB cap
    that is 0.9%, i.e. a difference in the ABUNDANT resource.

    A shared store trades local CPU for network latency, and the trade only pays
    if a round-trip is cheap against re-derivation.  Measured, not assumed:
    stdlib RESP, no client dependency, the same shape cassian's own collector
    uses.

    ⚑ AND PARALLELISM CUTS ACROSS ALL FOUR AXES RATHER THAN BEING A FIFTH (user,
    same exchange: *"not to mention parallelism"*).  It is WHY the axes disagree:
    concurrent round-trips are throughput-bound, so per-file latency largely
    vanishes from wall time — while N workers each materializing a position map
    MULTIPLY resident memory, which is the axis membudget's semaphore exists to
    arbitrate.  So parallelism improves the wall-time case for a shared store and
    WORSENS the RAM case for position maps: the two unmeasured axes move in
    opposite directions under it, and a serial measurement cannot see either.

    The files are an ANTICHAIN — nothing in `py_files()` depends on another
    entry — so this is trivially parallel and every number I took before this was
    serial."""
    import socket
    import statistics
    try:
        s = socket.create_connection(("127.0.0.1", 6379), 3)
    except OSError as e:
        return False, "unreachable: %s" % e
    try:
        s.sendall(b"*1\r\n$4\r\nPING\r\n")
        if not s.recv(64).startswith(b"+PONG"):
            return False, "no PONG"
        key = b"substrate:probe:rtt"
        s.sendall(b"*3\r\n$3\r\nSET\r\n$%d\r\n%s\r\n$4\r\nx\x00y\x00\r\n"
                  % (len(key), key))
        s.recv(64)
        req = b"*2\r\n$3\r\nGET\r\n$%d\r\n%s\r\n" % (len(key), key)
        ts = []
        for _ in range(n):
            t0 = time.perf_counter()
            s.sendall(req)
            s.recv(256)
            ts.append((time.perf_counter() - t0) * 1000)
        return True, statistics.median(ts)
    except Exception as e:
        return False, "error: %s" % e
    finally:
        s.close()


def rtt_concurrent(workers=8, per=100):
    """(ok, ms_per_op_effective) — round-trips under CONCURRENCY.

    ⚑ SERIAL RTT MEASURES LATENCY; CONCURRENT RTT MEASURES THROUGHPUT, and only
    the second is what a parallel sweep pays.  Reporting the serial median as
    "the cost of a shared store" would size the design against a bottleneck the
    real workload does not have — the files are an antichain, so the round-trips
    overlap."""
    import socket
    import concurrent.futures as cf

    def one(_i):
        try:
            s = socket.create_connection(("127.0.0.1", 6379), 3)
        except OSError:
            return None
        try:
            key = b"substrate:probe:rtt"
            req = b"*2\r\n$3\r\nGET\r\n$%d\r\n%s\r\n" % (len(key), key)
            for _ in range(per):
                s.sendall(req)
                s.recv(256)
            return per
        except Exception:
            return None
        finally:
            s.close()

    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        got = list(pool.map(one, range(workers)))
    dt = time.perf_counter() - t0
    ops = sum(g for g in got if g)
    if not ops:
        return False, "no worker completed"
    return True, (dt * 1000) / ops


def gil_scaling(paths, workers=8):
    """(serial_s, thread_s, speedup) for the DERIVATION — is it GIL-bound?

    ⚑ THE TWO HALVES OF THIS PROBE NEED DIFFERENT VEHICLES, AND I NEARLY MEASURED
    ONE WITH THE OTHER'S (user, 2026-08-03: *"don't forget GIL impact, if what
    you're doing is GIL-sensitive"*).  `rtt_concurrent` uses threads and that is
    CORRECT — socket I/O releases the GIL, so round-trips genuinely overlap.  But
    `MetadataWrapper.resolve` is pure-Python tree walking: GIL-BOUND, so eight
    threads give ~1x, not 8x.  Reporting a thread-pool speedup for the derivation
    would have claimed a parallelism that does not exist.

    ⚑ AND IT CHANGES THE RAM ARITHMETIC TOO.  Threads SHARE a heap (8 position
    maps, one interpreter); processes do not (8 maps + 8 interpreters).  My first
    "-j8 resident" line multiplied by 8 without saying which — a number that is
    wrong for one vehicle and right for the other, stated as if the choice did
    not exist.

    Measured here so the design reads a fact rather than my expectation."""
    import concurrent.futures as cf

    sample = list(paths)[:workers * 2]
    if not sample:
        return (0.0, 0.0, 0.0)

    def derive(p):
        try:
            src = open(p, encoding="utf-8").read()
            mod = cst.parse_module(src)
            w = cst.metadata.MetadataWrapper(mod)
            return len(w.resolve(cst.metadata.PositionProvider))
        except Exception:
            return 0

    t0 = time.perf_counter()
    for p in sample:
        derive(p)
    serial = time.perf_counter() - t0

    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(derive, sample))
    threaded = time.perf_counter() - t0

    return (serial, threaded, serial / max(threaded, 1e-9))


def _derive_count(p):
    """Module-level so a PROCESS pool can pickle it."""
    try:
        import libcst as _c
        src = open(p, encoding="utf-8").read()
        w = _c.metadata.MetadataWrapper(_c.parse_module(src))
        return len(w.resolve(_c.metadata.PositionProvider))
    except Exception:
        return 0


def proc_scaling(paths, workers=8):
    """(serial_s, proc_s, speedup) — does a PROCESS pool actually win?

    ⚑ THE POOL IS THE COMPOSITION, NOT AN ALTERNATIVE (user, 2026-08-03: *"you
    may also wish to have a worker proc pool. Then you can use threads or fibers
    or whatever you like effectively in the thing that dispatches to them"*).  I
    had been reading GIL-bound-derivation and threadable-I/O as a fork to pick
    between; they are two layers.  Processes for the derivation (real
    parallelism), threads in the DISPATCHER (socket I/O and coordination, both
    of which release the GIL).

    ⚑ AND IT TURNS THE RAM NUMBER FROM A COST INTO A TUNABLE.  A worker derives,
    serializes, returns, and RELEASES the map — so peak resident is
    `workers x one map`, bounded by pool size, which is precisely the knob
    membudget's semaphore already arbitrates.  I reported "131 MB at -j8" as a
    cost of parallelism; it is a dial, and the build already owns the dial.

    Measured rather than assumed, because a process pool is not free: returning
    a result crosses a pickle boundary, and for a 380 KB position blob that cost
    is real.  This returns a COUNT (cheap to pickle) so the number isolates the
    parallel speedup from the transfer — the transfer is measured separately by
    `pos-blob`, and conflating them would credit the pool with a cost it has."""
    import concurrent.futures as cf

    sample = list(paths)[:workers * 2]
    if not sample:
        return (0.0, 0.0, 0.0)

    t0 = time.perf_counter()
    for p in sample:
        _derive_count(p)
    serial = time.perf_counter() - t0

    t0 = time.perf_counter()
    try:
        with cf.ProcessPoolExecutor(max_workers=workers) as pool:
            list(pool.map(_derive_count, sample))
        procs = time.perf_counter() - t0
    except Exception:
        return (serial, 0.0, 0.0)

    return (serial, procs, serial / max(procs, 1e-9))


def probe(paths):
    """[(rel, bytes_src, t_parse, t_pos, n_nodes, b_pickle, b_answer)] per file."""
    rows = []
    for p in paths:
        try:
            src = open(p, encoding="utf-8").read()
        except OSError:
            continue
        t0 = time.perf_counter()
        try:
            mod = cst.parse_module(src)
        except Exception:
            continue
        t_parse = time.perf_counter() - t0

        # ⚑ TASK RAM IS THE FOURTH AXIS AND WAS UNMEASURED.  membudget's whole
        # discipline exists because resident memory is the binding constraint on
        # this box — a cache that trades storage for RSS is trading an abundant
        # resource for the scarce one.  `tracemalloc` attributes the allocation
        # to the position pass specifically, which a maxRSS delta cannot.
        import tracemalloc
        tracemalloc.start()
        _base = tracemalloc.get_traced_memory()[0]
        t0 = time.perf_counter()
        wrapper = cst.metadata.MetadataWrapper(mod)
        pos = wrapper.resolve(cst.metadata.PositionProvider)
        t_pos = time.perf_counter() - t0
        _peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        ram_pos = _peak - _base

        # ⚑ THE POSITION MAP KEYS ON NODE OBJECTS, so it cannot be serialized as
        # such — node identity does not survive a process.  What CAN cross is the
        # projection a mode actually reads: (line, column) per node, addressed by
        # a stable path through the tree.  Measuring the pickle of the VALUES is
        # the honest lower bound on that; it is not a working design.
        try:
            b_pickle = len(pickle.dumps(
                [(v.start.line, v.start.column) for v in pos.values()],
                protocol=pickle.HIGHEST_PROTOCOL))
        except Exception:
            b_pickle = -1

        # the derived ANSWER a mode returns for this file — what option 1 caches
        try:
            answer = P._cached_defs(p)
            b_answer = len(json.dumps(answer).encode())
        except Exception:
            b_answer = -1

        rows.append((os.path.relpath(p, P.ROOT), len(src.encode()),
                     t_parse, t_pos, len(pos), b_pickle, b_answer, ram_pos))
    return rows


def main(argv):
    if cst is None:
        print("libcst not importable — no measurement taken (an unmeasured "
              "footprint is not a small one)")
        return 2
    paths = [a for a in argv if not a.startswith("-")]
    files = P.py_files(*paths) if paths else P.py_files()
    rows = probe(files)
    if not rows:
        print("0 files measured")
        return 1

    print("%-40s %8s %7s %7s %9s %8s %8s"
          % ("file", "src", "parse", "pos", "pos-blob", "answer", "pos-RAM"))
    for rel, nsrc, tp, tq, nn, bp, ba, rp in sorted(rows, key=lambda r: -r[3])[:20]:
        print("%-40s %7dB %6.0fms %6.0fms %8dB %7dB %7dK"
              % (rel[-40:], nsrc, tp * 1000, tq * 1000, bp, ba, rp // 1024))

    n = len(rows)
    src_t = sum(r[1] for r in rows)
    par_t = sum(r[2] for r in rows)
    pos_t = sum(r[3] for r in rows)
    blob_t = sum(r[5] for r in rows if r[5] > 0)
    ans_t = sum(r[6] for r in rows if r[6] > 0)
    ram_pk = max(r[7] for r in rows)
    print("\n%d file(s), %.1f KB source%s"
          % (n, src_t / 1024, "  (top 20 shown)" if n > 20 else ""))

    # ⚑ FOUR AXES, REPORTED SEPARATELY, BECAUSE THEY DISAGREE.  Collapsing them
    # to one ratio is the mistake this section exists to correct: "cheaper" is
    # meaningless until the scarce resource is named, and the scarce one is not
    # the one I first measured.
    print("\n-- CPU (derivation, serial) --")
    print("  parse       %6.1fs   (%.0f%%)"
          % (par_t, 100 * par_t / max(par_t + pos_t, 1e-9)))
    print("  positions   %6.1fs   (%.0f%%)"
          % (pos_t, 100 * pos_t / max(par_t + pos_t, 1e-9)))
    print("\n-- CACHE STORAGE --")
    print("  pos-blob    %6.1f MB  (LOWER bound: values only, no addressing)"
          % (blob_t / 1048576.0))
    print("  answers     %6.1f KB  (the derived views actually consumed)"
          % (ans_t / 1024.0))
    print("\n-- TASK RAM (the axis membudget arbitrates) --")
    print("  peak pos    %6.1f MB  per file, ONE worker"
          % (ram_pk / 1048576.0))
    # ⚑ THE MULTIPLIER DEPENDS ON THE VEHICLE, and stating one number would hide
    # that: threads share a heap, processes do not.  Both are printed because the
    # GIL result below decides which is even available.
    print("  x8 threads  %6.1f MB  (maps only — one interpreter, shared heap)"
          % (8 * ram_pk / 1048576.0))
    print("  x8 procs    %6.1f MB+ (maps AND 8 interpreters — membudget's case)"
          % (8 * ram_pk / 1048576.0))

    print("\n-- GIL (is the derivation even threadable?) --")
    ser_d, thr_d, sp = gil_scaling(files)
    print("  serial      %6.2fs   over %d file(s)" % (ser_d, min(16, len(files))))
    print("  8 threads   %6.2fs   speedup %.2fx" % (thr_d, sp))
    if sp < 2.0:
        print("  ⚑ GIL-BOUND — `MetadataWrapper.resolve` is pure-Python tree")
        print("    walking, so threads do NOT parallelise it.")
    ser_p, prc_p, spp = proc_scaling(files)
    if prc_p:
        print("  8 procs     %6.2fs   speedup %.2fx" % (prc_p, spp))
        print("  ⚑ THE TWO ARE LAYERS, NOT A FORK: processes for the derivation,")
        print("    threads in the DISPATCHER (socket I/O releases the GIL). And a")
        print("    worker RELEASES its map on return, so peak RAM is")
        print("    `pool_size x one map` — a TUNABLE membudget already arbitrates,")
        print("    not a fixed cost of going parallel.")
    else:
        print("  8 procs     UNAVAILABLE — process scaling UNMEASURED, which is")
        print("              not the same as absent")

    print("\n-- WALL TIME (a shared store trades CPU for latency) --")
    ok, ser = rtt()
    if ok:
        okc, con = rtt_concurrent()
        print("  RTT serial  %6.2f ms/op   (latency-bound)" % ser)
        if okc:
            print("  RTT x8      %6.2f ms/op   (throughput-bound; %.0fx better)"
                  % (con, ser / max(con, 1e-9)))
        # the comparison that decides: a round-trip against re-deriving ONE file
        med_pos = sorted(r[3] for r in rows)[len(rows) // 2] * 1000
        print("  median re-derive (pos) %6.0f ms/file" % med_pos)
        print("  ⚑ a round-trip is %.0fx cheaper than re-deriving one file"
              % (med_pos / max(ser, 1e-9)))
    else:
        print("  cache UNREACHABLE (%s) — wall-time axis UNMEASURED, which is"
              "\n  not the same as zero" % ser)

    print("\n⚑ THE VERDICT IS WHICH RESOURCE IS SCARCE, NOT WHICH NUMBER IS BIG.")
    print("   storage is bounded by cassian's cap (2 GB) and both candidates are")
    print("   noise against it; RAM is bounded by membudget and scales with -j;")
    print("   wall time is what `--order` actually spends. Read the axis that")
    print("   binds YOUR run — the ratios above are not commensurable.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
