#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""sql_census.py — the GENERATED map of this repo's SQL / relational-algebra surface.

⚑ WHY THIS EXISTS, AND WHY IT IS GENERATED RATHER THAN WRITTEN.  The SQL surface here is
large (a 20 GB / 80 M-row postgres store, ~90 compiled query builders, a graded lift arc, an
Agda allegory) and it is the ONE family in this repo whose own map nothing kept honest:
`query_defs --check` gates the compiled cache and `toolmodes --check` gates the mode census,
but `sql_lift.py` shipped `--selftest`/`--report` only.  A reader asking "what is the SQL
story here" had to re-derive it from five tools, differently each time.

⚑ AND THE DRIFT IS NOT HYPOTHETICAL — IT WAS MEASURED WHILE THIS WAS BEING WRITTEN.  A
research agent reported `query_defs --check` STALE (3 builders differing); minutes later the
same command reported FRESH at 90 builders.  Both readings were honest; the tree moved.  A
hand-written map would have frozen the first one, and the next reader would have trusted a
sentence over the tool.  So this module DERIVES every figure it prints, and `--check` refuses
the block when the derivation and the committed text disagree.

The block lands in `.claude/skills/sql-relalg/SKILL.md` between the two marker lines.  Same
contract as `toolmodes.py --sync/--check`: `--sync` owns the block's CONTENT, never its
PLACEMENT — missing markers are a refusal, not an insertion, so "delete the block" stays an
instruction a human can carry out.

⚑ THE CENSUS IS A RENDERING, NOT A SECOND ANALYSIS.  Every number comes from the tool that
already owns the artifact — `sql_lift.build/licensed_lifts/classify_recursion` for the lift
map, `query_defs` for the builders, `schema_decl` for the relations and tiers.  A census that
re-derived any of these would be a second authority to drift against the first, which is the
roster-beside-a-roster shape this whole toolkit exists to retire.
"""

import os, sys, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SKILL_MD = os.path.join(REPO, ".claude", "skills", "sql-relalg", "SKILL.md")
BEGIN = "--- BEGIN sql-census ---"
END = "--- END sql-census ---"


class BlockError(Exception):
    """The host file or its marker pair is missing, duplicated or inverted — a fact
    about the TREE, reported as such rather than raised as a traceback.

    ⚑ A TRACEBACK IS NOT A DIAGNOSIS.  The first cut let a missing SKILL.md surface as a
    bare FileNotFoundError: the right exit code (1) attached to an unreadable message, so
    a gate whose HOST is absent read as a crashed tool rather than as the tree lacking the
    file.  Both halves — the code and the sentence — have to be answerable.
    """


def _read_skill():
    try:
        with open(SKILL_MD, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise BlockError(
            "%s does not exist — the census has no host. Create the skill with the two "
            "marker lines (`%s` … `%s`) where the block belongs; --sync-census fills "
            "between them but will not create the file."
            % (os.path.relpath(SKILL_MD, REPO), BEGIN, END)
        )


# ════════════════════════════════ the derivations ═════════════════════════════════════════
# Each returns plain data.  Nothing here formats; nothing here judges.


def lift_census(files=None):
    """The ⟡graded-relational-carrier map, from sql_lift's OWN build — never re-derived."""
    import sql_lift

    I, py, sql, rec = sql_lift.build(files)
    lifts = sql_lift.licensed_lifts(I, py, sql)
    verdict = lambda v: [r for r in rec if r[3].get("verdict") == v]
    return {
        "py_pipelines": len(py),
        "sql_pipelines": len(sql),
        "carrier_nodes": I.size(),
        "licensed": len(lifts),
        "recursion_pole": len(rec),
        "cte": len([r for r in rec if r[3]["transition"] == "recursion→parallel"]),
        "residue": len([r for r in rec if r[3]["sql_target"] == "residue"]),
        "carrier_unmodelled": len(verdict("carrier-unmodelled")),
        "refuted": len([r for r in rec if r[3].get("verdict") == "REFUTED"]),
        "heads": list(sql_lift.REL_HEADS),
        # the STEER line: the top lift by conductance×breadth, or None when there are none
        "top": (
            lambda rt: {
                "seq": " → ".join(h for h in rt.canon_seq() if h != "Scan"),
                "score": sql_lift.roofline(rt)["score"],
                "sites": len(rt.sites),
            }
        )(lifts[0][0])
        if lifts
        else None,
    }


