#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""sppf_decode.py — the DECODE→ROWS layer: shim decode, the surrogate interners, and the
single insert path every ingest lands on.

⚑⚑ SPLIT OUT OF `sppf_db.py` ON THE ARROW, NOT THE LINE COUNT (⟡split-1200, 2026-08-11).
`sppf_db` passed its CODE cap (993 of 1200) while being 1,754 PHYSICAL lines — the metric
said fine and the file was past the point the rule actually names, *"too large to read
whole and write back out"*. `pycodemod --size` now prints both numbers so that gap is
visible rather than something a reader notices from a line number in an editor.

⚑ THE SEAM IS THE DIRECTION, AND THE OBVIOUS CUT WAS THE WRONG ONE. The tempting extraction
was the ADDITIVE PROJECTIONS (`project_orbit_sppf` + `project_argperm`, ~190 physical lines,
switched on by flags and clearly separable as a capability). Measured: `project_orbit_sppf`
calls `_mk_interners`. Moving it would have made `sppf_db` import the new module while the
new module imported `_mk_interners` back — a CYCLE, from the cut that read as cleanest.

Everything here consumes only `_schema`, `query_builders`, `_content_addr._b64`,
`jea_agdai.decode_core_diag` and `sppf_recover.recover_fields` — nothing from `sppf_db`. So
moving the SUPPLIER leaves a leaf, and the two consumers (`write_events`'s windowed loop,
`ingest_core`) plus `project_orbit_sppf` all point one way into it.

    _mk_interners(con)                     → (tid, pid): the terms/path_text surrogate interners
    _decode_raw(path)                      → (core|None, reason|None) — the shim call (the pool worker)
    _decode_window(paths, p_star)          → decode N cores in parallel, IN ORDER
    _insert_decoded(con, dec, …)           → the ONE decode→rows write path
    _decode_insert_core(con, path, …)      → the composed serial form of the two above

⚑ THE NAMES KEEP THEIR LEADING UNDERSCORE even though they are now cross-module. It marks
them as internal to the ingest path rather than a published surface — the same reason
`schema_decl` keeps `_node`/`_unit` underscored while re-exporting them. `sppf_db` imports
them BY NAME for that reason: `import *` skips a leading underscore by construction, the
defect that silently broke `schema._node` while 123 cases still passed.
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))

from _content_addr import _b64
from jea_agdai import decode_core_diag
import schema as _schema  # THE schema declaration: rows/upsert/apply
from sppf_recover import recover_fields


def _mk_interners(con):
    """The terms/path interners — CONTENT-DERIVED ids. Shared by the batched `write_events` and
    the per-core `ingest_core`, so the decode→rows logic is single-sourced.

    ⚑⚑ THE ID NO LONGER CONTAINS ITS OWN TEXT (ⓝ). It was `_b64(s)` — reversible, and therefore
    GROWING WITH WHAT IT NAMES. That is fine for a qname and fatal for a node key, because a
    content-complete node identity references its CHILDREN, and if a child is referenced by a key
    that carries its whole subtree then the parent's key carries the subtree twice over. Reference
    children by fixed-width IDS and the interned text is O(arity) instead of O(subtree).

    ⚑ AND THE ALTERNATIVE WAS A DIGEST, WHICH WOULD HAVE BEEN THE REUSE-SEARCH FAILING (user,
    2026-08-11: *"Only true if you require the node_id to hold the concatenation. Intern the
    strings that would have been concatenated, and a node_id is a path through that set of
    interned strings."*). `terms` + `path_seg` ALREADY ARE that structure — a path as a
    uniquely-identified queryable object — so this is the store's own idiom, not a new mechanism.
    A digest would have bought the same width and paid for it with a collision assumption where
    today there is none.

    ⚑⚑ AND THAT ARGUMENT IS ABOUT `node_id`, NOT ABOUT THIS TABLE — the generalisation is the
    defect (⑸, 2026-08-12). It reasons from a key that REFERENCES CHILDREN; `terms.text` is a
    LEAF and has none, so nothing here was ever paying the subtree-twice-over cost. Applying a
    conclusion about the recursive case to the leaf dictionary is what left an interning table
    keyed by an allocated counter, which is what made concurrent ingest corrupt the store.
    `_content_addr._addr` is now the id: 11 fixed characters, and its collision is DETECTED by
    the PK+UNIQUE pair rather than assumed away — see `schema_diag.intern`.

    ⚑ IDS ARE STORE-LOCAL, AND THAT IS A DECISION, NOT AN OVERSIGHT (user: *"we're not aiming for
    cross-store compatibility of raw ID numbers"*). Reproducibility moves to the interned CONTENT:
    two stores of one corpus hold different ids and identical paths. Anything needing determinism
    must therefore sort on the SEGMENT TEXT, never on an id — see `project_orbit`'s canonical
    representative, which is the one place that is load-bearing rather than cosmetic.

    ⚑ THAT PARAGRAPH IS NOW WEAKER THAN THE TRUTH AND IS KEPT BECAUSE THE *RULE* IT STATES STILL
    BINDS. Under a derived id two stores of one corpus hold the SAME ids, so cross-store
    comparison happens to work — but nothing may DEPEND on it, because the id is still a handle
    and not a fact. Sort on the text.

    ⚑ INTERNING STAYS IDEMPOTENT, WHICH IS THE PROPERTY THE WHOLE INGEST RESTS ON. The maps are
    loaded from the store first, so a second ingest returns the SAME id for the same text rather
    than minting a new one — a fresh counter per run would silently fork every id on re-ingest and
    make `ON CONFLICT DO NOTHING` wrong instead of correct-by-construction.

    ⚑⚑ THE MAPS ARE A CACHE NOW, NOT THE AUTHORITY (⑸, 2026-08-12). They still short-circuit the
    overwhelmingly common HIT, but a MISS goes to `schema.intern`, which mints from a postgres
    SEQUENCE inside the INSERT. The paragraph above is exactly right about idempotence and was
    silent about the id, which is where the defect was.

    ⚑⚑ THE COUNTER THAT STOOD HERE — DELETED 2026-08-12 (⑸). It read:

        def _next(m):
            # ⚑ NON-NUMERIC IDS COUNT AS 0, so a store still holding the OLD `_b64` ids does not
            # crash here — it continues from 1 and the two schemes coexist until `--full`. The
            # migration path is a full rebuild; this only keeps a partial store readable meanwhile.
            n = 0
            for v in m.values():
                try:
                    n = max(n, int(v))
                except (TypeError, ValueError):
                    pass
            return n + 1
        ctr = {"t": _next(terms_map), "p": _next(paths_map)}

    Its legacy-id tolerance is KEPT, moved into SQL as the `~ '^[0-9]+$'` filter in
    `schema_decl.seq_align_sql` — a `max(term_id::bigint)` over a `_b64`-era store raises
    `InvalidTextRepresentation`, and the alignment runs from `apply()` on every ingest path.

    ⚑⚑ AND THIS COUNTER IS THE ONE THAT FAILED SILENTLY. `core_id_for`'s clash raised;
    this one wrote through `upsert(on_conflict="ignore")` → `ON CONFLICT DO NOTHING` with NO
    conflict target, so the PK clash was SWALLOWED, `terms_map[s] = got` bound this process's
    text to ANOTHER process's id, and every row written afterwards referenced it. MEASURED: 8
    concurrent `--ingest-core --sandbox` processes, **all exiting 0**, leaving **21,840 rows
    whose `ctor_id` resolves to another term's text** (`Z30JointGenViaProduct` local_id 29
    reading `#String:"_+Z6_"` where the core says `#String:"Z30"`) and 288 texts
    interned-but-absent. Zero dangling references — no constraint in the schema sees it.
    """
    import query_builders as _QB

    terms_map = {r[1]: r[0] for r in _QB.run(con, "terms_all")}
    paths_map = {r[1]: r[0] for r in _QB.run(con, "pathtext_all")}

    def tid(s):
        s = "" if s is None else s
        got = terms_map.get(s)
        if got is None:
            got = _schema.intern(con, "terms", s)
            terms_map[s] = got
        return got

    def pid(s):
        got = paths_map.get(s)
        if got is None:
            # ⚑⚑ ONE LOCK ORDER: `terms` → `path_text` → `path_seg` — the DDL
            # DECLARATION ORDER, and the invariant that makes this safe under any
            # concurrency rather than under one particular schedule.
            #
            # ⚑ THE INVERSION THIS REMOVES. `tid(seg)` used to be evaluated INSIDE
            # the `path_seg` upsert's argument list (below), so a single `pid()`
            # touched `path_text` → `terms` → `path_seg` while a concurrent process
            # walked `terms` → `path_text` → `path_seg`. Opposite orders over the
            # same three relations is a cycle by construction, and postgres's
            # detector proved it: `ShareLock on terms` held while waiting for
            # `ShareLock on path_seg`, against an `INSERT INTO terms` wanting
            # `RowExclusiveLock` — dozens of `DeadlockDetected` in one build.
            #
            # ⚑ AND THE MITIGATION THAT WAS ALREADY HERE GUARDED THE WRONG ARM.
            # `schema_diag.intern` commits early and its docstring names this exact
            # hazard — *"a deadlock window between two writers each holding what the
            # other wants"* — resting on the premise that *"ALL of a core's interning
            # happens BEFORE any of its upserts"*. That premise was FALSE at this
            # call site, and it is what this hoist restores.
            #
            # ⚑ THE ARGUMENT-LIST POSITION WAS THE WHOLE BUG. Nothing about the
            # statements changed; only WHEN `tid` runs. A lock order is not a
            # property of any one statement, so it cannot be read off one.
            _segs = [(o, tid(seg)) for o, seg in enumerate(s.split("."))]
            got = _schema.intern(con, "path_text", s)
            paths_map[s] = got
            # ⚑ `path_text` IS NOW WRITTEN AT INTERN TIME, not rebuilt afterwards. It used to be
            # DELETE+INSERT..SELECT from `path_seg ⋈ terms` (`refresh_path_text`), which was
            # harmless while `path_id` was `_b64(text)` — the id was recomputable. With a
            # surrogate, a rebuild that reassigns ids would ORPHAN every reference to them.
            #
            # ⚑ THE `_schema.upsert(con, "path_text", [(got, s)])` THAT STOOD HERE WENT WITH THE
            # COUNTER (⑸, 2026-08-12) — `intern` writes the row IN the statement that mints the
            # id, which is the whole point: a mint that leaves the caller to INSERT is
            # check-then-act, and a second write of the same fact is a second chance to disagree.
            # The paragraph above is the reason the row exists at all and survives the deletion.
            # ⚑ ONE upsert PER PATH, not per segment. This looped `con.execute` per segment;
            # batching them is the same statement with one round-trip instead of n, which
            # matters more on postgres (a network/socket hop each) than it did on sqlite.
            _schema.upsert(con, "path_seg", [(got, o, t) for o, t in _segs])
        return got

    return tid, pid


def _decode_raw(path):
    """Decode ONE core via the shim → `(core|None, reason|None)` — the PARALLELIZABLE work (pure; no
    con/interner/shared state). The ThreadPool worker; each call blocks on its shim subprocess (GIL
    released) → real N-core parallel decode.

    ⚑⚑ IT RETURNED A BARE `None` AND SWALLOWED EVERY EXCEPTION (⑼, 2026-08-12). The body was:

        try:
            return decode_core(path)
        except Exception:
            return None

    ⚑ SO THE FIRST DEFECT WAS THAT THE CAUSE WAS UNOBSERVABLE, AND IT IS THE ONE TO FIX FIRST.
    A core failing for a genuine reason (an unsupported node kind, a truncated file, a version
    skew) was INDISTINGUISHABLE from one failing for a trivial one — a missing shim binary, a
    permission error, a typo in a path — and the converge loop correctly typed all of them as
    skip-once-per-run without anyone ever learning which. Nine of 3,193 is 0.3% today and it is
    SILENT COVERAGE LOSS at corpus scale: a core that never decodes contributes nothing to the
    SPPF and nothing says so.

    ⚑ THE `except Exception` STAYS — the pool worker must not raise, or one bad core kills the
    window — but it now RECORDS. A blanket catch is a legitimate boundary; a blanket catch that
    discards its argument is the absent-read-as-a-verdict shape one layer down.

    ⚑ THE THREE OUTCOMES ARE TYPED APART, because they have different repairs:
        `decode-nothing: …`  Agda's own deserialiser refused the interface (stale / wrong version)
        `shim-exit-N: …`     the shim or its environment failed — the TOOL, not the core
        `<ExcType>: …`       a python-side failure before or around the subprocess
    """
    try:
        return decode_core_diag(path)
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)


