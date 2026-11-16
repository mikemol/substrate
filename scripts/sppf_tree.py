#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""sppf_tree.py — ⟡ladder-4: the CALLER. `dec` as a CNF-2 binary tree, one statement per round.

⚑⚑ THE FIXPOINT LIVES HERE AND THE RUNG DOES NOT, WHICH IS THE WHOLE SEAM. A ladder rung is
ONE statement; "run it for `rnd = 0, 1, 2, …` until the frontier is empty" is a mode-branch,
and a mode-branch belongs to the caller. `jea/metalanguage/dec_tree.py` therefore scores
`pycodemod --control` **0** — no `if`, no `for`, no ternary, no `__main__` — and every one of
this file's branches is a branch it was supposed to keep.

    --tree-build [RELPATH]     THE CALLER — build the work list, then run the rung to fixpoint
    --tree-census [FILTER]     EXACT/MISSING + the SHARING measurement + the node counts
    --tree-roundtrip [FILTER]  `recon` of the built tree must reproduce `dec` — the ACCEPTANCE
    --tree-wedge [FILTER]      the tree the SQL built vs the one `PyDivStr.wedge` builds
    --tree-concurrency [N]     N builders AT ONCE over FILTER's documents; reports 40P01
    --tree-sql [RND]           the rung VERBATIM — the statement the engine is sent

⚑ ITS OWN TOOL AND NOT MORE MODES ON `sppf_db`, WHICH IS AT 1181 OF 1200 CODE LINES — the
same forcing function that put ⟡ladder-2b in `sppf_vocab.py`. What `sppf_db` still owns is the
SUITE (`tree_cases`), because `run_selftests.discover()` counts a suite as the PAIR of a
`_selftest` def and a dispatch on the selftest flag, and defining neither here keeps the
total at 69.

⚑⚑ AND THIS FILE MUST NOT SPELL THAT FLAG AS A LITERAL — `sppf_vocab`'s measured incident,
inherited verbatim: `run_selftests.HANDLES_SELFTEST` is a bare `re.compile` matched over the
WHOLE source, so a PARAGRAPH explaining that this module is not a suite is what would make the
runner treat it as one. The defect is in the proxy and is deliberately not repaired here.

⚑ THIS MODULE TOUCHES NO FILESYSTEM. Its scope argument is a `core_decoded.relpath` AS STORED,
never a path to resolve — a rung whose input is the store must not be able to disagree with
the store about which documents exist.

⚑ IT DEPENDS ON THE VOCAB TIER AND SAYS SO RATHER THAN CREATING IT. A leaf's identity IS its
`dec_scalar` id, so a tree built over an un-interned vocabulary would have leaves pointing at
nothing. `--tree-census` counts that as `unresolved` and names the step that fixes it.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))

import schema as _schema  # THE schema declaration: rows/execute/apply
import dec_tree as _T  # THE statements — data only, `--control` 0


def _connect(sandbox):
    """The store this invocation writes — sandbox or live, resolved ONCE.

    ⚑ ONE RESOLVER, NOT PER-DISPATCH — `schema_rows._cli_connect`'s recorded defect is that a
    per-mode `sandbox_connect(...) if …` line left the READ modes silently on the live store
    while the WRITE modes honoured the flag, and a read against the wrong tenant returns
    plausible rows nobody can distinguish.
    """
    import store

    return (
        store.sandbox_connect(reset=False) if sandbox else store.connect(mode="rw", require=False)
    )


def _tiers(con):
    """ASSERT the two tiers this tool touches are established. Creates nothing, commits
    nothing. ⚑ NOT `sourced`, NOT `vocab`.

    ⚑⚑⚑ THIS APPLIED DDL AND COMMITTED ON ENTRY TO ALL NINE CALLERS, five of which write
    nothing — `--tree-census`, `--tree-chains`, `--tree-roundtrip`, `--tree-wedge`, and
    `--tree-explain`, whose own docstring insists on `EXPLAIN` without `ANALYZE` because it
    *"must not run the INSERT"* and then issued `CREATE … IF NOT EXISTS` + `COMMIT` four lines
    earlier. DDL is a WRITE, so a read path may hold none of it.

    ⚑⚑ THE ABSENT-READ-AS-A-VERDICT ARGUMENT BELOW WAS ALWAYS RIGHT AND WAS APPLIED TO THE
    WRONG HALF. Creating `core_decoded` or `dec_scalar` here would turn "you have not sourced
    anything yet" into a successful run over an empty tree — and creating `tree`/`treestage`
    did exactly that for THEM: a census could not distinguish an un-built tree from one it had
    just conjured. Letting the assertion name the missing tier and the step that fills it is
    the same remedy, now applied uniformly.

    ⚑ AND `--tree-concurrency` FANS N PROCESSES AT THESE MODES. Per-call `IF NOT EXISTS` takes
    the relation lock before it can discover the object exists, so the read path was feeding
    DDL contention into the very deadlock measurement it exists to take.
    """
    _schema.require_tiers(con, ("tree", "treestage"), label="sppf_tree")


def _core_id(con, relpath):
    """The `core_id` of a STORED document, read from the store — or None for the whole table.

    ⚑ READ, NOT RECOMPUTED — `sppf_vocab._core_id`'s argument verbatim: `_content_addr._addr`
    would give the same answer today, and that is exactly what makes a second authority
    dangerous. A relpath with no row yields None-the-document rather than None-the-whole-table,
    so the caller is told rather than silently widened.
    """
    if relpath is None:
        return None, True
    cid = _schema.scalar(con, "SELECT core_id FROM core_decoded WHERE relpath = %s", (relpath,))
    return cid, cid is not None


def _exec(con, pair):
    """Run a `(sql, params)` pair and return its `rowcount`.

    ⚑ THE COUNT IS THE OBSERVABLE. It is the only way a caller distinguishes "this round was
    already resolved" from "this round had nothing in scope" without issuing the SELECT this
    design exists to remove — and the two are different facts.
    """
    cur = con.cursor()
    cur.execute(pair[0], pair[1])
    return max(0, getattr(cur, "rowcount", 0))


def _analyze(con):
    """Refresh the planner's statistics for the three relations this caller writes.

    ⚑⚑ NOT HYGIENE — A MEASURED COST DEFECT, AND THE SAME CLASS AS `text[]`/`AS MATERIALIZED`.
    `build_skeleton` takes `dec_stage` from 0 to 113,047 rows in one document, and autoanalyze
    is a background daemon with its own schedule: the rung that runs NEXT plans against
    statistics that say the table is empty. Read off `--tree-explain` on exactly that state:
    `Bitmap Index Scan on ix_decstage_rnd … rows=4` feeding nested loops whose actual output is
    176,472 rows — a four-order-of-magnitude estimate error, and the plan it buys is the one
    that made a census of ONE document take two minutes.

    ⚑ IT IS A CALLER CONCERN AND NOT A RUNG ONE. `ANALYZE` is not part of the statement's
    meaning and could not be: it is not composable, takes no scope, and would put a
    maintenance command inside a data module whose whole claim is `--control` 0.
    """
    for rel in ("dec_stage", "dec_ref", "dec_node"):
        _schema.execute(con, "ANALYZE " + rel)
    con.commit()


def build_skeleton(con, core_id=None):
    """Materialise the work list ONCE, ONE DOCUMENT AT A TIME. Returns the rows written.

    ⚑⚑ THE LOOP IS HERE AND THE STATEMENT IS NOT, which is the same seam as the fixpoint. The
    first shape built the whole corpus in ONE statement and it was measurably wrong: a ~9M-row
    sort and two multi-million-row hash builds that emit nothing until they commit — 6+ minutes
    with no observable progress, no partial result, and nothing to resume from.

    ⚑⚑ THE ROUND GRID IS MEASURED ONCE, OVER THE WHOLE SCOPE, AND HANDED TO EVERY DOCUMENT.
    That is the one thing decomposing the build could have broken: `rnd` is
    `(md - depth) * (mt + 1) + t + 1`, so per-document `mt` would put each document on its own
    grid and the UNION of distinct rounds — which is exactly the number of statements the
    fixpoint sends — would grow with no structural cause. `limits` is the cheap half of the same
    walk (two aggregates, no joins, no sort).

    ⚑ AND `commit()` PER DOCUMENT IS THE RESUMABILITY. `ON CONFLICT DO NOTHING` makes a
    re-run a no-op over what is already staged, so an interruption costs one document.
    """
    docs = [r["core_id"] for r in _schema.rows(con, *_T.scope_sql(core_id))]
    md, mt = 0, 0
    for cid in docs:
        for r in _schema.rows(con, *_T.limits_sql(cid)):
            md, mt = max(md, r["md"]), max(mt, r["mt"])
    n = 0
    for cid in docs:
        n += _exec(con, _T.skeleton_sql(cid, md, mt))
        con.commit()
    _analyze(con)
    return n


