# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--control` — THE CONTROL-FLOW CENSUS: every branch, loop and early exit, TYPED.

⚑ WHY THIS IS A CENSUS AND NOT A LINT.  The store's work is moving out of Python and
into the SQL engine.  User, 2026-08-12: *"almost all of the python code needs to go
away.  The work belongs in the sql engine.  Think of it like ladder logic."*  A ladder
rung has NO CONTROL FLOW — the predicate IS the `WHERE` clause, and there is no window
between reading a contact and energising a coil.  In SQL that is `INSERT INTO b SELECT
… WHERE p` and `DELETE FROM b WHERE p'`.  So **control flow in this code is the measure
of the work that has not yet moved**: every `if` is a branch the engine should be taking
as a `WHERE`/`CASE`, every loop is a set the engine should be iterating.  The census
answers *how much is left, and where* — it does not judge, refuse, or exit non-zero.

⚑ WHY IT IS NOT `--relalg` DEEPER, and this is measured, not stylistic.  `--relalg`
asks *what ALGEBRA happens to rows after they land* and gates every hit on the
enclosing function reading the store.  That gate is exactly right for its question and
exactly wrong for this one: `_pycodemod_sql.py`'s own module docstring records that
`relalg_sites` **cannot see a loop-with-early-break**, because an early `break` is an
ORDERING DEPENDENCY and those are the hardest thing to express relationally.  A mode
that cannot see the hardest class is not a partial answer to this question; it is a
confident wrong one.  So: same row-provenance predicates (shared, not copied — see
`_pycodemod_sql.store_reader_fns` and friends), different population and no store gate.

⚑ AND THE CANONICAL WITNESS FOR THAT BLIND SPOT IS ALREADY RETIRED — STATED IN THE PAST
TENSE ON PURPOSE.  `_unreflected_floor` is named repeatedly as the site `--relalg` could
not see, and a census run 2026-08-12 finds it with **0 defs and 0 calls**: it was
replaced by the relational `drainable = below_floor × projected × determined`
(`jea/metalanguage/query_decl.py:317`, and `schema.py:6` records that retiring it took
four edits).  Carrying it here in the present tense would make this docstring assert a
live defect that the tree has already paid down — the stale-claim shape, arriving
through the very file that is supposed to be the incident log.  What survives is the
CLASS, and the class is why this mode exists: 45 early exits remain in the SPPF path.

⚑ COMPLETENESS OVER PRECISION, BECAUSE THE FORMS THAT DO NOT LOOK LIKE CONTROL FLOW ARE
WHERE THIS CODE IS DENSEST.  A frozen roster of "what counts" is the same defect class
this repo records repeatedly, so the roster below is deliberately wide and every entry
is REPORTED BY CONSTRUCT — a reader who judges one class out of scope can subtract it,
which is not possible if the census silently never looked.  `--control --constructs`
prints the roster with its counts, so what was counted is always readable from the tool.

The six KINDS are the actionable axis; the construct is only the syntax:

  row-iteration  a loop over rows read from the store — a set the engine owns
  row-branch     a branch on the CONTENT of a row — a `WHERE` or a `CASE`
  mode-branch    a branch on configuration/arguments (`if additive:`, `sys.argv`) —
                 a DIFFERENT class: these do not become SQL, they select WHICH
                 statement runs, and collapsing them into the same total is what
                 makes a control-flow count read as bigger work than it is
  external       file I/O, subprocess, the clock, the `.agdai` decoder shim — the ε
                 boundary, where no rung can reach.  THE IRREDUCIBLE HALF.
  early-exit     `break` / `continue` / a `return` inside iteration — called out
                 separately BECAUSE they are ordering dependencies
  unclassified   could not be determined.  Reported as such, never guessed.

⚑ AND THE `sqlform` COLUMN IS ALLOWED TO SAY `unknown`, WHICH IS THE POINT.  A plausible
guess in that column is noise that reads like analysis; the unknowns are the finding.
The mapping is a table keyed on (construct, kind) — never on the site's text — so it
cannot quietly acquire a per-site judgement that lives in nobody's program.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pycodemod_core
import _pycodemod_core
from _pycodemod_sql import (
    derived_names, has_read, row_names, store_reader_fns, touches,
)

