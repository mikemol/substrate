#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""qualify_imports.py — rewrite `from x import y` into `import x` + qualified uses.

⚑ WHY THIS EXISTS AND WHY IT IS NOT `RenameCommand`.  The operator's ruling: `from x import y`
IS what lacking a bare import looks like in python — it SELECTS names out of a module and binds
them where the definition site carries `x.y`, which is exactly agda's `open import M using (y)`.
So `import x` is the compliant form and this is the paydown tool.  `pycodemod.py:31` names
`libcst`'s `rename.RenameCommand` as the twin of `scratch/rename_at_source.py`, and reaching for
it here was the obvious first move.  IT CANNOT DO THIS TRANSFORM, and it does not say so:

    python3 -m libcst.tool codemod -x libcst.codemod.commands.rename.RenameCommand \\
        --old_name=strip --new_name=_agdatext.strip scripts/law_motif_apex.py
    → "Transformed 1 files successfully"   … and a ZERO diff.

`RenameCommand` resolves QUALIFIED names; a bare name bound by `from … import` is not one, so it
matched nothing and reported success anyway.  Acting on that message would have banked a paydown
that never happened — the false-positive-in-a-query-you-act-on class this toolkit calls a bug
rather than a caveat.  Measured before building, which is the only reason it was caught.

⚑ THE TRANSFORM IS SCOPE RESOLUTION, NOT SUBSTITUTION, and that is the whole content.  For
`scripts/law_motif_apex.py` (1 import, 14 call sites) the change is:

    from _agdatext import strip     →    import _agdatext
    strip(x)                        →    _agdatext.strip(x)

but NOT `s.strip()` (a method on a str), NOT a local variable named `strip`, NOT the string
`"strip"`.  Each of those is a bare `strip` token that a regex would rewrite and a scope-aware
pass must not.  `libcst`'s `ScopeProvider` answers exactly this — for each `Name` node, which
Assignment binds it — so this conforms to the library rather than rebuilding its core
(feedback_fix_infra_not_route_around).

⚑ SHADOWING IS A REFUSAL, NOT A GUESS.  If a file binds the same name BOTH by the import and by
something else (a parameter, a local, a def), the occurrences are not interchangeable and no
single rewrite is correct.  This refuses that file and names the shadowing site.  A tool that
guessed here would produce a plausible diff that changes behaviour, which is worse than none.

Usage:
    qualify_imports.py <file.py> [...]            # report the plan, write nothing
    qualify_imports.py <file.py> --apply          # rewrite in place
    qualify_imports.py <file.py> --module <name>  # only this module's imports
    qualify_imports.py <file-or-dir> … --refused  # HOW MUCH OF THE CORPUS THIS TOOL CANNOT TOUCH
                                                  # — the refusal population as a QUERY, not a
                                                  # guess. `_local_import_conflicts` was added
                                                  # after ONE file broke the toolkit, and how
                                                  # much it excludes was unmeasured, which makes
                                                  # every paydown estimate downstream unreliable.
                                                  # A refusal that silently shrinks the reachable
                                                  # set is a census that cannot see its own gaps.
                                                  # ⚑ Directory arguments EXPAND, and the output
                                                  # carries an `(of N file(s) read)` denominator:
                                                  # the first cut took only file paths, so a
                                                  # directory printed "0 refused" — a FALSE ZERO
                                                  # in the reassuring direction, from the mode
                                                  # built to make this population measurable.
    qualify_imports.py --selftest
