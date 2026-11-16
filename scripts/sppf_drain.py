#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""sppf_drain.py — ⟡ladder-retire: the CALLER. Retire the `sourced` tier, one statement each.

⚑⚑ THE FIXPOINT AND EVERY MODE-BRANCH LIVE HERE AND THE RUNGS DO NOT — `sppf_tree.py`'s seam,
inherited. `jea/metalanguage/dec_drain.py` scores `pycodemod --control` **0**; "run the rebuild
until it writes nothing" is a loop and therefore this file's job.

    --drain-rebuild            the value fixpoint — `dec_val` until a round writes 0 rows
    --drain-root [RELPATH]     build tier B+2's HEADER, under the reconstruction predicate
    --drain-licence [RELPATH]  the DRY RUN — licensed / mismatch / no-header, per document
    --drain-apply [RELPATH]    THE RETIRE — delete only on equality. Writes.
    --drain-answer [RELPATH]   read documents back from the durable tiers ALONE
    --drain-oracle [RELPATH]   the SQL shadow against python `recon` — the ORACLE
    --drain-stage [RELPATH]    retire `treestage` — a CLEANUP, not a rung. Writes.
    --drain-restore [RELPATH]  the retire's INVERSE — `sourced` FROM the shadow. Writes.
    --drain-census             the populations: sourced / headers / memo / held / bytes
    --drain-concurrency [N]    N retirers AT ONCE; reports 40P01 and exactly-once
    --drain-sql                the rungs VERBATIM — the statements the engine is sent

⚑ ITS OWN TOOL AND NOT MORE MODES ON `sppf_db`, which is at 1,183 of 1,200 code lines. What
`sppf_db` still owns is the SUITE (`drain_cases`), because `run_selftests.discover()` counts a
suite as the PAIR of a `_selftest` def and a dispatch on the selftest flag — defining neither
here keeps the suite total at 69.

⚑⚑ AND THIS FILE MUST NOT SPELL THAT FLAG AS A LITERAL — `sppf_tree`/`sppf_vocab`'s measured
incident, inherited verbatim: `run_selftests.HANDLES_SELFTEST` is a bare `re.compile` matched
over the WHOLE source, so a PARAGRAPH explaining that this module is not a suite is what would
make the runner treat it as one. The defect is in the proxy and is deliberately not repaired
here.

⚑ THE DEFAULT MODE IS THE **DRY RUN**. A tool whose bare-ish invocation deletes the corpus is
the defect; `--drain-licence` is what an unrecognised invocation falls through to, and every
writing mode has to be named.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))

import schema as _schema  # THE schema declaration: rows/execute/apply
import dec_drain as _R  # THE statements — data only, `--control` 0


def _connect(sandbox):
    """The store this invocation writes — sandbox or live, resolved ONCE.

    ⚑ ONE RESOLVER, NOT PER-DISPATCH — `schema_rows._cli_connect`'s recorded defect is a
    per-mode `sandbox_connect(...) if …` line that left the READ modes silently on the live
    store while the WRITE modes honoured the flag. In a tool that DELETES, the wrong-tenant
    read is the benign half.
    """
    import store

    return (
        store.sandbox_connect(reset=False) if sandbox else store.connect(mode="rw", require=False)
    )


def _tiers(con):
    """ASSERT the tiers this tool touches are established. Creates nothing, commits nothing.
    ⚑ NOT `sourced`, NOT `vocab`, NOT `tree`'s neighbours it only reads.

    ⚑⚑⚑ THIS APPLIED DDL AND COMMITTED, UNCONDITIONALLY, ON ENTRY TO ALL TEN CALLERS —
    including `--drain-census` (*"the populations. Writes nothing"*) and `--drain-licence`
    (*"the dry run. Writes nothing"*). Two docstrings claiming to write nothing, above a
    function that issued `CREATE … IF NOT EXISTS` + `COMMIT` before reading a row. DDL is a
    WRITE (operator, 2026-08-24: *"DDL of any kind counts as a write hazard, subject to the
    --dry vs --apply, typed operations restrictions"*), so a read path may hold none of it.

    ⚑⚑ AND THE SHADOW ARGUMENT SURVIVES INTACT — it just picks a different verb. `tree` is
    REQUIRED because the shadow is part of that tier's DDL and the licence cannot be asked
    without it; `valstage` because this caller fills it. Both are met by establishing once
    (`schema.py --establish tree valstage --apply`), which is where a precondition belongs.
    Applying per invocation made every read a check-then-act against the relation lock, in a
    tool that ships `--drain-concurrency` to fan N of these at the store at once.

    ⚑ THE REFUSAL IS THE OLD REASONING GENERALISED, not a new stance. This docstring already
    argued that creating `core_decoded` would turn *"you have not sourced anything"* into a
    successful drain of an empty table — correct, and it applied to every tier EXCEPT the two
    the function created for itself.
    """
    _schema.require_tiers(con, ("tree", "valstage"), label="sppf_drain")


def _core_id(con, relpath):
    """The `core_id` of a document, read from `dec_root` OR `core_decoded` — or None for all.

    ⚑⚑ TWO SOURCES, AND THAT IS THE WHOLE POINT OF THE ARC. `sppf_tree._core_id` reads
    `core_decoded`, which is the relation this tool DELETES — so after a drain a scoped
    invocation would report "no such document" for a document the store answers for perfectly
    well. The header is checked first because it is the durable one.

    ⚑ READ, NEVER RECOMPUTED — `sppf_vocab._core_id`'s rule: `_content_addr._addr` gives the
    same answer today, which is exactly what makes a second authority dangerous.
    """
    if relpath is None:
        return None, True
    cid = _schema.scalar(con, "SELECT core_id FROM dec_root WHERE relpath = %s", (relpath,))
    if cid is None:
        cid = _schema.scalar(con, "SELECT core_id FROM core_decoded WHERE relpath = %s", (relpath,))
    return cid, cid is not None


def _exec(con, pair):
    """Run a `(sql, params)` pair and return its `rowcount` — the observable."""
    cur = con.cursor()
    cur.execute(pair[0], pair[1])
    return max(0, getattr(cur, "rowcount", 0))


