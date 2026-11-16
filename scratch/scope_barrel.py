#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_barrel.py — the STRIPPED-CONDUIT repairs: a barrel or wrapper that now exports nothing.

⚑⚑ SPLIT OUT OF `scope_fix.py` 2026-08-11 (⟡split-1200). The three handlers here are one class,
and the class is defined by its INSTRUMENT rather than by topic: all three are driven by Agda's
`-W[no]ModuleDoesntExport` warning or by the `[NotInScope]` it causes downstream, and all three
answer the same question — *this statement names a module that used to forward, and no longer
does; where did the names actually come from?*

    fix_barrel(out)         a stripped BARREL: split one import into one line per true owner
    fix_applied_open(out)   an APPLIED wrapper (`open Newman _↦_ …`), reported against module `_`
    fix_wrapper_open(out)   the same transform, resolved by NAME when no warning is emitted

⚑ THIS MODULE DOES NOT DEPEND ON `scope_edit`, AND THAT IS A MEASUREMENT, NOT A DESIGN GOAL.
Every other handler family ends in `add_import`; these do not. `fix_barrel` composes the
replacement statement itself (`seg = f"open import {o}{oargs}" …`) because it must PRESERVE the
using/renaming structure of the statement it is replacing, which `add_import`'s merge-or-append
cannot express. So `scope_barrel` and `scope_edit` are siblings under `scope_fix`, not a chain —
and knowing that is what makes the import list below short and the cut safe.

⚑ AND THE WARNING IS THE BETTER INSTRUMENT THAN THE ERROR IT CAUSES. `fix()` originally parsed
only `[NotInScope]`, which is why these files never converged: the barrel warning names the
FILE, the BARREL and the EXACT missing names, while the downstream scope error names one leaf
at a time with no owner. That asymmetry is the reason this family exists at all.
"""
import os
import os as _o, sys as _s
import re

_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive
from scope_errors import BARREL_W, NOT_IN_SCOPE
from scope_resolve import owner_from_shape
from scope_source import (
    _applied_owner, _imports_of, _is_file_module, _module_exports, _module_params,
    _owner_admissible, _stmt_at, _stmt_span, _suppliable, _wrapper_owner, _write,
    application_args,
)
from scope_store import catalog_index, owner_by_catalog


def _barrel_owner(leaf, barrel, near):
    """⚑ T13 barrel cohesion: the owner the BARREL itself reached `leaf` through.

    A barrel is one carrier's façade — `S4` is `Symmetric Axis`, and every name it re-exported
    belongs to that one applied instance. Its own import list is the most specific evidence
    available, and using it keeps a nine-name statement from being split across three unrelated
    owners by per-name catalog ranking (which sent `≈-refl` to a 15-parameter `GroupAdapter`)."""
    for sub in _imports_of(barrel):
        if not _owner_admissible(sub, near) or not _suppliable(sub, near):
            continue
        for sp in (leaf, f"_{leaf}_"):
            if _module_exports(sub, sp, exact=True):
                return sub, sp
    return None, None


def _owner_for(leaf, barrel, near):
    """Owning module of `leaf`: the barrel's own subtree first, else the shape-ranked catalog."""
    for key in (leaf, f"_{leaf}_"):
        for q in catalog_index().get(key, ()):
            m = q.rsplit(".", 1)[0]
            # ⚑ m == barrel is NOT a repoint: the name lives in the barrel but is not EXPORTED
            # (nested module / private). Returning it rewrites the import to itself — a no-op
            # that re-fires every pass (X8aSkiInstance looped to max_iters on exactly this).
            if m != barrel and m.startswith(barrel + ".") and _is_file_module(m) \
               and _owner_admissible(m, near):
                return m, q.rsplit(".", 1)[-1]
    o, sp = _barrel_owner(leaf, barrel, near)
    if o:
        return o, sp
    # ⚑ outside the barrel's own subtree, ASK THE SHAPE DB FIRST — it records what this file
    # actually referenced pre-strip. Falling straight through to the ranked catalog is how the
    # wrong `V₄` (a `Σ Bool Bool`) got written into 7 files whose shape data named Bijection.
    o, sp = owner_from_shape(leaf, near)
    if o and _owner_admissible(o, near):
        return o, sp
    o, sp = owner_by_catalog(leaf, near)
    return (o, sp) if _owner_admissible(o, near) else (None, None)


