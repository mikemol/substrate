# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⟡exit-and-swallow — TWO CENSUSES OVER ONE FACT, and the fact is a class hierarchy.

⚑⚑⚑ `SystemExit` DERIVES FROM `BaseException`, NOT FROM `Exception`.  Everything in this
file follows from that one line of the Python data model, and it cuts BOTH WAYS:

  * `except Exception:`  does NOT catch it  → a swallowing handler FAILS OPEN precisely
                                              on the exit it was written to contain;
  * `except BaseException:` / bare `except:` DOES catch it → FAILS CLOSED on the one
                                              thing it must not swallow.

Both directions are wrong, and WHICH ONE YOU GET DEPENDS ON A DISTINCTION NOBODY WRITING
THE HANDLER WAS THINKING ABOUT.  That is why this is one module and not two: a census of
`sys.exit` sites and a census of swallowing handlers answer each other's question.

⚑⚑ THE CANONICAL LIVE CASE, MEASURED 2026-08-26, AND IT IS ONE EDGE.
`scripts/gate_census.py:496-501` wraps `edit_snapshot.guard(...)` in `except Exception`.
`--reaches guard set` resolves `edit_snapshot.guard → edit_snapshot.snapshot →
Ambient.set`, and `Ambient.set` calls `sys.exit(2)` on an unrecognised vocab value.  So:
the guard's handler CANNOT catch that exit, and an exit 2 propagates out of a
best-effort snapshot call into pre-commit.  Latent ONLY because the caller returns early
when the census is current — i.e. it fires exactly when Phase 0 matters.  The swallow
census alone reports `gate_census.py:500` as a benign logging handler; the exit census
alone reports `Ambient.set` as one of many exits.  Neither is the finding.  The EDGE is.

⚑ WHY THIS IS A SIBLING FILE AND NOT A FUNCTION IN `_pycodemod_query`.  All three
candidate homes (`pycodemod`, `_pycodemod_query`, `toolmodes`) are already OVER the
1200-line `--size` cap, and adding to an over-cap module grows the debt the cap exists to
measure.  `_pycodemod_placement.py` was split out on exactly this argument; this follows
it.

⚑ WHAT THIS DELIBERATELY DOES NOT REBUILD.  `_pycodemod_query.swallows` already censuses
SILENT discards (`pass`/`continue`/bare `return`) with the `_feeds_verdict` triage split,
and it is not re-implemented here.  This module asks the ORTHOGONAL question that
`swallows` cannot: does a handler CATCH `SystemExit` — which is a property of the
handler's TYPE, not of its body, and therefore fires on handlers `swallows` correctly
ignores (one that logs and continues still swallows the exit).
"""
import ast
import os

import _pycodemod_core

# ⚑ THE THREE SPELLINGS THAT CATCH `SystemExit`, AND THERE ARE EXACTLY THREE IN THE
# SYNTAX.  A bare `except:`, `except BaseException`, and `except SystemExit` (naming it,
# which is nearly always DELIBERATE and is reported as its own bucket rather than as a
# defect).  `except Exception` is the FAILS-OPEN side and is reported by `exits`, not
# here — the two censuses meet in `interlock`.
_CATCHERS = {"BaseException": "base", "SystemExit": "named"}

# ⚑ AN EXIT IS A CALL, AND IT HAS THREE SPELLINGS THIS READER RESOLVES.  `sys.exit(...)`,
# a bare `exit(...)`/`quit(...)` (the site-builtin — a defect in a tool regardless of
# ownership), and `os._exit(...)` (which does not even unwind, so no handler anywhere
# can contain it).  `raise SystemExit(...)` is the FOURTH and is handled separately
# because it is a Raise node, not a Call.
_EXIT_CALLS = {("sys", "exit"): "sys.exit", ("os", "_exit"): "os._exit"}
_EXIT_BARE = {"exit": "builtin-exit", "quit": "builtin-exit"}


def _parse(path):
    """Parsed tree for `path`, or None — and RECORD the skip on `_parse.skipped`.

    ⚑⚑⚑ THIS EXISTS BECAUSE THE FIRST CUT OF THIS MODULE COMMITTED THE DEFECT THE MODULE
    CENSUSES.  All three lenses opened files under `except (SyntaxError, OSError):
    continue` — a silent discard whose swallowed work FEEDS THE VERDICT, which is
    `_feeds_verdict`'s exact criterion and would have been a VERDICT row in `--swallows`
    had anyone run it against this file.  A corpus query that cannot read a file reports
    a smaller population and no number says so; `--dead` read GREEN on a file with 18
    defs that way.  The skip stays — one unparseable file must not abort the census —
    but it is now ACCOUNTED, which is the whole distinction.

    ⚑ ONE READER FOR ALL THREE LENSES, so a skip counted once cannot be counted twice
    and the reported population is the one actually read.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return ast.parse(fh.read(), filename=str(path))
    except SyntaxError as e:
        _parse.skipped.append((str(path), "unparseable", type(e).__name__))
    except OSError as e:
        _parse.skipped.append((str(path), "unreadable", type(e).__name__))
    return None