def rebuild(con):
    """THE FIXPOINT: the rebuild rung until a round writes nothing. Returns `(rounds, rows)`.

    ⚑⚑ THE TERMINATION CONDITION IS THE ROWCOUNT, NOT A SCHEDULE, and that is the difference
    from `sppf_tree.run_rounds`. The build's rounds were numbered in advance because a spine
    cell needed the NEXT cell's engine-assigned id; here `interior_pos` excludes what already
    has a memo row, so the rung is self-terminating and the round count is a MEASUREMENT of
    the corpus's JSON nesting rather than a number computed from it.

    ⚑ ONE COMMIT PER ROUND, LOAD-BEARING RATHER THAN TIDY — round `r+1` resolves its children
    with an ordinary PK lookup against a FRESH snapshot, so an uncommitted round `r` would be
    invisible to a concurrent writer and would stall it silently.
    """
    rounds, rows = 0, 0
    n = _exec(con, _R.rebuild_sql())
    con.commit()
    while n:
        rounds, rows = rounds + 1, rows + n
        n = _exec(con, _R.rebuild_sql())
        con.commit()
    return rounds + 1, rows


def licence(con, core_id=None):
    """Every document in scope with its verdict — the DRY RUN, writing nothing."""
    return [dict(r) for r in _schema.rows(con, *_R.licence_sql(core_id))]


def drain_census(con):
    """The drain's populations, one dict."""
    for r in _schema.rows(con, *_R.census_sql()):
        return dict(r)
    return {}


def licence_report(rs, res):
    """Render the licence — the HELD set first, because that is the number that means anything.

    ⚑ A DRAIN LICENCE THAT HAS NEVER REFUSED IS THE DEFECT THIS ARC OPENED WITH, so the
    refusals are printed with their documents and the acceptances are a count. The asymmetry
    is deliberate: "37 held" is a state somebody has to act on, "6 licensed" is not.
    """
    by = {}
    for r in rs:
        by.setdefault(r["verdict"], []).append(r)
    print("  ⟡ladder-retire LICENCE — core_decoded vs core_decoded_shadow (tier `tree`)")
    print(
        "     LICENSED  %s of %s document(s) — the shadow reproduces `dec` exactly"
        % (format(len(by.get("licensed", ())), ","), format(len(rs), ","))
    )
    for v in ("mismatch", "no-header"):
        held = by.get(v, ())
        print("     HELD      %s %s" % (format(len(held), ","), v))
        for r in held[:8]:
            print("        %-64s %s byte(s)" % (r["relpath"][-64:], format(r["bytes"], ",")))
        if len(held) > 8:
            print("        … %s more" % format(len(held) - 8, ","))
    print(
        "     POPULATION sourced %s · headers %s · memo %s · shadow %s · HELD %s"
        % (
            format(res["sourced"], ","),
            format(res["headers"], ","),
            format(res["memo"], ","),
            format(res["shadow"], ","),
            format(res["held"], ","),
        )
    )
    print(
        "     treestage dec_stage %s · dec_ref %s · sourced bytes %s · stale memo row(s) %s"
        % (
            format(res["staged"], ","),
            format(res["refs"], ","),
            format(res["bytes"], ","),
            format(res["stale_memo"], ","),
        )
    )


# ── THE ORACLE — the SQL shadow against `sppf_tree.rebuild`, which is python `recon` ─────────
#
# ⚑⚑ THE BRIEF'S RULE, HONOURED LITERALLY: *"the Python `recon` becomes the ORACLE the SQL is
# verified against, not the mechanism."* `sppf_tree.rebuild` walks `dec_node` in python — spine
# iteratively, nesting recursively — and is the function ⟡ladder-4 proved 6/6 exact against
# `dec`. This asks whether the SQL shadow agrees with it NODE FOR NODE, which is a stronger
# question than "does the shadow equal `dec`": the latter is answerable only while `dec`
# exists, and the oracle keeps working afterwards.
#
# ⚑ A MALFORMED TREE MUST **FAIL**, NOT CRASH — `roundtrip`'s measured repair, inherited: the
# oracle is handed whatever the store holds, so a wrong tree is its NORMAL input.
def oracle(con, relpath=None):
    """Per document: does `core_decoded_shadow.dec` equal python `recon` of the same root?"""
    import sppf_tree as _T

    out = []
    for r in _schema.rows(
        con,
        "SELECT d.core_id, d.relpath, d.root, s.dec FROM dec_root d "
        "LEFT JOIN core_decoded_shadow s ON s.core_id = d.core_id "
        "WHERE (%s::text IS NULL OR d.relpath = %s::text) "
        "ORDER BY d.relpath",
        (relpath, relpath),
    ):
        try:
            want = _T.rebuild(_T.read_tree(con, r["root"]), r["root"])
        except (KeyError, RecursionError):  # noqa: BLE001 — the class is the point
            out.append((r["relpath"], False, "python recon refused this tree"))
            continue
        out.append((r["relpath"], want == r["dec"], "shadow is NULL" if r["dec"] is None else "ok"))
    return out


# ── THE ACCEPTANCE TEST — retired documents remain answerable, byte for byte ─────────────────
#
# ⚑⚑ THE COMPARISON IS AGAINST A COPY TAKEN **BEFORE** THE DELETE, WHICH IS THE ONLY HONEST
# FORM. After the drain there is nothing left to compare to, so an "acceptance" run afterwards
# could only compare the shadow to itself. The copy lives in this process, never in the store —
# a second stored copy would be a tier nobody declared.
def drain_apply(con, core_id=None):
    """Snapshot, retire, then prove every retired document still reads back. Returns a dict."""
    before = {
        r["core_id"]: (r["relpath"], r["dec"])
        for r in _schema.rows(
            con,
            "SELECT core_id, relpath, dec FROM core_decoded c "
            "WHERE (%s::text IS NULL OR c.core_id = %s::text)",
            (core_id, core_id),
        )
    }
    n = _exec(con, _R.retire_sql(core_id))
    con.commit()
    after = {
        r["core_id"]
        for r in _schema.rows(
            con,
            "SELECT core_id FROM core_decoded c WHERE (%s::text IS NULL OR c.core_id = %s::text)",
            (core_id, core_id),
        )
    }
    gone = [c for c in before if c not in after]
    rebuilt, refused = [], []
    for c in gone:
        got = _schema.rows(con, "SELECT dec FROM core_decoded_shadow WHERE core_id = %s", (c,))
        rows = [r["dec"] for r in got]
        # ⚑ EXACTLY ONE SHADOW ROW, AND THE COUNT IS PART OF THE CHECK. A duplicate would mean
        # two headers claim one document, which `dec_root`'s PK makes unrepresentable — read
        # back rather than trusted, the same way `--tree-concurrency` reads EXACTLY-ONCE off
        # `rows == distinct ids` instead of citing the constraint.
        (rebuilt if (len(rows) == 1 and rows[0] == before[c][1]) else refused).append(c)
    return {
        "deleted": n,
        "gone": len(gone),
        "rebuilt": len(rebuilt),
        "refused": len(refused),
        "held": len(after),
        "refused_paths": [before[c][0] for c in refused][:8],
    }


