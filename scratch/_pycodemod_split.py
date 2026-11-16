# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`pycodemod --split` — cut an oversized module into SIBLING modules, mechanically.

⚑ THE MODE EXISTS BECAUSE THE CUT ITSELF HAD NO TOOL.  `--size` names a file too big to read
whole, `--layout` says where its top-level statements are, and `--commentary --since` gates
what a split DROPPED.  Between the census and the gate there was nothing that PERFORMED the
cut, so the cut was left to string surgery — the output-manipulation the standing rule forbids,
on exactly the corpus whose comments ARE the argument.  A named mode is approved once; a
one-off script is a permission granted once and a capability that never accumulates.

⚑ SIBLINGS, NOT A SUBPACKAGE, AND THAT IS CORRECTNESS RATHER THAN TASTE.  A body that reads
`Path(__file__).resolve().parent` is asking WHICH DIRECTORY AM I IN.  Moving it one level down
silently re-answers that question — the ledger file, the bib, the project root and every
`rglob` beneath them all shift, and every assertion over them goes on passing about the wrong
tree.  Emitting the parts BESIDE the original keeps `__file__`'s directory invariant, so those
bodies relocate byte-identically and still mean what they meant.  What no placement can
preserve is `__file__` read as SOURCE TEXT (`read_text`, `inspect.getsource`): after a split a
part sees only its own share.  Those statements are REPORTED AS HAZARDS, named and counted,
rather than relocated in silence — a split's under-coverage is invisible by construction,
because the shrunken scan still passes.

⚑ THE PART GRAPH IS ACYCLIC BY CONSTRUCTION, NOT BY INSPECTION.  Parts are packed out of a
TOPOLOGICAL order of the statement graph's STRONGLY-CONNECTED COMPONENTS, so part i can only
reference parts < i and no emitted `from <sibling> import` can ever close a cycle.  A cycle
between statements is CO-LOCATED rather than refused: `def f(): return T` beside `T = {"k": f}`
is a cycle in the reference graph and not one in Python, because `f` resolves `T` at CALL time.
What the cycle forbids is putting the two ends in different parts, where the sibling import
between them would be eager and genuinely circular.  (The first cut refused any cycle outright
and the mode's own selftest refuted it — that case is kept, and is why the SCC is the atom of
packing rather than the statement.)  A component that cannot fit in ONE part is then refused on
size, which is a size fact and not a shape one.