def _mtime_cohorts(relpaths, base):
    """`{YYYY-MM-DD: n}` — the BUILD DATES of a set of cores, which is the discriminator.

    ⚑⚑ THIS IS WHAT TURNED "REFUSED WITH A REASON" INTO A DIAGNOSIS (⑼, 2026-08-12). The
    shim's message for every failure is *"decode Nothing (stale/wrong-version .agdai; rebuild
    it)"* — and `--header` refuted the obvious reading of it: refused and decodable cores carry
    the SAME interface marker (`…0c120316`) and intact gzip framing at offset 24, so the file
    is not malformed and its format version is not skewed. The thing that actually splits the
    two populations is WHEN THEY WERE BUILT, which no instrument was reporting.

    ⚑ A DATE HISTOGRAM, NOT A MIN/MAX. Two ranges can overlap while the populations are
    cleanly separated by cohort, and a min/max would hide exactly that — the question is
    whether the split is CLEAN, and only the per-date counts answer it.
    """
    import time as _t

    out = {}
    for r in relpaths:
        try:
            d = _t.strftime("%Y-%m-%d", _t.localtime(os.path.getmtime(os.path.join(base, r))))
        except OSError:
            d = "(unreadable)"
        out[d] = out.get(d, 0) + 1
    return out


def undecodable_report(undec, ok=None, base=None):
    """Render `[(relpath, reason), …]` GROUPED BY REASON KIND. Prints nothing for an empty list.

    `ok` + `base` add the BUILD-DATE cohorts of both populations — the measurement that says
    whether "stale" is the real reason or the shim's guess.

    ⚑⚑ IT LIVES BESIDE THE DECODER, NOT IN THE CLI THAT PRINTS IT — the seam `schema_diag`
    took and argued for: a rendering inline in a dispatch branch is reachable only by running
    the whole chain, so no case can drive it and a wrong grouping reads as a clean report. It
    also paid down `sppf_db`'s 1200-line cap, which the ⑼ change had breached (1204) — the cap
    is a forcing function, and the thing it forced here was the right home.

    ⚑ GROUPED ON THE TYPED PREFIX, WHICH IS WHY A REASON IS SHAPED `kind: detail`. Same
    convention as `reconstruct.reason_of` — and the same trap: a detail that OPENS with a
    count once turned a 152-core population into 152 one-line buckets, because the grouping
    key became `"16697 row"`.

    ⚑ THE COUNT IS NEVER TRUNCATED AND THE LISTING SAYS WHEN IT IS. This replaced
    `", ".join(_undec[:4])`, which showed four names out of nine and said nine — asking the
    reader to believe a number it would not show. The first cut of the replacement printed
    EVERY name, which is right for 9 and unreadable at the measured **207 under one filter**;
    the honest middle is a head plus an explicit `… and N more`, so a truncation is a thing
    you can SEE rather than one you have to suspect.

    ⚑ AND THE SECOND GROUPING IS BY DIRECTORY, because that is what makes 207 actionable.
    A flat list of 207 module paths is a wall; "all 207 sit under these 6 subtrees" is a
    repair plan. The reason-kind grouping says WHAT went wrong, the directory grouping says
    WHERE — and neither substitutes for the other.
    """
    if not undec:
        return
    by = {}
    for r, w in undec:
        by.setdefault(str(w).split(":")[0], []).append(r)
    print("  ⚑ %d core(s) UNDECODABLE, by reason:" % len(undec))
    for k in sorted(by):
        names = sorted(by[k])
        more = "" if len(names) <= 12 else ", … and %d more" % (len(names) - 12)
        print("     %-16s %3d — %s%s" % (k, len(names), ", ".join(names[:12]), more))
    dirs = {}
    for r, _w in undec:
        dirs[os.path.dirname(r) or "."] = dirs.get(os.path.dirname(r) or ".", 0) + 1
    print(
        "     by directory (%d): %s"
        % (
            len(dirs),
            ", ".join(
                "%s=%d" % (d, n) for d, n in sorted(dirs.items(), key=lambda kv: -kv[1])[:12]
            ),
        )
    )
    if ok is not None and base is not None:
        _f = lambda h: ", ".join("%s=%d" % kv for kv in sorted(h.items()))  # noqa: E731
        print("     BUILD DATES — refused: %s" % _f(_mtime_cohorts([r for r, _ in undec], base)))
        print("     BUILD DATES — decoded: %s" % _f(_mtime_cohorts(ok, base)))
    print("     detail (first): %s" % undec[0][1])


def undecodable_census(paths, base, p_star=8):
    """Decode every core in `paths` WITHOUT writing, and return `[(relpath, reason), …]`.

    ⚑⚑ THE COVERAGE QUESTION HAD NO MODE, AND IT IS THE ONE THE CORPUS-SCALE INGEST NEEDS.
    `converge` reports the cores IT tried, so "how many of the 3,193 can the ingest never
    see?" was answerable only by running a full ingest — i.e. by paying for the thing the
    answer is supposed to size. A core that never decodes contributes nothing to the SPPF and
    nothing says so; this is what makes that absence a NUMBER instead of an assumption.

    ⚑ IT WRITES NOTHING AND TAKES NO CONNECTION, which is what makes it safe to run over the
    whole tree at any time. The read-only half of ingest is exactly `_decode_window`; asking
    it the coverage question costs one decode pass and risks no row.

    ⚑ A COST NOTE, BECAUSE IT IS NOT FREE: one shim subprocess per core (~50ms), so the whole
    corpus is a few minutes at `p_star`-way parallelism. That is Python + subprocesses, not a
    multi-GB agda elaboration, so it is not `membudget`'s class — but it IS `p_star` copies of
    a 95 MB binary, so do not raise `p_star` past the box's core count.
    """
    ok, bad = [], []
    for p, (dec, why, _s) in zip(paths, _decode_window(list(paths), p_star)):
        (ok if dec is not None else bad).append(
            os.path.relpath(p, base) if dec is not None else (os.path.relpath(p, base), why)
        )
    return sorted(ok), sorted(bad)


def reconcile_stamps(stampdir, base, sandbox=False):
    """⒯ — DELETE every ingest stamp the STORE does not back. Returns `(kept, [dropped …])`.

    ⚑⚑ A STAMP FILE IS A CLAIM ABOUT A DATABASE, HELD ON THE FILESYSTEM. `make` compares
    mtimes of FILES; an ingest lands in postgres. Wiring ingestion into the build therefore
    puts a claim in a place that cannot witness what it claims — and this repo has 23 reachable
    `store.sandbox_connect(reset=True)` call sites, a call that DROPS EVERY RELATION in the
    tenant. After any one of them every stamp is a lie, `make` skips the recipe, and the build
    goes green over an empty store. That is the prose-forging-a-structural-fact shape in a new
    register, and it is the defect this function exists to make impossible.

    ⚑ THE TOKEN IS `core_fp`, NOT A SECOND LEDGER — which is the whole reason this is sound.
    `ingest_core` ALREADY self-skips on `core_fp.mtime == the core's st_mtime_ns`; reading the
    same row here means stamp-truth and recipe-skip are keyed on ONE fact rather than two that
    can disagree. A private "what I ingested" sidecar would have been a second store, and the
    two would drift exactly when it mattered.

    **WHAT MAKES A STAMP FALSE** — the store holds no `core_fp` row for that core at that
    mtime. Enumerated causes: `sandbox_connect(reset=True)`; `sppf_db.init_db()` migrating a
    stale SCHEMA_VERSION (it DROPs `core_fp`); `build(full=True)` dropping the event tier;
    `finalize_db(prune=True)` deleting cores absent from disk; any out-of-band restore.

    **WHAT DETECTS IT** — this pass: ONE bulk `core_fp ⋈ terms` read, compared against the
    stamp tree, deleting every stamp not backed by a matching `(relpath, mtime)`. It is ONE
    query for the whole corpus, not one per module, so it costs the same at 168 cores as at
    3,479 — which is what lets it run on EVERY build instead of being a target someone
    remembers.

    ⚑ AND IT IS RUN AS AN ORDERED SUB-MAKE, NOT AN ORDER-ONLY PREREQUISITE. GNU make decides a
    target's staleness around the time it remakes prerequisites, so "reconcile first" expressed
    as `|`-prerequisites depends on stat timing that is subtle at best under `-j`. Two
    sequential `$(MAKE)` invocations have no such subtlety, and the root Makefile already has
    exactly that shape.

    ⚑ RESIDUE, STATED RATHER THAN IMPLIED: this detects the store→stamp direction ONLY. A
    PARTIAL ingest — a core's rows deleted while its `core_fp` row survives — is invisible
    here, and belongs to `finalize`/`converge`'s residue predicates. Recorded so a later reader
    does not read this gate as covering a completeness it never claimed.
    """
    import store as _store

    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    # ⚑ THE SAME JOIN `finalize_db`'s PRUNE USES: a core's id IS the term id of its relpath, so
    # `core_fp ⋈ terms` recovers the path from the ONE place it is stored. There is no
    # `core_fp.path` column to read instead, and inventing one here would be a second home.
    _rel = _schema.relations(con)
    if "core_fp" in _rel:
        _rows = list(
            _schema.rows(
                con,
                "SELECT t.text, t.term_id, f.mtime FROM core_fp f JOIN terms t "
                "ON t.term_id = f.core_id",
            )
        )
        backed = {r["text"]: r["mtime"] for r in _rows}
        # ⚑ THE ID MAP RIDES THE SAME READ — `.promoted` compares against `obs_node.core_id`,
        # which is a term id, while the stamp tree holds paths. Recovering the pairing from the
        # row set already fetched keeps ONE query for both halves; a second `core_fp ⋈ terms`
        # would be a second answer to "which id has this path", free to disagree with the first.
        ids_by_rel = {r["text"]: r["term_id"] for r in _rows}
    else:
        backed, ids_by_rel = {}, {}  # tier absent — every stamp is false, which is correct
    # ⚑⚑ `obs_node` IS READ AS A SET OF CORE IDS, NOT PER STAMP. One `SELECT DISTINCT` over the
    # addressing tier costs the same at 8 promoted cores as at 3,598 — the property
    # `reconcile_stamps` already argues for its `core_fp` read, and what lets this run on EVERY
    # build rather than being a target someone remembers.
    #
    # ⚑ ABSENT `obs_node` MEANS NOTHING IS PROMOTED, which is correct and not a degenerate case:
    # the relation is deliberately kept out of the default `sppf` tier (*"derived, disposable,
    # and not created by a default ingest that would never populate it"*), so it appears exactly
    # when something is about to fill it. Before that, every `.promoted` stamp is a lie.
    promoted_ids = set()
    if "obs_node" in _rel:
        promoted_ids = {
            r["core_id"] for r in _schema.rows(con, "SELECT DISTINCT core_id FROM obs_node")
        }
    kept, dropped = _reconcile_over(backed, stampdir, base)
    pk, pd = _reconcile_promoted_over(promoted_ids, ids_by_rel, stampdir, base)
    # ⚑⚑⚑ `.drained` IS PROBED PER STAMP, NOT ENUMERATED — the one place this function does not
    # take its "ONE query for the whole corpus" shape, and the reason is measured.
    # `SELECT DISTINCT core_id FROM obs` plans as a PARALLEL SEQ SCAN over 128M rows at cost
    # 2,863,738 (`schema.py --plan`, live). A single `WHERE core_id = … LIMIT 1` plans as an
    # Index Only Scan on `ix_obs_pk` at cost **0.82**, stopping at the first hit.
    #
    # ⚑⚑ SO THE DRIVER IS THE STAMP SET, WHICH IS SMALL, NOT THE RELATION, WHICH IS NOT. That is
    # `--holes`' recorded lesson one layer over: it replaced `LEFT JOIN (SELECT DISTINCT core_id
    # FROM obs)` — materialising the distinct set over the whole corpus before joining ~2,000
    # fingerprints against it — with `NOT EXISTS` asked once per driver row. `.ingested` and
    # `.promoted` enumerate because their tokens (`core_fp`, `obs_node`) are SMALL relations;
    # `obs` is the largest in the store and must be probed instead. The shape follows the
    # relation's size, not the function's habit.
    dk, dd = _reconcile_drained_over(promoted_ids, ids_by_rel, stampdir, base, _staged_probe(con))
    con.close()
    return kept + pk + dk, dropped + pd + dd


