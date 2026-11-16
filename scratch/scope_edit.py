#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_edit.py — HOW AN IMPORT STATEMENT IS WRITTEN: the four operations every handler ends in.

⚑⚑ SPLIT OUT OF `scope_fix.py` 2026-08-11 (⟡split-1200). `scope_fix` is a CHAIN, and the seam
is the arrow rather than the line count: the loop `fix()` consumes the `fix_*` handlers, and
every handler that ends by binding a name consumes THESE. Six of them do — `fix_parse_error`,
`fix_demand`, `fix_qualified`, `fix_alias_split`, `fix_missing_ctor`, `fix_silent_ctors` all
call `add_import`; two more call `add_renaming_import`. Moving the SUPPLIER leaves a leaf;
moving any one consumer would have left it reaching back up.

    add_import(path, module, name)            merge into an existing `using (…)`, else a new line
    add_renaming_import(path, m, src, tgt)    the `using () renaming (src to tgt)` form
    _rename_owner(leaf, path)                 WHERE a rename target comes from — the pair to it
    _repoint_alias(path, alias, owner)        point `import <old> as <alias>` at a new owner

⚑ `_rename_owner` IS HERE, NOT IN `scope_resolve`, BECAUSE IT IS HALF OF ONE OPERATION. It
looks like a resolver — it returns `(owner, source_name, args)` and consults no writer — but its
own docstring names the coupling: *"the caller re-issues `renaming (source to leaf)`"*. It
exists only to feed `add_renaming_import`, and a rename target is a qname NOWHERE, so no
ranking in `scope_resolve` can answer it; the alias module's own `renaming` clause is the only
record. Filing it with the resolvers would separate the finder from the only thing that acts on
what it finds — the split-the-pair shape that made `rewire_only` ship with zero callers.

