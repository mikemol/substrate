#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""reparameterize_record.py — MECHANICAL patch synthesis for the set1-carrier-always-parameterize
move on record INSTANCES: given a record's short name + its carrier field names (in the new param
order), rewrite every `X : Record …` / `X = record { <carrier fields> ; <law fields> }` instance to
`X : Record <carrier values…>` / `record { <law fields> }` — dropping the carrier field-lines and
lifting their VALUES into the type's argument position. Brace/paren-aware (robust to field layout).

Handles the regular BULK (the instances that only construct the record); the record def itself and
projection-consumers (functions that .project the moved fields) are bespoke, done by hand.

⟡tele-positional: ALSO rewrites POSITIONAL-constructor instances `X = Ctor a0 a1 … a(n-1)` (a telescope
migration's value-record instances, e.g. DescentTree/HappyFamily's `mkDescentTree`). Pass `--recdef=<path>`
naming the file that DEFINES the record: the tool parses it via record_def_edit, COMPUTES the moved-field
POSITIONS from `codomain_is_set` (NEVER hardcoded), derives the constructor + carrier names, and lifts the
args at those positions into the type-sig while the ctor keeps the rest.

Usage:  reparameterize_record.py CommutativeMonoid R,_+R_,0R  file1.agda file2.agda …   [--apply]
        reparameterize_record.py DescentTree --recdef=<Tree.agda>  <AsTree.agda> …      [--apply]
        (default = DRY RUN: prints a unified diff per instance; --apply writes in place)
