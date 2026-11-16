#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import os as _om, sys as _sm
_sm.path.insert(0, _om.path.dirname(_om.path.abspath(__file__)))
from agda_lex import mask_comments as _mask   # THE comment authority; never re-derive
"""scope_fix.py — the ⟡public-paydown loop, mechanized.

THE PATTERN (user, 2026-07-26): remove the re-export/`public`, attempt a build, take the
error message as telling you what needs fixing; repeat along the dep graph, upstream and
downstream.  `[NotInScope]` is the instrument — it ENUMERATES the requirement and usually
NAMES the owner ("did you mean 'Substrate.Algebra.F2.Vector.Vector'?"), so the rewiring is
mechanical rather than hand-derived (hand-deriving an owner map got it wrong twice).

Loop: compile → parse the first `Not in scope: <name>` + its `at <file>:<line>` (which may
be a DEPENDENCY, not the file you started from) → resolve the owner (suggestion first, tree
search as fallback) → add/merge `open import <Owner> using (<name>)` into THAT file → repeat.

Usage:  scope_fix.py <file.agda> [more.agda …] [--max N] {--dry-run|--apply}
        scope_fix.py <file.agda> … --seed <conduit.agda>[,<more.agda>…] [--max N] {--dry-run|--apply}
Run from agda/.

⚑ THE MUTATION INTENT IS REQUIRED (⟡explicit-mutation). This tool WRITES to the Agda tree and
iterates up to `--max` times, so a bad run compounds before anything checks it. It used to write
whenever `--dry` was absent AND validated no argv, so a typo'd `--dry-run` wrote. Now `--dry-run`
XOR `--apply` must be stated; `--dry` is caught by name and redirected to `--dry-run`.

⚑ `--seed` IS THE OTHER HALF OF THE LOOP, and it exists because `[NotInScope]` is not the only
error shape. A missing OPERATOR never surfaces as `[NotInScope]` — it makes the application
UNPARSEABLE (`[NoParseForApplication]`), and that error names NO owner, so the instrument the
loop above relies on goes silent exactly where it is needed. The candidate set is recoverable
anyway: it is precisely what the stripped conduit used to re-export, so `--seed` reads that list
back out of `git show HEAD:<conduit>` and resolves against it. Comma-separated for several
conduits. ⚑ A seed of ZERO names is a REPORTED number, not a silent empty map: an empty seed
once read as "this conduit re-exported nothing" and a consumer's import was dropped as dead —
a fact about the REGEX reported as a fact about the file.

⚑rederive: this tool PREDATES the scratch/ helper modules and does not use them.
Declared here so it enters the duplication census as COUNTABLE debt rather than
invisible debt — a ratchet is over a materialized census, and an undeclared
divergence is the only kind that is inadmissible.  Verified 2026-07-31:

  1. NO COMMENT MASKING — ~40 regexes run against RAW source; `agda_lex.mask_comments`
     is the authority (nesting-aware, length-preserving, treats `-->` as a name).
     A commented-out `-- open import Foo public`, or import-shaped text inside a
     `{- … -}` block, parses here as live structure.  HIGHEST-VALUE FIX (M): it is
     wide and it CHANGES BEHAVIOUR, so it wants its own commit with a build behind it.
  2. `_stmt_span` (:1240) uses an UNGUARDED `(?:\n[ \t]+[^\n]*)*`; `agda_lex.statements`
     is the authority.  It feeds `fix_barrel`, whose consumers REWRITE matched text
     rather than delete a span, so over-reach costs a bad rewrite, not a gutted file.
     `_stmt_at` (:1406) is hand-guarded against `open|import|module` openers and is
     NOT the 33-file-gutting rule — mechanically verified: `convert_span_rule.py`
     reports 0 convertible sites in this file.  It is under-reaching (not depth-aware
     inside a wrapped `using (…)`), i.e. conservative-wrong rather than destructive.
  3. 33 inline module↔path conversions; no shared helper exists to adopt yet.
  4. Self-import guarded by a string compare (:317) plus `_would_cycle` (:1539), NOT by
     `agda_imports.importable` — which `demand_imports.py` already imports correctly.
     Both concerns are covered, by different machinery.

  (The line numbers in 2 and 4 are as of that audit and predate the splits below; the
  named functions now live in `scope_source`.  Kept verbatim — it is a DATED finding,
  and re-deriving its coordinates would make it look like a fresh one.)

It has ONE write path (`_write`, now in `scope_source` — every write site routes through it)
and snapshots via `edit_snapshot.guard` before any non-`--dry` run.  It writes BY DEFAULT;
pass `--dry` to preview.

⟡split-1200 — THIS TOOL IS NINE FILES, each an AUTHORITY ON ONE KIND OF TRUTH:

  scope_store   what the INTERNED CORES say (catalog.db + the SPPF `ref` index): PRE-strip
                truth — elaborated qnames, references, application indices, the demand
                relation, and this tool's `--selftest`.
  scope_source  what the CURRENT AGDA TEXT says (exports/imports/applications/renames/
                telescopes): POST-strip truth.  Owns THE WRITE PATH and the cycle guard.
  scope_resolve how a name is RANKED across those two oracles.
  scope_errors  what AGDA'S OUTPUT says — every compiler message this tool parses.
  scope_edit    HOW AN IMPORT STATEMENT IS WRITTEN: the four operations a handler ends in.
  scope_barrel  the STRIPPED-CONDUIT repairs (barrel / applied-open / wrapper-open).
  scope_alias   the ALIAS / QUALIFIED-NAME repairs, demand-first then source heuristics.
  scope_ctors   the PATTERN-POSITION constructor repairs — the class with no error at all.
  scope_fix     this file — the LOOP, its two own handlers, and the CLI.

⚑ THE PRE/POST-STRIP DISTINCTION IS WHY THE SPLIT IS ALONG THIS AXIS.  Reading the store
oracle where the source oracle was meant is a recorded defect of this arc: the catalog
reports what a module defined BEFORE the `public` re-exports were removed, so it is a false
positive for exactly the names being repaired, and the resolver then "writes an import that
binds nothing" (⟡pd-export-oracle).  Two files, two names, no ambiguity at a call site.

⚑ AND THE SEAM WAS FIXED BY A MEASUREMENT ABOUT GLOBALS, NOT BY TOPIC.  A `global` rebinds
only in the DEFINING module, so `_write` (which clears `_IMPORTS` to keep the cycle guard
honest after the loop's own edits) had to move WITH `_import_graph`; splitting them would
have left one clearing a name while the other read a stale graph — a silent defeat of the
guard, in a writer.  A `global`-rebound cache may not straddle a seam; an item-mutated dict
(`_ADDED`, `_DEMAND`) may, the object being shared.

⚑⚑ THE 2026-08-11 CUT (1107 → this) TOOK THE SAME LESSON ONE LEVEL FURTHER: THE SEAM IS THE
ARROW, NOT THE LINE COUNT.  What is left here is the CHAIN'S TOP — `fix()` consumes every
`fix_*` handler, the handlers consume `scope_edit`, and `scope_edit` consumes the oracles.
Moving a SUPPLIER leaves a leaf; moving a consumer would have left it reaching back up, which
is how a first attempt at a sibling split elsewhere in this session failed twice by cutting
the two LARGEST defs.  `fix_ambiguous` and `fix_parse_error` stayed with the loop precisely
because they are not part of that chain: both are answers to a whole compile OUTPUT rather
than to one name, and `fix_ambiguous` is the only handler that REMOVES an import (it rolls
back `_ADDED`), so it belongs beside the loop that made the addition.

⚑ AND `NOT_IN_SCOPE` WENT DOWN TO `scope_errors` FOR A REASON THAT IS ONLY VISIBLE AS A
DEPENDENCE.  Both `fix()` here and `fix_wrapper_open` in `scope_barrel` read it, so leaving
the pattern beside its first caller would have made a SUPPLIER import its CONSUMER — the
Python twin of the cycle `_would_cycle` refuses in the Agda tree.  Size named the violation;
direction chose the cut.

Dependencies are a CHAIN (store → source; neither imports this file).  Every relocated name
is re-exported here, so `scope_fix.X` and `from scope_fix import X` are unchanged for all
five measured consumers.
"""
import base64
import os
import re
import subprocess
import sys
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive
import agda_lex                    # module_scopes/binds_at — THE telescope authority