def fix_barrel(out, dry=False):
    """Repoint every name of a now-empty barrel import onto its true owner. Returns #fixed."""
    fixed = 0
    for w in BARREL_W.finditer(out):
        path = os.path.relpath(w.group("file"), os.getcwd())
        barrel = w.group("mod")
        try:
            src = open(path).read()
        except OSError:
            continue
        if barrel == "_":
            # ⚑ an APPLIED barrel (`open import M 1 public hiding (…) renaming (…)`) is reported
            # against module `_`, the ANONYMOUS application — there is no name to look up, so
            # resolve by LOCATION and read the real module out of the statement itself.
            at = _stmt_at(src, int(w.group("line")))
            if not at:
                continue
            s0, s1, text = at
            mm = re.match(r"\s*open\s+(?:import\s+)?([\w.-]+)", text)
            if not mm:
                continue
            barrel = mm.group(1)
        else:
            st = _stmt_span(src, barrel)
            if not st:
                continue
            s0, s1, text = st.start(), st.end(), st.group(0)
        # ⚑ Agda names an ALIASED import by its alias ("The module S4 doesn't export …"), and an
        # alias is not a module — resolving it is what lets the barrel's own import list be read.
        al = re.match(r"(?:open )?import ([\w.-]+) as (\w+)(?![\w.-])", text) \
             or re.match(r"open import ([\w.-]+) as (\w+)(?![\w.-])", text)
        real = al.group(1) if al else barrel
        using = re.search(r"using \(([^)]*)\)", text, re.S)
        renam = re.search(r"renaming \(([^)]*)\)", text, re.S)
        plain = [n.strip() for n in re.split(r"[;\s]+", using.group(1)) if n.strip()] if using else []
        pairs = []
        if renam:
            for p in renam.group(1).split(";"):
                q = p.split(" to ")
                if len(q) == 2:
                    pairs.append((q[0].strip(), q[1].strip()))
        by_owner, unresolved = {}, []
        for n in plain:
            o, sp = _owner_for(n, real, path)
            (by_owner.setdefault(o, ([], []))[0].append(sp) if o else unresolved.append(n))
        for a, b in pairs:
            o, sp = _owner_for(a, real, path)
            (by_owner.setdefault(o, ([], []))[1].append((sp, b)) if o else unresolved.append(a))
        if not by_owner:
            # ⚑ T3 ⟡pd-barrel-delete-evidence. Delete ONLY when AGDA says the statement exports
            # none of its names — never merely because OUR resolver failed on all of them. Those
            # differ exactly when a name is real but unresolvable (a pattern synonym is not an
            # importable qname and appears in no interned core), and the difference cost a
            # working import plus a permanent residual file.
            missing = {n.strip() for n in re.split(r"[;\s]+", w.group("names") or "") if n.strip()}
            requested = set(plain) | {a for a, _ in pairs}
            if missing and not (requested - missing):
                new = src[:s0] + src[s1:]
                if new != src and not dry:
                    _write(path, new)
                print(f"    {path}: dropped DEAD `open {barrel} using (…)` "
                      f"(Agda: exports none of {len(requested)})")
                fixed += 1
            else:
                keep = sorted(requested - missing)
                print(f"    ! {path}: {barrel} unresolved {sorted(requested & missing)}"
                      f"{f'; KEEPING live {keep}' if keep else ''} — not deleting")
            continue
        lines = []
        # ⚑ T9: if this was `import <M> as <alias>`, the ALIAS may still be load-bearing —
        # V4-Embedding writes `V4.·`, which resolves through `Operations`. Replacing the whole
        # statement with per-owner imports would silently destroy that binding, so keep the
        # alias (bare `import … as …` binds only the qualified form) alongside the repoints.
        if al and re.search(rf"(?<![\w.-]){re.escape(al.group(2))}\.", re.sub(r"--[^\n]*", "", src)):
            lines.append(f"import {al.group(1)} as {al.group(2)}")
        for o, (us, rs) in sorted(by_owner.items()):
            # never re-import a name the file already gets from this same owner elsewhere
            us = [u for u in us if not re.search(
                rf"^open import {re.escape(o)}(?![\w.-])[^\n(]*using \([^)]*(?<![\w]){re.escape(u)}(?![\w])",
                src[:s0] + src[s1:], re.M)]
            if not us and not rs:
                continue
            # ⚑ T12: a PARAMETERIZED owner must be APPLIED here too. `fix_barrel` built the
            # statement by hand and never supplied arguments, so a correctly-resolved owner
            # still produced `Permutation : (A : Set) → Set` — the `Stab` residual, whose owner
            # was right for four runs while the import was unusable.
            oargs = ""
            if _module_params(o):
                a = application_args(o, path)
                # ⚑ a statement ABOVE the module header cannot mention a module PARAMETER —
                # rewriting a pre-header import into an applied one puts `n` out of scope.
                hdr = re.search(r"^module\s", src, re.M)
                if a and hdr and s0 < hdr.start() and \
                   any(t in module_path(_module_params(path, ""))
                       for t in re.findall(r"[A-Za-z_][\w′]*", a)):
                    print(f"    ! {path}: {o} needs a module parameter, but this import is "
                          f"ABOVE the module header — leaving {sorted(us)} unbound")
                    continue
                if not a:
                    print(f"    ! {path}: {o} is parameterized and its arguments are not in "
                          f"scope — leaving {sorted(us + [x for x, _ in rs])} unbound")
                    continue
                oargs = " " + a
            seg = f"open import {o}{oargs}"
            seg += f" using ({'; '.join(us)})" if us else (" using ()" if rs else "")
            if rs:
                seg += f" renaming ({'; '.join(f'{a} to {b}' for a, b in rs)})"
            lines.append(seg)
        if not lines:                       # everything it asked for is already imported
            new = src[:s0] + src[s1:]
            if new != src:
                if not dry:
                    _write(path, new)
                print(f"    {path}: dropped REDUNDANT `{barrel}` import (all names already in scope)")
                fixed += 1
            continue
        if unresolved:
            print(f"    ! {path}: unresolved from {barrel}: {', '.join(unresolved)}")
        new = src[:s0] + "\n".join(lines) + src[s1:]
        if new == src:                      # idempotence guard — never report a no-op as a fix
            continue
        if not dry:
            _write(path, new)
        print(f"    {path}: barrel {barrel} → {len(by_owner)} owner(s): "
              f"{', '.join(sorted(o.rsplit('.', 1)[-1] for o in by_owner))}")
        fixed += 1
    return fixed