# ── the CLI ──────────────────────────────────────────────────────────────────────────────────
def rebuild_cli(sandbox=False):
    """`--drain-rebuild`: the value fixpoint."""
    con = _connect(sandbox)
    _tiers(con)
    rounds, rows = rebuild(con)
    res = drain_census(con)
    con.close()
    print("  ⟡ladder-retire REBUILD — dec_val, the reconstruction's memo")
    print(
        "     ROUNDS %s statement(s) · %s memo row(s) written · %s total"
        % (format(rounds, ","), format(rows, ","), format(res["memo"], ","))
    )
    print("     ⚑ the round count is the corpus's JSON NESTING, not its spine length —")
    print("       a 115,268-member object is ONE statement (spine walk + outer aggregate)")
    return 0


def root_cli(args, sandbox=False):
    """`--drain-root [RELPATH]`: build tier B+2's header, under the reconstruction predicate."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --drain-root: no document named %r in dec_root or core_decoded" % args[0])
        con.close()
        return 2
    n = _exec(con, _R.root_sql(cid))
    con.commit()
    res = drain_census(con)
    con.close()
    print("  ⟡ladder-retire HEADER — dec_root, the part of tier `tree` that names a document")
    print(
        "     WROTE %s header(s) · %s total · over %s sourced document(s)"
        % (format(n, ","), format(res["headers"], ","), format(res["sourced"], ","))
    )
    print("     ⚑ a header is written ONLY where the rebuilt value IS NOT DISTINCT FROM `dec` —")
    print("       %s document(s) are therefore still HELD" % format(res["held"], ","))
    return 0


def licence_cli(args, sandbox=False):
    """`--drain-licence [RELPATH]`: the dry run. Writes nothing."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --drain-licence: no document named %r" % args[0])
        con.close()
        return 2
    rs, res = licence(con, cid), drain_census(con)
    con.close()
    licence_report(rs, res)
    # ⚑ AN EMPTY POPULATION IS NOT A PASS — the shape this arc has fixed at three tiers now.
    return 0 if rs else 1


def apply_cli(args, sandbox=False):
    """`--drain-apply [RELPATH]`: THE RETIRE. Delete only on equality, then prove answerable."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --drain-apply: no document named %r" % args[0])
        con.close()
        return 2
    r = drain_apply(con, cid)
    res = drain_census(con)
    con.close()
    print("  ⟡ladder-retire DRAIN — DELETE FROM core_decoded, licensed by core_decoded_shadow")
    print(
        "     DELETED   %s row(s) · %s document(s) left in `sourced`"
        % (format(r["deleted"], ","), format(res["sourced"], ","))
    )
    print(
        "     REBUILT   %s of %s retired document(s) read back byte-for-byte from the"
        % (format(r["rebuilt"], ","), format(r["gone"], ","))
    )
    print("               durable tiers ALONE (dec_root ⋈ dec_node ⋈ dec_scalar ⋈ dec_val)")
    print("     REFUSED   %s" % format(r["refused"], ","))
    for p in r["refused_paths"]:
        print("        ⚑ %s" % p)
    print("     HELD      %s document(s) the licence would not pass" % format(res["held"], ","))
    return 0 if (r["refused"] == 0 and r["gone"] == r["rebuilt"]) else 1


def answer_cli(args, sandbox=False):
    """`--drain-answer [RELPATH]`: read documents back from the durable tiers alone."""
    con = _connect(sandbox)
    _tiers(con)
    rs = [dict(r) for r in _schema.rows(con, *_R.answer_sql(args[0] if args else None))]
    con.close()
    print("  ⟡ladder-retire ANSWER — core_decoded_shadow, reading NO `core_decoded` row")
    for r in rs[:12]:
        print(
            "     %-58s %s byte(s) · mtime %s · %s"
            % (r["relpath"][-58:], format(len(str(r["dec"])), ","), r["mtime"], r["producer"])
        )
    if len(rs) > 12:
        print("     … %s more" % format(len(rs) - 12, ","))
    print("     %s document(s) answered" % format(len(rs), ","))
    return 0 if rs else 1


def oracle_cli(args, sandbox=False):
    """`--drain-oracle [RELPATH]`: the SQL shadow against python `recon`."""
    con = _connect(sandbox)
    _tiers(con)
    rs = oracle(con, args[0] if args else None)
    con.close()
    bad = [r for r in rs if not r[1]]
    print("  ⟡ladder-retire ORACLE — core_decoded_shadow vs sppf_tree.rebuild (python `recon`)")
    print(
        "     %s of %s document(s) AGREE exactly"
        % (format(len(rs) - len(bad), ","), format(len(rs), ","))
    )
    for relpath, _ok, why in bad[:10]:
        print("     ⚑ DIVERGENCE  %s  (%s)" % (relpath, why))
    return 0 if (rs and not bad) else 1


def stage_cli(args, sandbox=False):
    """`--drain-stage [RELPATH]`: retire `treestage`. A CLEANUP, not a rung. Writes."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --drain-stage: no document named %r" % args[0])
        con.close()
        return 2
    nr = _exec(con, _R.retire_ref_sql(cid))
    ns = _exec(con, _R.retire_stage_sql(cid))
    con.commit()
    res = drain_census(con)
    con.close()
    print("  ⟡ladder-retire TREESTAGE — a CLEANUP, licensed by the header's existence")
    print(
        "     DELETED dec_ref %s · dec_stage %s   (remaining: %s / %s)"
        % (format(nr, ","), format(ns, ","), format(res["refs"], ","), format(res["staged"], ","))
    )
    print("     ⚑ NOT an instance of the model: nothing sits above `treestage` and nothing")
    print("       reconstructs from it, so `B+2` does not resolve. The ORDER is the model's —")
    print("       `dec_ref` is where a root lives until `dec_root` exists.")
    return 0