def reconcile_report(kept, dropped):
    """Render one `reconcile_stamps` result. Prints; returns nothing.

    ⚑ IT LIVES BESIDE THE RUNG, NOT IN THE CLI THAT CALLS IT — the seam `undecodable_report`
    took and argued for, and the ⒯ change re-learned it the same way: `sppf_db` went 1203 code
    lines against its 1200 cap, and the cap is a FORCING FUNCTION, not a number to raise. The
    thing it forced was the right home. A render inline in a dispatch branch is reachable only
    by running the whole chain, so no case can drive it.

    ⚑ THE TRUNCATION IS VISIBLE, per `undecodable_report`'s rule: a head plus an explicit
    `… and N more`, so a cut is something you can SEE rather than suspect. `0 LYING` is the
    quiet, common case and prints no list at all.
    """
    tail = ""
    if dropped:
        names = sorted(dropped)
        tail = ": " + ", ".join(names[:8])
        if len(names) > 8:
            tail += ", … and %d more" % (len(names) - 8)
    print(
        "reconcile-stamps: %d backed by core_fp, %d LYING stamp(s) deleted%s"
        % (kept, len(dropped), tail)
    )


def reconcile_stamp_cases(check, tmp):
    """⒯ guarded cases for `reconcile_stamps`, driven from `sppf_db._selftest`.

    ⚑ THE PREDICATE IS DRIVEN AS A PURE FUNCTION OVER AN INJECTED MAP, not through a live
    store — the same lesson `decode_reason_cases` records: a case that cannot reach the branch
    it names is decoration, and a case that needs the corpus to be in a particular state tests
    the state. The store read is one line; the JUDGEMENT is the match, and that is what these
    drive.
    """
    base = os.path.join(tmp, "cores")
    os.makedirs(os.path.join(base, "Sub"), exist_ok=True)
    core = os.path.join(base, "Sub", "M.agdai")
    open(core, "w").write("x")
    stamp = os.path.join(base, "Sub", "M.ingested")
    mt = os.stat(core).st_mtime_ns

    def _run(backed):  # stamps sit beside the cores, as they do in _build
        return _reconcile_over(backed, base, base)

    open(stamp, "w").write("")
    k, d = _run({"Sub/M.agdai": mt})
    check("a stamp backed by core_fp at the CURRENT mtime is KEPT", (k, d), (1, []))
    check("...and it is still on disk", os.path.exists(stamp), True)

    open(stamp, "w").write("")
    k, d = _run({})
    check(
        "a stamp with NO core_fp row (the tenant was reset) is DELETED",
        (k, d),
        (0, ["Sub/M.agdai"]),
    )
    check(
        "...and the lying stamp is gone, so make re-runs the ingest", os.path.exists(stamp), False
    )

    open(stamp, "w").write("")
    k, d = _run({"Sub/M.agdai": mt - 1})
    check(
        "a stamp whose core_fp mtime is STALE (core rebuilt since) is DELETED",
        (k, d),
        (0, ["Sub/M.agdai"]),
    )

    # ⚑ THE ORPHAN ROUTE, AND IT IS THE ONE mtime ALONE CANNOT SEE. `catalog_db.classify_missing`
    # types a whole class whose `.agdai` survives while its SOURCE is gone; and decodability is a
    # function of the CURRENT TREE, not of the core's bytes — `decodeInterface` relocates the
    # source paths an interface records, so a byte-identical core goes undecodable when a sibling
    # moves. A stamp must not outlive the core it names even when `core_fp` still lists it.
    open(stamp, "w").write("")
    os.unlink(core)
    k, d = _run({"Sub/M.agdai": mt})
    check(
        "a stamp whose CORE is gone is DELETED even though core_fp still backs it",
        (k, d),
        (0, ["Sub/M.agdai"]),
    )

    # ── ⟡reconcile-cases: THE OTHER TWO STAMP KINDS ──────────────────────────────────────
    #
    # ⚑⚑⚑ THREE STAMP KINDS, THREE TOKENS, AND ONLY ONE HAD CASES. `.ingested` is driven above;
    # `.promoted` and `.drained` were verified BY HAND — I planted a false `.drained` stamp on a
    # promoted-but-still-staged core, ran `make reconcile`, and watched it die. That was the
    # right test and it lived only in a transcript. A predicate that authorises DELETING a build
    # stamp needs its verification to survive the session that wrote it.
    #
    # ⚑⚑ THE IDS ARE INJECTED, LIKE `backed` ABOVE. `.promoted` compares `obs_node.core_id`
    # against the `core_fp ⋈ terms` pairing, and `.drained` adds an `obs` existence probe — all
    # three reads have no judgement in them, and every way these gates can be WRONG is in the
    # match. `_staged_probe` exists so the conjunction can be driven without a store.
    _idmap = {"Sub/M.agdai": "cid-M"}
    _pstamp = os.path.join(base, "Sub", "M.promoted")
    _dstamp = os.path.join(base, "Sub", "M.drained")
    open(core, "w").write("x")  # restore the core the orphan case removed

    open(_pstamp, "w").write("")
    check(
        "a .promoted stamp whose core HAS obs_node rows is KEPT",
        _reconcile_promoted_over({"cid-M"}, _idmap, base, base),
        (1, []),
    )
    check("...and it is still on disk", os.path.exists(_pstamp), True)

    open(_pstamp, "w").write("")
    check(
        "a .promoted stamp with NO obs_node rows is DELETED (the tier was dropped)",
        _reconcile_promoted_over(set(), _idmap, base, base),
        (0, ["Sub/M.agdai"]),
    )

    # ⚑ NOT INGESTED ⟹ NOT PROMOTED. A core absent from the id map cannot have been promoted,
    # so its stamp is false — the same direction `_reconcile_over` takes for a missing core_fp
    # row, and the branch that would otherwise KeyError or silently keep.
    open(_pstamp, "w").write("")
    check(
        "...and a core with no core_fp id at all is DELETED, not skipped",
        _reconcile_promoted_over({"cid-M"}, {}, base, base),
        (0, ["Sub/M.agdai"]),
    )

    # ⚑⚑ THE CONJUNCTION, ASSERTED IN ALL FOUR CORNERS — this is the only predicate here with
    # two halves, so a case set that drove one value of each would pass against an
    # implementation that ignored either.
    _never = lambda _cid: False  # obs holds nothing for it — drained
    _always = lambda _cid: True  # obs still holds rows — NOT drained
    open(_dstamp, "w").write("")
    check(
        "a .drained stamp: promoted AND not staged ⟹ KEPT",
        _reconcile_drained_over({"cid-M"}, _idmap, base, base, _never),
        (1, []),
    )
    open(_dstamp, "w").write("")
    check(
        "...promoted BUT STILL STAGED ⟹ DELETED (the drain has not happened)",
        _reconcile_drained_over({"cid-M"}, _idmap, base, base, _always),
        (0, ["Sub/M.agdai"]),
    )
    open(_dstamp, "w").write("")
    check(
        "...NOT promoted and not staged ⟹ DELETED (nothing reconstructs it)",
        _reconcile_drained_over(set(), _idmap, base, base, _never),
        (0, ["Sub/M.agdai"]),
    )
    open(_dstamp, "w").write("")
    check(
        "...NOT promoted and still staged ⟹ DELETED",
        _reconcile_drained_over(set(), _idmap, base, base, _always),
        (0, ["Sub/M.agdai"]),
    )

    # ⚑ AND THE THREE PREDICATES DO NOT SEE EACH OTHER'S STAMPS — each filters on its own
    # suffix. A shared walk that matched loosely would have `.drained` deleting `.promoted`
    # stamps, which is the kind of cross-talk a per-kind case set cannot catch but a mixed
    # population can.
    open(stamp, "w").write("")
    open(_pstamp, "w").write("")
    open(_dstamp, "w").write("")
    _reconcile_drained_over({"cid-M"}, _idmap, base, base, _never)
    check(
        "the .drained pass leaves .ingested and .promoted untouched",
        (os.path.exists(stamp), os.path.exists(_pstamp)),
        (True, True),
    )
    _reconcile_promoted_over({"cid-M"}, _idmap, base, base)
    check(
        "...and the .promoted pass leaves .ingested and .drained untouched",
        (os.path.exists(stamp), os.path.exists(_dstamp)),
        (True, True),
    )


def _reconcile_over(backed, stampdir, base):
    """The stamp-tree half of `reconcile_stamps`, over an ALREADY-READ `core_fp` map.

    ⚑ SPLIT OUT SO THE JUDGEMENT IS DRIVABLE WITHOUT A STORE. `reconcile_stamps` is
    `read the map` ∘ `this`; the store read is one query and has no judgement in it, while
    every way this gate can be WRONG lives here. A case that had to stand up postgres to
    check a filename comparison would be testing the fixture.
    """
    kept, dropped = 0, []
    for dp, _, fns in os.walk(stampdir):
        for fn in sorted(fns):
            if not fn.endswith(".ingested"):
                continue
            sp = os.path.join(dp, fn)
            core = sp[: -len(".ingested")] + ".agdai"
            rel = os.path.relpath(core, base)
            try:
                now = os.stat(core).st_mtime_ns
            except OSError:
                now = None
            if now is not None and backed.get(rel) == now:
                kept += 1
            else:
                os.unlink(sp)
                dropped.append(rel)
    return kept, dropped


def _reconcile_promoted_over(promoted_ids, ids_by_rel, stampdir, base):
    """The `.promoted` half — a DIFFERENT truth condition, not an extension of the above.

    ⚑⚑⚑ ⟡reconcile-promoted — A `.promoted` STAMP CLAIMS SOMETHING ELSE, AND KEYING IT ON
    `core_fp` WOULD BE WRONG IN BOTH DIRECTIONS. `.ingested` is backed by a `core_fp` row at the
    core's current mtime; `.promoted` is backed by `obs_node` HOLDING ROWS for that core. Those
    are different relations with different lifetimes, and neither implies the other:

      · `project_sppf(additive=False)` DROPs `obs_node` corpus-wide while every `core_fp` row
        survives — so `core_fp` would call every `.promoted` stamp true when none of them are.
      · a re-ingest advances `core_fp.mtime` and deletes the `.ingested` stamp, but leaves the
        OLD `obs_node` rows in place — so the `.promoted` stamp is stale in a way `core_fp`'s
        mtime cannot express, and make would skip a promote the new observations need.

    ⚑⚑ AND `reclaim` DELETING A CORE'S `obs`/`edge` DOES **NOT** FALSIFY THIS STAMP. A drained
    core is still promoted — that is the whole point of the drain: the staged copy goes because
    the durable side reconstructs it. MEASURED on the live store (`schema.py --packed`): three
    cores read `staged 0 / packed 943,927 · 6,210 · 6,199` — DRAINED, and their `obs_node` rows
    are intact. Reconciling `.promoted` against `obs` would delete a true stamp on every core
    the drain succeeded on, i.e. would punish exactly the cores that completed the pipeline.

    ⚑ SO THE TOKEN IS `obs_node`, AND IT IS THE SAME DISCIPLINE `reconcile_stamps` STATES FOR
    `core_fp`: read the relation the WRITER writes, not a proxy. `--promote-core`'s success
    condition is that `project_sppf` wrote this core's addressing; `obs_node` is where that
    lands and is the only place it lands.

    ⚑ IDS, NOT PATHS, WHICH IS WHY THIS TAKES TWO MAPS. `obs_node.core_id` is a term id, not a
    relpath, so the stamp tree (paths) and the store's answer (ids) cannot be compared directly.
    `ids_by_rel` is the `core_fp ⋈ terms` map the caller already read for the `.ingested` pass —
    reused rather than re-queried, so one store read serves both halves and the two can never
    disagree about which id a path has.

    ⚑ A CORE WITH NO ID IS UNPROMOTED, NOT UNKNOWN. If `ids_by_rel` has no entry the core was
    never ingested, so it cannot have been promoted either and the stamp is false — the same
    direction `_reconcile_over` takes for a missing `core_fp` row.
    """
    kept, dropped = 0, []
    for dp, _, fns in os.walk(stampdir):
        for fn in sorted(fns):
            if not fn.endswith(".promoted"):
                continue
            sp = os.path.join(dp, fn)
            core = sp[: -len(".promoted")] + ".agdai"
            rel = os.path.relpath(core, base)
            if ids_by_rel.get(rel) in promoted_ids:
                kept += 1
            else:
                os.unlink(sp)
                dropped.append(rel)
    return kept, dropped