# ── ⟡paydown-applied-opens ───────────────────────────────────────────────────────────────────
# A PARAMETERIZED wrapper (`module Newman (_⇒_ : …) where open import RewriteConfluence _⇒_ …`)
# is a re-export conduit at a supplied argument. Its consumer writes `open Newman _↦_ …`, and
# when the wrapper's re-export is stripped Agda reports:
#     The module _ doesn't export the following: SN WCR …
# — module `_`, the ANONYMOUS application — so there is no name to resolve. Resolve by LOCATION
# instead, recover the OWNER from the wrapper's own body, and REDO THE APPLICATION at the owner:
#     open Newman _↦_ using () renaming (SN to SN-Acc; …)
#  →  open import Substrate.Foundation.RewriteConfluence _↦_ using () renaming (SN to SN-Acc; …)
# (No exemption for the wrapper: a narrowed re-export is still a re-export — user, 2026-07-27.)
def fix_applied_open(out, dry=False):
    """Repoint `open <Wrapper> <args>` onto the wrapper's OWNER, re-applying <args>."""
    fixed = 0
    for w in BARREL_W.finditer(out):
        if w.group("mod") != "_":
            continue
        path = os.path.relpath(w.group("file"), os.getcwd())
        try:
            src = open(path).read()
        except OSError:
            continue
        span = _stmt_at(src, int(w.group("line")))
        if not span:
            continue
        a, b, text = span
        m = re.match(r"^(?P<ind>\s*)open\s+(?P<wrap>[\w.-]+)(?P<rest>.*)$", text, re.S)
        if not m or m.group("wrap") == "import":
            continue
        owner = _wrapper_owner(path, m.group("wrap").rsplit(".", 1)[-1])
        if not owner:
            print(f"    ! {path}:{w.group('line')}: applied-open — no owner for {m.group('wrap')}")
            continue
        # A wrapper is ONLY ever a conduit, so repoint EVERY use of it in this file — including
        # the inline `let open <Wrapper> <args> in …` form, which is not a standalone statement
        # and so is invisible to a location-anchored rewrite. Then drop the now-dead
        # `using (module <Wrapper>)` from the import that brought the wrapper in.
        wrap = m.group("wrap").rsplit(".", 1)[-1]
        new = re.sub(rf"(?<![\w.-])open\s+{re.escape(wrap)}(?![\w.])",
                     f"open import {owner}", src)
        new = re.sub(rf"^open import [\w.-]+ using \(module {re.escape(wrap)}\)\n", "", new, flags=re.M)
        # ⚑ AGDA CONSTRAINT: `import` is NOT a valid let binding. The inline form
        # `let open <Wrapper> args in …` may only OPEN an already-imported module, so emit a
        # top-level `import <Owner>` and leave the let as a bare `open <Owner> args`.
        if f"let open import {owner}" in new:
            new = new.replace(f"let open import {owner}", f"let open {owner}")
            anc = re.search(r"^module [^\n]*\n", new, re.M)
            if anc and f"\nimport {owner}\n" not in new:
                new = new[:anc.end()] + f"import {owner}\n" + new[anc.end():]
        new = re.sub(rf"[;\s]*module {re.escape(wrap)}(?![\w.])", "", new) \
            if f"module {wrap}" in new and "using (" in new else new
        if new == src:
            continue
        if not dry:
            _write(path, new)
        print(f"    {path}: applied-open {m.group('wrap')} → {owner}   [application redone at the owner]")
        fixed += 1
    return fixed