CONTROL_KINDS = ("external", "row-iteration", "row-branch", "early-exit",
                 "mode-branch", "unclassified")

# ── the construct roster, grouped for reporting ───────────────────────────────────
# ⚑ THE GROUPS EXIST SO A READER CAN SUBTRACT A CLASS THEY JUDGE OUT OF SCOPE.  A bare
# total invites exactly the argument this census is meant to settle ("half of those are
# just `and`"), and the only honest answer to that is a per-construct breakdown that was
# always there rather than one recomputed after the objection.
CONSTRUCT_GROUPS = {
    "branch": ("if", "elif", "else", "ternary", "match", "case"),
    "loop": ("for", "while", "for-else", "while-else", "comp-for"),
    "guard": ("comp-if",),
    "exit": ("break", "continue", "return-in-loop", "return-guard", "exit",
             "raise", "raise-in-cond", "assert"),
    "handler": ("try", "except", "finally", "try-else", "with"),
    "short-circuit": ("and", "or", "or-default", "get-default", "get-none"),
    "fold": ("any", "all", "next-default", "filter"),
    "suspend": ("yield", "yield-from"),
}
CONSTRUCTS = tuple(c for g in CONSTRUCT_GROUPS.values() for c in g)
# ⚑ THE LOOP SET IS ALSO THE "NEVER A MODE-BRANCH" SET, AND THAT IS A CORRECTION.  The
# first cut tested every construct against the parameter names, so `for x in xs` in a
# pure helper reported as `mode-branch` — iterating an argument is not branching on
# configuration, and the misfile moved sites out of `unclassified` (an honest "I could
# not tell") into a kind that reads as a decision someone made.
LOOP_CONSTRUCTS = ("for", "while", "comp-for", "for-else", "while-else",
                   "yield", "yield-from")
EARLY_EXIT_CONSTRUCTS = ("break", "continue", "return-in-loop")
# ⚑ `sys.exit` IS ε, NOT MODE, AND THIS IS THE SECOND ANSWER TO THAT QUESTION.  The
# first was "it appears under a mode-branch in every CLI, so filing it as ε inflates the
# ratio" — which optimises the number instead of reading it.  Terminating a process is
# precisely *where no rung can reach*; scoring it as work-that-belongs-in-the-engine is
# the error that actually matters, because that is the half the report calls migratable.
ALWAYS_EXTERNAL = ("exit",)

# ── the ε boundary ────────────────────────────────────────────────────────────────
# ⚑ FILESYSTEM, PROCESS, NETWORK, CLOCK, TERMINAL — and NOT `hashlib`/`random`/`uuid`.
# The temptation is to call every non-relational library external; that would score
# content-addressing (a digest postgres also computes) as irreducible and inflate the
# ONE number this census exists to produce.  External here means *no rung can reach it*,
# which is a claim about reachability, not about purity.
EXTERNAL_ROOTS = frozenset((
    "os", "subprocess", "shutil", "glob", "tempfile", "socket", "urllib", "http",
    "requests", "pathlib", "io", "gzip", "zipfile", "tarfile", "struct", "signal",
    "threading", "multiprocessing", "concurrent", "fcntl", "select", "platform",
    "getpass", "atexit", "time", "shlex", "pickle", "csv", "webbrowser", "resource",
))
EXTERNAL_NAMES = frozenset((
    "open", "input", "print", "__file__", "Path", "eval", "exec", "compile",
))
EXTERNAL_ATTRS = frozenset((
    "read", "readline", "readlines", "write", "writelines", "communicate",
    "flush", "seek", "unlink", "mkdir", "makedirs", "listdir", "walk", "rmtree",
    "check_output", "check_call", "call", "Popen", "run_command",
))
# ⚑ `sys.argv` AND `os.environ` ARE MODE, NOT EXTERNAL, AND THE ORDER OF THESE TWO
# TESTS IS THE WHOLE DISTINCTION.  `os` is an external root, so a naive root test files
# `os.environ.get("X")` under the irreducible half — which would put the CLI's own
# configuration reads in the same bucket as reading a `.agdai` off the disk.  A branch
# on configuration selects WHICH statement runs; it is not work the engine can take.
MODE_DOTTED = (("sys", "argv"), ("os", "environ"))
MODE_NAMES = frozenset(("__name__", "__main__"))
# ⚑ `except OSError:` IS AN EXTERNAL HANDLER EVEN WHEN THE BODY IS PURE — the exception
# TYPE is the evidence of what the guarded work touched.
EXTERNAL_EXC = frozenset((
    "OSError", "IOError", "FileNotFoundError", "PermissionError", "EOFError",
    "BrokenPipeError", "TimeoutError", "ConnectionError", "KeyboardInterrupt",
    "CalledProcessError", "SystemExit", "UnicodeDecodeError",
))