def restore_cli(args, sandbox=False):
    """`--drain-restore [RELPATH]`: materialise `sourced` back FROM the shadow. Writes."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --drain-restore: no document named %r" % args[0])
        con.close()
        return 2
    n = _exec(con, _R.restore_sql(cid))
    con.commit()
    res = drain_census(con)
    con.close()
    print("  ⟡ladder-retire RESTORE — the retire's INVERSE, `sourced` from the shadow")
    print(
        "     WROTE %s row(s) · sourced %s · HELD %s"
        % (format(n, ","), format(res["sourced"], ","), format(res["held"], ","))
    )
    print("     ⚑ a tier is an EFFICIENCY fact, not an AVAILABILITY fact — this is that")
    print("       claim made operational, and it is what makes the drain repeatable")
    return 0


def census_cli(sandbox=False):
    """`--drain-census`: the populations. Writes nothing."""
    con = _connect(sandbox)
    _tiers(con)
    res = drain_census(con)
    con.close()
    print("  ⟡ladder-retire CENSUS")
    print(
        "     sourced %s · headers %s · shadow %s · HELD %s"
        % (
            format(res["sourced"], ","),
            format(res["headers"], ","),
            format(res["shadow"], ","),
            format(res["held"], ","),
        )
    )
    print(
        "     memo %s · dec_stage %s · dec_ref %s · sourced bytes %s · stale memo %s"
        % (
            format(res["memo"], ","),
            format(res["staged"], ","),
            format(res["refs"], ","),
            format(res["bytes"], ","),
            format(res["stale_memo"], ","),
        )
    )
    return 0


def _opt_int(argv, flag, default):
    """The integer following `flag` in `argv`, or `default`.

    ⚑ THE NEXT **FLAG** IS NOT MISTAKEN FOR N — `sppf_vocab._opt_int`'s measured edge:
    `int("--sandbox")` raises, and a `try/except: 0` would run ZERO processes and report a
    clean verdict over nothing.
    """
    argv = list(argv)
    if flag not in argv:
        return default
    i = argv.index(flag)
    n = argv[i + 1] if len(argv) > i + 1 else ""
    return int(n) if n.isdigit() else default


def drain_concurrency(n, sandbox=True):
    """Run `n` `--drain-apply` callers AT ONCE and report 40P01 and exactly-once.

    ⚑⚑ A MODE, NOT A SHELL FAN-OUT — `tree_concurrency`'s argument verbatim: launching N
    background jobs and reading N outputs is reasoning performed in the turn.

    ⚑⚑ THE CONTENDED OBJECT HERE IS A **DELETE**, WHICH IS A DIFFERENT SHAPE FROM EVERY EARLIER
    RUNG IN THIS LADDER. `dec_node`/`dec_scalar`/`dec_val` are content-keyed inserts arbitrated
    by `ON CONFLICT DO NOTHING`; a DELETE has no such arbiter, so N writers race for the SAME
    rows and exactly-once means "the rowcounts SUM to the population", not "each got them all".
    Postgres's DELETE takes no `ORDER BY`, so the only thing keeping the acquisition order
    common is that every process sends the IDENTICAL statement and therefore gets the identical
    plan. That is weaker than a declared order and is stated as weaker; this mode is what
    measures it.

    ⚑ IT REPORTS AND DOES NOT REPAIR. No retry, no backoff, no serialisation. Under this
    architecture a deadlock is a DESIGN VIOLATION and clearing it destroys the evidence.
    """
    import subprocess

    con = _connect(sandbox)
    _tiers(con)
    before = drain_census(con)
    lic = [r for r in licence(con) if r["verdict"] == "licensed"]
    con.close()
    if not lic:
        # ⚑ AN EMPTY SAMPLE IS A FACT ABOUT THE STORE, NOT A PASS — in an instrument whose whole
        # job is to detect a rare event, "0 deletable rows, 0 deadlocks" is worthless.
        print("  ⚑ no document is licensed — nothing was run, nothing is claimed")
        return 1
    tool = os.path.join(_ROOT, "scripts", "sppf_drain.py")
    procs = [
        subprocess.Popen(
            [sys.executable, tool, "--drain-apply"] + (["--sandbox"] if sandbox else []),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for _ in range(n)
    ]
    outs = [(pr.wait(), pr.stdout.read(), pr.stderr.read()) for pr in procs]
    con = _connect(sandbox)
    after = drain_census(con)
    con.close()
    # ⚑ `40P01` IS THE SQLSTATE AND IS WHAT IS MATCHED, not the word "deadlock": psycopg spells
    # the exception `DeadlockDetected` and the server message is localisable; the SQLSTATE is
    # neither. Both are looked for — a match on either is a finding, a miss on both is the claim.
    dead = [
        (i, e) for i, (_rc, _o, e) in enumerate(outs) if "40P01" in e or "DeadlockDetected" in e
    ]
    fail = [(i, rc, e) for i, (rc, _o, e) in enumerate(outs) if rc != 0]
    tot = sum(
        int(w.replace(",", ""))
        for _rc, o, _e in outs
        for line in o.splitlines()
        if "DELETED" in line
        for w in line.split()[1:2]
    )
    print(
        "  ⟡ladder-retire CONCURRENCY — %d retirer(s) at once over %d licensed document(s)"
        % (n, len(lic))
    )
    print("     exit codes: %s" % ", ".join(str(rc) for rc, _o, _e in outs))
    print(
        "     core_decoded %s → %s · headers %s → %s"
        % (
            format(before["sourced"], ","),
            format(after["sourced"], ","),
            format(before["headers"], ","),
            format(after["headers"], ","),
        )
    )
    print(
        "     EXACTLY-ONCE: %s (Σ rowcounts %s == documents drained %s)"
        % (
            "YES" if tot == before["sourced"] - after["sourced"] else "**NO**",
            format(tot, ","),
            format(before["sourced"] - after["sourced"], ","),
        )
    )
    if dead:
        print("     ⚑⚑ 40P01 DEADLOCK — %d of %d process(es). VERBATIM:" % (len(dead), n))
        for i, e in dead[:2]:
            print("        [proc %d] %s" % (i, e.strip()[:1200]))
    else:
        print("     40P01 DEADLOCK: NONE observed in %d concurrent retirer(s)" % n)
    for i, rc, e in fail:
        if (i, e) not in dead:
            print("     ⚑ process %d exited %d — %s" % (i, rc, e.strip().splitlines()[-1:]))
    return 1 if (dead or fail or tot != before["sourced"] - after["sourced"]) else 0


#: The ⟡ladder-retire modes `drain_cli` owns. ⚑ ONE PLACE, so the dispatch and the mode set
# cannot disagree — a mode branched on but not declared here simply never fires, and
# `drain_cases` asserts the two agree on the AST rather than on the prose that names them.
DRAIN_MODES = {
    "--drain-rebuild",
    "--drain-root",
    "--drain-licence",
    "--drain-apply",
    "--drain-answer",
    "--drain-oracle",
    "--drain-stage",
    "--drain-census",
    "--drain-restore",
    "--drain-concurrency",
    "--drain-sql",
}


def drain_cli(argv, args):
    """The ⟡ladder-retire CLI — one entry point for the drain's ten modes."""
    argv = list(argv)
    sandbox = "--sandbox" in argv
    if "--drain-sql" in argv:
        # ⚑⚑ A MODE, BECAUSE "WHAT STATEMENT DELETES MY DATA?" IS A QUESTION AND ANSWERING IT
        # BY HAND IS THE THING THE STANDING RULE FORBIDS. It prints exactly what the writing
        # modes send. It touches no store and writes nothing.
        for label, pair in (
            ("REBUILD  (dec_val, one round)", _R.rebuild_sql()),
            ("HEADER   (dec_root, under the predicate)", _R.root_sql(None)),
            ("RETIRE   (core_decoded, delete only on equality)", _R.retire_sql(None)),
            ("RESTORE  (core_decoded, the retire's inverse)", _R.restore_sql(None)),
            ("CLEANUP  (dec_ref)", _R.retire_ref_sql(None)),
            ("CLEANUP  (dec_stage)", _R.retire_stage_sql(None)),
        ):
            print("-- ── %s ──" % label)
            print(pair[0])
            print("-- parameters: %r  (NULL scope = every document)\n" % (pair[1],))
        return 0
    if "--drain-rebuild" in argv:
        return rebuild_cli(sandbox)
    if "--drain-root" in argv:
        return root_cli(args, sandbox)
    if "--drain-apply" in argv:
        return apply_cli(args, sandbox)
    if "--drain-answer" in argv:
        return answer_cli(args, sandbox)
    if "--drain-oracle" in argv:
        return oracle_cli(args, sandbox)
    if "--drain-stage" in argv:
        return stage_cli(args, sandbox)
    if "--drain-restore" in argv:
        return restore_cli(args, sandbox)
    if "--drain-census" in argv:
        return census_cli(sandbox)
    if "--drain-concurrency" in argv:
        return drain_concurrency(_opt_int(argv, "--drain-concurrency", 8), sandbox=sandbox)
    return licence_cli(args, sandbox)


