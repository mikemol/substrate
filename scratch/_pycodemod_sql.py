# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""SQL-inside-Python: the store-query layer of `pycodemod`.

⚑ THIS IS A SEAM BECAUSE THE STATE NEVER LEAVES IT.  `--sql`, `--rawreads`,
`--portable` and `--relalg` are four questions about one artifact — a SQL string
living inside a `.py` — and they share machinery no other mode touches: the
`_PG_*` postgres probe connections, `_PORT_REMEDY`, `RELALG_KINDS`.  `--binding`
confirms the cut: every reference to `_PG_CON` falls inside this block and none
outside it, so the module has no back-edge into the core.

⚑ THE ⚑ COMMENTS BELOW ARE THE ARC'S INCIDENT LOG AND MOVED VERBATIM WITH THEIR
FUNCTIONS — the measured defect that produced each mode is worth more than the
mode.  This file was produced by a CST transform, not a hand sweep, precisely so
that the commentary could not be silently dropped in transit.

⚑ TWO KNOWN DEFECTS TRAVEL WITH THIS CODE, unfixed and stated as findings:
`sql_sites` is blind to a SQL literal that is the left operand of a `%` BinOp —
the repo's own mandated `"…" % ph()` placeholder idiom — so every `--sql` census
is a LOWER BOUND; and `relalg_sites` cannot see a loop-with-early-break.  Both
are separate open items; nothing here makes them worse.

Imported for its public names by `pycodemod.py`, which remains the entry point
and the mode index.

⚑ `ROOT` IS READ THROUGH THE MODULE OBJECT, NEVER `from … import ROOT`, AND THAT
IS LOAD-BEARING.  `--binding ROOT` shows it rebound by `corpus.__enter__` at
runtime: `--archive` / `--in` work by swapping the corpus root under every mode.
A `from`-import binds a SNAPSHOT taken at import time, so these four modes would
have kept answering about the main tree while the rest of the tool answered about
the archive — a silent wrong-corpus read, the defect class the repo's own
`wrong-tenant-read-is-silent` memory records.  `_c.ROOT` re-reads the live value.
"""
import ast
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import libcst as cst
    import libcst.metadata  # noqa: F401
except ImportError:  # pragma: no cover - environment probe
    cst = None

import _pycodemod_core as _c
from _pycodemod_core import py_files




def sql_sites(ident, path):
    """[(style, table_or_kw, line, snippet)] — SQL literals touching `ident`.

    ⚑ BUILT BECAUSE THREE PROBES ANSWERED ONE QUESTION BADLY (research agent,
    2026-08-04, naming the gap per SKILL.md rather than routing around it).
    Asked "is the import DAG already a table, and does anything query it
    recursively", `--key module_edges` returned `0 of 750 files` — a null result
    about the MODE, since `--key` matches dict subscripts (`d["k"]`) and cannot
    see inside a SQL string.  The relation was plainly there: `_module_edges`,
    15,754 rows, indexed both ways.

    ⚑ SO THE ARTIFACT IS SQL-INSIDE-PYTHON, AND IT HAD NO READER.  A `.py` is
    owned by this tool; a SQL string inside one is structured text this tool
    could not parse.  That is the toolkit-gap-read-as-a-category error the
    standing rule names — the answer is a mode, not a grep for `SELECT`.

    ⚑ WHAT COUNTS AS SQL IS STRUCTURAL, NOT A KEYWORD MATCH.  A string is SQL
    here iff `sqlite3.complete_statement` accepts it as a complete statement, or
    it parses as a fragment whose first token is a DML/DDL keyword.  Grepping
    for `SELECT` would match this very docstring — and matching prose is how a
    census reports sites that are not sites.

    ⚑ AND THE STYLE IS THE FINDING, NOT JUST THE HIT.  This repo runs a
    three-layer split: `query_defs.py` COMPILES with SQLAlchemy (build-time),
    `query_sql.py` is the generated cache, `query_builders.run(con, name)` is
    the runtime that imports no SQLAlchemy.  A raw `con.execute("SELECT ...")`
    bypasses all three.  Reporting `raw` vs `compiled` vs `builder` is what
    makes the answer actionable rather than a count."""
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        return [("<unreadable>", str(e), 0, "")]
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        return [("<syntax-error>", str(e), 0, "")]

    import sqlite3 as _sq
    # ⚑ DDL/DML HEADS ONLY.  `WITH` is included because a recursive CTE is the
    # shape the DAG question turns on, and it never appears as a bare statement
    # head anywhere else in Python source.
    HEADS = ("select", "insert", "update", "delete", "create", "drop",
             "alter", "with", "pragma", "replace")

    # ⚑ A HEAD KEYWORD IS NOT A STATEMENT, AND MY FIRST PREDICATE SAID IT WAS.
    # Testing `--sql RECURSIVE` returned `sql_lift.py:565` = `"WITH RECURSIVE +"`
    # and `:567` = `"WITH RECURSIVE (UNION)"` — PROSE LABELS in a cost model,
    # admitted because the head matched and my fallback accepted any fragment
    # over two tokens.  That is the guard-from-the-instance defect: I wrote the
    # test against the statements I expected and it passed everything shaped
    # vaguely like them.  Caught by running the mode on a second identifier, not
    # by reading it.
    #
    # A statement is recognised by a SQL ENGINE ITSELF, never by a keyword list.
    #
    # ⚑ THE `CLAUSES` TUPLE THAT STOOD HERE WAS DEAD, AND ITS COMMENT DESCRIBED A
    # MECHANISM THE CODE DID NOT HAVE — "a fragment must additionally carry a
    # CLAUSE keyword" was true of the design and false of the body, which never
    # read the name. It is deleted rather than re-wired because the parser probe
    # SUBSUMES it: prose that clears the head test ("WITH RECURSIVE +") fails to
    # parse, which is the same rejection by a stronger judge. The note stays as
    # the residue — a reader finding the tuple gone should know it was redundant,
    # not lost.

    # ⚑⚑ A FORMAT PLACEHOLDER IS A VALUE, NOT SYNTAX — AND TREATING IT AS SYNTAX
    # MADE THIS CENSUS BLIND TO THE IDIOM THIS REPO MANDATES (ⓑ). `schema.ph()`
    # exists precisely so a caller never types a placeholder, so the house style is
    # `"… WHERE core_id = %s" % ph()` — and `%` is sqlite's MODULO, so every one of
    # those literals died at `syntax error near "%"` and was reported as not-SQL.
    # MEASURED before the fix: `--sql obs jea/metalanguage/schema_queue.py` returned
    # 5 sites while the file holds a `SELECT count(*) FROM obs …`, a
    # `SELECT count(*) FROM (…) d` and **the `DELETE FROM obs` the drain runs** —
    # i.e. the census could not see the statement that deletes the corpus.
    #
    # `NULL` and not `?`, because the same normalised text is offered to BOTH
    # engines below and `?` is not a postgres parameter marker. A placeholder in a
    # RELATION position (`FROM (%s) d`) still fails, and correctly: that string is a
    # TEMPLATE, not a statement, and it names no table for a census to find.
    _PLACEHOLDER = re.compile(r"%\(\w+\)s|%[sdifr]|(?<![\w$]):[a-z_]\w*", re.I)

    # ⚑ ONE CONNECTION FOR THE WHOLE FILE, and one memo for repeated strings. This
    # opened a fresh `:memory:` database PER STRING — thousands per corpus scan.
    _lite = _sq.connect(":memory:")
    _memo = {}

    def _parses(t):
        """Does either engine accept `t` as a statement? sqlite first (no I/O)."""
        try:
            _lite.execute("EXPLAIN " + t)
            return True
        except _sq.OperationalError as e:
            # "no such table/column" means it PARSED — the grammar is valid and
            # only the schema is absent, which is the normal case for a literal
            # read out of source with no database attached.
            if "no such" in str(e):
                return True
        except Exception:
            pass
        # ⚑⚑ AND THE SECOND ORACLE IS THE ONE THE STORE ACTUALLY RUNS. sqlite's
        # grammar is NOT postgres's, and this module kept judging a postgres-only
        # corpus by it long after ⓺ dropped the backend — `DELETE FROM event e
        # WHERE …` (a DELETE alias), `age(xmin)`, `IS DISTINCT FROM`, `WITH
        # ORDINALITY` and `RETURNING` are all valid here and all rejected there.
        # A recogniser holding a retired premise reports the corpus's own dialect
        # as prose. Postgres is tried ONLY when sqlite refuses, so the common path
        # costs nothing and a machine with no store degrades to sqlite alone.
        con = _pg_probe_con()
        if con is None:
            return False
        try:
            with con.transaction():
                con.cursor().execute("EXPLAIN " + t)
            return True
        except Exception as e:
            # UndefinedTable/UndefinedColumn == parsed; the schema's absence is a
            # fact about the STORE, exactly as "no such table" is above.
            return "does not exist" in str(e)

    def is_sql(s):
        t = s.strip().lstrip("(").strip()
        if not t:
            return False
        toks = [w.lower().strip("(),;") for w in t.split()]
        if not toks or toks[0] not in HEADS:
            return False
        if t not in _memo:
            _memo[t] = _parses(_PLACEHOLDER.sub("NULL", t))
        return _memo[t]

    # ⚑ `complete_statement` IS A LEXER, NOT A PARSER — and using it as one was
    # my SECOND wrong predicate here.  It reports whether a string is lexically
    # terminated (balanced quotes, trailing `;`), so appending `;` makes almost
    # anything "complete": `"WITH RECURSIVE +;"` passes.  My tightening therefore
    # changed NOTHING, and the re-run returned the same 7 rows — which is the only
    # reason I noticed, having been about to report the fix as landed.  A SQL
    # engine can actually PARSE, via `EXPLAIN`; that is what `_parses` above uses,
    # and it is why the keyword list it replaced could go.

    # ⚑ THE STYLE COMES FROM THE ENCLOSING CALL, so a literal is classified by
    # HOW IT IS RUN, not by what it says.  Walking Call nodes first and
    # recording their string args is what distinguishes `con.execute(raw)` from
    # a `_DB_SCHEMA = """..."""` constant that a schema applier consumes.
    style_of = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        nm = (fn.attr if isinstance(fn, ast.Attribute)
              else fn.id if isinstance(fn, ast.Name) else "")
        # ⚑⚑ DESCENDANTS OF THE ARGUMENT, NOT THE ARGUMENT ITSELF — because the
        # house style hands `execute` a BinOp, never a bare Constant. `execute(con,
        # "DELETE FROM obs WHERE core_id IN (%s)" % _DRAINABLE)` presented an
        # `ast.BinOp`, so the literal inside fell through to `literal` and the drain's
        # own DELETE was censused as an inert string. Walking each arg catches the
        # `%`, `.format`, and nested-call spellings with one rule instead of three.
        #
        # ⚑ AND THE EXECUTOR ROSTER INCLUDES THIS REPO'S OWN CONTRACT, WHICH IS A
        # NAMED WEAKNESS RATHER THAN A CLEAN PREDICATE. `schema.rows`/`scalar`/
        # `execute` ARE raw execution — `scalar(con, "SELECT count(*) …")` runs
        # exactly what `con.execute` would — but there is no structural test for "is
        # this function an executor", so this is a list, and a list is a frozen
        # roster. A new executor is invisible here until its name is added; that is
        # the cost, stated, of not having a call-graph reaching the driver.
        if nm in ("execute", "executemany", "executescript",
                  "execute_many", "rows", "scalar"):
            for a in node.args:
                for sub in ast.walk(a):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        style_of[id(sub)] = "raw"
        elif nm == "run":
            style_of[id(node)] = "builder"

    out = []
    low = ident.lower()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if not is_sql(s):
                continue
            if low not in s.lower():
                continue
            head = s.strip().split(None, 1)[0].upper()
            # ⚑ THE FULL STATEMENT, NOT A 70-CHAR EXCERPT. This truncated here, and
            # `_print_sql` printed the result — so the DISPLAY limit was baked into the
            # DATA. That was invisible until `--portable` fed these strings to postgres's
            # EXPLAIN and got "syntax error at end of input" on a perfectly valid
            # `CREATE TABLE …`: the census was judging a fragment. A consumer that wants
            # 70 characters can take them; one that wants to PARSE the statement cannot
            # recover what was cut.
            sql = " ".join(s.split())
            out.append((style_of.get(id(node), "literal"), head,
                        node.lineno, sql))
    return out


# ── `--relname` — WHERE IS THIS NAME USED **AS A RELATION** ─────────────────────────
#
# ⚑⚑ BUILT BECAUSE THE TWO NEIGHBOURING MODES ARE BOTH SUBSTRING MATCHES, AND FOR A
# SHORT RELATION NAME THAT IS NOT A CENSUS. `--sql node` returns 82 sites of which the
# overwhelming majority are `node_child`, `obs_node`, `orbit_node`, `unit_node` and
# `_node`; `--literal orbit` returns a 52 KB report dominated by `orbit_key`,
# `_orbit_def` and `--orbit`. Both docstrings state the substring bound honestly and
# both call it "good for a safety question" — which is true only while a HUMAN reads
# the value column and discards the misses. That discarding is the judgement the
# standing rule says must live in a program, and it is exactly the step a view-removal
# census cannot afford to get wrong: a missed consumer fails at RUNTIME, not at import.
#
# ⚑ SO THE QUESTION IS A GRAMMAR POSITION, NOT A TOKEN. `node` is referenced iff it
# appears where the SQL grammar expects a relation — after `FROM`, after `JOIN`, after
# `INSERT INTO`, after `UPDATE`, after `CREATE`/`DROP`/`ALTER`/`TRUNCATE TABLE|VIEW`.
# `obs_node` in a FROM clause is a DIFFERENT identifier, and `nd.node_id` is a column.
# A word-boundary regex gets the first right and the second wrong.
#
# ⚑ AND THE SECOND HALF IS THE SHIM SPELLING, WHICH CARRIES NO SQL AT ALL. `query_decl`
# declares views to the builder layer as `_T("node", …)` and `schema_rows.relations()`
# hands names about as bare strings — so a relation can be consumed with no SQL literal
# anywhere. Reported as role `name` (string literal EXACTLY equal, via `literal_sites`,
# whose substring match is filtered to equality here) beside role `sql`. One question —
# *where is this name used as a relation* — has two spellings, so it gets one mode.
#
# ⚑ THREE STATED BOUNDS, none of them repaired here:
#   * it inherits `sql_sites`'s corpus — `ast.Constant` strings only, so a table name
#     reaching SQL through an f-string or a `%s` in RELATION position is invisible (the
#     placeholder normaliser turns `%s` into `NULL`, which names no table). `--sql`'s
#     substring form still sees the surrounding text, so the two are complementary.
#   * a CTE is EXCLUDED (`WITH reach(…) AS (…) … FROM reach` reports `node_child`, not
#     `reach`) — a CTE is a name bound by the statement, not a relation the store holds.
#   * a table FUNCTION (`FROM generate_series(…)`) is not a relation and is skipped;
#     the trailing `(` is what distinguishes it, structurally.
_REL_TOK = re.compile(
    r"""(?P<ws>\s+)
      | (?P<lc>--[^\n]*)
      | (?P<bc>/\*.*?\*/)
      | (?P<str>'(?:[^']|'')*')
      | (?P<qid>"(?:[^"]|"")*")
      | (?P<id>[A-Za-z_][A-Za-z_0-9$]*)
      | (?P<num>\d+(?:\.\d+)?)
      | (?P<op>.)""",
    re.X | re.S)

# ⚑ A ROSTER OF KEYWORDS THAT END A RELATION LIST — and it is a roster, which is the
# known-frozen half of this mode. A relation genuinely NAMED `set` or `values` would be
# read as a terminator. Nothing in this corpus is; a wider grammar would need a parser,
# and there is no SQL parser in the venv (`uv pip list`: no sqlglot, no sqlparse), which
# is why this is a positional lexer rather than an AST walk.
_REL_END = frozenset("""
    where group order having limit offset fetch window union intersect except
    returning set values on using join left right inner outer full cross natural
    with select from into as and or not when then else end for do conflict nothing
    update delete insert create drop alter truncate table view index if exists
    distinct all by asc desc ordinality recursive primary key constraint unique
    default null case is in like between over partition filter tablesample