def _as_list(g):
    """A governing expression is a node, a list of nodes, or nothing."""
    if g is None:
        return []
    return list(g) if isinstance(g, list) else [g]


def _touch(g, names):
    return any(touches(n, names) for n in _as_list(g))


def _attr_root(node):
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _is_mode_dotted(node):
    if not isinstance(node, ast.Attribute):
        return False
    return (_attr_root(node), node.attr) in MODE_DOTTED or any(
        _attr_root(node) == r and _dotted_has(node, a) for r, a in MODE_DOTTED)


def _dotted_has(node, attr):
    while isinstance(node, ast.Attribute):
        if node.attr == attr:
            return True
        node = node.value
    return False


def external_expr(g):
    """Does this expression reach the ε boundary?  (the classifier's first test)"""
    for top in _as_list(g):
        for n in ast.walk(top):
            if isinstance(n, ast.Name) and n.id in EXTERNAL_NAMES:
                return True
            if isinstance(n, ast.Attribute):
                if _is_mode_dotted(n):
                    continue
                if n.attr in EXTERNAL_ATTRS:
                    return True
                if _attr_root(n) in EXTERNAL_ROOTS:
                    return True
            if isinstance(n, ast.Raise) or isinstance(n, ast.Try):
                continue
    return False


def mode_expr(g, params, consts):
    """Does this expression branch on configuration — a parameter, an ALL-CAPS
    module constant, `sys.argv`, `os.environ`, or the `__main__` guard?"""
    for top in _as_list(g):
        for n in ast.walk(top):
            if isinstance(n, ast.Name) and (n.id in params or n.id in consts
                                            or n.id in MODE_NAMES):
                return True
            if isinstance(n, ast.Attribute) and _is_mode_dotted(n):
                return True
    return False


def ext_names(nodes):
    """Names carrying a value that CAME FROM the ε boundary.

    ⚑ THE HOP IS THE WHOLE POINT, AND ITS ABSENCE WAS MEASURED ON THE FIRST RUN.
    `p = subprocess.run(cmd)` then `if p.returncode:` classified as `unclassified`:
    the branch's own expression names no external module, so a predicate reading only
    the governing expression sees a plain attribute test.  This is the same one-hop
    correction `derived_names` records for rows, arriving at the other boundary — and
    it is iterated to a fixpoint because `blob = fh.read()` / `blob = blob or b""`
    chains two hops in the fixture that found it."""
    nodes = list(nodes)
    out = set()
    for _round in range(5):
        before = len(out)
        for n in nodes:
            tgts, val = [], None
            if isinstance(n, ast.Assign):
                tgts, val = n.targets, n.value
            elif isinstance(n, ast.AnnAssign) and n.value is not None:
                tgts, val = [n.target], n.value
            elif isinstance(n, (ast.For, ast.AsyncFor)):
                tgts, val = [n.target], n.iter
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                for it in n.items:
                    if it.optional_vars is not None and external_expr(it.context_expr):
                        out |= _bound(it.optional_vars)
                continue
            if val is not None and (external_expr(val) or touches(val, out)):
                for t in tgts:
                    out |= _bound(t)
        if len(out) == before:
            break
    return out


def _bound(target):
    return {x.id for x in ast.walk(target) if isinstance(x, ast.Name)}