⚑ AND THE THREE WRITE SITES BELOW ARE NOT THE WRITE PATH. `_write` (in `scope_source`) is, and
it stays the single one — it clears `_IMPORTS` so the cycle guard stays honest after this
tool's own edits, and it had to move WITH `_import_graph` for that reason. A `global`-rebound
cache may not straddle a seam; these functions only CALL `_write`, so they may.
"""
import os as _o, sys as _s
import re

_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive
# ⚑ THE COMMENT AUTHORITY, AND IT IS DEFECT #1 OF THIS TOOL'S OWN REDERIVE AUDIT
# (`scope_fix.py` docstring: *"NO COMMENT MASKING — ~40 regexes run against RAW
# source; `agda_lex.mask_comments` is the authority … HIGHEST-VALUE FIX"*).  Measured
# here 2026-08-17: the bare-import guard below matched `open import …` INSIDE the
# 25-line comment banner of `Algebra/Bijection.agda` and reported the name as already
# imported, so the repair refused and the file stayed broken.  Nesting-aware and
# length-preserving, so match OFFSETS stay valid against the original source.
from agda_lex import mask_comments as _mask
from scope_source import (
    _ADDED, _alias_names, _head_text, _imports_of, _module_exports, _module_params,
    _module_text, _open_stmts, _owner_admissible, _rename_index, _rename_pairs,
    _suppliable, _conduit_set, _would_cycle, _write, application_args,
    rename_records,
)


def add_import(path, module, name, dry=False, args_hint=""):
    """Merge `name` into an existing `open import module using (…)`, else add a new line.

    ⚑ A PARAMETERIZED owner must be APPLIED. Importing `…Cyclic.Base` unapplied binds the
    module-as-function form, so `power k` becomes `(n : ℕ) → ℕ → Word (Gen n)` and every use
    fails with `[UnequalTerms]`. When the owner takes parameters and the consumer already
    applies that same owner (or is itself parameterized over the same names), reuse those args.
    """
    src = open(path).read()
    if _would_cycle(module, module_path(path, "")):
        return False, "refused: would close an import cycle"
    params = _module_params(module)
    args = ""
    for pn in params:
        if re.search(rf"^module [^\n]*\(\s*{re.escape(pn)}\s*:", src, re.M) or \
           re.search(rf"^open import [\w.-]+ {re.escape(pn)}(?![\w])", src, re.M):
            args += f" {pn}"
        else:
            args = ""                       # cannot supply every parameter by NAME
            break
    # ⚑ T2 ⟡pd-applied-not-unapplied. If the parameter names do not literally match, recover the
    # application from the context the shape DB records (the consumer's own existing `open
    # import owner <args>`, or how the module the consumer reached `owner` THROUGH applied it).
    if params and not args:
        a = application_args(module, path) or args_hint
        if a:
            args = " " + a
    # An UNAPPLIED import of a parameterized module binds the module-as-function form, so
    # `normalize (power k)` becomes `(Gen : Set) → …` and dies with `Word (Base.Gen n) !=< Set`.
    # Refusing is strictly better than writing an import that cannot typecheck.
    if params and not args:
        return False, f"refused: {module} is parameterized and its arguments are not in scope"
    module_applied = module + args
    if module == module_path(path, ""):
        return False, "self-import refused"
    # ⚑⚑ THE IMPORT BAN IS THE LATER POLICY, AND THIS FUNCTION PREDATES IT.
    # `771283c8` (⟡ban-decompose) forbids `using`/`renaming`/`hiding`/`as` on a
    # Substrate import: DECOMPOSITION IS THE MEANS, BARE IMPORTS ARE THE END, and a
    # `using` filter exists only where a module exports enough names to collide.
    # This tool is the mechanized ⟡public-paydown loop and predates that arc, so it
    # repaired one policy while writing violations of another — MEASURED 2026-08-17
    # on `Algebra/Bijection.agda`, which came out `✓ clean after 3 fix(es)` and
    # carrying three fresh `using (…)` clauses.  A sweep would have injected them at
    # the scale of the `NotInScope` population.
    #
    # ⚑ A BARE IMPORT IS ALSO STRICTLY MORE LIKELY TO BE CORRECT HERE.  The `using`
    # list was never a scoping decision this tool made on evidence — it names the ONE
    # name the compiler happened to report first, so a file needing three names from
    # one leaf took three iterations and three merges.  Post-decomposition a leaf
    # exports a handful of names, which is the precondition that makes the bare form
    # safe (and the reason the ban was payable at all).
    #
    # ⚑ IT STILL MERGES RATHER THAN DUPLICATING.  An EXISTING `using (…)` on a
    # Substrate import is pre-existing debt this function did not write; widening it
    # is not this tool's paydown to do, and rewriting a caller's filter could drop a
    # name the file relies on.  So: a bare import already present satisfies the need
    # (nothing to write); an existing `using` is still merged into, and reported.
    # ⚑ AGAINST THE MASKED SOURCE, NOT THE RAW TEXT.  A file's comment banner quotes
    # import statements (`Algebra/Bijection.agda` names four in prose), and a raw scan
    # reads those as live structure — measured: this guard reported `≡` as already
    # imported from a COMMENT and the repair refused, leaving the file broken.
    _masked = _mask(src)
    bare = re.compile(r"^open import " + re.escape(module) +
                      r"(?![\w.-])[^\n]*$", re.M)
    for _b in bare.finditer(_masked):
        tail = _b.group(0)[len("open import ") + len(module):]
        if not re.search(r"\b(using|renaming|hiding|as)\b", tail):
            return False, f"already imported bare from {module}"
    # allow module ARGUMENTS between the module name and `using` so an applied import
    # (`open import …Base n using (…)`) merges instead of spawning a duplicate line.
    merge = re.compile(r"(open import " + re.escape(module) + r"(?![\w.-])[^\n(]*using \()([^)]*)(\))", re.S)
    m = merge.search(src)
    if m:
        if re.search(rf"(^|[;\s]){re.escape(name)}\s*($|[;)])", m.group(2)):
            return False, "already imported"
        # an EMPTY using-list (`using () renaming (…)`) must not gain a leading separator
        sep = "; " if m.group(2).strip() else ""
        new = src[:m.end(2)] + f"{sep}{name}" + src[m.end(2):]
        how = f"merged into existing `open import {module}`"
    else:
        # ⟡paydown-telescope-anchor: a PARAMETERIZED module's header spans many lines
        #   module M
        #     (A : Set) …
        #     where
        # so anchoring on the header's FIRST line drops the import INSIDE the telescope
        # and corrupts the file ([ParseError]).  Anchor on the END of the header — the
        # line carrying `where` — which for a single-line header is the header itself.
        anchor = re.search(r"^module [^\n]*\n", src, re.M)
        if not anchor:
            return False, "no module header"
        if not re.search(r"\bwhere\b", src[anchor.start():anchor.end()]):
            w = re.compile(r"^[^\S\n]*where\b[^\n]*\n", re.M).search(src, anchor.end())
            if not w:
                return False, "module header has no `where`"
            anchor = w
        # ⚑ BARE — the ban's END STATE, and the form the decomposition made payable.
        # `name` is still carried in the RETURN so `_ADDED` can roll the statement back
        # on an `[AmbiguousName]`, and so the caller's log still says which name this
        # import was written FOR; only the emitted SOURCE drops the filter.
        line = f"open import {module_applied}\n"
        new = src[:anchor.end()] + line + src[anchor.end():]
        how = f"new `open import {module_applied}` (bare, for {name})"
    if not dry:
        _write(path, new)
        _ADDED[(path, name)] = module           # ⚑ T6: remember it, so it can be rolled back
    return True, how


def _repoint_alias(path, alias, owner, dry=False, args=""):
    """Point `import <old> as <alias>` at `owner` (optionally APPLIED), keeping uses qualified."""
    try:
        src = open(path).read()
    except OSError:
        return False
    m = re.search(rf"^(?:open\s+)?import\s+([\w.-]+)([^\n]*?)\s+as\s+{re.escape(alias)}(?![\w])",
                  src, re.M)
    if not m or not _owner_admissible(owner, path):
        return False
    applied = (owner + (" " + args if args else "")).strip()
    if (m.group(1) + m.group(2)).strip() == applied:
        return False
    # ⚑ an alias is ONE module's façade: repoint it only to a module that exports EVERY name
    # used through it, and that the consumer can apply. Without this the first resolvable leaf
    # dragged the whole alias onto an unrelated module (`Z₂` off `Z2-Coxeter` onto `V4-Coxeter`,
    # `Z₁` onto the 16-parameter `Coxeter.DirectProduct`), breaking every sibling name.
    # ⚑ a file whose aliases each stand for a DIFFERENT carrier (Z₂ … Z₇ over one generic
    # capability) hands the per-name resolver several equally-plausible owners: every Zₙ-Coxeter
    # reaches `Gen`/`Canonical`, so the FIRST that exports them wins and swallows the others.
    # A repoint that lands an alias on a module ANOTHER alias in this file already names is that
    # collapse — the silent miscompile (all five Zₙ became FreeCyclic-Coxeter, and it typechecked).
    # De-qualification / alias-split is the correct move there; refuse the repoint.
    # ⚑ compare module AND application: `Cyclic.Base 1 as Z₂` beside `Cyclic.Base 2 as Z₃` is the
    # CORRECT shape (one generic module, two instances) — only an identical application merges.
    others = {a: (t + " " + ar.strip()).strip() for t, ar, a in re.findall(
        r"^(?:open\s+)?import\s+([\w.-]+)([^\n]*?)\s+as\s+([^\s;]+)", src, re.M) if a != alias}
    if applied in others.values():
        clash = sorted(a for a, t in others.items() if t == applied)
        print(f"    ! {path}: alias {alias} NOT repointed to {owner.rsplit('.', 1)[-1]} — "
              f"alias {'/'.join(clash)} already names it (distinct carriers must not merge)")
        return False
    names = _alias_names(src, alias)
    if not _suppliable(owner, path) or not all(
            _module_exports(owner, n) for n in names):
        missing = sorted(n for n in names if not _module_exports(owner, n))
        print(f"    ! {path}: alias {alias} NOT repointed to {owner.rsplit('.', 1)[-1]} — "
              f"it does not serve {missing or 'the alias (unsuppliable)'}")
        return False
    new = src[:m.start(1)] + applied + src[m.end(2):]
    if new == src:
        return False
    if not dry:
        _write(path, new)
    print(f"    {path}: alias {alias} → {applied}   "
          f"[kept qualified — {alias}.… has several providers]")
    return True


def _rename_owner(leaf, path):
    """⟡pd-renaming-target — `leaf` exists ONLY as a RENAMING TARGET, so it is a qname NOWHERE.

    `Z2-Coxeter` reaches `inv-left-canonical` by `open import …InvCanonical.Left 1 using ()
    renaming (inv-left-canonical-ex to inv-left-canonical)`. catalog.db shows the point exactly:
    the only `copy = 0` definition is the `-ex` name at `Cyclic.InvCanonical.Left`; every
    `inv-left-canonical` in the corpus is a module-application COPY or a record field. So no
    ranking over definitions can ever resolve the target — the resolver has to read the alias
    module's own `renaming` clause and re-issue it at the DEFINER.

    Returns `(owner, source_name)`; the caller re-issues `renaming (source to leaf)`.
    """
    for c in dict.fromkeys(_conduit_set(path)):
        for body, ind in ((_module_text(c)), (_head_text(c), 0)):
            if not body:
                continue
            for sub, stmt in _open_stmts(body):
                if len(stmt) - len(stmt.lstrip()) != ind:
                    continue
                rest = stmt.split(sub, 1)[1] if sub in stmt else ""
                sargs = re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b",
                                 rest)[0].strip()
                for src_name, tgt in _rename_pairs(stmt):
                    if tgt != leaf:
                        continue
                    if _owner_admissible(sub, path) and _module_exports(sub, src_name):
                        return sub, src_name, sargs
                    # the renamer is ITSELF a conduit the strip emptied (`Fin-from-Cyclic` gets
                    # `σ-OrderOf` from `Cyclic.Base n`): follow one hop to the module that owns
                    # the SOURCE name, and re-issue the rename there.
                    for nxt in _imports_of(sub) or [s for s, _ in _open_stmts(_head_text(sub))]:
                        if _owner_admissible(nxt, path) and _module_exports(nxt, src_name):
                            return nxt, src_name, sargs
    # ⚑ the conduit that held the rename may no longer be imported at all: once every OTHER name
    # from that alias de-qualifies, its import is dropped, and with it the only local record of
    # the mapping. A rename TARGET is unique in the corpus by construction, so index them.
    # ⚑ ⟡rename-index-arbitrary-carrier — `rename_records` not `_rename_index()[leaf]`.
    # The raw index is a LIST, and iterating it positionally lets ORDER bias which
    # carrier is found first among several that all pass the tests below.  The accessor
    # ranks on `_module_exports` (the same test line 243 applies) and returns EMPTY where
    # the records differ only by application argument — a distinction this corpus-wide
    # index cannot adjudicate.  Empty falls through to `return None, None, ""`, which
    # `fix()` reports as "no owner found" and DEFERS: declining a name is safe, binding
    # the wrong carrier is the silent miscompile this whole module exists to prevent.
    for sub, src_name, sargs in rename_records(leaf):
        if _owner_admissible(sub, path) and _module_exports(sub, src_name):
            return sub, src_name, sargs
        for nxt in _imports_of(sub) or [s for s, _ in _open_stmts(_head_text(sub))]:
            if _owner_admissible(nxt, path) and _module_exports(nxt, src_name):
                return nxt, src_name, sargs
    return None, None, ""


def add_renaming_import(path, module, src_name, target, dry=False, args_hint=""):
    """`open import <module> <args> using () renaming (<src_name> to <target>)`, merged if present."""
    src = open(path).read()
    if _would_cycle(module, module_path(path, "")):
        return False, "refused: would close an import cycle"
    args = ""
    if _module_params(module):
        a = application_args(module, path) or args_hint
        if not a:
            return False, f"refused: {module} is parameterized and its arguments are not in scope"
        args = " " + a
    pat = re.compile(r"(open import " + re.escape(module) + r"(?![\w.-])[^\n(]*renaming \()([^)]*)(\))", re.S)
    m = pat.search(src)
    if m:
        if re.search(rf"(^|[;\s]){re.escape(src_name)}\s+to\b", m.group(2)):
            return False, "already imported"
        sep = "; " if m.group(2).strip() else ""
        new = src[:m.end(2)] + f"{sep}{src_name} to {target}" + src[m.end(2):]
        how = f"merged into existing `open import {module}` renaming"
    else:
        line = f"open import {module}{args} using () renaming ({src_name} to {target})\n"
        anchor = re.search(r"^module [^\n]*\n", src, re.M)
        if not anchor:
            return False, "no module header"
        at = anchor.end()
        if not re.search(r"\bwhere\b", src[anchor.start():at]):
            w = re.compile(r"^[^\S\n]*where\b[^\n]*\n", re.M).search(src, at)
            if not w:
                return False, "no module header"
            at = w.end()
        new = src[:at] + line + src[at:]
        how = f"new `{line.strip()}`"
    if not dry:
        _write(path, new)
    return True, how
