#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_source.py — the SOURCE ORACLE layer of `scope_fix`, split out verbatim.

⚑ WHY THIS FILE EXISTS, AND IT IS NOT TIDINESS. `scope_fix.py` reached 2,142 code lines,
over the 1,200-line cap (`pycodemod.py --size`). The rule (user, 2026-08-11): *"if a file
is so big you have to patch-edit it, then it needs to be decomposed into smaller files."*
It fired after a four-edit sequence on another over-cap module left it unparseable — two of
the four edits repaired damage the PREVIOUS edit caused, because no edit could see the
region whole. `scope_fix` REWRITES AGDA SOURCE, so that failure mode here is corrupted
source, not a broken query (precedent: a statement-span regex gutted 33 Agda files, twice).

WHAT IS HERE, AND WHY THE SEAM IS *THIS* SEAM. Everything below answers a question about
the CURRENT (or `HEAD`) Agda source — "what does this module export / import / apply /
rename / bind" — and, with it, the single write path those answers must stay coherent with.
The `fix_*` error handlers and the resolvers that RANK candidates sit above it, in
`scope_fix.py`, and call downward only. Verified with `pycodemod --calls` per name before
the cut: nothing in this file reaches `add_import`, `add_renaming_import`, or any `fix_*`.

⚑ THE SEAM WAS CHOSEN BY A MEASUREMENT ABOUT GLOBALS, NOT BY TOPIC. A `global X` statement
rebinds the name only in the module that DEFINES it. `_write` sets `_IMPORTS = None` to
invalidate the import-graph cache — that invalidation is what makes the cycle guard honest
after the loop's own edits (its docstring records that it "used to be computed once and
never refreshed"). Had `_write` been left in `scope_fix.py` while `_import_graph` moved
here, `_write` would have rebound a global in the OTHER module and `_import_graph` would
have gone on reading a stale graph — a silent defeat of the guard, in a tool that writes.
So the rule the cut follows is:

  * a `global`-REBOUND cache may not straddle the seam  → `_IMPORTS` + `_write` +
    `_import_graph` + `_would_cycle` + `_owner_admissible` all live here, together;
  * an item-MUTATED dict may straddle safely (the object is shared, never rebound) →
    `_ADDED` is written here by nothing and read by `scope_fix.fix_ambiguous`; `_DEMAND`
    and `_DEMAND_CANDS` stay above, in `scope_fix`, where `_demand_of` owns them.

`_EXPORTS`, `_LOCAL_MOD`, `_HEAD_TEXT` and `_RENAME_IDX` are mutated ONLY by functions in
this file, which is what makes them movable at all.

⚑ THE ⚑ COMMENTS ARE THE POINT AND THEY MOVED VERBATIM. Nearly every function here carries
a block recording the measured defect that produced it. This is a PURE RELOCATION: no
signature, no body, and no comment was altered. `scope_fix.py` re-exports every name below,
so `scope_fix.X` and `from scope_fix import X` keep working unchanged.

⚑ THE `vfs` MIGRATION IS NOT DONE, AND THE REMAINDER IS A CENSUS RATHER THAN A CLAIM.
Six read sites have been migrated across three dispatches (`_wrapper_owner` ×2,
`_parent_kind`, `_alias_target`, `_module_params`, `_rename_index`). Re-derive what is
left with `pycodemod --calls open scratch/scope_source.py` — it reported SIX at the
close of ⟡rename-index-sixth-site, 2026-08-25, and they are NOT one more instance of
the same thing:

  `_write`             ⚑ CLOSED 2026-08-26 (⟡scope-source-write-codec). Now routes
                       through `vfs.write` — UTF-8, atomic, honours `vfs.DRY_RUN`,
                       keeps its own `_IMPORTS = None`. This is the layering
                       `vfs.write`'s own docstring prescribes.
  `_nearest_reexporter` ⚑ CLOSED 2026-08-26 (⟡nearest-reexporter-grep). The
                       `subprocess.run(["grep", …])` is replaced by
                       `agda_defs.reexporters_by_target()`, a mode added to the corpus
                       authority for it. The grep was wrong in BOTH directions —
                       6 false negatives (a `min(i+6)` tail window) and 5 false
                       positives (an unanchored `-F` prefix matching `X.Core.Sub` for
                       owner `X.Core`). Its bare `open()` went with it.
  `_reexports_fields`  SELF-DISCOVERED (built from a module name), `return False`
  `_in_scope`          CALLER-SUPPLIED `path`, `return False` — and its `False` is a
                       positive answer three `application_args` callers ACT on
  `application_args`   CALLER-SUPPLIED `path`, `return ""`
  `_applied_via_import` CALLER-SUPPLIED `path`, `return ""`

⚑ THE LAST FOUR ARE ONE CODEC DECISION EACH, NOT ONE DECISION FOUR TIMES — the two
axes (caller-supplied vs self-discovered; act-on-it vs decline) have to be re-run per
site, and a uniform answer across them is the tell that they were not. Left un-migrated
deliberately, on the precedent that produced Ⓥ18 and this item.

⚑⚑⚑ A **SEVENTH SITE** EXISTS AND THE CENSUS ABOVE NEVER NAMED IT — `_local_module_file`
runs `subprocess.run(["grep", "-rlE", …, "Substrate"])` to find the file declaring a
NON-file module. It was invisible to the six-item census because that census was keyed
on `pycodemod --calls open` — a query about the CODEC — and this site's defect is the
STANDING-RULE one (a textual query against a structured artifact), with no bare `open()`
of its own to report. ⚑ `census-keyed-on-one-spelling`, in this file's own remainder
list: two greps lived here, the census named one, and the one it named was the one that
also happened to hold an `open()`. A fact about the QUERY reported as the population.

⚑ IT IS **NOT** CLOSED BY THIS ROUND, AND IT IS NOT THE SAME FIX. `_nearest_reexporter`
had an authority waiting for it (`agda_defs.reexport_index`, needing only a transpose);
`_local_module_file` asks *"which file declares `module <name>`"* for a LOCAL, non-file
module, and `agda_defs`' index is keyed on FILE modules. Whether that is a missing
`agda_defs` mode or a genuinely different index is the open question — filed as
⟡local-module-file-grep rather than answered here, because guessing it wrong writes the
wrong file into a resolution. Its `if len(files) == 1` refusal-on-ambiguity is at least
already the right discipline.