import scope_source
import scope_store
from scope_source import (            # noqa: F401 — RE-EXPORTED: the public surface must not move
    _ADDED, _alias_binding, _alias_names, _alias_target, _applied_owner, _applied_via_import,
    _conduit_owner, _conduit_pair, _conduit_set, _head_text, _import_graph, _imports_of,
    _in_scope, _is_file_module, _local_module_file, _module_exports, _module_params,
    _module_text, _nearest_reexporter, _open_stmts, _owner_admissible, _parent_kind,
    _QNAME_CHAR, _reexports_fields, _rename_index, _rename_pairs, _stmt_at, _stmt_span,
    _suppliable, _wrapper_owner, _would_cycle, _write, application_args,
    # ⚑ ⟡rename-index-arbitrary-carrier — the RANKED/REFUSING accessor over
    # `_rename_index`. Re-exported alongside the raw index because this module's header
    # promises `scope_fix.X` keeps working for every name in `scope_source`, and a new
    # public name that the facade does not forward is exactly the half-landed edit
    # `pycodemod`'s own banner records (`rewire_only`: written, documented, never wired).
    rename_records,
)
# ⚑⚑ `_selftest` IS NO LONGER RE-EXPORTED FROM HERE, AND ITS PRESENCE WAS A DOUBLE-COUNT.
# `run_selftests` invokes `python <path> --selftest` per discovered suite; this module and
# `scope_store` are BOTH pairs (body + dispatch), so re-exporting the body made ONE suite run
# under TWO names and report its cases twice. MEASURED 2026-08-11: both read `VACUOUS 0/0` with
# byte-identical output, for byte-identical reasons — because it was byte-identically the same
# function. That is the `schema_selftest.py` class arriving from the other direction, and the
# runner's own note names the trade: a visible NOT-OK is strictly better than a silent
# over-count. A selftest is not public surface; it is this module's own suite, below.
from scope_store import (             # noqa: F401 — RE-EXPORTED: the public surface must not move
    _b64, _connect_catalog, _demand_of, _DEMAND, _DEMAND_CANDS, _event_refs, _FREE_CTORS,
    _module_defines, _owner_of_ref, audit_demand, catalog_index, consumer_refs,
    owner_by_catalog, ref_index, split_qname,
)
from scope_resolve import (           # noqa: F401 — RE-EXPORTED: the public surface must not move
    SUGG, _resolve_owner, owner_by_search, owner_from_shape, owner_from_suggestion,
    owner_of_ctor, shape_candidates,
)
# ⚑ THE FIVE MODULES BELOW ARE THE 2026-08-11 CUT, AND THEY ARE RE-EXPORTED ON THE SAME TERMS.
# `scope_fix.add_import`, `scope_fix.fix_barrel`, `scope_fix.NOT_IN_SCOPE` … all still resolve;
# a relocation is never an interface change, which is what makes it safe to do at all.
#
# ⚑ AND `SUGG` IS NOT RE-DECLARED HERE ANY MORE, WHICH IS A DELETION AND NOT A MOVE. This file
# carried `SUGG = re.compile(r"'([^']+)'")` at :120 — byte-identical to `scope_resolve`'s, and
# SHADOWING the import twelve lines above it. Measured (`pycodemod --shape '\bSUGG\b' scratch/`):
# four sites, of which the only READ is `scope_resolve:70`, inside the one function that owns it.
# So the local copy bound nothing anybody consulted while quietly making `scope_fix.SUGG` a
# different object from `scope_resolve.SUGG` — the shared-NAME-is-not-shared-AUTHORITY shape.
from scope_errors import (            # noqa: F401 — RE-EXPORTED
    ALIAS_ERR, AMBIGUOUS, BARREL_W, CTOR_ERRS, CYCLIC, NOT_IN_SCOPE,
)
from scope_edit import (              # noqa: F401 — RE-EXPORTED
    _rename_owner, _repoint_alias, add_import, add_renaming_import,
)
from scope_barrel import (            # noqa: F401 — RE-EXPORTED
    _barrel_owner, _owner_for, fix_applied_open, fix_barrel, fix_wrapper_open,
)
from scope_alias import (             # noqa: F401 — RE-EXPORTED
    fix_alias_fanout, fix_alias_split, fix_arg_name_closure, fix_demand, fix_qualified,
    fix_unapplied_import,
)
from scope_ctors import (             # noqa: F401 — RE-EXPORTED
    fix_alias_repoint, fix_missing_ctor, fix_silent_ctors,
)