def drain_cases(check):
    """The ⟡ladder-retire guarded cases, driven from `sppf_db._selftest`.

    ⚑ THE CASES LIVE BESIDE THE CODE AND THE SUITE STAYS WHERE IT WAS — `tree_cases`'s
    precedent: `run_selftests.discover()` counts a suite as the PAIR of a `_selftest` def and a
    dispatch on the selftest flag, so defining neither here adds no suite and the total stays 69.

    ⚑⚑ THE FIXTURE CARRIES A DOCUMENT THE LICENCE MUST **REFUSE**, ON PURPOSE. A drain licence
    that has never refused is the defect this arc opened with, so `fixture/held.agdai` is built
    into the tree and then has one `dec_ref` row removed, which leaves its tree INCOMPLETE — the
    header cannot be written, the shadow holds no row, and the document is held. It is then
    repaired and licensed. Both directions are asserted, in that order.
    """
    import json as _json
    import sppf_tree as _T
    import sppf_vocab as _V

    con = _schema.sandbox_fixture("sppf_drain")

    # ⚑ TWO DOCUMENTS THAT SHARE STRUCTURE, because the drain's hardest property is that
    # deleting one document may not disturb another's reconstruction — content sharing means
    # `{"b":2,"c":3}` is ONE node in both, and a per-document delete must not reach it.
    a = {
        "e_obj": {},
        "e_arr": [],
        "tail": {"a": 1, "b": 2, "c": 3},
        "alone": {"b": 2, "c": 3},
        "arr3": [7, 8, 9],
        "deep": [[{"k": [1]}]],
        "k": "k",
    }
    b = {"alone": {"b": 2, "c": 3}, "new": [1], "n": None, "t": True, "z": 0}
    for cid, path, doc in (("d1", "fixture/drain.agdai", a), ("d2", "fixture/held.agdai", b)):
        _schema.execute(
            con,
            "INSERT INTO core_decoded (core_id, relpath, mtime, dec) VALUES (%s, %s, 7, %s)",
            (cid, path, _json.dumps(doc)),
        )
    con.commit()
    _V.intern_scalars(con)
    con.commit()
    # ⚑ ONLY `d1`'s TREE IS BUILT HERE. `d2` is left with NO tree at all so the licence has a
    # document it must refuse before it has one to pass — the order matters, because a licence
    # first observed passing is a licence nobody has seen say no.
    try:
        _T.build_skeleton(con, "d1")
        con.commit()
        _T.run_rounds(con, "d1")
        con.commit()
        rounds, memo = rebuild(con)
    except Exception as _err:  # noqa: BLE001 — naming IS the job
        con.rollback()
        check("the drain's relations and rungs RUN at all", str(_err), "")
        con.close()
        return
    check(
        "the reconstruction fixpoint terminates and writes a memo",
        (rounds > 0, memo > 0),
        (True, True),
    )
    # ⚑⚑ THE ROUND COUNT IS THE JSON NESTING, NOT THE SPINE LENGTH — the claim the whole cost
    # argument rests on, and the one a fixture with 9-member spines can actually witness.
    # `deep` is `[[{"k":[1]}]]`, four levels, so this must be small and MUST NOT scale with the
    # 9-member objects beside it.
    check(
        "...in a number of rounds bounded by the JSON nesting, not by any sequence length",
        rounds <= 8,
        True,
    )

    # ── the LICENCE REFUSES BEFORE IT LICENSES ──────────────────────────────────────────
    # ⚑ NO HEADER HAS BEEN BUILT YET, so EVERY document is held. A licence that passed here
    # would be passing on the strength of the tree existing, which is the structural check
    # F31 measured as insufficient.
    _l0 = {r["relpath"]: r["verdict"] for r in licence(con)}
    check(
        "with no header built, the licence HOLDS every document",
        sorted(set(_l0.values())),
        ["no-header"],
    )
    _exec(con, _R.root_sql(None))
    con.commit()
    _l1 = {r["relpath"]: r["verdict"] for r in licence(con)}
    check(
        "a document with NO tree is refused a header while its sibling is licensed",
        (_l1["fixture/drain.agdai"], _l1["fixture/held.agdai"]),
        ("licensed", "no-header"),
    )
    # ⚑⚑ AND A **PARTIALLY** BUILT TREE IS THE HARDER CASE, WHICH IS WHY IT IS SEPARATE. `d2`
    # shares `{"b":2,"c":3}` with `d1`, so most of its nodes ALREADY EXIST in `dec_node` before
    # a single round runs for it — a licence keyed on "are this document's nodes present" would
    # pass it here. The fixpoint is run to one round short of completion, which leaves the ROOT
    # unresolved while everything under it is built.
    import dec_tree as _TD

    _T.build_skeleton(con, "d2")
    con.commit()
    _sched = [r["rnd"] for r in _schema.rows(con, *_TD.rounds_sql("d2"))]
    for _rnd in _sched[:-1]:
        _exec(con, _TD.round_sql(_rnd, "d2"))
        con.commit()
    rebuild(con)
    _exec(con, _R.root_sql(None))
    con.commit()
    _l2 = {r["relpath"]: r["verdict"] for r in licence(con)}
    check(
        "...and a tree built to one round SHORT of its root is still refused",
        (
            _l2["fixture/held.agdai"],
            _schema.scalar(con, "SELECT count(*) FROM dec_ref WHERE core_id='d2'") > 0,
        ),
        ("no-header", True),
    )
    # ⚑ THE REPAIR LICENSES IT — the other half, without which "it refuses" is just "it never
    # passes". The rung that closes the gap is the TREE's, not the drain's: the drain reports
    # and the builder repairs, which is the tier separation doing its job.
    _exec(con, _TD.round_sql(_sched[-1], "d2"))
    con.commit()
    rebuild(con)
    _exec(con, _R.root_sql(None))
    con.commit()
    _l3 = {r["relpath"]: r["verdict"] for r in licence(con)}
    check(
        "...and once the LAST round runs, the SAME licence passes it",
        sorted(set(_l3.values())),
        ["licensed"],
    )

    # ── the SHADOW is the reconstruction, and it agrees with python `recon` ─────────────
    check(
        "the shadow reproduces `dec` for every document, byte for byte",
        _schema.scalar(
            con,
            "SELECT count(*) FROM core_decoded c JOIN core_decoded_shadow s "
            "ON s.core_id = c.core_id WHERE s.dec IS NOT DISTINCT FROM c.dec",
        ),
        2,
    )
    # ⚑⚑ THE ORACLE IS THE REPO'S OWN `recon`, NOT A SECOND OPINION WRITTEN BESIDE IT.
    # `sppf_tree.rebuild` is the function ⟡ladder-4 proved 6/6 exact against `dec`; the SQL is
    # checked against it rather than against a fresh python walk written here.
    check(
        "...and agrees with python `recon` node for node",
        [(p, ok) for p, ok, _w in oracle(con)],
        [("fixture/drain.agdai", True), ("fixture/held.agdai", True)],
    )
    # ⚑ THE HEADER CARRIES THE COLUMNS `dec_node` CANNOT. Without them the tier does not
    # reconstruct `core_decoded` at all, and the drain would be deleting facts nothing holds.
    check(
        "the shadow carries relpath, mtime and producer — not just `dec`",
        [
            (r["relpath"], r["mtime"], r["producer"])
            for r in _schema.rows(con, *_R.answer_sql("fixture/drain.agdai"))
        ],
        [("fixture/drain.agdai", 7, "agdai")],
    )

    # ── THE DELETE-TIME RE-ASK — why the predicate is a WHERE clause in TWO statements ──
    # ⚑⚑ BOTH HEADERS WERE WRITTEN UNDER THE EQUALITY. Change what the DURABLE side says a
    # scalar is, and the SAME licence now REFUSES the document it passed a moment ago. A
    # build-time-only check would have banked "licensed" and deleted on the strength of it —
    # that is the check-then-act window the model names, and this is it being closed.
    #
    # ⚑ THE VICTIM IS A **KEY** OF `d2`'s ROOT OBJECT, chosen so the damage lands in the part
    # of the reconstruction the SHADOW computes inline rather than in the memo. A memo defect
    # can only cause a refusal (an absent row); a `dec_scalar` change alters a value the shadow
    # aggregates at delete time, which is the class this case has to exhibit.
    _leaf = _schema.scalar(con, "SELECT id FROM dec_scalar WHERE v = '\"new\"'::jsonb")
    _schema.execute(con, "UPDATE dec_scalar SET v = '\"CORRUPTED\"'::jsonb WHERE id = %s", (_leaf,))
    con.commit()
    _l5 = {r["relpath"]: r["verdict"] for r in licence(con)}
    check(
        "a durable tier CHANGED after the header reads as `mismatch`, never as `licensed`",
        (_l5["fixture/held.agdai"], _l5["fixture/drain.agdai"]),
        ("mismatch", "licensed"),
    )
    check("...and the retire rung deletes NOTHING for it", _exec(con, _R.retire_sql("d2")), 0)
    con.commit()
    _schema.execute(con, "UPDATE dec_scalar SET v = '\"new\"'::jsonb WHERE id = %s", (_leaf,))
    con.commit()
    check(
        "...and restoring the scalar restores the licence, with no header rewritten",
        (
            {r["relpath"]: r["verdict"] for r in licence(con)}["fixture/held.agdai"],
            _schema.scalar(con, "SELECT count(*) FROM dec_root"),
        ),
        ("licensed", 2),
    )

    # ── THE DRAIN, and the acceptance test ──────────────────────────────────────────────
    _r = drain_apply(con, None)
    check(
        "the drain deletes exactly the licensed documents and every one reads back",
        (_r["deleted"], _r["gone"], _r["rebuilt"], _r["refused"], _r["held"]),
        (2, 2, 2, 0, 0),
    )
    # ⚑⚑ ANSWERABLE WITH `core_decoded` EMPTY — the ladder's entire claim, as a SELECT.
    check(
        "...and the durable tiers answer for both documents with `sourced` now empty",
        (
            _schema.scalar(con, "SELECT count(*) FROM core_decoded"),
            _schema.scalar(con, "SELECT count(*) FROM core_decoded_shadow"),
        ),
        (0, 2),
    )
    # ⚑ IDEMPOTENCE: a second drain deletes 0. Not "reports 0" — the rowcount IS the observable.
    check("a second drain deletes NOTHING", _exec(con, _R.retire_sql(None)), 0)
    con.commit()
    # ⚑⚑ AND THE MEMO IS REBUILDABLE FROM THE DURABLE TIERS ALONE, WHICH IS WHAT MAKES IT
    # DISPOSABLE RATHER THAN A THIRD COPY OF THE CORPUS. `core_decoded` is empty and
    # `treestage` is about to be; flushing `dec_val` and re-running the fixpoint must restore
    # every answer. If this failed, `valstage` would be a tier nobody could rebuild — i.e. a
    # durable tier wearing a staging label.
    _schema.execute(con, "DELETE FROM dec_val")
    con.commit()
    check(
        "with the memo flushed the shadow answers for NOTHING — a refusal, never a wrong row",
        _schema.scalar(con, "SELECT count(*) FROM core_decoded_shadow"),
        0,
    )
    rebuild(con)
    check(
        "...and re-running the fixpoint from dec_node + dec_scalar alone restores every answer",
        _schema.scalar(con, "SELECT count(*) FROM core_decoded_shadow"),
        2,
    )
    # ⚑⚑ THE LINK IS INVERTIBLE, WHICH IS THE MODEL'S *"a record's TIER is an EFFICIENCY fact,
    # not an AVAILABILITY fact"* as a statement rather than a slogan. `drain ∘ restore` is a
    # fixpoint: the rows come back, the same licence passes them, and the same rung takes them
    # again. Without this the drain is a deletion with a good argument attached.
    _nr0 = _exec(con, _R.restore_sql(None))
    con.commit()
    check(
        "the shadow can REFILL the tier it shadows — the PROMOTE direction, spelled",
        (_nr0, _schema.scalar(con, "SELECT count(*) FROM core_decoded")),
        (2, 2),
    )
    check(
        "...and drain ∘ restore is a fixpoint: licensed again, retired again",
        (sorted(set(r["verdict"] for r in licence(con))), _exec(con, _R.retire_sql(None))),
        (["licensed"], 2),
    )
    con.commit()

    # ── the TREESTAGE cleanup, and its ORDERING constraint ──────────────────────────────
    _nr, _ns = (_exec(con, _R.retire_ref_sql(None)), _exec(con, _R.retire_stage_sql(None)))
    con.commit()
    check(
        "the treestage cleanup empties both staging relations",
        (
            _nr > 0,
            _ns > 0,
            _schema.scalar(con, "SELECT count(*) FROM dec_ref"),
            _schema.scalar(con, "SELECT count(*) FROM dec_stage"),
        ),
        (True, True, 0, 0),
    )
    # ⚑⚑ THE POINT OF THE ORDER, ASSERTED RATHER THAN EXPLAINED. With `core_decoded` empty AND
    # `treestage` empty, the ONLY thing that can still name a document is `dec_root` — and the
    # shadow still answers. Had the cleanup run first the roots would be unrecoverable.
    check(
        "with sourced AND treestage both empty, dec_root still names every document",
        [r["relpath"] for r in _schema.rows(con, *_R.answer_sql(None))],
        ["fixture/drain.agdai", "fixture/held.agdai"],
    )

    # ── THE DRIFT GATE — the purge's REAL objection, met rather than argued around ──────
    # ⚑⚑ ⟡view-purge's case against views was not the naming, it was that *"a DB view would be
    # a second spelling of the query algebra living OUTSIDE `--check`'s drift gate"* — a
    # deployed object can disagree with the fragment it was emitted from and nothing compares
    # them. This compares them, and the comparison has to go through POSTGRES on both sides:
    # `pg_get_viewdef` returns the engine's own normalisation of the stored rewrite, so
    # comparing it to the emitted TEXT would report drift on every whitespace change and would
    # still miss a semantic one. Re-creating the declaration under a probe name and comparing
    # two normalised bodies is exact in both directions.
    _decl = _schema.view_ddl()[0]
    _schema.execute(con, _decl.replace("VIEW core_decoded_shadow", "VIEW shadow_drift_probe", 1))
    con.commit()

    def _viewdef(n):
        return _schema.scalar(con, "SELECT pg_get_viewdef(%s::regclass, true)", (n,))

    check(
        "the DEPLOYED shadow is exactly what the declaration emits today",
        _viewdef("core_decoded_shadow"),
        _viewdef("shadow_drift_probe"),
    )
    # ⚑⚑ SHOWN FIRING BEFORE IT IS TRUSTED, AND NO CODE MUTATION CAN DO IT — both sides of the
    # comparison come from ONE `view_ddl()` call in ONE process, so a mutant changes them
    # together and the gate stays green. The scenario it exists for is a LONG-LIVED STORE whose
    # deployed body predates a change to the fragment, and the only way to exhibit that is to
    # put an old body in the store. This one is the shape that would be worst: a shadow that
    # still has the right columns and reconstructs NOTHING, i.e. one that reads as a total
    # refusal — which under the drain would look like caution rather than like breakage.
    _schema.execute(
        con,
        "CREATE OR REPLACE VIEW core_decoded_shadow AS "
        "SELECT core_id, relpath, mtime, producer, NULL::jsonb AS dec "
        "FROM dec_root",
    )
    con.commit()
    check(
        "...and it FIRES on a store whose deployed body the declaration would not emit",
        _viewdef("core_decoded_shadow") == _viewdef("shadow_drift_probe"),
        False,
    )
    _schema.execute(con, _decl)
    con.commit()
    check(
        "...and re-applying the declaration reconciles it",
        _viewdef("core_decoded_shadow"),
        _viewdef("shadow_drift_probe"),
    )
    _schema.execute(con, "DROP VIEW shadow_drift_probe")
    con.commit()
    # ⚑ AND THE EXCEPTION STAYS ONE. The policy is *a view is admissible IFF it is the
    # reconstruction claim of a relation supposed to be reconstructible* — so every entry must
    # name a real tier, and the emitter must have nothing else to emit. A convenience view
    # cannot be added without also asserting it shadows a drainable relation.
    check(
        "every shadow names a real tier and the emitter emits nothing else",
        (
            sorted(_schema.SHADOWS),
            sorted(set(t for _s, t in _schema.SHADOWS.values()) - set(_schema._TIERS)),
            len(_schema.view_ddl()),
        ),
        (["core_decoded_shadow"], [], 1),
    )

    # ── the dispatch: a mode that never fires is the silent-skip defect one layer up ────
    import ast as _ast
    import inspect as _inspect
    import re as _re

    # ⚑ THE POPULATION IS "STRINGS SHAPED LIKE A FLAG", NOT "STRINGS STARTING WITH `--`" —
    # `tree_cases`'s narrowing, for its measured reason: `'-- parameters: %r …'` is an SQL
    # COMMENT prefix in a print, not a flag.
    _flag = _re.compile(r"^--[a-z0-9]+(-[a-z0-9]+)*$")
    _branched = {
        n.value
        for n in _ast.walk(_ast.parse(_inspect.getsource(drain_cli)))
        if isinstance(n, _ast.Constant) and isinstance(n.value, str) and _flag.match(n.value)
    }
    check(
        "every flag `drain_cli` branches on is a declared DRAIN_MODE",
        sorted(_branched - {"--sandbox"} - DRAIN_MODES),
        [],
    )
    check(
        "...and DRAIN_MODES declares nothing `drain_cli` cannot serve",
        sorted(DRAIN_MODES - _branched - {"--drain-licence"}),
        [],
    )

    # ── the compiled SQL: properties a COMMENT cannot fake ──────────────────────────────
    _rsql, _rp = _R.retire_sql("d1")
    # ⚑⚑ NO `--` AT ALL. `_insert_row_sql`'s residue records the measured forgery: a guard
    # anchored on compiled SQL was satisfied by an SQL COMMENT naming what it guarded, and the
    # suite read green. SQL has comments too, so the emitted statement may carry none.
    check("the retire rung carries no SQL comment", "--" in _rsql, False)
    check("...and is ONE statement, so a drain cannot become a script", _rsql.count(";"), 0)
    check(
        "...parameterised by scope, never interpolated", (_rp, "d1" in _rsql), (("d1", "d1"), False)
    )
    # ⚑⚑ `IS NOT DISTINCT FROM`, NOT `=`. This is the difference between refusing an
    # unreconstructible core and draining it quietly: `=` against a NULL reconstruction yields
    # NULL, and NULL's reading flips depending on whether the predicate sits under a negation.
    # No behavioural case on THIS fixture can distinguish them — the shadow never yields a NULL
    # `dec` here — so it is pinned as a claim about the FUTURE database.
    check(
        "...and compares with IS NOT DISTINCT FROM, never with `=`",
        ("IS NOT DISTINCT FROM c.dec" in _rsql, "s.dec = c.dec" in _rsql),
        (True, False),
    )
    # ⚑ THE LICENCE IS A JOIN AGAINST THE SHADOW, WHICH IS WHAT MAKES THE HELD SET A RELATION.
    # A rung that recomputed the reconstruction inline would work and would put a second
    # spelling of it in the delete path.
    check(
        "...and reads the SHADOW, so the held set is `EXCEPT`-able rather than a report",
        ("core_decoded_shadow" in _rsql, "jsonb_object_agg" in _rsql),
        (True, False),
    )
    _rt, _rtp = _R.root_sql("d1")
    # ⚑⚑ THE SAME PREDICATE AT THE OTHER END. Build asks *is it there now*; delete asks *is it
    # still there*. They are separate runs, so this is a `WHERE` clause appearing twice, not a
    # check that moved.
    check(
        "the header BUILD carries the same equality predicate as the DELETE",
        ("IS NOT DISTINCT FROM c.dec" in _rt, _rt.count(";")),
        (True, 0),
    )
    check(
        "...and is the ONLY writer of dec_root, so a header implies the tree rebuilt it",
        ("INSERT INTO dec_root" in _rt, "ON CONFLICT DO NOTHING" in _rt),
        (True, True),
    )
    _bs, _bp = _R.rebuild_sql()
    # ⚑ THE MEMO RUNG ORDERS ITS INSERT, which is the only concurrency device it carries — and
    # the retire cannot, because postgres's DELETE has no ORDER BY.
    check(
        "the memo rung orders its insert and takes no scope",
        ("ORDER BY 1 ON CONFLICT DO NOTHING" in _bs, _bp),
        (True, ()),
    )
    # ⚑ AND IT READS NEITHER TIER IT IS SUPPOSED TO OUTLIVE. A reconstruction that touched
    # `core_decoded` or `dec_ref` would stop working at exactly the moment it is needed.
    check(
        "...and reads NO relation the drain retires",
        ("core_decoded" in _bs, "dec_ref" in _bs, "dec_stage" in _bs),
        (False, False, False),
    )
    con.close()