_parse.skipped = []


def report_skips(population):
    """Print the incomplete-scan accounting `Mode(scans=True)` owes, or nothing."""
    sk = _parse.skipped
    if not sk:
        return
    kinds = {}
    for _p, why, exc in sk:
        kinds.setdefault(why, []).append(exc)
    print(f"   ⚑ INCOMPLETE SCAN — read {population - len(sk)} of {population} "
          f"file(s); {len(sk)} skipped:")
    for why in sorted(kinds):
        print(f"     {why}: {len(kinds[why])} ({', '.join(sorted(set(kinds[why])))})")
    for p, why, exc in sorted(set(sk))[:10]:
        print(f"       - {os.path.relpath(p, _ROOT)}  [{why}: {exc}]")
    if len(sk) > 10:
        print(f"       … and {len(sk) - 10} more")
    if population and len(set(p for p, _w, _e in sk)) == population:
        print("   ⚑⚑ EVERY file was skipped — a BROKEN QUERY, not an empty result.")


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _module_name(path):
    return os.path.basename(str(path))[:-3] if str(path).endswith(".py") else None


def _owners(tree):
    """{id(node): (innermost def name or None, under __main__ guard)} — ONE pass.

    ⚑⚑ BY IDENTITY, NOT BY LINE RANGE.  A line-range containment test gets nested defs
    and decorators wrong, and `id()` is exact — the same mechanism `_feeds_verdict`
    relies on, and for the same reason.

    ⚑ AND IT IS ONE DESCENT, NOT A SEARCH PER SITE, BECAUSE THE OBVIOUS SHAPE DID NOT
    FINISH.  The first cut asked "which def contains this node" by walking every def and
    testing membership — O(defs × nodes) per site, which over `scratch/ scripts/ jea/`
    ran past two minutes of CPU on files like `applied_grammar (1).py`.  A census nobody
    can afford to run is a census nobody runs.  Pushing the context DOWN the tree once
    computes the same map in a single traversal.
    """
    out = {}

    def go(n, fn, main):
        out[id(n)] = (fn, main)
        for c in ast.iter_child_nodes(n):
            f2, m2 = fn, main
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                f2 = c.name
            elif isinstance(c, ast.If):
                t = c.test
                if isinstance(t, ast.Compare) and isinstance(t.left, ast.Name) \
                        and t.left.id == "__name__":
                    m2 = True
            go(c, f2, m2)

    go(tree, None, False)
    return out