def _reconcile_drained_over(promoted_ids, ids_by_rel, stampdir, base, still_staged):
    """The `.drained` half — a CONJUNCTION, and the third distinct truth condition here.

    ⚑⚑⚑ ⟡reconcile-drained — THREE STAMP KINDS, THREE TOKENS, AND NONE IMPLIES ANOTHER:

        .ingested   `core_fp` holds this core AT THE CORE'S CURRENT MTIME
        .promoted   `obs_node` holds rows for this core
        .drained    `obs_node` holds rows  ∧  `obs` holds NONE

    The third is the only one that is a conjunction, and both halves are load-bearing. Without
    the `obs_node` half a core whose durable side was dropped would read as drained (it has no
    `obs` rows — because it never had any). Without the `obs` half, every PROMOTED core reads as
    drained the moment it is promoted, and `make drain` would never run.

    ⚑⚑ THE STAMP CLAIMS THE STAGED COPY IS GONE **AND** RECONSTRUCTIBLE, which is exactly what
    the retire licence authorised. Falsifying events: a re-ingest rewrites `obs` for the core
    (staged rows are back, so the drain must be re-asked); `project_sppf(additive=False)` DROPs
    `obs_node` corpus-wide (the durable side is gone, so nothing reconstructs it and the claim
    that the drain was safe no longer holds); a tenant reset takes both.

    ⚑ A CORE THE LICENCE HELD IS **NOT** DRAINED, AND ITS STAMP IS STILL TRUE — which is the
    subtlety this predicate must not get wrong. `--drain-core` writes the stamp when the licence
    was ASKED, not when rows went (see its note), so a held core keeps `obs` rows and would fail
    the conjunction here. That is correct and deliberate: the stamp is dropped, make re-asks on
    the next build, and the licence gets another chance now that whatever held it may have been
    repaired. The alternative — treating "asked" as permanently satisfied — would mean a core
    held once is never re-offered, which is the silent-skip shape the integer roster produced.

    ⚑ PROBED, NOT ENUMERATED, and the caller's note carries the measurement: one index-only
    probe per stamp at cost 0.82 against a parallel seq scan of 128M rows at 2.86M. The driver
    is the stamp set because the stamp set is small and `obs` is the largest relation here.
    """
    kept, dropped = 0, []
    for dp, _, fns in os.walk(stampdir):
        for fn in sorted(fns):
            if not fn.endswith(".drained"):
                continue
            sp = os.path.join(dp, fn)
            core = sp[: -len(".drained")] + ".agdai"
            rel = os.path.relpath(core, base)
            cid = ids_by_rel.get(rel)
            if cid in promoted_ids and not (cid is not None and still_staged(cid)):
                kept += 1
            else:
                os.unlink(sp)
                dropped.append(rel)
    return kept, dropped


def _staged_probe(con):
    """`core_id → bool` — does `obs` still hold rows for this core? ONE index-only probe.

    ⚑ THE STORE READ, SEPARATED FROM THE JUDGEMENT — the split `_reconcile_over` prescribes and
    that `_reconcile_drained_over` could not have without it. That predicate has the only
    CONJUNCTION among the three stamp kinds and therefore the most ways to be subtly wrong; a
    case for it must be able to say "promoted but still staged" without standing up postgres.

    ⚑ `LIMIT 1`, NOT `count(*)`. The question is existence, and the plan says so: `WHERE
    core_id = … LIMIT 1` is an Index Only Scan on `ix_obs_pk` at cost **0.82**, stopping at the
    first hit, against a parallel seq scan of 128M rows at cost 2,863,738 for the enumerating
    form. The shape follows the relation's size.
    """
    _p = _schema.ph()
    return lambda cid: bool(
        _schema.scalar(con, "SELECT 1 FROM obs WHERE core_id = %s LIMIT 1" % _p, (cid,))
    )


def decode_reason_cases(check):
    """The ⑼ guarded cases for the decode-reason path, driven from `sppf_db._selftest`.

    ⚑ THE CASES LIVE BESIDE THE CODE AND THE SUITE STAYS WHERE IT WAS. This module defines no
    `_selftest` and dispatches no `--selftest`, so `run_selftests.discover()` — which counts a
    suite as the PAIR — does not see a new suite here; the count stays 69 and the cases stay
    readable next to `_decode_raw`. Moving them also paid down `sppf_db`'s cap breach, which is
    what made the right home unavoidable rather than merely preferable.
    """
    # ⚑⚑ THE DISCRIMINATOR IS DRIVEN AS A PURE FUNCTION, AND THE REASON IS MEASURED. A first
    # cut asserted it through the subprocess and MUTATION-PASSED: collapsing `decode_reason`'s
    # kind to the constant `"decode-nothing"` changed nothing, because the shim maps every
    # failure it has ever been shown to `decode Nothing` and the only other route (a
    # nonexistent path) never reaches the shim at all. **A case that cannot reach the branch it
    # names is decoration**, so the judgement was lifted out of the I/O.
    from jea_agdai import decode_reason as _dr, substrate_core_root

    check(
        "Agda refusing the interface is `decode-nothing`",
        _dr(1, "agdai_shim: decode Nothing (stale/wrong-version .agdai; rebuild it)").startswith(
            "decode-nothing:"
        ),
        True,
    )
    check(
        "...and any other non-zero exit is `shim-exit-N` — the TOOL, not the core",
        _dr(2, "agdai_shim: error while loading shared libraries").startswith("shim-exit-2:"),
        True,
    )
    # ⚑ THE HEAD OF STDERR, NOT THE TAIL — the defect this pins is measured, not hypothetical:
    # keeping the LAST 400 characters made all nine cores report the bottom of a GHC CallStack,
    # identical whatever went wrong.
    check(
        "...and the reason keeps the MESSAGE, not the backtrace tail",
        "decode Nothing" in _dr(1, "agdai_shim: decode Nothing\n" + "x" * 900),
        True,
    )
    check(
        "...and an empty stderr says so rather than reading as a blank reason",
        _dr(9, ""),
        "shim-exit-9: (no stderr)",
    )

    # ⚑⚑ THE CASE THAT COULD NOT HAVE EXISTED BEFORE, because there was nothing to assert:
    # `_decode_raw` returned a bare `None` for a missing shim, a truncated core, a version skew
    # and a permission error alike, so `converge` could report *"9 core(s) UNDECODABLE"* over a
    # 3,193-core corpus and no instrument anywhere could say which. Nine of 3,193 is 0.3% today
    # and it is SILENT COVERAGE LOSS at corpus scale.
    _dec_missing, _why_missing = _decode_raw("/nonexistent/core.agdai")
    check("a decode failure returns (None, reason), not a bare None", _dec_missing, None)
    check("...and the reason is TYPED, not empty", bool(_why_missing), True)
    # ⚑ A PATH THAT DOES NOT EXIST IS THE SHIM'S FAILURE, NOT THE CORE'S — it must NOT be
    # reported as `decode-nothing`, which is the one reason that means "rebuild this module".
    check(
        "...and a missing file is not misreported as decode-nothing",
        str(_why_missing).startswith("decode-nothing"),
        False,
    )
    # ⚑ AND THE FAST PATH STILL RETURNS THE PAIR. A change that returned the core bare on
    # success would break every caller's unpack at the one moment nothing is failing.
    _ok = os.path.join(
        substrate_core_root(os.path.join(_ROOT, "agda")), "Algebra", "F2", "F2.agdai"
    )
    if os.path.exists(_ok):
        _d_ok, _w_ok = _decode_raw(_ok)
        check("a successful decode returns (core, None)", (_d_ok is not None, _w_ok), (True, None))
        # ⚑ AND THE WINDOW YIELDS THE REASON IN ITS TRIPLE — the shape `write_events` unpacks.
        # It was a PAIR `(dec, secs)`; a window that dropped the reason on the floor would leave
        # `write_events` unable to report anything however good `_decode_raw` became.
        check(
            "_decode_window yields (core, reason, seconds)",
            [len(t) for t in _decode_window([_ok], 1)],
            [3],
        )
        # ⚑ THE COVERAGE CENSUS SPLITS BOTH WAYS, and the case drives a MIXED population
        # deliberately. One that saw only failures would pass against an implementation that
        # reported everything as undecodable — the absent-read-as-a-verdict shape, in the very
        # instrument built to size an absence.
        _b = os.path.dirname(_ok)
        _cok, _cbad = undecodable_census([_ok, os.path.join(_b, "__no_such_core.agdai")], _b, 1)
        check(
            "undecodable_census separates decoded from refused",
            (_cok, [r for r, _w in _cbad]),
            (["F2.agdai"], ["__no_such_core.agdai"]),
        )
        # ⚑ THE BUILD-DATE COHORT IS THE DIAGNOSIS, so it owes a case: it must key by DATE and
        # account for every path, including one it cannot stat (which is a fact about the
        # method and must not silently vanish from the histogram).
        _co = _mtime_cohorts(["F2.agdai", "__no_such_core.agdai"], _b)
        check(
            "_mtime_cohorts accounts for every path, unreadable included",
            (sum(_co.values()), _co.get("(unreadable)")),
            (2, 1),
        )


def insert_source(con, dec, relpath, mtime, producer="agdai"):
    """⟡ladder-1: the decoded core, WHOLE, into ONE `core_decoded` row by ONE statement.

    Returns 1 if the rung fired (row written or genuinely changed), 0 if the engine declined
    it because the stored copy was already this one.

    ⚑⚑ THIS IS A RUNG, NOT A HELPER, AND THE DIFFERENCE IS THAT NOTHING IS HELD BETWEEN
    READING A CONTACT AND ENERGISING A COIL. Everything the store has been paying for is a
    SCRATCHPAD VARIABLE — a value the interpreter held between a read and a write:
    `terms.term_id` as `max(term_id)+1` (21,840 rows resolving to another term's text, all
    exiting 0), `_node.node_id` as `str(len(node_ids)+1)`, `obs.seq` and `consumer.lwm` as
    positions standing in for identities, `project_sppf`'s `head`/`sym`/`pack` dicts copying
    the store's own witnesses into the interpreter to compute over, and the batch that
    deadlocked. They were patched one at a time as separate defects; they are one defect.
    This function holds nothing: the id is a pure function of the path, the payload is one
    value, and the "has it changed?" test is a conjunct of the write.

    ⚑⚑ AND THAT DISSOLVES THE `40P01` RATHER THAN FIXING IT. The reproduced deadlock was in
    `ingest_core → _insert_decoded → upsert(con,"event",erows) → cur.executemany`, and the
    measured cause is that **`executemany` is ONE transaction over N rows even under
    `autocommit=True`** — so a core's ~10⁴ `event` index tuples are HELD while the writer
    WANTS the next, in `dec["nodes"].items()` order, which is a decoder artifact and
    therefore unrelated between two cores. One row written by one statement has no batch, no
    client-chosen order, and nothing held across rows. The cycle is not broken here; it is
    **unconstructible**.

    ⚑ `core_id` IS COMPUTED, NOT INTERNED, AND THAT IS THE TIER BOUNDARY DOING ITS JOB.
    `_insert_decoded` gets its `cid` from `tid(relpath)` → `schema_diag.intern` → a write
    into `terms`, which lives in the tier ABOVE this one. Interning here would make the
    lower tier unwritable without the higher one, inverting the reconstruction arrow the
    tier exists to provide. `intern` is already content-derived (*"NO SELECT, NO nextval, NO
    RE-READ — THE ID IS A PURE FUNCTION OF THE TEXT"*), so `_addr(relpath)` is not a second
    authority for the id; it is the SAME function with the write removed, and a case asserts
    the two agree rather than assuming it.

    ⚑ NO `sort_keys`, DELIBERATELY, AND IT IS THE SAME ANTIPATTERN THE BATCH SORT WAS.
    `jsonb` defines the stored key order itself, so sorting client-side has no observable
    effect on what lands — and `sort_keys=True` RAISES `TypeError` on any object mixing key
    types, which JSON itself accepts because it coerces every key with `str`. Sorting a value
    whose order is not part of the value is work that can only fail.

    ⚑ `on_conflict='replace'` AND NOT `'ignore'`, BECAUSE A STALE ROW HERE IS A SILENT WRONG
    ANSWER. A core is re-decoded when its `.agdai` mtime advances; under DO NOTHING the row
    would keep the PREVIOUS decode forever, and every rung built on this tier would read it.
    The content-conditioned WHERE (`insert_row`) makes the unchanged case a no-op the ENGINE
    decides, so re-running an ingest costs no write and no dead tuple.
    """
    from _content_addr import _addr

    return _schema.insert_row(
        con,
        "core_decoded",
        {
            "core_id": _addr(relpath),
            "relpath": relpath,
            "mtime": mtime,
            "producer": producer,
            "dec": json.dumps(dec, ensure_ascii=False),
        },
        on_conflict="replace",
    )