def builder_census():
    """The compiled-query layer, from query_defs — the builder count and the dialect.

    ⚑ NO `hasattr` FALLBACK ON THE COUNT, and that is the `0 tier(s)` lesson applied.  A
    `getattr(..., [])` here would render `0 compiled builder(s)` the day the symbol is
    renamed — a figure that looks like a measurement and is an attribute miss.  Let the
    AttributeError escape: a census that cannot find its source must FAIL, not report zero.
    """
    import query_defs

    names = sorted(query_defs.INTERN_BUILDERS)
    out = {"builders": len(names), "dialect": None}
    try:
        import store

        d = store.dialect()
        # ⚑ THE DIALECT'S NAME, NEVER THE OBJECT.  A first cut printed `store.dialect()`
        # directly and rendered `<…PGDialect_psycopg2 object at 0x71f0a8319f50>` — an
        # ADDRESS, different every run, so `--check` would have failed nondeterministically
        # and the gate would have taught readers to ignore it.  A generated block may only
        # carry values that are functions of the TREE.
        out["dialect"] = getattr(d, "name", None) or str(d)
    except Exception:
        pass
    return out


def store_census():
    """The declared store: relations and tiers, FROM THE DECLARATION, never a list typed here.

    ⚑ DECLARED, NOT LIVE, AND THE DIFFERENCE IS THE POINT.  A census keyed on what the running
    tenant happens to hold would flip between a developer's sandbox and the live store, and a
    gate that flips is not a gate.  What the repo COMMITS to is the declaration; whether the
    tenant currently matches it is `schema.py --relations`' question, asked at read time.
    """
    import schema_decl

    tables = sorted(schema_decl.MD.tables)
    # ⚑ THE TIER MAP IS `_TIERS`, AND GUESSING `TIERS` RENDERED A CONFIDENT ZERO.  The first
    # cut read a public-looking name that does not exist; `getattr(..., {})` swallowed it and
    # the block printed `0 tier(s)` beside a correct relation count — a false figure in the
    # artifact built to stop false figures.  The selftest below now asserts `> 0` precisely
    # because a census cannot distinguish "none declared" from "read the wrong attribute".
    # ⚑ NO SILENT `{}` DEFAULT.  `_TIERS` is the declaration's own spelling; if it moves, this
    # must raise rather than render `0 tier(s)` — which is exactly what the first cut did.
    tiers = getattr(schema_decl, "_TIERS", None)
    if tiers is None:
        tiers = schema_decl.TIERS  # let the AttributeError name the missing symbol
    return {
        "relations": len(tables),
        "tiers": len(tiers),
        "tier_names": sorted(tiers),
        "views": len(getattr(schema_decl, "SHADOWS", {}) or {}),
    }


def readers_census():
    """The tools that OWN a question about this surface — path → the question it answers.

    ⚑ A ROSTER, AND DELIBERATELY A SHORT ONE.  This is the `artifact → tool` row-set for the
    SQL family, the same shape struct-tools carries for the repo at large.  It is DATA here
    (not prose in the skill) so the block can assert each path still exists: a tool that is
    renamed or deleted breaks the gate instead of rotting into a false pointer.
    """
    return [
        ("jea/metalanguage/schema.py", "the live store — census, spread, lifecycle, locks, plan"),
        ("jea/metalanguage/schema_decl.py", "THE schema declaration — tables, tiers, shadows"),
        ("jea/metalanguage/store.py", "THE tenant authority — dsn, dialect, sandbox vs live"),
        (
            "jea/metalanguage/query_defs.py",
            "the query COMPILER — sql, equiv, explain, scans, check",
        ),
        ("jea/metalanguage/query_builders.py", "the cached SQLAlchemy-free RUNTIME"),
        (
            "jea/metalanguage/query_registry.py",
            "index priority by orbit BREADTH × direction × selectivity",
        ),
        ("jea/metalanguage/sql_lift.py", "⟡graded-relational-carrier — which python ops LIFT"),
        ("jea/metalanguage/numpy_builders.py", "the ⟡H3 numpy↔SQL hexagon (byte-exact arms)"),
        ("scratch/pycodemod.py", "--sql/--sqlname/--relname/--relalg over the python corpus"),
        ("agda/Substrate/Category/Allegory.agda", "Rel as a TABULAR allegory (the modular law)"),
    ]


def _exists(rel):
    return os.path.exists(os.path.join(REPO, rel))


# ════════════════════════════════ the block ═══════════════════════════════════════════════