⚑ `ast` FOR THE SCOPE ANALYSIS, `libcst` FOR THE CUT — this file's parent states the division
and it is load-bearing twice over here.  Deciding WHICH names a statement needs is a read-only
scope question, so the stdlib answers it; MOVING the statement must reproduce its comments and
blank lines byte-for-byte, so libcst does that.  Using `ast` for the second half would discard
the incident log, which is the more valuable half of these files.
"""
import ast
import os
import textwrap

import _pycodemod_core as _c

try:
    import libcst as cst
except ImportError:  # pragma: no cover - environment probe
    cst = None

#: Attribute calls that read a path as SOURCE TEXT rather than as a location.  A statement
#: combining one of these with `__file__` cannot be relocated without changing what it reads.
_TEXT_READS = ("read_text", "read_bytes", "readlines", "getsource", "getsourcelines")


# ── reading sub-options without inventing modes ───────────────────────────────────────────────

def argopt(argv, flag, default=None):
    """The token after `flag`, or `default`.

    ⚑ A FUNCTION, NOT AN `if "--x" in sys.argv` INSIDE `_dispatch`, and the reason is the mode
    census.  `modes()` DERIVES the roster from exactly that shape, so writing a sub-option
    inline would enter `--max`, `--prefix`, `--keep` and `--export` into the census as
    top-level modes, `--banner` would then demand a usage line for each, and the tool's own
    self-description would claim four commands that do not exist on their own.  A sub-option
    belongs in its owner's usage line, which is where this one is documented.
    """
    return (argv[argv.index(flag) + 1]
            if flag in argv and argv.index(flag) + 1 < len(argv) else default)


def argflag(argv, flag):
    """Is `flag` present?  See `argopt` for why this is not written inline."""
    return flag in argv


# ── the scope analysis ────────────────────────────────────────────────────────────────────────

def _args_of(a):
    """Every `ast.arg` of an arguments node, in one list."""
    out = list(getattr(a, "posonlyargs", ())) + list(a.args) + list(a.kwonlyargs)
    if a.vararg:
        out.append(a.vararg)
    if a.kwarg:
        out.append(a.kwarg)
    return out


def scope(nodes, params=()):
    """(bound, free) for ONE lexical scope whose body is `nodes`.

    ⚑ PRECISION HERE IS NOT POLISH — AN OVER-APPROXIMATION MANUFACTURES CYCLES.  The cheap
    version of this ("every Name loaded anywhere inside") reports a function whose LOCAL
    variable happens to share a module-level name as depending on that name.  One such false
    edge turns a DAG into a strongly-connected component, and the mode then refuses a split
    that is perfectly legal.  So function, lambda, class and comprehension bodies are each
    treated as their own scope, and a name bound there does not read as a module reference.

    ⚑ THE FIRST ITERABLE OF A COMPREHENSION IS EVALUATED IN THE ENCLOSING SCOPE, and every
    other clause inside it.  Folding the whole comprehension into the inner scope would let a
    target name shadow a genuine outward reference in that first iterable.
    """
    bound, loaded, gdecl, kids = set(params), set(), set(), []

    def walk(n):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bound.add(n.name)
            for d in n.decorator_list:
                walk(d)
            a = n.args
            for d in list(a.defaults) + [x for x in a.kw_defaults if x]:
                walk(d)
            for arg in _args_of(a):
                if arg.annotation:
                    walk(arg.annotation)
            if n.returns:
                walk(n.returns)
            kids.append(scope(n.body, [x.arg for x in _args_of(a)]))
            return
        if isinstance(n, ast.Lambda):
            a = n.args
            for d in list(a.defaults) + [x for x in a.kw_defaults if x]:
                walk(d)
            kids.append(scope([ast.Expr(value=n.body)], [x.arg for x in _args_of(a)]))
            return
        if isinstance(n, ast.ClassDef):
            bound.add(n.name)
            for d in n.decorator_list:
                walk(d)
            for b in n.bases:
                walk(b)
            for k in n.keywords:
                walk(k.value)
            kids.append(scope(n.body))
            return
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            gens = n.generators
            walk(gens[0].iter)
            inner = [ast.Expr(value=x) for x in
                     ([n.key, n.value] if isinstance(n, ast.DictComp) else [n.elt])]
            for g in gens[1:]:
                inner.append(ast.Expr(value=g.iter))
            for g in gens:
                inner.extend(ast.Expr(value=c) for c in g.ifs)
            tgt = {t.id for g in gens for t in ast.walk(g.target) if isinstance(t, ast.Name)}
            kids.append(scope(inner, tgt))
            return
        if isinstance(n, ast.Name):
            (bound if isinstance(n.ctx, (ast.Store, ast.Del)) else loaded).add(n.id)
            return
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for al in n.names:
                bound.add((al.asname or al.name).split(".")[0])
            return
        if isinstance(n, ast.Global):
            # a `global x` write is a MODULE binding performed from inside a body; the split
            # cannot move the writer away from the name, so it is reported as a hazard above
            gdecl.update(n.names)
            loaded.update(n.names)
            return
        if isinstance(n, ast.ExceptHandler):
            if n.name:
                bound.add(n.name)
        for c in ast.iter_child_nodes(n):
            walk(c)

    for s in nodes:
        walk(s)
    free = set(loaded)
    for _kb, kf in kids:
        free |= kf
    return bound, free - (bound - gdecl)


def _uses_file(node):
    """(reads_file, reads_source) — does this statement name `__file__`, and does `__file__`
    ITSELF flow into a source-text read?

    ⚑ THE SECOND HALF MUST BE FLOW-SENSITIVE, AND THE COARSE VERSION WAS USELESS.  The first
    cut asked "does this statement mention `__file__` anywhere AND call `read_text` anywhere",
    which reported 23 of 33 hazards on gcalculus' cotype — and nearly all of them were witnesses
    that use `Path(__file__).parent` to locate the PROJECT and then `read_text()` OTHER files
    under it.  Those relocate safely to a sibling.  A hazard list that is mostly false positives
    is worse than none: it is read once, disbelieved, and then the three real entries in it are
    disbelieved too.  So the subject of each read is examined, not the statement.
    """
    names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
    if "__file__" not in names:
        return False, False
    for c in ast.walk(node):
        if not isinstance(c, ast.Call):
            continue
        subject = None
        if isinstance(c.func, ast.Attribute) and c.func.attr in _TEXT_READS:
            subject = c.func.value
        elif isinstance(c.func, ast.Name) and c.func.id == "open" and c.args:
            subject = c.args[0]
        elif (isinstance(c.func, ast.Attribute)
              and c.func.attr in ("getsource", "getsourcelines", "getsourcefile") and c.args):
            subject = c.args[0]
        if subject is None or not any(isinstance(n, ast.Name) and n.id == "__file__"
                                      for n in ast.walk(subject)):
            continue
        # ⚑ AND `__file__` REACHING A READ IS STILL NOT ENOUGH — WHAT IS READ MUST BE THIS FILE.
        # `(Path(__file__).parent / "concepts.bib").read_text()` reaches a read through
        # `__file__` and reads something else entirely: the parent DIRECTORY is the only thing
        # taken from it, and that is invariant under a sibling emission.  Three of the four
        # hazards this mode first reported on gcalculus' cotype were of exactly that shape, and
        # the one that was real (`_P(__file__).read_text()`, a witness scanning its own source
        # for route keys) was indistinguishable from them.  A path JOIN or a `.parent` in the
        # subject means the read has left this file behind.
        away = any((isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div))
                   or (isinstance(n, ast.Attribute)
                       and n.attr in ("parent", "parents", "with_name", "with_suffix",
                                      "joinpath", "dirname", "replace"))
                   for n in ast.walk(subject))
        if not away:
            return True, True
    return True, False


# ── the statement census ──────────────────────────────────────────────────────────────────────

def statements(path):
    """[(record)] for every TOP-LEVEL statement of one module, with its bindings and its needs.

    Each record is a dict: `i`, `kind`, `name`, `binds`, `free`, `text` (BYTE-IDENTICAL source,
    leading comments and blank lines included), `lines`, `is_import`, `is_docstring`,
    `is_main_guard`, `reads_file`, `reads_source`.

    ⚑ THE TWO PARSES ARE ALIGNED AND THE ALIGNMENT IS CHECKED.  `a = 1; b = 2` is ONE libcst
    `SimpleStatementLine` and TWO `ast` statements, so index-for-index correspondence is an
    assumption, not a fact.  It is asserted rather than assumed: a mode that silently mis-pairs
    would attribute one statement's dependencies to another and emit imports that are wrong in
    a way nothing downstream can see.
    """
    src = open(path, encoding="utf-8").read()
    mod = cst.parse_module(src)
    tree = ast.parse(src)
    if len(mod.body) != len(tree.body):
        raise ValueError(
            f"{path}: libcst sees {len(mod.body)} top-level statements and ast sees "
            f"{len(tree.body)} — a `;`-joined line breaks the correspondence this mode needs")
    wrap = cst.metadata.MetadataWrapper(mod, unsafe_skip_copy=True)
    ranges = wrap.resolve(cst.metadata.PositionProvider)
    out = []
    for i, (cnode, anode) in enumerate(zip(mod.body, tree.body)):
        r = ranges[cnode]
        if not r.start.line <= anode.lineno <= r.end.line:
            raise ValueError(f"{path}: statement {i} does not align between the two parses")
        binds, free = scope([anode])
        rf, rs = _uses_file(anode)
        # ⚑ THE OTHER WAY A STATEMENT NAMES ITS OWN FILE IS AS A STRING, AND IT IS INVISIBLE TO
        # THE `__file__` ANALYSIS ABOVE.  gcalculus' `_p_no_definition_is_shadowed` builds its
        # population as `[root / "concepts.py"] + rglob("gcalc/**")` — a LITERAL basename.  After
        # a split that literal still resolves, still reads, and now covers a 90-line entry module
        # instead of 3,209 lines of witnesses: the shadowing check silently stops looking at 109
        # defs and goes on passing.  A hazard that keeps passing is the only kind worth a mode.
        names_self = any(isinstance(n, ast.Constant) and isinstance(n.value, str)
                         and os.path.basename(path) in n.value for n in ast.walk(anode))
        text = cst.Module(body=[cnode], header=(), footer=()).code
        is_doc = (i == 0 and isinstance(anode, ast.Expr)
                  and isinstance(anode.value, ast.Constant) and isinstance(anode.value.value, str))
        guard = (isinstance(anode, ast.If)
                 and any(isinstance(n, ast.Name) and n.id == "__name__"
                         for n in ast.walk(anode.test)))
        out.append(dict(
            i=i, kind=type(anode).__name__, name=_name_of(anode), binds=binds, free=free,
            text=text, lines=len(text.split("\n")) - 1, is_import=isinstance(
                anode, (ast.Import, ast.ImportFrom)), is_docstring=is_doc, is_main_guard=guard,
            is_future=isinstance(anode, ast.ImportFrom) and anode.module == "__future__",
            is_def=isinstance(anode, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)),
            is_pure=_is_pure(anode), names_self=names_self,
            reads_file=rf, reads_source=rs, start=r.start.line, end=r.end.line))
    return src, mod, out


def _is_pure(anode):
    """Does this top-level statement do nothing but BIND a name?

    ⚑ THE DISTINCTION EXISTS BECAUSE A TOPOLOGICAL SORT WILL HAPPILY REORDER SIDE EFFECTS, AND
    THE COST OF THAT IS SILENT.  gcalculus' cotype ends with two statements that share no name
    dependency in either direction: a `for` loop that POPULATES `ROUTES["shadow"]` from the bib,
    and a comprehension that then DROPS the axis buckets that stayed empty.  Both merely read
    the name `ROUTES`, so a data-flow sort is free to emit them in either order — and emitting
    the pruning first drops every bucket while they are all still empty, after which the
    population writes into a table nothing will read.  The cotype would have come up with ZERO
    shadow routes, every witness would have gone unrun, and the sweep would have reported a
    clean pass over an empty table.  A def, a class, an import and an assignment to a bare name
    are pure; a subscript assignment, a bare call, a loop or a conditional are not, and the
    source order of anything impure is pinned rather than inferred.
    """
    if isinstance(anode, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                          ast.Import, ast.ImportFrom)):
        return True
    if isinstance(anode, ast.AnnAssign):
        return isinstance(anode.target, ast.Name)
    if isinstance(anode, ast.Assign):
        return all(isinstance(t, ast.Name) for t in anode.targets)
    if isinstance(anode, ast.Expr):        # a bare docstring is not a side effect
        return isinstance(anode.value, ast.Constant)
    return False


def _name_of(anode):
    if isinstance(anode, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return anode.name
    if isinstance(anode, (ast.Import, ast.ImportFrom)):
        return "import"
    for t in getattr(anode, "targets", ()) or ([anode.target] if hasattr(anode, "target") else []):
        if isinstance(t, ast.Name):
            return t.value if hasattr(t, "value") else t.id
    return "-"


# ── the plan ──────────────────────────────────────────────────────────────────────────────────

def _components(idxs, deps):
    """[[i, …]] — the strongly-connected components of the statement graph, each in source
    order.  Tarjan, iterated over `sorted(idxs)` so the result is deterministic."""
    live = set(idxs)
    index, low, onstack, stack, out, counter = {}, {}, set(), [], [], [0]

    def strong(v):
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        onstack.add(v)
        for w in sorted(deps.get(v, ())):
            if w not in live:
                continue
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in onstack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.discard(w)
                comp.append(w)
                if w == v:
                    break
            out.append(sorted(comp))

    for v in sorted(idxs):
        if v not in index:
            strong(v)
    return out


def _topo(idxs, deps):
    """The statement graph's SCCs in dependency order, ties broken by SOURCE order.

    ⚑ A CYCLE IS CO-LOCATED, NOT REFUSED — AND THE FIRST CUT GOT THIS WRONG.  It reported any
    cycle as unsplittable, which is over-strict on the single most common shape in a dispatch
    module: `def f(): return T` beside `T = {"k": f}`.  That is a cycle in the reference graph
    and NOT one in Python, because `f`'s reference to `T` is resolved at CALL time.  The mode's
    own selftest is what caught it — the case asserting that an acyclic-in-practice fan-in table
    splits, failing with `'cycle'`.  What the cycle actually forbids is putting the two ends in
    DIFFERENT parts, since the sibling import between them would then be eager and genuinely
    circular.  So the strongly-connected component is the atom of packing.  A cycle is refused
    only when its component cannot fit in one part at all, which is a size fact, not a shape one.

    ⚑ THE TIE-BREAK IS THE READABILITY OF THE RESULT.  Any topological order is correct; the one
    that keeps source neighbours together is the one whose parts still read as sections.
    """
    import heapq
    comps = _components(idxs, deps)
    home = {i: k for k, c in enumerate(comps) for i in c}
    pending = {k: set() for k in range(len(comps))}
    users = {k: set() for k in range(len(comps))}
    for i in idxs:
        for d in deps.get(i, ()):
            if d in home and home[d] != home[i]:
                pending[home[i]].add(home[d])
                users[home[d]].add(home[i])
    ready = [(min(comps[k]), k) for k in pending if not pending[k]]
    heapq.heapify(ready)
    out = []
    while ready:
        _lo, k = heapq.heappop(ready)
        out.append(comps[k])
        for u in sorted(users[k]):
            pending[u].discard(k)
            if not pending[u]:
                heapq.heappush(ready, (min(comps[u]), u))
    return out


def _defcount(ids, by_i):
    """How many TOP-LEVEL DEFINITIONS a part would hold.

    ⚑ THE UNIT IS THE DEFINITION BECAUSE THAT IS WHAT AN ADDITION INVALIDATES.  A Δ-grade cache
    keys each check on the definitions it is sensitive to PLUS a hash of the module's sorted
    qualname SET.  Editing one body invalidates the one check sensitive to that body; ADDING a
    definition changes the qualname set and therefore invalidates EVERY READER of the module —
    by design, since a new definition can change what any reader does.  So a file holding N
    definitions carries N times the blast radius of an addition, and a LINE bound cannot see
    that: 8 definitions in 143 lines is fully compliant on lines and is the worst case here.
    The two bounds are independent and a part must satisfy BOTH — measured on this corpus, a
    1156-line module with 8 defs (one 316-line body) passes a def bound and fails lines, while
    a 143-line module with 8 defs passes lines and fails defs.  Neither subsumes the other.
    """
    return sum(1 for i in ids if by_i[i]["is_def"])


def plan(path, max_lines=1200, max_defs=None, prefix=None, keep=(), export="public"):
    """The parts a split WOULD produce — the whole decision, before anything is written.

    ⚑ `max_defs` COMPOSES WITH `max_lines`, IT DOES NOT REPLACE IT.  `--max` keeps its meaning
    exactly; a part is committed only while it is under BOTH bounds.  See `_defcount` for why
    the definition count is the quantity an ADDITION's blast radius is proportional to, and why
    a line bound is structurally blind to it.  `None` means unbounded, so every existing caller
    and every existing plan is unchanged by construction.

    ⚑ THE HEADER COST IS PART OF THE BUDGET, AND A RESERVE CANNOT STAND IN FOR IT.  A part's
    `from <sibling> import` block depends on which statements landed elsewhere, so packing
    against a guessed reserve reports parts under the bound and writes them over it — the
    off-by-a-header that makes a size gate go red on the output of the very tool that exists to
    satisfy it.  Measured here: `_CONTENT`, a 86-line table naming 75 witnesses, needs a 97-line
    import header, so its part came out at 183 against a bound of 150 while every reserve-based
    estimate said it fit.

    ⚑ AND THE FIX IS NOT A BIGGER RESERVE — IT IS PACKING IN TOPOLOGICAL ORDER, WHICH MAKES THE
    COST EXACT.  A statement's header contribution is decided by where its DEPENDENCIES live,
    and in topological order every dependency is already placed.  So each candidate part can be
    RENDERED before it is committed, and the bound is checked against the real bytes rather than
    against an estimate.  A first pass shrank the rooms globally on retry, which is exactly
    backwards for a header-dominated part: smaller rooms mean more parts, more parts mean more
    `from <sibling> import` lines, and the one statement that did not fit fit less well each
    time.  A single statement that cannot fit ALONE is a refusal, and it names the statement.
    """
    src, mod, tops = statements(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    prefix = prefix or f"{stem}_"
    keep = set(keep)

    binder = {}
    twice = {}
    for t in tops:
        for n in t["binds"]:
            if n in binder and not t["is_import"] and not tops[binder[n]]["is_import"]:
                twice.setdefault(n, [binder[n]]).append(t["i"])
            binder[n] = t["i"]

    imports = [t for t in tops if t["is_import"]]
    futures = [t for t in imports if t["is_future"]]
    doc = next((t for t in tops if t["is_docstring"]), None)
    guard = [t for t in tops if t["is_main_guard"]]

    # THE PREFIX IS PINNED.  Everything before the first def/class is module SET-UP whose order
    # is semantic (`sys.path.insert` must precede the imports it enables) and which binds
    # nothing a later statement can be ordered against.  It becomes part 00 verbatim.
    first_def = next((t["i"] for t in tops if t["is_def"]), len(tops))
    base = [t for t in tops if t["i"] < first_def and not t["is_docstring"]]
    entry_ids = {t["i"] for t in guard} | {t["i"] for t in tops if t["name"] in keep}
    movable = [t for t in tops
               if t["i"] >= first_def and not t["is_import"] and t["i"] not in entry_ids]

    provider = {n: i for n, i in binder.items()
                if not tops[i]["is_import"] and not tops[i]["is_docstring"]}
    deps = {t["i"]: {provider[n] for n in t["free"] if n in provider and provider[n] != t["i"]}
            for t in tops}
    # ⚑ SIDE EFFECTS ARE PINNED TO SOURCE ORDER; DATA FLOW ALONE DOES NOT ORDER THEM.  See
    # `_is_pure` for the measured case this exists to prevent.  The edge is added only where an
    # IMPURE statement shares a module-level name with another statement, so the pin is as
    # narrow as the hazard: two impure statements about different tables stay independent.  Every
    # such edge runs from the lower source index to the higher, so no edge added here can close
    # a cycle with another one — only a genuine backwards data dependency can, and that is
    # reported as the refusal it is rather than emitted.
    for a in tops:
        if a["is_pure"]:
            continue
        touch_a = (a["binds"] | a["free"]) & set(provider)
        for b in tops:
            if b["i"] == a["i"] or not touch_a & ((b["binds"] | b["free"]) & set(provider)):
                continue
            lo, hi = sorted((a["i"], b["i"]))
            deps[hi].add(lo)
    # the pinned prefix is one unit: a movable statement depending on ANY of it depends on 00
    base_ids = {t["i"] for t in base}
    groups = _topo([t["i"] for t in movable],
                   {i: {d for d in ds if d not in base_ids} for i, ds in deps.items()})
    for t in movable:      # a part may not depend on a statement kept in the entry module
        if deps[t["i"]] & entry_ids:
            return dict(path=path, error="entry-dep", tops=tops,
                        scc=[t["name"]] + [tops[d]["name"] for d in deps[t["i"]] & entry_ids])

    by_i = {t["i"]: t for t in tops}
    ctx = dict(by_i=by_i, tops=tops, provider=provider, futures=futures, prefix=prefix,
               origin=os.path.basename(path))
    parts = [[t["i"] for t in base]]
    home = {t["i"]: 0 for t in base}
    cur, pi = [], 1
    for grp in groups:
        trial = cur + list(grp)
        # BOTH bounds gate the commit.  The line bound must be measured on the RENDERED part
        # (the sibling-import header is part of the budget); the def bound is a property of the
        # statements alone, so it needs no render — but it is checked in the same place, because
        # a part that satisfies one and not the other is not a legal part.
        too_big = (_size(_render_part(pi, trial, home, ctx)) > max_lines
                   or (max_defs is not None and _defcount(trial, by_i) > max_defs))
        if too_big and cur:
            parts.append(cur)
            pi, cur = pi + 1, list(grp)
        else:
            cur = trial
        for i in grp:
            home[i] = pi
    if cur:
        parts.append(cur)
    rendered = _render_all(path, mod, tops, parts, prefix, doc, guard, export,
                           futures, provider, entry_ids, ctx)
    over = [(n, _size(c)) for n, c in sorted(rendered.items()) if _size(c) > max_lines]
    # ⚑ A DEF-BOUND OVERRUN IS REPORTED AS A REFUSAL LIKE ANY OTHER, AND IT NAMES THE PART.  An
    # SCC holding more definitions than the bound allows cannot be packed at all — the component
    # travels together by construction — so this is the def-side twin of the single-statement
    # size refusal, and the repair is likewise an authoring act (break the cycle) not a move.
    if max_defs is not None and not over:
        for pi_, ids_ in enumerate(parts):
            if _defcount(ids_, by_i) > max_defs:
                return dict(path=path, error="budget", tops=tops, prefix=prefix, parts=parts,
                            files=rendered,
                            over=[(f"{prefix}{pi_:02d}.py", _size(rendered[f"{prefix}{pi_:02d}.py"]))],
                            detail=[(f"{prefix}{pi_:02d}.py", _defcount(ids_, by_i), 0,
                                     [(by_i[j]["name"], by_i[j]["lines"]) for j in ids_
                                      if by_i[j]["is_def"]])])
    if not over:
        return dict(path=path, error=None, tops=tops, parts=parts, prefix=prefix,
                    files=rendered, twice=twice, groups=groups,
                    hazards=[t for t in tops if t["reads_file"]],
                    selfnamed=[t for t in tops
                               if t["names_self"] and not t["is_docstring"]])
    # ⚑ THE REFUSAL MUST NAME THE STATEMENT, NOT THE FILE.  "concepts_37.py is 183 lines" is a
    # fact about the OUTPUT and leaves the reader to re-derive which body caused it — the same
    # census-names-a-defect-it-cannot-help-you-fix shape `--layout` was written to close one
    # level up.  What the caller needs is the part's composition and its HEADER cost, which is
    # the half a line count hides: a part goes over because one def is too big OR because its
    # sibling imports are, and those are different repairs.
    detail = []
    for name, n in over:
        ids = next((p for k, p in enumerate(parts)
                    if f"{prefix}{k:02d}.py" == name), None)
        body = sum(by_i[j]["lines"] for j in ids) if ids else 0
        detail.append((name, n, n - body,
                       [(by_i[j]["name"], by_i[j]["lines"]) for j in (ids or ())]))
    return dict(path=path, error="budget", tops=tops, over=over, detail=detail,
                parts=parts, files=rendered, prefix=prefix)


def _size(code):
    """The line count a SIZE GATE sees — `len(text.split("\\n"))`, trailing newline included.

    ⚑ COUNTED THE GATE'S WAY, NOT THE OBVIOUS WAY.  `splitlines()` and `split("\\n")` differ by
    one on every file that ends in a newline, i.e. on every file.  A splitter that plans against
    one count and is judged against the other is off by exactly one on every part it writes —
    invisible until the bound is tight, and then wrong on all of them at once.
    """
    return len(code.split("\n"))


def _wrap_import(module, names, tail="", width=98):
    """`from <module> import …`, hanging-indented, deterministic in name order.

    ⚑ THE IMPORT BLOCK IS PART OF THE BUDGET, SO ITS SHAPE IS A CORRECTNESS QUESTION AND NOT A
    STYLE ONE.  A four-line-per-sibling form (`from X import (` / names / `)` / blank) spends
    two lines of pure punctuation per source part.  `_CONTENT` — one 86-line table naming 75
    witnesses spread over twenty parts — paid FORTY of them, and its part came out at 170 lines
    against a bound of 150: the split was refused by its own formatting.  The hanging-indent
    form spends the punctuation once per sibling instead of thrice, which is the difference
    between a legal packing and none.
    """
    one = f"from {module} import {', '.join(sorted(names))}{tail}\n"
    if len(one) <= width + 1:
        return one
    lead = f"from {module} import ("
    body = textwrap.fill(", ".join(sorted(names)), width=width,
                         initial_indent=" " * len(lead),
                         subsequent_indent=" " * len(lead))[len(lead):]
    return f"{lead}{body}){tail}\n"


def _render_part(pi, ids, home, ctx):
    """One part's full source.  `home` need only cover statements EARLIER in topological
    order, which is exactly what makes an incremental, exact packing possible."""
    by_i, tops, provider = ctx["by_i"], ctx["tops"], ctx["provider"]
    prefix = ctx["prefix"]
    imported_names = {b for t in tops if t["is_import"] for b in t["binds"]}
    binds = set().union(*[by_i[i]["binds"] for i in ids]) if ids else set()
    need_import, need_part = set(), {}
    for i in ids:
        for n in by_i[i]["free"]:
            if n in binds:
                continue
            j = provider.get(n)
            if j is not None and home.get(j) is not None and home[j] != pi:
                need_part.setdefault(home[j], set()).add(n)
            elif n in imported_names:
                need_import.add(n)
    # ⚑ TWO LINES, NOT FIVE, AND THE ARITHMETIC IS THE REASON.  A generated header is paid once
    # per part, so a five-line docstring spends 135 lines across a 27-part split — and it spends
    # them out of the budget of the tightest part, which is the one holding the biggest def.  On
    # gcalculus' cotype the three lines saved here were the three that let the size-gate witness
    # itself (a 135-line body) carry its own registration and still fit under 150.
    head = [f'"""{prefix}{pi:02d}.py — part {pi:02d} of {ctx["origin"]}, cut by '
            f'`pycodemod.py --split`.  Statements\nbelow are BYTE-IDENTICAL to their originals; '
            f'the bound is INHERITED, not reset."""\n']
    for f in ctx["futures"]:
        head.append(f["text"].lstrip("\n"))
    for t in tops:
        if t["is_import"] and not t["is_future"] and t["binds"] & need_import:
            head.append(t["text"].lstrip("\n"))
    for j in sorted(need_part):
        head.append(_wrap_import(f"{prefix}{j:02d}", need_part[j]))
    return "".join(head) + "".join(by_i[i]["text"] for i in ids)