def _own_walk(scope):
    """Every node in one SCOPE, not descending into a nested def/class.

    ⚑ THE MODULE SCOPE IS THE REASON THIS EXISTS.  `ast.walk(module)` reaches every
    function-local name in the file, so a module-level census would inherit every row
    variable in it and report the `if __name__` guard as a row-branch."""
    stack = list(_children(scope))
    while stack:
        n = stack.pop()
        yield n
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        stack.extend(ast.iter_child_nodes(n))


def _children(scope):
    if isinstance(scope, ast.Module):
        return list(scope.body)
    out = list(scope.body)
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        out += list(scope.args.defaults) + [d for d in scope.decorator_list]
    return out


def scopes(tree):
    """[(node, label)] — the module and every def/class in it, each its own scope."""
    out = [(tree, "<module>")]
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((n, n.name))
        elif isinstance(n, ast.ClassDef):
            out.append((n, "class " + n.name))
    return out


def _params(scope):
    if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return set()
    a = scope.args
    names = {x.arg for x in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)}
    for extra in (a.vararg, a.kwarg):
        if extra is not None:
            names.add(extra.arg)
    return names


def _module_consts(tree):
    """ALL-CAPS module-level bindings — the configuration a branch can read."""
    out = set()
    for s in tree.body:
        tgts = []
        if isinstance(s, ast.Assign):
            tgts = s.targets
        elif isinstance(s, ast.AnnAssign):
            tgts = [s.target]
        for t in tgts:
            if isinstance(t, ast.Name) and t.id.isupper():
                out.add(t.id)
    return out


# ── the (construct, kind) → SQL form table ────────────────────────────────────────
# ⚑ KEYED ON THE PAIR, NEVER ON THE SITE.  A per-site judgement is exactly the
# reasoning-not-codified shape the standing rule forbids: it evaporates when the turn
# ends and the next reader re-derives it differently.  A missing key is `unknown`, and
# `unknown` is a FINDING — the sites nobody has yet shown a relational form for.
SQL_FORM = {
    ("for", "row-iteration"): "the SELECT itself — the engine iterates the set",
    ("comp-for", "row-iteration"): "the SELECT itself",
    ("while", "row-iteration"): "recursive CTE",
    ("for-else", "row-iteration"): "NOT EXISTS over the same SELECT",
    ("while-else", "row-iteration"): "NOT EXISTS over the same SELECT",
    ("if", "row-branch"): "WHERE",
    ("elif", "row-branch"): "CASE WHEN",
    ("else", "row-branch"): "CASE ELSE",
    ("ternary", "row-branch"): "CASE",
    ("comp-if", "row-branch"): "WHERE",
    ("and", "row-branch"): "WHERE … AND …",
    ("or", "row-branch"): "WHERE … OR …",
    ("or-default", "row-branch"): "COALESCE",
    ("get-default", "row-branch"): "COALESCE / LEFT JOIN with a default",
    ("get-none", "row-branch"): "LEFT JOIN",
    ("any", "row-branch"): "EXISTS",
    ("all", "row-branch"): "NOT EXISTS (negated predicate)",
    ("next-default", "row-branch"): "LIMIT 1 + COALESCE",
    ("filter", "row-branch"): "WHERE",
    ("match", "row-branch"): "CASE",
    ("case", "row-branch"): "CASE WHEN",
    ("assert", "row-branch"): "CHECK constraint",
    ("yield", "row-iteration"): "the SELECT's own output — the cursor IS the generator",
    ("yield-from", "row-iteration"): "the SELECT's own output",
}
# early-exit forms depend on WHAT the enclosing loop iterates, not on the exit itself
SQL_FORM_EXIT_ROW = {
    "break": "LIMIT 1 / EXISTS",
    "continue": "WHERE NOT (…)",
    "return-in-loop": "LIMIT 1",
}
EXTERNAL_FORM = "external boundary, stays"
MODE_FORM = "not SQL — selects WHICH statement runs"


def sql_form(construct, kind, loop_is_row):
    if kind == "external":
        return EXTERNAL_FORM
    if kind == "mode-branch":
        return MODE_FORM
    if kind == "early-exit":
        return SQL_FORM_EXIT_ROW.get(construct, "unknown") if loop_is_row else "unknown"
    return SQL_FORM.get((construct, kind), "unknown")


