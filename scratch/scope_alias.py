#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_alias.py — the ALIAS / QUALIFIED-NAME repairs: a name reached THROUGH something.

⚑⚑ SPLIT OUT OF `scope_fix.py` 2026-08-11 (⟡split-1200). Six handlers, one class: every one of
them is about a name the consumer does not reach DIRECTLY — it reaches it through an alias
(`import M as Z₃`, then `Z₃.normalize`), through a conduit's re-export, or through a
parameterized module it forgot to apply. When the re-export goes, the indirection is what has
to be repaired, and the repair is never "restore the conduit".

    fix_arg_name_closure(n, p)  an APPLICATION ARGUMENT that is itself an unbound name
    fix_demand(n, p)            ⟡demand-first-resolver — bind where the ELABORATED demand says
    fix_alias_fanout(p)         one conduit alias becomes ONE ALIAS PER OWNER
    fix_qualified(n, p)         `F.++-assoc` — de-qualify onto the true owner
    fix_alias_split(p)          an alias whose module cannot serve it: bind each name at ITS owner
    fix_unapplied_import(p)     apply the arguments of an unapplied parameterized import

⚑ THE ORDER ABOVE IS A DEPENDENCE, NOT A LISTING. `fix_demand` calls `fix_arg_name_closure`
first — closing over a definition is cheaper and more certain than resolving an owner — and
`fix_qualified` falls through to `_repoint_alias` and `add_renaming_import` in `scope_edit`.
Every arrow inside this file points down the list; every arrow out of it points at
`scope_edit` / `scope_resolve` / `scope_source` / `scope_store`. Nothing here is read by them,
which is what makes this a leaf under `scope_fix` rather than a cut through the chain.