def _render_all(path, mod, tops, parts, prefix, doc, guard, export,
                futures, provider, entry_ids, ctx):
    """{filename: full source} for every part AND the rewritten entry module."""
    by_i = {t["i"]: t for t in tops}
    home = {}                               # statement index -> the part that now owns it
    for pi, ids in enumerate(parts):
        for i in ids:
            home[i] = pi
    names = [f"{prefix}{pi:02d}" for pi in range(len(parts))]
    out = {}
    for pi, ids in enumerate(parts):
        out[names[pi] + ".py"] = _render_part(pi, ids, home, ctx)
    # ── the entry module: docstring, what it keeps, and the re-exports ────────────────────
    head = cst.Module(body=[], header=mod.header, footer=()).code
    if doc is not None:
        head += doc["text"]
    kept = [t for t in tops if t["i"] in entry_ids]
    kept_free = set().union(*[t["free"] for t in kept]) if kept else set()
    surface = set()
    for n, j in provider.items():
        if home.get(j) is None:
            continue
        # ⚑ `--export` ADDS TO THE PUBLIC SURFACE, IT DOES NOT REPLACE IT.  Read as a
        # replacement, naming one private name to keep (`--export _CONTENT`) would silently drop
        # every public one — a re-export list that looks deliberate and is a truncation.  The
        # public names are the module's contract whatever else is asked for.
        if export == "all" or not n.startswith("_") or n in export:
            surface.add(n)
    surface |= {n for n in kept_free if n in provider and home.get(provider[n]) is not None}
    pieces = [head]
    for f in futures:
        pieces.append(f["text"].lstrip("\n"))
    for t in tops:
        if t["is_import"] and not t["is_future"] and t["binds"] & kept_free:
            pieces.append(t["text"].lstrip("\n"))
    # ⚑ EVERY PART IS IMPORTED, WHETHER OR NOT THE ENTRY NEEDS A NAME FROM IT.  A part's
    # module-level statements are its SIDE EFFECTS, and a part nothing imports never runs.
    # gcalculus' cotype populates `ROUTES["shadow"]` from the bib in a module-level `for` loop;
    # had that loop landed in a part whose every binding is private, the entry would have
    # imported nothing from it, the loop would never have executed, and `ROUTES` would have
    # carried an EMPTY shadow family — a table that resolves nothing while every gate reports a
    # clean sweep over it.  An unreferenced import is a lint complaint; a part that never runs
    # is a silent behaviour change, so the import is unconditional and says why.
    for pi in range(len(parts)):
        mine = {n for n in surface if home.get(provider[n]) == pi}
        if mine:
            pieces.append(_wrap_import(names[pi], mine, tail="  # noqa: F401"))
        else:
            pieces.append(f"import {names[pi]}  # noqa: F401  — imported for its "
                          f"module-level effects\n")
    pieces.append("".join(t["text"] for t in kept))
    pieces.append(cst.Module(body=[], header=(), footer=mod.footer).code)
    out[os.path.basename(path)] = "".join(pieces)
    return out