if __name__ == "__main__":
    _argv = sys.argv
    _args = [a for a in _argv[1:] if not a.startswith("--")]
    if not (DRAIN_MODES & set(_argv)):
        # ⚑ A BARE RUN DESCRIBES AND DOES NOT WRITE — `sppf_db`'s worst recorded defect is a
        # bare run that defaulted to a subtree and opened a write transaction against the live
        # store. In a tool whose whole job is DELETE, that is not a style point.
        print(__doc__.strip().splitlines()[0])
        print(
            "\n⚑ NO MODE GIVEN — refusing. A tool that DELETES when asked to describe "
            "itself is the defect.\n"
        )
        print("modes:")
        print("  --drain-rebuild            the value fixpoint — run the rebuild rung until a")
        print("                             round writes 0 rows. Fills `dec_val`, the memo.")
        print("  [RELPATH] --drain-root     build tier B+2's HEADER (`dec_root`) under the")
        print("                             reconstruction predicate — the ONLY writer of it")
        print("  [RELPATH] --drain-licence  THE DRY RUN — licensed / mismatch / no-header per")
        print("                             document, with the HELD set named. Writes nothing.")
        print("  [RELPATH] --drain-apply    THE RETIRE — DELETE FROM core_decoded, licensed by")
        print("                             the shadow, then prove every retired document")
        print("                             still reads back byte-for-byte. WRITES.")
        print("  [RELPATH] --drain-answer   read documents back from the durable tiers ALONE")
        print("  [RELPATH] --drain-oracle   the SQL shadow against python `recon`")
        print("  [RELPATH] --drain-stage    retire `treestage` — a CLEANUP, not a rung. WRITES.")
        print("  [RELPATH] --drain-restore  the retire's INVERSE — materialise `sourced` from")
        print("                             the shadow. A tier is an EFFICIENCY fact. WRITES.")
        print("  --drain-census             the populations, including the HELD set")
        print("  --drain-concurrency [N]    N retirers AT ONCE; reports 40P01 and exactly-once")
        print("  --drain-sql                every rung VERBATIM. Touches nothing.")
        print("      [--sandbox]            every mode: the THROWAWAY tenant, never the corpus")
        sys.exit(2)
    sys.exit(drain_cli(_argv, _args))