"""
import os
import sys

# ⚑ BARE IMPORTS, INCLUDING THE SUBMODULES — this tool would otherwise be the first offender
# against the policy it implements. `libcst.matchers` and `libcst.metadata` are separate
# modules and each needs its own `import`; attribute access off `libcst` alone raises
# AttributeError, which is how the omission announced itself on the first run.
import libcst
import libcst.matchers
import libcst.metadata


def _as_imports(tree, only=None):
    """[(node, module, alias)] for each `import x as q` — the AS-MOD form.

    ⚑ A DIFFERENT TRANSFORM FROM THE `from` CASE, and conflating them would get both wrong.
    `from x import y` changes the IMPORT FORM (selecting → whole-module) and every use site
    gains a qualifier.  `import x as q` already takes the module whole — only the LABEL is
    wrong — so the repair is to drop the alias and respell `q.name` as `x.name`.  Same policy
    (the name a consumer writes is the name the definition carries), different edit.
    """
    out = []
    for node in libcst.matchers.findall(tree, libcst.matchers.Import()):
        for alias in node.names:
            if alias.asname is None:
                continue
            mod = libcst.Module(body=()).code_for_node(alias.name)
            if only and mod != only:
                continue
            out.append((node, mod, alias.asname.name.value))
    return out


def _dotted(name):
    """`a.b.c` as a libcst node — a Name for one segment, nested Attributes beyond.

    ⚑ A DOTTED MODULE IS NOT A `Name`, and constructing one directly emits a module whose
    "identifier" contains dots — which libcst accepts into the tree and python then rejects
    at parse. `jea.metalanguage.store` is a real import in this corpus, so the multi-segment
    case is the norm here, not an edge.
    """
    parts = name.split(".")
    node = libcst.Name(parts[0])
    for p in parts[1:]:
        node = libcst.Attribute(value=node, attr=libcst.Name(p))
    return node


def _from_imports(tree, only=None):
    """[(node, module, {bound_name: original_name})] for each module-or-function `from x import`.

    ⚑ RELATIVE IMPORTS ARE SKIPPED, NOT REWRITTEN.  `from . import y` has no module NAME to
    qualify with — `..y` is not an expression — so the compliant form is a different edit
    (naming the package) and guessing it here would be inventing a module path.
    """
    out = []
    for node in libcst.matchers.findall(tree, libcst.matchers.ImportFrom()):
        if node.relative or node.module is None:
            continue
        if isinstance(node.names, libcst.ImportStar):
            continue
        mod = libcst.Module(body=()).code_for_node(node.module)
        if only and mod != only:
            continue
        bound = {}
        for alias in node.names:
            orig = libcst.Module(body=()).code_for_node(alias.name)
            # `from x import y as z` binds z; the qualified form is still x.y.
            bound[alias.asname.name.value if alias.asname else orig] = orig
        out.append((node, mod, bound))
    return out


class _Qualify(libcst.CSTTransformer):
    """Rewrite the bound names this import introduced, and the import itself."""

    METADATA_DEPENDENCIES = (libcst.metadata.ScopeProvider,)

    def __init__(self, plan, attr_names, import_ids,
                 alias_plan=None, as_import_ids=None, as_modules=None):
        # plan: {bound_name: (module, original_name)}   — the `from x import y` case
        # alias_plan: {alias: module}                   — the `import x as q` case
        # attr_names: ids of Name nodes that are an Attribute's `.attr` — never free
        # import_ids / as_import_ids: the import nodes being rewritten, by identity
        self.plan = plan
        self.attr_names = attr_names
        self.import_ids = import_ids
        self.alias_plan = alias_plan or {}
        self.as_import_ids = as_import_ids or set()
        self.as_modules = as_modules or set()
        self.rewrites = 0

    def leave_ImportFrom(self, orig, updated):
        # ⚑ THE IMPORT BECOMES `import <module>`, and the modules come from the PLAN rather
        # than from this node, so `from x import a, b` collapses to one `import x` instead of
        # one per name.
        if id(orig) not in self.import_ids:
            return updated
        mod = libcst.Module(body=()).code_for_node(orig.module)
        return libcst.Import(names=[libcst.ImportAlias(name=_dotted(mod))])

    def leave_Import(self, orig, updated):
        # ⚑ `import x as q` → `import x`: drop the alias, keep the module. Only the aliases
        # this run planned — an `import numpy as np` in the same statement is untouched.
        #
        # ⚑ Ⓧ4′ — THE TRAILING COMMENT IS REALIGNED, and the shrink is exactly computable so
        # this is arithmetic rather than reflow. Dropping ` as _store` shortens the code by
        # len(" as ") + len(alias); adding that many spaces back before the comment restores
        # the column it was written at. The comment itself is never touched.
        #
        # ⚑ THE WHITESPACE BELONGS TO THE ENCLOSING `SimpleStatementLine`, NOT TO THIS NODE —
        # which is why the first cut left it drifting and I filed it as needing "whole-block
        # column tracking". It doesn't: libcst attaches the trailing comment (and the
        # whitespace before it) to the statement line, so `leave_SimpleStatementLine` can
        # widen it by the delta this method recorded. Per-node after all, once the node is
        # the right one.
        #
        # ⚑ REALIGN ONLY, NEVER INTRODUCE. A line with no trailing comment gets nothing, and
        # a comment that was NOT column-aligned (a single space before `#`) is left at its
        # single space — widening that would invent an alignment the author did not choose.
        if id(orig) not in self.as_import_ids:
            return updated
        names = []
        shrunk = 0
        for alias in updated.names:
            mod = libcst.Module(body=()).code_for_node(alias.name)
            if alias.asname is not None and mod in self.as_modules:
                # ⚑ `code_for_node(asname)` RENDERS THE WHOLE CLAUSE — measured: `' as _store'`,
                # length 10, keyword and leading space included. NOT `asname.name.value`
                # (`'_store'`, 6), which would leave the column 4 short. Verified rather than
                # assumed: the first alignment probe came out exact, and a correct result from
                # an unchecked premise is worth less than the check.
                shrunk += len(libcst.Module(body=()).code_for_node(alias.asname))
                names.append(libcst.ImportAlias(name=alias.name))
            else:
                names.append(alias)
        if shrunk:
            self._pending_shrink = shrunk
        # `ImportAlias` carries its own trailing comma; rebuilding the list drops the last
        # one, which libcst requires to be absent on the final element anyway.
        return updated.with_changes(names=names)

    def leave_SimpleStatementLine(self, orig, updated):
        """Widen the gap before a trailing comment by exactly what the alias drop removed."""
        shrink = getattr(self, "_pending_shrink", 0)
        self._pending_shrink = 0
        if not shrink:
            return updated
        tw = updated.trailing_whitespace
        if tw is None or tw.comment is None:
            return updated
        ws = tw.whitespace
        # ⚑ ONLY A COLUMN-ALIGNED COMMENT. A single space before `#` is prose spacing, not an
        # alignment, and padding it would invent a column the author never chose. Two or more
        # spaces is the signal that the author aligned it to something.
        if not isinstance(ws, libcst.SimpleWhitespace) or len(ws.value) < 2:
            return updated
        return updated.with_changes(
            trailing_whitespace=tw.with_changes(
                whitespace=libcst.SimpleWhitespace(ws.value + " " * shrink)))

    def leave_Name(self, orig, updated):
        # ⚑ AN ALIAS RESPELL IS A *NAME* SUBSTITUTION, NOT A QUALIFICATION — `_store.connect`
        # becomes `store.connect`, so the Name node is replaced in place rather than wrapped
        # in an Attribute.
        #
        # ⚑⚑ AND IT NEEDS THE SAME SCOPE CHECK AS THE `from` ARM. My first cut skipped it on
        # the reasoning that "an alias is unambiguous within its file" — FALSE, and measured
        # false on the first real target. `autocorr_synth.py` imports `store as _s` at module
        # scope AND uses `_s` as a tuple-unpacking LOOP VARIABLE in four comprehensions:
        #     for _s, name, sz_ in run:        →  for store, name, sz_ in run:
        # which rebinds the module name inside the loop and silently changes behaviour. Short
        # aliases (`_s`, `_D`, `_V`) collide with locals constantly. Unambiguous at MODULE
        # scope is not unambiguous in the FILE, and the diff was the only witness.
        if orig.value in self.alias_plan:
            if id(orig) in self.attr_names:
                return updated
            try:
                scope = self.get_metadata(libcst.metadata.ScopeProvider, orig)
            except KeyError:
                return updated
            if scope is None:
                return updated
            # ⚑⚑ EXCLUSIVELY THE IMPORT — `any()` IS NOT ENOUGH, AND THE WEAKER TEST BROKE THE
            # TOOLKIT'S OWN SELFTEST. `_pycodemod_selftest.py` imports `_pycodemod_core as _c`
            # at module scope AND assigns `_c` as a local FIFTEEN times inside `_selftest`
            # (tuple-unpacking throwaways: `for _p, _l, v, _c, _n in rv`). ScopeProvider then
            # reports BOTH the import and the local for the same name, so `any(... Import)`
            # passed and the reads were rewritten — producing
            #     UnboundLocalError: cannot access local variable '_pycodemod_core'
            # because python treats a name assigned anywhere in a function as local THROUGHOUT,
            # including before the assignment. The file was restored from the edit_snapshot
            # commit and the suite went back to 383/383.
            #
            # ⚑ SAME CLASS AS THE `store as _s` LOOP-VARIABLE CORRUPTION, one form deeper: there
            # the local shadowed in a comprehension, here it coexists with the import in one
            # function. Fixing the first taught me to check the scope; it did not teach me to
            # check that the scope is UNAMBIGUOUS. A name bound two ways has no single correct
            # rewrite, so this refuses it — the same rule the `from`-arm's `shadowed` list
            # already applies at plan time.
            _asgs = list(scope[orig.value])
            if not _asgs or not all(isinstance(getattr(a, "node", None), libcst.Import)
                                    for a in _asgs):
                return updated
            self.rewrites += 1
            return _dotted(self.alias_plan[orig.value])
        if orig.value not in self.plan:
            return updated
        # ⚑ AN ATTRIBUTE'S `.attr` IS NOT A FREE NAME, and libcst hands a transformer the node
        # without its parent — so `s.strip()` arrives here as a bare `strip` and would become
        # `s._agdatext.strip()`. Collected up front and matched by IDENTITY.
        if id(orig) in self.attr_names:
            return updated
        # ⚑ ONLY A NAME THE IMPORT BOUND. `ScopeProvider` gives the assignments a Name resolves
        # to; if none of them is our ImportFrom, this occurrence means something else and must
        # be left alone. That is the `s.strip()` / local-variable case, and it is the reason
        # this pass exists rather than a substitution.
        try:
            scope = self.get_metadata(libcst.metadata.ScopeProvider, orig)
        except KeyError:
            return updated
        if scope is None:
            return updated
        assignments = scope[orig.value]
        if not any(isinstance(getattr(a, "node", None), libcst.ImportFrom)
                   for a in assignments):
            return updated
        module, original = self.plan[orig.value]
        self.rewrites += 1
        return libcst.Attribute(value=_dotted(module), attr=libcst.Name(original))


def _attr_context(tree):
    """The `Name` nodes that are an Attribute's `attr` — `s.strip` is not a free `strip`.

    ⚑ A SEPARATE PASS BECAUSE `leave_Name` CANNOT SEE ITS PARENT.  libcst hands a transformer
    the node, not its context, so `s.strip()` would otherwise reach `leave_Name` as a bare
    `strip` and be rewritten to `s._agdatext.strip()`. Collected up front and matched by
    identity, which is exact where a value comparison would over-match.
    """
    out = set()
    for node in libcst.matchers.findall(tree, libcst.matchers.Attribute()):
        out.add(id(node.attr))
    return out


def _local_import_conflicts(tree, only=None):
    """[(module, alias)] — modules imported INSIDE a function under an alias.

    ⚑ THE REFUSAL THIS EXISTS FOR, and it is not a scope-resolution question — it is a
    consequence of python's function-local rule that no per-name analysis can see. Rewriting
    `import X as _alt` (function-scoped) to a bare `import X` binds X LOCALLY for that whole
    function; any read of `X.attr` EARLIER in the same function — including one this tool just
    created by qualifying a `from`-bound name — becomes a read-before-assignment.

        UnboundLocalError: cannot access local variable 'X' where it is not associated with a value

    RECOVERED BY `symtable` after two wrong reconstructions (comprehension shadowing, refuted;
    "an aliased import makes the module name local", refuted by hand — `import X as _alt` binds
    `_alt`). The decisive reading was `local=True assigned=False imported=True` for the module
    name inside the function. `compile()` ACCEPTS the broken output; only executing it fails,
    which is why a parse check and a compile check both passed over it.

    So the two arms are individually correct and JOINTLY unsafe on one file. A file carrying
    both shapes has no single safe rewrite, and this is what makes the plan refuse it.
    """
    out = []
    # ⚑ ONE MATCHER COVERS BOTH — libcst models `async def` as a `FunctionDef` carrying an
    # `asynchronous` field, not as a separate node type. My first cut asked for
    # `matchers.AsyncFunctionDef` and got AttributeError.
    for fn in libcst.matchers.findall(tree, libcst.matchers.FunctionDef()):
        for node in libcst.matchers.findall(fn, libcst.matchers.Import()):
            for alias in node.names:
                if alias.asname is None:
                    continue
                mod = libcst.Module(body=()).code_for_node(alias.name)
                if only and mod != only:
                    continue
                out.append((mod, alias.asname.name.value))
    return out


def plan_file(path, only=None):
    """(module_binds, shadowed, imports) — what this file's `from` imports would become.

    Returns `shadowed` non-empty when a name is bound by BOTH the import and something else;
    the caller must refuse rather than rewrite.
    """
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    tree = libcst.parse_module(src)
    froms = _from_imports(tree, only)
    binds, shadowed = {}, []
    for _node, mod, bound in froms:
        for name, orig in bound.items():
            if name in binds and binds[name] != (mod, orig):
                shadowed.append((name, binds[name][0], mod))
            binds[name] = (mod, orig)
    return binds, shadowed, froms


def rewrite(path, only=None):
    """(new_source, rewrites, shadowed) — the qualified form, or (None, 0, shadowed) on refusal.

    ⚑ THE COUNT IS RETURNED SO A CALLER CAN REFUSE A ZERO. `RenameCommand` reported
    "Transformed 1 files successfully" over a zero diff, which is the failure this whole module
    exists because of; a rewrite that changed nothing must be VISIBLE as nothing.
    """
    binds, shadowed, froms = plan_file(path, only)
    with open(path, encoding="utf-8") as _fh:
        _probe = libcst.parse_module(_fh.read())
    _as = _as_imports(_probe, only)
    # ⚑⚑ THE JOINT-UNSAFETY REFUSAL. Each arm alone is correct; together on ONE file they can
    # emit a module-qualified read in a function that also carries a function-scoped aliased
    # import of the same module — which the AS-MOD arm turns into a bare `import X`, binding X
    # locally and stranding the earlier read. See `_local_import_conflicts`. Refusing is the
    # same discipline the `from` arm already applies to `shadowed`: a file with no single safe
    # rewrite is declined, not half-done.
    # ⚑⚑ SCOPED TO THE MODULES THIS RUN WOULD QUALIFY — and the unscoped version was WRONG in
    # the direction that stops work. Measured on a 6-file sample: it refused 4 of 6, flagging
    # `tempfile as _tf`, `hashlib as _h`, `libcst as _lc` — stdlib aliases with no relation to
    # the module being rewritten. The hazard needs the function-scoped alias to name the SAME
    # module the `from` arm is qualifying; anything else cannot collide, because the bare name
    # the rewrite introduces is a different name entirely.
    #
    # ⚑ A REFUSAL THAT OVER-TRIGGERS IS NOT "SAFE" — it silently shrinks the reachable set and
    # every downstream estimate inherits the shrinkage. That is the same shape as a census that
    # cannot see its own gaps, which is why `--refused` exists to MEASURE this rather than let
    # the sweep's skip-count imply it.
    _qualified = {m for _n, m, _b in froms}
    _conflicts = [(m, a) for m, a in _local_import_conflicts(_probe, only)
                  if m in _qualified]
    if _conflicts:
        return None, 0, [("%s (function-scoped `as %s`)" % (m, a), "module-qualified read",
                          "function-local import") for m, a in _conflicts]
    if shadowed or (not froms and not _as):
        return None, 0, shadowed
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    tree = libcst.parse_module(src)
    # ⚑⚑ RE-DERIVE THE IMPORT NODES FROM *THIS* TREE. `plan_file` parses its own tree and
    # discards it, so `froms`' node ids belong to an object that no longer exists — every
    # `id(orig) in self.import_ids` test compared against ids from a different parse and
    # matched nothing. The names rewrote correctly (they key on VALUE) while the imports were
    # silently left alone: 16/18, and the two red cases were the only witnesses.
    #
    # ⚑ AND MY FIRST DIAGNOSIS WAS WRONG — I read it as MetadataWrapper's deep copy and added
    # `unsafe_skip_copy=True`, which is correct for a different reason and did not fix this.
    # A probe on the real file showed `leave_ImportFrom` firing with a MATCHING id, which is
    # what ruled the copy theory out: the fixture and the file differed because `plan_file`
    # was called once in one path and twice in the other.
    froms = _from_imports(tree, only)
    # ⚑ `MetadataWrapper` DEEP-COPIES BY DEFAULT, so node ids captured from `tree` do not
    # match the nodes the transformer actually visits — `import_ids` and `attr_names` silently
    # matched NOTHING and the imports were left as-is while the names rewrote fine (16/18,
    # with the two import cases red). `unsafe_skip_copy=True` keeps the identities, which is
    # safe here because nothing else holds a reference to this tree.
    as_rows = _as_imports(tree, only)
    wrapper = libcst.metadata.MetadataWrapper(tree, unsafe_skip_copy=True)
    xf = _Qualify(binds, _attr_context(tree), {id(n) for n, _m, _b in froms},
                  alias_plan={alias: mod for _n, mod, alias in as_rows},
                  as_import_ids={id(n) for n, _m, _a in as_rows},
                  as_modules={mod for _n, mod, _a in as_rows})
    new = wrapper.visit(xf)
    return new.code, xf.rewrites, []


def _selftest():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import rungs
    import tempfile
    check = rungs.Cases(key="scratch/qualify_imports.py")
    d = tempfile.mkdtemp(prefix="qualify_")

    # ⚑ THE FIXTURE CARRIES EVERY CASE THAT MUST *NOT* BE REWRITTEN. A pass that only proves it
    # rewrites the right thing is untested in the direction that breaks code.
    f = os.path.join(d, "consumer.py")
    open(f, "w", encoding="utf-8").write(
        "from helper import strip, split_arrows\n"
        "from other import thing as renamed\n"
        "from . import sibling\n"
        "import os\n"
        "\n"
        "def f(text, strip_mode):\n"
        "    a = strip(text)\n"                    # REWRITE — the imported name
        "    b = text.strip()\n"                   # LEAVE   — a method on a str
        "    c = \"strip\"\n"                      # LEAVE   — a string literal
        "    d = strip_mode\n"                     # LEAVE   — a different name entirely
        "    e = split_arrows(text)\n"             # REWRITE
        "    g = renamed(text)\n"                  # REWRITE to other.thing
        "    return a, b, c, d, e, g\n")
    binds, shadowed, froms = plan_file(f)
    check("every `from` import's bound names are planned, relative and plain skipped",
          sorted(binds), ["renamed", "split_arrows", "strip"])
    check("an `as` binding plans to the ORIGINAL name, not the alias",
          binds["renamed"], ("other", "thing"))
    check("a relative import is not planned (no module name to qualify with)",
          [m for _n, m, _b in froms if m == "."], [])
    check("nothing is shadowed in the clean fixture", shadowed, [])

    # ⚑ SHADOWING MUST REFUSE. Two imports binding one name have no single correct rewrite.
    f2 = os.path.join(d, "shadow.py")
    open(f2, "w", encoding="utf-8").write(
        "from alpha import common\n"
        "from beta import common\n"
        "x = common()\n")
    _b2, shadow2, _fr2 = plan_file(f2)
    check("a name bound by two different imports is reported as shadowed",
          [(n, a, b) for n, a, b in shadow2], [("common", "alpha", "beta")])

    # ⚑ `--module` NARROWS THE PLAN, so a cluster can be paid down one provider at a time
    # rather than a whole file at once — the 18-consumer `_agdatext` cluster is the motivating
    # case, and a file-at-a-time tool would force unrelated churn into the same diff.
    b3, _s3, _f3 = plan_file(f, only="helper")
    check("--module restricts the plan to one provider",
          sorted(b3), ["split_arrows", "strip"])

    # ── THE REWRITE HALF ──────────────────────────────────────────────────────────────
    # ⚑ THE PLAN BEING RIGHT PROVES NOTHING ABOUT THE REWRITE, and that gap is the exact
    # shape of the defect that made this module necessary: `RenameCommand` planned fine and
    # emitted a zero diff while reporting success.
    out, n, _sh = rewrite(f)
    check("the rewrite changes something (a zero-diff success is the RenameCommand defect)",
          n > 0, True)
    check("the import becomes bare", "import helper\n" in out, True)
    check("...and the `from` form is gone",
          "from helper import" in out, False)
    check("an imported call is qualified", "helper.strip(text)" in out, True)
    # ⚑ THE THREE LEAVE-ALONE CASES, each a bare `strip` token a regex would rewrite.
    check("a METHOD call on a value is untouched", "text.strip()" in out, True)
    check("...and did not become an attribute of the module",
          "text.helper.strip" in out, False)
    check("a STRING literal is untouched", 'c = "strip"' in out, True)
    check("a DIFFERENT local name is untouched", "d = strip_mode" in out, True)
    check("an `as` import qualifies to the ORIGINAL name",
          "other.thing(text)" in out, True)
    check("a relative import survives the rewrite untouched",
          "from . import sibling" in out, True)
    # ⚑ THE RESULT MUST PARSE. A transform that emits a tree python cannot read is worse than
    # none, and `_dotted` exists because the naive `libcst.Name("a.b")` does exactly that.
    import ast as _ast
    _ok = True
    try:
        _ast.parse(out)
    except SyntaxError:
        _ok = False
    check("the rewritten source parses", _ok, True)
    # ⚑ A REFUSED FILE REWRITES NOTHING — the shadow case must not emit a partial edit.
    _o2, _n2, _s2 = rewrite(f2)
    check("a shadowed file returns no source and no rewrites", (_o2, _n2), (None, 0))

    # ── THE AS-MOD ARM: `import x as q` → `import x`, `q.name` → `x.name` ──────────────
    # ⚑ A DIFFERENT TRANSFORM, and the fixture must prove it does NOT behave like the `from`
    # one. `import x as q` already takes the module whole — only the LABEL is wrong — so the
    # repair respells the alias in place; it does not wrap anything in a new Attribute.
    f3 = os.path.join(d, "aliased.py")
    open(f3, "w", encoding="utf-8").write(
        "import store as _store\n"
        "import numpy as np\n"                     # foreign — must survive untouched
        "\n"
        "def g(conn, _store_flag):\n"
        "    a = _store.connect()\n"               # RESPELL to store.connect()
        "    b = conn._store\n"                    # LEAVE — an ATTRIBUTE named _store
        "    c = _store_flag\n"                    # LEAVE — a different name
        "    d = np.array([1])\n"                  # LEAVE — foreign alias
        "    return a, b, c, d\n")
    out3, n3, _sh3 = rewrite(f3, only="store")
    check("the alias respells to the module name", "store.connect()" in out3, True)
    check("...and the aliased import loses its alias", "import store\n" in out3, True)
    check("an ATTRIBUTE with the alias's spelling is untouched",
          "conn._store" in out3, True)
    check("a similarly-named local is untouched", "c = _store_flag" in out3, True)
    # ⚑ `--module` MUST NOT TOUCH A FOREIGN ALIAS. `import numpy as np` is not this repo's
    # namespace to govern, and a pass that dropped it would break the file for a policy that
    # does not apply to it.
    check("a foreign alias outside --module survives", "import numpy as np" in out3, True)
    check("...and its uses survive", "np.array([1])" in out3, True)
    _ok3 = True
    try:
        _ast.parse(out3)
    except SyntaxError:
        _ok3 = False
    check("the AS-MOD rewrite parses", _ok3, True)
    check("the AS-MOD rewrite reports its count", n3 > 0, True)

    # ⚑⚑ THE LOOP-VARIABLE SHADOW — measured on the first real target, not imagined.
    # `autocorr_synth.py` imports `store as _s` at module scope and ALSO uses `_s` as a
    # tuple-unpacking loop variable in four comprehensions. The first AS-MOD cut skipped
    # scope resolution ("an alias is unambiguous within its file") and rewrote
    #     for _s, name, sz_ in run:   →   for store, name, sz_ in run:
    # rebinding the module inside the loop. This case FAILS against that version.
    f4 = os.path.join(d, "shadowed_alias.py")
    open(f4, "w", encoding="utf-8").write(
        "import store as _s\n"
        "\n"
        "def h(run):\n"
        "    conn = _s.connect()\n"                # RESPELL — resolves to the import
        "    out = [n for _s, n, z in run]\n"      # LEAVE — a loop variable, shadows it
        "    return conn, out\n")
    out4, n4, _sh4 = rewrite(f4, only="store")
    check("a module-scope alias use is respelled", "store.connect()" in out4, True)
    check("a LOOP VARIABLE sharing the alias's spelling is NOT rewritten",
          "for _s, n, z in run" in out4, True)
    check("...and the module name was not injected into the comprehension",
          "for store, n, z in run" in out4, False)
    # ⚑ ONE, NOT TWO — `rewrites` counts NAME substitutions, and the import statement losing
    # its alias is not one. I expected 2 and the case caught the expectation, not the code.
    check("only the genuine use counted, and the import is not a 'rewrite'", n4, 1)

    # ── Ⓧ4′: the trailing comment keeps its column ────────────────────────────────────
    # ⚑ COSMETIC BUT NOT OPTIONAL — in this corpus the ⚑ comments ARE the incident log, and an
    # import block whose comment column walks left by the alias length on every paydown is a
    # diff that reviewers stop reading. The delta is exactly computable, so this is arithmetic.
    f5 = os.path.join(d, "aligned.py")
    open(f5, "w", encoding="utf-8").write(
        "import store as _store        # THE store authority\n"
        "import other as _o            # kept: --module scopes this out\n"
        "x = _store.connect()\n"
        "y = 1  # single space, an author's spacing and not an alignment\n")
    out5, _n5, _sh5 = rewrite(f5, only="store")
    _cols = {l.split("#")[0].rstrip(): l.index("#") for l in out5.splitlines() if "#" in l}
    check("the realigned import keeps the ORIGINAL comment column",
          out5.splitlines()[0].index("#"), 30)
    check("...and an untouched import is not disturbed",
          out5.splitlines()[1].index("#"), 30)
    # ⚑ A SINGLE SPACE IS SPACING, NOT ALIGNMENT. Padding it would invent a column the author
    # never chose, so the guard is `len(ws) >= 2` and this case pins it.
    check("a single-space comment is NOT padded",
          "y = 1  # single space" in out5, True)
    # ⚑ THE CODE HALF IS WHAT PRECEDES THE `#`, and my first version of this case asserted on a
    # string built by deleting the comment text — which cannot produce `import store\n` because
    # the padding sits between them. The case was wrong, not the code; it now reads the code
    # half directly instead of reconstructing it.
    check("the alignment pass did not alter the code half",
          out5.splitlines()[0].split("#")[0].strip(), "import store")

    # ⚑⚑ BOUND TWO WAYS IN ONE FUNCTION — the defect that broke pycodemod's own selftest.
    # `_pycodemod_selftest.py` imports `_pycodemod_core as _c` at module scope AND assigns `_c`
    # as a local 15× inside `_selftest` (tuple-unpacking throwaways). ScopeProvider reports BOTH
    # assignments for the name, so an `any(... Import)` test passes and the module reads get
    # rewritten — yielding `UnboundLocalError: cannot access local variable`, because python
    # treats a name assigned anywhere in a function as local THROUGHOUT it. This case fails
    # against the `any()` version.
    # ⚑⚑ THE MECHANISM, MEASURED — and my first fixture did NOT reproduce it. I assumed the
    # local was a comprehension variable; a probe showed comprehensions get their OWN
    # `ComprehensionScope`, so `_c` there is genuinely separate and rewriting the module read
    # is CORRECT. The real break is a MODULE-SCOPE `from` import combined with a
    # FUNCTION-SCOPE `import ... as`: qualifying the `from`-bound names to `_pycodemod_core.x`
    # while a function separately does `import _pycodemod_core as _core` makes the bare module
    # name FUNCTION-LOCAL there — so every module-scope-qualified read inside that function
    # raises `UnboundLocalError: cannot access local variable`, at RUNTIME, past any parse check.
    # ⚑⚑ THE REAL SHAPE, RECOVERED BY `symtable` AFTER TWO WRONG RECONSTRUCTIONS. Guess 1 was
    # comprehension shadowing (refuted: comprehensions get their own ComprehensionScope, so the
    # module read there is correctly rewritable). Guess 2 was "a function-scope alias makes the
    # module name local" — I hand-wrote it and it did NOT raise, because `import X as _alt`
    # binds `_alt`, not `X`. The decisive reading:
    #
    #     symtable, inside _selftest:  _pycodemod_core  local=True assigned=False imported=True
    #
    # ONE function contains BOTH a module-qualified read (from the `from`-arm rewrite, early)
    # AND a function-scoped `import <module> as <alias>` (rewritten by the AS-MOD arm to a bare
    # `import <module>`, later). The bare import binds the module name LOCALLY for the whole
    # function, so the earlier read — which the rewrite made module-qualified — is a read of a
    # local before assignment: UnboundLocalError, at runtime, past any parse or compile check.
    # (`compile()` accepts it; only executing the function fails.)
    f6 = os.path.join(d, "dual_bound.py")
    open(f6, "w", encoding="utf-8").write(
        "from store import connect\n"               # module scope: `from`-arm qualifies this
        "\n"
        "def k():\n"
        "    a = connect()\n"                       # → store.connect()  — EARLY in the function
        "    import store as _alt\n"                # → import store     — binds `store` LOCALLY
        "    return a, _alt.dialect()\n")
    out6, n6, _sh6 = rewrite(f6, only="store")
    # ⚑⚑ Ⓧ4ᶜ′ — THE FIXTURE EXECUTES, and that is the whole point of this case. An earlier
    # version `exec`'d the rewritten source with no importable `store` on the path, so it died
    # at ImportError BEFORE reaching the aliasing function and passed without exercising
    # anything. It pinned the shape and claimed the failure. `store.py` already exists in this
    # temp dir (written for the AS-MOD cases), so putting `d` on sys.path makes the import
    # succeed and the call reachable — `UnboundLocalError` is a RUNTIME error and only running
    # it can see one.
    #
    # ⚑ `dialect` IS ADDED TO THE FIXTURE MODULE for this case: `j()` must actually CALL
    # something through the function-scoped alias, or the local binding is never exercised.
    # ⚑ WRITTEN, NOT APPENDED, and both functions named explicitly. Appending assumed a
    # `store.py` with a `connect` already existed from a sibling case — it did not, and the
    # case failed with `AttributeError: module 'store' has no attribute 'connect'`. That
    # failure is the fixture being incomplete, which is exactly what an EXECUTING case is for:
    # the previous non-executing version would have passed over the same gap.
    open(os.path.join(d, "store.py"), "w", encoding="utf-8").write(
        "def connect(**k): return 'CON'\n"
        "def dialect(): return 'sqlite'\n")
    _dual_ok, _dual_err = True, ""
    if out6 is not None:
        # Only reachable if the refusal above ever regresses — kept so a future change that
        # starts EMITTING for this shape is caught by execution rather than by inspection.
        _saved_path = list(sys.path)
        sys.path.insert(0, d)
        try:
            _ns = {}
            exec(compile(out6, "dual_bound.py", "exec"), _ns)  # noqa: S102 — our own fixture
            _ns["k"]()                 # the qualified read, then the aliased import
        except Exception as _e:        # noqa: BLE001 — ANY failure is the finding
            _dual_ok, _dual_err = False, "%s: %s" % (type(_e).__name__, _e)
        finally:
            sys.path[:] = _saved_path
    # ⚑ THE FILE IS REFUSED, so there is nothing to run — and that IS the pass condition. An
    # earlier version of this case asserted the rewritten source RUNS; it went red with the
    # exact corpus error (`UnboundLocalError: cannot access local variable 'store'`), which is
    # what proved the fixture faithful. The fix is a refusal rather than a cleverer rewrite:
    # a file carrying both shapes has no single safe output.
    check("a file combining a qualified read with a function-scoped alias is REFUSED",
          (out6, n6), (None, 0))
    check("...and the refusal names the conflicting import",
          bool(_sh6) and "store" in str(_sh6[0]), True)
    check("nothing was executed, because nothing was emitted",
          (_dual_ok, _dual_err), (True, ""))
    check("the multi-form import file is detected as such (2 forms, one module)",
          len(_from_imports(libcst.parse_module(open(f6).read()), "store"))
          + len(_as_imports(libcst.parse_module(open(f6).read()), "store")), 2)
    # ⚑ AND A COMPILE CHECK WOULD NOT HAVE CAUGHT THIS — measured, not assumed. The broken
    # output PARSED and COMPILED cleanly; `symtable` on it reports `_pycodemod_core` as
    # `local=True assigned=False imported=True` inside the function, and python only raises
    # when the function RUNS. So the earlier `compile(out6, ...)` case here was testing a layer
    # that cannot see the defect, and it has been removed rather than left as reassurance.
    # What catches this class is `_local_import_conflicts` at plan time, and — for anything it
    # misses — executing the result, as the case above does.
    return check.report()


def main():
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    only = None
    if "--module" in sys.argv:
        i = sys.argv.index("--module")
        if len(sys.argv) > i + 1:
            only = sys.argv[i + 1]
            paths = [p for p in paths if p != only]
    if not paths:
        print(__doc__.strip().split("Usage:")[-1].strip())
        sys.exit(2)

    # ⚑ Ⓧ4ᵈ — THE REFUSAL POPULATION IS A QUERY, NOT A GUESS. `_local_import_conflicts` was
    # added after ONE file broke the toolkit; how much of the corpus it excludes was unmeasured,
    # which makes every remaining paydown estimate unreliable. A refusal that silently shrinks
    # the reachable set is the same shape as a census that cannot see its own gaps — so the
    # count gets its own mode rather than being inferred from what the sweep happens to skip.
    if "--refused" in sys.argv:
        # ⚑⚑ A DIRECTORY ARGUMENT MUST EXPAND, NOT READ AS ZERO FILES. The first cut took only
        # file paths, so `--refused scratch` printed "0 refused, 0 rewritable, 0 with no
        # matching import (of 0 file(s) read)" — a FALSE ZERO in the reassuring direction, from
        # a mode built to make an unmeasured population measurable. The `(of N file(s) read)`
        # denominator is what exposed it; a bare "0 refused" would have read as good news.
        #
        # ⚑ EVERY `.py` UNDER THE PATH, INCLUDING VENDORED SUBTREES — deliberately, and NOT
        # `pycodemod.py_files()`. I proposed swapping to that reader to skip `eliza/` and
        # `estate/` on the assumption they were third-party and out of scope; the operator's
        # ruling is that they are OWNED CODE and the policy reaches them. So the walk stays
        # bare: `_SKIP_DIRS` encodes a different question (which files the TOOLING corpus
        # spans) and borrowing it here would silently narrow a policy census to a tooling one.
        # The 3150-file denominator is the honest total, not an inflated one.
        _expanded = []
        for p in paths:
            if os.path.isdir(p):
                for dirpath, _dn, fns in os.walk(p):
                    # ⚑⚑ Ⓧ4ᵈ‴ — THIRD-PARTY ≠ VENDORED, AND CONFLATING THEM COST BOTH
                    # DIRECTIONS. I first proposed skipping `eliza/` and `estate/` as
                    # "vendored"; the operator's ruling is that they are OWNED (measured: 168
                    # files, 0 refused, 161 rewritable — real work I had written off). What is
                    # genuinely not ours is INSTALLED DEPENDENCY code: `.venv`/`site-packages`
                    # supplied 6 of the 18 refusals (scipy, numpy, setuptools) and no policy of
                    # this repo governs a line of it.
                    #
                    # ⚑ SO THE PREDICATE IS "DID WE INSTALL IT", NOT "IS IT A SUBTREE".
                    # `py_files()`'s comment says "VENDORED CODE IS NOT OUR CORPUS" but its
                    # motivating case was a virtualenv — the label is broader than the rule it
                    # actually implements, which is how I read it as excluding owned subtrees.
                    # Matching PATH COMPONENTS, not substrings, for the reason that file
                    # records: `"build" in rel` also eats `rebuild/`.
                    _parts = set(os.path.relpath(dirpath, p).split(os.sep))
                    if _parts & {".venv", "site-packages", "node_modules",
                                 "__pycache__", ".edit-snapshots", ".git"}:
                        continue
                    _expanded += [os.path.join(dirpath, f) for f in sorted(fns)
                                  if f.endswith(".py")]
            else:
                _expanded.append(p)
        paths = _expanded
        _ref, _clean, _none, _unread = [], 0, 0, []
        for p in paths:
            try:
                with open(p, encoding="utf-8") as _fh:
                    _t = libcst.parse_module(_fh.read())
            except (SyntaxError, OSError, UnicodeDecodeError) as _e:
                # ⚑ AN UNREADABLE FILE IS REPORTED, NEVER SILENTLY SKIPPED. `continue` alone
                # would shrink the denominator without saying so, which makes "N of M" a claim
                # about the files that happened to parse — a fact about the METHOD printed as a
                # fact about the corpus.
                _unread.append((p, type(_e).__name__))
                continue
            # ⚑ THE SAME SCOPING AS `rewrite` — a census that applied a different predicate
            # than the tool would report a population nothing acts on. Derived from `_fr` here
            # exactly as `rewrite` derives it from `froms`.
            _fr = _from_imports(_t, only)
            _q = {m for _n, m, _b in _fr}
            _cf = [(m, a) for m, a in _local_import_conflicts(_t, only) if m in _q]
            if _cf:
                _ref.append((p, _cf))
            elif _fr or _as_imports(_t, only):
                _clean += 1
            else:
                _none += 1
        for p, cf in _ref:
            print("  REFUSED  %s" % p)
            for m, a in cf:
                print("               %s imported as %s inside a function" % (m, a))
        print("%d refused, %d rewritable, %d with no matching import (of %d file(s) read)"
              % (len(_ref), _clean, _none, len(_ref) + _clean + _none))
        if _unread:
            print("   ⚑ %d file(s) this reader could not parse — a fact about the READER, "
                  "not about them:" % len(_unread))
            for _p, _k in _unread[:5]:
                print("        %s  (%s)" % (_p, _k))
        # ⚑ THE REFUSED SET IS NOT DEBT — it is the population needing a DIFFERENT repair
        # (hoist the function-scoped alias to module scope first, then the sweep reaches it).
        # Reporting it as "cannot" rather than "not yet" would turn work into a wall.
        print("   refused = both a `from` import AND a function-scoped `import x as q` for the")
        print("   same module: the two arms are individually correct and jointly unsafe.")
        print("   Repair: hoist the function-scoped alias to module scope, then re-run.")
        sys.exit(0)

    apply = "--apply" in sys.argv
    if apply:
        # ⚑ SNAPSHOT BEFORE THE FIRST WRITE — the convention 66 call sites in this repo
        # share. `edit_snapshot.py:263` names the gap it closes: "the decision was made and
        # the damage written before any verification could run."
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "scripts"))
        import edit_snapshot
        edit_snapshot.guard("qualify_imports (%d file(s))" % len(paths), paths)
    refused = written = 0
    for p in paths:
        out, n, shadowed = rewrite(p, only)
        if shadowed:
            refused += 1
            print("%s: REFUSED — %d name(s) bound by two imports:" % (p, len(shadowed)))
            for name, a, b in shadowed:
                print("    %s from both %s and %s" % (name, a, b))
            continue
        if out is None:
            print("%s: nothing to do (no matching `from` import)" % p)
            continue
        # ⚑ THE REWRITTEN SOURCE MUST PARSE BEFORE IT IS WRITTEN. The selftest asserts this
        # on a fixture; a corpus file can carry shapes the fixture does not, and a transform
        # that emits unparseable python is worse than no transform. Refuse, never write.
        import ast
        try:
            ast.parse(out)
        except SyntaxError as e:
            refused += 1
            print("%s: REFUSED — rewritten source does not parse (%s)" % (p, e))
            continue
        # ⚑ A ZERO-REWRITE "SUCCESS" IS THE DEFECT THIS MODULE EXISTS BECAUSE OF, so it is
        # reported as nothing-done rather than as a transform.
        if n == 0:
            print("%s: 0 rewrites — import(s) present but no free use; left alone" % p)
            continue
        if apply:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(out)
            written += 1
        binds, _sh, froms = plan_file(p, only)
        print("%s: %d import(s) -> bare, %d use(s) qualified%s"
              % (p, len(froms), n, "" if apply else "  (dry run)"))
        for name, (mod, orig) in sorted(binds.items()):
            print("    %s -> %s.%s" % (name, mod, orig))
    if refused:
        print("%d file(s) REFUSED — nothing written for those" % refused)
    if apply:
        print("%d file(s) rewritten" % written)


if __name__ == "__main__":
    main()