def _exit_sites_one(path, tree, own=None):
    """[(line, spelling, defname, under_main)] for one parsed file.

    ⚑ `under_main` IS THE CHEAP HALF OF THE DISCRIMINATOR AND NOT THE WHOLE ANSWER.  A
    module-level exit under `if __name__ == "__main__":` is a CLI exiting its own
    process — fine.  An exit inside a `def` is the case that matters, and the guard
    cannot see it: the def may be called from the main block AND imported by another
    module.  The importer join in `exits` answers that; this only clears the
    trivially-fine population.
    """
    own = own if own is not None else _owners(tree)
    out = []
    for node in ast.walk(tree):
        spelling = None
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                spelling = _EXIT_CALLS.get((f.value.id, f.attr))
            elif isinstance(f, ast.Name):
                spelling = _EXIT_BARE.get(f.id)
        elif isinstance(node, ast.Raise):
            exc = node.exc
            nm = None
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                nm = exc.func.id
            elif isinstance(exc, ast.Name):
                nm = exc.id
            if nm == "SystemExit":
                spelling = "raise SystemExit"
        if spelling is None:
            continue
        fn, main = own.get(id(node), (None, False))
        out.append((node.lineno, spelling, fn, main))
    return sorted(out)


def _reached_names(paths):
    """{module: {name reachable from SOME OTHER file}} — the def-level half.

    ⚑⚑⚑ THE MODULE-LEVEL JOIN ALONE OVER-REPORTS, AND IT OVER-REPORTED BY 130 ROWS IN
    ONE DEF.  The first cut asked only *"is this module imported by another file"*, so
    `pycodemod._dispatch` — 130 `sys.exit` calls in the CLI dispatcher — read LIBRARY
    because seven files `import pycodemod`.  `--calls _dispatch` says its only callers
    are `pycodemod.py:3815/3817`, INSIDE its own `__main__` block.  Nothing imports the
    dispatcher; they import the query functions beside it.  A census reporting 174
    LIBRARY sites of which 130 are one unreachable def is a fact about the JOIN.

    ⚑⚑ SO THE PREDICATE IS NARROWED, NOT WIDENED, AND THE NARROWING IS STRUCTURAL.  A
    def is library-reached when another file NAMES it — `from m import f`, or `m.f`
    read as an attribute — or when it is transitively called (within its own module)
    from such a name.  `import m` alone reaches only what the importer then SPELLS.
    Widening this back to "the module is imported" to avoid a miss would restore exactly
    the unactionable rows it was built to remove.

    ⚑ THE COST IS UNDER-REPORTING VIA `getattr` AND `*`-IMPORT, WHICH ARE DECLARED IN
    `KNOWN_MISSES` rather than papered over with a wider rule.  A `from m import *` is
    treated as reaching every public name, since that is what it does.
    """
    named = {}
    for p in paths:
        tree = _parse(p)
        if tree is None:
            continue
        self_mod = _module_name(p)
        # module alias -> real module, so `import x as P` then `P.f` resolves
        alias = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    alias[a.asname or a.name.split(".")[0]] = a.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                m = node.module.split(".")[0]
                if m == self_mod:
                    continue
                for a in node.names:
                    named.setdefault(m, set()).add(a.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                m = alias.get(node.value.id)
                if m and m != self_mod:
                    named.setdefault(m, set()).add(node.attr)
    return named


def _imported_modules(paths):
    """{module_name: {importing file, …}} over the scanned corpus.

    ⚑ FLAT-MODULE ONLY, AND THAT IS THE CORPUS' OWN SHAPE.  `scratch/` and `scripts/`
    are sys.path-flat: `import edit_snapshot` binds the file `scratch/edit_snapshot.py`.
    A dotted package import is recorded under its FIRST segment, which over-approximates
    (it may name a stdlib package) — over-approximation here means a module reads as
    imported when it is not, which biases toward reporting a site as library-reachable.
    That is the conservative direction: over-report, never miss.
    """
    idx = {}
    for p in paths:
        tree = _parse(p)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    idx.setdefault(a.name.split(".")[0], set()).add(str(p))
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                idx.setdefault(node.module.split(".")[0], set()).add(str(p))
    return idx


def exits(paths=None):
    """[(path, line, spelling, defname, verdict, why)] — every process-exit site, CLASSIFIED.

    ⚑⚑⚑ A RAW COUNT OF `sys.exit` SITES IS USELESS AND THE COUNT IS LARGE.  The
    population is mostly LEGITIMATE: a CLI's dispatch branch ending in `sys.exit(0)` owns
    its process and is correct.  The DEFECT is `sys.exit` in a function another module
    IMPORTS — *"no script should assume it's the sole owner of the current pid"* — because
    an exit there kills the CALLER's process.  Measured in this corpus, tools DO import
    each other: `build_census` is reached only as a library from `gen_build_makefiles`;
    `split_pipeline` calls `rename_at_source`; `check_mypy_ratchet` imports
    `check_scratch_independence`.

    The verdict buckets, and each is a STRUCTURAL property, not a taste call:

      main-only   the exit is under `if __name__ == "__main__":`, or at module level in a
                  file NO other file imports.  The process is the tool's own.  FINE.
      dispatch    the exit is inside a def NO IMPORTER REACHES — either nothing imports
                  the module, or importers name only other things in it.  ⚑ NOT the same
                  as "unimported", and the difference is 130 rows: see `_reached_names`.
      LIBRARY     the exit is inside a def another file NAMES (or reaches through this
                  module's own calls from such a name).  This is the defect the operator
                  named: a callee terminating a caller's process.
      hard        `os._exit` — does not unwind, so NO handler anywhere can contain it.
                  Reported separately at any reachability, because the reachability
                  question does not change what it does.

    ⚑⚑ `raise SystemExit` IS COUNTED AS AN EXIT, AND THAT IS DELIBERATE.  It is the same
    control flow with a spelling that reads as a raise; a reader auditing `sys.exit` by
    name misses it entirely, which is exactly the one-spelling census defect this repo
    keeps paying for (`--calls emit` vs `_emit_one`).  It is reported under its own
    spelling so the two are never conflated.
    """
    paths = [str(p) for p in (paths or _pycodemod_core.py_files())]
    imported_by = _imported_modules(paths)
    reached = _reached_names(paths)
    rows = []
    for p in paths:
        tree = _parse(p)
        if tree is None:
            continue
        mod = _module_name(p)
        own_all = _owners(tree)
        # ⚑ THE ENTRY NAMES ANOTHER FILE SPELLS, CLOSED FORWARD OVER THIS MODULE'S OWN
        # CALLS.  `edit_snapshot.guard` is what consumers name; the exit is two hops
        # down in `Ambient.set`. A one-hop test would miss the live case entirely —
        # which is the whole reason `reaches` is transitive.
        calls = {}
        for n in ast.walk(tree):
            d, _m = own_all.get(id(n), (None, False))
            if d is None or not isinstance(n, ast.Call):
                continue
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else \
                (f.id if isinstance(f, ast.Name) else None)
            if nm:
                calls.setdefault(d, set()).add(nm)
        live = set(reached.get(mod, ()))
        for _ in range(len(calls) + 1):
            grew = set()
            for d in live & set(calls):
                grew |= calls[d]
            grew -= live
            if not grew:
                break
            live |= grew
        # ⚑ SELF-IMPORT IS NOT AN IMPORTER.  A file that imports its own name (a
        # re-export shim, a __main__ re-entry) would otherwise make every tool read as
        # library-reachable and the census would classify nothing.
        others = {q for q in imported_by.get(mod, ()) if q != p}
        for line, spelling, defname, under_main in _exit_sites_one(p, tree, _owners(tree)):
            if spelling == "os._exit":
                verdict, why = "hard", "does not unwind — no handler can contain it"
            elif under_main:
                verdict, why = "main-only", "under the __main__ guard"
            elif defname is None:
                verdict, why = ("main-only", "module level, nothing imports this module") \
                    if not others else \
                    ("LIBRARY", "module level in a module %d file(s) import" % len(others))
            elif defname in live:
                verdict, why = "LIBRARY", "in def %s(), NAMED by another file; %d " \
                    "file(s) import %s" % (defname, len(others), mod)
            else:
                # ⚑ NOT "no importer" — "no importer REACHES THIS DEF".  Saying the
                # former would be the module-level claim the def-level join replaced,
                # and it is false for `pycodemod._dispatch` (7 importers, none of which
                # name it).  The row is fine either way; the REASON must be the one
                # actually computed.
                verdict, why = "dispatch", "in def %s(); no importer names or " \
                    "reaches it (%d file(s) import %s)" % (defname, len(others), mod)
            rows.append((p, line, spelling, defname, verdict, why))
    return sorted(rows)


def catchers(paths=None):
    """[(path, line, kind, defname, silent)] — every handler that CATCHES `SystemExit`.

    ⚑⚑⚑ THE OTHER HALF, AND IT IS A PROPERTY OF THE HANDLER'S TYPE, NOT ITS BODY.  This
    is why it cannot be a filter over `_pycodemod_query.swallows`: `swallows` reports a
    handler whose body is exactly `pass`/`continue`/`return`, which is the SILENT-DISCARD
    question.  A handler that catches `BaseException` and then LOGS and continues is not
    a silent discard — `swallows` correctly ignores it — and it still eats a
    `KeyboardInterrupt` and a `SystemExit`.  Two orthogonal predicates over the same
    node type; running one as the other reports the method as the substrate.

      bare-except   `except:`               — catches SystemExit AND KeyboardInterrupt
      base          `except BaseException`  — same, spelled explicitly
      named         `except SystemExit`     — DELIBERATE by construction.  Naming the
                                              class is the accounting; a reader cannot
                                              write this by accident.  Reported so the
                                              census is complete, NOT as a defect.

    `silent` carries whether the body is a bare discard, so the intersection with the
    `swallows` population is readable WITHOUT a carve-out list.
    """
    paths = [str(p) for p in (paths or _pycodemod_core.py_files())]
    rows = []
    for p in paths:
        tree = _parse(p)
        if tree is None:
            continue
        own = _owners(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue
            if node.type is None:
                kind = "bare-except"
            elif isinstance(node.type, ast.Name):
                kind = _CATCHERS.get(node.type.id)
            elif isinstance(node.type, ast.Tuple):
                kind = next((_CATCHERS[e.id] for e in node.type.elts
                             if isinstance(e, ast.Name) and e.id in _CATCHERS), None)
            else:
                kind = None
            if kind is None:
                continue
            # ⚑ A HANDLER THAT RE-RAISES IS NOT A SWALLOW EVEN IF IT IS BARE.  `except:
            # cleanup(); raise` is the correct spelling of a finally-like block and must
            # not be censused beside a discard, or the list is one nobody triages.
            reraises = any(isinstance(s, ast.Raise) for s in ast.walk(node))
            body = [s for s in node.body
                    if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            silent = (not reraises and len(body) == 1
                      and isinstance(body[0], (ast.Pass, ast.Continue))) or \
                     (not reraises and len(body) == 1
                      and isinstance(body[0], ast.Return) and body[0].value is None)
            fn, _m = own.get(id(node), (None, False))
            rows.append((p, node.lineno, kind, fn, bool(silent), bool(reraises)))
    return sorted(rows)


def interlock(paths=None):
    """[(path, line, defname, callee)] — an `except Exception` guarding a call that can EXIT.

    ⚑⚑⚑ THIS IS THE CENSUS THE TWO HALVES EXIST TO PRODUCE, AND NEITHER HALF SEES IT.
    A handler spelled `except Exception` reads as containment and IS NOT: if anything in
    its `try` body reaches a `sys.exit`, the exit walks straight through, because
    `SystemExit` is not an `Exception`.  The site LOOKS defended.  `gate_census.py:500`
    is exactly this, on the pre-commit hook path.

    ⚑⚑ AND THE REACHABILITY HERE IS HONEST-BY-REFUSAL, EXACTLY AS `reaches` IS.  A call
    inside the try is matched against the set of function NAMES this corpus defines that
    contain (transitively, WITHIN THEIR OWN MODULE) an exit.  A bare callee name is not a
    resolved symbol — `reaches` records that fabricating cross-module hops produced 26 of
    29 false round trips — so a cross-module chain longer than one hop reads as NOT
    REACHED.  The cost is UNDER-reporting, which is the safe direction: an over-report is
    a fabricated dependency someone acts on.  This is therefore a FLOOR.
    """
    paths = [str(p) for p in (paths or _pycodemod_core.py_files())]
    # names of functions that exit, per module, closed transitively within the module
    trees, exiting = {}, {}
    for p in paths:
        t = _parse(p)
        if t is not None:
            trees[p] = t
    for p, tree in trees.items():
        own = _owners(tree)
        # ⚑ ONE PASS FOR BOTH FACTS.  The `_owners` map already says which def each node
        # is in, so the call graph and the exiting-def set come out of a single walk —
        # the per-def re-walk this loop first did was the same quadratic that made the
        # census unaffordable to run.
        direct, calls = set(), {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                calls.setdefault(fn.name, set())
        for n in ast.walk(tree):
            d, _m = own.get(id(n), (None, False))
            if d is None:
                continue
            if isinstance(n, ast.Call):
                f = n.func
                nm = f.attr if isinstance(f, ast.Attribute) else \
                    (f.id if isinstance(f, ast.Name) else None)
                if nm:
                    calls.setdefault(d, set()).add(nm)
        for _l, _sp, d, under_main in _exit_sites_one(p, tree, own):
            if d is not None and not under_main:
                direct.add(d)
        # ⚑ FIXPOINT, NOT ONE HOP.  `guard → snapshot → set` is the live case and a
        # single-hop join does not see it.  Bounded by the def count, so it terminates.
        closed = set(direct)
        for _ in range(len(calls) + 1):
            grew = {f for f, ns in calls.items() if ns & closed} - closed
            if not grew:
                break
            closed |= grew
        exiting[p] = closed
    # a module's exiting names are visible to any file that imports that module
    by_mod = {_module_name(p): names for p, names in exiting.items()}
    imported_by = _imported_modules(paths)
    rows = []
    for p, tree in trees.items():
        own = _owners(tree)
        visible = set(exiting.get(p, ()))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name.split(".")[0] for a in node.names] \
                    if isinstance(node, ast.Import) else \
                    ([node.module.split(".")[0]] if node.module and not node.level else [])
                for m in mods:
                    visible |= by_mod.get(m, set())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            broad = [h for h in node.handlers
                     if isinstance(h.type, ast.Name) and h.type.id == "Exception"]
            if not broad:
                continue
            if any(isinstance(s, ast.Raise) for h in broad for s in ast.walk(h)):
                continue                       # re-raises: the exit is not absorbed anyway
            # ⚑ WALK THE ORIGINAL STATEMENTS, never a synthetic `ast.Module` wrapper.
            # `id()` identity is the whole mechanism in `_owners`, and re-wrapping would
            # give fresh nodes that match nothing — the enclosing-def lookup would come
            # back `<module>` for every row. `_feeds_verdict` records the same trap.
            for s in (x for st in node.body for x in ast.walk(st)):
                if not isinstance(s, ast.Call):
                    continue
                f = s.func
                nm = f.attr if isinstance(f, ast.Attribute) else \
                    (f.id if isinstance(f, ast.Name) else None)
                if nm and nm in visible:
                    d, _m = own.get(id(node), (None, False))
                    rows.append((p, node.lineno, d, nm))
                    break
    _ = imported_by
    return sorted(set(rows))


# ⚑⚑ DECLARED, NOT COMPUTED — A CENSUS CANNOT DERIVE ITS OWN BLIND SPOTS.  `--ambient`
# established this shape and it is followed here rather than re-argued: every spelling
# below is one this reader provably does not see, written down so a zero in a bucket is
# read as the boundary of the instrument and not as a fact about the tree.
KNOWN_MISSES = (
    "an exit reached through an ALIAS — `from sys import exit as bail`, or "
    "`_exit = sys.exit` then `_exit(2)`: the call node names a local, not `sys.exit`.",
    "an exit behind INDIRECTION — a handler stored in a dict/registry and dispatched, "
    "or `getattr(sys, 'exit')`. The call node has no resolvable name.",
    "an exit in a SUBPROCESS or a `python -c` string: not python this reader parses.",
    "a LIBRARY exit reached across TWO OR MORE module hops. `interlock`'s call graph is "
    "same-module-transitive plus ONE import hop, matching `reaches`' refusal to "
    "fabricate cross-module edges. A longer chain reads as not-reached.",
    "a decorator or a metaclass that installs an exiting wrapper: the exit is not "
    "lexically inside the def it terminates.",
    "`argparse`'s own `parser.error()` / `parse_args()`, which raise SystemExit from "
    "STDLIB code. Every tool using argparse has an exit this census cannot attribute, "
    "and an `except Exception` around a parse call is an interlock site invisible here.",
    "an importer spelled as a PACKAGE path (`from a.b import c`) is recorded under `a`, "
    "so a module named `c` reads as un-imported. Over-approximates the other way too.",
    "the non-python surface entirely: a shell wrapper, a Makefile recipe, or a hook "
    "that reads an exit code has no node here.",
    # ⚑⚑ NEWLY LEARNED 2026-08-26, and it is a miss of the CLI around the census rather
    # than of the reader.  Recorded here because a reader auditing this mode's numbers
    # needs to know which invocations the tool will and will not honour.
    "a MODIFIER FLAG that is ALSO a declared mode name is accepted by any mode, whether "
    "or not that mode declares it: `--sites` is both `MODES['--sites']` and an opt of "
    "five other modes, so `--swallows --sites` runs silently while `--swallows "
    "--misses` correctly refuses. Every other unrecognised flag now REFUSES (exit 2).",
    "the UNDER-MAIN test is lexical: an exit inside a def CALLED ONLY from the "
    "`__main__` block still reads `dispatch`, and an exit under a `__main__` guard "
    "spelled other than `__name__ == ...` (a `main()` invoked by a console-script entry "
    "point) is not recognised as one. Checked against `edit_snapshot` (all 5 exits "
    "genuinely under the guard); the spelling variants are unmeasured.",
)

# ⚑⚑⚑ CLOSED — KEPT AS RESIDUE, NOT DELETED, BECAUSE THE REPORT WAS PLAUSIBLE AND WRONG.
# `--exits` was reported (2026-08-26) as blind to FUNCTION-LOCAL imports: `edit_snapshot`
# has 91 import sites in 58 files, most of them `import edit_snapshot as _es` INSIDE a
# def, and the mode reports 0 LIBRARY for it.  Two positive controls settle it:
#
#   * FIRES — a file whose only reference is a function-local `import lib_a as _la`
#     followed by `_la.bang()` classifies `bang()` as LIBRARY.  `_reached_names` walks
#     with `ast.walk`, which descends into defs, so both the alias binding and the
#     attribute read are already collected.  There is no function-local blind spot.
#   * DOES NOT FIRE — a sibling def `unreached_bang()` in the same module, named by
#     nobody, classifies `dispatch`.  So the join is not merely permissive.
#
# ⚑⚑ AND THE ZERO WAS CORRECT FOR A SECOND, INDEPENDENT REASON.  All 5 of
# `edit_snapshot`'s exits are genuinely under its `__main__` guard, and the `sys.exit(2)`
# in `Ambient.set` that the module docstring above cites as the live case WAS ALREADY
# REPAIRED (⟡intent-conflict-reconverted): it raises `AmbientVocabError` now.  The
# docstring's canonical example is therefore a historical record, not a current finding.
# Nothing was widened, and the 130 `pycodemod._dispatch` rows the narrowed join removes
# stay removed.