"""
import sys, re, difflib, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# the shared brace/depth-aware Agda-text kit (∩, single-sourced in telescope_text — no longer defined here).
from telescope_text import _match_brace, _split_top, _parse_field, _arg, _strip_comment

_SNAPPED = []


def _snapshot_once(path):
    """Arm edit_snapshot on the FIRST write of a run; a no-op thereafter.

    ⚑ This tool rewrites files it read — the shape that made 33 files
    unrecoverable (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop,
    so a per-file `guard` would arm only the first file AND shell out to `git
    stash create` on every iteration; arming once per run is both correct and
    cheap.  Recovery is per-file and MANUAL by design — edit_snapshot never
    restores anything itself.
    """
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        edit_snapshot.guard('reparameterize_record', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



# CLI-set config (populated in __main__ / by a caller before `transform`). `transform` reads them as globals.
REC = None
CARRIERS = []
CTOR = None            # positional-ctor mode: the record's constructor (None ⇒ only the `= record` branch)
MOVED_POS = []         # positions (COMPUTED via record_def_edit.codomain_is_set) whose args → the sig
_fields = []


def _rewrite_sig(out, name, args_str):
    """APPEND `args_str` to the RETURN-type `REC …` application in `name`'s type signature. The sig may be
    MULTI-LINE (continuation lines indented past the `name :` line) and may mention REC in BINDERS before the
    return type — so the rewrite targets the LAST line of the sig block that applies REC, appending at its end
    (record_def_edit appends moved params AFTER the orig params, so append is always the right arity move for
    records with pre-existing params; the old replace-to-EOL semantics truncated `tee : … (b : Brick T) → … →
    Brick (t T O)` at the binder and dropped `SylowDecomposition G _·_ ε 2`'s existing args). The single home
    for the sig-rewrite — the `= record{}` and positional-ctor branches both route through here."""
    lines = out.split("\n")
    # `name : …` on one line, OR the name ALONE on its line with the `: …` on the indented next line
    # (the round-robin-merger style — the old `name\s*:` matcher silently no-opped on it)
    sig_start = re.compile(r"^(\s*)" + re.escape(name) + r"\s*(?::|$)")
    for i, ln in enumerate(lines):
        m = sig_start.match(ln)
        if not m:
            continue
        base_indent = len(m.group(1))
        # sig block = this line + continuation lines (more-indented, non-blank)
        j = i + 1
        while j < len(lines) and lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) > base_indent:
            j += 1
        rec_re = re.compile(agda_lex.word(REC).pattern)
        last = max((k for k in range(i, j) if rec_re.search(lines[k])), default=None)
        if last is None:
            return out                                   # sig exists but never applies REC — leave it
        lines[last] = lines[last].rstrip() + f" {args_str}"
        return "\n".join(lines)
    return out


def _mask_comments(s):
    """blank `--`-to-EOL with SPACES (length-preserving): depth-0 splits and value-parses run on the masked
    text (a `;` or bracket INSIDE a comment can no longer corrupt them), while original offsets stay valid so
    the rebuild keeps the ORIGINAL segments — kept fields' inline comments survive verbatim."""
    out = []
    for l in s.split("\n"):
        m = re.search(r"(?:^|\s)--", l)
        out.append(l[:m.start()] + " " * (len(l) - m.start()) if m else l)
    return "\n".join(out)


def _block_end(src, pos):
    """A ctor application spans from `pos` (just after the ctor token) to the def-end: the first
    following line that is col-0 non-blank (a new top-level def) OR blank. Return that exclusive end."""
    nl = src.find("\n", pos)
    if nl < 0:
        return len(src)
    end = nl                                    # end of the ctor line (its remainder may hold args)
    while True:
        ls = end + 1
        if ls >= len(src):
            break
        nl2 = src.find("\n", ls)
        line = src[ls:] if nl2 < 0 else src[ls:nl2]
        if re.match(r"\S", line) or line.strip() == "":
            break                               # col-0 non-blank OR blank ⇒ block ended
        end = len(src) if nl2 < 0 else nl2      # indented continuation ⇒ absorb this line
        if nl2 < 0:
            break
    return end


def transform(src):
    """Rewrite every Record instance in src; return (new_src, n_instances)."""
    n = 0
    out = src
    # iterate over `<name> = record {…}` blocks
    for m in list(re.finditer(r"(?m)^(\s*)([^\s:=][^\n=]*?)\s*=\s*record\b", src)):
        name = m.group(2).strip().split()[0]      # base def name (drop LHS params, e.g. `foo m`)
        rb = src.find("{", m.end() - 1)
        if rb < 0:
            continue
        re_ = _match_brace(src, rb)
        if re_ < 0:
            continue
        body = src[rb + 1:re_]
        masked = _mask_comments(body)             # parse/split on the mask; rebuild from the original
        msegs = _split_top(masked, ";")
        osegs, pos = [], 0                        # original segments at the SAME depth-0 boundaries
        for s_ in msegs:
            osegs.append(body[pos:pos + len(s_)]); pos += len(s_) + 1
        parsed = [_parse_field(s_) for s_ in msegs]
        fnames = [fn for fn, _ in parsed if fn]
        if not all(c in fnames for c in CARRIERS):
            continue                              # not an instance of THIS record
        vals = {fn: " ".join((fv or "").split()) for fn, fv in parsed}   # comment-free, ws-normalized
        carrier_args = " ".join(_arg(vals[c]) for c in CARRIERS)
        # rebuild the record body with ONLY the non-carrier (law) fields — ORIGINAL text, comments intact
        keep = [o for o, (fn, _) in zip(osegs, parsed) if fn not in CARRIERS]
        new_body = ";".join(keep)
        new_record = src[m.start():rb] + "{" + new_body + "}"
        out = _rewrite_sig(out, name, carrier_args)     # lift the carrier VALUES into the type sig
        out = out.replace(src[m.start():re_ + 1], new_record, 1)
        n += 1

    # ── POSITIONAL-CONSTRUCTOR branch (⟡tele-positional) — runs AFTER the `= record` finder so it
    #    never double-matches (a `= record` block is not a `= Ctor` application). ──
    if CTOR:
        # LHS may carry clause params (`name arg = mkCtor …`) — group(2) is the def NAME, group(3) the params
        ctor_re = re.compile(r"(?m)^(\s*)(\S+)((?:[ \t]+\S+)*)\s*=\s*" + re.escape(CTOR) + r"\b")
        for m in list(ctor_re.finditer(src)):
            indent, name, lhs_args = m.group(1), m.group(2), m.group(3)
            end = _block_end(src, m.end())              # exclusive end of the ctor-application block
            block = src[m.end():end]                    # the args span (may start mid-line, then continue)
            flat = " ".join(_strip_comment(l) for l in block.split("\n"))
            args = [a for a in (x.strip() for x in _split_top(flat, " ")) if a]
            if len(args) != len(_fields):
                print(f"# SKIP {name}: {len(args)} args ≠ {len(_fields)} fields — not a plain "
                      f"{CTOR} application (partial/where/named-arg?)", file=sys.stderr)
                continue
            moved = [_arg(args[p]) for p in MOVED_POS]
            kept = [args[i] for i in range(len(args)) if i not in set(MOVED_POS)]
            out = _rewrite_sig(out, name, " ".join(moved))   # same sig-rewrite as the record branch
            new_inst = f"{indent}{name}{lhs_args} = {CTOR} {' '.join(kept)}"
            out = out.replace(src[m.start():end], new_inst, 1)
            n += 1
    return out, n


if __name__ == "__main__":
    _args = sys.argv[1:]
    APPLY = "--apply" in _args
    RECDEF = next((a.split("=", 1)[1] for a in _args if a.startswith("--recdef=")), None)
    _pos = [a for a in _args if not a.startswith("--")]
    REC = _pos[0]
    if RECDEF:
        from record_def_edit import parse_record_def, codomain_is_set
        _orig, _fields, _lvl, CTOR = parse_record_def(open(RECDEF).read(), REC)
        MOVED_POS = [i for i, (fn, ft) in enumerate(_fields) if codomain_is_set(ft)]
        CARRIERS = [fn for fn, ft in _fields if codomain_is_set(ft)]   # derived, single-source
        FILES = _pos[1:]
    else:
        CARRIERS = _pos[1].split(",")                                  # in NEW param order, e.g. R,_+R_,0R
        FILES = _pos[2:]

    # ⚑ ONE ACT: state the intent AND snapshot, at the earliest point `FILES` is
    # known — which is HERE and not at the top of `__main__`, because the target
    # list is positional-slice-dependent on `--recdef=` (`_pos[1:]` vs `_pos[2:]`).
    # Gating one line earlier would state intent correctly and snapshot a set that
    # includes the CARRIERS spec as if it were a path: a false assurance.
    # ⚑ `_snapshot_once` sits under `if APPLY:` in the loop — after the decision,
    # and unreached on a run where every file transforms to itself.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("reparameterize_record", paths=FILES)
    for path in FILES:
        src = open(path).read()
        new, n = transform(src)
        if n == 0 or new == src:
            continue
        if APPLY:
            _snapshot_once(path)
            open(path, "w").write(new)
            print(f"# APPLIED {path} — {n} instance(s)")
        else:
            diff = difflib.unified_diff(src.splitlines(True), new.splitlines(True),
                                        fromfile=path, tofile=path + " (reparameterized)")
            sys.stdout.writelines(diff)
            print(f"# ^ {path}: {n} instance(s)\n")