⚑ AND THE TWO ORACLES MUST NOT BE CONFUSED HERE OF ALL PLACES. `fix_demand` reads the INTERNED
CORES (pre-strip, elaborated) and `fix_qualified` reads the CURRENT TEXT (post-strip); the
catalog reports what a module defined BEFORE the `public` re-exports were removed, so it is a
false positive for exactly the names being repaired and the resolver then "writes an import
that binds nothing" (⟡pd-export-oracle). That is why `fix()` consults the demand FIRST and the
source heuristics after, and why both live here where the ordering is visible in one reading.
"""
import os as _o, sys as _s
import re

_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive
from scope_edit import _repoint_alias, _rename_owner, add_import, add_renaming_import
from scope_resolve import (
    _resolve_owner, owner_from_suggestion, shape_candidates,
)
from scope_source import (
    _alias_binding, _alias_names, _alias_target, _conduit_pair, _head_text, _is_file_module,
    _module_exports, _module_params, _module_text, _open_stmts, _owner_admissible,
    _suppliable, _write, application_args,
)
from scope_store import _DEMAND_CANDS, _demand_of, _module_defines, owner_by_catalog


def fix_arg_name_closure(name, path, dry=False):
    """An APPLICATION ARGUMENT that is an unbound NAME is closed over from the conduit that supplied it.

    Binding a name through a parameterized owner writes `open import M <args>`, and `<args>` may
    itself be a NAME the consumer does not have (`GroupFromCapability cap-Z₃`). That name is not
    importable — the conduit DEFINES it, as an application of an orbit:

        Z3-Coxeter-Group.agda:  import …Capabilities.CoxeterGroup.Witness as CoxeterGroupW
                                cap-Z₃ = CoxeterGroupW.cap 2

    So the consumer needs the DEFINITION, not an import — copied verbatim from the conduit the
    demand named. Both the capability (CoxeterGroup vs xFreeCyclic vs PhaseProjection) and the
    index come from that one statement, so nothing is inferred from the subscript and nothing is
    guessed: `Z3-x-FreeCyclic` yields `xFreeCyclicW.cap 2` and `Z3-Coxeter-Group` yields
    `CoxeterGroupW.cap 2` for the same spelling `cap-Z₃`.

    ⚑ The SPPF cannot answer this one: module APPLICATION ARGUMENTS are not recorded (the shim
    emits only `defCopy`), and the orbit modules postdate the last catalog build. The store names
    the CONDUIT; the conduit's own source names the argument. That is the honest division.
    """
    leaf = name.rsplit(".", 1)[-1]
    self_mod = module_path(path, "")
    src = open(path).read()
    if re.search(rf"^{re.escape(leaf)}\s*=", src, re.M):
        return False                                       # already defined locally
    _demand_of(self_mod)                                   # prime the candidate cache
    # every conduit this file's demand touches, plus any conduit it already applies by this name
    conduits = {c for cs in _DEMAND_CANDS.get(self_mod, {}).values() for *_r, c in cs}
    conduits |= {m for m in re.findall(r"(?:open\s+)?import\s+([\w.-]+)[^\n]*?(?<![\w.-])"
                                       + re.escape(leaf) + r"(?![\w-])", src)}
    for conduit in sorted(conduits):
        text = _module_text(conduit)[0] or _head_text(conduit)
        if not text:
            continue
        d = re.search(rf"^{re.escape(leaf)}\s*=\s*([^\n]+)$", text, re.M)
        if not d:
            continue
        rhs = d.group(1).strip()
        head = rhs.split(".", 1)[0].split()[0] if "." in rhs else ""
        imp = re.search(rf"^import\s+([\w.-]+)\s+as\s+{re.escape(head)}\s*$", text, re.M) if head else None
        # ⚑ CLOSE ONLY OVER A DEFINITION WE CAN ALSO SUPPLY. `cap-Z₃ = xFreeCyclicW.cap 2` is
        # closeable because its head is an ALIAS IMPORT we can copy alongside. A definition like
        # `ε = ε-in` is not: its right-hand side depends on the conduit's own scope, and copying it
        # manufactures a fresh unresolved name — the tool chasing a problem it just created.
        if not imp:
            continue
        if dry:
            return True
        # ⚑ the DEFINITION must land AFTER the alias import it uses. Anchoring every insertion at
        # the module header puts the second closure's def ABOVE the first's import, which is a
        # scope error the tool would then chase as a missing name of its own making.
        block, anchor = "", re.search(r"^module [^\n]*\bwhere\b[^\n]*\n", src, re.M)
        if not anchor:
            return False
        at = anchor.end()
        have = re.search(rf"^import\s+{re.escape(imp.group(1))}(?![\w.-])[^\n]*\n", src, re.M) \
            if imp else None
        if imp and not have:
            block += f"import {imp.group(1)} as {head}\n"
        elif have:
            at = max(at, have.end())               # sit below the existing alias import
        block += f"{leaf} = {rhs}\n"
        _write(path, src[:at] + block + src[at:])
        print(f"    {path}: {leaf} = {rhs}   [arg-name closure from {conduit.rsplit('.', 1)[-1]}]")
        return True
    return False


def fix_demand(name, path, dry=False):
    """⟡demand-first-resolver — bind `name` where the elaborated demand says, canonically.

    When the demand records a CANONICAL spelling different from the use site's (the site wrote a
    conduit's rename target), the use site is rewritten onto the canonical name: binding the
    conduit spelling would re-import the conduit at the NAME grade, which is the blast radius the
    no-conduit policy exists to remove.
    """
    if not path.endswith(".agda"):
        return False
    if fix_arg_name_closure(name, path, dry):
        return True
    self_mod = module_path(path, "")
    leaf = name.rsplit(".", 1)[-1]
    demand = _demand_of(self_mod)
    hit = demand.get(leaf)
    if not hit:
        return False
    owner, canon = hit
    cands = _DEMAND_CANDS.get(self_mod, {}).get(leaf, [])
    demand_args = cands[0][2] if len(cands) == 1 else ""

    # ⚑ SELECT THE DEMAND CANDIDATE BY ITS CONDUIT — the carrier the SPPF recorded. A use site
    # `Z₃.normalize` names the alias `Z₃`; that alias targets `Z3-Coxeter`; the demand holds
    # `Z3-Coxeter._.normalize`. Matching those two is a DERIVATION from the elaborated reference,
    # not a text search: the ref path already says which carrier, at which index.
    if "." in name:
        target = _alias_target(path, name.rsplit(".", 1)[0])
        pick = next((c for c in cands if c[3] == target), None) if target else None
        if pick:
            owner, canon, demand_args = pick[0], pick[1], pick[2]
        elif target:
            o, sname, a = _alias_binding(target, leaf)
            if o and _owner_admissible(o, path):
                owner, canon, demand_args = o, sname, a
    elif len(cands) > 1:
        # unqualified AND genuinely ambiguous (two applications / two definers). Guessing here is
        # exactly the silent-miscompile class: it compiles green and means the other carrier.
        print(f"    ! {path}: {name} AMBIGUOUS in the demand "
              f"({'; '.join(f'{cd}::{o}{(chr(32) + a) if a else str()}' for o, _c, a, cd in cands)})"
              f" — qualify the use site; refusing to pick")
        return False

    if owner == self_mod or not _owner_admissible(owner, path):
        return False

    def _args_for(o, prefer=""):
        if not _module_params(o):
            return ""
        # the alias-derived index wins over any application already in the file: a two-carrier
        # file HAS the other index in scope, and `application_args` would hand it back.
        a = prefer or application_args(o, path)
        if not a:
            _o2, _s2, a = _alias_binding(self_mod, canon)
        return a

    args = _args_for(owner, demand_args)
    if (_module_params(owner) and not args) or not _module_exports(owner, canon):
        # the demand names a definition inside a LOCAL module, or one whose own telescope the
        # consumer cannot apply (`ListPresentation.normalize`). It is importable at whichever
        # module ALREADY IN THIS FILE'S DEMAND re-exports it applied (`Cyclic.Existential n`) —
        # a re-host among names already required, not a tree-wide guess.
        host = next(((o2, _args_for(o2)) for o2, _c in set(_demand_of(self_mod).values())
                     if o2 != owner and _module_exports(o2, canon)
                     and not (_module_params(o2) and not _args_for(o2))), None)
        if not host:
            return False
        owner, args = host
    src = open(path).read()
    surface = name.rsplit(".", 1)[-1]
    new = src
    if "." in name:
        # ⚑ DE-QUALIFYING IS SAFE ONLY AT ONE CARRIER. `Z₃.Canonical → Canonical-ex` is a merge:
        # if the file ALSO needs Z₂'s `Canonical-ex`, one bare name now serves two carriers and the
        # file typechecks meaning the wrong thing for one of them. When the demand names more than
        # one concrete carrier for this leaf, the QUALIFIER IS THE ONLY THING KEEPING THEM APART —
        # refuse, and leave it to the alias fan-out, which repoints each alias to its own owner.
        if len({(o, a) for o, _c, a, _p in cands if a}) > 1:
            print(f"    ! {path}: {name} — {len(cands)} carriers demanded; NOT de-qualifying "
                  f"(the qualifier is the carrier distinction). Deferring to alias fan-out.")
            return False
        new = re.sub(rf"(?<![\w.-]){re.escape(name.rsplit('.', 1)[0])}\."
                     rf"{re.escape(surface)}(?![\w])", canon, new)
    elif canon != surface:
        new = re.sub(rf"(?<![\w.-]){re.escape(surface)}(?![\w-])", canon, new)
    if dry:
        return True
    if new != src:
        _write(path, new)
    ok, how = add_import(path, owner, canon, dry, args_hint=args)
    print(f"    {path}: {name} → {canon} @ {owner}{' ' + args if args else ''}   [demand; {how}]")
    # ⚑ `already imported` is a SUCCESS for this name: the canonical binding is present and the
    # use site has just been rewritten onto it. Reporting it as failure sent the name back down
    # the heuristic chain, which then declared `no owner found` for a name already resolved.
    return ok or how == "already imported" or new != src


def fix_alias_fanout(path, dry=False):
    """⚑ T21 ⟡pd-alias-fanout — one conduit alias becomes ONE ALIAS PER OWNER.

    Under the no-re-export policy a conduit module stops serving the names it used to forward, so
    an alias standing for it can no longer be repointed anywhere: no single module serves
    `Gen` AND `normalize` any more (they are `Cyclic.Base n` and `Cyclic.Existential n`). And the
    alias cannot simply be dropped either — `act-letter : Word Z₂.Gen → Word Z₃.Gen` keeps two
    carriers apart BY the qualification, so de-qualifying collides.

    The move both constraints leave is to fan the alias out: one alias per owning module, each
    APPLIED at the index the conduit used, with every use rewritten to its owner's alias (and to
    the owner's own spelling when the conduit reached it through a rename).
    """
    try:
        src = open(path).read()
    except OSError:
        return False
    self_mod = module_path(path, "")
    for m in list(re.finditer(
            r"^(?:open\s+)?import\s+([\w.-]+)([^\n]*?)\s+as\s+([^\s;]+)[^\n]*\n", src, re.M)):
        target, targs, alias = m.group(1), m.group(2).strip(), m.group(3)
        if not target.startswith("Substrate"):
            continue
        names = [n for n in _alias_names(src, alias) if n]
        if not names or all(_module_exports(target, n) for n in names):
            continue
        groups, ok = {}, True
        for n in names:
            if _module_exports(target, n):
                groups.setdefault((target, targs), []).append((n, n))
                continue
            o, s, a = _alias_binding(target, n)
            if not (o and o != self_mod and _owner_admissible(o, path)
                    and _module_exports(o, s)):
                ok = False
                break
            groups.setdefault((o, a), []).append((n, s))
        if not ok or not groups:
            continue
        taken = set(re.findall(r"^(?:open\s+)?import\s+[\w.-]+[^\n]*?\s+as\s+([^\s;]+)", src, re.M))
        lines, subs = [], []
        for (o, a), pairs in groups.items():
            na = alias if (o, a) == (target, targs) else f"{alias}-{o.rsplit('.', 1)[-1]}"
            k = na
            while k in taken and (o, a) != (target, targs):
                k += "′"
            taken.add(k)
            lines.append(f"import {o}{' ' + a if a else ''} as {k}\n")
            for n, s in pairs:
                if (k, s) != (alias, n):
                    subs.append((n, k, s))
        new = src[:m.start()] + "".join(lines) + src[m.end():]
        for n, k, s in sorted(subs, key=lambda t: -len(t[0])):
            new = re.sub(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(n)}(?![\w])", f"{k}.{s}", new)
        if new == src:
            continue
        if not dry:
            _write(path, new)
        print(f"    {path}: alias {alias} fanned out → "
              f"{', '.join(sorted(o.rsplit('.', 1)[-1] + (' ' + a if a else '') for o, a in groups))}")
        return True
    return False


def fix_qualified(name, path, dry=False, sugg=None, alias_owner=None):
    """`F.++-assoc` — an ALIAS-qualified name whose alias-module lost its re-export.

    The consumer reached a lemma through an INSTANCE-module conduit (`import …FreeCyclic-Coxeter
    as F`), but the lemma is generic and lives elsewhere (`Coxeter.Word.++-assoc`, `{Gen : Set}`).
    The paydown is to bind it at the OWNER and DROP the qualification — not to restore the alias
    module's re-export. If the owner is already imported (it usually is), no import is even needed.
    """
    if "." not in name:
        return False
    alias, leaf = name.rsplit(".", 1)
    # ⚑ THE COMPILER NAMES THE OWNER — `did you mean 'Substrate.Groups.Coxeter.Word.Word'?`.
    # That beats any ranking we can compute, so consult the suggestion FIRST and fall back to
    # the catalog only when Agda offered none ("`[NotInScope]` IS THE INSTRUMENT").
    owner = spell = None
    # ⚑ T19 ⟡pd-alias-binding. The alias module's OWN statement that binds `leaf` is the record of
    # which `leaf` it meant — authoritative over any export search, which cannot tell two
    # same-named things apart (`Base.Canonical : Fin (suc n) → Set` vs the `Canonical-ex : Word
    # Gen → Set` that Z2-Coxeter renames to `Canonical`). Consult it FIRST; when it names a
    # rename, re-issue the rename at that owner rather than de-qualifying onto a homonym.
    ab_owner, ab_src, ab_args = _alias_binding(_alias_target(path, alias) or "", leaf)
    # ⚑ T20 ⟡pd-alias-applied-repoint. When the file keeps SEVERAL carriers apart by alias
    # (`Z₂.Gen` and `Z₃.Gen` in one module), de-qualifying collides and every candidate owner is
    # the SAME module — they differ only in its ARGUMENT (`Cyclic.Base 1` vs `Cyclic.Base 2`).
    # The alias module's own binding statement carries that argument; repoint the alias to the
    # APPLIED owner and keep the qualification.
    if ab_owner and ab_args and len({m for _k, m, _l in shape_candidates(leaf, path)}) > 1:
        if _repoint_alias(path, alias, ab_owner, dry, args=ab_args):
            return True
    if ab_owner and _owner_admissible(ab_owner, path) and _suppliable(ab_owner, path):
        if ab_src != leaf:
            src = open(path).read()
            if not re.search(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(leaf)}(?![\w])", src):
                return False
            if dry:
                return True
            _write(path, re.sub(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(leaf)}(?![\w])",
                                leaf, src))
            ok, how = add_renaming_import(path, ab_owner, ab_src, leaf, dry)
            print(f"    {path}: {name} → {leaf} @ {ab_owner} renaming ({ab_src} to {leaf})"
                  f"   [{how}]")
            return ok
        owner, spell = ab_owner, leaf
    # ⚑ SAME ALIAS ⇒ SAME OWNER. If a sibling name from this same alias already resolved
    # (F._++_, F.++-assoc → Coxeter.Word), F.Word belongs there too. Without this the
    # already-imported-module preference can pick a DIFFERENT module that happens to export
    # the leaf (Coxeter.DirectProduct.Word) → [UnequalTerms]. Alias cohesion beats proximity.
    if alias_owner and alias in alias_owner:
        cand = alias_owner[alias]
        for q in (leaf, f"_{leaf}_"):
            if _is_file_module(cand) and _module_defines(cand, q):
                owner, spell = cand, q
                break
    if not owner and sugg:
        owner, spell = owner_from_suggestion(leaf, sugg)
    # ⚑ the conduit chain (this file's own import edges) before the tree-wide catalog rank —
    # otherwise a `Z₂.Gen` is de-qualified onto `V4-Coxeter`, which exports a `Gen` but is not
    # the instance the file is built on.
    if not owner:
        owner, spell = _conduit_pair(leaf, path)
    if not owner:
        owner, spell = owner_by_catalog(leaf, path)
    if not owner:
        # ⚑ T18 ⟡pd-renaming-target, qualified form. `Z₃-Fin.action-of-a-is-σ₃` is the alias
        # module's own RENAME of `action-of-a-is-σ-ex`; the target is a qname nowhere, so every
        # ranking above is blind to it. Re-issue the rename at the definer and de-qualify.
        ro, rsrc, rargs = _rename_owner(leaf, path)
        if not ro:
            return False
        src = open(path).read()
        if not re.search(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(leaf)}(?![\w])", src):
            return False
        if dry:
            return True
        _write(path, re.sub(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(leaf)}(?![\w])", leaf, src))
        ok, how = add_renaming_import(path, ro, rsrc, leaf, dry, rargs)
        print(f"    {path}: {name} → {leaf} @ {ro} renaming ({rsrc} to {leaf})   [{how}]")
        return ok
    if not _suppliable(owner, path):
        return False
    src = open(path).read()
    if not re.search(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(leaf)}(?![\w])", src):
        return False
    # ⚑ T5 ⟡pd-no-dequalify-on-collision. The file may QUALIFY this name precisely because it
    # uses two different ones (V4-Embedding has S₄'s `_·_`/`ε` AND V₄'s, and disambiguated by
    # writing `V4.·`). De-qualifying then collides — and the collision only surfaces later, in a
    # line that mixes both. When the consumer's own pre-strip refs show several providers, keep
    # the qualification and REPOINT THE ALIAS instead.
    providers = {m for _k, m, _l in shape_candidates(leaf, path)}
    if len(providers) > 1:
        return _repoint_alias(path, alias, owner, dry)
    already = re.search(rf"^open import {re.escape(owner)}(?![\w.])", src, re.M)
    # ⚑ T5 ⟡pd-infix-use-site. An OPERATOR may be written INFIX (`x C.++ y`) or in ARGUMENT /
    # SECTION position (`(F._++_)`, `act = V4._·_`). The replacement is the use-site spelling
    # with the qualifier dropped — i.e. `leaf` VERBATIM, since `leaf` is exactly what the source
    # wrote after the dot. Deciding from the RESOLVED spelling instead turned `(F._++_)` into
    # `(++)` and `act = V4._·_` into `act = ·`, neither of which is in scope under any spelling;
    # the loop then re-proposed the already-present import every pass, forever.
    new = re.sub(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(leaf)}(?![\w])", leaf, src)
    if dry:
        return True
    _write(path, new)
    if not already:
        # single-source the insertion through add_import — it owns the module-header anchor
        # (⟡paydown-telescope-anchor); re-implementing it here is what corrupted 4 files.
        ok, _ = add_import(path, owner, spell)
        if not ok:
            return False
    if alias_owner is not None:
        alias_owner[alias] = owner
    print(f"    {path}: {name} → {spell} @ {owner}"
          f"   [{'already imported' if already else 'import added'}; qualification dropped]")
    return True


def fix_alias_split(path, dry=False):
    """De-qualify an alias whose module cannot serve it, binding each name at ITS owner.

    ⚑ T16. `import <M> as F` is unusable the moment M is parameterized and its arguments are
    not in scope — every `F.x` is then the module-as-function form. Repointing the alias to a
    single owner is only honest when ALL its names live there; when they do not, the fix is not
    a majority pick (that is the guessing this arc has been unwinding) but the mission's own
    rule: bind each name at its owner and retire the alias."""
    try:
        src = open(path).read()
    except OSError:
        return 0
    m = re.search(r"^(?:open )?import ([\w.-]+) as (\w+)(?![\w.-])[^\n]*\n", src, re.M)
    if not m:
        return 0
    mod, alias = m.group(1), m.group(2)
    if not _module_params(mod) or application_args(mod, path):
        return 0                                      # the alias is usable — nothing to repair
    names = sorted(_alias_names(src, alias))
    if not names:
        return 0
    owners = {}
    for n in names:
        o = _resolve_owner(n, path)
        if not o:
            print(f"    ! {path}: alias {alias} ({mod}) unusable, and `{n}` has no exporting owner")
            return 0                                  # all-or-nothing: never half-retire an alias
        owners[n] = o
    new = src[:m.start()] + src[m.end():]
    for n, o in owners.items():
        new = re.sub(rf"(?<![\w.-]){re.escape(alias)}\.{re.escape(n)}(?![\w])", n, new)
    if new == src:
        return 0
    if not dry:
        _write(path, new)
        for n, o in owners.items():
            add_import(path, o, n, dry)
    print(f"    {path}: alias {alias} ({mod.rsplit('.', 1)[-1]}) unsuppliable → bound "
          f"{len(names)} name(s) at {len(set(owners.values()))} owner(s)")
    return 1


def fix_unapplied_import(path, dry=False):
    """Apply the arguments of any UNAPPLIED import of a parameterized module. Returns #fixed.

    An `open import <M> using (…)` where M takes parameters binds the module-as-FUNCTION form,
    so a name comes out as `(A : Set) → Set` instead of a type. That is always wrong — there is
    no context in which the unapplied form is what a consumer meant — which makes this a repair
    the tool can run unconditionally rather than an error-specific handler. It heals statements
    an earlier pass wrote before T12 as well as anything a future pass writes."""
    try:
        src = open(path).read()
    except OSError:
        return 0
    # ⚑ A DEAD LINE THAT CRASHED THE WHOLE TOOL, AND ONLY ON THE PATH THAT REACHES IT.
    # This read `body, _ = module_path(_module_text(path, "")) if path.endswith(".agda")
    # else ("", 0)` — three defects in one statement: `_module_text` takes ONE argument
    # (`scope_source.py:367`, 11 call sites, this the only two-argument one),
    # `module_path` is the path→dotted-name authority and does not take source text,
    # and `body` was BOUND AND NEVER READ (`pycodemod --binding body` → 1 binding, 0
    # reads). So the statement computed nothing and raised `TypeError` on every `.agda`
    # target, making `scope_fix` — the mechanized ⟡public-paydown loop — unrunnable.
    #
    # ⚑ IT SURVIVED BECAUSE THE SELFTEST DOES NOT REACH IT.  `fix_unapplied_import` is
    # called unconditionally from `scope_fix.fix()` (`:317`), so the crash is on the
    # ONLY production path, yet `--selftest` passes: the suite exercises the resolvers
    # against the interned cores and never drives a file through `fix()`.  A gate that
    # cannot reach the entry point measures the library, not the tool.
    fixed = 0
    for sub, stmt in list(_open_stmts(src)):
        if not sub.startswith("Substrate") or not _module_params(sub):
            continue
        head = stmt.split("\n")[0]
        after = head[head.index(sub) + len(sub):]
        if re.split(r"\bas\b|\busing\b|\brenaming\b|\bhiding\b|\bpublic\b", after)[0].strip():
            continue                                  # already applied
        a = application_args(sub, path)
        if not a:
            continue
        new_head = head[:head.index(sub) + len(sub)] + " " + a + after
        new = src.replace(head, new_head, 1)
        if new == src:
            continue
        if not dry:
            _write(path, new)
        print(f"    {path}: applied `{sub} {a}` (was unapplied — module-as-function)")
        src, fixed = new, fixed + 1
    return fixed