# ⚑ `scope_source` NEEDS THREE CATALOG ORACLES AND TAKES THEM BY INJECTION, NOT IMPORT.
# `scope_source._applied_owner` needs `_module_defines`, and its `application_args` needs
# `consumer_refs`/`split_qname` — all three are STORE questions, i.e. the layer ABOVE it.
# Having `scope_source` import `scope_store` would close a Python import cycle (store already
# imports source): the exact hazard `_would_cycle` exists to catch in the Agda tree,
# reproduced in our own tooling. Binding them onto the module object keeps the chain acyclic
# and the dependency visible. Done here, once, where both modules are already loaded.
scope_source._module_defines = scope_store._module_defines
scope_source.consumer_refs = scope_store.consumer_refs
scope_source.split_qname = scope_store.split_qname



# ⚑ ABSOLUTE, DERIVED FROM THIS FILE — a relative `../scripts/membudget` made the tool
# invocable ONLY from `agda/`, and the repo forbids `cd X && tool` (the no-chaining hook
# refuses a composed command, and a one-off pipeline is a one-off approval).  So the
# tool's own docstring said "Run from agda/" while the only compliant way to satisfy
# that was a chain the hook rejects: a capability bound wearing a usage note.
# `os.path.dirname(__file__)` is `scratch/`, so the sibling is one level up.
MEMBUDGET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "scripts", "membudget")