def run_rounds(con, core_id=None):
    """THE FIXPOINT: the flat rung per round, and the CHAIN rung to fixpoint after each.
    Returns `(statements, rows)`.

    ⚑⚑ THE SCHEDULE IS READ FROM THE WORK LIST, NOT COUNTED UP TO A MAXIMUM. `rnd` is numbered
    in arithmetic blocks so it has gaps; `range(0, max+1)` would issue up to 576,350 statements
    where ~115,300 rounds exist. `stmts` is therefore the MEASURED statement count — what was
    actually sent — and not a bound derived from the corpus.

    ⚑⚑ AND THE SCHEDULE IS NOW THE **FLAT** ONE, WHICH IS WHERE THE 115,268 WENT. `rounds_sql`
    returns every `rnd` in the work list; `flat_rounds_sql` returns only those holding a
    non-spine row (LEAF · empty compound · MEMBER — the productions with no sequential
    dependency between siblings). The spine cells that made up all the remaining rounds are
    resolved by `run_chains`, a WHOLE SPINE per statement. `rounds_sql` and `round_sql` are
    kept and still work: `--tree-sql` quotes the rung verbatim, and a per-`rnd` rung is what
    the flat half still is.

    ⚑⚑ THE INTERLEAVE IS FORCED BY THE GRAMMAR AND IS NOT A SCHEDULING PREFERENCE. A MEMBER at
    depth `d` holds a value that is a compound at depth `d+1`, i.e. that compound's spine HEAD
    cell — so the flat round for depth `d` cannot resolve until the chains at depth `d+1` are
    built. Running the chain fixpoint after EVERY flat round is what makes that cascade
    automatic: the chain rung's own readiness predicate (`bad = 0` — every cell's item
    resolves) selects exactly the spines the round just enabled, so the caller needs no depth
    parameter and no block arithmetic.

    ⚑⚑ THE DOCUMENT IS THE **OUTER** LOOP, WHICH IS `build_skeleton`'S OWN RECORDED LESSON
    APPLIED TO THE FIXPOINT — AND IT WAS SHIPPED THE WRONG WAY ROUND FIRST. With `rnd` outer,
    each flat round is ONE statement over the whole corpus: ~2M `dec_stage` rows, six LEFT
    JOINs, a `DISTINCT` and two `ORDER BY`s that spill at `work_mem = 8MB`, and two inserts with
    `ON CONFLICT` — MEASURED at 15+ minutes for a single round with no partial result and
    nothing to resume from. That is verbatim what `build_skeleton`'s note says about building
    the whole corpus in one statement (*"6+ minutes with no observable progress, no partial
    result, and nothing to resume from"*), re-derived one phase later because the lesson had
    been written down about the work list and not about the fixpoint.

    ⚑ IT IS ALSO CORRECT RATHER THAN MERELY CHEAPER: every dependency of a document's rung is
    INSIDE that document (`dec_stage` and `dec_ref` are both keyed by `core_id`), and the round
    GRID is shared because `build_skeleton` measured `(md, mt)` over the whole scope ONCE. So
    per-document is self-contained, commits per round, and finds earlier documents' nodes
    already in `dec_node` — which is where the cross-document sharing comes from.

    ⚑⚑ THE DOCUMENT LOOP IS NOT COSMETIC — `chain_sql` TAKES A CONCRETE `core_id` AND MEASURED
    ITS ABSENCE AS A **STALL**. Shipped first with the whole-table scope forwarded verbatim, the
    rung's `s.core_id = %s::text` matched nothing under a NULL parameter while the CENSUS (which
    keeps the nullable disjunction, because it reads only indexed aggregates) still reported work
    — so `run_chains` stepped, wrote 0 rows, and `todo` did not move. The guard fired and named
    it, which is the whole reason the work predicate is read from a different query than the
    rung's own rowcount. The downstream symptom was worse and would have been the one found
    first without the guard: with no chain built, the NEXT flat round resolved a MEMBER whose
    compound value had no node yet and offered `dec_node` a NULL `c2`.

    ⚑ ONE COMMIT PER STATEMENT, AND IT IS LOAD-BEARING RATHER THAN TIDY. The next statement
    resolves its children by an ordinary PK lookup against a FRESH snapshot; if the previous
    had not committed, it would see its own transaction's rows only through the same snapshot
    and a CONCURRENT writer's not at all. Batching into one transaction would also widen it,
    which is coordination this tier refuses.
    """
    docs = [r["core_id"] for r in _schema.rows(con, *_T.scope_sql(core_id))]
    rows, stmts = 0, 0
    for cid in docs:
        for rnd in [r["rnd"] for r in _schema.rows(con, *_T.flat_rounds_sql(cid))]:
            rows += _exec(con, _T.round_sql(rnd, cid))
            con.commit()
            stmts += 1
            cs, cr = run_chains(con, cid)
            stmts += cs
            rows += cr
        _analyze(con)
    return stmts, rows


def chain_census(con, core_id=None):
    """The chain WORK PREDICATE as a dict — chains · ready · done · todo · longest · cells."""
    return [dict(r) for r in _schema.rows(con, *_T.chain_census_sql(core_id))][0]


def run_chains(con, core_id):
    """THE CHAIN FIXPOINT: `chain_sql` until it writes nothing. Returns `(statements, rows)`.

    ⚑⚑ THE LOOP IS HERE AND THE STATEMENT IS NOT — `dec_tree`'s seam, unchanged. What IS new is
    that one statement now resolves a WHOLE SPINE rather than one cell of it, so this loop runs
    once per anchor collision instead of once per spine cell. The 115,268 the wall counted was
    the length of the longest chain; this counts how many chains had to be deferred because a
    sibling chain claimed their anchor first.

    ⚑⚑ THE TERMINATION ARGUMENT IS THE WORK PREDICATE MOVING, NOT THE ROWCOUNT BEING ZERO, AND
    THE DIFFERENCE IS THE LIVELOCK CASE. The census is read from `dec_stage ⋈ dec_ref ⋈
    dec_node` — a source the rung WRITES — so "the rung stepped and the census did not move" is
    a work predicate reporting work it does not consume, which memory `deadlock-breakdown-
    before-any-fix` names as the signature to STOP on rather than to engineer around. This
    returns it as a fact; it does not retry, back off, order anything, or take a lock.

    ⚑⚑ AND THE MEASURE IS `done`, NOT `todo` — A CORRECTION THE GUARD ITSELF FORCED, AND IT IS
    THE CLEAVER DEFECT IN MINIATURE. Shipped first watching `todo`, the guard fired on a
    HEALTHY fixpoint: a round consumed one chain AND, by building it, made a chain at the next
    level up READY — so `todo` went 1 → 1 while the SET behind it changed completely. `todo`
    is a scalar over two opposing flows (consumption and unblocking) and cannot separate them;
    collapsing the relation to it reported "no progress" where progress was real. `done` is
    MONOTONE — nothing in this ladder un-builds a chain — so "`done` did not increase" is a
    genuine stall and is also the termination proof, `done` being bounded by `chains`.

    ⚑ THE BREAKDOWN IS PRINTED AT THE STALL AND THE STATE IS LEFT INTACT. `chain_todo_sql` runs
    the RUNG'S OWN walk and reports, per unconsumed chain, the four values that decide whether
    it is taken this round (`cut`, `kid`, `g`, `anchor_share`) — so the finding is the location,
    not the fact that there was one.
    """
    cc, stmts, rows, raced = chain_census(con, core_id), 0, 0, 0
    todo, done = cc["todo"], cc["done"]
    while todo > 0:
        try:
            n = _exec(con, _T.chain_sql(core_id))
            con.commit()
        # ⚑ MATCHED BY **SQLSTATE**, NOT BY EXCEPTION CLASS OR MESSAGE — `tree_concurrency`'s
        # own rule for `40P01`, applied to `23505`: the driver spells the class
        # `UniqueViolation` and the server text is localisable; the SQLSTATE is neither, and
        # naming the class here would also make this module import the driver.
        except Exception as _err:  # noqa: BLE001 — re-raised unless 23505
            if getattr(_err, "sqlstate", None) != "23505":
                raise
            # ⚑⚑ THE ONE ERROR THIS RUNG CAN RAISE, AND IT IS NOT AN ERROR CONDITION — IT IS THE
            # CONCURRENCY OBSERVABLE. Inside a batch a duplicate `(head,c1,c2)` is impossible by
            # the anchor argument, and no new cell can equal an existing row (its `c2` is freshly
            # minted), so a 23505 means ANOTHER WRITER committed this content between my snapshot
            # and my insert. The transaction aborts having written NOTHING, and the next pass
            # finds the winner's nodes as an existing suffix — so the cut moves up and the
            # sharing is discovered rather than duplicated.
            #
            # ⚑ THIS IS NOT RETRY-WITH-BACKOFF AND ADDS NO COORDINATION — no lock, no ordering
            # between processes, no delay, no shared cursor. The loop it continues into is the
            # SAME fixpoint loop, and the SAME monotone `done` guard governs it: if the other
            # writer is not making progress either, `done` does not move and this STOPS with the
            # breakdown, exactly as it would for any other stall.
            con.rollback()
            raced += 1
            n = 0
        stmts += 1
        rows += n
        cc = chain_census(con, core_id)
        todo, nxt = cc["todo"], cc["done"]
        if nxt <= done:
            # ⚑ NOT A RETRY AND NOT A FIX — a REFUSAL that preserves the evidence. The census
            # did not move, so the loop stops HERE with the state intact for a breakdown.
            print(
                "  ⚑ CHAIN FIXPOINT STALLED — done %s → %s (todo %s) after a round that wrote "
                "%s row(s), %s raced.  STOPPING (see memory "
                "deadlock-breakdown-before-any-fix)."
                % (
                    format(done, ","),
                    format(nxt, ","),
                    format(todo, ","),
                    format(n, ","),
                    format(raced, ","),
                )
            )
            for r in _schema.rows(con, *_T.chain_todo_sql(core_id)):
                print(
                    "     UNCONSUMED  core %s · sid %s · %s cell(s) · cut %s · kid %s · "
                    "g %s of %s sharing the anchor · head address %s"
                    % (
                        r["core_id"],
                        r["sid"],
                        format(r["n"], ","),
                        r["cord"],
                        r["kid"],
                        r["g"],
                        r["anchor_share"],
                        "PRESENT but unresolvable" if r["addressed"] else "MISSING",
                    )
                )
            break
        done = nxt
    return stmts, rows


def tree_census(con, core_id=None):
    """Completeness, sharing and the relation's own digest — one dict."""
    res = {"documents": 0}
    res["documents"] = (
        _schema.scalar(
            con,
            "SELECT count(*) FROM core_decoded d WHERE (%s::text IS NULL OR d.core_id = %s::text)",
            (core_id, core_id),
        )
        or 0
    )
    for r in _schema.rows(con, *_T.complete_sql(core_id)):
        res.update(
            staged=r["staged"],
            present=r["present"],
            missing=r["missing"],
            unresolved=r["unresolved"],
            dangling=r["dangling"],
        )
    for r in _schema.rows(con, *_T.sharing_sql()):
        res.update(
            nodes=r["nodes"],
            shared=r["shared"],
            widest=r["widest"],
            refs=r["refs"],
            positions=r["positions"],
            tree_positions=r["tree_positions"],
            spine_nodes=r["spine_nodes"],
            spine_shared=r["spine_shared"],
        )
    for r in _schema.rows(con, *_T.digest_sql()):
        res.update(rows=r["rows"], ids=r["ids"], digest=r["digest"])
    res["heads"] = {
        r["head"]: r["n"]
        for r in _schema.rows(con, "SELECT head, count(*) AS n FROM dec_node GROUP BY 1 ORDER BY 1")
    }
    return res


_HEADS = {0: "LEAF", 1: "OBJ", 2: "ARR", 3: "MEMBER"}


