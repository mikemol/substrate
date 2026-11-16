#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""lift_pyhelper.py — MECHANICAL rung-0 lift: route every IDENTICAL copy of a top-level helper through a
single-source home. Identity is decided by the WEDGE EQUIVALENCE ITSELF (jea_pysim support = alpha-quotiented
canonical structure) — NOT a hand-rolled string/ast compare (which would miss that two copies alpha-rename
their locals). It interns the home + the target files in ONE Corpus, and removes a copy ONLY when its support
== the home canonical's support (a drifted copy is left + reported), inserting `from <home> import <canonicals>`
(+ an `<alias> = <canonical>` compat line where the local name differed, killing the name-distinction).

Recursive-to-fixpoint: after --apply, re-run scratch/scripts_dedup.py; the next rung's families appear as the
lifted leaves stop masking them. Lift, re-intern, repeat until no cross-file IDENTICAL family remains.

Usage:  lift_pyhelper.py --home _agdatext --fn strip --fn split_arrows:sa  scripts/*.py   [--apply]
"""
import sys, os, re, argparse, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
import jea_pysim as P

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
        edit_snapshot.guard('lift_pyhelper', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")




def def_block(lines, i):
    """lines[i] is `def name(…`; return exclusive end = after the last indented body line (keeps trailing blanks)."""
    j, last = i + 1, i
    while j < len(lines):
        ln = lines[j]
        if ln.strip() == "":
            j += 1; continue
        if ln[:1] in " \t":
            last = j; j += 1; continue
        break
    return last + 1


def route_file(path, removals, home):
    """removals: list of (local_name, canonical). Remove each top-level `def local(` block; insert the import
    + alias compat lines. Returns new_src (or None if nothing changed)."""
    lines = open(path).read().split("\n")
    want = {loc: can for loc, can in removals}
    out, i, removed, aliases = [], 0, set(), []
    while i < len(lines):
        m = re.match(r"def\s+(\w+)\s*\(", lines[i])
        if m and m.group(1) in want and not lines[i][:1].isspace():
            local = m.group(1); canon = want[local]
            end = def_block(lines, i)
            removed.add(canon)
            if local != canon:
                aliases.append(f"{local} = {canon}")
            if end < len(lines) and lines[end].strip() == "":
                end += 1                                   # eat one trailing blank
            i = end; continue
        out.append(lines[i]); i += 1
    if not removed:
        return None
    imp = f"from {home} import " + ", ".join(sorted(removed))
    # insert after the FIRST top-of-file import (always before module-level logic that may USE the helper —
    # a later mid-file `import sys` must NOT be the anchor, or the helper import lands after its use).
    first_imp = next((k for k, l in enumerate(out) if re.match(r"(import|from)\s", l)), 0)
    out[first_imp + 1:first_imp + 1] = [imp] + aliases
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", required=True)
    ap.add_argument("--fn", action="append", required=True, help="NAME[:ALIAS…]")
    ap.add_argument("--apply", action="store_true")
    # ⚑ DECLARED SO THE CONTRACT'S OTHER HALF IS SAYABLE.  The gate below reads
    # argv for `--dry-run`; without this, argparse would reject the very flag the
    # refusal message tells the caller to pass — a tool that demands a statement it
    # cannot parse.  It is unused in the body: `not a.apply` is already the dry
    # path, so this makes the existing default STATABLE rather than adding a mode.
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()

    fn_map, canons = {}, []
    for spec in a.fn:
        names = spec.split(":"); fn_map.update({nm: names[0] for nm in names}); canons.append(names[0])
    home_path = os.path.join(ROOT, "scripts", a.home + ".py")
    files = [f if os.path.isabs(f) else os.path.join(ROOT, f) for f in a.files]
    files = [f for f in files if os.path.abspath(f) != os.path.abspath(home_path)]
    # ⚑ ONE ACT: state the intent AND snapshot, at the earliest point the TARGET
    # SET is known.  `_snapshot_once` sits under `if a.apply:` inside the write
    # loop — after the decision, and unreached by a run where every candidate
    # DRIFTS (support ≠ canonical) and nothing is rewritten.
    # ⚑ IT IS PLACED AFTER `files` RESOLVES, NOT AT THE TOP OF `main`, because the
    # snapshot needs the ABSOLUTE, home-excluded list; gating one line earlier
    # would state the intent correctly and snapshot the wrong (or a relative) set,
    # which is the false-assurance half of the same defect.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    # ⚑ NO `intent=` HERE, DELIBERATELY.  Forwarding `"apply" if a.apply else
    # "dry-run"` would read as compliance and be the OPPOSITE of it: `--apply` is a
    # bare store_true with no `--dry-run` beside it, so an unstated run parses as
    # False and would be laundered into a STATED dry-run. That is the silent
    # default the contract exists to refuse, wearing the contract's own vocabulary.
    # Letting the gate read argv makes an unstated run refuse, which is the point.
    _es.require_at_entry("lift_pyhelper", paths=files)

    # ONE Corpus (the wedge interner): home + targets, so support ids align and support-equality = identity.
    C = P.Corpus()
    C.add_file(home_path)
    for f in files:
        try:
            C.add_file(f)
        except Exception as e:
            print(f"# skip {f}: {e}", file=sys.stderr)
    canon_sup = {}                                          # canonical name -> its support (from the home)
    for u in C.units:
        if os.path.abspath(u.path) == os.path.abspath(home_path) and u.name in canons:
            canon_sup[u.name] = frozenset(u.support)
    missing = [c for c in canons if c not in canon_sup]
    if missing:
        sys.exit(f"lift_pyhelper: canonical not found / unparsed in {a.home}: {missing}")

    per_file, drift = {}, []
    for u in C.units:
        if u.name not in fn_map:
            continue
        if os.path.abspath(u.path) == os.path.abspath(home_path):
            continue
        canon = fn_map[u.name]
        if frozenset(u.support) == canon_sup[canon]:       # THE WEDGE VERDICT: identical support ⇒ same def
            per_file.setdefault(u.path, []).append((u.name, canon))
        else:
            drift.append((os.path.relpath(u.path, ROOT), u.name))

    for f, rel in drift:
        print(f"# ⚠ DRIFT {f}: «{rel}» present but support ≠ canonical — left in place", file=sys.stderr)

    for path, removals in sorted(per_file.items()):
        src = open(path).read()
        new = route_file(path, removals, a.home)
        if not new or new == src:
            continue
        tag = "drop " + ", ".join(sorted({c for _, c in removals}))
        if a.apply:
            _snapshot_once(path)
            open(path, "w").write(new); print(f"# APPLIED {os.path.relpath(path, ROOT)} — {tag}")
        else:
            sys.stdout.writelines(difflib.unified_diff(src.splitlines(True), new.splitlines(True),
                                                        fromfile=os.path.relpath(path, ROOT), tofile="(lifted)"))
            print(f"# ^ {os.path.relpath(path, ROOT)}: {tag}\n")


if __name__ == "__main__":
    main()