def json_value(o):
    """`o` as the JSON VALUE it denotes — object keys coerced by JSON's OWN rule, `str`.

    ⚑⚑ THIS IS THE FIDELITY COMPARATOR AND IT APPLIES EXACTLY ONE RULE. The invariant is
    *"the stored row is a faithful copy of the decoded structure, whole"*, driven from `dec`
    itself at every depth — never from a roster of what some consumer currently extracts,
    which is a lower bound at best and a frozen roster at worst.

    ⚑ THE ONE RULE IS NEEDED BECAUSE `dec["nodes"]` IS KEYED BY **int** AND JSON OBJECT KEYS
    ARE STRINGS. So `json.loads(json.dumps(dec)) != dec` before any database is involved.
    `str(k)` is not a heuristic and not a repair — it is precisely the coercion
    `json.dumps` performs, so comparing under it asks "do these two denote the same JSON
    value?" and nothing more. In particular it does NOT re-int anything: a rule like *"re-key
    any object whose keys all parse as integers"* would silently rewrite a genuine string key
    `"0"`, which is a guess dressed as an inverse.

    ⚑ AND THE COERCION IS REPORTED SEPARATELY RATHER THAN HIDDEN BY THIS FUNCTION. A
    comparator that quietly normalises the one place the copy is not literal would make the
    gap invisible, which is the opposite of naming it — `source_fidelity` counts the
    non-string keys and how many are recoverable from their own record.
    """
    if isinstance(o, dict):
        return {str(k): json_value(v) for k, v in o.items()}
    if isinstance(o, list):
        return [json_value(v) for v in o]
    return o


def _key_census(o, acc):
    """Accumulate `{non_str_keys, recoverable, nul_strings, depth}` over a decoded structure.

    ⚑ `recoverable` COUNTS A NON-STRING KEY THAT EQUALS ITS OWN VALUE'S `id` FIELD — a
    WITNESS that the coercion is invertible without a codec assumption, reported as a
    measurement rather than used as one. Naming `id` in a report is a fact about what was
    found; naming it in `json_value` would have been a rule about what to do.
    """
    if isinstance(o, dict):
        for k, v in o.items():
            if not isinstance(k, str):
                acc["non_str_keys"] += 1
                if isinstance(v, dict) and v.get("id") == k:
                    acc["recoverable"] += 1
            _key_census(v, acc)
    elif isinstance(o, list):
        for v in o:
            _key_census(v, acc)
    elif isinstance(o, str) and "\x00" in o:
        # ⚑ POSTGRES `jsonb` REFUSES `NUL` INSIDE A STRING (`unsupported Unicode escape
        # sequence`), while `json` and python both accept it. That is the one VALUE-level
        # difference between the two types that could make a write fail rather than a
        # comparison differ, so it is counted rather than assumed absent.
        acc["nul_strings"] += 1


def source_fidelity(con, paths, base, p_star=8):
    """Write each core's `core_decoded` row, read it back, and compare against `dec` ITSELF.

    Returns the measurement dict `source_fidelity_report` renders. Nothing is asserted here;
    the caller decides what a mismatch means.

    ⚑⚑ THE POPULATION IS NAMED AND THE UNDECODABLE HALF IS NOT SILENTLY DROPPED. This arc has
    three recorded instances of an absent read reported as a pass — `--edge` printing `EXACT 0
    MISMATCH 0 ⇒ verified` over an empty store, `reflects_obs` returning `[] == []`, the
    census whose population shrank exactly as the drain succeeded. So `undecodable` is a
    reported field, and `exact` is meaningless without it.

    ⚑ THE READBACK IS A SECOND STATEMENT AND THAT IS FINE HERE, because this is a PROBE, not
    the rung. The rung is `insert_source`; measuring it necessarily reads what it wrote.
    """
    from _content_addr import _addr

    res = {
        "cores": 0,
        "undecodable": 0,
        "exact": 0,
        "mismatch": 0,
        "witnesses": [],
        "wrote": 0,
        "declined": 0,
        "payload_bytes": 0,
        "nodes": 0,
        "non_str_keys": 0,
        "recoverable": 0,
        "nul_strings": 0,
        "per_core_bytes": [],
    }
    for p, (dec, _why, _s) in zip(paths, _decode_window(list(paths), p_star)):
        res["cores"] += 1
        if dec is None:
            res["undecodable"] += 1
            continue
        rel = os.path.relpath(p, base)
        try:
            mtime = os.stat(p).st_mtime_ns
        except OSError:
            mtime = None
        _key_census(dec, res)
        res["nodes"] += len(dec.get("nodes", ()))
        n = insert_source(con, dec, rel, mtime)
        res["wrote"] += n
        res["declined"] += 1 - n
        b = len(json.dumps(dec, ensure_ascii=False).encode())
        res["payload_bytes"] += b
        res["per_core_bytes"].append(b)
        got = None
        for r in _schema.rows(
            con, "SELECT dec FROM core_decoded WHERE core_id = %s", (_addr(rel),)
        ):
            got = r["dec"]
            break
        if got is not None and json_value(got) == json_value(dec):
            res["exact"] += 1
        else:
            res["mismatch"] += 1
            res["witnesses"].append(rel)
    res["rows"] = _schema.scalar(con, "SELECT count(*) FROM core_decoded") or 0
    res["bytes"] = _schema.scalar(con, "SELECT pg_total_relation_size('core_decoded')") or 0
    return res