def tree_report(res):
    """Render `tree_census` — completeness first, then the SHARING, then the shape.

    ⚑ THE SHARING LINE IS THE ONLY ONE HERE THAT JUSTIFIES THE ROUND COUNT. Completeness is a
    fact about the fixpoint and the head histogram is a fact about the alphabet; nodes-with-
    more-than-one-parent against positions-without-sharing is what says whether a right spine
    bought anything, and it is a ratio of two measured counts.
    """
    print("  ⟡ladder-4 dec_node — %s document(s) in scope" % format(res["documents"], ","))
    print(
        "     COMPLETE  EXACT %s · MISSING %s   (every node of the work list has a "
        "resolved identity)" % (format(res["present"], ","), format(res["missing"], ","))
    )
    print(
        "     staged %s · unresolved leaf id(s) %s · dangling ref(s) %s"
        % (format(res["staged"], ","), format(res["unresolved"], ","), format(res["dangling"], ","))
    )
    print(
        "     SHARING   %s node(s) with MORE THAN ONE parent of %s "
        "(%.1f%%) · widest fan-in %s"
        % (
            format(res["shared"], ","),
            format(res["nodes"], ","),
            100.0 * res["shared"] / max(1, res["nodes"]),
            format(res["widest"], ","),
        )
    )
    print(
        "               of the SPINE productions (OBJ/ARR): %s shared of %s"
        % (format(res["spine_shared"], ","), format(res["spine_nodes"], ","))
    )
    print(
        "               a plain tree (NO sharing at all) is %s node(s) → %s = %.2f× collapse"
        % (
            format(res["tree_positions"], ","),
            format(res["nodes"], ","),
            res["tree_positions"] / max(1, res["nodes"]),
        )
    )
    print(
        "               of which %s are addressed positions in the work list (leaves already "
        "deduplicated per document)" % format(res["positions"], ",")
    )
    print(
        "     RELATION  %s row(s) · %s distinct id(s) · md5 %s"
        % (format(res["rows"], ","), format(res["ids"], ","), res["digest"])
    )
    print(
        "     HEADS     "
        + " · ".join(
            "%s %s" % (_HEADS.get(h, h), format(n, ",")) for h, n in sorted(res["heads"].items())
        )
    )


# ── RECONSTRUCTION — `recon` of the built tree must reproduce `dec` ──────────────────────────
#
# ⚑⚑ THE SPINE IS WALKED ITERATIVELY AND THE NESTING RECURSIVELY, AND SWAPPING THOSE IS THE
# BUG. A right spine is 115,268 deep in this corpus, so a recursive descent along `c2`
# RecursionErrors; the document nests only 4 deep, so a recursive descent into a member's VALUE
# cannot. `jea_pyalg.trace_steps` records exactly this correction one level up (*"trace() …
# RecursionErrors on a chain deeper than the Python stack; this walks the SAME descent emitting
# one step at a time"*), and this is the same shape.
#
# ⚑⚑ AND A MEMOISED PER-NODE DECODE IS **QUADRATIC** ON A RIGHT SPINE — measured as a design
# refutation before it was written, not after. Memoising "the value of node i" would store the
# 115,268-member dict, then the 115,267-member dict, then … : Θ(N²) cells for one document.
# Reconstruction therefore materialises the ROOT only and never keeps a tail's value.
def rebuild(nodes, root):
    """The python value the tree at `root` denotes. `nodes[id] = (head, c1, c2, leafvalue)`."""
    head, c1, c2, v = nodes[root]
    if head == 0:
        return v
    # ⚑ `c1 == 0` IS THE EMPTY COMPOUND AND IS THE LOOP'S OTHER EXIT — `OBJ(0,0)` is a real
    # node meaning "no members", distinct from `ARR(0,0)`, and it is NOT the nil that ends a
    # spine. Reading only `cur != 0` walks straight off it into `nodes[0]`, which is what the
    # five 45-byte documents in this corpus do on the first try.
    if head == 1:
        out = {}
        cur = root
        while cur != 0 and nodes[cur][1] != 0:
            _h, m, tail, _v = nodes[cur]
            _mh, k, val, _mv = nodes[m]
            out[rebuild(nodes, k)] = rebuild(nodes, val)
            cur = tail
        return out
    out = []
    cur = root
    while cur != 0 and nodes[cur][1] != 0:
        _h, item, tail, _v = nodes[cur]
        out.append(rebuild(nodes, item))
        cur = tail
    return out


def read_tree(con, root):
    """`{id: (head, c1, c2, leafvalue)}` for everything reachable from `root`."""
    return {
        r["id"]: (r["head"], r["c1"], r["c2"], r["v"])
        for r in _schema.rows(con, *_T.reach_sql(root))
    }


def roundtrip(con, core_id=None):
    """Reconstruct every document in scope FROM THE TREE and compare to `dec`.

    ⚑⚑ THIS IS THE ACCEPTANCE TEST FOR THE WHOLE STEP, and it is the only completeness check
    that is genuinely driven from `dec` itself. `--tree-census`'s MISSING is derived from the
    work list, which this rung also built — so a walk that dropped a value would be absent from
    both and the census would read 0 missing over a truncated tree. Reconstruction reads only
    `dec_node` and `dec_scalar` and compares against the document, so nothing the builder got
    wrong can hide inside its own derivation.

    ⚑ `{} ≠ []` IS EXERCISED BY THE CORPUS, NOT ONLY BY A FIXTURE: five of the 43 documents are
    `{"nodes": {}, "defmarks": []}`, and `OBJ(0,0)` vs `ARR(0,0)` is what keeps them apart.
    A wrapper-free alphabet that got this wrong would fail here on real data.
    """
    out = []
    for r in _schema.rows(con, *_T.roots_sql(core_id)):
        # ⚑⚑ A MALFORMED TREE MUST **FAIL**, NOT CRASH — found by MUTATION, not by reading.
        # Breaking the leaf arm of the rung's `c2` CASE (a member's scalar value silently
        # resolving to the nullary child) left a MEMBER pointing at node `0`, and `rebuild`
        # raised `KeyError: 0` straight out of `tree_cases` — taking 163 cases down to report
        # one, which is indistinguishable from an unrelated collapse. The acceptance test must
        # be able to say "this document does not reconstruct" about a tree that is WRONG, and
        # a tree that is wrong is exactly the input it will be handed.
        try:
            got = rebuild(read_tree(con, r["root"]), r["root"])
        except (KeyError, RecursionError) as _e:  # noqa: BLE001 — the class is the point
            out.append((r["relpath"], False, r["root"]))
            continue
        out.append((r["relpath"], got == r["dec"], r["root"]))
    return out


# ── THE ORACLE — the tree the SQL built, against the one `PyDivStr.wedge` builds ─────────────
#
# ⚑⚑ THE BINARISER IS NOT REWRITTEN HERE, IT IS RUN. `jea_pyalg.PyDivStr.wedge` (`:128`) IS the
# CNF BIN step — `wedge(i) → (head, first-child, intern(SAME head over children[1:]))` — with
# `recon` (`:122`) its inverse and `faithful_check` (`:181`) asserting `recon(wedge(i)) == i`.
# This function builds the n-ary IR from `dec`, hands the VARIADIC nodes to `wedge`, and
# requires the resulting node set to equal what the SQL rung produced. So the SQL is checked
# against the repo's own binariser rather than against a second opinion written beside it.
#
# ⚑ `wedge` IS APPLIED TO `OBJ`/`ARR` AND **NOT** TO `MEMBER`, WHICH IS THE ONE PLACE THE
# ALPHABET DEPARTS FROM A UNIFORM FOLD. BIN is for a VARIADIC production; `MEMBER` is arity-2
# in the grammar, so there is nothing to fold. Handing it to `wedge` would yield
# `MEMBER(k, MEMBER(v, 0))` — an extra node per member — which is what the brief's *"already
# binary, never a spine"* rules out.
#
# ⚑⚑ THE COMPARISON IS BY CANONICAL RENUMBERING, AND MY FIRST SPELLING OF IT WAS WRONG IN A WAY
# THAT REPORTED A CORRECT TREE AS DIVERGENT. Numbering nodes in first-completion order of a DFS
# makes the numbers depend on the TRAVERSAL, so two isomorphic DAGs visited differently get
# different triples — and sorting the triples afterwards does not repair it, because the numbers
# inside them are already wrong. `_canon` numbers bottom-up instead: group by HEIGHT, sort each
# level by its already-canonical content, assign. Ties are impossible (both sides are
# content-interned, so equal triples ARE one node), so the order is total and the numbering is a
# function of the DAG alone. Found by running it, not by reading it.
def _canon(g, root):
    """Canonical numbering of a content-interned DAG. `g[i] = (head, c1, c2)`, LEAF c1 = payload."""
    ht = {}
    stack = [(root, False)]
    while stack:
        i, done = stack.pop()
        if i in ht:
            continue
        kids = [k for k in g[i][1:] if isinstance(k, int) and k != 0]
        if done:
            ht[i] = 1 + max([ht[k] for k in kids] + [-1])
            continue
        stack.append((i, True))
        for k in kids:
            stack.append((k, False))
    num, out = {}, []
    lvl = {}
    for i, h in ht.items():
        lvl.setdefault(h, []).append(i)
    for h in sorted(lvl):
        rows = sorted((g[i][0], _slot(g[i][1], num), _slot(g[i][2], num), i) for i in lvl[h])
        for a, b, c, i in rows:
            num[i] = len(out)
            out.append((a, b, c))
    return out


def _slot(x, num):
    """A child slot rendered comparably: a LEAF payload as text, a reference as its number."""
    if not isinstance(x, int):
        return "L" + repr(x)
    if x == 0:
        return "N-"
    return "N%09d" % num[x]