# ── applying it, and the evidence that it was lossless ────────────────────────────────────────

def verify(path, p):
    """(ok, detail) — is the SET of relocated statements byte-identical to the original's?

    ⚑ `--roundtrip` STRUCTURALLY CANNOT ANSWER THIS AND SAYS SO.  Losslessness is per file:
    both halves of a split round-trip green while a block that explained a moved def is gone.
    The question a decomposition asks is whether the MULTISET of top-level statement texts
    survived the move, which is a set question across a GROUP of files — so it is checked here,
    on the rendered output, before anything is written.
    """
    from collections import Counter
    want = Counter(t["text"] for t in p["tops"] if not t["is_docstring"])
    got = Counter()
    for fname, code in p["files"].items():
        for t in statements_from_source(code):
            got[t] += 1
    missing = sorted((want - got).elements())
    extra = 0
    for t in (got - want).elements():
        extra += 1
    if missing:
        return False, f"{len(missing)} original statement(s) not reproduced byte-for-byte"
    return True, f"{sum(want.values())} statement(s) reproduced byte-for-byte ({extra} generated)"


def statements_from_source(code):
    """The byte-exact text of every top-level statement of `code`, as a list."""
    m = cst.parse_module(code)
    return [cst.Module(body=[s], header=(), footer=()).code for s in m.body]