class _Census:
    """One scope's control-flow sites, classified."""

    def __init__(self, rows, ext, params, consts, rfns, label):
        self.rows, self.ext = rows, ext
        self.params, self.consts = params, consts
        self.rfns, self.label = rfns, label
        self.loops = []          # stack of loop-is-row flags
        self.tests = []          # stack of enclosing `if` tests
        self.elifs = set()
        self.tail = set()        # id() of a function's trailing `return` — not control flow
        self.out = []

    # -- classification ------------------------------------------------------------
    def classify(self, construct, g, mode_g):
        if construct in EARLY_EXIT_CONSTRUCTS and self.loops:
            return "early-exit"
        if construct in ALWAYS_EXTERNAL:
            return "external"
        if external_expr(g) or _touch(g, self.ext):
            return "external"
        if _touch(g, self.rows) or any(has_read(n, self.rfns) for n in _as_list(g)):
            return "row-iteration" if construct in LOOP_CONSTRUCTS else "row-branch"
        if construct not in LOOP_CONSTRUCTS and mode_expr(mode_g, self.params,
                                                          self.consts):
            return "mode-branch"
        return "unclassified"

    def emit(self, lineno, construct, g, snippet, mode_g=False):
        # ⚑ THE MODE TEST READS A DIFFERENT EXPRESSION THAN THE ROW TEST, and conflating
        # them mislabelled every comprehension guard over an argument.  `[x for x in xs
        # if p(x)]` must consult BOTH `p(x)` and `xs` for row provenance (the rows arrive
        # through the iterable) but ONLY `p(x)` for configuration — otherwise the guard
        # inherits the iterable's parameter-ness and reports as `mode-branch`.
        mg = g if mode_g is False else mode_g
        kind = self.classify(construct, g, mg)
        loop_is_row = bool(self.loops) and self.loops[-1]
        self.out.append((lineno, construct, kind,
                         sql_form(construct, kind, loop_is_row),
                         self.label, snippet.replace("\n", " ")[:96]))

    def _cur_test(self):
        return self.tests[-1] if self.tests else None

    # -- statements ----------------------------------------------------------------
    def stmts(self, body):
        for s in body:
            self.stmt(s)

    def stmt(self, s):
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return                                   # its own scope
        if isinstance(s, ast.If):
            kw = "elif" if id(s) in self.elifs else "if"
            self.emit(s.lineno, kw, s.test, _u(s.test))
            self.tests.append(s.test)
            self.stmts(s.body)
            self.tests.pop()
            if s.orelse:
                if len(s.orelse) == 1 and isinstance(s.orelse[0], ast.If):
                    self.elifs.add(id(s.orelse[0]))
                    self.stmt(s.orelse[0])
                else:
                    # ⚑ AN `else:` HAS NO NODE OF ITS OWN, so the line reported is its
                    # FIRST STATEMENT.  Stated rather than silently off-by-N: a site
                    # table whose line numbers are approximate in one row class and
                    # exact in the rest is unreadable unless it says which.
                    self.emit(s.orelse[0].lineno, "else", s.test,
                              "else of `%s`" % _u(s.test))
                    self.tests.append(s.test)
                    self.stmts(s.orelse)
                    self.tests.pop()
            return
        if isinstance(s, (ast.For, ast.AsyncFor)):
            self.emit(s.lineno, "for", s.iter,
                      "for %s in %s" % (_u(s.target), _u(s.iter)))
            is_row = (_touch(s.iter, self.rows) or has_read(s.iter, self.rfns))
            self.loops.append(bool(is_row))
            self.stmts(s.body)
            self.loops.pop()
            if s.orelse:
                self.emit(s.orelse[0].lineno, "for-else", s.iter,
                          "else of `for … in %s`" % _u(s.iter))
                self.stmts(s.orelse)
            return
        if isinstance(s, ast.While):
            self.emit(s.lineno, "while", s.test, "while %s" % _u(s.test))
            is_row = (_touch(s.test, self.rows) or has_read(s.test, self.rfns))
            self.loops.append(bool(is_row))
            self.stmts(s.body)
            self.loops.pop()
            if s.orelse:
                self.emit(s.orelse[0].lineno, "while-else", s.test,
                          "else of `while %s`" % _u(s.test))
                self.stmts(s.orelse)
            return
        if isinstance(s, ast.Break):
            self.emit(s.lineno, "break", self._cur_test(), "break")
            return
        if isinstance(s, ast.Continue):
            self.emit(s.lineno, "continue", self._cur_test(), "continue")
            return
        if isinstance(s, ast.Return):
            # ⚑ A TRAILING `return` IS NOT CONTROL FLOW and is EXCLUDED — the only
            # exclusion in the roster, and it is stated here rather than left to be
            # inferred from a number.  Every OTHER return is an exit: inside a loop it
            # is an ordering dependency, outside one it is a guard clause.
            if id(s) in self.tail:
                return
            if self.loops:
                self.emit(s.lineno, "return-in-loop", self._cur_test(),
                          "return %s" % _u(s.value))
            else:
                self.emit(s.lineno, "return-guard", self._cur_test(),
                          "return %s" % _u(s.value))
            return
        if isinstance(s, ast.Raise):
            kw = "raise-in-cond" if self._cur_test() is not None else "raise"
            self.emit(s.lineno, kw, self._cur_test() or s.exc, _u(s.exc) or "raise")
            return
        if isinstance(s, ast.Assert):
            self.emit(s.lineno, "assert", s.test, "assert %s" % _u(s.test))
            return
        if isinstance(s, ast.Try) or type(s).__name__ == "TryStar":
            self.emit(s.lineno, "try", s.body, "try:")
            self.stmts(s.body)
            for h in s.handlers:
                g = [h.type] if h.type is not None else []
                if h.type is not None and isinstance(h.type, ast.Name) \
                        and h.type.id in EXTERNAL_EXC:
                    g = [ast.Name(id="open", ctx=ast.Load())]   # force the ε verdict
                self.emit(h.lineno, "except", g or h.body,
                          "except %s" % (_u(h.type) or ""))
                self.stmts(h.body)
            if s.orelse:
                self.emit(s.orelse[0].lineno, "try-else", s.orelse, "else of try")
                self.stmts(s.orelse)
            if s.finalbody:
                self.emit(s.finalbody[0].lineno, "finally", s.finalbody, "finally")
                self.stmts(s.finalbody)
            return
        if isinstance(s, (ast.With, ast.AsyncWith)):
            ctxs = [it.context_expr for it in s.items]
            self.emit(s.lineno, "with", ctxs,
                      "with " + ", ".join(_u(c) for c in ctxs))
            self.stmts(s.body)
            return
        if isinstance(s, ast.Match):
            self.emit(s.lineno, "match", s.subject, "match %s" % _u(s.subject))
            for c in s.cases:
                ln = getattr(c.pattern, "lineno", None) or c.body[0].lineno
                self.emit(ln, "case", s.subject, "case …")
                self.stmts(c.body)
            return
        # any other statement kind carries no control flow of its own; its
        # EXPRESSIONS are covered by the second pass.

    # -- expressions ---------------------------------------------------------------
    def exprs(self, scope):
        for n in _own_walk(scope):
            if isinstance(n, ast.IfExp):
                self.emit(n.lineno, "ternary", n.test,
                          "%s if %s else %s" % (_u(n.body), _u(n.test), _u(n.orelse)))
            elif isinstance(n, ast.BoolOp):
                is_or = isinstance(n.op, ast.Or)
                # ⚑ `x or DEFAULT` IS A BRANCH WEARING A VALUE, and separating it from a
                # plain `or` is what lets a reader see the COALESCEs without arguing
                # about short-circuit noise.
                dflt = (is_or and len(n.values) == 2
                        and isinstance(n.values[-1], (ast.Constant, ast.Dict,
                                                      ast.List, ast.Tuple, ast.Set)))
                self.emit(n.lineno, "or-default" if dflt else ("or" if is_or else "and"),
                          n, _u(n))
            elif isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp,
                                ast.GeneratorExp)):
                for gen in n.generators:
                    self.emit(getattr(gen.iter, "lineno", n.lineno), "comp-for",
                              gen.iter, "for %s in %s" % (_u(gen.target), _u(gen.iter)))
                    for cond in gen.ifs:
                        # ⚑ A COMPREHENSION GUARD IS A FILTER WEARING A LITERAL, and it
                        # is the single most-missed form: it never reads as a branch.
                        self.emit(getattr(cond, "lineno", n.lineno), "comp-if",
                                  [cond, gen.iter], "if %s" % _u(cond),
                                  mode_g=cond)
            elif isinstance(n, ast.Call):
                self._call(n)
            elif isinstance(n, ast.Yield):
                self.emit(n.lineno, "yield", n.value, "yield %s" % _u(n.value))
            elif isinstance(n, ast.YieldFrom):
                self.emit(n.lineno, "yield-from", n.value,
                          "yield from %s" % _u(n.value))

    def _call(self, n):
        f = n.func
        if isinstance(f, ast.Name):
            if f.id in ("any", "all") and n.args:
                self.emit(n.lineno, f.id, n.args[0], "%s(%s)" % (f.id, _u(n.args[0])))
            elif f.id == "next" and len(n.args) >= 2:
                self.emit(n.lineno, "next-default", n.args[0], _u(n))
            elif f.id == "filter" and len(n.args) >= 2:
                self.emit(n.lineno, "filter", n.args[1], _u(n))
            elif f.id in ("exit", "quit"):
                self.emit(n.lineno, "exit", n, _u(n))
        elif isinstance(f, ast.Attribute):
            if f.attr == "exit" and _attr_root(f) == "sys":
                # ⚑ `sys.exit` IS AN EXIT, NOT AN EXTERNAL READ.  It appears under a
                # mode-branch in every CLI here, and filing it as ε would inflate the
                # one ratio this census reports.
                self.emit(n.lineno, "exit", n.args[0] if n.args else None, _u(n))
            elif f.attr == "get" and len(n.args) == 2:
                self.emit(n.lineno, "get-default", [f.value] + list(n.args), _u(n))
            elif f.attr == "get" and len(n.args) == 1:
                self.emit(n.lineno, "get-none", [f.value] + list(n.args), _u(n))