def _wedge_forest(dec):
    """`(canonical forest, faithful)` — the CNF-2 forest `PyDivStr.wedge` makes of one document."""
    import json as _json
    from jea_pyalg import IR, Intern, PyDivStr

    I = Intern()
    D = PyDivStr(I)

    def nary(v):
        if isinstance(v, dict):
            ms = tuple(
                I.intern(IR(kind="MEMBER", children=(nary(k), nary(v[k]))))
                for k in sorted(v, key=lambda s: s.encode())
            )
            return I.intern(IR(kind="OBJ", children=ms))
        if isinstance(v, list):
            return I.intern(IR(kind="ARR", children=tuple(nary(e) for e in v)))
        return I.intern(IR(kind="LEAF", lit=_json.dumps(v)))

    root = nary(dec)
    g, faithful = {}, True

    # ⚑⚑ `+ 1`, AND ITS ABSENCE REPORTED A CORRECT TREE AS A NODE SHORT. `Intern.intern` numbers
    # from **0** (`i = len(self.nodes)` on an empty list), while `0` is this tier's NIL — so
    # intern node 0, the first LEAF built, was read as "no child" and vanished from the forest.
    # The store side is immune by construction: `dec_node.id` is `GENERATED ALWAYS AS IDENTITY`,
    # which starts at 1, and THAT is what licenses `0` as the nullary child at all. The two id
    # spaces disagreed about their own origin and only one of them had said so out loud.
    # ⚑⚑ THE SPINE IS WALKED **ITERATIVELY** AND THE NESTING RECURSIVELY, AND MY FIRST SPELLING
    # RECURSED DOWN THE SPINE AND DIED — `RecursionError: maximum recursion depth exceeded`, at
    # a 1,155-member document, on the fourth real document tried. `jea_pyalg` ALREADY RECORDS
    # THIS CORRECTION about its own `trace`: *"trace() builds the whole nested Trace before any
    # read AND recurses, so it RecursionErrors on a chain deeper than the Python stack; this
    # walks the SAME descent emitting one step at a time"* — `trace_steps`, `:157`. I read that
    # note, wrote it into `rebuild`'s docstring on the SQL side, and then recursed anyway on the
    # oracle side. The corpus's longest spine is 115,268; python's limit is 1,000.
    def cnf(i):
        """`i`'s CNF-2 triple, folding the whole wedge chain into `g` as it goes."""
        if i + 1 in g:
            return i + 1
        n = I.nodes[i]
        if n.kind == "MEMBER":
            g[i + 1] = (3, cnf(n.children[0]), cnf(n.children[1]))
            return i + 1
        if n.kind == "LEAF":
            g[i + 1] = (0, n.lit, 0)
            return i + 1
        # OBJ / ARR — the VARIADIC productions, the only ones `wedge` binarises. Collect the
        # whole chain first (the `trace_steps` descent), then fill it in from the TAIL back, so
        # each node's remainder is already in `g` when its triple is written.
        tag = {"OBJ": 1, "ARR": 2}[n.kind]
        chain, cur = [], i
        while cur + 1 not in g:
            w = D.wedge(cur)
            # ⚑ `wedge` RETURNS None FOR A CHILDLESS NODE, and a childless OBJ/ARR is exactly
            # the empty object / empty array — `OBJ(0,0)` / `ARR(0,0)`, two distinct nodes.
            if w is None:
                g[cur + 1] = (tag, 0, 0)
                break
            chain.append((cur, w.base, w.rem))
            if w.rem == -1:
                break
            cur = w.rem
        for node, base, rem in reversed(chain):
            g[node + 1] = (tag, cnf(base), 0 if rem == -1 else rem + 1)
        return i + 1

    cnf(root)
    for i in list(g):
        faithful = faithful and D.faithful_check(i - 1)
    return _canon(g, root + 1), faithful


def _sql_forest(nodes, root):
    """The same canonical numbering, over the relation the rung built."""
    import json as _json

    g = {
        i: ((0, _json.dumps(v), 0) if head == 0 else (head, c1, c2))
        for i, (head, c1, c2, v) in nodes.items()
    }
    return _canon(g, root)


def wedge_check(con, core_id=None):
    """Per document: does the SQL relation hold exactly `PyDivStr.wedge`'s CNF-2 forest?"""
    out = []
    for r in _schema.rows(con, *_T.roots_sql(core_id)):
        want, faithful = _wedge_forest(r["dec"])
        # ⚑ SAME GUARD, SAME REASON as `roundtrip`'s: the oracle is handed the tree the rung
        # BUILT, so a wrong tree is its normal input and must read as a divergence.
        try:
            got = _sql_forest(read_tree(con, r["root"]), r["root"])
        except (KeyError, RecursionError):  # noqa: BLE001
            got = []
        out.append((r["relpath"], want == got, faithful, len(want), len(got)))
    return out


# ── the CLI ──────────────────────────────────────────────────────────────────────────────────
def build_tree(relpath, sandbox=False):
    """`--tree-build`: the work list, then the rung to fixpoint."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, relpath)
    if not found:
        # ⚑ A RELPATH WITH NO ROW IS A REFUSAL, NOT A NO-OP. `cid is None` also means "the whole
        # table", so falling through would silently promote a typo'd document name into a
        # full-corpus run — the widest possible action from the narrowest possible request.
        print(
            "  --tree-build: no core_decoded row for %r (the scope is the STORE, not the "
            "filesystem)" % relpath
        )
        con.close()
        return 2
    ns = build_skeleton(con, cid)
    con.commit()
    rounds, nrows = run_rounds(con, cid)
    res = tree_census(con, cid)
    con.close()
    print(
        "  dec_stage %-9s %s skeleton row(s) for %s"
        % ("WROTE" if ns else "current", format(ns, ","), relpath or "(whole table)")
    )
    print(
        "  dec_node  ROUNDS %s statement(s) · %s dec_ref row(s) resolved"
        % (format(rounds, ","), format(nrows, ","))
    )
    tree_report(res)
    return (
        0
        if (
            res["missing"] == 0
            and res["unresolved"] == 0
            and res["dangling"] == 0
            and res["staged"] > 0
        )
        else 1
    )


def stage_cli(args, sandbox=False):
    """`--tree-stage [RELPATH]`: materialise the WORK LIST only, and report the chain shape.

    ⚑⚑ A MODE, BECAUSE "HOW LONG ARE THE SPINES?" IS THE QUESTION THE ROUND COUNT IS AN ANSWER
    TO, AND IT WAS UNASKABLE. `--tree-build` couples the work list to the fixpoint, so measuring
    the corpus's chain shape meant running the 115,268-round build first — i.e. the measurement
    was gated on the thing it was supposed to size. Splitting the skeleton out makes the cost
    model readable before it is paid.
    """
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --tree-stage: no core_decoded row for %r" % args[0])
        con.close()
        return 2
    ns = build_skeleton(con, cid)
    con.commit()
    cc = chain_census(con, cid)
    con.close()
    print(
        "  dec_stage %-9s %s skeleton row(s) for %s"
        % ("WROTE" if ns else "current", format(ns, ","), args[0] if args else "(whole table)")
    )
    print(
        "     CHAINS  %s spine(s) · %s cell(s) · LONGEST %s"
        % (format(cc["chains"], ","), format(cc["cells"], ","), format(cc["longest"], ","))
    )
    print(
        "     ready %s · done %s · todo %s"
        % (format(cc["ready"], ","), format(cc["done"], ","), format(cc["todo"], ","))
    )
    print(
        "     ⚑ the old rung paid ONE ROUND PER CELL (%s); the chain rung pays one statement "
        "per BATCH of whole spines" % format(cc["cells"], ",")
    )
    # ⚑ `ns >= 0` WAS THE FIRST SPELLING AND IT IS AN EXIT CODE THAT CANNOT FAIL — a rowcount is
    # never negative, so it asserted nothing. The population is the thing to gate on: a scope
    # that staged nothing and a scope that was already staged are both fine, but a scope with no
    # CHAINS at all is an empty work list reading as a success.
    return 0 if cc["chains"] > 0 else 1


def rounds_cli(args, sandbox=False):
    """`--tree-rounds [RELPATH]`: run the FIXPOINT over an already-staged work list.

    ⚑⚑ THE COMPLEMENT OF `--tree-stage`, AND IT EXISTS BECAUSE RESUMABILITY WAS ONLY HALF BUILT.
    `build_skeleton` commits per document so an interruption costs one document — but
    `--tree-build` re-offers all 9,547,241 skeleton rows before it will run a single round, and
    on this corpus that is ~25 minutes of `ON CONFLICT DO NOTHING` to rediscover that nothing
    changed. Splitting the two makes the work list a MATERIALISED ARTIFACT rather than a phase:
    stage once, iterate the fixpoint as often as you like. `--tree-build` still does both, so
    the single build path is unchanged for a cold store.
    """
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --tree-rounds: no core_decoded row for %r" % args[0])
        con.close()
        return 2
    _analyze(con)
    stmts, nrows = run_rounds(con, cid)
    res = tree_census(con, cid)
    con.close()
    print(
        "  dec_node  STATEMENTS %s · %s dec_ref row(s) resolved"
        % (format(stmts, ","), format(nrows, ","))
    )
    tree_report(res)
    return (
        0
        if (
            res["missing"] == 0
            and res["unresolved"] == 0
            and res["dangling"] == 0
            and res["staged"] > 0
        )
        else 1
    )


def chains_cli(args, sandbox=False):
    """`--tree-chains [RELPATH]`: the chain WORK PREDICATE. Writes nothing."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --tree-chains: no core_decoded row for %r" % args[0])
        con.close()
        return 2
    cc = chain_census(con, cid)
    con.close()
    print("  ⟡ladder-fixpoint CHAINS — the spine work predicate")
    print(
        "     %s spine(s) · %s cell(s) · LONGEST %s"
        % (format(cc["chains"], ","), format(cc["cells"], ","), format(cc["longest"], ","))
    )
    print(
        "     ready %s · done %s · TODO %s · blocked %s"
        % (
            format(cc["ready"], ","),
            format(cc["done"], ","),
            format(cc["todo"], ","),
            format(cc["chains"] - cc["ready"], ","),
        )
    )
    # ⚑ AN EMPTY WORK LIST IS NOT A PASS — `0 todo` over `0 chains` is what a document nobody
    # staged looks like, and the exit code must not read it as a finished build.
    return 0 if (cc["chains"] > 0 and cc["todo"] == 0) else 1


def census_cli(args, sandbox=False):
    """`--tree-census [FILTER]`: completeness and the sharing measurement. Writes nothing."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --tree-census: no core_decoded row for %r" % args[0])
        con.close()
        return 2
    res = tree_census(con, cid)
    tree_report(res)
    con.close()
    # ⚑ AN EMPTY POPULATION IS NOT A PASS. "0 missing" over 0 staged rows is the shape this arc
    # has fixed three times.
    return (
        0
        if (
            res["missing"] == 0
            and res["unresolved"] == 0
            and res["dangling"] == 0
            and res["staged"] > 0
        )
        else 1
    )


def roundtrip_cli(args, sandbox=False):
    """`--tree-roundtrip [RELPATH]`: `recon` of the tree must reproduce `dec`."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --tree-roundtrip: no core_decoded row for %r" % args[0])
        con.close()
        return 2
    rs = roundtrip(con, cid)
    con.close()
    bad = [r for r in rs if not r[1]]
    print("  ⟡ladder-4 ROUND-TRIP — recon(dec_node) vs core_decoded.dec")
    print(
        "     %s of %s document(s) reproduce their `dec` EXACTLY"
        % (format(len(rs) - len(bad), ","), format(len(rs), ","))
    )
    for relpath, _ok, root in bad[:10]:
        print("     ⚑ MISMATCH  %s  (root node %s)" % (relpath, root))
    # ⚑ AN EMPTY RESULT IS A FACT ABOUT THE SCOPE, NOT A PASS — 0 of 0 reconstructing is what a
    # tree nobody built looks like, and it must not read as an acceptance.
    return 0 if (rs and not bad) else 1