def fix_wrapper_open(out, dry=False):
    """Rewrite `open <Wrapper> <args>` → `open import <Owner> <args>`. Returns #fixed.

    A parameterized WRAPPER whose whole body was `open import <Owner> _⇒_ … public` exports
    nothing once the re-export is gone, and its consumers fail with a plain `[NotInScope]` — no
    `ModuleDoesntExport` warning, because a `let open W (…) in` requests no names. `fix_applied_
    open` already knows this transform but is driven by the warning's LOCATION, so it never sees
    this shape. Resolve by NAME instead: the owner is recovered from the wrapper's own body, and
    the consumer REDOES THE APPLICATION at the owner — the paydown, not a restored re-export."""
    m = NOT_IN_SCOPE.search(out)
    if not m:
        return 0
    name = m.group("name")
    if "." in name:
        return 0
    path = os.path.relpath(m.group("file"), os.getcwd())
    try:
        src = open(path).read()
    except OSError:
        return 0
    self_mod = module_path(path, "")
    fixed = 0
    for wrapper in dict.fromkeys(re.findall(r"(?<!import )\bopen\s+([A-Z][\w′]*)(?![\w.-])", src)):
        owner, _a = _applied_owner(wrapper, name)
        if not owner or owner == self_mod or not _module_exports(owner, name):
            continue
        # ⚑ a `let open W (…) in …` sits mid-expression, where `open import` is a parse error,
        # so the rewrite is `open <Owner> <args>` (legal in both positions) plus a bare
        # top-level `import <Owner>` to bring the qualified name into scope. Same transform
        # in both places, which is why the wrapper's two call sites stay consistent.
        new = re.sub(rf"\bopen\s+{re.escape(wrapper)}(?![\w.-])", f"open {owner}", src)
        if not re.search(rf"^(?:open )?import {re.escape(owner)}(?![\w.-])", new, re.M):
            anchor = re.search(r"^module [^\n]*\n", new, re.M)
            if anchor and not re.search(r"\bwhere\b", new[anchor.start():anchor.end()]):
                anchor = re.compile(r"^[^\S\n]*where\b[^\n]*\n", re.M).search(new, anchor.end())
            if not anchor:
                continue
            new = new[:anchor.end()] + f"import {owner}\n" + new[anchor.end():]
        if new == src:
            continue
        if not dry:
            _write(path, new)
        print(f"    {path}: wrapper `open {wrapper}` → `open {owner}` (redo the application at the owner)")
        src, fixed = new, fixed + 1
    return fixed
