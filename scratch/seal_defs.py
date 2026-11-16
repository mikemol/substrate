#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Wrap named TOP-LEVEL definitions in an `opaque` block.

⟡cap64-stage, step (3) of cap_diagnose's recommendation: when a module is still
ELABORATION-BOUND after its own proofs are staged, the dense redex is UPSTREAM —
the consumer re-normalises the DEPENDENCY's equality chains every time it cites
them.  Sealing those chains at the definer turns each into a non-reducing
HANDLE, so every consumer composes handles instead.

⚑ SEAL AT THE EQUALITY-CHAIN BOUNDARY, never the neutral the proof is ABOUT.
This tool only wraps whole named definitions; choosing WHICH names is the
judgement it does not make.  An `_≡_`-valued lemma cited in `trans`/`cong`
chains is the safe class; an operator whose definitional unfolding a consumer
needs is not (sealing `_*Q_` failed with a scope error, not a smaller peak).

A definition's block runs from its signature to the last line before the next
column-0 declaration, minus any trailing comment block (which belongs to the
NEXT definition — pulling it inside the seal is a silent relocation).

    seal_defs.py <file.agda> <name> [<name> …]
"""
import re, sys

# ⚑⚑ `_snapshot_once` WAS DELETED HERE (Ⓐ49 ⟡split-8-unprotected).  Its rationale is
# KEPT AS RESIDUE — it was RIGHT about the danger, wrong only about PLACEMENT:
#
#   "This tool rewrites files it read — the shape that made 33 files unrecoverable
#    (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop, so a per-file
#    `guard` would arm only the first file AND shell out to `git stash create` on
#    every iteration; arming once per run is both correct and cheap."
#
# "Arm once per run" is now structural: the snapshot rides the single entry-point intent
# statement.  Leaving this as dead code would make `--unbound-snapshot` read FALSE-RED,
# since it keys on a `guard` call site being PRESENT, not on it being REACHABLE.




def block_end(lines, i, ind=0):
    """Last line index (exclusive) of the definition whose signature is at i.

    `ind` is the definition's own indent: 0 for a column-0 definition, 2 for one
    inside a `module Over … where` telescope (the in-telescope `opaque` idiom).
    A line at indent <= ind ends the definition, exactly as column 0 does for a
    top-level one.
    """
    j = i + 1
    last = j
    while j < len(lines):
        l = lines[j]
        if l.strip() and (len(l) - len(l.lstrip())) <= ind:
            # a column-0 line: either the next declaration, or a comment block
            # that heads it.  Either way this definition has ended at `last`.
            if l.lstrip().startswith("--"):
                break
            # A further CLAUSE of this definition also starts at column 0, and
            # its head is followed by PATTERNS, not `:`/`=` — matching on the
            # punctuation dropped every clause and sealed a bare signature.
            # The head token alone is the test.
            if l.split()[0] in own:
                j += 1
                last = j
                continue
            # ⚑ A `with`-CLAUSE continues the definition at the SAME indent:
            #     f x with p
            #     ... | yes e = …
            # Treating `...` as a terminator sealed the head and left the
            # clauses outside the `opaque` block ⇒ [Syntax.MissingWithClauses]
            # (measured on Laws/MonomialDelta.agda `xpower-basis-symm`).
            if l.lstrip().startswith("..."):
                j += 1
                last = j
                continue
            break
        j += 1
        if l.strip():
            last = j
    return last


def seal(path, names):
    src = open(path).read()
    lines = src.split("\n")
    global own
    out = []
    i = 0
    sealed = []
    while i < len(lines):
        l = lines[i]
        m = re.match(r"^(\s*)([^\s:;{}()@|]+)\s*:", l)
        if m and m.group(2) in names:
            own = {m.group(2)}
            ind = len(m.group(1))
            end = block_end(lines, i, ind)
            blk = lines[i:end]
            out.append(m.group(1) + "opaque")
            out.extend(("  " + b) if b.strip() else b for b in blk)
            sealed.append(m.group(2))
            i = end
            continue
        out.append(l)
        i += 1
    missing = set(names) - set(sealed)
    if missing:
        raise SystemExit(f"REFUSING: {path} has no top-level definition(s) {sorted(missing)}")
    # ⚑ THE WRITE-SITE `_snapshot_once(path)` IS GONE, NOT MOVED (Ⓐ49).  It sat BELOW
    # the `REFUSING: ... has no top-level definition(s)` raise above, so a run that
    # refused took no snapshot — and it fired only once the rewritten text was already
    # in hand.  The snapshot is taken at the entry intent statement.
    open(path, "w").write("\n".join(out))
    return sealed


own = set()

if __name__ == "__main__":
    # ⚑⚑ THIS TOOL HAS NO DRY RUN AT ALL — `seal()` writes unconditionally, and the
    # `_snapshot_once` at its last line arms only once the rewritten text is already in
    # hand.  So the entry guard is the ONLY point at which a caller can say what they
    # meant (Ⓐ44 ⟡move-guards-to-entry), and stating `--dry-run` here now REFUSES rather
    # than silently sealing: the tool cannot honour it, and the honest answer to an
    # intent it cannot serve is a refusal, not a write.
    # ⚑ AND THE OPERANDS ARE BARE POSITIONALS (`sys.argv[2:]` is the NAME SET), so a
    # mutation flag must be filtered out of them or `--apply` would be sealed as a
    # definition name.  That filtering is why the guard cannot be bolted on by a caller.
    # ⚑⚑⚑ SNAPSHOT BOUND TO THE INTENT STATEMENT (Ⓐ49 ⟡split-8-unprotected).  Ⓐ44 moved
    # the intent check here and left `_snapshot_once` at `seal()`'s last line, so this
    # tool read COMPLIANT to `intent_census` and was UNPROTECTED in practice.
    # ⚑ AND `seal()` HAS AN EARLY REFUSAL ABOVE ITS WRITE (`REFUSING: ... has no
    # top-level definition(s)`), so the unprotected window was not hypothetical: a run
    # naming one good and one bad definition raised past the snapshot having already
    # rewritten nothing — and any run that refused took no snapshot at all.
    # ⚑ `paths` IS LOAD-BEARING, NOT ADVISORY: `snapshot()` covers TRACKED content
    # whole-worktree, but `_copy_untracked(paths)` is the ONLY reach to untracked files.
    # So the operand filter is hoisted ABOVE the entry call to resolve the target first.
    import edit_snapshot as _es
    _argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    _es.require_at_entry("seal_defs", paths=_argv[:1])
    if "--dry-run" in sys.argv:
        raise SystemExit(
            "seal_defs has NO dry-run path: `seal()` writes unconditionally.\n"
            "  Refusing rather than writing under a stated --dry-run.\n"
            "  successor:  seal_defs.py <file.agda> <name>... --apply")
    p, ns = _argv[0], set(_argv[1:])
    if not ns:
        raise SystemExit(__doc__)
    if "opaque" in open(p).read():
        print(f"note: {p} already contains an `opaque` block — check for double-sealing")
    print(f"sealed in {p}: {', '.join(seal(p, ns))}")