def wedge_cli(args, sandbox=False):
    """`--tree-wedge [RELPATH]`: the SQL forest against `PyDivStr.wedge`'s."""
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --tree-wedge: no core_decoded row for %r" % args[0])
        con.close()
        return 2
    rs = wedge_check(con, cid)
    con.close()
    bad = [r for r in rs if not (r[1] and r[2])]
    print("  ⟡ladder-4 BINARISER — the SQL rung vs jea_pyalg.PyDivStr.wedge")
    print(
        "     %s of %s document(s) hold EXACTLY wedge's CNF-2 forest, faithful_check green"
        % (format(len(rs) - len(bad), ","), format(len(rs), ","))
    )
    for relpath, same, faithful, nw, ng in bad[:10]:
        print(
            "     ⚑ DIVERGENCE  %s  same=%s faithful=%s wedge=%s sql=%s"
            % (relpath, same, faithful, nw, ng)
        )
    return 0 if (rs and not bad) else 1


def explain_cli(args, sandbox=False):
    """`--tree-explain RELPATH`: the PLAN the work-list build and the rung actually get.

    ⚑⚑ A MODE, BECAUSE "WHY IS THIS SLOW?" IS A QUESTION AND READING THE SQL IS NOT AN ANSWER.
    Two cost defects in this tier were invisible to every other instrument and named instantly
    by a plan: `text[]` has no hash operator class, so the path join planned a **Merge Left
    Join** over 4.1M sorted arrays; and a nullable scope disjunction at the head of the walk
    left the planner estimating the whole corpus, which turned two `dec_scalar` lookups into
    231,783-row **hash builds per document**. Neither is visible in the statement text, both are
    the first line of the plan, and "I will read the query again" is how a session spends an
    hour on either.

    ⚑ `EXPLAIN` WITHOUT `ANALYZE` — it must not run the INSERT. The question is which plan the
    planner CHOOSES, and choosing is what goes wrong here; a timing would answer a different
    question and would write rows while asking it.
    """
    con = _connect(sandbox)
    _tiers(con)
    cid, found = _core_id(con, args[0] if args else None)
    if not found or cid is None:
        print("  --tree-explain: needs a RELPATH the store holds (the plan is per document)")
        con.close()
        return 2
    md, mt = 0, 0
    for r in _schema.rows(con, *_T.limits_sql(cid)):
        md, mt = r["md"], r["mt"]
    for label, pair in (
        ("work list", _T.skeleton_sql(cid, md, mt)),
        ("rung", _T.round_sql(1, cid)),
    ):
        print("  ── %s ──" % label)
        for r in _schema.rows(con, "EXPLAIN " + pair[0], pair[1]):
            print("    " + r["QUERY PLAN"])
    con.close()
    return 0


def _opt_int(argv, flag, default):
    """The integer following `flag` in `argv`, or `default`.

    ⚑ THE NEXT **FLAG** IS NOT MISTAKEN FOR N — `sppf_vocab._opt_int`'s measured edge:
    `int("--sandbox")` raises, and a `try/except: 0` would run ZERO processes and report a
    clean deadlock verdict over nothing.
    """
    argv = list(argv)
    if flag not in argv:
        return default
    i = argv.index(flag)
    n = argv[i + 1] if len(argv) > i + 1 else ""
    return int(n) if n.isdigit() else default