⚑rederive: the raw-source regex debt and the comment-masking gap declared in `scope_fix`'s
own header apply to this file too — it is where most of those ~40 regexes now live. That is
DECLARED debt carried across the split, deliberately unpaid here: paying it CHANGES
BEHAVIOUR and wants its own commit with a build behind it.
"""
import os
import re
import subprocess
import sys

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import mask_comments as _mask   # THE comment authority; never re-derive
from agda_lex import module_path              # THE path<->module authority; never re-derive
import agda_lex                               # module_scopes/binds_at — THE telescope authority
import agda_defs                              # THE Agda-corpus authority (re-export census)
import vfs                                    # THE read/write seam; codec is never the locale's


def _source():
    """The vfs source these reads are addressed against — the CWD, not the repo root.

    ⚑ THIS IS NOT `vfs.WorkingTree()`'s DEFAULT AND THE DIFFERENCE IS LOAD-BEARING.
    `vfs.WorkingTree()` roots at the REPO; every path in this file is relative to
    `agda/` (`os.walk("Substrate")`, `mod.replace(".","/") + ".agda"`), because that is
    where `scope_fix` is run from. Passing the default would join `Substrate/...` onto
    the repo root and report every module ABSENT — the read would succeed at being
    wrong, which is worse than the locale bug it replaces.

    ⚑ It is a FUNCTION, not a module-level constant, because `os.getcwd()` must be read
    at the point of use: a constant bound at import time freezes a directory a caller
    may `chdir` out of (`reread-meters-toctou`).

    ⚑ AND IT IS THE SEAM FOR `--at HEAD`. Returning a `source` OBJECT rather than
    reading directly is what later makes a revision a PARAMETER instead of a mode:
    `vfs.Rev("HEAD")` substitutes here with no change at any read site.
    """
    return vfs.WorkingTree(os.getcwd())


def _is_file_module(mod):
    return os.path.exists(mod.replace(".", "/") + ".agda")


def _module_params(module):
    """The parameter names of a PARAMETERIZED module, e.g. `module …Cyclic.Base (n : ℕ) where`.

    ⚑ ⟡module-params-fifth-site. Was a bare `open()` under `except OSError: return []` —
    the FIFTH instance of the locale default in this file, and the widest: 24 call sites
    across 8 modules (`pycodemod --calls _module_params --root scratch`). It was named and
    left un-migrated by the agent that did the other four, rather than swept in silently.

    ⚑⚑ THE DECODE FAILURE RAISES, and the axis that puts it here is ACT-ON-IT, not
    caller-supplied-vs-self-discovered. On that first axis it is SELF-DISCOVERED (we
    build the path from a module name), which is `_alias_target`'s side — but the second
    axis overrides, exactly as it does for `_parent_kind`:

      `[]` IS NOT THIS FUNCTION'S "DON'T KNOW". It is the POSITIVE ANSWER *"this module
      is parameterless"*, and all 24 consumers act on it by taking the no-application
      branch — `if not _module_params(o): return ""` (scope_alias:163), `if
      _module_params(module):` (scope_edit:257, scope_barrel:169), `len(...)`
      (scope_store:384). What they then WRITE is a bare `open import M`.

    And `scope_edit`'s own docstring (:52) states the cost of that being wrong:
    importing a parameterized module unapplied binds the module-as-function form, so
    `power k` becomes `(n : ℕ) → ℕ → Word (Gen n)` and every use fails `[UnequalTerms]`.
    A telescope sitting behind a bad byte would be read as "no telescope" and the tool
    would write that import into Agda source. So an undecodable module must be LOUD.

    ⚑ ABSENCE still returns `[]` — unchanged, and legitimately so: nothing there says
    `(n : ℕ)`, and the old OSError contract is what the 24 callers are written against.
    The split is `_parent_kind`'s exactly: absence is an answer, a codec accident is not.
    """
    r = vfs.read(module.replace(".", "/") + ".agda", _source())
    if r.presence is not vfs.Presence.PRESENT:
        return []                         # ABSENT/unreadable ⇒ the old default, unchanged
    src = r.text()                        # strict UTF-8; an undecodable module RAISES
    m = re.search(rf"^module {re.escape(module)}\b(?P<params>.*?)\bwhere", src, re.S | re.M)
    if not m:
        return []
    return re.findall(r"\(\s*([A-Za-z_][\w′]*)[^)]*:", m.group("params"))


def _stmt_span(src, mod):
    """The whole `open import mod …` / `open mod …` statement, plus indented continuations.

    The bare `open <alias> using (…)` form matters: an alias pointing at a stripped barrel binds
    NOTHING, and that dead statement is what leaves a constructor as a pattern variable.

    ⚑ T9 ⟡pd-aliased-barrel: Agda reports an ALIASED import by its ALIAS — `open import
    Substrate.Groups.V4 as V4 using (…)` is reported as "The module V4 doesn't export …". The
    alias is not a file module, so the two forms above never match and `fix_barrel` silently did
    nothing. `Axes.agda:33` is exactly this, and because warnings are failures it blocked every
    consumer of `Substrate.Axes` — two of the five residual files, neither of which has any
    defect of its own."""
    m = re.search(rf"^open (?:import )?{re.escape(mod)}(?![\w.-])[^\n]*(?:\n[ \t]+[^\n]*)*",
                  src, re.M)
    if m:
        return m
    return re.search(rf"^(?:open )?import [\w.-]+ as {re.escape(mod)}(?![\w.-])"
                     r"[^\n]*(?:\n[ \t]+[^\n]*)*", src, re.M)


def _stmt_at(src, lineno):
    """The statement beginning at 1-based `lineno`, plus its indented continuation lines."""
    lines = src.split("\n")
    i = lineno - 1
    if i < 0 or i >= len(lines):
        return None
    j = i + 1
    while j < len(lines) and (lines[j].startswith((" ", "\t")) and lines[j].strip()
                              and not re.match(r"^\s*(open|import|module)\b", lines[j])):
        j += 1
    start = sum(len(l) + 1 for l in lines[:i])
    return start, start + sum(len(l) + 1 for l in lines[i:j]) - 1, "\n".join(lines[i:j])


def _wrapper_owner(path, wrapper):
    """(owner-module, #params) for a parameterized wrapper re-exported as `module <wrapper>`.

    ⚑ ⟡scope-source-remainder. Both reads were bare `open()` — the locale default over a
    corpus of `σ`/`∷`/`𝟙`. THE TWO SITES GET DIFFERENT CODEC BRANCHES, because their
    falsy answers mean different things to the caller:

      · `path` (the CONSUMER, arg 1) — RAISES on an undecodable read, and does NOT catch
        the absence either. It always did: the original had no `try` here at all, so a
        missing consumer already propagated `OSError`. That is right — the caller HANDED
        us this path; if we cannot read the file we were pointed at, every answer about
        it is a fabrication, and this function's `None` means "no wrapper re-export here",
        a positive claim about a file we would not have read.
      · `home` (the OWNER, discovered by us) — returns `None`, matching the
        `os.path.exists(home)` guard one line above it that already treats an unreachable
        owner as "no answer". A wrapper whose owner is undecodable is a wrapper we cannot
        resolve, which is exactly what `None` says here; raising would let one mangled
        module in the tree abort a resolution that was about to decline anyway.

    ⚑ So the asymmetry is CALLER-SUPPLIED vs SELF-DISCOVERED, and it is the same split
    `_module_text` (raise) and `_import_graph` (skip) already make one level up."""
    src = vfs.read(path, _source()).text()      # PRESENT-or-raise: see above
    m = re.search(rf"open import ([\w.-]+)[^\n]*\bmodule {re.escape(wrapper)}\b", src)
    if not m:
        return None
    home = m.group(1).replace(".", "/") + ".agda"
    if not os.path.exists(home):
        return None
    hr = vfs.read(home, _source())
    if hr.presence is not vfs.Presence.PRESENT:
        return None                             # raced away / unreadable ⇒ no answer
    try:
        wsrc = hr.text()
    except UnicodeDecodeError:
        return None                             # a wrapper we cannot resolve, not a defect to raise
    w = re.search(rf"^module {re.escape(wrapper)}\b(.*?)^\s*where", wsrc, re.S | re.M)
    if not w:
        return None
    body = wsrc[w.end():]
    o = re.search(r"^\s*open import (Substrate[\w.-]+)", body, re.M)
    return o.group(1) if o else None


# ── ⟡paydown-cycle-guard ─────────────────────────────────────────────────────────────────────
# An owner that (transitively) imports the CONSUMER cannot be imported by it: Agda rejects the
# whole component with [CyclicModuleDependency]. This is not a ranking preference but a hard
# constraint, so it is checked before any import is written. (Binding `e` to
# `…Trace.V4FullCocycle` closed exactly such a cycle: FourProduct → Bundle → V4FullCocycle →
# V4 → FourProduct.)
#
# ⚑⚑ THE CACHE IS KEYED ON ITS SOURCE, AND THE TWO LIFETIMES ARE DIFFERENT KINDS.
# Until 2026-08-25 `_IMPORTS` was a bare global keyed on NOTHING, invalidated by `_write`.
# That is correct for the WORKING TREE and only for it: the tree is mutable, our own edits
# are the mutation, and `_write` is where they happen. It is the wrong shape the moment a
# `Rev` can be asked for — one `_IMPORTS` would serve HEAD's graph to a working-tree caller
# or the reverse, silently, inside a CYCLE GUARD in a tool that writes Agda source.
#
# So the two sources get two stores, because they have two LIFETIMES — not one store with a
# fancier key:
#
#   `_IMPORTS`        the WORKING TREE's graph. Mutable, so it is INVALIDATED (`_write`).
#                     Exactly the old object and the old invalidation, unchanged.
#   `_IMPORTS_REV`    keyed graphs for IMMUTABLE sources. A revision's tree cannot change
#                     under us, so there is nothing to invalidate and `_write` must not
#                     touch it — clearing it would be a lie about what a commit can do.
#
# ⚑⚑⚑ THE ASYMMETRY IS INHERITED FROM `vfs`, NOT INVENTED HERE. `head_read` caches PRESENT
# and ABSENT (facts about a REVISION — immutable) and refuses to cache BROKEN (a fact about
# the ATTEMPT), because "memoizing it would freeze one bad moment into the process". Same
# distinction, one level up: a graph over an immutable source is a fact about that source;
# a graph over the working tree is a fact about a MOMENT of it, and a moment expires.
_IMPORTS = None
_IMPORTS_REV = {}


def _graph_key(source):
    """The cache identity of `source`, or `None` for the mutable working tree.

    ⚑ `None` is not "no key" — it is the WORKING TREE's key, and it selects the
    invalidated store. A `Rev` keys on `(rev, root)`: the root is load-bearing because
    `Rev("HEAD")` against two different repositories names two different trees, and a
    key of `rev` alone would serve one repo's graph for the other.

    ⚑ A source this function does not RECOGNISE gets no cache at all rather than a
    default bucket — `Presence.of`'s discipline: an unrecognised thing silently reading
    as a known one is the false-green shape. It is spelled as a sentinel object so it
    can never collide with a real key.
    """
    if isinstance(source, vfs.WorkingTree):
        return None
    if isinstance(source, vfs.Rev):
        return ("Rev", source.rev, source.root)
    return _UNCACHEABLE


_UNCACHEABLE = object()


def _import_graph(source=None):
    """module → set(imported module), over `source` (default: the working tree).

    ⚑ The default is `_source()`, NOT `vfs.WorkingTree()`: every path here is relative
    to `agda/`. See `_source`'s own note — the default root would report every module
    ABSENT, a read that succeeds at being wrong.
    """
    global _IMPORTS
    source = source or _source()
    key = _graph_key(source)
    if key is None:
        if _IMPORTS is not None:
            return _IMPORTS
    elif key is not _UNCACHEABLE and key in _IMPORTS_REV:
        return _IMPORTS_REV[key]

    graph = {}
    # ⚑ THE WALK IS `vfs.listdir`, WHICH IS WHAT MAKES `Rev` PASSABLE. It used to be
    # `os.walk` — meaningless at a revision — and the previous item REFUSED a non-
    # WorkingTree source rather than serve a working-tree graph under a revision's key.
    # `vfs.listdir` was the successor that refusal named, and it already existed.
    #
    # ⚑⚑ THE PATTERN IS `Substrate/**` AND IT IS NOT INTERCHANGEABLE WITH THE OBVIOUS
    # `Substrate/**/*.agda`. THE TWO BRANCHES USE DIFFERENT MATCHERS — WorkingTree globs,
    # Rev fnmatches — and they disagree. MEASURED 2026-08-25 against two INDEPENDENT
    # oracles (os.walk for the tree, `git ls-tree` for the revision):
    #
    #     pattern                working tree            at HEAD
    #     Substrate/**/*.agda    3598  EXACT              2403  MISSES 6
    #     Substrate/*.agda          6  misses 3592        2409  EXACT
    #     Substrate/**           3598  EXACT              2409  EXACT
    #
    # `**/` cannot match a DEPTH-0 path in either matcher, so `Substrate/**/*.agda` drops
    # every top-level module — `Substrate.Foundation`, `Substrate.Generators`,
    # `Substrate.Cocycle`, `Substrate.Cardinality`, `Substrate.Discipline` and one more.
    # On the working tree that is invisible (glob's depth-0 miss coincides with nothing
    # the old os.walk-plus-suffix-filter also missed), so the wrong pattern LOOKS exact
    # on the branch you can easily check and silently truncates the one you cannot — into
    # `_IMPORTS_REV`, which is NEVER invalidated, feeding a CYCLE GUARD. The suffix test
    # is therefore done HERE, in code, rather than delegated to the pattern.
    #
    # ⚑ This is also why `_head_text`'s docstring figure of "2403" is short by 6: it was
    # derived with `--census 'agda/Substrate/**/*.agda'`. The corpus is 2409 at HEAD.
    #
    # ⚑ THE PREFIX IS DERIVED, NOT ASSUMED. Every path in this file is relative to the
    # CWD (`agda/`), but a `Rev` is keyed by paths relative to ITS OWN ROOT — the repo,
    # normally. Hardcoding `"agda/"` would bake in one caller's layout and silently
    # enumerate nothing for a `Rev` rooted anywhere else. So it is computed from the two
    # roots that are actually in play, and an unrelated root is REFUSED rather than
    # guessed at: a wrong prefix yields an EMPTY graph, which a cycle guard reads as
    # "nothing reaches anything" — a false all-clear in a tool that writes Agda source.
    prefix = ""
    if not isinstance(source, vfs.WorkingTree):
        rel = os.path.relpath(os.getcwd(), source.root).replace(os.sep, "/")
        if rel.startswith(".."):
            raise ValueError(
                "_import_graph: cwd %s is not inside %s's root %s, so the Substrate "
                "paths this module uses cannot be addressed at that source."
                % (os.getcwd(), source, source.root))
        prefix = "" if rel == "." else rel + "/"
    for p in vfs.listdir(prefix + "Substrate/**", source):
        if not p.endswith(".agda"):
            continue
        mod = module_path(p[len(prefix):] if prefix else p, "")
        # ⚑ ⟡vfs-encoding. Was `open(p).read()` — the LOCALE default over a corpus
        # of `σ`/`∷`/`𝟙`. MEASURED 2026-08-25: under `LC_ALL=C` that spelling raises
        # `UnicodeDecodeError` on a real module (`Substrate/S5/S5EEABridge.agda`,
        # byte 0xe2 at offset 137); through this seam the same file decodes to the
        # identical sha1 under C.UTF-8, C, and en_US.ISO-8859-1. UTF-8 is not a guess
        # here — it is what agda emits and what `vfs.write` already writes.
        r = vfs.read(p, source)
        if r.presence is not vfs.Presence.PRESENT:
            continue                     # ABSENT (raced away) / BROKEN (perm, dir) — as before
        try:
            src = r.text()               # strict UTF-8
        except UnicodeDecodeError:
            # ⚑ BEHAVIOUR PRESERVED DELIBERATELY, AND IT IS *NOT* THE STRICT CHOICE.
            # The old `except OSError` never covered a decode failure at all
            # (`UnicodeDecodeError` is a `ValueError`), so a mangled module used to
            # take down the whole graph build mid-walk. This is a whole-tree WALK
            # feeding a CYCLE GUARD: one undecodable file must not deny the guard
            # every OTHER edge, which is what a raise here would do. So it is skipped
            # exactly like an unreadable one — the guard degrades on one module
            # instead of failing closed on all ~3.5k.
            continue
        graph[mod] = set(re.findall(r"^\s*(?:open\s+)?import\s+([\w.-]+)", src, re.M))

    if key is None:
        _IMPORTS = graph                 # the mutable store `_write` invalidates
    elif key is not _UNCACHEABLE:
        _IMPORTS_REV[key] = graph        # immutable: cached forever, never invalidated
    return graph


# ⚑ T6 ⟡pd-ambiguity-rollback. The tool only ever ADDS `using (…)`, so it can create ambiguity
# but never resolve it — `[AmbiguousName]` survived all six runs untouched, byte-identical.
# Rolling back requires knowing which import WE added; `add_import` returned a description and
# persisted nothing. This ledger is that memory: (file, name) → module.
#
# ⚑ IT LIVES HERE, WITH THE WRITE PATH, THOUGH ITS WRITER (`add_import`) AND ITS READER
# (`fix_ambiguous`) BOTH SIT ABOVE. That is safe precisely because it is only ever ITEM-mutated
# (`_ADDED[k] = v` / `.pop`), never rebound — the dict object is shared across the seam. A
# `global`-rebound cache in the same position would NOT be, which is the distinction the split
# is built on.
_ADDED = {}


def _write(path, new):
    """The ONE write path. Invalidates the import-graph cache, which is what makes the cycle
    guard honest after the loop's own edits (it used to be computed once and never refreshed).

    ⚑⚑ IT INVALIDATES THE WORKING-TREE STORE *ONLY*, AND THE OMISSION IS THE POINT.
    `_IMPORTS_REV` holds graphs over IMMUTABLE sources; a write to the working tree cannot
    change what a revision contains, so clearing it would not be extra safety — it would be
    a false statement about what a write can reach, and it would re-pay a whole-tree walk
    per edit for nothing. The invalidation follows the MUTATION, not the cache.

    ⚑⚑⚑ THE WRITE IS STILL THE LOCALE CODEC, AND IT IS THE ASYMMETRY THE SIX READ
    MIGRATIONS CREATED. `open(path, "w")` encodes with whatever `locale.getpreferredencoding()
    ()` returns, over a corpus of `σ`/`∷`/`𝟙`/`⟦⟧`. Six READ sites in this file have now
    been moved onto `vfs` one at a time; the ONE WRITE site — which this module's own
    header calls *"the single write path those answers must stay coherent with"* — was
    never in any of their scopes, so the seam is UTF-8 in and locale out. `vfs.write` is
    UTF-8 on the wire, atomic, and carries the `DRY_RUN` refusal, none of which this has.

    ⚑⚑⚑⚑ MIGRATED (⟡scope-source-write-codec, 2026-08-26), AND THE LAYERING IS
    `vfs.write`'s OWN, NOT ONE INVENTED HERE. Its docstring names this seam by name:

        tool --apply -> edit_snapshot.guard -> scope_source._write -> vfs.write

    and says this function "should CALL this for its encoding and atomicity, and keep
    its own `_IMPORTS = None`". That is exactly what happens below — the invalidation
    stays, because `vfs.write` deliberately does NOT touch caches. Three properties
    arrive that a bare `open(path, "w")` never had:

      · UTF-8 ON THE WIRE, by construction rather than by whatever `LANG` is. The
        corpus is `σ`/`∷`/`𝟙`/`⟦⟧`; the six READ sites were migrated one at a time and
        left the seam UTF-8 in / locale out, which is the asymmetry this closes.
      · ATOMIC (temp + `os.replace`). `open(p, "w")` TRUNCATES before it writes, so an
        interrupted write destroys the source — over Agda files whose only other copy
        may be an uncommitted working-tree edit.
      · THE `DRY_RUN` REFUSAL, which is a TRIPWIRE here rather than a mode. See below.

    ⚑⚑ WHY `vfs.DRY_RUN` IS SAFE TO ARM FROM `scope_fix --dry-run`, AND THE CAVEAT THAT
    DECIDES IT. `--dry-run` means NO BYTE OF THE WORKING TREE DIFFERS AFTERWARD — a
    statement about the FILESYSTEM, not about the tool's internal passes. The dangerous
    shape is a tool that WRITES THEN RESTORES even on the dry path (`prune_leaf_opens`
    does exactly that, and correctly arms its snapshot with a hardcoded
    `intent="apply"`). Such a tool must set `vfs.DRY_RUN = False` deliberately.

    ⚑ `scope_fix` DOES NOT HAVE THAT SHAPE, AND IT WAS VERIFIED RATHER THAN ASSUMED.
    `fix()` threads `dry` down into every handler, and `pycodemod --guarded _write
    --root scratch` reports all 34 call sites in the `scope_*` family sitting behind
    either `if not dry` (11 directly) or an earlier `if dry: return True` early-return
    (the rest — `scope_alias:110/204/313/351/378` each read that way when opened). No
    reachable path writes under `--dry-run`, so arming `DRY_RUN` can never fire in
    normal operation.

    ⚑⚑⚑ WHICH IS PRECISELY WHAT MAKES IT WORTH ARMING. `vfs._declare` RAISES on
    `DRY_RUN` — it does not silently skip. So this is not a second suppression layer
    that could mask a missing guard; it is an assertion that the guards above are
    complete. A future handler that forgets its `if not dry` gets a loud
    `RuntimeError` under `--dry-run` instead of silently mutating the tree, which is
    the one failure mode a preview flag exists to prevent.
    """
    global _IMPORTS
    vfs.write(path, new, _source())      # UTF-8, atomic, honours vfs.DRY_RUN
    _IMPORTS = None


def _owner_admissible(owner, path):
    """⚑ T4 ⟡pd-single-source-writers. Is `owner` a legal import target for the consumer?

    These two guards used to live ONLY inside `add_import`, while `fix_barrel`,
    `fix_applied_open` and `fix_alias_repoint` each wrote imports directly — so they inherited
    neither, and one of them emitted a literal self-import (`open import …V4FullCocycle` into
    `V4FullCocycle.agda`) that Agda reported as `[CyclicModuleDependency]`. Selecting the owner
    is the right place for the check: then no writer can choose an inadmissible one."""
    if not owner or not path or not path.endswith(".agda"):
        return True
    self_mod = module_path(path, "")
    if owner == self_mod:
        return False
    return not _would_cycle(owner, self_mod)


def _would_cycle(owner, consumer_module, source=None):
    """Does `owner` already reach `consumer_module`? Then importing it closes a cycle.

    ⚑ `source` is threaded rather than defaulted-at-the-graph, so the guard and the graph
    it consults can never be addressed against different trees. Omitted ⇒ the working
    tree, which is every existing caller's contract."""
    g = _import_graph(source)
    seen, stack = set(), [owner]
    while stack:
        m = stack.pop()
        if m == consumer_module:
            return True
        if m in seen:
            continue
        seen.add(m)
        stack.extend(g.get(m, ()))
    return False


def _parent_kind(mod, parent):
    """Is `parent` a RECORD (so `parent.leaf` is a field) or a data type (so it is a ctor)?

    ⚑ ⟡scope-source-remainder. Was a bare `open()` under `except OSError: return "ctor"`.
    THE DECODE FAILURE RAISES, and that is the opposite of the OSError arm one line below
    it — deliberately, because this function has NO "don't know" value. Its miss-branch is
    `"ctor"`, a POSITIVE ANSWER: the caller writes a qualified reference on the strength
    of it. On an ABSENT module `"ctor"` is defensible (nothing says `record`, and the old
    contract is preserved); on an UNDECODABLE one it is a guess dressed as a reading —
    the `record` line we needed may be sitting right there behind the bad byte. This is
    `_module_text`'s reasoning exactly: a falsy/default answer that `scope_fix` ACTS on
    must not be manufacturable by a codec accident.
    """
    r = vfs.read(mod.replace(".", "/") + ".agda", _source())
    if r.presence is not vfs.Presence.PRESENT:
        return "ctor"                     # ABSENT/unreadable ⇒ the old default, unchanged
    src = r.text()                        # strict UTF-8; an undecodable module RAISES
    return "field" if re.search(rf"^\s*record\s+{re.escape(parent)}\b", src, re.M) else "ctor"


def _reexports_fields(mod, parent):
    """Does `mod` do `open <parent> public`? Then its FIELDS are importable names of `mod`."""
    try:
        src = open(mod.replace(".", "/") + ".agda").read()
    except OSError:
        return False
    return bool(re.search(rf"^\s*open\s+{re.escape(parent)}\b[^\n]*\bpublic\b", src, re.M))


_REEXPORTERS = {}


def _reexporters_of(owner):
    """`agda_defs.reexporters_by_target()[owner]`, asked from the root IT expects.

    ⚑⚑ THIS SEAM EXISTS BECAUSE THE OBVIOUS CALL RETURNS ZERO, SILENTLY — the exact
    trap `_source()` is written against, in a second module. `agda_defs.AG` is the
    literal `"agda"`, resolved against the CWD; `scope_fix` runs from `agda/`, so a
    bare `reexporters_by_target()` there globs `agda/agda/Substrate/**` — a directory
    that does not exist — and reports **0 rows** rather than raising. MEASURED
    2026-08-26: 151 rows / 116 targets from the repo root, 0 / 0 from `agda/`.

    That is a read that succeeds at being wrong, and it is WORSE than the grep it
    replaces: `_nearest_reexporter` would have returned `None` universally, and its
    callers DECLINE on `None`, so the resolver would have quietly stopped finding
    applied re-exporters with no error anywhere. The probe's non-default count is what
    would have caught it — and did.

    ⚑ THE FIX IS LOCAL, AND DELIBERATELY NOT A CHANGE TO `AG`. `AG="agda"` is a
    convention shared by 14 tools (`pycodemod --binding AG --root .` → 16 bindings);
    re-anchoring it in `agda_defs` alone would be a one-consumer fix to shared infra —
    sprawl by exception, and the wrong half of `fix_infra_not_route_around`. So this
    restores the root the authority documents for the duration of the call, and the
    real repair is filed rather than smuggled: ⟡agda-defs-ambient-root, which a related
    agent's ⟡ambient-root work bears directly on.

    ⚑ AND IT REFUSES THE SILENT ZERO rather than caching it. An empty index means the
    root is wrong far more often than it means the corpus has no re-exports (151 rows
    today), so an empty result is NOT memoised and NOT returned as an answer — it
    raises, naming the cause. `report presence, never absence`: a zero here would be a
    fact about the CWD reported as a fact about the substrate.
    """
    if not _REEXPORTERS:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prev = os.getcwd()
        try:
            os.chdir(root)                      # the root `agda_defs.AG` is written against
            by = agda_defs.reexporters_by_target()
        finally:
            os.chdir(prev)
        if not by:
            raise RuntimeError(
                "agda_defs.reexporters_by_target() is EMPTY from %s. That is a fact "
                "about the ROOT, not the corpus (151 rows / 116 targets are expected). "
                "`agda_defs.AG` is CWD-relative; see ⟡agda-defs-ambient-root." % root)
        _REEXPORTERS.update(by)
    return _REEXPORTERS.get(owner, ())


def _nearest_reexporter(owner, near):
    """A module that still does `open import <owner> <args> … public` — i.e. one that exports
    the APPLIED instance. Ranked by longest shared path prefix with the consumer.

    This is how a parameterized definer stays reachable after the strip: `Cyclic.Existential`
    retains `open import …ListPresentation Gen … public`, so `normalize` is importable there
    APPLIED, whereas the definer itself is only usable unapplied (and therefore wrong).

    ⚑⚑⚑ ⟡nearest-reexporter-grep — THE `subprocess.run(["grep", "-rn", …])` IS GONE, AND
    IT WAS THE LOUDEST STANDING-RULE VIOLATION IN THE TREE: a TEXTUAL query against a
    STRUCTURED artifact, living inside `scope_source.py`, in the repo whose first law
    forbids exactly this. `agda_defs` is the Agda-corpus authority and already owned the
    census (`reexport_index`, the ban's uncensused half); what it lacked was the
    TRANSPOSE, so `reexporters_by_target` was added there — a missing mode is WORK, not
    grounds for keeping the grep.

    ⚑⚑ AND THE GREP WAS WRONG IN BOTH DIRECTIONS, WHICH IS WHY THIS IS A FIX AND NOT A
    TIDY-UP. Measured 2026-08-26 by differencing the two hit sets over all 116 Substrate
    targets — 101 agreed, and every disagreement resolved AGAINST the grep:

      · 6 FALSE NEGATIVES from a hardcoded `min(i + 6, len(lines))` tail window. All 6
        have their `public` at span >= 6 and no span < 6 row was missed, so the bound IS
        the cause. `Coxeter.GroupFromCapability -> GroupAdapter` sits at span 17.
      · 5 FALSE POSITIVES from `-F "open import <owner>"` being an UNANCHORED substring:
        owner `…Coxeter.Core` matched `…Coxeter.Core.Operations`, `.NormalizeIdem`,
        `.NormalizeAppend.Left`. That is the DANGEROUS direction — a miss makes this
        function DECLINE, but a prefix-bleed hit makes the caller WRITE an import naming
        a module that never re-exported the owner, which is `_alias_binding`'s
        wrong-carrier defect arriving through a different door.

    ⚑ The authority also sees the `open <applied module> … public` form (43 rows
    tree-wide) that the grep could not match at all, and masks comments and walks
    continuations to the statement's true end rather than a fixed window.

    ⚑ STILL WORKING-TREE-ONLY, AND NOW THAT IS THE AUTHORITY'S PROPERTY RATHER THAN
    THIS FUNCTION'S. `reexport_index` globs the working tree; it takes no `source`. So
    `_nearest_reexporter` cannot yet answer at a `Rev` — but the blocker has MOVED from
    a `subprocess` call embedded here (unfixable without reimplementing the corpus
    reader) to one parameter on the corpus authority, where it belongs and where one
    change serves all 7 of its callers. Named, not swept: ⟡reexport-index-at-rev."""
    self_mod = module_path(near, "") if near and near.endswith(".agda") else None
    hits = [m for m, _tail, _kind in _reexporters_of(owner)
            if m != self_mod and m != owner]
    if not hits:
        return None
    def score(h):
        a, b = h.replace(".", "/").split("/"), (near or "").split("/")
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        # ⚑ `h` IS THE TIE-BREAK, AND IT WAS ADDED WITH THE AUTHORITY MIGRATION.
        # `(-i, len(h))` TIES for two equal-length modules at the same prefix depth,
        # and `sorted` is stable — so the winner was decided by INPUT ORDER, which
        # used to be grep's filesystem walk and is now `reexport_index`'s glob. Both
        # are incidental. MEASURED: `Functor.AsNamed` (12 candidates) and
        # `Coxeter.Word` (5) changed their answer under IDENTICAL candidate sets and
        # an unchanged `score` — a pure ordering artifact, exactly the
        # ⟡rename-index-arbitrary-carrier shape one function below. Appending the
        # name makes the pick TOTAL, so it no longer depends on how the corpus was
        # enumerated. This is the reproducible-not-arbitrary direction the ratchet
        # goes; it does not claim `Z2-Coxeter` is a BETTER carrier than `Z4-Coxeter`,
        # only that the answer stops moving with the walk.
        return (-i, len(h), h)
    return sorted(hits, key=score)[0]


def _in_scope(path, tok, lineno=None):
    r"""Is the identifier `tok` available in the consumer (module param / import / own def)?

    `lineno` (1-based) makes the answer POSITIONAL: a module parameter is reported
    only where its module's body actually encloses that line.  Omitted → the
    file-level question the three `application_args` callers ask ("can this file
    supply this argument at all?"), which is the original contract.

    ⚑ THE TELESCOPE BRANCH WAS BROKEN AND SILENTLY SO.  It read
    `^module [^\n]*\({tok}\s*:`, which demands the parameter on the header's FIRST
    line; a wrapped telescope

        module Over {A : Set}
          (_+_ : A → A → A) …

    binds `_+_` on the SECOND, so the pattern missed it.  MEASURED: this returned
    False for `_+_` in `Algebra/Polynomial/Graded/Defs.agda`.  The identical hazard
    is documented at :362 of THIS FILE (⟡paydown-telescope-anchor) — the note and
    the bug coexisted.  Now delegated to `agda_lex.module_scopes`, the span
    authority, so there is one telescope parser rather than two.
    """
    try:
        src = open(path).read()
    except OSError:
        return False
    if lineno is None:
        tele = any(tok in params for _n, _i, params, _a, _b in agda_lex.module_scopes(src))
    else:
        tele = agda_lex.binds_at(src, tok, lineno)
    return bool(tele
                or re.search(rf"^open import [\w.-]+[^\n]*\busing \([^)]*\b{re.escape(tok)}\b", src, re.M)
                or re.search(rf"^open import [\w.-]+ {re.escape(tok)}(?![\w])", src, re.M)
                or re.search(rf"^{re.escape(tok)}\s*:", src, re.M))


# ── T10/T14/T15 ⟡pd-export-oracle ────────────────────────────────────────────────────────────
# The catalog records what a module DEFINED *before* the strip, so `_module_defines` answers the
# WRONG question for any name whose only route was a `public` that is now gone — it reports a
# false positive and the resolver writes an import that binds nothing. Everything below reads the
# CURRENT source instead, and it is what lets the tool follow a conduit chain forward rather than
# guessing tree-wide.
_LOCAL_MOD = {}          # local (non-file) module name → the file declaring it
_EXPORTS = {}            # (module, leaf) → bool


def _open_stmts(text):
    """(module, statement) for every `open [import] M …`, continuations folded in.

    A continuation line must be STRICTLY more indented than the `open` itself — inside an
    indented local-module block every sibling line is indented, so a naive `\\n[ \\t]+` would
    swallow the rest of the block and report one giant statement."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        # ⚑ a BARE `import M as A` is an import edge too. Matching only `open …` made every
        # aliased conduit invisible to the export/conduit machinery, which is why an alias onto
        # a stripped barrel could not be resolved: the module supplying the alias was not even
        # in the consumer's reachable set.
        m = re.match(r"^([ \t]*)(?:open\s+import|import|open)\s+([\w.-]+)", lines[i])
        if not m:
            i += 1
            continue
        ind, stmt, j = len(m.group(1)), [lines[i]], i + 1
        while j < len(lines):
            s = lines[j]
            if not s.strip() or (len(s) - len(s.lstrip())) <= ind:
                break
            stmt.append(s)
            j += 1
        yield m.group(2), "\n".join(stmt)
        i = j


def _local_module_file(name):
    """The file declaring a NON-file module (`module WithLemmas …` inside ListPresentation)."""
    if name in _LOCAL_MOD:
        return _LOCAL_MOD[name]
    hit = None
    try:
        # ⚑ the parameters of a local module often start on the NEXT line, so the declaration
        # can end right after the name — `[ \t(]` alone silently missed `module WithLemmas`.
        r = subprocess.run(["grep", "-rlE", rf"^[ \t]*module {re.escape(name)}([ \t(]|$)",
                            "--include=*.agda", "Substrate"], capture_output=True, text=True)
        files = [f for f in r.stdout.split() if f]
        if len(files) == 1:                          # ambiguous ⇒ no answer, never a guess
            hit = files[0]
    except OSError:
        pass
    _LOCAL_MOD[name] = hit
    return hit


def _module_text(mod):
    """(source, body-indent) of `mod` — a whole FILE module, or a local module's block.

    The indent matters: a name declared INSIDE a nested module is not exported by the enclosing
    one, so every export test must be anchored to the module's own body column. Ignoring that
    made `Cyclic.Existential` look like an exporter of `_·_` merely because `ListPresentation`
    happens to CONTAIN a `module WithLemmas` that re-exports it."""
    # ⚑ ⟡vfs-encoding. Both reads below were bare `open(...)` — the locale default. Here the
    # codec decision is STRICT UTF-8 AND A DECODE FAILURE RAISES, which is the opposite of
    # `_import_graph`'s choice above and deliberately so: this reads ONE NAMED module whose
    # text is about to be regex-scanned for exports. Returning `("", 0)` on a mangled file
    # would report "this module exports nothing" — a false NEGATIVE that `scope_fix` acts on
    # by writing an import elsewhere. Absence of a file is a legitimate answer here; absence
    # of a DECODE is a defect in the tree, and it must be loud.
    p = mod.replace(".", "/") + ".agda"
    if os.path.exists(p):
        r = vfs.read(p, _source())
        if r.presence is not vfs.Presence.PRESENT:
            return "", 0                     # as before: unreadable ⇒ "no text"
        return r.text(), 0
    f = _local_module_file(mod)
    if not f:
        return "", 0
    r = vfs.read(f, _source())
    if r.presence is not vfs.Presence.PRESENT:
        return "", 0
    lines = r.text().split("\n")
    pat = re.compile(rf"^([ \t]*)module {re.escape(mod)}(?![\w.-])")
    for i, ln in enumerate(lines):
        m = pat.match(ln)
        if not m:
            continue
        ind, block = len(m.group(1)), [ln]
        for j in range(i + 1, len(lines)):
            s = lines[j]
            if s.strip() and (len(s) - len(s.lstrip())) <= ind:
                break
            block.append(s)
        inner = [len(s) - len(s.lstrip()) for s in block[1:] if s.strip()]
        return "\n".join(block), (min(inner) if inner else ind + 2)
    return "", 0


def _module_exports(mod, leaf, depth=12, seen=None, exact=False):
    """Does `mod` EXPORT `leaf`, read off the CURRENT source?

    A top-level definition, or a still-live `… public` re-export chain — including through a
    LOCAL module (`open WithLemmas … public`), which is how the applied Coxeter surface reaches
    `Cyclic.Core` and the reason a grep for `open import <owner>` finds nothing."""
    key = (mod, leaf, exact)
    if key in _EXPORTS:
        return _EXPORTS[key]
    if depth <= 0 or mod in (seen or set()):
        return False
    seen = (seen or set()) | {mod}
    body, ind = _module_text(mod)
    if not body:
        return False
    pad = " " * ind
    # ⚑ an operator PRINTS bare (`≈`) and IMPORTS underscored (`_≈_`); the tolerant set answers
    # "is this name reachable here", `exact` answers "which spelling do I write in the using-list".
    spellings = {leaf} if exact else {leaf, f"_{leaf}_", leaf.strip("_")}
    for l in spellings:
        if not l:
            continue
        # ⚑ a declaration may carry PARAMETERS between the name and its `:` (`data Word (Gen :
        # Set) : Set`), so anchoring on `name\s*:` silently reported `Coxeter.Word` as not
        # exporting `Word` — the one name the whole alias hung on.
        if any("=" in d.group(0) or ":" in d.group(0) for d in re.finditer(
                rf"^{pad}(?:data\s+|record\s+|pattern\s+)?{re.escape(l)}(?![\w′-])[^\n]*(?:\n[ \t]+[^\n]*)*", body, re.M)):
            _EXPORTS[key] = True
            return True
        # a DATA CONSTRUCTOR is exported with its datatype (unlike a record field, which needs
        # the record opened publicly), and it lives indented inside the `data … where` block.
        for d in re.finditer(rf"^{pad}data\s+\w[^\n]*where[^\n]*(?:\n(?:[ \t]+[^\n]*|[ \t]*))*",
                             body, re.M):
            if re.search(rf"^[ \t]+{re.escape(l)}(?![\w′-])[^\n]*:", d.group(0), re.M):
                _EXPORTS[key] = True
                return True
        # a RECORD FIELD is an exported projection wherever the module does `open <Rec> public`
        # (`Symmetric` re-exports `Permutation`'s `apply`/`invₐ`/`inv-l`/`inv-r` that way), and
        # a field is indented inside the record, so the body-column test above cannot see it.
        # ⚑ the search MUST be scoped to the record's own block. Unscoped, any indented `x :`
        # line in the file matched — including a `variable\n  a b : Level` declaration, which
        # made `Foundation.Product` look like an exporter of `a` and sent a Coxeter generator
        # into a pre-header import where the module parameter is not yet in scope.
        for rec in re.findall(rf"^{pad}open\s+(\w[\w.′]*)[^\n]*\bpublic\b", body, re.M):
            blk = re.search(rf"^{pad}record\s+{re.escape(rec)}(?![\w′-])[^\n]*"
                            rf"(?:\n(?:[ \t]+[^\n]*|[ \t]*))*", body, re.M)
            if blk and re.search(rf"^[ \t]+{re.escape(l)}(?![\w′-])[^\n]*:", blk.group(0), re.M):
                _EXPORTS[key] = True
                return True
    for sub, stmt in _open_stmts(body):
        if len(stmt) - len(stmt.lstrip()) != ind:     # only the module's OWN body column
            continue
        # ⚑ comment-masked, as at the sibling site above: an unmasked `\bpublic\b`
        # reads the word out of a trailing comment and walks a conduit that is not one.
        if not re.search(r"(?<![\w.'-])public(?![\w'-])", _mask(stmt)):
            continue
        u = re.search(r"using \(([^)]*)\)", stmt, re.S)
        if u:
            # a `using` list is EXHAUSTIVE: nothing outside it is re-exported
            names = {n.strip() for n in re.split(r"[;\s]+", u.group(1)) if n.strip()}
            if names & spellings:
                _EXPORTS[key] = True
                return True
            continue
        r = re.search(r"renaming \(([^)]*)\)", stmt, re.S)
        if r and {p.split(" to ")[-1].strip() for p in r.group(1).split(";")} & spellings:
            _EXPORTS[key] = True
            return True
        if _module_exports(sub, leaf, depth - 1, seen, exact):  # wholesale ⇒ follow the chain
            _EXPORTS[key] = True
            return True
    _EXPORTS[key] = False
    return False


def _rename_pairs(stmt):
    """(source, target) for every `renaming (src to tgt; …)` pair in an import statement."""
    out = []
    for r in re.findall(r"renaming\s*\(([^)]*)\)", stmt, re.S):
        for pair in r.split(";"):
            parts = pair.split()
            if len(parts) == 3 and parts[1] == "to":
                out.append((parts[0], parts[2]))
    return out


def head_read(mod, rev="HEAD"):
    """`vfs.Result` for `mod` at `rev` — the PRESENCE-AWARE read. ⟡vfs.

    ⚑⚑ THIS IS THE CAPABILITY `_head_text` ALWAYS WAS, MINUS THE COLLAPSE. The old body
    ended `out.stdout if out.returncode == 0 else ""`, which makes FOUR different facts
    indistinguishable — every one of them rendering as the empty string:

        the module is absent at HEAD          (new in the working tree)
        the module is EMPTY at HEAD           (a zero-byte file — legitimately "")
        the revision is bad                   (a typo'd sha)
        this is not a git repository          (or git is not installed)

    MEASURED 2026-08-25 in this very tree: `Substrate.Algebra.CayleyDickson.Curve.Gray`
    is an in-flight module present in the working tree and absent at HEAD, and
    `_head_text` reported it byte-identically to `Substrate.Nonexistent.Module.Xyzzy` —
    both `len=0`. The ABSENT→EMPTY inversion is exactly what `at_revision`'s docstring
    warns about after a `git checkout` used to *look at* history destroyed working
    copies, and this function is the same capability in a SECOND BODY that made the
    inversion worse.

    ⚑ `_head_text` REMAINS, delegating here, because its 8 call sites across 4 modules
    all want `str`. It is not a duplicate; it is a lossy VIEW of this, and the loss is
    now stated at the seam instead of buried in a ternary. New callers should take the
    `Result` and branch on `.presence`.
    """
    key = (mod, rev)
    if key in _HEAD_RESULT:
        return _HEAD_RESULT[key]
    p = mod.replace(".", "/") + ".agda"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = vfs.read(f"agda/{p}", vfs.Rev(rev, root=root))
    # ⚑ PRESENT and ABSENT are FACTS ABOUT THE REVISION — immutable, so caching them is
    # sound. BROKEN is a fact about the ATTEMPT (a transient repo lock, a permission, a
    # not-yet-fetched sha) and is NOT cached: memoizing it would freeze one bad moment
    # into every later read in the process, which is the "cached failure reads as an
    # answer" shape. The old body cached `""` for this case too — inheriting that was
    # not required, only easy.
    if r.presence is not vfs.Presence.BROKEN:
        _HEAD_RESULT[key] = r
    return r


def _head_text(mod):
    """`mod`'s PRE-STRIP source (git HEAD), or ''.

    A module whose whole body was one `open import … public renaming (…)` is a pure CONDUIT: the
    strip empties it, and with it the only record of WHICH name each target renamed. That record
    is pre-strip data, so read it from HEAD — the same move the seed already makes.

    ⚑ A LOSSY VIEW OF `head_read`, KEPT DELIBERATELY. The `""`-on-miss contract is what
    its 8 existing call sites are written against, so preserving it is what makes this
    migration behaviour-preserving rather than a flag-day edit. But the loss is REAL:
    this cannot tell absent from empty from broken. ⚑ Callers that care — and a caller
    reconstructing a pre-strip `renaming` list DOES care, because "no record exists"
    and "the record was empty" license different repairs — must call `head_read`.

    ⚑⚑ AND THE BROKEN ARM IS NOW LOUD RATHER THAN SILENT. A bad rev or a missing repo
    used to return `""` and read as "this module is new". It now warns once to stderr
    before degrading, so the condition is observable instead of being absorbed into a
    plausible-looking answer.

    ⚑⚑⚑ THE VIEW SURVIVES DELIBERATELY, AND HERE IS THE MEASUREMENT THAT SETTLED IT
    (⟡lossy-view-retirement, 2026-08-25). The retirement plan was: migrate all 8 callers
    to `head_read`, then delete this. Enumerated with `pycodemod --calls _head_text`
    (8 calls / 4 refs; the 4 refs are import re-exports, not consumers):

        demand_imports.py:110   renames()          _open_stmts(text or "")
        scope_alias.py:79       fix_arg_name_closure()  `_module_text(c)[0] or _head_text(c)`
        scope_edit.py:219       _rename_owner()    `if not body: continue`
        scope_edit.py:236       _rename_owner()    `_open_stmts(_head_text(sub))` → []
        scope_edit.py:245       _rename_owner()    `_open_stmts(_head_text(sub))` → []
        scope_source.py:*       _alias_binding()   ×2, `if not text: continue`
        scope_source.py:*       _rename_index()    `if not text: continue`

    ⚑ ALL EIGHT ARE ONE SHAPE: `_head_text` is a SUPPLEMENTARY statement source, fed to
    `_open_stmts` alongside the working-tree text, and every falsy branch means *"this
    text contributed no import statements"*. For that predicate ABSENT and EMPTY are the
    SAME instruction — contribute nothing — so a three-armed rewrite would be a
    behaviour-preserving no-op. Verified by differencing the statement yield of the
    current view against a three-armed reader over PRESENT / ABSENT / never-existed:
    12/12, 0/0, 0/0 — `differ=False` on every arm.

    ⚑⚑ AND THE COLLAPSE IS UNINHABITED IN THIS CORPUS, WHICH IS THE STRONGER FACT.
    `vfs --census 'agda/Substrate/**/*.agda' --at HEAD` reports **PRESENT-empty = 0 of
    2403** (working tree: 0 of 3598). There is no zero-byte `.agda` for `""` to be
    ambiguous ABOUT, so within these callers' actual population `"" ⇒ ABSENT` is not
    merely safe, it is EXACT. `--census` was added to `vfs` for this question; a
    `--list` could not have answered it, and no reading of the code could either.

    ⚑⚑⚑ THE DENOMINATOR ABOVE IS SHORT BY SIX, AND THE PARAGRAPH IT SITS IN IS AN
    ARGUMENT FROM A CENSUS (⟡head-census-denominator, re-derived 2026-08-25). Kept as
    written rather than overwritten, because the defect is the transferable part: this
    is `report n of m` WITH THE PROVENANCE OF `m` MISSING, in the artifact that argues
    from that census. `agda/Substrate/**/*.agda` cannot match a DEPTH-0 path at a Rev
    (`fnmatch` has no `**`), so it silently dropped the six top-level modules —
    `Substrate.Foundation`, `.Generators`, `.Cocycle`, `.Cardinality`, `.Discipline`,
    `.ShadowArchitecture`. ⚑ And it is INVISIBLE on the branch anyone checks: python's
    `glob(recursive=True)` DOES let `**/` match zero segments, so the same pattern is
    EXACT on the working tree. `vfs.listdir` now REFUSES the pattern outright
    (`AmbiguousPattern`), and the spelling that is depth-agnostic under BOTH matchers is

        vfs.py --census 'agda/Substrate/**' --suffix .agda --at HEAD

    ⚑ THE CONCLUSION DOES NOT MOVE — only its scope was understated. Re-derived over
    that pattern: **PRESENT-empty = 0 of 2409** at HEAD (working tree: 0 of 3598). The
    `empty` cell is what the argument rests on and it is 0 in both readings, so the six
    modules the glob dropped contain no zero-byte `.agda` either. Had they, the
    CONCLUSION would have changed and not merely the denominator — which is why the
    figure was re-derived rather than incremented.

    ⚑ SO WHAT REMAINS IS A TYPE-LEVEL DEFECT WITH AN EMPTY EXTENSION — real, worth
    naming, and NOT worth converting 8 working callers to three-armed ones for. The
    honest repair was to make the loss *stated and observable* (this docstring, plus the
    BROKEN warning) rather than to churn the callers for symmetry. A NEW caller that
    reconstructs a pre-strip `renaming` list — where "no record exists" and "the record
    was empty" license different repairs — must still call `head_read`, and a corpus
    that ever grows an empty `.agda` re-opens this: the census is the tripwire.
    """
    r = head_read(mod)
    if r.presence is vfs.Presence.PRESENT:
        return r.text(errors="replace")
    if r.presence is vfs.Presence.BROKEN and r.error is not None:
        if not _HEAD_WARNED:
            _HEAD_WARNED.append(1)
            print(f"   ⚑ _head_text: history unreadable ({r.error}) — every module will "
                  f"read as absent-at-HEAD. This is a BROKEN read, not an empty tree.",
                  file=sys.stderr)
    return ""


# ⚑⚑ ⟡two-vfs-import-spellings — THE LAZY `vfs_Presence()` HELPER IS RETIRED, AND A
# MEASUREMENT RETIRED IT, NOT A PREFERENCE. Two agents landed two spellings in this file:
# a top-level `import vfs` (the encoding migration) and a `vfs_Presence()` that imported
# inside the function, whose stated rationale was "so `scope_source` keeps importing when
# `pygit2` is not installed — the read only NEEDS it on the `Rev` path".
#
# That rationale is ALREADY SATISFIED BY `vfs` ITSELF, which defers `import pygit2` into
# `Rev.resolve()`. MEASURED 2026-08-25 via `sys.modules`, starved both ways:
#
#     baseline                    pygit2 in sys.modules = False
#     after `import vfs`          pygit2 in sys.modules = False
#     after `import scope_source` pygit2 in sys.modules = False
#     after a Rev READ            pygit2 in sys.modules = True
#
# and pygit2 IS importable in that interpreter — so the three `False`s are a fact about
# the IMPORT GRAPH, not about the environment, and the fourth line shows the check can
# report True, which is what makes the first three a measurement rather than a constant.
# A lazy import guarding against something the guarded module never does is a second
# spelling with no residual duty, so the top-level one survives.
_HEAD_RESULT = {}
_HEAD_WARNED = []


def _alias_target(path, alias):
    """The module `import <M> as <alias>` names in `path`.

    ⚑ ⟡scope-source-remainder. Was a bare `open()` under `except OSError: return None`.
    THE DECODE FAILURE RETURNS `None` — the same arm as the absence, and here that IS the
    honest answer rather than a guess. `None` is this function's genuine "don't know": it
    means "I found no `import M as <alias>` statement", and every caller branches on it by
    DECLINING to rewrite the alias. Contrast `_parent_kind` directly above, whose miss is
    the positive answer `"ctor"` that a caller acts on — that is why that one raises and
    this one does not. The failure branch is only safe when it means *do nothing*.
    """
    r = vfs.read(path, _source())
    if r.presence is not vfs.Presence.PRESENT:
        return None
    try:
        src = r.text()
    except UnicodeDecodeError:
        return None                       # "no alias statement found" — a declining answer
    m = re.search(rf"^(?:open\s+)?import\s+([\w.-]+)[^\n]*?\bas\s+{re.escape(alias)}(?![\w])",
                  src, re.M)
    return m.group(1) if m else None


def _alias_binding(alias_mod, leaf, depth=4):
    """How `alias_mod` ITSELF binds `leaf`: `(owner, source_name)`.

    ⚑ For a qualified `A.x` this beats every tree-wide search, because A's own import statement
    is the record of WHICH `x` it meant. `Canonical` is the witness: `Cyclic.Base n` defines a
    `Canonical : Fin (suc n) → Set`, while `Z2-Coxeter` means `Cyclic.Existential`'s
    `Canonical-ex : Word Gen → Set` (it renames it). Both are exported and both are named
    `Canonical`; only the binding statement — or, equivalently, the codomain catalog.db records —
    tells them apart, and picking by export alone silently wires the wrong one.
    """
    for text in (_module_text(alias_mod)[0], _head_text(alias_mod)):
        if not text:
            continue
        for sub, stmt in _open_stmts(text):
            if not sub.startswith("Substrate"):
                continue
            rest = stmt.split(sub, 1)[1] if sub in stmt else ""
            args = re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b", rest)[0].strip()
            for s, t in _rename_pairs(stmt):
                if t == leaf:
                    return sub, s, args
            u = re.search(r"using \(([^)]*)\)", stmt, re.S)
            if u and leaf in {n.strip() for n in re.split(r"[;\s]+", u.group(1)) if n.strip()}:
                return sub, leaf, args
    # a WHOLESALE statement (`open import M public`, no using-list) names no leaf, so the scan
    # above cannot see it — and the chain it heads is exactly what the strip emptied
    # (`Z2-Coxeter` reached `a` through `open import Cyclic 1 public`). Walk that chain down to
    # the module that still exports the leaf, carrying the application through: the inner
    # statement applies the barrel's OWN parameter, so the outer index is the one that survives.
    # Stay INSIDE the conduit — widening to the consumer's imports would re-admit the sibling
    # carrier this alias exists to keep apart.
    if depth <= 0:
        return None, None, ""
    for text in (_module_text(alias_mod)[0], _head_text(alias_mod)):
        if not text:
            continue
        for sub, stmt in _open_stmts(text):
            if not sub.startswith("Substrate") or re.search(r"using \(", stmt):
                continue
            rest = stmt.split(sub, 1)[1] if sub in stmt else ""
            args = re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b",
                            rest)[0].strip()
            if _module_exports(sub, leaf):
                return sub, leaf, (args if _module_params(sub) else "")
            o, s, a = _alias_binding(sub, leaf, depth - 1)
            if o:
                if not _module_params(o):
                    return o, s, ""            # a parameterless owner takes no application
                # an inner arg that is the barrel's own parameter name is re-bound by the outer
                # application; a literal (`1`) stands on its own.
                return o, s, (a if a and not a.isidentifier() else args or a)
    return None, None, ""


_RENAME_IDX = None


def _rename_index():
    """target-name → [(module-renamed-from, source-name)] over the corpus, working tree AND HEAD.

    ⚑ ⟡rename-index-sixth-site. The FIRST site in this file with BOTH halves of the
    defect — a bare `open(p).read()` (the locale codec, over a corpus of `σ`/`∷`/`𝟙`)
    AND an `os.walk`. Named and left un-migrated by the agent that did the other five,
    rather than swept in silently.

    ⚑⚑ THE CODEC BRANCH IS **RAISE**, AND THE AXIS THAT PUTS IT THERE IS ACT-ON-IT.
    On the first axis (caller-supplied vs self-discovered) this is `_alias_target`'s
    side — we discover every path ourselves — but the second axis overrides, exactly as
    it does for `_parent_kind` and `_module_params`:

      A MISSING ENTRY IS NOT THIS FUNCTION'S "DON'T KNOW". `.get(leaf, ())` returning
      empty is the POSITIVE ANSWER *"nothing in the corpus renames to this leaf"*, and
      it is REACHED BY SKIPPING A FILE, not by that file saying so. Both consumers act:

        scope_edit:242  `_rename_owner`  — iterates the records to pick an owner and a
                        SOURCE NAME, which `add_renaming_import` then WRITES as
                        `open import <owner> using () renaming (<src> to <target>)`.
        scope_store:512 `_demand_of`     — maps a conduit spelling onto the canonical
                        one. Its own comment at :518 states the cost of losing a record
                        here: the candidate list is not carried across the rename, the
                        no-merge guard then sees a single carrier and DE-QUALIFIES.
                        *"Fourth instance of the same defect."*

    So a silent skip does not mean "do nothing" — at scope_edit it declines (safe), but
    at scope_store it changes what gets written. And the failure is PER-FILE inside a
    WHOLE-CORPUS index whose entire value is completeness: one unreadable module would
    silently convert *"F renames X to Y"* into *"nobody renames to Y"* — a fact about
    the METHOD reported as a fact about the SUBSTRATE, in a tool that writes Agda.

    ⚑ AND THE OLD BODY ALREADY RAISED. `open(p).read()` carried no `try`, so an
    undecodable module aborted the index under the LOCALE codec. Raising here is
    therefore behaviour-PRESERVING; what changes is only that the codec is now UTF-8 by
    construction rather than by whatever `LANG` happened to be. Agda source is UTF-8 by
    specification, so an undecodable `.agda` is a defect to surface, not a corpus
    member to skip.

    ⚑⚑⚑ THE WALK IS `vfs.listdir` BUT THE FUNCTION IS **NOT** SOURCE-PARAMETRIC, AND
    THAT IS A DECISION, NOT AN OMISSION. `_import_graph` became source-parametric
    because it answers ONE question about ONE source. This one does not: its contract
    is the UNION of the working tree and HEAD (`for text in (<wt>, _head_text(mod))`),
    because a pure CONDUIT whose body the strip emptied holds its `renaming` record
    only in history. A `source=` parameter would have to mean one of

      · *"which source"* — which contradicts the union that is the whole point, or
      · *"which source is the LEFT half"* — a parameter that silently keeps HEAD
        pinned on the right, so `_rename_index(Rev("v1"))` would return v1-∪-HEAD and
        read as *"the index at v1"*. A read that succeeds at being wrong.

    ⚑ AND `_RENAME_IDX` IS A BARE GLOBAL KEYED ON NOTHING — the exact shape `_IMPORTS`
    was found wrong for the moment a `Rev` became passable. Adding the parameter
    without keying the cache would serve one revision's index under another's. So the
    honest state is: the WALK is now source-capable (`vfs.listdir` + `_source()`), the
    FUNCTION is not, and the two blockers are named. Making it parametric means first
    deciding what a rename index AT a revision means — which is a question about the
    union, not about the walk. ⟡rename-index-parametric is that item, unclaimed.

    ⚑⚑ ⟡rename-index-parametric RE-EVALUATED 2026-08-26 — **NEITHER BLOCKER HAS MOVED,
    AND THE FIRST IS NOT A BLOCKER AT ALL BUT A DESIGN FACT.** Reported rather than
    worked around, because "still blocked" is a finding and a forced parameter would be
    the read-that-succeeds-at-being-wrong this docstring already argues against.

      1. THE UNION CONTRACT — UNCHANGED, and it is INHERENT rather than incidental. The
         contract is working-tree ∪ HEAD because a pure conduit the strip emptied holds
         its `renaming` record ONLY in history; that is not a limitation waiting on a
         parameter, it is what the index IS. A `source=` would still have to mean
         "which source" (contradicting the union) or "which LEFT half" (leaving HEAD
         pinned on the right, so `_rename_index(Rev("v1"))` returns v1-∪-HEAD and reads
         as *"the index at v1"*). ⚑ The honest successor is not a `source=` parameter
         but a SECOND PARAMETER PAIR — `(left, right)` — making the union explicit
         rather than implicit. That is a contract change with two consumers to migrate,
         and it is not this item's mandate.
      2. `_RENAME_IDX` KEYED ON NOTHING — UNCHANGED. Verified this round, not recalled:
         `pycodemod --binding _RENAME_IDX` still reports a bare module-level global
         (`scope_source.py:1070`), against `_IMPORTS_REV`'s keyed `("Rev", rev, root)`.

    ⚑⚑⚑ AND THE ⟡ambient-root INTERACTION, WHICH IS REAL BUT HAS NOT LANDED. An explicit
    root IS a key, so that work bears directly on blocker 2 — `_IMPORTS_REV`'s key is
    `(rev, root)` precisely because `Rev("HEAD")` names different trees in different
    repositories. Measured this round: `_source()` still builds `vfs.WorkingTree(
    os.getcwd())` from the ambient CWD (`pycodemod --calls WorkingTree --root scratch`
    → the only `scope_source` construction is :103), so nothing to key on has appeared
    yet. **Noted as an interaction, NOT depended on** — this item does not block on
    another agent's work, and does not pre-emptively shape itself around a root
    parameter that may take a different form.

    ⚑ WHAT DID CHANGE THIS ROUND IS THE OTHER HALF: the ARBITRARY-CARRIER defect this
    docstring filed is now resolved (see the ⟡rename-index-arbitrary-carrier block
    above and `rename_records`). Parametricity and carrier-selection were always two
    items sharing a docstring; one shipped, one is still honestly blocked.

    ⚑⚑ THE MIGRATION IS MEMBERSHIP-EXACT BUT **NOT** ORDER-PRESERVING, AND THAT IS
    REPORTED RATHER THAN WAVED THROUGH. Differenced against the old body over the whole
    corpus (7,380 probes; 184 index keys, 3,598 paths, 210 telescopes non-default):
    **0 membership differences, 13 reorderings** — `os.walk` yields in OS order,
    `vfs.listdir` yields SORTED. In all 13 the FIRST record moved, and the first record
    is exactly what `scope_edit._rename_owner` returns and `add_renaming_import` WRITES:

        _+₂_      Algebra.F2.PlusF/_+F_          ->  Algebra.F2/_+_
        e₄ α₄ β₄ γ₄  Groups.V4.Bijection/…       ->  Groups.V4.Bijection.V4/…
        Canonical-at, canonical-cover-fin, insert-canonical, inv-canonical,
        inv-{inv,left,right}-canonical  — same owner, APPLICATION ARG `3` -> `1`

    ⚑⚑⚑ SO THE ORDERING WAS NEVER A CHOICE, AND THAT IS THE FINDING. `os.walk` order is
    filesystem order — it differs between machines, checkouts and after a `git clean`.
    The old pick among several carriers was therefore ALREADY NONDETERMINISTIC; sorting
    does not replace a principled ordering with an arbitrary one, it replaces an
    arbitrary one with a REPRODUCIBLE one. That is the direction the ratchet goes, so it
    is kept.

    ⚑ WHAT IT EXPOSES IS A REAL DEFECT AND IT IS NOT MINE TO FIX HERE: for a
    parameterized owner this index holds one record PER APPLICATION (`Canonical-ex` at
    `1`,`2`,`3`,`4`,`6`) and the consumer takes `[0]`, so the ARGUMENT is selected by
    list position. `1` and `3` name different carriers, and `_alias_binding` exists
    precisely because picking a carrier by anything other than the binding statement
    "silently wires the wrong one". Filed as ⟡rename-index-arbitrary-carrier: the pick
    needs `_owner_admissible`-style ranking or a refusal-on-ambiguity, not an ordering.

    ⚑⚑⚑⚑ ⟡rename-index-arbitrary-carrier RESOLVED (2026-08-26) — AND IT IS **BOTH**
    RANKING AND REFUSAL, BECAUSE THE AMBIGUOUS POPULATION IS NOT ONE KIND. Measured over
    the whole corpus: 184 keys, **31 with more than one record**, and classifying each by
    what actually DIFFERS across its records splits them three ways:

        23  OWNER differs          — of which **21 are parent/own-leaf pairs**
                                     (`Foundation.Empty` vs `Foundation.Empty.Bot`,
                                     `Nat` vs `Nat.Nat`, `Refinement` vs
                                     `Refinement.Chain`) and only 2 are genuinely
                                     rival, unrelated owners.
         7  APPLICATION-ARG differs — identical owner AND identical source name; the
                                     records differ ONLY in the argument (`1`…`6`).
         1  SOURCE-NAME differs     — `F.Over` renaming both `_+F_` and `_+_` to `_+r_`.

    ⚑⚑ THE 23 ARE NOT RIVAL CARRIERS AT ALL, WHICH IS WHY A RANKING IS HONEST THERE.
    They are ONE rename seen from two places: the leaf that now defines the name, and the
    parent whose `public` conduit the strip emptied. A criterion that separates them
    already exists and **is the one the consumer itself applies** — `_module_exports`.
    Measured per key: in 13 of them exactly ONE record survives `_module_exports(owner,
    src)`, and it is the leaf every time (`Foundation.Empty.Bot` True / `Foundation.Empty`
    False). So ranking here does not invent a preference; it PROMOTES the test the caller
    was going to run anyway, from after the positional pick to before it.

    ⚑⚑⚑ THE 7 ARE THE OPPOSITE, AND NO RANKING CAN TOUCH THEM. Owner and source name are
    IDENTICAL across all five records, so `_module_exports` returns the SAME verdict for
    every one — the criterion that resolves the 23 is blind here by construction. The only
    thing distinguishing `Canonical-ex 1` from `Canonical-ex 3` is the argument, and
    NOTHING IN THIS INDEX SAYS WHICH THE CONSUMER WANTS: the index is corpus-wide, and the
    application belongs to a particular consumer's binding statement. That is exactly
    `_alias_binding`'s thesis — *"only the binding statement tells them apart, and picking
    by export alone silently wires the wrong one"*. So this class REFUSES.

    ⚑ WHAT THE CONSUMER DOES ON A REFUSAL, WHICH IS THE HALF THAT MAKES REFUSAL SAFE.
    Both consumers already degrade correctly, and neither needed changing:

      · `scope_edit:242 _rename_owner` — ITERATES the records under
        `_owner_admissible and _module_exports` (the brief's *"takes [0]"* is not what
        the code does; ordering biased it, it never bound it). An empty list falls
        through to `return None, None, ""`, and `fix()` then prints *"no owner found"*
        and DEFERS the name. Safe: a name it declines to bind is a name a human reads.
      · `scope_store:512 _demand_of` — the de-qualification its own comment at :518 calls
        *"the fourth instance of the same defect"*. Refusing to supply a record is
        precisely what STOPS the collapse that comment describes: with no record, `out`
        gains no entry for the conduit spelling, the candidate list is not silently
        narrowed to one carrier, and the no-merge guard keeps the qualification.
        Refusal here is the CONSERVATIVE direction, not a new failure.

    ⚑ AND THE ORDER IS STILL SORTED UNDERNEATH. Ranking does not replace the sort — it
    reads it. Where the criterion cannot discriminate (the 7), the sort is what makes the
    REFUSAL reproducible rather than machine-dependent, which is what lets a gate count it.
    """
    global _RENAME_IDX
    if _RENAME_IDX is not None:
        return _RENAME_IDX
    _RENAME_IDX = {}
    source = _source()
    # ⚑ `Substrate/**` + an in-code suffix test, NOT `Substrate/**/*.agda`: the latter
    # cannot match a depth-0 path at a `Rev` and drops the six top-level modules, while
    # reading EXACT on the working tree. `vfs.listdir` now refuses it outright.
    for p in vfs._suffixed(vfs.listdir("Substrate/**", source), ".agda"):
        mod = module_path(p, "")
        r = vfs.read(p, source)
        if r.presence is not vfs.Presence.PRESENT:
            continue                      # raced away between listdir and read
        for text in (r.text(), _head_text(mod)):   # strict UTF-8; undecodable RAISES
            if not text:
                continue
            for sub, stmt in _open_stmts(text):
                rest = stmt.split(sub, 1)[1] if sub in stmt else ""
                a = re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b",
                             rest)[0].strip()
                for s2, t in _rename_pairs(stmt):
                    _RENAME_IDX.setdefault(t, [])
                    if (sub, s2, a) not in _RENAME_IDX[t]:
                        _RENAME_IDX[t].append((sub, s2, a))
    return _RENAME_IDX


def rename_records(leaf):
    """The `_rename_index` records for `leaf`, RANKED — or `()` where the pick is arbitrary.

    ⚑ ⟡rename-index-arbitrary-carrier. `_rename_index()[leaf]` is a LIST, and a consumer
    reading it positionally selects a carrier by LIST POSITION. Sorting the walk made that
    pick reproducible; reproducible is not correct. This is the accessor that either
    RESOLVES the ambiguity on a criterion the consumer can verify, or REFUSES it — never a
    position standing in for an identity. See `_rename_index`'s docstring for the measured
    3-way split of the 31 ambiguous keys that this shape is derived from.

    ⚑⚑ THE CRITERION IS `_module_exports`, AND IT IS NOT A NEW PREFERENCE. It is the test
    both consumers ALREADY apply to whatever record they receive (`scope_edit:243`,
    and the export-checked resolver chain in `fix()`); running it HERE only moves it
    ahead of the positional pick. A criterion invented for the ranking would be a
    judgement in the tool; this one is the consumer's own acceptance test, promoted.

    ⚑⚑⚑ REFUSAL IS NOT "NO RECORDS" — it is *"the records are indistinguishable BY
    ANYTHING THIS INDEX HOLDS"*, and the two must not collapse. When several records
    survive the export test and differ ONLY in their application argument, the index is
    corpus-wide while the argument belongs to one consumer's binding statement, so any
    pick here is a guess. `()` is returned and the caller declines — which for
    `_rename_owner` means DEFERRING the name (a human reads it) and for `_demand_of`
    means NOT de-qualifying (the qualification, i.e. the carrier distinction, survives).
    Both are the conservative direction.

    ⚑ THE THREE-WAY VERDICT, MEASURED OVER ALL 31 AMBIGUOUS KEYS (2026-08-26) — and it
    is THREE, not two, which is the correction this function needed:

        17  RANKED           exactly one record survives `_module_exports` -> that one.
                             The parent/leaf pairs: `Bot`, `Nsuc`, `Nzero`, `ℕzero`,
                             `Rchain`, `Riterate`, `E←`, `E→`, `+F-assoc`, `+F-comm`,
                             `_+₂_`, `e₄`, `btail~`, `trace-out`, `~-refl'`,
                             `coemit-coalg`, `Progress⟦cbe99ef5⟧`.
         7  REFUSED          SEVERAL survive and are indistinguishable — the five-way
                             application-argument families (`Canonical-at`,
                             `canonical-cover-fin`, `insert-canonical`, `inv-canonical`,
                             `inv-left-canonical`, `inv-right-canonical`) plus
                             `Tm⟦533ef80d⟧`, where two genuinely rival owners both
                             export. Nothing in a corpus-wide index can pick.
         7  UNDISCRIMINATED  ZERO survive -> ALL records kept, see below.

    ⚑⚑ **UNDISCRIMINATED IS NOT REFUSED, AND COLLAPSING THEM WAS A BUG THIS FUNCTION
    SHIPPED** — caught by its own case (`α₄`), not by re-reading the code. `live == []`
    means THE TEST SAID NOTHING, because `_module_exports` reads POST-STRIP source and
    every record may name a conduit the strip emptied; it does NOT mean the records
    conflict. `α₄`, `β₄`, `γ₄`, `+ℕ-comm`, `bhead~`, `_+r_`, `inv-inv-canonical` are
    that class. Refusing them would delete the key outright and with it the one-hop
    fallback at `scope_edit:245`, which exists precisely to re-issue the rename one
    module further in. So the criterion applies ONLY where it separates — which is the
    whole of its warrant, and the reason `report presence, never absence` is the rule
    it is written against: an empty `live` is a fact about the TEST.
    """
    recs = _rename_index().get(leaf, ())
    if len(recs) <= 1:
        return tuple(recs)
    # RANK: keep the records whose owner still exports the source name.
    live = [r for r in recs if _module_exports(r[0], r[1])]
    # ⚑⚑ AN ALL-FALSE KEY IS **UNDISCRIMINATED, NOT AMBIGUOUS**, AND COLLAPSING THE TWO
    # IS A BUG THIS FUNCTION SHIPPED FOR ONE REVISION — caught by its own case, not by
    # reading. 8 of the 31 ambiguous keys have ZERO surviving records (`α₄`, `β₄`, `γ₄`,
    # `+ℕ-comm`, `bhead~`, `_+r_`, `inv-inv-canonical`, …) because `_module_exports`
    # reads POST-STRIP source and every record may name a conduit the strip emptied.
    # Refusing those would DELETE the key and with it the one-hop fallback at
    # `scope_edit:245`, which exists precisely to re-issue the rename one module further
    # in. `live == []` means THE TEST SAID NOTHING; it does not mean the records
    # conflict. So the criterion applies only where it actually separates.
    if not live:
        return tuple(recs)
    if len(live) == 1:
        return tuple(live)
    # REFUSE: several records SURVIVED the test, so they differ only in something this
    # index cannot adjudicate — the application argument, or a same-owner source-name
    # alternative. A position would decide it; nothing here legitimately can.
    return ()


def _imports_of(mod):
    """The `Substrate…` modules `mod` currently imports (its own body column only)."""
    body, ind = _module_text(mod)
    return [sub for sub, stmt in _open_stmts(body)
            if sub.startswith("Substrate") and len(stmt) - len(stmt.lstrip()) == ind]


def _conduit_set(path):
    """Modules reachable from the consumer along its own import edges (BFS, shallowest first).

    ⚑ THE `range(3)` IS A KNOWN, MEASURED BOUND — NOT AN OVERSIGHT, AND NOT MINE TO WIDEN HERE.
    Max pure-conduit chain depth in this corpus is 3, i.e. exactly AT the bound. Recorded as a
    separate item; a decomposition is a pure relocation and must not smuggle a behaviour change.
    """
    self_mod = module_path(path, "") if path.endswith(".agda") else None
    if not self_mod:
        return []
    cands, seen, frontier = [], {self_mod}, [self_mod]
    for _ in range(3):
        nxt = []
        for c in frontier:
            for s in _imports_of(c):
                if s in seen:
                    continue
                seen.add(s)
                cands.append(s)
                nxt.append(s)
        frontier = nxt
    return cands


def _conduit_owner(leaf, path):
    """The owner reachable through a CONDUIT the consumer already imports.

    After the strip, a name the consumer used to get transitively through `open import C …
    public` is supplied by one of C's OWN (already-repaired) imports. Restricting the candidate
    set to that one-hop chain is what keeps this from becoming a tree-wide guess — and it is the
    only route to an applied re-exporter like `Cyclic.Core n`, which no grep for `open import
    <definer>` can find because it re-exports through a LOCAL module."""
    self_mod = module_path(path, "") if path.endswith(".agda") else None
    if not self_mod:
        return None
    # BFS over the conduit chain, SHALLOWEST first: a stripped `public` can be several hops up
    # (`Z2-Coxeter` → `Cyclic` → `NthPower` → `Cyclic.Core`), and stopping at one hop reported
    # "no owner" for names that are two modules away along the consumer's own import edges.
    cands = _conduit_set(path)
    hits = []
    for sub in dict.fromkeys(cands):
        if not _owner_admissible(sub, path):
            continue
        if _module_params(sub) and not application_args(sub, path):
            continue                                  # unsuppliable ⇒ the import cannot typecheck
        if _module_exports(sub, leaf):
            hits.append(sub)
    if not hits:
        return None

    order = {m: i for i, m in enumerate(cands)}      # discovery order == hop distance

    def score(h):
        a, b = h.replace(".", "/").split("/"), path.split("/")
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        return (order[h], -i, len(_module_params(h)), len(h))
    return sorted(hits, key=score)[0]


def _suppliable(mod, path):
    return not _module_params(mod) or bool(application_args(mod, path))


def _conduit_pair(name, path):
    """(owner, SPELLING) from the conduit chain — an operator prints bare but imports as `_x_`."""
    o = _conduit_owner(name, path)
    if not o:
        return None, None
    for sp in (name, f"_{name}_"):
        if _module_exports(o, sp, exact=True):
            return o, sp
    return o, name


def _applied_owner(via, name):
    """`via` re-exported `name` through an APPLIED open, recorded as `via._.name`.

    Return (owner, args) for the `open import <owner> <args>` inside `via` that defines it —
    so the consumer can REDO the application instead of importing the owner unapplied."""
    # ⚑ `via` may be a LOCAL module (`module Newman (_⇒_) where open import …`), which has no
    # file of its own — reading `<via>.agda` silently returned "no owner" for exactly the
    # parameterized-wrapper conduits this function exists to resolve.
    src, _ind = _module_text(via)
    if not src:
        return None, ""
    for m in re.finditer(r"^[ \t]*open import (Substrate[\w.-]+)([^\n]*)$", src, re.M):
        owner, rest = m.group(1), m.group(2)
        if not (_module_defines(owner, name) or _module_defines(owner, f"_{name}_")
                or _module_exports(owner, name)):
            continue
        args = re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b", rest)[0].strip()
        return owner, args
    return None, ""


def application_args(owner, path):
    """Args to apply `owner` with, in the CONSUMER's context — '' if it cannot supply them.

    Sources, in order: the consumer's own existing application; then any module the consumer
    reached `owner` THROUGH (the `M._.name` qnames), whose source shows how M applied it."""
    params = _module_params(owner)
    if not params:
        return ""
    try:
        src = open(path).read()
    except OSError:
        return ""
    m = re.search(rf"^open import {re.escape(owner)}([^\n(]*?)(?:\busing\b|\brenaming\b|$)", src, re.M)
    cands = [m.group(1).strip()] if m and m.group(1).strip() else []
    for qn in consumer_refs(path):
        mod, extra = split_qname(qn)
        if mod and len(extra) == 2 and extra[0] == "_":
            o, a = _applied_owner(mod, extra[1])
            if o == owner and a:
                cands.append(a)
    for a in cands:
        toks = re.findall(r"[A-Za-z_][\w′]*", a)
        if toks and all(_in_scope(path, t) for t in toks):
            return a
    # ⚑ SAME-FAMILY application: a consumer that already writes `…Cyclic.Base 1` is applying the
    # whole `…Cyclic.*` family at 1 — the parameter is the family's index, not a per-module
    # accident. Matching on the shared parent AND identical parameter NAMES keeps this from
    # borrowing an unrelated neighbour's argument.
    fam = owner.rsplit(".", 1)[0]
    for c, stmt in _open_stmts(src):
        if not c.startswith("Substrate") or c == owner:
            continue
        if not (c.rsplit(".", 1)[0] == fam or owner.startswith(c + ".") or c.startswith(owner + ".")):
            continue
        if _module_params(c) != params:
            continue
        rest = stmt[stmt.index(c) + len(c):]
        a = re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b", rest)[0].split()
        if len(a) == len(params) and all(re.fullmatch(r"\d+", t) or _in_scope(path, t) for t in a):
            return " ".join(a)
    return _applied_via_import(owner, path)


def _applied_via_import(owner, path):
    """Arguments for `owner` obtained by SUBSTITUTING into a module the consumer already applies.

    The consumer writes `open import …Coxeter.Cyclic 1`; `Cyclic`'s own body says `open import
    …Cyclic.Base n` where `n` is Cyclic's parameter — so the consumer's arguments for `Base` are
    Cyclic's, with Cyclic's parameters replaced by the arguments the consumer supplied. This is
    the only route when the argument is a LITERAL (`1`), which lives in no scope and is therefore
    invisible to every name-based test."""
    try:
        src = open(path).read()
    except OSError:
        return ""
    def _args(text, mod):
        rest = text[text.index(mod) + len(mod):]
        return re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b", rest)[0].split()

    frontier = [(c, _args(s, c)) for c, s in _open_stmts(src) if c.startswith("Substrate")]
    seen = set()
    for _ in range(4):                                # the chain is short: Cyclic → NthPower → Base
        nxt = []
        for c, cargs in frontier:
            if (c, tuple(cargs)) in seen:
                continue
            seen.add((c, tuple(cargs)))
            if c == owner:
                if cargs and all(re.fullmatch(r"\d+", t) or _in_scope(path, t) for t in cargs):
                    return " ".join(cargs)
                continue
            params = _module_params(c)
            if len(params) != len(cargs):
                continue                              # a partial application cannot be substituted
            sub = dict(zip(params, cargs))
            cbody, _ci = _module_text(c)
            for sm, sstmt in _open_stmts(cbody):
                if sm.startswith("Substrate"):
                    nxt.append((sm, [sub.get(t, t) for t in _args(sstmt, sm)]))
        frontier = nxt
    return ""


_QNAME_CHAR = r"[\w′⁻¹·∙₀-₉ᵃ-ᶻα-ωΑ-Ω+*/^-]"


def _alias_names(src, alias):
    return set(re.findall(rf"(?<![\w.-]){re.escape(alias)}\.({_QNAME_CHAR}+)", src))


# ⚑ THE CATALOG-BACKED ORACLES BELOW ARE INJECTED, NOT IMPORTED — AND THAT IS THE ONE PLACE
# THE SPLIT COULD HAVE INTRODUCED A CYCLE. `_applied_owner` needs `_module_defines`, and
# `application_args` needs `consumer_refs`/`split_qname`; all three read catalog.db and rank
# candidates, which is the layer ABOVE this one (`scope_fix`). Importing `scope_fix` from here
# would close an import cycle — the exact hazard `_would_cycle` exists to catch in the Agda
# tree, reproduced in our own Python.
#
# So `scope_fix` binds them onto this module at import time (see its `scope_source.X = …`
# block). They are declared here as module-level names so the reference resolves against THIS
# module's globals at call time, and so a reader sees the dependency instead of inferring it.
# ⚑ NOT A DEFAULT-VALUED PARAMETER AND NOT A LAZY IMPORT: either would change a call signature
# or re-introduce the cycle at first use. This is a pure relocation; the seam absorbs the
# indirection rather than the call sites.
_module_defines = None      # (mod, leaf) -> bool          — set by scope_fix
consumer_refs = None        # path -> set(qname)           — set by scope_fix
split_qname = None          # qname -> (module, [extra])   — set by scope_fix