""".split())


def _rel_tokens(sql):
    """[(kind, text)] — SQL lexed, whitespace and comments dropped."""
    out = []
    for m in _REL_TOK.finditer(sql):
        if m.lastgroup not in ("ws", "lc", "bc"):
            out.append((m.lastgroup, m.group()))
    return out


def _rel_ident(t):
    """`"foo"` → `foo`; a bare identifier is returned unchanged."""
    return t[1:-1].replace('""', '"') if t.startswith('"') else t


def _rel_match(toks, i, hi):
    """Index of the `)` matching the `(` at `i`, or `hi` if unbalanced."""
    d = 0
    while i < hi:
        if toks[i][1] == "(":
            d += 1
        elif toks[i][1] == ")":
            d -= 1
            if d == 0:
                return i
        i += 1
    return hi


def _rel_skip_alias(toks, i, hi):
    """Past an `AS x` / bare `x` alias and any `(col, …)` alias list."""
    if i < hi and toks[i][0] == "id" and toks[i][1].lower() == "as":
        i += 1
        if i < hi and toks[i][0] in ("id", "qid"):
            i += 1
    elif i < hi and toks[i][0] in ("id", "qid") and (
            toks[i][0] == "qid" or toks[i][1].lower() not in _REL_END):
        i += 1
    if i < hi and toks[i][1] == "(":
        i = _rel_match(toks, i, hi) + 1
    return i


def _rel_list(toks, i, hi, ctes, single=False, fn_call=True, role="r"):
    """(next_index, {(name, role)}) — the relation list starting at `i`.

    ⚑⚑ `role` IS THE READ/WRITE SPLIT AND IT IS CARRIED HERE RATHER THAN RECOVERED
    LATER, because the position is the only thing that knows. `DELETE FROM
    core_decoded c WHERE EXISTS (SELECT 1 FROM core_decoded_shadow …)` and `INSERT
    INTO dec_val … SELECT … FROM dec_val` both name a relation TWICE with opposite
    meanings; a set of names, differenced after the fact, reports the first as a read
    it is not and the second as a write-only it is not. The grammar position that
    `_rel_walk` already computes to find the name at all is exactly the datum, so it
    is tagged in place and `sql_relnames` becomes a projection — the two cannot
    disagree about what a statement touches while disagreeing about which way.

    ⚑ A DERIVED TABLE RECURSES rather than being skipped, and the difference is
    measurable: `SELECT count(*) FROM (SELECT n.core_id FROM obs_node n WHERE …) d`
    is the shape `schema_queue.py:769` actually uses, and a wholesale skip of the
    parenthesised group reports that statement as touching NO relation at all.

    ⚑⚑ `fn_call` IS WHY `INSERT INTO terms (term_id, text)` FINDS `terms`, and its
    absence was a real miss the selftest caught rather than review. A `(` after a name
    means opposite things in the two positions this function serves: in a FROM/JOIN
    position `name(…)` is a TABLE FUNCTION (`generate_series(1,3)`) and names no stored
    relation, while after `INSERT INTO` / `UPDATE` / `CREATE TABLE` the identical token
    sequence is a COLUMN LIST and the name IS the relation. Reading it as a function
    dropped the target of every column-listed INSERT in the corpus — an absence produced
    by the method, reported as a fact about the SQL.
    """
    out = set()
    while i < hi:
        while i < hi and toks[i][0] == "id" and toks[i][1].lower() in ("only", "lateral"):
            i += 1
        if i >= hi:
            break
        k, t = toks[i]
        if t == "(":
            end = _rel_match(toks, i, hi)
            nxt = toks[i + 1][1].lower() if i + 1 < end else ""
            out |= _rel_walk(toks, i + 1, end, ctes,
                             nxt in ("select", "with", "values", "table"))
            i = _rel_skip_alias(toks, end + 1, hi)
        elif k in ("id", "qid"):
            if k == "id" and t.lower() in _REL_END:
                break
            parts = [_rel_ident(t)]
            i += 1
            while i + 1 < hi and toks[i][1] == "." and toks[i + 1][0] in ("id", "qid"):
                parts.append(_rel_ident(toks[i + 1][1]))
                i += 2
            if fn_call and i < hi and toks[i][1] == "(":
                # a table FUNCTION — `generate_series(…)` names no stored relation.
                i = _rel_match(toks, i, hi) + 1
            else:
                out.add((parts[-1].lower(), role))
            i = _rel_skip_alias(toks, i, hi)
        else:
            break
        if single or i >= hi or toks[i][1] != ",":
            break
        i += 1
    return i, out


def _rel_walk(toks, lo, hi, ctes, qscope):
    """{(name, role)} referenced in `toks[lo:hi]` — role `'r'` read, `'w'` written.

    ⚑ THE WRITE POSITIONS ARE THE FOUR THE GRAMMAR HAS, and `DELETE` is the one that
    does NOT look like one: its target sits after `FROM`, the same token that
    introduces every read in the language. What separates them is the token BEFORE —
    `prev` — which this walk already computes for the `INSERT INTO` / `CREATE TABLE`
    cases. A reader that keyed on `FROM` alone would report the retire rung's DELETE
    target as a read of the tier it deletes, i.e. it would manufacture the exact
    same-tier read the ⒣ gate exists to refuse.

    ⚑ `qscope` IS WHY `EXTRACT(EPOCH FROM ts)` DOES NOT REPORT A RELATION `ts`. A
    paren opens a QUERY scope iff its first token is `select`/`with`/`values`/`table`;
    otherwise it is an EXPRESSION scope, where `FROM` is the `extract`/`substring`/
    `trim` idiom and introduces nothing. Recursion happens either way — a subquery
    nested inside an expression (`coalesce((SELECT max(x) FROM t), 0)`) re-enters
    query scope on its own paren, so gating the RECURSION on the scope (my first cut)
    would have lost it.
    """
    out = set()
    i = lo
    while i < hi:
        k, t = toks[i]
        if t == "(":
            end = _rel_match(toks, i, hi)
            nxt = toks[i + 1][1].lower() if i + 1 < end else ""
            out |= _rel_walk(toks, i + 1, end, ctes,
                             nxt in ("select", "with", "values", "table"))
            i = end + 1
            continue
        if k != "id" or not qscope:
            i += 1
            continue
        low = t.lower()
        prev = ""
        for j in range(i - 1, max(lo, i - 3) - 1, -1):
            if toks[j][0] == "id":
                prev = toks[j][1].lower()
                break
        # ⚑⚑ `IS [NOT] DISTINCT FROM` IS NOT A RELATION INTRODUCER, AND THIS WAS A LIVE
        # FALSE POSITIVE, not a hypothetical. `dec_drain`'s retire predicate is
        # `s.dec IS NOT DISTINCT FROM c.dec` — the operator this whole ladder turns on —
        # and the walker read its `FROM` as a relation list, reporting a relation named
        # `dec` in the read set of every statement that carries the predicate (MEASURED:
        # `retire_sql` and `root_sql`, both). It belongs to the same family as the
        # `EXTRACT(EPOCH FROM ts)` guard one branch down, and is missed by it because
        # this `FROM` sits at query scope with no paren of its own. `distinct` is the
        # discriminator: nothing else in the grammar puts it immediately before `FROM`.
        if low in ("from", "join") and not (low == "from" and prev == "distinct"):
            i, got = _rel_list(toks, i + 1, hi, ctes, single=(low == "join"),
                               role=("w" if low == "from" and prev == "delete"
                                     else "r"))
            out |= got
            continue
        if low == "update" or (low == "into" and prev in ("insert", "replace")):
            i, got = _rel_list(toks, i + 1, hi, ctes, single=True, fn_call=False,
                               role="w")
            out |= got
            continue
        if low in ("table", "view") and prev in (
                "create", "drop", "alter", "truncate", "replace", "materialized",
                "temp", "temporary", "unlogged", "or"):
            j = i + 1
            while j < hi and toks[j][0] == "id" and toks[j][1].lower() in (
                    "if", "not", "exists"):
                j += 1
            i, got = _rel_list(toks, j, hi, ctes, single=True, fn_call=False,
                               role="w")
            out |= got
            continue
        i += 1
    return out


def sql_rel_roles(sql):
    """{(lowercased relation name, `'r'` | `'w'`)} — every GRAMMAR RELATION POSITION.

    CTE names are excluded — they are bound by the statement, not held by the store.

    ⚑ A NAME MAY CARRY BOTH ROLES, and collapsing that is a defect rather than a
    tidy-up: `INSERT INTO dec_val … SELECT … WHERE NOT EXISTS (SELECT 1 FROM
    dec_val …)` is the self-terminating rung idiom, and it genuinely reads what it
    writes. Returning pairs keeps the two facts; returning two disjoint sets would
    force a choice the SQL does not make.
    """
    toks = _rel_tokens(sql)
    n = len(toks)
    ctes = set()
    # ⚑ `X AS (` IS THE CTE SIGNATURE, and `X (cols) AS (` its column-listed form.
    # Nothing else in this grammar puts `AS` immediately before an open paren, so the
    # detection needs no notion of where the WITH clause ends — which is the part a
    # positional lexer would get wrong on a nested CTE.
    for i in range(n):
        if toks[i][0] != "id" or toks[i][1].lower() != "as":
            continue
        if i + 1 >= n or toks[i + 1][1] != "(":
            continue
        j = i - 1
        if j >= 0 and toks[j][1] == ")":
            d = 0
            while j >= 0:
                if toks[j][1] == ")":
                    d += 1
                elif toks[j][1] == "(":
                    d -= 1
                    if d == 0:
                        break
                j -= 1
            j -= 1
        if j >= 0 and toks[j][0] in ("id", "qid"):
            ctes.add(_rel_ident(toks[j][1]).lower())
    return {(r, k) for r, k in _rel_walk(toks, 0, n, ctes, True) if r not in ctes}


def sql_relnames(sql):
    """{lowercased relation names `sql` references in a GRAMMAR RELATION POSITION}.

    ⚑ A PROJECTION OF `sql_rel_roles`, NOT A SECOND WALK. This was the whole body
    until the read/write split landed; keeping it as a re-implementation would be the
    two-spellings-of-one-question shape this file's own `--relname` note argues
    against, and the two could then disagree about what a statement touches.
    """
    return {r for r, _k in sql_rel_roles(sql)}


def sql_kind(sql):
    """The statement's TOP-LEVEL DML/DDL head — `'delete'`, `'insert'`, `'select'`, ….

    ⚑⚑ DEPTH-AWARE, BECAUSE THE FIRST KEYWORD IS NOT THE HEAD. This repo's rungs are
    written `WITH r AS (SELECT …) INSERT INTO dec_root … SELECT …` — three heads in
    one string, of which only the last-but-one is the statement's. Reading the first
    token types the ladder's header BUILD as a `select` and takes it out of the ⒣
    population entirely; reading the first DML keyword types it as a `select` for the
    same reason. Parenthesis depth is what separates a CTE body and a column list
    from the statement, and this walker already computes it.

    ⚑ IT IS HERE AND NOT IN THE GATE because the artifact is SQL-inside-Python and
    this file owns it — `struct-tools`: *"a MODE first, a new TOOL only for a new
    artifact kind"*. A consumer-local `sql.split()[0]` would be the second reader of
    a grammar that already has one.
    """
    d = 0
    for k, t in _rel_tokens(sql):
        if t == "(":
            d += 1
        elif t == ")":
            d -= 1
        elif d == 0 and k == "id" and t.lower() in (
                "delete", "insert", "update", "replace", "merge",
                "create", "drop", "alter", "truncate", "select", "values"):
            return t.lower()
    return ""


def sql_rw(sql):
    """`(writes, reads)` — the relations `sql` WRITES and the relations it READS.

    ⚑⚑ THIS IS THE ⒣ READ-SET PRIMITIVE. *"For each tier, its retire predicate's read
    set must contain nothing at or below the tier it writes"*
    ([[deadlock-breakdown-before-any-fix]]) is a question about two sets, and until
    this mode the tool could only produce their UNION. A union cannot state the
    property at all: the retire rung's own DELETE target is in it, so every retire
    reads like a same-tier violation of itself.

    ⚑ THE SETS OVERLAP WHEN THE SQL DOES. `writes & reads` is not an error to
    normalise away — for a retire predicate it is precisely the violation.
    """
    rr = sql_rel_roles(sql)
    return ({r for r, k in rr if k == "w"}, {r for r, k in rr if k == "r"})


def relname_sites(name, path):
    """[(role, style, head, line, text)] — `name` used AS A RELATION in `path`.

    role='sql'   a SQL literal referencing it in a relation position
    role='name'  a string literal EXACTLY equal to it (the `_T("node", …)` shim
                 spelling, `relations()` roster entries, `QB.run` targets)
    """
    # ⚑ DEFERRED, NOT MODULE-SCOPE: `_pycodemod_query` and this module are SIBLING
    # seams under one entry point, and a module-scope edge between them would make the
    # import order load-bearing for no gain — the call is once per file, not per node.
    from _pycodemod_query import literal_sites
    low = name.lower()
    out = [("sql", style, head, line, sql)
           for style, head, line, sql in sql_sites("", path)
           if low in sql_relnames(sql)]
    for _p, line, role, ctx, val in literal_sites(name, [path]):
        if val == name:
            out.append(("name", role, ctx, line, val))
    return sorted(out, key=lambda r: (r[3], r[0]))


# ⚑ THE REMEDY HINTS ONLY — POSTGRES ITSELF DECIDES WHAT IS BROKEN (user, 2026-08-06:
# *"can't you ask pgsql to EXPLAIN the query string and catch if it complains?"*).
#
# My first cut was a hand-maintained PATTERN LIST that classified SQL by regex. That is a
# frozen roster: it knows only the sqlite-isms I personally hit during the port, so
# anything else passes the census silently and fails at ingest. MEASURED the moment the
# engine was asked instead — `LIKELIHOOD(1, 0.5)` came back `no-func`, a sqlite-only
# function no pattern here would ever have listed.
#
# So the VERDICT comes from `EXPLAIN` (below) and this table supplies only the human
# remedy for a recognised shape. An unrecognised failure is still REPORTED, with the
# engine's own message — the list can be incomplete without the census being wrong.
# ⚑ ORDER IS SPECIFIC-FIRST, AND FIRST-MATCH-WINS IS WHY. `INSERT OR IGNORE INTO terms
# VALUES (?,?)` carries TWO blockers — the `OR IGNORE` clause and the `?` paramstyle —
# and `_schema.upsert()` fixes both, while `_schema.ph()` fixes only the second and
# leaves a statement postgres still rejects. Listing `?` first (as I did) therefore named
# the WEAKER remedy for nine sites: technically true, and it would have sent a reader to
# patch placeholders inside a statement that needs replacing wholesale.
_PORT_REMEDY = [
    # whole-statement replacements first: they subsume the token-level ones
    (r"\bINSERT\s+OR\s+(?:IGNORE|REPLACE)\b", "use _schema.upsert()"),
    (r"\bsqlite_master\b", "use _schema.relations()"),
    (r"\bPRAGMA\b", "sqlite-only: guard, or drop"),
    (r"\browid\b", "use _schema.dedup() / a real key"),
    (r"\bGROUP_CONCAT\b", "postgres: string_agg(x, '.')"),
    # token-level last — only reached when nothing above claims the statement
    (r"(?<![%\w])\?", "use _schema.ph()"),
]


def _core_func_sites(path):
    """[(line, name)] — SQLAlchemy `func.<name>(...)` calls in one file, the SQL this census
    CANNOT judge.

    ⚑ DELIBERATELY A LOCAL, NARROW READER AND NOT AN IMPORT OF `_pycodemod_query.funcnames`.
    That function is the full census (corpus walk, generic-vs-verbatim grading, its own skip
    accounting); all that is wanted here is *does this file build SQL a literal census cannot
    see*, per file, cheaply. Importing it would add a `_pycodemod_sql -> _pycodemod_query`
    edge for a one-line question, and this module currently imports neither of its siblings.
    ⚑ The GRADING deliberately does NOT live here — a second opinion on which names are
    dialect-specific is exactly the `agda_files()`-as-four-bodies defect. This says "there is
    Core-built SQL here, go ask `--funcnames`"; it does not judge it.
    """
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except Exception:                                   # noqa: BLE001
        return []
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                and f.value.id == "func"):
            out.append((node.lineno, f.attr))
    return sorted(set(out))


def portable_sites(path):
    """[(line, blocker, remedy, snippet)] — SQL literals that are NOT backend-portable.

    ⚑ WHY A CENSUS AND NOT A CODEMOD (user, 2026-08-06: *"I'd rather fix the codemod's
    flag reporting and use it as a census"*). I wrote a libcst codemod to route ~101
    `con.execute` sites through the portable helper, dry-ran it, and STOPPED: the diff
    rewrites the CALL and leaves the SQL, so it would have produced 101 sites that LOOK
    migrated while `PRAGMA`, `INSERT OR IGNORE`, `?` and `GROUP_CONCAT` still fail on
    postgres — a large diff that reads as done and buries the real work.

    ⚑ AND THE CODEMOD COULD NOT EVEN REPORT ITS OWN RESIDUE. `libcst.tool` runs each file
    in a WORKER PROCESS, so flags accumulated on the command instance never reach the
    parent; the one part designed to surface what was left was inert. A census belongs in
    a single-process reader — this tool — not in a transform harness.

    ⚑ IT REUSES `sql_sites`' PARSER. What counts as SQL is already settled there
    (`sqlite3.complete_statement`, or a fragment whose head is a DML/DDL keyword), and
    re-deriving that would be a second, differently-wrong definition of "is this SQL".

    ⚑ AND THE VERDICT COMES FROM POSTGRES, VIA `EXPLAIN`. `EXPLAIN <stmt>` parses and
    PLANS without executing, so the engine — not a pattern list — decides what it
    rejects. MEASURED (2026-08-06) against the live tenant:

        sqlite paramstyle `?`   → SyntaxError       "syntax error at end of input"
        INSERT OR IGNORE        → SyntaxError       "syntax error at or near \"OR\""
        PRAGMA …                → SyntaxError       "syntax error at or near \"PRAGMA\""
        GROUP_CONCAT(…)         → UndefinedFunction "function group_concat… does not exist"
        rowid                   → UndefinedColumn   "column \"rowid\" does not exist"
        LIKELIHOOD(1, 0.5)      → UndefinedFunction ← no pattern list would have had this

    ⚑ `UndefinedTable` IS EXCLUDED, AND THAT IS THE LOAD-BEARING DISTINCTION. The store
    is empty of the orbit/argperm tiers, so a query against a table we have not created
    yet raises `UndefinedTable` — a fact about the STORE, not a defect in the SQL.
    Counting those would flag the entire schema as unportable. ⚑ The cost is real and
    stated: `sqlite_master` ALSO reports `UndefinedTable`, so it is invisible to this
    verdict — which is exactly why `_PORT_REMEDY` still carries a pattern for it, and why
    the two instruments are complementary rather than one replacing the other.

    ⚑ EVERY STATEMENT RUNS IN ITS OWN SAVEPOINT. A postgres error aborts the whole
    transaction; without `con.transaction()` per probe the first rejection would poison
    the connection and every later site would report `InFailedSqlTransaction` instead of
    its own verdict. Verified: the connection survives all nine probe shapes.

    Falls back to the pattern list when postgres is unreachable, so the census still runs
    (degraded, and it SAYS so) on a machine with no store.
    """
    # ⚑ A GENERATED CACHE IS NOT A PORT DEFECT, and censusing one inflates the worklist
    # with work nobody should do. `query_sql.py` is EMITTED by `query_defs.py --compile`
    # and contributed 21 of 85 sites — a quarter of the census — all of them `:named`
    # params that are CORRECT for the compiled runtime. Editing that file is explicitly
    # forbidden by its own header; the fix for anything wrong in it is to recompile.
    #
    # ⚑ DISCOVERED FROM THE FILE, NOT A FILENAME LIST. Keying on `query_sql.py` would be
    # a frozen roster that misses the next generated artifact — and this repo already
    # emits a per-backend one (`query_sql_postgres.py`) that appeared THIS session.
    # The `GENERATED by` marker is what the generators actually write.
    # ⚑ RESET FIRST, BEFORE ANY EARLY RETURN. A per-call attribute that is only ASSIGNED on
    # the happy path keeps the PREVIOUS file's value on every early exit, so a caller looping
    # over files would attribute one file's Core sites to another — the stale-context defect
    # `_report_skipped(where=…)` exists to prevent, at per-file granularity.
    portable_sites.core_built = []
    try:
        head_txt = open(path, encoding="utf-8").read(400)
    except OSError:
        head_txt = ""
    if re.search(r"^#\s*GENERATED\b", head_txt, re.M):
        return []

    # ⚑⚑ WHAT THIS CENSUS STRUCTURALLY CANNOT SEE, RECORDED BEFORE THE EARLY RETURN.
    # The population is SQL LITERALS (`sql_sites`); a SQLAlchemy Core statement is never a
    # string, so a `func.<name>` call is invisible here. MEASURED: this mode reported
    # `0 blocking site(s)` on `jea/metalanguage/autocorr_synth.py` while that file raised
    # `UndefinedFunction: function group_concat(text) does not exist` on EVERY invocation —
    # a whole capability dark, and the gate green over it.
    #
    # ⚑ THE FIX IS NOT TO WIDEN THE PREDICATE. `EXPLAIN` needs a statement; recovering one
    # from a Core expression means building it, which needs the caller's tables and binds —
    # a different instrument, and `--funcnames` is it. What belongs HERE is the honest
    # boundary: this verdict is about literals, and a file whose SQL is Core-built has not
    # been judged. Set before the `not rows` return, because a file with ONLY Core
    # statements is exactly the case that would otherwise read as a confident empty.
    portable_sites.core_built = _core_func_sites(path)

    rows = [(line, snippet) for style, head, line, snippet in sql_sites("", path)
            if style not in ("<unreadable>", "<syntax-error>")]
    if not rows:
        return []

    def _remedy(snippet):
        for rx, rem in _PORT_REMEDY:
            if re.search(rx, snippet, re.I):
                return rem
        return "(no known remedy — read the engine's message)"

    con = _pg_probe_con()
    if con is None:                      # degraded: pattern-only, and the caller says so
        out = []
        for line, snippet in rows:
            for rx, rem in _PORT_REMEDY:
                if re.search(rx, snippet, re.I):
                    out.append((line, "pattern", rem, snippet))
                    break
        return out

    import psycopg
    out = []
    for line, snippet in rows:
        head = snippet.strip().split(None, 1)[0].upper() if snippet.strip() else ""
        # ⚑ DDL IS EXECUTED IN THE SANDBOX TENANT, not EXPLAINed and not skipped.
        # `EXPLAIN` accepts only DML — measured: `EXPLAIN CREATE TABLE IF NOT EXISTS
        # path_text (…)` → "syntax error at or near TEXT", the PREFIX being the error, so
        # every CREATE/DROP read as a port defect while being valid postgres.
        #
        # ⚑ AND I BRIEFLY CONCLUDED DDL COULD NOT BE JUDGED AT ALL, because executing it
        # inside `con.transaction()` does not roll back (that manager COMMITS on success —
        # a probe created `_probe_ddl` in the REAL store and it persisted). That was a
        # property of WHICH DATABASE I pointed at, read as a property of the technique
        # (user: *"You can enroll another tenant, this one as a sandbox"*). With a
        # throwaway tenant the technique is fine: run it, and the only thing harmed is a
        # database that exists to be harmed.
        if head in ("CREATE", "DROP", "ALTER", "VACUUM", "ATTACH", "PRAGMA"):
            sb = _pg_sandbox_con()
            if sb is None:                       # no sandbox → pattern-only, and say so
                for rx, rem in _PORT_REMEDY:
                    if re.search(rx, snippet, re.I):
                        out.append((line, "pattern/ddl", rem, snippet))
                        break
                continue
            # ⚑ EACH DDL STATEMENT IS JUDGED IN ISOLATION, and the reason is that the
            # census was CONTAMINATING ITSELF. `catalog_db.py` contains two
            # `CREATE TABLE core_fp` statements; validating the first CREATED the table,
            # so the second came back `DuplicateTable` — reported as a port defect when
            # it is perfectly portable SQL that merely ran second. A per-run sandbox
            # reset does not fix this: the collision is WITHIN one run, between two
            # sites in one file.
            #
            # `DuplicateTable` and `DuplicateObject` are therefore SUCCESS: postgres
            # parsed and planned the statement well enough to know the object already
            # exists, which is exactly what "portable" means here. Dropping the object
            # first would be the alternative, and it is worse — it makes the verdict
            # depend on statement ORDER within a file.
            try:
                sb.cursor().execute(snippet)
                continue                          # postgres accepted the DDL: portable
            except (psycopg.errors.UndefinedTable,
                    psycopg.errors.DuplicateTable,
                    psycopg.errors.DuplicateObject):
                continue                          # parsed fine; the object's existence
                                                  # is a fact about the SANDBOX, not SQL
            except Exception as e:
                kind = type(e).__name__.replace("Error", "")
                out.append((line, kind, _remedy(snippet), snippet))
                continue
        try:
            with con.transaction():
                con.cursor().execute("EXPLAIN " + snippet)
            continue                                     # postgres planned it: portable
        except psycopg.errors.UndefinedTable:
            continue                                     # a fact about the STORE, not the SQL
        except Exception as e:
            kind = type(e).__name__.replace("Error", "")
            out.append((line, kind, _remedy(snippet), snippet))
    return out


_PG_CON = None
_PG_TRIED = False
_PG_SANDBOX = None
_PG_SANDBOX_TRIED = False
#: WHY the sandbox probe is absent, when it is — see `pg_probe_status`. `None` means
#: either "connected" or "not yet attempted"; the two are told apart by the connection.
_PG_SANDBOX_ERR = None


def _pg_sandbox_con():
    """The THROWAWAY tenant, for DDL that must be EXECUTED to be validated.

    ⚑ IT IS NOW THE ONLY STORE THIS MODULE OPENS. `_pg_probe_con` used to hold a second,
    LIVE, read-WRITE handle for `EXPLAIN`; the old note here read *"Sharing a connection
    would put the live store one code path away from a CREATE TABLE issued by a census"* —
    which described a hazard that had already landed, since that live handle was proven
    able to CREATE TABLE (see `_pg_probe_con`). Both probes are throwaway-tenant now, so
    there is no live path to keep separate.

    ⚑⚑ THE FAILURE IS RECORDED, NOT SWALLOWED. This returned `None` on any exception, so
    *no store reachable* and *connected fine* produced the SAME reading from outside —
    every verdict about this probe was unfalsifiable (`sql-F4`: a zero needs a positive
    control; `gate-F1`: vacuous green). The exception is still non-fatal — a census must
    degrade to pattern-only on a machine with no store — but it now leaves a WITNESS that
    a caller can read and print, so "unreachable" is a stated fact with a cause attached
    rather than an absence.
    """
    global _PG_SANDBOX, _PG_SANDBOX_TRIED, _PG_SANDBOX_ERR
    if _PG_SANDBOX_TRIED:
        return _PG_SANDBOX
    _PG_SANDBOX_TRIED = True
    try:
        sys.path.insert(0, os.path.join(_c.ROOT, "jea", "metalanguage"))
        import store as _store
        _PG_SANDBOX = _store.sandbox_connect()
        _PG_SANDBOX_ERR = None
    except Exception as e:
        _PG_SANDBOX = None
        _PG_SANDBOX_ERR = f"{type(e).__name__}: {e}"
    return _PG_SANDBOX


def pg_probe_status():
    """Why there is (or is not) a probe connection — the positive control.

    Returns (con_or_None, reason). `reason` is "" when connected, otherwise the
    exception that prevented it, so a SKIP line can name its cause instead of asserting
    an unexplained absence. ⚑ IT FORCES THE ATTEMPT: asking the status IS the probe, so
    a caller cannot read "unreachable" off a connection nobody tried to open.
    """
    con = _pg_sandbox_con()
    return con, ("" if con is not None else (_PG_SANDBOX_ERR or "not attempted"))


def _pg_probe_con():
    """A postgres connection for EXPLAIN probing, or None if unreachable.

    ⚑ ONE CONNECTION FOR THE WHOLE CENSUS, cached. Opening one per file would be ~750
    socket handshakes; opening one per STATEMENT would be thousands.

    ⚑⚑⚑ THE ORACLE IS POSTGRES' PARSER, AND A PARSER IS NOT A TENANT. This opened
    `connect(mode="rw", back="postgres")` — a LIVE READ-WRITE connection to the main
    store — reached from `_selftest`, which the pre-commit roster runs. It never called
    `store.tenant`, so it never consulted argv: it was the one store the tenant contract
    could not bind (`gate-F29`), and a `selftest-tenant: sandbox` pragma at the call site
    would have been a FALSE declaration, since appending `--sandbox` changed nothing here.

    ⚑⚑ `mode="rw"` WAS NOT A WRITE INTENT — IT WAS A COPY-PASTE THAT GRANTED WRITE
    ACCESS, and the docstring two functions up asserted the opposite: *"That one runs
    `EXPLAIN`, which cannot mutate."* True of `EXPLAIN`; false of the CONNECTION.
    MEASURED 2026-08-24 (⟡live-store-in-precommit), all three arms against the same six
    dialect cases:
      * live/rw  — every case identical, and `CREATE TABLE _witness_rw_probe` SUCCEEDED.
      * live/ro  — every case identical; the same CREATE refused, `ReadOnlySqlTransaction`.
      * sandbox  — every case identical, and no live store touched at all.
    Three arms, one grammar verdict: the live store contributed NOTHING the sandbox did
    not, because both run the same parser. The probe's schema-absence arms
    (`UndefinedTable`/`does not exist` == parsed) mean it never wanted the live SCHEMA
    either — a table it cannot find is already a success for it.

    ⚑ SO IT IS THE SANDBOX HANDLE, NOT A SECOND CONNECTION. `_pg_sandbox_con` split from
    this specifically to keep DDL off the live store; with the live arm gone the
    justification for two handles goes with it, and sharing one means there is no longer
    a code path from a census to the main store to keep separate. The separation the old
    note defended has been achieved by DELETING the dangerous half, not by guarding it.
    """
    return _pg_sandbox_con()


def rawread_sites(path):
    """[(line, kind, snippet)] — reads that CONSUME rows without normalising them.

    ⚑ THE DEFECT CLASS `--portable` CANNOT SEE, and it cost five ingest rounds. A
    psycopg cursor with `dict_row` yields DICTS; iterating a dict yields its KEYS. So
    `for a, b, c in con.execute(...)` unpacks COLUMN NAMES under postgres — silently,
    with no exception and a plausible-looking row count upstream.

    MEASURED, three separate sites of the same bug:
      * `query_builders.run` — every NAMED query; `obs_all` gave 18,334 rows and a
        1-entry dict keyed `('core_id','local_id')`
      * `sppf_db:524` — the unit loop; 419 rows in, 0 units out, while `_node` and
        `node_child` projected correctly
      * and the reason each hid: the projection HALF-BUILT and exited 0.

    ⚑ `--portable` IS BLIND TO IT BY CONSTRUCTION: the SQL is valid, the connection
    carries the right backend, the query returns rows. What is wrong is the SHAPE of a
    row at the consumer — a fact about the CALL SITE, not the statement. Three different
    censuses were green while the ingest produced an empty unit tier.

    Flags a `con.execute`/`.executemany` whose result is ITERATED, UNPACKED, or fed to a
    comprehension — i.e. where row shape matters. A bare `con.execute("DELETE …")` is
    not a hit: nothing reads its rows.
    """
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src, filename=str(path))
    except (OSError, SyntaxError):
        return []

    def _is_conn_execute(node):
        return (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("execute", "executemany")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in ("con", "conn", "c", "connection"))

    out = []
    for node in ast.walk(tree):
        # `for <targets> in con.execute(...)` — the unpacking shape
        if isinstance(node, (ast.For, ast.AsyncFor)) and _is_conn_execute(node.iter):
            kind = ("unpacked" if isinstance(node.target, (ast.Tuple, ast.List))
                    else "iterated")
            out.append((node.iter.lineno, kind, ast.unparse(node.iter)[:70]))
        # a comprehension over it
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp,
                               ast.GeneratorExp)):
            for gen in node.generators:
                if _is_conn_execute(gen.iter):
                    out.append((gen.iter.lineno, "comprehension",
                                ast.unparse(gen.iter)[:70]))
        # `x = list(con.execute(...))` / `sorted(...)` — materialised, shape still matters
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id in ("list", "sorted", "set", "dict", "tuple")
              and node.args and _is_conn_execute(node.args[0])):
            out.append((node.lineno, f"{node.func.id}()",
                        ast.unparse(node.args[0])[:70]))
    return out


# ── the ROW-PROVENANCE layer, shared ─────────────────────────────────────────────
# ⚑ THESE WERE CLOSURES INSIDE `relalg_sites` AND ARE NOW MODULE-LEVEL, because a
# SECOND mode needed exactly the same question answered.  `--control` (the
# control-flow census, `_pycodemod_control.py`) must know whether a loop iterates
# ROWS or a filesystem glob, which is the identical "did this value come out of the
# store" predicate.  Copying it would have re-derived `agda_files()`-as-four-bodies
# one level up — the defect this whole tool exists to stop, and the one its own
# docstring opens with.  `relalg_sites` now delegates; its ⚑ blocks travelled here
# with the code they explain, so nothing about WHY each hop exists was dropped.
STORE_READERS = ("execute", "executemany", "run", "rows", "fetchall", "fetchone",
                 "scalar", "scalars")
STORE_CONNS = ("con", "conn", "c", "connection", "cur", "cursor", "db", "QB",
               "_schema")


def is_store_read(node):
    """A call that pulls rows out of the store."""
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if isinstance(f, ast.Attribute) and f.attr in STORE_READERS:
        base = f.value
        if isinstance(base, ast.Name) and base.id in STORE_CONNS:
            return True
        # `QB.run(con, "name")` / `_schema.rows(con, ...)` / chained `.execute(...).fetchall()`
        if isinstance(base, ast.Call) or isinstance(base, ast.Attribute):
            return True
    return False


# ⚑ NAMES OF STORE-READING FUNCTIONS IN THIS MODULE, so a row set that arrives
# via a HELPER counts as rows. Without this the highest-volume site in the
# corpus is invisible: `reconstruct.reflects_edge` does `edge_from_obs(...) -
# edge_stored(...)` — a 6.27M-row EXCEPT — and both operands are plain calls,
# so a predicate keyed on direct `con.execute` sees a function that merely
# subtracts two locals. The defect is one hop from the cursor, which is
# exactly where a per-call-site reader stops looking.
def store_reader_fns(tree):
    """Names of store-reading functions DEFINED in this module."""
    out = set()
    for f in ast.walk(tree):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(is_store_read(n) for n in ast.walk(f)):
                out.add(f.name)
    return out


# ── `--snapshots` — ONE VALUE BUILT FROM SEVERAL WORLD-STATES ───────────────────────
#
# ⚑⚑ BUILT BECAUSE THE QUESTION HAD NO MODE AND THE ANSWER WAS A LIVE DEFECT (user,
# 2026-08-12: *"No; don't do a live query while preparing a query…"*). `sppf_db.project_sppf`
# returned `(scalar("… _node"), scalar("… _unit"), scalar("… shared_subtree"), scalar("MAX…"))`
# — four executions, so `_node` was counted at one moment and `_unit` at another, and the
# tuple reported a store state THAT NEVER EXISTED. It is this arc's core defect at its
# smallest scale: the same shape as `pin_persistent → lwm() → floor → DELETE`, six
# world-states composed into one decision.
#
# ⚑ AND `--calls scalar` CANNOT ANSWER IT. That mode reports `file:line` with no enclosing
# scope, so "two reads in ONE function" is not expressible; `--rawreads` asks a different
# question entirely (does a row's SHAPE survive the driver). Reading `--calls` output and
# grouping by eye is precisely the judgement the standing rule says belongs in a program.
#
# ⚑⚑ TWO KINDS, AND THE DISTINCTION IS THE WHOLE VALUE — because "N reads in one function"
# is NOT a defect on its own. A loop reading once per core is correct and common.
#
#   composed    ≥2 store reads inside ONE expression — a single value assembled from
#               several round trips. This IS the defect: the reads cannot be concurrent, so
#               the value is a composite of distinct instants. Structurally decidable.
#   sequential  ≥2 store reads in one function, in different statements. A SIGNAL, not a
#               verdict: it is the defect when a later read's result is combined with an
#               earlier one, and it is fine when each stands alone. Reported separately and
#               NEVER counted in the headline, because collapsing the two would report
#               correct code as broken — the over-report that makes a census unusable.
def _read_trips(node):
    """Store ROUND TRIPS in `node` — not store-read CALL NODES, which is not the same count.

    ⚑⚑ THE FIRST CUT COUNTED NODES AND THE FIRST RUN WAS MOSTLY FALSE POSITIVES — 32
    "composed" sites of which the majority were `con.execute(sql).fetchall()`, ONE round trip
    spelled with two calls, because `execute` and `fetchall` are both in `STORE_READERS`. A
    census of a defect that flags the correct spelling of it is worse than none: it trains the
    reader to skim, which is the state the defect was already hiding in.

    Two structural corrections, each measured against the corpus rather than reasoned:

      * a CHAINED accessor is the same trip. `x.execute(…).fetchone()` /
        `QB.run(…).fetchall()` — the receiver IS the read, so the outer call transports rows
        already fetched. Detected by the receiver being a store-read Call, not by a name list.
      * an `IfExp` runs ONE branch. `cur.execute(sql, params) if params else cur.execute(sql)`
        is `schema_rows.execute`'s own body and is a single trip under either binding, so the
        branches are MAXed rather than summed.
    """
    if isinstance(node, ast.IfExp):
        return (_read_trips(node.test)
                + max(_read_trips(node.body), _read_trips(node.orelse)))
    n = 0
    if is_store_read(node):
        f = node.func
        chained = isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call) \
            and is_store_read(f.value)
        n = 0 if chained else 1
    return n + sum(_read_trips(ch) for ch in ast.iter_child_nodes(node))


def _iterated_read(expr):
    """A store read inside a COMPREHENSION — one call site, N executions, one value.

    ⚑ THE CASE `_read_trips` CANNOT SEE, and it is a real instance rather than a
    hypothetical: `query_defs._population` is
    `{t: con.execute('SELECT count(*) FROM %s' % t).fetchone() for t in ('obs','obs_node',
    'edge')}` — ONE syntactic read, THREE executions, three instants, collected into one dict
    that is then printed as a single store state. Counting nodes reports 1 and counting
    executions is undecidable in general, so this is reported as its own KIND rather than
    folded into a number that would be wrong either way.
    """
    for node in ast.walk(expr):
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            body = [node.elt] if hasattr(node, "elt") else [node.key, node.value]
            if any(_read_trips(b) for b in body):
                return True
    return False


def snapshot_sites(path):
    """[(kind, fn, line, n, snippet)] — values composed across several store reads."""
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=str(path))
    except (OSError, SyntaxError):
        return []
    owner = {}

    def _walk(node, fn):
        for ch in ast.iter_child_nodes(node):
            nxt = ch.name if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
            owner[id(ch)] = nxt
            _walk(ch, nxt)
    owner[id(tree)] = "<module>"
    _walk(tree, "<module>")

    out, seen_fn = [], {}
    for node in ast.walk(tree):
        # the EXPRESSION of a simple statement, or a branch test: one evaluation point.
        exprs = []
        if isinstance(node, (ast.Return, ast.Assign, ast.AugAssign, ast.AnnAssign,
                             ast.Expr)) and getattr(node, "value", None) is not None:
            exprs = [node.value]
        elif isinstance(node, (ast.If, ast.While)):
            exprs = [node.test]
        for e in exprs:
            n = _read_trips(e)
            snip = ast.unparse(e).replace("\n", " ")[:88]
            if n >= 2:
                out.append(("composed", owner.get(id(node), "<module>"),
                            node.lineno, n, snip))
            elif n and _iterated_read(e):
                out.append(("iterated", owner.get(id(node), "<module>"),
                            node.lineno, n, snip))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # ⚑ DIRECT READS ONLY — a read inside a NESTED def belongs to that def, not to
            # this one, and attributing it upward would report every module's outer scope.
            # ⚑ AND THE CHAIN COLLAPSE APPLIES HERE TOO — `_read_trips` cannot be reused
            # because it RECURSES, so calling it per walked node would count every trip once
            # per ancestor. The predicate is inlined rather than the total re-derived.
            n = 0
            for s in ast.walk(node):
                if not is_store_read(s) or owner.get(id(s), node.name) != node.name:
                    continue
                f = s.func
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call) \
                        and is_store_read(f.value):
                    continue
                n += 1
            if n >= 2:
                seen_fn[node.name] = (node.lineno, n)
    for fn, (line, n) in seen_fn.items():
        out.append(("sequential", fn, line, n, ""))
    return sorted(out, key=lambda r: (r[0], -r[3], r[2]))


def _print_snapshots(paths):
    files = py_files(*paths) if paths else py_files()
    tot = {"composed": 0, "iterated": 0, "sequential": 0}
    shown = 0
    for p in files:
        rows = snapshot_sites(p)
        if not rows:
            continue
        shown += 1
        rel = os.path.relpath(p, _c.ROOT)
        for kind, fn, line, n, snip in rows:
            tot[kind] += 1
            print(f"  {kind:<10} {n} trip(s)  {rel}:{line}  {fn}()  {snip}")
    # ⚑ THE HEADLINE IS `composed` + `iterated`, and `sequential` is printed beside it rather
    # than added to it. A total over all three would say "N snapshot defects" about a
    # population that is mostly correct loops — the collapse these kinds exist to refuse.
    print(f"snapshots: {tot['composed']} COMPOSED + {tot['iterated']} ITERATED "
          f"(one value, several world-states) · {tot['sequential']} sequential "
          f"(signal only) in {shown} of {len(files)} file(s)")
    return 0


def is_store_read2(node, rfns):
    """A direct store read OR a call to a store-reading helper in this module."""
    if is_store_read(node):
        return True
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in rfns)


def touches(node, names):
    """Does this expression mention any of `names`?"""
    return node is not None and any(isinstance(n, ast.Name) and n.id in names
                                    for n in ast.walk(node))


def has_read(node, rfns):
    """Does this expression contain a store read (direct or one hop)?"""
    return node is not None and any(is_store_read2(n, rfns) for n in ast.walk(node))


def row_names(nodes, rfns):
    """Names bound FROM a store read — the row variables whose algebra matters.

    ⚑ TAKES A NODE ITERABLE, NOT A FUNCTION, and the difference is not cosmetic.
    `--relalg` asks about a whole function and passes `ast.walk(fn)`; `--control`
    must ask about ONE SCOPE without descending into nested defs, or a module-level
    census inherits every function-local row name and reports mode-branches as
    row-branches.  A parameter that is a walk is the only spelling both can use."""
    names = set()
    for n in nodes:
        tgt = None
        if isinstance(n, ast.Assign) and has_read(n.value, rfns):
            tgt = n.targets
        elif isinstance(n, (ast.For, ast.AsyncFor)) and has_read(n.iter, rfns):
            tgt = [n.target]
        if not tgt:
            continue
        for t in tgt:
            for sub in ast.walk(t):
                if isinstance(sub, ast.Name):
                    names.add(sub.id)
    return names


def derived_names(nodes, rows):
    """Names carrying row DATA one hop on — `out.append(<row expr>)`.

    ⚑ WITHOUT THIS HOP THE MOST COMMON SHAPE IS INVISIBLE, and the selftest
    caught it: the corpus almost never sorts the row variable itself. It
    accumulates into a fresh list and sorts THAT (`out.append(...)` then
    `sorted(out)`), so a predicate keyed only on row names sees the ORDER BY
    as ordinary in-memory work. One hop is deliberate — a full dataflow
    closure would re-derive taint analysis for a census.
    """
    d = set()
    for n in nodes:
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in ("append", "add", "extend")
                and isinstance(n.func.value, ast.Name)
                and any(touches(a, rows) for a in n.args)):
            d.add(n.func.value.id)
        if isinstance(n, ast.Assign) and touches(n.value, rows):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    d.add(t.id)
    return d


RELALG_KINDS = ("join", "group-by", "filter", "sort", "set-op", "distinct")


def relalg_sites(path):
    """[(line, kind, fn, snippet)] — RELATIONAL ALGEBRA performed in Python on rows
    that came out of the store.

    ⚑ THE DEFECT THIS EXISTS TO FIND, and the store's own code already states the
    rule: `schema.lifecycle_census`'s docstring says *"THE STAGES ARE COMPUTED IN
    SQL, NOT PER-ROW IN PYTHON. Pulling 506k rows to evaluate four predicates would
    be the relational-algebra-withheld-from-the-engine defect this store exists to
    stop."* It was then committed again in `schema.reclaim` (select ids → Python
    loop → one DELETE per element). A rule stated in a docstring governs the reader
    who is already looking at that docstring; a mode governs the corpus.

    ⚑ WHY THIS IS NOT `--rawreads` DEEPER. `--rawreads` asks whether a row's SHAPE
    survives the driver — a question about ONE call site, answered at the cursor.
    This asks what ALGEBRA happens to the rows AFTER they land, which is a question
    about the enclosing function: a broad `select()` whose result feeds a dict-build
    plus a second `select()` correlated against that dict is a JOIN, and neither
    statement is individually wrong. So the unit here is the FUNCTION, not the call.

    The six kinds, each an operator the engine owns:
      join      — rows keyed into a dict, then a second row-source looked up in it
      group-by  — per-key accumulation (`d[k] = d.get(k,0)+1`, `setdefault(k,[]).append`,
                  Counter/defaultdict update) over query rows
      filter    — `if <pred>: continue` / a comprehension `if` over query rows (a WHERE)
      sort      — `sorted(...)` / `.sort()` on query rows (an ORDER BY)
      set-op    — `set(a) - set(b)` / `&` / `|` between two row-sources (EXCEPT/INTERSECT/UNION)
      distinct  — `set()` built purely to dedupe query rows (a DISTINCT)

    A hit is reported only inside a function that ALSO reads the store, so pure
    in-memory helpers are not swept in. That gate is what keeps this from flagging
    every `sorted()` in the corpus.

    ⚑ THE MODE FINDS SITES; IT DOES NOT JUDGE EXPRESSIBILITY — and the first audit
    to use it got that judgement wrong twice, in the same function, both times by
    reasoning about the Python instead of probing postgres.

      * `sppf_db.project_sppf`'s `pack()` was called "a memoized bottom-up hash …
        genuinely awkward as a CTE". It is not a fold: the child term at
        `sppf_db.py:894` is `sym[obs[(c,cl)]]` — the child's HEAD symbol, depth-1,
        already computed in the loop above. `pack()` NEVER CALLS ITSELF. The memo
        caches a lookup, not a recursion, and the shape is
        `string_agg(child_sym, ',' ORDER BY ord)` over one join.
      * The verdict was reached against an EMPTY TABLE. `obs_node(core_id,
        local_id, node_id)` IS that packing map, persisted earlier from the very
        dict in question; on any run after the first it is a stored relation, not
        a computation. A census reads the store's CURRENT contents — an empty tier
        means UNMEASURED, never "must be recomputed in Python".

    ⚑ SO A "NOT EXPRESSIBLE" VERDICT NEEDS `schema.py --probe`, NOT AN ARGUMENT.
    Every construct assumed unreachable here has since been probed WORKING against
    the sandbox: base64→jsonb→`jsonb_array_elements_text … WITH ORDINALITY` for
    edge reconstruction, `EXCEPT` both ways for a 6.27M-row set difference, and a
    recursive CTE that flattens an associative rig op while `ORDER BY leaf` vs
    `ORDER BY path` selects the commutative-canonical vs positional child order —
    i.e. `project_orbit_sppf.canon_syms` (`sppf_db.py:1056`), the one function here
    that DOES genuinely recurse. The only site that truly cannot migrate fails for
    a reason no probe would fix: `catalog_db.completeness` set-differences against
    a FILESYSTEM GLOB, which is not a relation.
    """
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src, filename=str(path))
    except (OSError, SyntaxError):
        return []

    # ⚑ THE ROW-PROVENANCE PREDICATES NOW LIVE AT MODULE LEVEL (see the block above
    # `RELALG_KINDS`) BECAUSE `--control` ASKS THE SAME QUESTION.  These bindings keep
    # the body below spelled exactly as it was measured; the ⚑ blocks that explained
    # each hop travelled WITH the code, not away from it.
    _reader_fns = store_reader_fns(tree)

    def _is_read(node):
        return is_store_read(node)

    def _is_read2(node):
        return is_store_read2(node, _reader_fns)

    def _reads_store(fn):
        return any(_is_read2(n) for n in ast.walk(fn))

    def _row_names(fn):
        return row_names(ast.walk(fn), _reader_fns)

    def _has_read(node):
        return has_read(node, _reader_fns)

    def _derived(fn, rows):
        return derived_names(ast.walk(fn), rows)

    def _touches(node, names):
        return touches(node, names)

    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _reads_store(fn):
            continue
        rows = _row_names(fn)
        rowsd = rows | _derived(fn, rows)
        seen = set()

        def emit(line, kind, snippet):
            key = (line, kind)
            if key in seen:
                return
            seen.add(key)
            out.append((line, kind, fn.name, snippet[:78]))

        # dict-building keyed off row data → the JOIN / GROUP BY probe
        dict_targets = set()
        for n in ast.walk(fn):
            # d[k] = ...  /  d[k] = d.get(k, 0) + 1  /  d.setdefault(k, []).append(v)
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                        if _touches(t.slice, rows) or _touches(n.value, rows):
                            dict_targets.add(t.value.id)
                            agg = (isinstance(n.value, ast.BinOp)
                                   or (isinstance(n.value, ast.Call)
                                       and isinstance(n.value.func, ast.Attribute)
                                       and n.value.func.attr == "get"))
                            emit(n.lineno, "group-by" if agg else "join",
                                 ast.unparse(n))
            if isinstance(n, ast.AugAssign):
                t = n.target
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                    if _touches(t.slice, rows) or _touches(n.value, rows):
                        dict_targets.add(t.value.id)
                        emit(n.lineno, "group-by", ast.unparse(n))
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ("setdefault", "update")
                    and isinstance(n.func.value, ast.Name)
                    and _touches(n, rows)):
                dict_targets.add(n.func.value.id)
                emit(n.lineno, "group-by", ast.unparse(n))
            # Counter/defaultdict over rows
            if (isinstance(n, ast.Call) and _touches(n, rows)
                    and ((isinstance(n.func, ast.Name)
                          and n.func.id in ("Counter", "defaultdict"))
                         or (isinstance(n.func, ast.Attribute)
                             and n.func.attr in ("Counter", "defaultdict")))):
                emit(n.lineno, "group-by", ast.unparse(n))

        for n in ast.walk(fn):
            # a lookup into a row-keyed dict = the JOIN's probe side
            if (isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
                    and n.value.id in dict_targets and _touches(n.slice, rows)):
                emit(n.lineno, "join", ast.unparse(n))
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "get"
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id in dict_targets and _touches(n, rows)):
                emit(n.lineno, "join", ast.unparse(n))
            # sort = ORDER BY
            if isinstance(n, ast.Call):
                if (isinstance(n.func, ast.Name) and n.func.id == "sorted"
                        and n.args and _touches(n.args[0], rowsd | dict_targets)):
                    emit(n.lineno, "sort", ast.unparse(n))
                if (isinstance(n.func, ast.Attribute) and n.func.attr == "sort"
                        and isinstance(n.func.value, ast.Name)
                        and n.func.value.id in (rowsd | dict_targets)):
                    emit(n.lineno, "sort", ast.unparse(n))
                # DISTINCT via set() — over a row name, a row-derived name, or
                # directly over a comprehension that reads the store.
                if (isinstance(n.func, ast.Name) and n.func.id == "set" and n.args
                        and (_touches(n.args[0], rowsd) or _has_read(n.args[0]))):
                    emit(n.lineno, "distinct", ast.unparse(n))
            # set difference / intersection / union between row-derived sets
            if (isinstance(n, ast.BinOp)
                    and isinstance(n.op, (ast.Sub, ast.BitAnd, ast.BitOr))
                    and (_touches(n.left, rowsd) or _has_read(n.left))
                    and (_touches(n.right, rowsd) or _has_read(n.right))):
                emit(n.lineno, "set-op", ast.unparse(n))
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ("difference", "intersection", "union",
                                        "symmetric_difference")
                    and _touches(n, rowsd)):
                emit(n.lineno, "set-op", ast.unparse(n))
            # WHERE withheld: a guard-continue inside a loop over rows
            if isinstance(n, (ast.For, ast.AsyncFor)) and _has_read(n.iter):
                for b in n.body:
                    if (isinstance(b, ast.If) and len(b.body) == 1
                            and isinstance(b.body[0], (ast.Continue, ast.Pass))):
                        emit(b.lineno, "filter", ast.unparse(b.test))
            # comprehension `if` over a store read = a WHERE
            if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp,
                              ast.GeneratorExp)):
                for gen in n.generators:
                    if _has_read(gen.iter) and gen.ifs:
                        for cond in gen.ifs:
                            emit(gen.iter.lineno, "filter", ast.unparse(cond))
                if isinstance(n, ast.SetComp) and any(_has_read(g.iter)
                                                      for g in n.generators):
                    emit(n.lineno, "distinct", ast.unparse(n))
    return out


def _print_relalg(paths):
    """`--relalg` — relational algebra performed in Python over rows from the store."""
    files = py_files(*paths) if paths else py_files()
    total, shown, by_kind, by_fn = 0, 0, {}, {}
    for p in files:
        rows = relalg_sites(p)
        if not rows:
            continue
        shown += 1
        rel = os.path.relpath(p, _c.ROOT)
        for line, kind, fn, snippet in rows:
            total += 1
            by_kind.setdefault(kind, []).append((rel, line, fn, snippet))
            by_fn[(rel, fn)] = by_fn.get((rel, fn), 0) + 1
    # ⚑ THE FUNCTION IS THE UNIT, NOT THE LINE.  One withheld join shows up as a
    # dict-build plus N probes; ranking by line count would report the same defect
    # N+1 times and bury a single-line `set(a)-set(b)` that moves more rows.
    if by_fn:
        print("  ── by function (the migration unit) ──")
        for (rel, fn), n in sorted(by_fn.items(), key=lambda kv: -kv[1])[:25]:
            kinds = sorted({k for k, hits in by_kind.items()
                            for r, _l, f, _s in hits if (r, f) == (rel, fn)})
            print(f"    {n:>3} site(s)  {rel}::{fn}  [{','.join(kinds)}]")
    for kind in RELALG_KINDS:
        hits = by_kind.get(kind)
        if not hits:
            continue
        print(f"  {kind}  ({len(hits)} site(s)) → the engine owns this operator")
        for rel, line, fn, snippet in sorted(hits)[:10]:
            print(f"      {rel}:{line}  ({fn})  {snippet}")
        if len(hits) > 10:
            print(f"      … and {len(hits) - 10} more")
    # ⚑ `n of m`, ALWAYS — an empty result must distinguish "no algebra found" from
    # "no files searched".
    print(f"relalg: {total} withheld-algebra site(s) in {shown} of {len(files)} file(s)")
    return 0


def _print_rawreads(paths):
    """`--rawreads` — reads whose ROW SHAPE breaks on psycopg, invisible to --portable."""
    files = py_files(*paths) if paths else py_files()
    total, shown, by_kind = 0, 0, {}
    for p in files:
        rows = rawread_sites(p)
        if not rows:
            continue
        shown += 1
        rel = os.path.relpath(p, _c.ROOT)
        for line, kind, snippet in rows:
            total += 1
            by_kind.setdefault(kind, []).append((rel, line, snippet))
    for kind in sorted(by_kind, key=lambda k: -len(by_kind[k])):
        hits = by_kind[kind]
        print(f"  {kind}  ({len(hits)} site(s)) → route through _schema.rows()")
        for rel, line, snippet in sorted(hits)[:8]:
            print(f"      {rel}:{line}  {snippet}")
        if len(hits) > 8:
            print(f"      … and {len(hits) - 8} more")
    print(f"rawreads: {total} shape-unsafe read(s) in {shown} of {len(files)} file(s)")
    return 0


def _print_portable(paths):
    """`--portable` — what still blocks the postgres port, per site, with its remedy."""
    files = py_files(*paths) if paths else py_files()
    by_blocker, by_file, total, shown = {}, {}, 0, 0
    core_built = {}
    for p in files:
        rows = portable_sites(p)
        # ⚑ ACCUMULATED BEFORE THE `continue`, WHICH IS THE WHOLE POINT. A file whose SQL is
        # ENTIRELY Core-built has no literal rows, so the old loop skipped it silently and it
        # never appeared anywhere in the report — `autocorr_synth.py` was exactly that file,
        # and it was raising UndefinedFunction on every call while this printed a clean total.
        if portable_sites.core_built:
            core_built[os.path.relpath(p, _c.ROOT)] = portable_sites.core_built
        if not rows:
            continue
        shown += 1
        rel = os.path.relpath(p, _c.ROOT)
        by_file[rel] = len(rows)
        for line, blocker, remedy, snippet in rows:
            total += 1
            by_blocker.setdefault(blocker, []).append((rel, line, remedy, snippet))

    # ⚑ GROUPED BY BLOCKER, NOT BY FILE — the blocker names the TOOL that fixes it, so
    # the grouping IS the work breakdown. A per-file listing would make the reader
    # re-derive that classification for every row.
    # ⚑ GROUP BY REMEDY, NOT BY EXCEPTION CLASS. Postgres reports `INSERT OR IGNORE`,
    # `PRAGMA` and a stray `?` all as SyntaxError, so grouping on the engine's exception
    # merged three DIFFERENT jobs into one bucket — and the per-bucket display cutoff
    # then hid whole classes below a `… and N more`.
    #
    # ⚑ THAT COST ME TWO WRONG DIAGNOSES. The PRAGMA sites "vanished" from the report and
    # I concluded first that `sql_sites` never saw them (falsified by `--sql
    # journal_mode`), then that a poisoned sandbox transaction swallowed them. Neither:
    # they were in the output all along, ranked below the cutoff. *A display limit is not
    # a measurement, and reading one as a finding is how a working census gets
    # "debugged".* The remedy is the actionable key — it names the tool — so it is what
    # the grouping keys on.
    _by_remedy = {}
    for blocker, hits in by_blocker.items():
        for rel, line, remedy, snippet in hits:
            _by_remedy.setdefault((remedy, blocker), []).append((rel, line, snippet))
    for (remedy, blocker) in sorted(_by_remedy, key=lambda k: -len(_by_remedy[k])):
        hits = _by_remedy[(remedy, blocker)]
        print(f"  {remedy}  [{blocker}]  ({len(hits)} site(s))")
        for rel, line, snippet in sorted(hits)[:6]:
            print(f"      {rel}:{line}  {snippet[:64]}")
        if len(hits) > 6:
            print(f"      … and {len(hits) - 6} more")
    if by_file:
        print("  heaviest files: " + ", ".join(
            "%s=%d" % kv for kv in sorted(by_file.items(), key=lambda kv: -kv[1])[:5]))
    # ⚑ NAME THE INSTRUMENT. An engine verdict and a pattern guess are different KINDS of
    # answer, and a census that reported them identically would let a degraded run — one
    # on a machine with no postgres — read as authoritative. The pattern list is
    # incomplete BY CONSTRUCTION (it knows only the sqlite-isms already hit); the engine
    # is not. Saying which one spoke is what keeps an incomplete answer honest.
    if _pg_probe_con() is None:
        print("  ⚑ DEGRADED: postgres unreachable — verdicts are PATTERN GUESSES, not")
        print("    the engine's. A site absent here may still fail; re-run with a store.")
    else:
        print("  verdicts from postgres EXPLAIN (UndefinedTable excluded: an empty store")
        print("    is not a port defect — so `sqlite_master` is invisible to it, and is")
        print("    caught by pattern instead)")
    # ⚑⚑ NAME WHAT THE INSTRUMENT CANNOT SEE, WHICH IS THE SAME PRINCIPLE AS THE LINE ABOVE
    # ONE LAYER OUT. That one distinguishes an ENGINE verdict from a PATTERN guess; this one
    # distinguishes "judged and clean" from "not in the population at all". Both exist
    # because an incomplete answer that does not say so reads as authoritative.
    #
    # ⚑ MEASURED, AND IT IS WHY THIS IS HERE: `--portable jea/metalanguage/autocorr_synth.py`
    # printed `0 blocking site(s) in 0 of 1 file(s)` while that file raised
    # `UndefinedFunction: group_concat` on EVERY invocation. The zero was true of LITERALS
    # and read as true of the file. A gate green over a live defect is worse than no gate.
    if core_built:
        _n = sum(len(v) for v in core_built.values())
        print(f"  ⚑ NOT JUDGED HERE: {_n} SQLAlchemy Core `func.<name>` call(s) in "
              f"{len(core_built)} file(s). A Core statement is never a string, so EXPLAIN")
        print("    has nothing to parse and these are OUTSIDE this census by construction —")
        print("    not clean, UNSEEN. `pycodemod --funcnames --verbatim` is that half.")
        for rel, hits in sorted(core_built.items(), key=lambda kv: -len(kv[1]))[:5]:
            print(f"      {rel}  {', '.join(sorted({n for _l, n in hits}))[:60]}")
        if len(core_built) > 5:
            print(f"      … and {len(core_built) - 5} more file(s)")
    # ⚑ `n of m`, ALWAYS — an empty result must distinguish "everything is portable"
    # from "no files were read".
    print(f"portable: {total} blocking site(s) in {shown} of {len(files)} file(s)")
    return 0


def _print_sql(ident, paths):
    files = py_files(*paths) if paths else py_files()
    total, shown = 0, 0
    by_style = {}
    for p in files:
        rows = sql_sites(ident, p)
        if not rows:
            continue
        total += len(rows)
        shown += 1
        rel = os.path.relpath(p, _c.ROOT)
        for style, head, line, snippet in rows:
            by_style[style] = by_style.get(style, 0) + 1
            # truncate at DISPLAY time — `sql_sites` now yields the full statement so a
            # parsing consumer (`--portable`) is not handed a fragment.
            print(f"  {style:<8} {head:<8} {rel}:{line}  {snippet[:70]}")
    if by_style:
        # ⚑ THE STYLE BREAKDOWN IS THE VERDICT.  A count says "this identifier
        # appears in SQL"; the split says whether consumers reach it through the
        # compiled-builder layer or bypass it with a raw string, which is the
        # question a refactor actually asks.
        print("  styles: " + ", ".join("%s=%d" % kv
                                       for kv in sorted(by_style.items())))
    # ⚑ `n of m`, ALWAYS — the rule `_print_bindings` states verbatim.  An empty
    # result must distinguish "no SQL mentions it" from "no files searched"; the
    # missing denominator on `--key` is precisely what made this mode necessary.
    print(f"{ident}: {total} SQL site(s) in {shown} of {len(files)} file(s)")
    return 0


def _print_relname(name, paths):
    """`--relname <rel>` — every consumer of `<rel>` AS A RELATION.

    ⚑ WITH NO OPERAND IT IS A CORPUS CENSUS, and that form is the one a REMOVAL needs:
    "which relations does this corpus reference at all" is the check that a name is
    gone, and it cannot be asked by naming the name you expect to be absent. Reporting
    presence over the whole corpus distinguishes *nothing references it* from *the
    query found nothing* — the `n of m` rule applied to the relation axis.
    """
    files = py_files(*paths) if paths else py_files()
    if not name:
        census = {}
        for p in files:
            for _style, _head, _line, sql in sql_sites("", p):
                for r in sql_relnames(sql):
                    census[r] = census.get(r, 0) + 1
        for r, k in sorted(census.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {k:>5}  {r}")
        print(f"corpus: {len(census)} distinct relation(s) referenced, "
              f"{sum(census.values())} reference(s) in {len(files)} file(s)")
        return 0
    total, shown = 0, 0
    by_role = {}
    for p in files:
        rows = relname_sites(name, p)
        if not rows:
            continue
        total += len(rows)
        shown += 1
        rel = os.path.relpath(p, _c.ROOT)
        for role, a, b, line, text in rows:
            by_role[role] = by_role.get(role, 0) + 1
            print(f"  {role:<5} {a:<8} {b:<10} {rel}:{line}  {text[:64]}")
    if by_role:
        print("  roles: " + ", ".join("%s=%d" % kv for kv in sorted(by_role.items())))
    print(f"{name}: {total} relation-use site(s) in {shown} of {len(files)} file(s)")
    return 0