def compile_one(f):
    r = subprocess.run([MEMBUDGET, "run", "384", "scopefix", "--",
                        "agda", "--safe", "--without-K", "-i.", f],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def fix_ambiguous(out, dry=False):
    """⚑ T6 ⟡pd-ambiguity-rollback: drop the import WE added for an ambiguous name.

    `[AmbiguousName] n` means `n` is in scope twice. The tool's own additions are the usual
    second source — typically a top-level UNAPPLIED `using (n)` layered on top of a name the
    file already gets from an APPLIED open, which are two distinct names for a parameterized
    module. Removing what we added is the only rollback that is provably safe: it restores the
    file's pre-tool scope for `n`."""
    fixed = 0
    for m in AMBIGUOUS.finditer(out):
        path = os.path.relpath(m.group("file"), os.getcwd())
        name = m.group("name")
        module = _ADDED.get((path, name))
        if not module:
            continue
        try:
            src = open(path).read()
        except OSError:
            continue
        # drop the whole statement if `n` is all it brings in, else just the one name
        one = re.compile(rf"^open import {re.escape(module)}[^\n(]*using \(\s*{re.escape(name)}\s*\)"
                         r"[^\n]*\n", re.M)
        new, n = one.subn("", src)
        if not n:
            merged = re.compile(r"(open import " + re.escape(module) + r"[^\n(]*using \()([^)]*)(\))", re.S)
            mm = merged.search(src)
            if not mm:
                continue
            names = [x.strip() for x in re.split(r"[;\s]+", mm.group(2)) if x.strip()]
            if name not in names:
                continue
            names.remove(name)
            new = src[:mm.start(2)] + "; ".join(names) + src[mm.end(2):]
        if new == src:
            continue
        # ⚑⚑ THE LEDGER POP IS PART OF THE WRITE, AND IT USED TO SIT OUTSIDE THE GUARD. `dry`
        # guarded `_write` and nothing else, so a PREVIEW consumed its own rollback record.
        #
        # ⚑ AND THE HARM IS TO THE PREVIEW'S FIDELITY, NOT TO SOURCE — measured, because I
        # first read it as a source-damage defect and it is not. `_ADDED` is process-local
        # (`scope_source.py:164`, never persisted), and a dry run writes nothing, so a real run
        # in a fresh process is unaffected. What breaks is WITHIN the dry run: `fix()` iterates
        # compile→fix→recompile, the unwritten file reports the same `[AmbiguousName]` again,
        # and the second pass finds no ledger entry, hits `continue`, and silently stops
        # reporting a fix it is perfectly able to make. **A preview that under-reports the run
        # it previews is worse than no preview** — it reads as "nothing more to do".
        if not dry:
            _write(path, new)
            _ADDED.pop((path, name), None)
        # ⚑ AND THE VERB MUST MATCH THE MODE. Saying "rolled back" on a dry run states that a
        # file changed when none did — the same class as a census that prints a total it did
        # not measure.
        print(f"    {path}: {'would roll back' if dry else 'rolled back'} `{name}` ← {module}"
              f"   [ambiguous; it was already in scope]")
        fixed += 1
    return fixed


def seed_map(stripped):
    """name → owning module, from the `public` re-exports a conduit JUST LOST (git diff).

    A missing OPERATOR does not surface as `[NotInScope]` — it makes the application
    unparseable (`[NoParseForApplication]`), which names no owner.  But the candidate set is
    exactly what the stripped conduit used to re-export, so recover it from the diff.
    """
    pre = subprocess.run(["git", "rev-parse", "--show-prefix"],
                         capture_output=True, text=True).stdout.strip()
    r = subprocess.run(["git", "show", f"HEAD:{pre}{stripped}"], capture_output=True, text=True)
    seed = {}
    # ⚑⚑ `public` AND `using` COMMUTE, AND MATCHING ONE ORDER SILENTLY SEEDS
    # NOTHING.  This required `using (…) public`; `Algebra/Z/Arithmetic.agda`
    # writes `public using (…)` — both are valid Agda, and the census
    # (`agda_defs --reexports`) shows BOTH orders live in the tree (9 sites in
    # `AES.AES` use the first, the 4 in `Q.Arithmetic` the second).
    #
    # MEASURED 2026-08-17: the mode printed `seed: 0 name(s)` and then dropped a
    # consumer's import as DEAD — a silent empty map reads as "this conduit
    # re-exported nothing", which is a fact about the REGEX reported as a fact
    # about the file.  A seed that cannot be empty-by-accident is the point of
    # recovering it from git at all.
    for m in re.finditer(
            r"open import ([\w.-]+)\s+(?:public\s+using\s*\(([^)]*)\)"
            r"|using\s*\(([^)]*)\)\s+public)", r.stdout):
        for n in re.split(r"[;\s]+", m.group(2) or m.group(3) or ""):
            if n.strip():
                seed[n.strip()] = m.group(1)
    # ⚑ A BARE `open import M public` RE-EXPORTS EVERYTHING M PROVIDES, and it is
    # 14 of the 48 censused sites — invisible to any `using`-shaped pattern.
    for m in re.finditer(r"open import ([\w.-]+)\s+public\s*$", r.stdout, re.M):
        try:
            import agda_defs as _ad
            for n in _ad.provides(m.group(1)):
                seed.setdefault(n, m.group(1))
        except Exception:
            pass
    return seed


def seed_key(tok, seed):
    """The seed key `tok` names, across agda's THREE spellings — or None.

    An operator has one declaration (`_+ℤ_`) and several renderings, and agda
    prints the one the SITE used:
      · bare        `+ℤ`      — an infix use, quoted without its underscores
      · declared    `_+ℤ_`    — the name as imported
      · a SECTION   `_+ℤ`     — partially applied; the underscores that survive
                                are the argument slots still open

    ⚑⚑ THE THIRD WAS MISSING AND COST A REPAIR.  MEASURED 2026-08-17 on
    `Q/Properties/Field.agda:108` — `Could not parse the application
    _+ℤ (na *ℤ (+ suc da₋))`.  The seed HELD `_+ℤ_` and the owner was
    unambiguous, but the caller probed only `tok` and `_tok_`, so a right
    section matched neither; `fix_parse_error` reported a non-scope error on a
    file it could have repaired and the import went in by hand.

    ⚑ EXTRACTED SO IT CAN BE DRIVEN.  `fix_parse_error` is uncovered by this
    module's suite for a stated reason — it writes to a real Agda tree and asks
    the catalog, neither of which the suite has a fixture for.  The SPELLING
    question is not that: it is a pure predicate over two strings, so pulling it
    out converts an untestable branch into a tested one rather than adding a
    case that asserts what a stub returns.
    """
    if tok in seed:
        return tok
    if f"_{tok}_" in seed:
        return f"_{tok}_"
    # section syntax: a leading/trailing `_` is an open argument slot, never
    # part of the name.  Strip and re-probe the two canonical forms.
    if tok.startswith("_") or tok.endswith("_"):
        bare = tok.strip("_")
        if bare:
            if bare in seed:
                return bare
            if f"_{bare}_" in seed:
                return f"_{bare}_"
    return None


def fix_parse_error(out, seed, dry=False):
    """A parse error names no owner — add every SEED name appearing in the failing expression."""
    # three shapes carry an unparseable expression: NoParseForApplication (missing operator),
    # NoParseForLHS (missing constructor in a pattern), AmbiguousParseForLHS.
    m = re.search(r"(?P<file>[^\s:]+):[\d.\-]+: error: \[NoParseFor\w+\]"
                  r".*?Could not parse the (?:application|left-hand side)\s*(?P<expr>.*?)"
                  r"\n(?:Problematic expression|Operators used)", out, re.S)
    if not m:
        return False
    path = os.path.relpath(m.group("file"), os.getcwd())
    added = False
    for tok in set(re.split(r"[\s()\{\}]+", m.group("expr"))):
        if not tok or tok in (":", "=", "→", "?", "_", "...", "|"):
            continue
        key = seed_key(tok, seed)
        if key:
            owner, spell = seed[key], key
        else:
            # not from a stripped conduit — ask the CATALOG (the interned cores). Unlike a free
            # grep search (which wrote a self-import and a wrong-tier `sgn`), this refuses
            # record fields and resolves constructors to their real home.
            owner, spell = owner_by_catalog(tok, path)
            if not owner:
                continue
        ok, how = add_import(path, owner, spell, dry)
        if ok:
            print(f"    {path}: {tok} (as {spell}) ← {owner}   [{how}]")
            added = True
    return added


def fix(target, max_iters=40, dry=False, seed=None):
    seed = seed or {}
    alias_owner = {}          # alias → owner, so siblings of one alias stay cohesive
    deferred = set()          # names this file cannot bind — skipped, not fatal (⟡pd-refusal-not-terminal)
    # ⚑ BOUND BEFORE THE LOOP so the cap report can read it: `max_iters=0` would
    # otherwise reach the exhaustion branch with `out` undefined and raise there —
    # a guard that crashes instead of reporting.
    out = ""
    for i in range(max_iters):
        # ⚑ T8: in --dry the handlers report what they WOULD write without writing, so the loop
        # would re-see identical output and spin to max_iters. One proposal is the whole point.
        if dry and i:
            return False
        rc, out = compile_one(target)
        # ⚑ A SUCCESSFUL compile is NOT necessarily a correct one. `ModuleDoesntExport` (an
        # `open`/`using` that binds nothing) and `PatternShadowsConstructor` (a constructor
        # silently demoted to a catch-all pattern variable) are WARNINGS — the file typechecks
        # with altered semantics and the breakage appears only in a downstream consumer.
        # Throwing away a green compile's output is what let `rotate _ = _` ship.
        silent = re.search(r"-W\[no\](ModuleDoesntExport|PatternShadowsConstructor)", out)
        if rc == 0 and not silent:
            print(f"  ✓ {target} clean after {i} fix(es)")
            return True
        if rc == 0:
            print(f"    ⚠ {target}: compiles, but a warning says a binding is missing — continuing")
        # ⚑ an UNAPPLIED import of a parameterized module is wrong in every context, so repair it
        # before reading the error — the error it causes (`(A : Set) → Set` is not a sort) names
        # neither the import nor the module, and no error-driven handler can find it.
        if fix_unapplied_import(target, dry) or fix_alias_split(target, dry) \
                or fix_alias_fanout(target, dry):
            continue
        # the barrel warning is the ROOT CAUSE of the NotInScope below it — handle it first
        if fix_barrel(out, dry) or fix_applied_open(out, dry) or fix_wrapper_open(out, dry):
            continue
        # a pattern-position constructor fails with a NON-scope error — handle before
        # falling through to the `Not in scope:` path, which cannot see it
        if fix_missing_ctor(out, target, dry):
            continue
        if fix_alias_repoint(out, dry):
            continue
        # ⚑ T6: ambiguity is caused by having too MANY names in scope, so it is the one class
        # an add-only tool can never fix by adding. Roll back our own addition instead.
        if fix_ambiguous(out, dry):
            continue
        # ⚑ T7 ⟡pd-wire-silent-ctors: this handler was written, documented as THE silent
        # miscompile repair, and never called from anywhere. A constructor silently demoted to
        # a catch-all pattern variable compiles GREEN with altered semantics; the ⚠ branch above
        # detects it, and this is what repairs it — in the file the warning NAMES, which is
        # often a dependency rather than the target.
        if silent:
            sp = re.search(r"(?P<f>[^\s:]+\.agda):[\d.\-]+: warning: "
                           r"-W\[no\](?:PatternShadowsConstructor|ModuleDoesntExport)", out)
            spath = target
            if sp:
                try:
                    spath = os.path.relpath(sp.group("f"), os.getcwd())
                except ValueError:
                    spath = target
            if os.path.exists(spath) and fix_silent_ctors(spath, dry):
                continue
        # ⚑ T7: take the first not-in-scope error we have NOT already given up on, so one
        # unresolvable name no longer masks every fixable error behind it.
        m = next((x for x in NOT_IN_SCOPE.finditer(out) if x.group("name") not in deferred), None)
        if not m:
            if fix_parse_error(out, seed, dry):
                continue
            if deferred:
                print(f"  ✗ {target}: unresolved {sorted(deferred)}")
                return False
            err = re.search(r"^.*: error:.*$", out, re.M)
            print(f"  ✗ {target}: non-scope error — {err.group(0) if err else 'unknown'}")
            return False
        name, path = m.group("name"), os.path.relpath(m.group("file"), os.getcwd())
        # ⚑ T22 ⟡demand-first-resolver. The DEMAND RELATION goes first — ahead of every source
        # heuristic, qualified or not. `_node.op_path_id` records what this definition ACTUALLY
        # referenced, elaborated: the conduit is already skipped and the name is the definer's own
        # canonical spelling. Every resolver below reads post-strip SOURCE, which cannot separate
        # homonyms (`Base.Canonical : Fin (suc n) → Set` from `Existential.Canonical-ex : Word Gen
        # → Set` — five `copy=0` definitions share the leaf `Canonical`). Consulting the canonical
        # relation last is what let the loop plateau while binding plausible-but-wrong owners.
        if fix_demand(name, path, dry):
            continue
        if "." in name and fix_qualified(name, path, dry, m.group("sugg"), alias_owner):
            continue
        owner = spell = None
        fallback = None
        reach = set(_conduit_set(path))
        cp_owner, cp_spell = _conduit_pair(name, path)
        for resolve in (lambda: owner_from_shape(name, path),   # what this file ACTUALLY referenced
                        # ⚑ the conduit chain is evidence from THIS file's own import edges; the
                        # ranked catalog is a tree-wide guess that will happily hand back an
                        # unrelated module which merely happens to export the name (`ε` from
                        # `F2Cubed` instead of the `Cyclic.Core` the file is built on).
                        lambda: _conduit_pair(name, path),
                        lambda: owner_by_catalog(name, path),
                        lambda: owner_from_suggestion(name, m.group("sugg")),
                        lambda: owner_by_search(name, path)):
            o, sp = resolve()
            if not (o and _owner_admissible(o, path)):   # ⚑ T4: one guard, every resolver
                continue
            # ⚑ prefer an owner that still EXPORTS the name. Every resolver above reads
            # pre-strip data, so each can name a module whose route to the name was the very
            # `public` this arc removed — and the import it writes then binds nothing, which
            # reads downstream as `already imported` on a name that is still missing.
            if _module_exports(o, sp or name) and _suppliable(o, path):
                # ⚑ prefer an owner the file ALREADY REACHES over one that would add a brand-new
                # dependency edge. The pre-strip reference set can name a module this file merely
                # co-occurred with (`normalize` from `V4-Coxeter` in a `Cyclic`-built module);
                # importing it compiles the name but wires the wrong instance.
                if cp_owner and cp_owner != o and o not in reach:
                    owner, spell = cp_owner, cp_spell
                else:
                    owner, spell = o, sp
                break
            # only fall back to an owner we could not READ — one whose source says it does not
            # export the name will produce an import that binds nothing, and the loop then reads
            # the still-missing name as `already imported` and spins.
            if fallback is None and not _module_text(o)[0]:
                fallback = (o, sp)
        if not owner and fallback:
            owner, spell = fallback
        if not owner:
            # ⚑ T18 ⟡pd-renaming-target. A name that is a RENAMING TARGET is a qname nowhere, so
            # every resolver above is structurally blind to it; the alias module's own `renaming`
            # clause is the only record of where it comes from. Re-issue that rename at the definer.
            ro, rsrc, rargs = _rename_owner(name, path)
            if ro:
                ok, how = add_renaming_import(path, ro, rsrc, name, dry, rargs)
                print(f"    {path}: {name} ← {ro} renaming ({rsrc} to {name})   [{how}]")
                if dry:
                    return False
                if ok:
                    continue
            print(f"  ✗ {target}: no owner found for `{name}` (needed in {path})")
            deferred.add(name)
            continue
        ok, how = add_import(path, owner, spell, dry)
        print(f"    {path}: {name} (as {spell}) ← {owner}   [{how}]")
        if dry:
            return False
        if not ok:
            # ⚑ T7 ⟡pd-refusal-not-terminal. A refusal is about THIS NAME, not the file. Giving
            # up here abandoned files whose remaining errors were fixable, and — when the reason
            # was `already imported` — printed a FIX-SHAPED line for a no-op, which is why two
            # files recurred every pass in every run with neither a ✓ nor a ✗ to explain them.
            deferred.add(name)
    # ⚑⚑ THE CAP IS A THRASH DETECTOR, AND IT FIRED WITHOUT SAYING WHAT IT DETECTED.
    # This printed `hit max_iters` and nothing else, so the one state the guard exists
    # to surface — WHAT the loop was still doing on round N — was the state it threw
    # away.  MEASURED 2026-08-17/18: a `--max 40` run on four files ran ~10 hours; the
    # cap is what should have made that legible in minutes, and the output would not
    # have said any more than "it stopped".
    #
    # ⚑⚑ AND THE REPORT MUST NOT CLAIM THRASHING.  Without cycle detection, "looping"
    # and "one round short" are INDISTINGUISHABLE from here (operator, 2026-08-18:
    # *"You'll never know whether or not the fix was just around the corner unless you
    # do cycle detection"*) — and that detection is deliberately not built.  So this
    # states the STATE, never a verdict about convergence: what the last compile said,
    # which names were given up on, and how many rounds ran.  A guard that names its
    # cause is the rule; a guard that names a cause it cannot establish is worse than
    # one that stays quiet.
    print(f"  ✗ {target}: stopped at the {max_iters}-round cap "
          f"(round limit reached — NOT a verdict that it was looping; "
          f"whether a fix was one round away is undecidable without cycle detection)")
    if deferred:
        # the names the loop knowingly abandoned — each already reported once, but a
        # reader arriving at the cap needs them here rather than scrolled off above.
        print(f"      gave up on {len(deferred)} name(s): {sorted(deferred)}")
    _last = re.search(r"^.*: error:.*$", out, re.M) if out else None
    if _last:
        print(f"      last error: {_last.group(0)[:140]}")
    elif out and re.search(r"-W\[no\]", out):
        # the `rc == 0 but a warning says a binding is missing` path — it `continue`s,
        # so a file can reach the cap while COMPILING.  Saying so matters: that is a
        # different state from a file that never built, and the two want different work.
        print("      last compile SUCCEEDED with a missing-binding warning "
              "(the ⚠ path above) — the file builds; the loop kept going on the warning")
    print(f"      re-run with a higher --max to continue, or read the last error above")
    return False


# ⚑ THE `if __name__` BLOCK THAT LIVED HERE HAS MOVED TO THE END OF THE MODULE, and the
# move is the fix for a defect I introduced and then misdiagnosed twice.
#
# It was MID-FILE and called `sys.exit`, so everything below it was unreachable as a CLI.
# When I added a `--selftest` dispatch at the end of the module it never ran: on
# `--selftest` the arg filter drops the flag, `args` is empty, `all(...)` over nothing is
# True, and the exit fired with status 0 — silently, before reaching the dispatch.
#
# ⚑ I READ THAT SILENCE AS IMPORT COST. `scope_fix.py --selftest` printing nothing, plus the
# runner exceeding 120s, looked like "this module does expensive work at import". It does
# not; the CLI simply exited first. I had dispatched two agents on the import-cost
# hypothesis before checking whether the entry point was even reached.
#
# ⚑ AND HOISTING THE DISPATCH INTO THIS BLOCK DOES NOT WORK EITHER — measured, `NameError`.
# A mid-file `__main__` guard executes DURING module execution, so it cannot dispatch to
# anything declared after it. Two entry points in one module is the defect; a module has
# ONE, and the only place it can see the whole module is the end.


def _selftest():
    """⚑⚑ THIS MODULE HAD NO SUITE OF ITS OWN — IT RAN `scope_store`'s (2026-08-11).
    `_selftest` sat in the `from scope_store import (…)` re-export list beside the real public
    surface, so `scope_fix.py --selftest` executed a function that verifies the STORE resolver
    and knows nothing about this file. Both suites therefore reported `VACUOUS 0/0` with
    byte-identical output — one measurement, counted twice, of neither module's own machinery.

    ⚑ AND THE MODULE IT LEFT UNVERIFIED IS A WRITER. `fix_ambiguous` REWRITES AGDA SOURCE, and
    its whole safety argument is that it only ever removes an import THIS TOOL ADDED — a
    property nothing drove. These cases drive it against real files in a temp dir, on both the
    dry and the writing path.

    ⚑ `seed_map`, `fix_parse_error` and `fix` ARE NOT COVERED HERE, and that is a stated gap
    rather than a silent one: `seed_map` shells to `git show HEAD:<path>` (its result is a fact
    about the checkout's history, not about the parser), and the other two drive `add_import`
    against a real Agda tree plus the catalog. Neither can be given a truthful case without a
    fixture this suite does not have — and a case that asserts what a stub returns would be a
    fabricated denominator, which is worse than an honest absence."""
    import ast as _ast
    import io as _io
    import tempfile as _tf
    from contextlib import redirect_stdout as _redirect_stdout
    _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
    import rungs
    check = rungs.Cases(key="scratch/scope_fix.py")
    _this = sys.modules[__name__]

    # ── the RE-EXPORT SURFACE: "the public surface must not move", as a case ──────────────
    # ⚑ THE CENSUS IS DERIVED FROM THIS FILE'S OWN IMPORTS, never a second list to drift. The
    # defect it guards is MEASURED and recorded above: a local `SUGG = re.compile(r"'([^']+)'")`
    # shadowed the import twelve lines over, so `scope_fix.SUGG` was a DIFFERENT OBJECT from
    # `scope_resolve.SUGG` — a shared NAME presenting as a shared AUTHORITY.
    _reex = {}
    for _n in _ast.parse(open(__file__, encoding="utf-8").read()).body:
        if isinstance(_n, _ast.ImportFrom) and (_n.module or "").startswith("scope_"):
            _reex.setdefault(_n.module, []).extend(a.name for a in _n.names)
    check("the re-export census is non-empty (this file IS a facade)",
          len(_reex) >= 6 and sum(len(v) for v in _reex.values()) > 40, True)
    for _mod, _names in sorted(_reex.items()):
        _src = sys.modules[_mod]
        _moved = [n for n in _names
                  if getattr(_this, n, None) is not getattr(_src, n, object())]
        check(f"every name re-exported from {_mod} IS the supplier's object "
              f"(not a local shadow)", _moved, [])

    # ── seed_key: agda's THREE spellings of one operator ──────────────────────────────────
    # ⚑ THE SECTION SPELLING WAS MISSING AND COST A REPAIR (Ⓣ23).  `fix_parse_error` probed
    # `tok` and `_tok_` only, so `_+ℤ (na *ℤ …)` — a RIGHT SECTION, which is how agda prints a
    # partially-applied operator — matched neither while the seed held `_+ℤ_`.  Measured on
    # `Q/Properties/Field.agda:108`: owner unambiguous, repair available, mode reported a
    # non-scope error and the import went in by hand.
    _sd = {"_+ℤ_": "Substrate.Algebra.Z.Add", "_*ℤ_": "Substrate.Algebra.Z.Mul"}
    check("seed_key: the DECLARED spelling matches itself", seed_key("_+ℤ_", _sd), "_+ℤ_")
    check("seed_key: a BARE infix token resolves to the declared name",
          seed_key("+ℤ", _sd), "_+ℤ_")
    check("seed_key: a RIGHT section `_+ℤ` resolves (the Ⓣ23 case)",
          seed_key("_+ℤ", _sd), "_+ℤ_")
    check("seed_key: a LEFT section `+ℤ_` resolves too", seed_key("+ℤ_", _sd), "_+ℤ_")
    # ⚑ AND IT MUST NOT INVENT A MATCH.  Stripping underscores off an unrelated token could
    # collide with a seeded name; a token the seed does not hold is None, never a guess — the
    # caller falls through to the CATALOG, which refuses record fields and resolves
    # constructors to their real home.
    check("seed_key: a name the seed does not hold is None", seed_key("_∷_", _sd), None)
    check("seed_key: a bare `_` is not a name", seed_key("_", _sd), None)

    # ── the CAP REPORT: a guard that fires must say what it detected (Ⓣ26′) ───────────────
    # ⚑ THE EXHAUSTION BRANCH HAD NEVER BEEN DRIVEN.  It printed `hit max_iters` — the file
    # and nothing else — so the ONE state the guard exists to surface (what the loop was
    # still doing on round N) was the state it discarded.  `max_iters=0` reaches it without
    # compiling anything, which is what makes it testable at all: the loop body needs a real
    # Agda tree, the REPORT needs only the exhaustion path.
    _cap = _io.StringIO()
    with _redirect_stdout(_cap):
        _capped = fix("/nonexistent/Target.agda", max_iters=0, dry=True)
    _capout = _cap.getvalue()
    check("the cap path returns False (a stop is not a success)", _capped, False)
    check("the cap report names the round limit that fired",
          "0-round cap" in _capout, True)
    # ⚑⚑ AND IT MUST NOT CALL IT THRASHING.  Without cycle detection, "looping" and "one
    # round short" are indistinguishable from here, and that detection is deliberately not
    # built.  A guard naming a cause it cannot establish is worse than one that stays quiet
    # — the same rule as `NOT CONFIRMED IS NOT FAILED`.
    check("the cap report does NOT claim the loop was looping",
          "undecidable without cycle detection" in _capout, True)
    check("...and offers the continuation (a higher --max), not a verdict",
          "--max" in _capout, True)
    # ⚑ `out` IS BOUND BEFORE THE LOOP so this path cannot raise on an unbound name —
    # a guard that crashes instead of reporting is the failure mode one level down.
    check("the cap path survives max_iters=0 (no unbound `out`)",
          isinstance(_capout, str) and bool(_capout), True)

    # ── the ORACLE INJECTION: three store questions bound onto `scope_source` ─────────────
    # ⚑ THIS IS THE ACYCLICITY MECHANISM, and nothing drove it. `scope_source` needs three
    # catalog oracles; importing `scope_store` there would close a Python import cycle — the
    # hazard `_would_cycle` catches in the Agda tree, reproduced in our own tooling. The
    # binding is done once, here, and a future edit that drops a line breaks a caller far away.
    for _nm in ("_module_defines", "consumer_refs", "split_qname"):
        check(f"scope_source.{_nm} is injected from scope_store (the acyclic chain)",
              getattr(scope_source, _nm, None) is getattr(scope_store, _nm), True)

    # ── the AmbiguousName instrument ──────────────────────────────────────────────────────
    _msg = ("/x/C.agda:12.1-9: error: [AmbiguousName]\n"
            "Ambiguous name n. It could refer to any one of\n")
    _m = AMBIGUOUS.search(_msg)
    check("AMBIGUOUS reads the file and the name out of agda's message",
          (_m.group("file"), _m.group("name")) if _m else None, ("/x/C.agda", "n"))

    # ── fix_ambiguous: it may ONLY roll back what THIS TOOL added ─────────────────────────
    _cwd = os.getcwd()
    with _tf.TemporaryDirectory() as _td:
        try:
            os.chdir(_td)
            _p = os.path.join(_td, "C.agda")
            _err = (f"{_p}:12.1-9: error: [AmbiguousName]\n"
                    "Ambiguous name n. It could refer to any one of\n")
            _body = "module C where\nopen import Some.Mod using (n)\nx = n\n"

            # ⚑ THE SAFETY ARGUMENT, DRIVEN: an ambiguity we did NOT cause is left alone.
            # Without this case the handler could roll back any import and still pass.
            open(_p, "w").write(_body)
            _ADDED.clear()
            check("an ambiguity this tool did not cause is NOT rolled back",
                  fix_ambiguous(_err), 0)
            check("...and the file is untouched", open(_p).read(), _body)

            # dry: it REPORTS the rollback and writes nothing
            _ADDED[("C.agda", "n")] = "Some.Mod"
            check("a dry run reports the rollback", fix_ambiguous(_err, dry=True), 1)
            check("...and writes nothing", open(_p).read(), _body)
            # ⚑⚑ THIS CASE WAS WRITTEN INVERTED — PINNING THE DEFECT AS MEASURED — AND FIXING
            # THE DEFECT IS WHAT FLIPPED IT. The dry path used to POP the `_ADDED` entry:
            # `dry` guarded the WRITE and nothing else, so a preview consumed its own rollback
            # record. The pop now sits inside `if not dry:`, with the write it belongs to.
            #
            # ⚑ AND THE ORIGINAL NOTE MISJUDGED THE HARM, WHICH IS WHY IT READ AS DEFERRABLE.
            # It called the pop "harmless as invoked today", reasoning that `--dry` is a
            # whole-run mode so no writing pass follows in that process. True — but `fix()`
            # ITERATES compile→fix→recompile, and the unwritten file reports the same
            # `[AmbiguousName]` on the next pass. With the entry consumed, that pass hits
            # `continue` and the tool silently stops reporting a fix it can make. The harm was
            # never to source; it was to the PREVIEW'S FIDELITY, and a preview that
            # under-reports the run it previews reads as "nothing more to do".
            check("...and LEAVES the _ADDED entry, so the real pass can still roll it back",
                  ("C.agda", "n") in _ADDED, True)

            # ⚑ THE WHOLE STATEMENT GOES when the ambiguous name is all it brings in —
            # leaving `using ()` behind would be a different (and invalid) import.
            _ADDED[("C.agda", "n")] = "Some.Mod"
            check("the write path removes the statement we added",
                  fix_ambiguous(_err), 1)
            check("...the whole `using (n)` line, and only it",
                  open(_p).read(), "module C where\nx = n\n")
            # ⚑ AND THE LEDGER ENTRY IS CONSUMED, so a second pass is a no-op rather than a
            # second edit against a file that no longer has the line.
            check("the _ADDED entry is popped after the rollback",
                  ("C.agda", "n") in _ADDED, False)
            check("...so a second pass changes nothing", fix_ambiguous(_err), 0)

            # ⚑ THE MERGED FORM IS THE OTHER BRANCH, and it must remove ONE NAME, not the
            # line: dropping the whole statement here would take two live names with it.
            open(_p, "w").write("module C where\nopen import Some.Mod using (a; n; b)\ny = a\n")
            _ADDED[("C.agda", "n")] = "Some.Mod"
            check("a merged `using (…)` loses only the ambiguous name",
                  fix_ambiguous(_err), 1)
            check("...and keeps its siblings",
                  open(_p).read(),
                  "module C where\nopen import Some.Mod using (a; b)\ny = a\n")
        finally:
            os.chdir(_cwd)
            _ADDED.clear()

    return check.report()


# ⚑ THE DISPATCH IS WHAT MAKES THE SUITE RUNNABLE, and a module that DEFINES `_selftest`
# without one is scored as a FAILING suite by the runner (it looks for the `selftest: N/M`
# line and finds usage text). `rewire_to_leaves` shipped exactly that shape — a `--selftest`
# flag wired to a function that did not exist — so this is the inverse defect, guarded by
# being written at the same time as the function.
# selftest-tenant: sandbox
# ⚑ ⟡tenant-mandatory — reaches a store via `scope_store→store`, so `store.tenant` would exit
# 2 on an unstated tenant. SANDBOX: this tool REWRITES AGDA SOURCE from what the store tells
# it, and a suite that read the live corpus to rehearse a rewrite is the wrong-tenant failure
# with the worst possible blast radius.
# ⚑⚑ THIS SUITE WAS INVISIBLE TO THE CENSUS UNTIL 2026-08-24 and the reason is worth keeping:
# `scope_store` imported `store` INSIDE a function, so import-closure reach stopped one hop
# short and this file — plus `drop_dead_renames` and `rewire_to_leaves` behind it — read as
# reaching no store at all. Hoisting that one import surfaced three suites at once. A
# deferred import does not merely hide its own module; it truncates every chain THROUGH it.
if __name__ == "__main__":
    # THE module's single entry point. Placed at the END so it can see every definition —
    # see the note where the old mid-file block used to be.
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    # ⚑ THE TOOL ANCHORS ITSELF INSTEAD OF DEMANDING A CWD.  Its docstring said "Run
    # from agda/" and five `os.getcwd()` sites plus a relative MEMBUDGET made that a
    # hard precondition — but this repo's no-chaining hook REFUSES `cd agda && tool`,
    # and the Bash tool's cwd does not persist across calls, so the documented
    # invocation was not expressible in one approved command.  A usage note that
    # cannot be followed is a capability bound, not documentation.
    #
    # ⚑ IDEMPOTENT AND NON-SURPRISING: it chdirs ONLY when the cwd is not already the
    # agda root, and paths given on the command line are re-anchored relative to it, so
    # both `scope_fix Substrate/Foo.agda` (from agda/) and
    # `scope_fix agda/Substrate/Foo.agda` (from the repo root) name the same file.
    _agda = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "agda")
    _prior = os.getcwd()
    if os.path.isdir(_agda) and os.path.realpath(_prior) != os.path.realpath(_agda):
        os.chdir(_agda)
    skip = set()
    for flag in ("--max", "--seed"):
        if flag in sys.argv: skip.add(sys.argv.index(flag) + 1)
    args = [a for i, a in enumerate(sys.argv[1:], 1)
            if not a.startswith("--") and i not in skip]
    # re-anchor caller-relative paths against the cwd they were written against
    args = [a if os.path.exists(a)
            else (os.path.relpath(os.path.join(_prior, a), _agda)
                  if os.path.exists(os.path.join(_prior, a)) else a)
            for a in args]
    # ⚑ BEFORE THE BRANCH, NOT INSIDE THE WRITE ARM.  The old `_es.guard` call was
    # correct where it fired but sat under `if not dry and args` — the placement
    # `ratchet.mutating_argv` measures as unable to observe the unstated case at all
    # ("a guard reached only after `apply` is true can never observe the case where
    # apply was never chosen").  Demanding the statement here fixes that.
    #
    # ⚑⚑⚑ AND THE SNAPSHOT RIDES THE STATEMENT, WHICH IS THE OTHER HALF (operator,
    # 2026-08-25: *"it needs to be triggered at the same place as the gate for live vs
    # dry, else it will get missed downstream for the same reason the gate was"*).
    # `require_explicit_mutation` here plus `guard` at the write made this file the LAST
    # `SPLIT` row in `pycodemod --unbound-snapshot` — the shape that reads COMPLIANT to
    # `check_snapshot_guard.intent_census` (the contract is named) while a run that finds
    # nothing to change never reaches the snapshot.  `require_at_entry` is the ONE call
    # that does both: it delegates to `require_explicit_mutation`, and on a stated
    # `--apply` it delegates to `guard` in the same act.  Two calls could drift apart
    # again; one cannot.
    #
    # ⚑ `paths=args` IS LOAD-BEARING, NOT DECORATION.  `snapshot()` is whole-worktree for
    # TRACKED content, but `_copy_untracked(paths)` is the ONLY mechanism that reaches
    # untracked files — and this tree currently carries 40+ untracked Agda leaves from an
    # in-flight split, exactly the population a bad run would destroy irrecoverably.
    # Without `paths=` the census reports `entry-nopaths` rather than `entry`, which is a
    # narrower gap than SPLIT but still a real one.
    import os as _o2, sys as _s2
    _s2.path.insert(0, _o2.path.dirname(_o2.path.abspath(__file__)))
    import edit_snapshot as _es0
    _es0.require_at_entry("scope_fix", paths=args)
    dry = "--dry-run" in sys.argv
    # ⚑⚑ ⟡scope-source-write-codec — ARM THE BYTE-LEVEL SEAM'S OWN REFUSAL.
    # `scope_source._write` now routes through `vfs.write`, whose `_declare` RAISES
    # when `vfs.DRY_RUN` is set rather than silently skipping.  `--dry-run` means NO
    # BYTE OF THE WORKING TREE DIFFERS AFTERWARD — a statement about the FILESYSTEM,
    # not about this tool's internal passes — so arming it here is exactly that promise
    # made enforceable one layer down.
    #
    # ⚑ SAFE **HERE** BECAUSE `fix()` THREADS `dry` DOWN, and that was verified rather
    # than assumed: `pycodemod --guarded _write --root scratch` puts every `scope_*`
    # call site behind `if not dry` or an earlier `if dry: return True`.  A tool with
    # the WRITE-THEN-RESTORE shape (`prune_leaf_opens` writes and restores even on the
    # dry path) must NOT do this — it would have to set `vfs.DRY_RUN = False`
    # deliberately.  So this line is a claim about scope_fix's control flow, and it is
    # a TRIPWIRE rather than a suppressor: it can only fire if a future handler forgets
    # its guard, which is the one failure a preview flag exists to prevent.
    import vfs as _vfs0
    _vfs0.DRY_RUN = dry
    mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 40
    sd = {}
    if "--seed" in sys.argv:
        for sfile in sys.argv[sys.argv.index("--seed") + 1].split(","):
            sd.update(seed_map(sfile))
        print(f"seed: {len(sd)} name(s) from the stripped conduit(s)")
    # ⚑ THE SNAPSHOT USED TO BE TAKEN HERE, under `if not dry and args`, with the comment
    # *"costs nothing on the dry path, which is why it is guarded on `dry`"*.  That
    # reasoning is SOUND about cost and WRONG about placement, and keeping the residue is
    # the point: the condition it was guarded on is the same condition the intent gate is
    # about, so the two guards could disagree — and `--unbound-snapshot` measured exactly
    # that disagreement on this file.  `require_at_entry` above now takes the snapshot on
    # a stated `--apply` and skips it on a stated `--dry-run`, which preserves the cost
    # argument verbatim while removing the second placement that could rot.
    ok = all(fix(t, mx, dry, sd) for t in args)
    sys.exit(0 if ok else 1)