def source_fidelity_report(res, corpus_n=None):
    """Render `source_fidelity`'s measurement — fidelity, then SIZE with its extrapolation.

    ⚑ THE EXTRAPOLATION IS LABELLED AS ONE, EVERY TIME. A per-core mean multiplied by a
    corpus count is an ESTIMATE from a sample, and this arc has already recorded a figure
    ("9 undecodable") that was a fact about one run reported as a fact about the corpus. The
    min/max are printed beside the mean precisely so a reader can see how much the mean is
    hiding — 38 cores measured here span two orders of magnitude.
    """
    dec_n = res["cores"] - res["undecodable"]
    print(
        "  ⟡ladder-1 core_decoded — %d core(s) offered, %d decoded, %d undecodable"
        % (res["cores"], dec_n, res["undecodable"])
    )
    print(
        "     FIDELITY  EXACT %d · MISMATCH %d   (readback vs `dec` as a JSON value, "
        "every depth)" % (res["exact"], res["mismatch"])
    )
    if res["witnesses"]:
        print("       witnesses: %s" % ", ".join(res["witnesses"][:8]))
    print(
        "     the copy is literal EXCEPT: %d non-string object key(s), of which %d equal "
        "their own record's `id`" % (res["non_str_keys"], res["recoverable"])
    )
    print("     strings containing NUL (jsonb refuses these): %d" % res["nul_strings"])
    print(
        "     RUNG      wrote %d · declined %d (already current — the engine's WHERE, "
        "not a prior read)" % (res["wrote"], res["declined"])
    )
    per = res["per_core_bytes"]
    if per and dec_n:
        mean = res["bytes"] / max(1, res["rows"])
        print(
            "     SIZE      %s row(s) → %s B on disk (pg_total_relation_size), "
            "mean %s B/core"
            % (format(res["rows"], ","), format(res["bytes"], ","), format(int(mean), ","))
        )
        print(
            "               canonical JSON offered: %s B total, per core min %s / "
            "median %s / max %s  (%.1f× compressed by TOAST)"
            % (
                format(res["payload_bytes"], ","),
                format(min(per), ","),
                format(sorted(per)[len(per) // 2], ","),
                format(max(per), ","),
                res["payload_bytes"] / max(1, res["bytes"]),
            )
        )
        # ⚑⚑ `pg_total_relation_size` COUNTS DEAD TUPLES, SO THIS NUMBER IS ONLY CLEAN OVER A
        # FRESHLY TRUNCATED RELATION — measured, by getting it wrong first. Three successive
        # runs against an accumulating table reported 441,655 / 431,172 B per core; after
        # `TRUNCATE core_decoded` the same instrument read **305,009**. The bloat is TOAST
        # holding the superseded payloads of every earlier run, and `pg_column_size(dec)`
        # summed to 4 MB against a 15 MB relation, which is what exposed it. A size figure
        # taken from a table that has been written more than once is measuring the run
        # history as well as the data.
        if corpus_n:
            print(
                "     ⚑ EXTRAPOLATION (not a measurement): %s B/core × %s core(s) ≈ "
                "%.2f GB if every core were resident at once. This tier DRAINS, so the "
                "resident set is bounded by the drain, not by the corpus."
                % (format(int(mean), ","), format(corpus_n, ","), mean * corpus_n / 1e9)
            )


def ingest_source(core, base, apply=False):
    """⟡ladder-1 ENTRY POINT: decode ONE core and write its `core_decoded` row. Nothing else.

    ⚑⚑⚑ THE `sandbox=False` PARAMETER IS GONE (⟡explicit-tenant, 2026-08-27) AND ITS DEFAULT
    WAS THE DEFECT. A per-core WRITER whose tenant defaulted to LIVE when nobody said
    otherwise — `sandbox = "--sandbox" in argv` in the CLI, threaded down as a bool. The
    tenant now comes from `store.tenant`, which REFUSES an unstated one and publishes to the
    write-once ambient. **A bool cannot be seen by code that did not receive it; an ambient
    can, which is the whole point.**

    ⚑⚑ AND `apply` REPLACES IT ON THE OTHER AXIS, WHICH THIS MODE HAD NO NOTION OF AT ALL.
    `--ingest-source` wrote unconditionally — no `--dry-run`, no `--apply` — against the
    operator's *"nothing dry by default, nothing apply by default … explicitly stated on the
    command line."* Its make-driven siblings (`--ingest-core`, `--promote-core`,
    `--drain-core`) all share `_require_mutation_stated` as their prologue; this one was the
    odd writer out.

    ⚑ MEASURED, AND IT IS A POPULATION NOT AN OVERSIGHT: `toolmodes --conventions` reports
    **47 half-paired tools**, each still with a silent default — up from the 40 recorded when
    the convention was written. The convention is declared, symbol-tagged
    (⟡explicit-mutation / ⟡explicit-tenant), reported on every `--conventions` run, and
    **enforced by nothing**, so it drifts in the wrong direction. This fixes one member; the
    gate is the real repair.

    ⚑⚑ A SEPARATE ENTRY POINT, NOT A CALL ADDED INSIDE `_insert_decoded`, AND THAT IS THE
    WHOLE MEANING OF "ADDITIVE" HERE. Wiring the rung into `_insert_decoded` would make every
    existing ingest depend on the `sourced` tier existing — and neither `write_events` nor
    `ingest_core` applies it (both apply `only="event"`), so the production path would have
    started raising `UndefinedTable` on a change advertised as leaving it untouched. The
    alternative — teaching those two functions to apply a second tier — is a change to the
    path the brief says must keep working exactly as it does. So the rung lands BESIDE them.

    ⚑ THE COST OF THAT DECISION, NAMED RATHER THAN LEFT FOR A READER TO DISCOVER: the
    production ingest does NOT populate this tier today. `core_decoded` is written only by
    this entry point. Making it the source the event tier is shredded FROM is the next rung
    and is deliberately not taken here.

    ⚑ THE DDL IS APPLIED PER CALL, WHICH MATCHES `ingest_core` AND CARRIES ITS HAZARD. Two
    processes issuing `CREATE TABLE … IF NOT EXISTS` at the same instant can still collide on
    `pg_type` (`UniqueViolation … Key (typname, typnamespace)` — measured in this repo when
    two suite fixtures raced). `--init` exists precisely so the parallel sweep never has to,
    and a concurrent run of this mode owes the same courtesy: touch the tier once first.
    """
    import store as _store

    if not os.path.exists(core):
        return 0  # not built yet — nothing to source
    # ⚑⚑⚑ THE TENANT COMES FROM THE RESOLVER, NOT FROM A BOOLEAN PARAMETER (⟡explicit-tenant,
    # operator 2026-08-27: *"Correct form has to do with context vars (or, rather our own
    # wrapping of context vars)."*). This read `sandbox = "--sandbox" in argv` in the CLI and
    # threaded the bool down here, so **BARE MEANT LIVE, SILENTLY** — a per-core WRITER with an
    # unstated tenant, which is the worse half of `wrong-tenant-read-is-silent`.
    #
    # ⚑⚑ A BOOLEAN PARAMETER IS THE DEFECT, NOT THE PLUMBING. `store.tenant` REFUSES an
    # unstated tenant and publishes its answer to the write-once `edit_snapshot.TENANT`
    # ambient, so a SECOND, DISAGREEING resolution anywhere in the process RAISES instead of
    # quietly winning. A bool cannot do that: it is invisible to code that did not receive it,
    # which is exactly ⟡index-coverage-wrong-store (two functions in one report each resolved
    # the tenant independently, one read sqlite and one read postgres, and the disagreement
    # shipped as 32 work-generating false candidates).
    #
    # ⚑ `require=` IS NOT USED HERE, DELIBERATELY. This tenant IS the operator's to choose —
    # a core may legitimately be sourced into either store — so it must be stated on the
    # command line rather than pinned in code. The fixture path passes `require=` at its own
    # named site; this one refuses.
    con = _store.tenant(mode="rw", label="ingest_source")
    # ⚑⚑ ASSERT, DO NOT ESTABLISH (⟡ddl-is-a-write, 2026-08-24). This is a PER-CORE writer —
    # `--source-concurrency` fans N of them — and `CREATE … IF NOT EXISTS` takes the relation
    # lock BEFORE it can discover the object exists, which is the measured deadlock shape
    # (`ix_terms_text`: 13 backends, 11 queued; `ix_obsnode_pk`: five workers, pairs
    # deadlocked). Establishing the tier is a build-time act done once:
    # `schema.py --establish sourced --apply`.
    _schema.require_tiers(con, ("sourced",), label="ingest_source")
    rel = os.path.relpath(core, base)
    dec, why = _decode_raw(core)
    if dec is None:
        # ⚑ AN UNDECODABLE CORE WRITES NO ROW AND SAYS SO. It must not write an empty `dec`:
        # a row asserting "this core decoded to nothing" is indistinguishable from a core
        # that genuinely has no nodes, and the tier would then carry a fiction the rungs
        # above it cannot detect.
        # ⚑⚑ EXIT **3**, NOT 1, AND THE DISTINCTION IS THE ⑼ LESSON APPLIED TO AN EXIT CODE.
        # An undecodable core is a fact about the CORE (rebuild it); a non-zero exit from the
        # writer is a fact about the WRITE. The concurrency reproduction reads these codes to
        # decide whether a run is clean, and a shared `1` made 4 stale `.agdai` files read as
        # 4 failed writers — measured on the first run of that mode, which reported
        # `exit codes: 1, 1, 0, 0, 1, 0, 1, 0` beside `40P01: NONE` and looked contradictory.
        print("  UNDECODABLE %s — %s" % (rel, why))
        con.close()
        return 3
    try:
        mtime = os.stat(core).st_mtime_ns
    except OSError:
        mtime = None
    # ⚑⚑ THE DRY BRANCH DECODES AND THEN DOES NOT WRITE, WHICH IS THE ONLY HONEST FORM HERE.
    # Short-circuiting earlier would be cheaper and would report a PLAN for something that
    # cannot happen: an undecodable core exits 3 above, so a dry run that skipped the decode
    # would say "would write" about a core that would in fact refuse. ⚑ MEASURED IN THE
    # SIBLING, TODAY: `--ingest-core --dry-run` prints `plan … re-run with --apply` WITHOUT
    # reaching its own schema guard, so it reads GREEN for an invocation that refuses on
    # `--apply`. A dry run that cannot see what blocks it is worse than none.
    if not apply:
        print(
            "  plan  core_decoded %s (%d node(s)) — re-run with --apply"
            % (rel, len(dec.get("nodes", ())))
        )
        con.close()
        return 0
    n = insert_source(con, dec, rel, mtime)
    con.commit()
    con.close()
    print(
        "  core_decoded %-9s %s (%d node(s))"
        % ("WROTE" if n else "current", rel, len(dec.get("nodes", ())))
    )
    return 0


def source_fidelity_cli(filt, base, argv=(), sandbox=False):
    """`--source-fidelity [N]`: write, read back, compare against `dec`, and report SIZE.

    ⚑ `argv` IS PARSED HERE, BESIDE THE MODE, rather than unpacked at the dispatch. A
    dispatch that reads a mode's own arguments is a second place its signature is written
    down, and the two drift the first time a mode gains an option. `_sample` owns the
    stride-vs-head-slice argument for both modes that need a sample.
    """
    import store as _store

    sample, total = _sample(base, filt, _opt_int(argv, "--source-fidelity", 24))
    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    _schema.require_tiers(con, ("sourced",), label="source_fidelity")  # ⟡ddl-is-a-write
    res = source_fidelity(con, sample, base)
    con.commit()
    source_fidelity_report(res, corpus_n=total)
    con.close()
    # ⚑ A MISMATCH IS A NON-ZERO EXIT, AND SO IS AN EMPTY POPULATION. "0 exact, 0 mismatch"
    # over nothing decoded is not a pass; it is the absent-read-as-a-verdict shape that has
    # cost this arc three separate fixes.
    return 0 if (res["mismatch"] == 0 and res["exact"] > 0) else 1


def _sample(base, filt, want):
    """`want` cores under `filt`, taken by STRIDE across the sorted corpus, plus the total.

    ⚑ A STRIDE AND NOT A HEAD SLICE. A head slice is one directory, and a per-core figure
    drawn from one directory then multiplied by 3,192 is a fact about that directory reported
    as a fact about the corpus — the shape this arc has already recorded twice ("9
    undecodable" was one run's reach reported as the corpus's).
    """
    import glob

    cores = [
        c
        for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True))
        if filt in c
    ]
    return cores[:: max(1, len(cores) // max(1, want))][:want], len(cores)


def _opt_int(argv, flag, default):
    """The integer following `flag` in `argv`, or `default`. Parsed WITH the mode, not at the
    dispatch — a dispatch that unpacks a mode's arguments is a second place its signature
    lives, and the two drift the first time the mode gains an option."""
    argv = list(argv)
    if flag not in argv:
        return default
    i = argv.index(flag)
    n = argv[i + 1] if len(argv) > i + 1 else ""
    return int(n) if n.isdigit() else default


def source_concurrency(base, filt, n, sandbox=True):
    """Run `n` `--ingest-source` processes AT ONCE and report whether a `40P01` occurred.

    ⚑⚑ THIS IS THE CLAIM ⟡ladder-1 MAKES, SO IT IS A MODE RATHER THAN A SHELL FAN-OUT. The
    reproduced deadlock was 8 concurrent `--ingest-core --sandbox`, and re-running it by hand
    means launching eight background jobs and reading eight outputs — reasoning performed in
    the turn, which evaporates when the turn ends. As a mode the claim is re-checkable by
    anyone, at any later tree state, in one command.

    ⚑ IT REPORTS AND DOES NOT REPAIR. No retry, no backoff, no serialisation, no ordering.
    Under this architecture a deadlock is a DESIGN VIOLATION and clearing it destroys the
    evidence — so a `40P01` here is a finding to be read, with the losing process's own
    message preserved verbatim.

    ⚑ THE TIER IS CREATED ONCE, BEFORE THE FAN-OUT, AND THAT IS NOT PART OF THE CLAIM.
    Concurrent `CREATE TABLE … IF NOT EXISTS` can collide on `pg_type` in postgres
    (`UniqueViolation … Key (typname, typnamespace)` — measured in this repo when two suite
    fixtures raced), which is what `--init` exists to avoid for the event tier. A DDL race is
    a different phenomenon from a row-write deadlock, and letting it into the sample would
    contaminate the one being measured.

    ⚑ EACH CHILD TAKES A **DIFFERENT** CORE, WHICH IS THE HARDER CASE FOR THE OLD PATH AND
    THE EASIER ONE FOR THIS. Distinct cores are what made the original `40P01` possible: the
    insert order is `dec["nodes"].items()`, a decoder artifact, so two cores' `event` batches
    interleave in unrelated orders. Same-core contention is measured separately by the caller
    passing a one-core filter — there the conflict is on ONE row, which cannot form a cycle.
    """
    import subprocess
    import store as _store

    sample, total = _sample(base, filt, n)
    if not sample:
        # ⚑ AN EMPTY SAMPLE IS A FACT ABOUT THE FILTER, NOT A PASS. "0 processes, 0
        # deadlocks" is the absent-read-as-a-verdict shape in the instrument whose whole job
        # is to detect a rare event.
        print("  ⚑ no cores under filter %r — nothing was run, so nothing is claimed" % filt)
        return 1
    # ⚑ THE SAMPLE IS CYCLED UP TO `n`, so N processes always start even when the filter
    # yields fewer cores than N. Silently running 3 processes for a request of 8 would report
    # a contention level that was never applied.
    picks = [sample[i % len(sample)] for i in range(n)]
    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    # ⚑ THE CONCURRENCY INSTRUMENT MUST NOT WRITE DDL AT THE STORE IT IS ABOUT TO MEASURE
    # CONTENTION ON (⟡ddl-is-a-write) — establishing here made the baseline a state this mode
    # had created, and fed the fan-out's own DDL into the deadlock reading.
    _schema.require_tiers(con, ("sourced",), label="source_concurrency")
    before = _schema.scalar(con, "SELECT count(*) FROM core_decoded") or 0
    con.close()
    tool = os.path.join(_ROOT, "scripts", "sppf_db.py")
    # ⚑⚑⚑ THE CHILDREN MUST STATE BOTH AXES, AND THIS MODE MEASURED ITS OWN OMISSION.
    # `--ingest-source` gained `_require_mutation_stated` + `store.tenant` on 2026-08-27; this
    # fan-out still spawned it BARE, so all 8 children exited 2 before opening a transaction.
    # The run reported `reached the WRITE: 8 of 8` beside `core_decoded rows: 4 → 4` and
    # `40P01: NONE` — ⚑ **a clean deadlock verdict over zero writers.**
    #
    # ⚑⚑ AND THE CONTRADICTION WAS VISIBLE ON THE FACE OF THE OUTPUT, WHICH IS WHY IT WAS
    # CAUGHT: "reached the WRITE" is computed as `n - undecodable`, so a child that refuses for
    # ANY OTHER REASON counts as having reached a write it never attempted. The rows-delta line
    # is the only thing that contradicted it. **`reached the WRITE` is a subtraction, not an
    # observation** — it cannot see a refusal it has no code for, which is the census-blind-spot
    # shape one layer inside the instrument built to observe writers.
    #
    # ⚑ THE TENANT IS FORWARDED, NOT DEFAULTED. `--apply` is unconditional here because a
    # concurrency probe that dry-ran would measure nothing — the mutation IS the subject. That
    # is a tenant/mutation choice made IN CODE at a named site, which is the sanctioned form.
    argv = [sys.executable, tool, "--ingest-source"]
    tflag = "--sandbox" if sandbox else "--live"
    procs = [
        subprocess.Popen(
            argv + [p, tflag, "--apply"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for p in picks
    ]
    outs = [(pr.wait(), pr.stdout.read(), pr.stderr.read()) for pr in procs]
    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    after = _schema.scalar(con, "SELECT count(*) FROM core_decoded") or 0
    con.close()
    # ⚑ `40P01` IS THE POSTGRES SQLSTATE AND IS WHAT IS MATCHED, not the word "deadlock".
    # psycopg spells the exception `DeadlockDetected` and the server message is localisable;
    # the SQLSTATE is neither. Both are looked for, because a match on either is a finding
    # and a miss on both is what the claim rests on.
    dead = [
        (i, e) for i, (_rc, _o, e) in enumerate(outs) if "40P01" in e or "DeadlockDetected" in e
    ]
    # ⚑ EXIT 3 IS AN UNDECODABLE CORE AND IS NOT A WRITER FAILURE. Typing them apart is the
    # ⑼ lesson: a run where 4 of 8 `.agdai` files are stale must not read as 4 broken writers
    # beside a clean deadlock verdict.
    undec = [i for i, (rc, _o, _e) in enumerate(outs) if rc == 3]
    fail = [(i, rc, e) for i, (rc, _o, e) in enumerate(outs) if rc not in (0, 3)]
    print(
        "  ⟡ladder-1 CONCURRENCY — %d process(es) at once, %d distinct core(s) under %r "
        "(corpus %d)" % (n, len(set(picks)), filt, total)
    )
    print("     exit codes: %s" % ", ".join(str(rc) for rc, _o, _e in outs))
    # ⚑⚑ THE NUMBER THAT MATTERS IS HOW MANY PROCESSES REACHED THE WRITE, not how many were
    # launched. A run where most cores are undecodable applies far less contention than its
    # headline N suggests, and reporting only N would overstate what the claim rests on.
    # ⚑⚑ COUNT THE PROCESSES THAT DID NOT REFUSE, rather than subtracting the one refusal kind
    # this line happened to know about. It read `n - len(undec)`, so a child refusing for ANY
    # other reason — an unstated tenant, an unstated mutation, an absent tier — was counted as
    # having reached the write. MEASURED 2026-08-27: 8 children exited 2 on an unstated
    # mutation and the line printed `reached the WRITE: 8 of 8` beside `rows: 4 → 4`.
    # ⚑ `rc == 0` is the only positive evidence available here; every other code is a refusal
    # of some kind, and the ones this mode cannot name are exactly the ones it must not credit.
    _wrote = sum(1 for rc, _o, _e in outs if rc == 0)
    print(
        "     reached the WRITE: %d of %d (%d undecodable core(s) — a fact about the "
        "core, not the writer; %d refused for another reason)"
        % (_wrote, n, len(undec), n - _wrote - len(undec))
    )
    print("     core_decoded rows: %d → %d" % (before, after))
    if dead:
        print("     ⚑⚑ 40P01 DEADLOCK — %d of %d process(es). VERBATIM:" % (len(dead), n))
        for i, e in dead[:2]:
            print("        [proc %d] %s" % (i, e.strip()[:1200]))
    else:
        print("     40P01 DEADLOCK: NONE observed in %d concurrent writer(s)" % n)
    for i, rc, e in fail:
        if (i, e) not in dead:
            print("     ⚑ process %d exited %d — %s" % (i, rc, e.strip().splitlines()[-1:]))
    return 1 if (dead or fail) else 0


#: The ⟡ladder-1 modes `source_cli` owns. ⚑ DERIVED FROM ONE PLACE so `sppf_db`'s dispatch
# and this module cannot disagree about which flags reach here — the dispatch tests exactly
# this set, and a mode added below without adding it here simply never fires, loudly (the
# usage line names it and nothing happens) rather than silently.
SOURCE_MODES = {"--ingest-source", "--source-fidelity", "--source-concurrency"}


def source_cli(argv, args, base, resolve):
    """The ⟡ladder-1 CLI — one entry point for the SOURCED tier's three modes.

    `resolve` is `sppf_db._resolve_core` passed in rather than imported: `sppf_db` imports
    THIS module, so reaching back would close the cycle the ⟡split-1200 cut opened on
    purpose (*"moving the SUPPLIER leaves a leaf"*).
    """
    argv = list(argv)
    sandbox = "--sandbox" in argv
    filt = args[0] if args else ""
    if "--ingest-source" in argv:
        i = argv.index("--ingest-source")
        if len(argv) <= i + 1 or argv[i + 1].startswith("--"):
            # ⚑ REFUSE A MISSING PATH rather than falling through to a default. `sppf_db`'s
            # own worst recorded defect is a bare run that defaulted to a subtree and opened
            # a write transaction against the live store.
            print("  --ingest-source: needs a PATH (a .agdai core or its .agda source)")
            return 2
        # ⚑⚑ THE MUTATION AXIS IS STATED HERE, THE TENANT AXIS INSIDE (⟡explicit-mutation).
        # `_require_mutation_stated` is `sppf_db`'s — the SHARED prologue `--ingest-core`,
        # `--promote-core` and `--drain-core` already use — so this is one more caller of one
        # guard, not a fourth copy of it. ⚑ The import is local: `sppf_db` imports THIS module,
        # so a module-level import would close the cycle the ⟡split-1200 cut opened on purpose
        # (the same reason `resolve` is passed in rather than imported).
        import sppf_db as _db

        _apply = _db._require_mutation_stated("sppf_db --ingest-source")
        return ingest_source(resolve(argv[i + 1], base), base, _apply)
    if "--source-concurrency" in argv:
        return source_concurrency(
            base, filt, _opt_int(argv, "--source-concurrency", 8), sandbox=sandbox
        )
    return source_fidelity_cli(filt, base, argv, sandbox)


def source_row_cases(check):
    """The ⟡ladder-1 guarded cases for the SOURCED tier, driven from `sppf_db._selftest`.

    ⚑ THE CASES LIVE BESIDE THE CODE AND THE SUITE STAYS WHERE IT WAS — the `decode_reason_cases`
    precedent, for the same two reasons: `run_selftests.discover()` counts a suite as the PAIR
    (a `_selftest` def AND a `--selftest` dispatch), so defining neither here adds no suite and
    the total stays 69; and `sppf_db` sits 16 code lines under its 1200 cap, which is the
    forcing function that makes the right home unavoidable rather than merely preferable.
    """
    # ⚑ THE COMPARATOR IS DRIVEN AS A PURE FUNCTION FIRST, because the store round-trip below
    # cannot distinguish "the copy is faithful" from "the comparator normalises everything".
    # A comparator that returned True for any pair would pass every fidelity case ever
    # written for it — the absent-read-as-a-verdict shape, in the instrument built to detect
    # exactly that.
    check("json_value coerces an int key the way JSON does", json_value({1: "a"}), {"1": "a"})
    check(
        "...recursively, at every depth",
        json_value({"n": [{2: {3: "x"}}]}),
        {"n": [{"2": {"3": "x"}}]},
    )
    # ⚑ AND IT MUST NOT RE-INT. A rule like "re-key any object whose keys all parse as
    # integers" would silently rewrite a genuine string key `"0"` — a guess dressed as an
    # inverse, and the reason the int-keying is REPORTED rather than repaired.
    check(
        "...and never invents the inverse: a genuine string key stays a string",
        list(json_value({"0": "a"}).keys()),
        ["0"],
    )
    check(
        "...so it does NOT collapse a real difference",
        json_value({"a": 1}) == json_value({"a": 2}),
        False,
    )

    # ── the CLI plumbing: a mode that never fires is the silent-skip defect one layer up ──
    check(
        "`--source-concurrency N` is parsed beside the mode",
        _opt_int(["--source-concurrency", "16"], "--source-concurrency", 8),
        16,
    )
    check(
        "...and a MISSING N falls back rather than crashing on the index",
        _opt_int(["--source-concurrency"], "--source-concurrency", 8),
        8,
    )
    # ⚑ A NON-NUMERIC NEXT ARGUMENT IS THE REAL CASE, not a hypothetical: `--source-concurrency
    # --sandbox` is exactly how these modes are typed. `int(...)` on it would raise, and a
    # `try/except: 0` would silently run ZERO processes and report a clean deadlock verdict.
    check(
        "...and the next FLAG is not mistaken for N",
        _opt_int(["--source-concurrency", "--sandbox"], "--source-concurrency", 8),
        8,
    )
    # ⚑⚑ ON THE AST, NOT ON THE SOURCE TEXT, AND THIS IS `service_order`'s DEFECT ONE LAYER
    # DOWN. `sppf_db`'s dispatch fires on `SOURCE_MODES & set(sys.argv)`; a mode added to
    # `source_cli` and NOT to that set is simply never reached — the roster-drops-an-entry
    # shape `lifecycle.boundary_index` raises over. The ⚑ blocks here NAME every flag to
    # explain them, so a substring scan would be satisfied by the prose.
    import ast as _ast
    import inspect as _inspect

    _branched = {
        n.value
        for n in _ast.walk(_ast.parse(_inspect.getsource(source_cli)))
        if isinstance(n, _ast.Constant)
        and isinstance(n.value, str)
        # ⚑ THE BARE `"--"` IS A PREFIX TEST, NOT A FLAG — `source_cli` uses it to
        # refuse `--ingest-source --sandbox` (a mode whose PATH argument is the next
        # flag). Counting it as a mode made this case fail on its first run, which
        # is the case doing its job on the wrong population rather than a defect.
        and n.value.startswith("--")
        and len(n.value) > 2
    }
    # `--sandbox` is a MODIFIER every mode honours, not a mode — it selects the tenant, never
    # the action, so it is the one flag that must NOT reach the dispatch's mode set.
    check(
        "every flag `source_cli` branches on is a declared SOURCE_MODE",
        sorted(_branched - {"--sandbox"} - SOURCE_MODES),
        [],
    )
    check(
        "...and SOURCE_MODES declares nothing `source_cli` cannot serve",
        sorted(SOURCE_MODES - _branched - {"--source-fidelity"}),
        [],
    )

    from jea_agdai import substrate_core_root

    _base = substrate_core_root(os.path.join(_ROOT, "agda"))
    # ⚑ THE SAMPLE IS BOUNDED BY `want` AND THE CORPUS TOTAL IS REPORTED SEPARATELY — the two
    # numbers the extrapolation multiplies. A `_sample` that returned the whole corpus would
    # make `--source-fidelity 24` decode 3,192 cores, and one that reported `total` as the
    # SAMPLE size would make the extrapolation silently self-referential.
    _s24, _tot = _sample(_base, "Algebra", 24)
    check("the stride sample is bounded by `want`", len(_s24) <= 24, True)
    check(
        "...while the corpus total is the FILTERED population, not the sample",
        _tot >= len(_s24) and all("Algebra" in c for c in _s24),
        True,
    )
    _core = os.path.join(_base, "Algebra", "F2", "F2.agdai")
    if not os.path.exists(_core):
        return
    _dec, _why = _decode_raw(_core)
    if _dec is None:
        return
    _rel = os.path.relpath(_core, _base)
    from _content_addr import _addr

    con = _schema.sandbox_fixture("sppf_decode_sourced")
    # ⚑⚑ THE DERIVED KEY MUST AGREE WITH THE INTERNER, CHECKED RATHER THAN ASSUMED. ⓟ's
    # defect was two authorities for one id — `obs.core_id` from `tid(relpath)` against a
    # `core_fp.core_id` minted from a parallel sequence — and it hid because *"nothing joins
    # them"*. `insert_source` deliberately does NOT intern (the tier boundary: `terms` is
    # above it), so the same shape is available again and this is what closes it.
    check(
        "the sourced row's key IS the interner's, computed without interning",
        _addr(_rel),
        _schema.core_id_for(_rel, con),
    )

    # the rung: first write FIRES, the identical re-write is DECLINED by the engine
    _schema.execute(con, "DELETE FROM core_decoded")
    _first = insert_source(con, _dec, _rel, 111)
    _again = insert_source(con, _dec, _rel, 111)
    check("the rung fires once", _first, 1)
    # ⚑ THE DECLINE IS THE WHERE CLAUSE, NOT A CACHE AND NOT A PRIOR READ. If this ever
    # returns 1 the guard has silently become an unconditional overwrite — same rows, same
    # counts, a dead tuple per re-ingest and no way to tell "already current" from "just
    # landed". The count is the only observable that separates them.
    check("...and declines an identical re-write, so re-ingest costs no write", _again, 0)
    _changed = dict(_dec)
    _changed["defmarks"] = list(_dec["defmarks"]) + [{"unit": "X", "root": 0}]
    check(
        "...but fires again when the decoded content actually changed",
        insert_source(con, _changed, _rel, 111),
        1,
    )
    check(
        "...and still holds exactly ONE row for the core",
        _schema.scalar(con, "SELECT count(*) FROM core_decoded"),
        1,
    )

    # ── FIDELITY: the stored row against `dec` ITSELF, driven by `dec`'s own keys ────────
    _schema.execute(con, "DELETE FROM core_decoded")
    insert_source(con, _dec, _rel, 111)
    # ⚑⚑ THE READBACK IS TOLERANT OF *NO ROW*, AND THAT IS A MUTATION-TEST FINDING RATHER
    # THAN CAUTION. A `next(...)` here raised `StopIteration` when `insert_source` was
    # mutated to address the row by a DIFFERENT key — so the guard against a parallel id
    # authority (ⓟ's defect) reported a TRACEBACK instead of naming the defect, and a
    # traceback out of a case function takes the whole suite with it rather than failing one
    # line. An absent row is a FINDING and gets its own case below.
    _got = None
    for _r in _schema.rows(con, "SELECT dec FROM core_decoded WHERE core_id = %s", (_addr(_rel),)):
        _got = _r["dec"]
        break
    # ⚑ ONE AUTHORITY FOR THE ID, ASSERTED ON THE WRITE AND NOT ONLY ON THE FUNCTION. The
    # case above checks that `_addr` agrees with the interner; this checks that the RUNG
    # actually addresses its row that way. ⓟ's split authority hid precisely because
    # *"nothing joins them"* — two ids for one core, each internally consistent.
    check("...and the rung addressed it by that derived key", _got is not None, True)
    # ⚑ THE NON-INERTNESS GUARD COMES FIRST, and this file has already paid for its absence:
    # `[] == []` passes just as well when the population is empty. A fidelity claim over
    # nothing is the shape `reflects_obs` shipped for months.
    check(
        "...over a NON-EMPTY structure (the population guard)",
        len(_dec["nodes"]) > 100 and len(_dec["defmarks"]) > 0,
        True,
    )
    check(
        "the stored row IS the decoded structure, whole, at every depth",
        json_value(_got) == json_value(_dec),
        True,
    )
    # ⚑⚑ AND THE ONE PLACE THE COPY IS NOT LITERAL IS ASSERTED AS A FACT, NOT LEFT IMPLICIT.
    # `dec["nodes"]` is keyed by int and JSON object keys are strings, so the raw readback is
    # NOT `==` to `dec` in python — before any database is involved. Pinning it means the gap
    # cannot silently widen (a new non-string key elsewhere) and cannot silently vanish
    # (someone "fixing" it with a heuristic re-key). It is the honest boundary of the claim
    # above, and the recovery witness is beside it.
    check("...and the ONLY departure is JSON's own string-keying of objects", _got == _dec, False)
    _acc = {"non_str_keys": 0, "recoverable": 0, "nul_strings": 0}
    _key_census(_dec, _acc)
    check(
        "...every one of which is recoverable from its own record's `id`",
        (_acc["non_str_keys"] > 0, _acc["non_str_keys"] - _acc["recoverable"]),
        (True, 0),
    )
    con.close()


def _decode_insert_core(con, path, relpath, mtime, tid, pid):
    """Decode + insert ONE core (the composed SERIAL path; ingest_core + the serial fallback use it).

    Returns `(ingested, reason)` — `reason` is None on success and the typed decode failure otherwise."""
    dec, why = _decode_raw(path)
    return _insert_decoded(con, dec, relpath, mtime, tid, pid), why


def _decode_window(paths, p_star):
    """⟡gce-consume: decode a window's cores — p_star>1 → a ThreadPool of shim subprocesses (real parallel
    decode; the GIL is released during subprocess.run so P shims run on P cores), else serial. Returns
    [(dec, reason, wall_seconds), …] IN ORDER, so the INSERT stays serial (shared interners tid/pid + con).
    Decode is the ONLY parallel part; the parent process interns+writes single-threaded → no python-spawn tax.

    ⚑ THE REASON RIDES BACK WITH THE DECODE (⑼) rather than being re-derived by the caller. Re-running
    the shim to ask why it failed would decode twice on the failure path AND could answer differently —
    a diagnosis taken from a second run is a diagnosis of a second run."""

    def one(p):
        t0 = time.perf_counter()
        dec, why = _decode_raw(p)
        return dec, why, time.perf_counter() - t0

    if p_star > 1 and len(paths) > 1:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=p_star) as ex:
            return list(ex.map(one, paths))
    return [one(p) for p in paths]


def _insert_decoded(con, dec, relpath, mtime, tid, pid, producer="agdai"):
    """INSERT one already-decoded core's rows (SERIAL — shared interners tid/pid + con). The caller has deleted
    any stale rows for this core_id. Returns True if ingested, False if `dec` is None (undecodable). The SINGLE
    decode→rows path (write_events' windowed loop and ingest_core both land here)."""
    if dec is None:
        return False  # undecodable: no rows, no version — re-attempted next run
    cid = tid(relpath)  # intern the core path so _unit.file_id resolves in `terms`
    # ⚑ THE MODULE NAME IS A PROPERTY OF THE PRODUCER, NOT OF THIS WRITER. This line was
    # the ONE Agda-shaped assumption in an otherwise producer-agnostic path: it hardcodes
    # the `Substrate.` prefix and strips a `.agdai` suffix, so a python core would have
    # been filed under `Substrate.scratch/pycodemod.py::foo` — wrong in both halves, and
    # silently, since `pid` interns whatever string it is handed.
    #
    # A caller that already KNOWS its module name passes it; only the agdai producer
    # derives one from the path. Branching on `producer` here instead would put the
    # second corpus's naming rule inside the writer, which is where the first one's
    # having lived is exactly the defect.
    module = dec.get("module")
    if module is None:
        module = "Substrate." + relpath[: -len(".agdai")].replace(os.sep, ".")  # agdai_module
    mpid = pid(module)
    erows, orows, edgerows = [], [], []
    for lid, rec in dec["nodes"].items():
        ctor = rec.get("constructor")
        kids = rec.get("children", [])
        # ⚑⚑⚑ ⟡recovery-at-intern — RECOVERY IS NOT PERFORMED HERE ANY MORE, AND THE LINE
        # BELOW ALREADY SAID SO WHILE THE LINE ABOVE IT DID THE OPPOSITE. The comment at the
        # `obs_rec` assignment has always read *"raw record content, children = LOCAL ids, NO
        # resolution"*, and three lines earlier this called `recover_fields(rec, dec["nodes"])`
        # — which walks to child[0], reads its constructor, and reconstructs the v1
        # `qname`/`index` semantics. That IS resolution, inside the writer whose whole contract
        # (`write_events`: *"decode each core to raw OBSERVATIONS … No interning, no
        # resolution"*) is that it performs none.
        #
        # ⚑⚑ THE COST WAS NOT LAYERING TIDINESS, IT WAS THE COMMIT GRAIN (operator, 2026-08-22:
        # *"that recovery should be EXPECTED to happen at internment time, not event writing
        # time… that's one of the key values behind having tiny commits"*). With recovery at
        # write time the `ekey` is a function of WHICH RECOVERY VERSION RAN, so improving
        # recovery re-keys the tier — the all-or-nothing migration the deleted block below
        # documented at length. That is precisely the un-resumable, whole-corpus act the
        # ingest→intern→reflect→retire cycle was rebuilt to eliminate: a recovery fix could not
        # be landed incrementally, because a partially re-ingested tier holds TWO keyings of
        # the same content, both well-formed, and no constraint in the schema can see it.
        #
        # ⚑ AT INTERN TIME THE SAME FIX IS A RE-PROJECTION. Events are untouched; `obs_node` is
        # rebuilt per core, which is already the resumable unit (`--project-core`,
        # residue-driven, one core per step, `_seed_node_ids` recovering the signature map on
        # every additive run). Same reasoning as ⟡project-granularity: put the work at the
        # grain the cycle already supports rather than inventing a mechanism for it.
        #
        # ⚑ AND IT REMOVES A CONSTRAINT FROM EVERY FUTURE PRODUCER. With recovery at write
        # time, a python or SQL producer would have to reimplement it IDENTICALLY or the tier
        # holds two keyings — the exact divergence a shared kernel exists to prevent.
        # Downstream, recovery is common to all producers by construction.
        #
        # ⚑⚑⚑ THE KEY IS UNCHANGED, AND MY FIRST CUT AT THIS CHANGED IT ON A FALSE PREMISE.
        # I dropped `q`/`i` from `obs_rec` believing them a vestigial v1 field shape the v2
        # walker never emits. REFUTED by the store (`schema.py --live --sample event`):
        #
        #     ekey ⟨'{"c": "QName", "ch": [262461, 262487], "i": null,
        #             "q": "Substrate.Foundation.Product.Σ.proj₂"}'⟩   qname_pid 'nsra8Sr1Y0k'
        #
        # Recovery WORKS and populates them exactly where applicable — a `QName` node carries
        # its qname; `Arg` and `[]` nodes legitimately do not. The 95%/97% NULL rates are
        # CONSTRUCTORS WITHOUT QNAMES, not recovery misses. So dropping them would LOSE
        # discrimination: every `QName` with the same children would key identically.
        #
        # ⚑ THREE SUCCESSIVE READINGS OF THOSE COLUMNS WERE WRONG (sparse-payload → vestigial-v1
        # → recovery-missed), each derived from a census rather than from the rows. One
        # `--sample` settled it. A NULL RATE CANNOT DISTINGUISH "not applicable" FROM "not
        # recovered", and only opening the data can.
        #
        # ⚑⚑ WHAT REMAINS TRUE IS THE LAYERING, WHICH IS WHY THIS BLOCK STAYS. `q`/`i` are
        # DERIVED, and deriving them at write time makes the content-address a function of the
        # DERIVER'S VERSION — so improving recovery re-keys the tier. That is the un-resumable
        # act the cycle exists to prevent, and it is orthogonal to whether the values belong in
        # the key (they do).
        #
        # ⚑ THE FIX IS VERSIONING, NOT REMOVAL (operator, 2026-08-22: *"sounds like ekeys need
        # versioning, so that conjuncts can be applied per-version"*). `recover_fields` already
        # names the gap — *"there is no version tag on the JSON … so field-presence IS the
        # discriminator"* — and field-presence is exactly what forces the migration to be
        # atomic: "v2 without a qname" and "v3 that has no qnames" are indistinguishable. A `v`
        # INSIDE the document (not a column beside it — that would be a second fact needing
        # atomicity with the key it describes, the stored-cursor defect this store retired
        # twice) makes the keyings coexist legitimately and lets the licence dispatch per row.
        # Filed as ⟡ekey-version; NOT done here, because the first versioned write IS the
        # migration boundary and that is a stated act, not a side effect of an edit.
        qname, idx, litval = recover_fields(rec, dec["nodes"])
        obs_rec = {"c": ctor, "q": qname, "i": idx, "ch": kids}
        if litval:
            obs_rec["l"] = litval
        content = json.dumps(obs_rec, sort_keys=True, ensure_ascii=False)
        ekey = _b64(content)
        erows.append((ekey, tid(ctor), (pid(qname) if qname else None), idx, tid(litval)))
        orows.append((cid, lid, ekey))
        edgerows += [(cid, lid, o, ch) for o, ch in enumerate(kids)]
    dms = dec["defmarks"]
    root_of = {}  # qname → root, LAST-WINS per core (matches reuse_catalog)
    for d in dms:
        root_of[d["unit"]] = d["root"]

    def uid(qn, r):
        return _b64(qn + "\x00" + str(r))

    urows = [
        (
            cid,
            uid(d["unit"], d["root"]),
            pid(d["unit"]),
            d["root"],
            tid(d.get("kind", "?")),
            mpid,
            1 if d.get("copy") else 0,  # defCopy provenance: instantiation-copy vs original
            d.get("level"),
        )  # ⟡gqs-S0.2: elaborated universe level (level>=1 ⟺ Set₁)
        for d in dms
    ]
    mrows = []
    for d in dms:
        su = uid(d["unit"], d["root"])
        for o, m in enumerate(d.get("members", [])):
            mr = root_of.get(m)
            mrows.append((cid, su, o, pid(m), (uid(m, mr) if mr is not None else None)))
    # ⚑ ONE CAPABILITY, WAS SIX HAND-WRITTEN SPELLINGS — each hardcoding three
    # sqlite-isms: `OR IGNORE` (postgres: `ON CONFLICT DO NOTHING`), the `?` paramstyle
    # (postgres: `%s`), and a positional VALUES arity maintained by hand. That last one
    # already bit this session: adding `producer` to `core_fp` meant editing `(?,?)` to
    # `(?,?,?)` here, and any site left unedited would have written 2 values into 3
    # columns. `schema.upsert` reads the arity off the declaration, so the same mistake
    # now raises instead of shifting data.
    _schema.upsert(con, "event", erows)
    _schema.upsert(con, "obs", orows)
    _schema.upsert(con, "edge", edgerows)
    _schema.upsert(con, "unit_obs", urows)
    _schema.upsert(con, "unit_member", mrows)
    # ⚑ THREE COLUMNS — `path` WAS ADDED HERE AND REMOVED AGAIN (ⓟ). `cid` IS the term id of
    # `relpath`, so the path is already stored in `terms` under this very id; a `core_fp.path`
    # column was a second copy of that fact, and `core_path` reading the copy rather than the
    # original is how two sources of truth drift apart unnoticed.
    _schema.upsert(con, "core_fp", [(cid, mtime, producer)], on_conflict="replace")
    return True