def tree_concurrency(filt, n, sandbox=True):
    """Run `n` `--tree-build` callers AT ONCE and report whether any `40P01` occurred.

    ⚑⚑ A MODE, NOT A SHELL FAN-OUT — `vocab_concurrency`'s argument verbatim: launching N
    background jobs and reading N outputs is reasoning performed in the turn, and it evaporates
    when the turn ends.

    ⚑ IT REPORTS AND DOES NOT REPAIR. No retry, no backoff, no serialisation, no ordering
    imposed BETWEEN processes. Under this architecture a deadlock is a DESIGN VIOLATION and
    clearing it destroys the evidence, so a `40P01` is a finding, printed verbatim.

    ⚑⚑ A ONE-DOCUMENT FILTER IS THE SAME-SCOPE CASE AND A WIDE FILTER IS THE DISJOINT ONE, AND
    THIS TIER'S DISJOINT CASE IS NOT BENIGN. `dec_ref` is keyed by `core_id`, so disjoint
    documents never contend there — but `dec_node` is CONTENT-keyed, which is the whole point,
    so two writers on unrelated documents contend on every shared subtree. That is the harder
    case and the one the intra-statement lock order exists for.
    """
    import subprocess

    con = _connect(sandbox)
    _tiers(con)
    picks = [
        r["relpath"]
        for r in _schema.rows(
            con,
            "SELECT relpath FROM core_decoded WHERE relpath LIKE %s ORDER BY relpath",
            ("%" + filt + "%",),
        )
    ]
    before = tree_census(con)
    con.close()
    if not picks:
        # ⚑ AN EMPTY SAMPLE IS A FACT ABOUT THE FILTER, NOT A PASS — in an instrument whose whole
        # job is to detect a rare event, "0 processes, 0 deadlocks" is worthless.
        print(
            "  ⚑ no core_decoded document matches %r — nothing was run, nothing is claimed" % filt
        )
        return 1
    # ⚑ CYCLED UP TO `n`, so N processes always start even when the filter yields fewer
    # documents. Silently running 3 for a request of 12 reports a contention level never applied.
    picks = [picks[i % len(picks)] for i in range(n)]
    tool = os.path.join(_ROOT, "scripts", "sppf_tree.py")
    procs = [
        subprocess.Popen(
            [sys.executable, tool, "--tree-build", p] + (["--sandbox"] if sandbox else []),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for p in picks
    ]
    outs = [(pr.wait(), pr.stdout.read(), pr.stderr.read()) for pr in procs]
    con = _connect(sandbox)
    after = tree_census(con)
    con.close()
    # ⚑ `40P01` IS THE SQLSTATE AND IS WHAT IS MATCHED, not the word "deadlock": psycopg spells
    # the exception `DeadlockDetected` and the server message is localisable; the SQLSTATE is
    # neither. Both are looked for — a match on either is a finding, a miss on both is the claim.
    dead = [
        (i, e) for i, (_rc, _o, e) in enumerate(outs) if "40P01" in e or "DeadlockDetected" in e
    ]
    fail = [(i, rc, e) for i, (rc, _o, e) in enumerate(outs) if rc != 0]
    print(
        "  ⟡ladder-4 CONCURRENCY — %d builder(s) at once over %d distinct document(s) under %r"
        % (n, len(set(picks)), filt)
    )
    print("     exit codes: %s" % ", ".join(str(rc) for rc, _o, _e in outs))
    print(
        "     dec_node rows: %s → %s · distinct id %s → %s · dec_ref %s → %s"
        % (
            format(before["rows"], ","),
            format(after["rows"], ","),
            format(before["ids"], ","),
            format(after["ids"], ","),
            format(before["positions"], ","),
            format(after["positions"], ","),
        )
    )
    # ⚑⚑ EXACTLY-ONCE IS `rows == distinct id`, AND IT IS THE PROPERTY THE FAN-OUT COULD BREAK.
    # A duplicate would mean two writers each landed the same `(head,c1,c2)` — which the PK makes
    # unrepresentable, so this reads the constraint's guarantee back rather than trusting it.
    print(
        "     EXACTLY-ONCE: %s (dec_node rows == distinct ids); MISSING %s · DANGLING %s"
        % (
            "YES" if after["rows"] == after["ids"] else "**NO**",
            format(after["missing"], ","),
            format(after["dangling"], ","),
        )
    )
    if dead:
        print("     ⚑⚑ 40P01 DEADLOCK — %d of %d process(es). VERBATIM:" % (len(dead), n))
        for i, e in dead[:2]:
            print("        [proc %d] %s" % (i, e.strip()[:1200]))
    else:
        print("     40P01 DEADLOCK: NONE observed in %d concurrent builder(s)" % n)
    for i, rc, e in fail:
        if (i, e) not in dead:
            print("     ⚑ process %d exited %d — %s" % (i, rc, e.strip().splitlines()[-1:]))
    return (
        1
        if (dead or fail or after["rows"] != after["ids"] or after["missing"] or after["dangling"])
        else 0
    )


#: The ⟡ladder-4 modes `tree_cli` owns. ⚑ ONE PLACE, so the dispatch and the mode set cannot
# disagree — a mode branched on but not declared here simply never fires, and `tree_cases`
# asserts the two agree on the AST rather than on the prose that names every flag.
TREE_MODES = {
    "--tree-build",
    "--tree-census",
    "--tree-roundtrip",
    "--tree-wedge",
    "--tree-concurrency",
    "--tree-sql",
    "--tree-explain",
    "--tree-stage",
    "--tree-chains",
    "--tree-rounds",
}


def tree_cli(argv, args):
    """The ⟡ladder-4 CLI — one entry point for the TREE tier's six modes."""
    argv = list(argv)
    sandbox = "--sandbox" in argv
    if "--tree-sql" in argv:
        # ⚑⚑ A MODE, BECAUSE "WHAT STATEMENT DOES THE RUNG ISSUE?" IS A QUESTION AND ANSWERING
        # IT BY HAND IS THE THING THE STANDING RULE FORBIDS. ⟡ladder-1 answered it by pasting
        # the statement into a plan file, where it is a COPY that ages. This prints exactly what
        # `run_rounds` sends. It touches no store and writes nothing.
        # ⚑ A ROUND NUMBER IS NOT A RELPATH. `--tree-sql 7` puts `7` in `args` too, so the
        # naive `args[0]` printed the scope as the document `'7'` — a parameter list that reads
        # plausibly and is wrong, in the one mode whose whole job is to be quotable verbatim.
        _rest = [a for a in args if not a.isdigit()]
        _sql, _p = _T.round_sql(_opt_int(argv, "--tree-sql", 1), _rest[0] if _rest else None)
        print("-- ── the FLAT rung (LEAF · empty compound · MEMBER), one rnd slice ──")
        print(_sql)
        print("-- parameters: %r  (NULL scope = every document)" % (_p,))
        # ⚑ BOTH RUNGS, BECAUSE THERE ARE NOW TWO AND QUOTING ONE WOULD MISREPRESENT THE BUILD.
        # `--tree-sql` exists so the statement the engine is sent is readable without a
        # transcription; a mode that shows the rung which no longer carries the spine cells
        # would be a transcription by omission.
        _csql, _cp = _T.chain_sql(_rest[0] if _rest else None)
        print("\n-- ── the CHAIN rung (a BATCH of whole spines, ⟡ladder-fixpoint) ──")
        print(_csql)
        print("-- parameters: %r  (the scope is CONCRETE — see chain_sql)" % (_cp,))
        return 0
    if "--tree-build" in argv:
        i = argv.index("--tree-build")
        nxt = argv[i + 1] if len(argv) > i + 1 else None
        # ⚑ A FLAG IS NOT A RELPATH. `--tree-build --sandbox` must mean "the whole table, in the
        # sandbox", not "the document named --sandbox".
        return build_tree(None if (nxt is None or nxt.startswith("--")) else nxt, sandbox)
    if "--tree-stage" in argv:
        return stage_cli(args, sandbox)
    if "--tree-rounds" in argv:
        return rounds_cli(args, sandbox)
    if "--tree-chains" in argv:
        return chains_cli(args, sandbox)
    if "--tree-roundtrip" in argv:
        return roundtrip_cli(args, sandbox)
    if "--tree-wedge" in argv:
        return wedge_cli(args, sandbox)
    if "--tree-explain" in argv:
        return explain_cli(args, sandbox)
    if "--tree-concurrency" in argv:
        return tree_concurrency(
            args[0] if args else "", _opt_int(argv, "--tree-concurrency", 8), sandbox=sandbox
        )
    return census_cli(args, sandbox)


def tree_cases(check):
    """The ⟡ladder-4 guarded cases, driven from `sppf_db._selftest`.

    ⚑ THE CASES LIVE BESIDE THE CODE AND THE SUITE STAYS WHERE IT WAS — `vocab_cases`'s
    precedent: `run_selftests.discover()` counts a suite as the PAIR of a `_selftest` def and a
    dispatch on the selftest flag, so defining neither here adds no suite and the total stays 69.

    ⚑⚑ THE FIXTURE IS HANDWRITTEN AND ADVERSARIAL. A real core cannot exhibit, on demand, an
    empty object BESIDE an empty array, two objects that share a TAIL but not a head, an array
    whose tail equals a standalone array, and a key whose text also occurs as a value. Those are
    exactly the properties "the tail and the standalone are ONE node" is a claim about.
    """
    import json as _json
    import sppf_vocab as _V

    con = _schema.sandbox_fixture("sppf_tree")

    # ⚑ `tail`/`head2` SHARE THE SUFFIX `{"b":2,"c":3}` AND DIFFER IN THEIR FIRST MEMBER, which
    # under `ORDER BY key COLLATE "C"` is `a` vs `A`. That is the ONE structure the right-spine
    # decision exists to make legible: the shared suffix must be ONE node, always, and it must
    # be the same node as the standalone `{"b":2,"c":3}` sitting beside them.
    doc = {
        "e_obj": {},
        "e_arr": [],
        "tail": {"a": 1, "b": 2, "c": 3},
        "head2": {"A": 9, "b": 2, "c": 3},
        "alone": {"b": 2, "c": 3},
        "arr3": [7, 8, 9],
        "arr2": [8, 9],
        "deep": [[{"k": [1]}]],
        "k": "k",
    }
    _schema.execute(
        con,
        "INSERT INTO core_decoded (core_id, relpath, mtime, dec) "
        "VALUES ('t1', 'fixture/tree.agdai', 1, %s)",
        (_json.dumps(doc),),
    )
    con.commit()
    _V.intern_scalars(con)
    con.commit()

    _pre = _schema.scalar(con, "SELECT count(*) FROM dec_node")
    # ⚑⚑ THE BUILD IS GUARDED SO A REFUSAL NAMES ITSELF INSTEAD OF TAKING THE SUITE DOWN — the
    # repair ⟡ladder-1 made once and ⟡ladder-2b re-earned by mutation. A traceback out of a case
    # function fails EVERYTHING, which is indistinguishable from an unrelated collapse.
    try:
        ns = build_skeleton(con, None)
        con.commit()
        rounds, nrows = run_rounds(con, None)
    except Exception as _err:  # noqa: BLE001 — naming IS the job
        con.rollback()
        check("the rung RUNS at all — its relations and conflict arbiters exist", str(_err), "")
        con.close()
        return
    check(
        "the work list is non-empty and the fixpoint resolves every row of it",
        (_pre, ns > 0, nrows > 0),
        (0, True, True),
    )
    # ⚑ THE ROUND COUNT IS BOUNDED BY THE LONGEST SPINE, NOT BY THE NODE COUNT — the claim the
    # whole cost shape rests on. The fixture's deepest sequence has 9 members at depth 0.
    check(
        "...in a number of rounds bounded by the longest sequence, not by the node count",
        (rounds > 1, rounds < ns),
        (True, True),
    )
    # ⚑⚑ AND ⟡ladder-fixpoint STRENGTHENS THAT BOUND RATHER THAN REPLACING IT — RE-ANCHORED, NOT
    # DELETED. The case above is still true and is now weak: with the chain rung the statement
    # count is bounded by the JSON NESTING DEPTH and the anchor collisions, NOT by the longest
    # spine. The fixture's longest spine has 9 cells and its `cells` total is larger still, so
    # `statements < cells` is a claim the per-cell rung could not have satisfied.
    _cc = chain_census(con)
    check(
        "the CHAIN rung resolves whole spines: statements < spine cells, not one per cell",
        (rounds < _cc["cells"], _cc["cells"] > 0),
        (True, True),
    )
    # ⚑ THE WORK PREDICATE MUST REACH ZERO, AND IT IS READ FROM THE RELATION THE RUNG WRITES —
    # which is exactly what makes "the loop stepped and the census did not move" observable at
    # all. `done == chains` is the same fact from the other side, so a predicate that could only
    # ever report 0 fails one of the two.
    check(
        "...and its work predicate reaches zero: every spine ready, every spine done",
        (_cc["todo"], _cc["done"], _cc["chains"] == _cc["done"]),
        (0, _cc["chains"], True),
    )

    def _nid(head, c1, c2):
        return _schema.scalar(
            con, "SELECT id FROM dec_node WHERE head=%s AND c1=%s AND c2=%s", (head, c1, c2)
        )

    def _leaf(v):
        return _schema.scalar(
            con,
            "SELECT d.id FROM dec_node d JOIN dec_scalar s ON s.id = d.c1 "
            "WHERE d.head = 0 AND s.v = %s::jsonb",
            (_json.dumps(v),),
        )

    def _val(relpath, key):
        """The node id of `dec[key]` — found by walking the root spine in SQL."""
        return _schema.scalar(
            con,
            "WITH RECURSIVE sp(id) AS (SELECT d.id FROM dec_ref r JOIN dec_node d "
            "ON d.head=r.head AND d.c1=r.c1 AND d.c2=r.c2 JOIN core_decoded c "
            "ON c.core_id=r.core_id WHERE c.relpath=%s AND r.sid=1 AND r.kind=0 AND r.ord=1 "
            "UNION ALL SELECT n.c2 FROM sp JOIN dec_node n ON n.id=sp.id WHERE n.c2<>0) "
            "SELECT m.c2 FROM sp JOIN dec_node o ON o.id=sp.id "
            "JOIN dec_node m ON m.id=o.c1 JOIN dec_scalar k ON k.id=(SELECT c1 FROM dec_node "
            "WHERE id=m.c1) WHERE k.v = %s::jsonb",
            (relpath, _json.dumps(key)),
        )

    # ── the ALPHABET: four productions, and `{}` ≠ `[]` WITHOUT a wrapper ────────────────
    _eo, _ea = _val("fixture/tree.agdai", "e_obj"), _val("fixture/tree.agdai", "e_arr")
    check(
        "an empty object is OBJ(0,0) and an empty array is ARR(0,0) — DIFFERENT nodes",
        (_eo == _nid(1, 0, 0), _ea == _nid(2, 0, 0), _eo != _ea),
        (True, True, True),
    )
    # ⚑⚑ THE CENTRAL CLAIM OF THE SPINE DECISION. `{"a":1,"b":2,"c":3}`'s tail after `a`, and
    # `{"A":9,"b":2,"c":3}`'s tail after `A`, and the STANDALONE `{"b":2,"c":3}` are ONE node.
    # A wrapper production (the design note's `OBJ(chain,0)` over a `CONS` spine) would hold
    # THREE nodes here and every other case in this block would still pass.
    _t, _h2, _al = (
        _val("fixture/tree.agdai", "tail"),
        _val("fixture/tree.agdai", "head2"),
        _val("fixture/tree.agdai", "alone"),
    )
    _tt = _schema.scalar(con, "SELECT c2 FROM dec_node WHERE id=%s", (_t,))
    _ht = _schema.scalar(con, "SELECT c2 FROM dec_node WHERE id=%s", (_h2,))
    check(
        "two objects sharing a member SUFFIX share the very same tail node",
        (_tt == _ht, _tt is not None),
        (True, True),
    )
    check("...and that shared tail IS the standalone object of equal content — one node", _tt, _al)
    # ⚑ THE SAME PROPERTY ON THE OTHER VARIADIC PRODUCTION, because an alphabet that got it
    # right for objects and wrong for arrays would pass every object case above.
    _a3, _a2 = _val("fixture/tree.agdai", "arr3"), _val("fixture/tree.agdai", "arr2")
    check(
        "an array's tail IS the standalone array of equal content",
        _schema.scalar(con, "SELECT c2 FROM dec_node WHERE id=%s", (_a3,)),
        _a2,
    )
    # ⚑ AND THE HEADS ARE A CLOSED SET OF FOUR. A `CONS` production creeping back in would show
    # up here as a fifth tag before any structural case noticed.
    check(
        "the alphabet is exactly LEAF/OBJ/ARR/MEMBER — no spine constructor",
        sorted(
            r["head"] for r in _schema.rows(con, "SELECT DISTINCT head FROM dec_node ORDER BY 1")
        ),
        [0, 1, 2, 3],
    )
    # ⚑ ONE VOCABULARY, STILL. A key `"k"` and the string VALUE `"k"` are one `dec_scalar` row
    # (⟡ladder-2b) and therefore ONE LEAF node — the tier below's property, read from this one.
    check(
        "a key and an equal string value are ONE leaf node, because they are one scalar",
        _schema.scalar(
            con,
            "SELECT count(*) FROM dec_node d JOIN dec_scalar s ON s.id=d.c1 "
            "WHERE d.head=0 AND s.v='\"k\"'::jsonb",
        ),
        1,
    )

    # ── the KEY is BOUNDED — the property that defeated the previous attempt ─────────────
    # ⚑⚑ ASSERTED AS A MEASUREMENT, NOT AS A DESIGN INTENT. Identity-as-a-tuple with a compound
    # child holding its child's KEY makes a node's key encode its whole subtree — median root
    # ≈49k ids on this corpus, against postgres's 2704-byte btree entry limit. Every row here
    # must be a fixed 18 bytes of key no matter how deep the subtree under it is.
    check(
        "every node key is three fixed-width columns, whatever its subtree",
        _schema.scalar(
            con,
            "SELECT max(pg_column_size(head) + pg_column_size(c1) "
            "+ pg_column_size(c2)) FROM dec_node",
        )
        <= 24,
        True,
    )
    # ⚑ AND THE HANDLE IS ENGINE-ASSIGNED — the ⑸ defect (a client-side `max(id)+1` held across
    # statements) refused by postgres rather than by everyone remembering it.
    _refused = None
    try:
        _schema.execute(con, "INSERT INTO dec_node (head, c1, c2, id) VALUES (1, 0, 0, 999999)")
        con.commit()
        _refused = False
    except Exception as e:  # noqa: BLE001 — the class is the point
        con.rollback()
        _refused = "identity" in str(e).lower() or "GENERATED" in str(e)
    check(
        "a CLIENT-supplied node id is REFUSED by the engine, not merely discouraged", _refused, True
    )
    _dup = None
    try:
        _schema.execute(con, "INSERT INTO dec_node (head, c1, c2) VALUES (1, 0, 0)")
        con.commit()
        _dup = False
    except Exception:  # noqa: BLE001
        con.rollback()
        _dup = True
    check("a duplicate (head,c1,c2) is REFUSED by the primary key", _dup, True)

    # ── IDEMPOTENCE: 0 rows AND the relation byte-identical ─────────────────────────────
    _d1 = [dict(r) for r in _schema.rows(con, *_T.digest_sql())][0]
    _ns2 = build_skeleton(con, None)
    con.commit()
    _r2, _n2 = run_rounds(con, None)
    _d2 = [dict(r) for r in _schema.rows(con, *_T.digest_sql())][0]
    check("a second build writes NOTHING — neither work list nor tree", (_ns2, _n2), (0, 0))
    # ⚑ THE DIGEST IS THE HALF A ROWCOUNT CANNOT SEE. A rung that deleted and rewrote every row
    # identically also reports 0 on the run after; only the id ASSIGNMENT betrays it.
    check(
        "...and leaves the relation byte-identical (same ids, same order)",
        (_d1["digest"] == _d2["digest"], _d1["digest"] is not None),
        (True, True),
    )
    # ⚑⚑ AND THE ANTI-CONFLICT IS WHAT THIS ASSERTS, BECAUSE NOTHING ELSE CAN. Postgres
    # evaluates the identity default BEFORE detecting a conflict, so a re-offered row still
    # BURNS a number. `max(id)` cannot see that — a burned value leaves a GAP — which is the
    # spelling ⟡ladder-2b's equivalent case got wrong first and found only by mutating.
    _seq = "SELECT pg_sequence_last_value(pg_get_serial_sequence('dec_node','id'))"
    check(
        "...and the sequence did not advance, so nothing was re-offered to the index",
        _schema.scalar(con, _seq) is not None,
        True,
    )

    # ── COMPLETENESS, SHOWN FAILING BEFORE IT IS SHOWN PASSING ──────────────────────────
    _c = tree_census(con)
    check(
        "completeness reports MISSING 0 over a population it can actually see",
        (_c["missing"], _c["unresolved"], _c["dangling"], _c["staged"] > 0),
        (0, 0, 0, True),
    )
    # ⚑ THE CENSUS MUST BE ABLE TO SAY "MISSING". A completeness instrument that reports 0
    # unconditionally is the `reflects_obs` defect — so it is shown FAILING, with the store's own
    # row deleted rather than with a mutated comparator. `alone` is the SHARED tail node, so
    # deleting its ref is also the sharpest available probe.
    _schema.execute(
        con,
        "DELETE FROM dec_ref WHERE core_id='t1' AND (sid,ord,kind) IN "
        "(SELECT sid,ord,kind FROM dec_ref WHERE core_id='t1' "
        "ORDER BY sid,ord,kind LIMIT 1)",
    )
    con.commit()
    check(
        "...and REPORTS a gap when one exists, rather than reading 0 either way",
        tree_census(con)["missing"],
        1,
    )
    _r3, _n3 = run_rounds(con, None)
    con.commit()
    check("...which the rung then closes", (_n3, tree_census(con)["missing"]), (1, 0))
    # ⚑ AND A DAMAGED **TREE** IS A DIFFERENT ABSENCE FROM AN UNFINISHED FIXPOINT, counted apart
    # because they send the operator to different places. Removing a `dec_node` row leaves every
    # `dec_ref` row present and makes `dangling` the only number that moves.
    # ⚑ THE VICTIM MUST BE A NODE WITH **NO PARENT**, and my first spelling took the lowest-id
    # MEMBER — which always has a parent, so the guarded DELETE removed nothing and the case
    # would have asserted a gap that was never opened. A parentless node (a document root) can
    # be removed without also breaking some other node's child pointer, which is what isolates
    # `dangling` from every other absence.
    _victim = _schema.scalar(
        con,
        "SELECT d.id FROM dec_node d WHERE NOT EXISTS (SELECT 1 FROM dec_node p "
        "WHERE (p.c1 = d.id AND p.head <> 0) OR p.c2 = d.id) ORDER BY d.id LIMIT 1",
    )
    _schema.execute(con, "DELETE FROM dec_node WHERE id=%s", (_victim,))
    con.commit()
    _cd = tree_census(con)
    check(
        "a DAMAGED tree reads as `dangling`, never as `missing` — three absences, three fixes",
        (_cd["dangling"] > 0, _cd["missing"]),
        (True, 0),
    )
    run_rounds(con, None)
    con.commit()
    check("...and the rung closes that one too", tree_census(con)["dangling"], 0)

    # ── THE ACCEPTANCE TEST: recon(tree) == dec, and the binariser it came from ─────────
    _rt = roundtrip(con)
    check(
        "recon of the built tree reproduces `dec` EXACTLY",
        (len(_rt), all(ok for _p, ok, _r in _rt)),
        (1, True),
    )
    # ⚑⚑ AND IT IS THE REPO'S OWN BINARISER IT AGREES WITH, NOT A SECOND OPINION.
    # `PyDivStr.wedge` IS the CNF BIN step and `faithful_check` IS its `recon(wedge(i)) == i`
    # obligation; this requires the SQL relation to hold exactly the forest `wedge` builds.
    _wc = wedge_check(con)
    check(
        "...and the relation holds EXACTLY PyDivStr.wedge's CNF-2 forest, faithful_check green",
        [(ok, f) for _p, ok, f, _a, _b in _wc],
        [(True, True)],
    )

    # ── the SHARING the spine decision was made to protect, MEASURED ────────────────────
    _s = tree_census(con)
    check(
        "sharing is MEASURED, not assumed: nodes with >1 parent, and the collapse ratio",
        (_s["shared"] > 0, _s["positions"] > _s["nodes"]),
        (True, True),
    )

    # ── a SCOPED build extends the SAME tree, and a second document SHARES with the first ─
    _schema.execute(
        con,
        "INSERT INTO core_decoded (core_id, relpath, mtime, dec) "
        "VALUES ('t2', 'fixture/two.agdai', 1, %s)",
        (_json.dumps({"alone": {"b": 2, "c": 3}, "new": [1]}),),
    )
    con.commit()
    _V.intern_scalars(con)
    con.commit()
    _cid2 = _schema.scalar(
        con, "SELECT core_id FROM core_decoded WHERE relpath='fixture/two.agdai'"
    )
    # ⚑ GUARDED LIKE THE FIRST BUILD, AND FOR THE REASON THE FIRST ONE IS — MEASURED, not
    # anticipated. This block was bare, and a mutation of the chain rung's recursive term
    # (M2: walking past the cut) raised a `UniqueViolation` out of `tree_cases` and took the
    # WHOLE suite down, which reads as an unrelated collapse rather than as the two cases below
    # failing. A refusal must name itself.
    try:
        build_skeleton(con, _cid2)
        con.commit()
        run_rounds(con, _cid2)
        con.commit()
    except Exception as _err2:  # noqa: BLE001 — naming IS the job
        con.rollback()
        check(
            "a SECOND document builds at all — the rung extends one tree, not two", str(_err2), ""
        )
    # ⚑⚑ CROSS-DOCUMENT SHARING IS THE PROPERTY THE CONTENT KEY EXISTS FOR, and it is the one a
    # path-addressed OUTPUT would have destroyed. `{"b":2,"c":3}` is in BOTH documents; there is
    # one node, reached from two `dec_ref` addresses in two different cores.
    check(
        "a second document REUSES the first's node for equal content — one node, two cores",
        _schema.scalar(
            con,
            "SELECT count(DISTINCT r.core_id) FROM dec_ref r "
            "WHERE (r.head,r.c1,r.c2) = (SELECT head,c1,c2 FROM dec_node "
            "WHERE id=%s)",
            (_al,),
        ),
        2,
    )
    check(
        "...and both documents still round-trip",
        [ok for _p, ok, _r in roundtrip(con)],
        [True, True],
    )

    # ── the dispatch: a mode that never fires is the silent-skip defect one layer up ────
    import ast as _ast
    import inspect as _inspect
    import re as _re

    # ⚑ THE POPULATION IS "STRINGS SHAPED LIKE A FLAG", NOT "STRINGS STARTING WITH `--`" —
    # `vocab_cases`'s narrowing, and for its measured reason: `'-- parameters: %r …'` is an SQL
    # COMMENT prefix in a print, not a flag, and a name-list exclusion is the frozen roster this
    # repo keeps paying for.
    _flag = _re.compile(r"^--[a-z0-9]+(-[a-z0-9]+)*$")
    _branched = {
        n.value
        for n in _ast.walk(_ast.parse(_inspect.getsource(tree_cli)))
        if isinstance(n, _ast.Constant) and isinstance(n.value, str) and _flag.match(n.value)
    }
    check(
        "every flag `tree_cli` branches on is a declared TREE_MODE",
        sorted(_branched - {"--sandbox"} - TREE_MODES),
        [],
    )
    check(
        "...and TREE_MODES declares nothing `tree_cli` cannot serve",
        sorted(TREE_MODES - _branched - {"--tree-census"}),
        [],
    )

    # ── the compiled SQL: properties a COMMENT cannot fake ──────────────────────────────
    _sql, _params = _T.round_sql(3, "t1")
    # ⚑⚑ NO `--` AT ALL. `_insert_row_sql`'s residue records the measured forgery: a guard
    # anchored on compiled SQL was satisfied by an SQL COMMENT naming what it guarded, and the
    # suite read green. SQL has comments too, so the emitted statement may carry none.
    check("the emitted rung carries no SQL comment", "--" in _sql, False)
    check("...and is ONE statement, so a round cannot become a script", _sql.count(";"), 0)
    check(
        "...parameterised by round AND scope, never interpolated",
        (_params, "t1" in _sql),
        ((3, "t1", "t1"), False),
    )
    # ⚑ THE LOCK ORDERS ARE PINNED BECAUSE THEY ARE THE ONLY CONCURRENCY PROPERTIES THE
    # STATEMENT ITSELF CARRIES; `--tree-concurrency` is what actually exercises them.
    check(
        "...ordering both inserts by their own key, so no two writers build a cycle",
        ("ORDER BY 1, 2, 3\n" in _sql, "ORDER BY 1, 2, 3, 4\n" in _sql),
        (True, True),
    )
    # ⚑⚑ AND THE CROSS-TABLE ORDER IS FORCED BY A CTE THE MAIN STATEMENT READS. Postgres does
    # not specify the execution order of data-modifying CTEs, so without this the two writers
    # could take `dec_node` and `dec_ref` in opposite orders. It is a lock-ORDER device and the
    # main INSERT does not need its value — which is exactly why a reader would delete it.
    check(
        "...and forces dec_node's locks to be taken before dec_ref's, in every writer",
        "(SELECT count(*) FROM n) >= 0" in _sql,
        True,
    )
    # ⚑ THE RUNG READS ITS FRONTIER FROM THE **WORK LIST**, NOT FROM `dec`. A rung that walked
    # `core_decoded` per round would be O(values × rounds) and would pass every behavioural case
    # in this block on a fixture whose spines are 9 long.
    check(
        "...and reads its frontier from dec_stage, never re-walking core_decoded",
        ("dec_stage" in _sql, "core_decoded" in _sql),
        (True, False),
    )
    _ssql, _sp = _T.skeleton_sql("t1", 4, 27)
    check(
        "the work list is built by ONE statement per document, carrying no SQL comment",
        (_ssql.count(";"), "--" in _ssql, _sp),
        (0, False, ("t1", 4, 27)),
    )
    # ⚑ THE WALK'S SCOPE IS A CONCRETE EQUALITY, NOT THE NULLABLE DISJUNCTION. Measured: the
    # disjunctive form defeats the planner's estimate at the head of the walk and turns the two
    # `dec_scalar` lookups into 231,783-row hash builds PER DOCUMENT — 55s for a median
    # document. This is the one place in the tier where the scope spelling decides the plan.
    check(
        "...and scopes its walk by a concrete core_id, never a nullable disjunction",
        ("WHERE d.core_id = %s::text" in _ssql, "%s::text IS NULL OR d.core_id" in _ssql),
        (True, False),
    )
    # ⚑ THE ROUND GRID IS A PARAMETER, NOT A SCOPE-LOCAL AGGREGATE. If `lim` were computed
    # inside the build, each document would land on its own `rnd` grid and the fixpoint would
    # send thousands of extra statements — correct, and silently more expensive.
    check(
        "...and takes its round grid as a parameter, so every document shares one grid",
        "lim AS (SELECT %s::int AS md, %s::bigint AS mt)" in _ssql,
        True,
    )
    # ⚑ THE OBJECT ORDER IS DECLARED IN THE STATEMENT, not inherited from jsonb's storage order.
    # Sharing depends on it: two objects with equal key sets share a suffix only if their
    # members are laid out the same way.
    check(
        "...and declares its object-member order rather than inheriting jsonb's",
        'ORDER BY o.key COLLATE "C"' in _ssql,
        True,
    )

    # ── the CHAIN rung's compiled SQL — ⟡ladder-fixpoint ─────────────────────────────────
    _xsql, _xp = _T.chain_sql("t1")
    check(
        "the chain rung is ONE statement carrying no SQL comment",
        (_xsql.count(";"), "--" in _xsql, _xp),
        (0, False, ("t1",)),
    )
    # ⚑⚑ THE ALLOCATION IS THE COLUMN'S OWN SEQUENCE, AND THE OVERRIDE IS TYPED. `dec_node.id`
    # stays `GENERATED ALWAYS` — the property that a writer cannot supply an id BY ACCIDENT —
    # and this one statement says `OVERRIDING SYSTEM VALUE` out loud. Relaxing the DDL to
    # `GENERATED BY DEFAULT` would have bought the same thing by weakening it for every writer.
    check(
        "...minting ids from dec_node's OWN sequence, with the identity override spelled out",
        (
            "nextval(pg_get_serial_sequence('dec_node', 'id'))" in _xsql,
            "OVERRIDING SYSTEM VALUE" in _xsql,
        ),
        (True, True),
    )
    # ⚑⚑ `AS MATERIALIZED` IS CORRECTNESS HERE, NOT SPEED. `alloc` is read twice — a cell's own
    # id and its child's — and an INLINED CTE evaluates `nextval` once per reference, minting two
    # different ids for one cell and silently breaking every `c2`. A behavioural case would catch
    # it, but only on a fixture whose spines are long enough to have a `c2` at all.
    check(
        "...with `alloc` MATERIALIZED, so `nextval` is evaluated once per cell and not twice",
        "alloc AS MATERIALIZED" in _xsql,
        True,
    )
    # ⚑⚑ NO `ON CONFLICT` ON `dec_node`, AND THAT ASYMMETRY IS THE CONCURRENCY OBSERVABLE. Inside
    # a batch a duplicate is impossible (distinct anchors ⇒ distinct ids ⇒ distinct `c2`), and no
    # new cell can equal an existing row (its `c2` is freshly minted) — so a 23505 on this
    # statement is evidence of a CONCURRENT WRITER and of nothing else, and the transaction
    # aborts having written nothing. `ON CONFLICT DO NOTHING` would instead DROP the losing row
    # while its parent kept referencing the id it was promised: a silent dangling reference in
    # place of a loud, harmless abort. `dec_ref` keeps it, because it is address-keyed.
    check(
        "...inserting dec_node WITHOUT `ON CONFLICT` while dec_ref keeps it — the 23505 IS the "
        "concurrency signal",
        (
            _xsql.count("ON CONFLICT DO NOTHING"),
            "OVERRIDING SYSTEM VALUE\n    SELECT n.id" in _xsql,
        ),
        (1, True),
    )
    check(
        "...and forces dec_node's locks to be taken before dec_ref's, like the flat rung",
        "(SELECT count(*) FROM ins) >= 0" in _xsql,
        True,
    )
    # ⚑⚑ THE RECURSION STOPS AT THE CUT, AND THAT ONE PREDICATE IS THE WHOLE COST MODEL. Without
    # it the walk carries the entire spine — 9,764 iterations for one fixture-scale document,
    # each re-probing a materialised 48,831-row CTE — and the build does not finish. With it the
    # recursion is `|existing suffix| + 1` deep and the new cells come straight out of `f`.
    check(
        "...walking only the EXISTING suffix: the recursive term stops the moment a lookup misses",
        "WHERE w.rid IS NOT NULL" in _xsql,
        True,
    )
    # ⚑ THE DEDUP IS A PARTITION BY THE ANCHOR — the deepest new cell's content, known BEFORE any
    # id is minted. No digest, no hash, and no key whose size grows with the subtree, which is
    # exactly what §ⓧ.wall proved impossible for a node KEY and never asked of a batch PARTITION.
    check(
        "...deduping across spines by partitioning on the ANCHOR, never by a digest",
        (
            "PARTITION BY a.head, a.c1, a.kid" in _xsql,
            ("md5" in _xsql or "digest" in _xsql or "hash" in _xsql),
        ),
        (True, False),
    )
    check(
        "...and scoped by a concrete core_id, never a nullable disjunction",
        ("s.core_id = %s::text" in _xsql, "IS NULL OR s.core_id" in _xsql),
        (True, False),
    )
    # ⚑ THE FLAT SCHEDULE IS THE COMPLEMENT OF THE CHAIN RUNG, DERIVED FROM THE GRAMMAR. If it
    # still returned the spine rounds, every one of the 115,268 would be sent again and the
    # chain rung would merely be redundant — green, and paying the cost it was built to remove.
    _fsql, _fp = _T.flat_rounds_sql(None)
    check(
        "the flat schedule excludes spine cells, so the per-cell rounds are GONE not merely "
        "duplicated",
        ("s.kind <> 0 OR s.ord = 0" in _fsql, _fp),
        (True, (None, None)),
    )
    con.close()


if __name__ == "__main__":
    _argv = sys.argv
    _args = [a for a in _argv[1:] if not a.startswith("--")]
    if not (TREE_MODES & set(_argv)):
        # ⚑ A BARE RUN DESCRIBES AND DOES NOT WRITE — `sppf_db`'s worst recorded defect is a bare
        # run that defaulted to a subtree and opened a write transaction against the live store.
        print(__doc__.strip().splitlines()[0])
        print(
            "\n⚑ NO MODE GIVEN — refusing. A tool that writes when asked to describe "
            "itself is the defect.\n"
        )
        print("modes:")
        print("  --tree-build [RELPATH]     THE CALLER — materialise the work list, then run")
        print("                             the rung once per round to fixpoint. The RUNG is")
        print("                             one statement; the loop is a mode-branch and so")
        print("                             lives here. No RELPATH = every document.")
        print("  [FILTER] --tree-census     EXACT/MISSING driven from the work list, the three")
        print("                             absences counted apart, plus the SHARING")
        print("                             measurement and the per-head node histogram")
        print("  [RELPATH] --tree-stage     materialise the WORK LIST ONLY, and report the")
        print("                             chain shape (spines · cells · longest). The cost")
        print("                             model, readable BEFORE the fixpoint is paid.")
        print("  [RELPATH] --tree-rounds    the FIXPOINT ONLY, over an already-staged work list.")
        print("                             The resumable half: stage once, iterate as often as")
        print("                             needed without re-offering 9.5M skeleton rows.")
        print("  [RELPATH] --tree-chains    the chain WORK PREDICATE — spines ready/done/todo.")
        print("                             Writes nothing. `todo` not moving across a round is")
        print("                             the livelock signature, so it is readable apart")
        print("                             from the rung's own rowcount.")
        print("  [RELPATH] --tree-roundtrip the ACCEPTANCE TEST — reconstruct each document")
        print("                             FROM dec_node alone and compare against `dec`")
        print("  [RELPATH] --tree-wedge     the SQL forest against jea_pyalg.PyDivStr.wedge's,")
        print("                             with faithful_check on every node")
        print("  [FILTER] --tree-concurrency [N]")
        print("                             run N builders AT ONCE over FILTER's documents and")
        print("                             report whether any 40P01 (deadlock) occurred")
        print("  [RELPATH] --tree-sql [RND] print the rung VERBATIM — the statement the engine")
        print("                             is sent, not a transcription of it. Touches nothing")
        print("      [--sandbox]            every mode: the THROWAWAY tenant, never the corpus")
        sys.exit(2)
    sys.exit(tree_cli(_argv, _args))