def _u(node):
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:                        # pragma: no cover - unparse is total in 3.9+
        return type(node).__name__


def control_sites(path):
    """[(line, construct, kind, sqlform, scope, snippet)] for one file.

    Every site is reported once.  The population is the CONSTRUCT roster, not a
    judgement about which constructs matter — see the module docstring."""
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src, filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return []
    rfns = store_reader_fns(tree)
    consts = _module_consts(tree)
    out = []
    for scope, label in scopes(tree):
        own = list(_own_walk(scope))
        rows = row_names(own, rfns)
        rows |= derived_names(own, rows)
        cen = _Census(rows, ext_names(own), _params(scope), consts, rfns, label)
        body = scope.body if not isinstance(scope, ast.Module) else scope.body
        if body and isinstance(body[-1], ast.Return):
            cen.tail.add(id(body[-1]))
        cen.stmts(body)
        cen.exprs(scope)
        out.extend(cen.out)
    return sorted(out, key=lambda r: (r[0], r[1]))


def census(paths):
    """{path: rows} over a file population — the corpus form of `control_sites`."""
    files = _pycodemod_core.py_files(*paths) if paths else _pycodemod_core.py_files()
    return files, {p: control_sites(p) for p in files}


def _print_control(paths, summary=False, kind=None, constructs=False):
    """`--control` — every piece of control flow, typed by what the engine could take."""
    files, per = census(paths)
    rows = []
    for p in files:
        rel = os.path.relpath(p, _pycodemod_core.ROOT)
        for line, construct, k, form, scope, snip in per[p]:
            if kind and k != kind:
                continue
            rows.append((rel, line, construct, k, form, scope, snip))
    by_kind, by_construct, by_group, by_file = {}, {}, {}, {}
    by_file_kind = {}
    for rel, _l, construct, k, _f, _s, _sn in rows:
        by_kind[k] = by_kind.get(k, 0) + 1
        by_construct[construct] = by_construct.get(construct, 0) + 1
        by_file[rel] = by_file.get(rel, 0) + 1
        by_file_kind[(rel, k)] = by_file_kind.get((rel, k), 0) + 1
        for g, cs in CONSTRUCT_GROUPS.items():
            if construct in cs:
                by_group[g] = by_group.get(g, 0) + 1
    if constructs:
        # ⚑ THE ROSTER WITH ITS COUNTS, INCLUDING THE ZEROES.  A construct the corpus
        # does not use and a construct the mode cannot see are different facts, and only
        # printing the zero rows keeps them distinguishable.
        for g, cs in CONSTRUCT_GROUPS.items():
            print("  ── %s  (%d site(s))" % (g, by_group.get(g, 0)))
            for c in cs:
                print("       %-16s %5d" % (c, by_construct.get(c, 0)))
        print("%d construct kind(s) in the roster; %d site(s) over %d of %d file(s)"
              % (len(CONSTRUCTS), len(rows), len(by_file), len(files)))
        return 0
    if not summary:
        for rel, line, construct, k, form, scope, snip in sorted(rows):
            print("  %-13s %-14s %-42s %s:%d  (%s)  %s"
                  % (k, construct, form, rel, line, scope, snip))
    # ⚑ THE EARLY EXITS ARE PRINTED AGAIN, SEPARATELY, and that duplication is
    # deliberate: they are the ordering dependencies, the hardest class to express
    # relationally, and the class `--relalg` structurally could not see.  Buried in a
    # 2,000-row table they are invisible, which is how `_unreflected_floor` stayed
    # unnoticed for four edits while a mode that "covered" the file reported green.
    ee = [r for r in rows if r[3] == "early-exit"]
    if ee and not summary:
        print("  ── EARLY EXITS (ordering dependencies — call these out) ──")
        for rel, line, construct, _k, form, scope, snip in sorted(ee):
            print("       %-14s %-28s %s:%d  (%s)  %s"
                  % (construct, form, rel, line, scope, snip))
    # ⚑ THE BY-FILE TABLE CARRIES THE KIND SPLIT, NOT A TOTAL.  A bare per-file count
    # cannot tell a decoder shim (almost all ε, irreducible by construction) from a
    # row-processing module of the same size — and the whole question is which is which.
    # The first run of this census reported `jea_agdai.py: 122` beside `sppf_db.py: 305`
    # and said nothing about the only difference that matters.
    print("  ── by file × kind ── (%s)"
          % "  ".join("%s=%s" % (k[:4], k) for k in CONTROL_KINDS))
    print("     %6s %6s %6s %6s %6s %6s   %6s  %s"
          % tuple([k[:4] for k in CONTROL_KINDS] + ["total", "file"]))
    for rel, n in sorted(by_file.items(), key=lambda kv: -kv[1]):
        cells = [by_file_kind.get((rel, k), 0) for k in CONTROL_KINDS]
        print("     %6d %6d %6d %6d %6d %6d   %6d  %s"
              % tuple(cells + [n, rel]))
    print("  ── by group ──")
    for g in CONSTRUCT_GROUPS:
        print("     %-15s %5d" % (g, by_group.get(g, 0)))
    print("  ── by kind ──")
    for k in CONTROL_KINDS:
        print("     %-14s %5d" % (k, by_kind.get(k, 0)))
    unk = sum(1 for r in rows if r[4] == "unknown")
    ext = by_kind.get("external", 0)
    # ⚑ THE HEADLINE IS THE RATIO, NOT THE TOTAL.  The question being asked is *how much
    # of this belongs in the engine* — a bare total answers a different question and
    # reads as bigger work than it is.
    print("control: %d site(s) in %d of %d file(s)" % (len(rows), len(by_file), len(files)))
    if rows:
        print("   ε IRREDUCIBLE (external)            %5d  (%.1f%%)"
              % (ext, 100.0 * ext / len(rows)))
        print("   work that belongs in the engine     %5d  (%.1f%%)"
              % (len(rows) - ext, 100.0 * (len(rows) - ext) / len(rows)))
        print("   of which no relational form named   %5d  (sqlform=unknown — the finding)"
              % unk)
    if not files:
        print("   ⚑ NO FILES SEARCHED — a fact about the QUERY, not the code.")
    return 0
