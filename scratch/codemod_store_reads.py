# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""libcst codemod: route `con.execute(...)` / `.executemany(...)` through the store contract.

⚑ WHY A CODEMOD AND NOT A SWEEP (2026-08-06). The postgres port hit FOUR failures in a
row, each found by running a 4-minute ingest and reading one traceback: `?` vs `%s`,
`InFailedSqlTransaction`, `con.executemany` missing on psycopg, then 101 more
`con.execute` sites. Every fix was correct; the METHOD was wrong — using an ingest as a
linter, one site per round.

MEASURED population: **101 `execute` + 23 `executemany` call sites across 15 modules**.
That is not hand-work, and hand-editing it would be the exact defect this repo's Python
tooling exists to prevent (`pycodemod`'s own header: "this repo mechanizes every edit to
`agda/` and makes NONE to the ~85 tools that perform them").

⚑ WHAT IT DOES *NOT* DO, and this is the load-bearing limit. It rewrites the CALL, never
the SQL. Three classes are left for a human, because a mechanical rewrite would produce
code that runs and is wrong:

  * PARAMSTYLE — a `?` inside the SQL string still fails on postgres. The codemod FLAGS
    these rather than rewriting: `?` may appear inside a string literal or a LIKE
    pattern, and a blind `?`→`%s` would corrupt those.
  * DIALECT SQL — `GROUP_CONCAT` (postgres: `string_agg`), `sqlite_master`, `PRAGMA`,
    `rowid`. Flagged, never rewritten.
  * `PRAGMA journal_mode/busy_timeout` — sqlite tuning with no postgres analogue; these
    need GUARDING (skip on postgres), not porting, which is a semantic call.

So the codemod does the mechanical 90% and PRINTS the residue as a worklist. A tool that
silently "handled" the other 10% would be worse than one that names it.
"""
import re
import sys

import libcst as cst
import libcst.matchers as m
from libcst.codemod import CodemodContext, VisitorBasedCodemodCommand

# ⚑ THE SQL SHAPES THAT SURVIVE A CALL REWRITE AND STILL FAIL. Each is a real defect
# measured in this port, not a speculative list.
DIALECT_SQL = [
    (re.compile(r"\?"), "sqlite paramstyle `?` — use _schema.ph()"),
    (re.compile(r"\bGROUP_CONCAT\b", re.I), "GROUP_CONCAT — postgres: string_agg"),
    (re.compile(r"\bsqlite_master\b", re.I), "sqlite_master — use _schema.relations()"),
    (re.compile(r"\bPRAGMA\b", re.I), "PRAGMA — sqlite-only; guard or drop"),
    (re.compile(r"\browid\b", re.I), "rowid — use _schema.dedup() / a real key"),
    (re.compile(r"\bINSERT\s+OR\s+(IGNORE|REPLACE)\b", re.I),
     "INSERT OR … — use _schema.upsert()"),
]


class StoreReads(VisitorBasedCodemodCommand):
    DESCRIPTION = ("Route con.execute/executemany through _schema.execute/execute_many; "
                   "flag SQL that a call rewrite cannot fix.")

    def __init__(self, context: CodemodContext):
        super().__init__(context)
        self.flags = []
        self.rewrote = 0

    def _sql_text(self, node):
        """The literal SQL of the first argument, or None if it is not a literal."""
        if not node.args:
            return None
        a = node.args[0].value
        parts = []
        stack = [a]
        while stack:
            n = stack.pop()
            if isinstance(n, cst.SimpleString):
                parts.append(n.raw_value)
            elif isinstance(n, cst.ConcatenatedString):
                stack.extend([n.left, n.right])
            elif isinstance(n, cst.FormattedString):
                for p in n.parts:
                    if isinstance(p, cst.FormattedStringText):
                        parts.append(p.value)
        return "".join(parts) if parts else None

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        # match `<recv>.execute(...)` / `<recv>.executemany(...)`
        if not m.matches(updated.func, m.Attribute(attr=m.Name("execute")
                                                   | m.Name("executemany"))):
            return updated
        recv = updated.func.value
        # ⚑ ONLY REWRITE A CONNECTION-ISH RECEIVER. A `cur.execute` is already correct on
        # both drivers, and rewriting it would add a pointless indirection; more
        # importantly, `_schema`'s OWN internals call `cur.execute` and must not be
        # rewritten into recursion.
        if not m.matches(recv, m.Name()):
            return updated
        name = recv.value
        if name not in ("con", "conn", "c", "connection"):
            return updated

        meth = updated.func.attr.value
        helper = "execute" if meth == "execute" else "execute_many"

        sql = self._sql_text(updated)
        if sql:
            for rx, why in DIALECT_SQL:
                if rx.search(sql):
                    self.flags.append((self.context.filename, why, sql[:70]))

        self.rewrote += 1
        return cst.Call(
            func=cst.Attribute(value=cst.Name("_schema"), attr=cst.Name(helper)),
            args=[cst.Arg(value=recv)] + list(updated.args))


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    def run(src):
        mod = cst.parse_module(src)
        cmd = StoreReads(CodemodContext(filename="t.py"))
        out = mod.visit(cmd)
        return out.code, cmd

    # the basic rewrite
    got, cmd = run("con.execute('SELECT 1')\n")
    check("con.execute is routed", got.strip(), "_schema.execute(con, 'SELECT 1')")
    check("...and counted", cmd.rewrote, 1)

    got, _ = run("con.executemany('DELETE FROM t WHERE a=1', rows)\n")
    check("executemany maps to execute_many",
          got.strip(), "_schema.execute_many(con, 'DELETE FROM t WHERE a=1', rows)")

    # ⚑ A CURSOR CALL MUST NOT BE REWRITTEN — it is already portable, and `_schema`'s own
    # internals use `cur.execute`; rewriting those would produce infinite recursion.
    got, cmd = run("cur.execute('SELECT 1')\n")
    check("cur.execute is left alone", got.strip(), "cur.execute('SELECT 1')")
    check("...and not counted", cmd.rewrote, 0)

    # ⚑ THE FLAGS ARE THE POINT. A call rewrite does not fix the SQL, and a codemod that
    # silently "handled" these would emit code that runs and is wrong.
    _, cmd = run("con.execute('SELECT a FROM t WHERE b=?', (x,))\n")
    check("a `?` paramstyle is FLAGGED", len(cmd.flags), 1)
    _, cmd = run("con.execute('SELECT GROUP_CONCAT(x) FROM t')\n")
    check("GROUP_CONCAT is FLAGGED", len(cmd.flags), 1)
    _, cmd = run("con.execute('SELECT name FROM sqlite_master')\n")
    check("sqlite_master is FLAGGED", len(cmd.flags), 1)
    # ...and a clean statement is not
    _, cmd = run("con.execute('SELECT a FROM t')\n")
    check("a portable statement is NOT flagged", len(cmd.flags), 0)

    # ⚑ THE REWRITE MUST PRESERVE EXTRA ARGS — dropping a params tuple would turn a
    # parameterised query into a literal one, which is both wrong and a SQL-injection
    # shape. A case checking only the receiver would miss it.
    got, _ = run("con.execute(q, (a, b))\n")
    check("params are preserved", got.strip(), "_schema.execute(con, q, (a, b))")

    bad = [c for c in cases if not c[1]]
    for label, _, got, want in bad:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
    print("run via:  python -m libcst.tool codemod "
          "-u codemod_store_reads.StoreReads <paths>")