def render_block(files=None):
    """The census as it belongs between the markers.  Pure function of the tree."""
    L = lift_census(files)
    B = builder_census()
    S = store_census()
    R = readers_census()
    out = []
    out.append(
        "⚑ **GENERATED — DO NOT EDIT BY HAND.** `python3 jea/metalanguage/sql_lift.py --sync-census`"
    )
    out.append("rewrites everything between the markers; a hand edit is overwritten on the next")
    out.append(
        "sync, and `--check-census` is a pre-commit gate that refuses drift. Every figure is"
    )
    out.append(
        "DERIVED from the tool that owns it — the lift map from `sql_lift.build`, the builder"
    )
    out.append(
        "count from `query_defs`, the relations and tiers from `schema_decl`. No number below"
    )
    out.append("is typed by a human, which is why none of them can rot into a false claim.")
    out.append("")
    out.append("```")
    out.append("── THE GRADED RELATIONAL CARRIER (⟡graded-relational-carrier / the sql-lift arc)")
    out.append(
        "   %d python Rel-pipelines · %d SQL builder pipelines · ONE interned carrier (%d nodes)"
        % (L["py_pipelines"], L["sql_pipelines"], L["carrier_nodes"])
    )
    out.append("   Rel heads: %s" % " ".join(L["heads"]))
    out.append(
        "   A python op is a LICENSED LIFT exactly when its Rel-lowering is grade-0 coherent"
    )
    out.append("   with an SQL construct — PROVED BY SAME-INTERNED-ID, never by similarity.")
    out.append("")
    out.append("   licensed lifts .......... %d" % L["licensed"])
    out.append("   recursion-pole walks .... %d" % L["recursion_pole"])
    out.append("     → recursion→parallel .. %d   (lifts to WITH RECURSIVE)" % L["cte"])
    out.append(
        "     → residue ............. %d   (no relational form — the honest greatest-fp)"
        % L["residue"]
    )
    out.append("     → carrier-unmodelled .. %d   ⚑ WORK, NOT A WALL" % L["carrier_unmodelled"])
    out.append(
        "     → refuted ............. %d   (a residue verdict a probe overturned)" % L["refuted"]
    )
    if L["top"]:
        out.append(
            "   STEER: [%s] first (score %+.4f over %d site(s))"
            % (L["top"]["seq"], L["top"]["score"], L["top"]["sites"])
        )
    out.append("")
    out.append(
        "   ⚑ CARRIER-UNMODELLED IS NOT RESIDUE. Residue is a claim about the COMPUTATION (a"
    )
    out.append(
        "     Merkle fold has no SQL aggregate). Carrier-unmodelled is a claim about what has"
    )
    out.append(
        "     been MODELLED: the walk is already a closure and lifts the moment its carrier has"
    )
    out.append(
        "     a relational form — which need not be durable (a VALUES list, a CTE, an unnest)."
    )
    out.append("")
    out.append("── THE QUERY LAYER (⟡qinfra)")
    out.append(
        "   %d compiled builder(s)%s"
        % (B["builders"], ("  ·  dialect: %s" % B["dialect"]) if B["dialect"] else "")
    )
    out.append("   query_defs.py is the COMPILER; query_builders.py is the cached SQLAlchemy-free")
    out.append("   RUNTIME. `--check` gates the two against each other and pre-commit runs it.")
    out.append("")
    out.append("── THE DECLARED STORE")
    out.append(
        "   %d relation(s) · %d tier(s) · %d declared view/shadow(s)"
        % (S["relations"], S["tiers"], S["views"])
    )
    out.append("   tiers: %s" % " ".join(S["tier_names"]))
    out.append(
        "   ⚑ DECLARED, not live. Whether the running tenant matches is `schema.py --relations`'"
    )
    out.append("     question — and it takes --sandbox or --live, because a read against the wrong")
    out.append("     tenant returns PLAUSIBLE ROWS nobody can distinguish.")
    out.append("")
    out.append("── WHO OWNS WHICH QUESTION")
    for rel, what in R:
        mark = "" if _exists(rel) else "   ⚑ ABSENT"
        out.append("   %-42s %s%s" % (rel, what, mark))
    out.append("```")
    return "\n".join(out)


def _span(src):
    """(body_start, body_end) for the marker block — missing markers REFUSE, never insert."""
    i, j = src.find(BEGIN), src.find(END)
    if i < 0 or j < 0:
        raise BlockError(
            "no `%s` … `%s` pair in %s — add the two marker lines where the block belongs; "
            "--sync-census fills between them but will not choose their place."
            % (BEGIN, END, SKILL_MD)
        )
    if src.count(BEGIN) != 1 or src.count(END) != 1:
        raise BlockError(
            "%s carries %d `%s` and %d `%s` marker(s); exactly one of each is required."
            % (SKILL_MD, src.count(BEGIN), BEGIN, src.count(END), END)
        )
    if j < i + len(BEGIN):
        raise BlockError(
            "`%s` precedes `%s` in %s — the markers are inverted." % (END, BEGIN, SKILL_MD)
        )
    return i + len(BEGIN), j