def apply_plan(p):
    """Write the plan.  Returns [(filename, lines, written)] — the parent LAST, so a crash
    mid-write leaves the original intact and the siblings merely unreferenced."""
    d = os.path.dirname(os.path.abspath(p["path"]))
    rows = []
    order = [n for n in p["files"] if n != os.path.basename(p["path"])]
    for name in order + [os.path.basename(p["path"])]:
        code = p["files"][name]
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write(code)
        rows.append((name, len(code.split("\n")), True))
    return rows


def _print_split(path, max_lines, prefix, keep, export, apply_it, max_defs=None):
    p = plan(path, max_lines=max_lines, max_defs=max_defs, prefix=prefix, keep=keep, export=export)
    rel = os.path.relpath(path, _c.ROOT)
    if p["error"] == "entry-dep":
        print(f"── {rel}: REFUSED — a part would depend on a statement kept in the entry module")
        print("   " + ", ".join(p["scc"][:12]))
        return 1
    if p["error"] == "budget":
        print(f"── {rel}: REFUSED — no packing fits {max_lines} lines")
        for name, n, head, comp in p["detail"]:
            print(f"   {name:<28} {n:>5} lines = {head} header + {n - head} body")
            for nm, ln in comp:
                print(f"        {ln:>5}  {nm}")
        print("   ⚑ relocation cannot shrink a body.  If the part above holds ONE statement, that\n"
              "     body must be decomposed first — an authoring act, not a move.  If it holds\n"
              "     several, they are a strongly-connected component that has to travel together,\n"
              "     and the cycle between them is what has to go.")
        return 1
    bound = f"bound {max_lines} lines" + (f", {max_defs} defs" if max_defs is not None else "")
    print(f"── {rel} → {len(p['parts'])} part(s) + the entry module, {bound}")
    by_i = {t["i"]: t for t in p["tops"]}
    for name in sorted(p["files"]):
        code = p["files"][name]
        n = len(code.split("\n"))
        ids = None
        for pi, part in enumerate(p["parts"]):
            if name == f"{p['prefix']}{pi:02d}.py":
                ids = part
        what = (", ".join(p["tops"][i]["name"] for i in ids[:3]) + (" …" if len(ids) > 3 else "")
                if ids else "the entry module — docstring, re-exports, __main__")
        nd = _defcount(ids, by_i) if ids else 0
        flag = "  ⚑ OVER" if (n > max_lines or (max_defs is not None and nd > max_defs)) else ""
        print(f"  {name:<22} {n:>4} lines  {len(ids) if ids else 0:>3} stmt  "
              f"{nd:>2} def  {what}{flag}")
    ok, detail = verify(path, p)
    print(f"  {'LOSSLESS' if ok else 'LOSSY':<10} {detail}")
    if p["twice"]:
        print(f"  ⚑ {len(p['twice'])} name(s) bound by more than one top-level statement: "
              + ", ".join(sorted(p["twice"])))
    haz = [t for t in p["hazards"] if t["reads_source"]]
    if p["hazards"]:
        print(f"  ⚑ {len(p['hazards'])} statement(s) read `__file__`; {len(haz)} of them read it "
              f"as SOURCE TEXT.  Only those are hazards — a DIRECTORY read is invariant under\n"
              f"     a sibling emission, which is why the parts are siblings.")
        for t in haz:
            print(f"       SOURCE  {rel}:{t['start']}  {t['name']}")
        if haz:
            print("     ⚑ a SOURCE-TEXT read does not survive a split: the part sees only its own\n"
                  "       share, so the scan SHRINKS and still passes.  Widen it to the sibling set\n"
                  "       BY HAND — this mode will not guess what population was meant.")
    if p["selfnamed"]:
        print(f"  ⚑ {len(p['selfnamed'])} statement(s) name {os.path.basename(path)!r} as a "
              f"STRING LITERAL — same hazard, different\n     spelling: the literal still "
              f"resolves after the split and now covers the entry module only.")
        for t in p["selfnamed"]:
            print(f"       LITERAL {rel}:{t['start']}  {t['name']}")
    if apply_it:
        for name, n, _w in apply_plan(p):
            print(f"  WROTE  {name:<22} {n:>4} lines")
    else:
        print("   (plan only — pass `--apply` to write it)")
    return 0 if ok else 1