def splice(src, body):
    a, b = _span(src)
    return src[:a] + "\n" + body + "\n" + src[b:]


def current_body(src):
    a, b = _span(src)
    return src[a:b]


def cmd_sync(files=None):
    src = _read_skill()
    new = splice(src, render_block(files))
    rel = os.path.relpath(SKILL_MD, REPO)
    if new == src:
        print("sql_lift --sync-census: %s in %s already current." % (BEGIN.strip("- "), rel))
        return 0
    with open(SKILL_MD, "w", encoding="utf-8") as f:
        f.write(new)
    print(
        "sql_lift --sync-census: rewrote the census in %s (%d bytes -> %d)."
        % (rel, len(src), len(new))
    )
    return 0


def cmd_check(files=None):
    """DRIFT GATE — exit 1 unless the committed block is what --sync-census would write."""
    src = _read_skill()
    fresh = render_block(files)
    rel = os.path.relpath(SKILL_MD, REPO)
    if splice(src, fresh) == src:
        print("sql_lift --check-census: the census in %s is fresh." % rel)
        return 0
    # ⚑ PRINT THE DIFFERENCE, NOT JUST THE VERDICT — the gate already holds the delta,
    # and withholding it costs the reader a --sync plus a `git diff` to learn what moved.
    for line in difflib.unified_diff(
        current_body(src).splitlines(),
        ("\n" + fresh + "\n").splitlines(),
        fromfile="%s (committed)" % rel,
        tofile="derived just now",
        lineterm="",
    ):
        print(line)
    print(
        "\nsql_lift --check-census: the census in %s is STALE — run "
        "`python3 jea/metalanguage/sql_lift.py --sync-census`" % rel,
        file=sys.stderr,
    )
    return 1


# ════════════════════════════════ the guarded cases ═══════════════════════════════════════
def selftest():
    """⚑ EVERY DERIVATION IS A CASE, because each one reaches into ANOTHER module's
    surface (`schema_decl.MD`, `query_defs.INTERN_BUILDERS`, `sql_lift.build`) and an
    attribute that quietly moves would otherwise turn this census into a confident
    ZERO.  A count of 0 renders exactly as legitimately as a count of 90; only a case
    can tell the two apart.  Same defect class as `--dead` and its callbacks: the
    absence is real, the conclusion drawn from it is not.
    """
    sys.path.insert(0, os.path.join(REPO, "scratch"))
    sys.path.insert(0, HERE)
    import rungs

    check = rungs.Cases(key="jea/metalanguage/sql_census.py")

    S = store_census()
    check("the declaration yields relations", S["relations"] > 0, True)
    check("the declaration yields tiers", S["tiers"] > 0, True)
    B = builder_census()
    check("query_defs yields compiled builders", B["builders"] > 0, True)

    # ⚑ THE ROSTER MUST NAME FILES THAT EXIST.  A renamed tool would otherwise leave a
    # pointer that reads as authoritative — the same rot the generated block prevents
    # for NUMBERS, here applied to PATHS.
    missing = [rel for rel, _ in readers_census() if not _exists(rel)]
    check("every tool the census names exists", missing, [])

    try:
        src = _read_skill()
        body = render_block()
        check("splice is idempotent", splice(splice(src, body), body), splice(src, body))
        check(
            "the block round-trips through its markers",
            current_body(splice(src, body)).strip(),
            body.strip(),
        )
    except BlockError as e:
        check("the skill carries exactly one marker pair", str(e), "")

    return check.report()


# ⚑ A SUITE THAT CANNOT BE INVOKED DOES NOT RUN, AND `run_selftests` DISCOVERS BY
# CONVENTION — a `--selftest` flag on a module in its scan set.  Without this block the
# cases above would exist, pass in principle, and contribute nothing to any total: the
# same "written but never wired" shape the pre-commit hook records for five gates.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--sync" in sys.argv:
        sys.exit(cmd_sync())
    if "--check" in sys.argv:
        sys.exit(cmd_check())
    print(__doc__, file=sys.stderr)
    print(
        "modes:\n  --sync      rewrite the census block in the sql-relalg skill\n"
        "  --check     DRIFT GATE: exit 1 unless that block is current\n"
        "  --selftest  the guarded cases\n"
        "(the canonical spellings are `sql_lift.py --sync-census` / `--check-census`)",
        file=sys.stderr,
    )
    sys.exit(2)
