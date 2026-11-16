#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""telescope_migrate_gen.py — GENERALIZED quantifier-threading telescope migrator for OBJECT-TYPE records
(LanguageWitness / Brick / Strict2Monoid). Shares the binder-rewrite + variable-block SKELETON with the
UPArrow-specific scratch/telescope_migrate.py via scratch/telescope_lib.py (∩, lifted by the dedup machinery).

RESIDUE of THIS tool (the symmetric-difference half it keeps, vs the UPArrow one): the CONFIGS table —
per-record carrier specs — and its ⟡tele-projection-tails post-pass (the moved-field projection rewrite).
(The UPArrow tool's residue is its import-retype + Source/Target/Witness projection renames; kept there.)

Two passes per file:
  1. thread_binders  — `{v : Record}` → `{v : Record C1ᵥ C2ᵥ…}` + the `private variable` carrier block.
  2. project_tails   — a surviving PROJECTION `Record.f v` of a MOVED field f (v a threaded binder) becomes
     the threaded carrier `<suffix>v` (the field is now a PARAM, so its projection IS the carrier var).

Usage: telescope_migrate_gen.py <record-key> <file.agda> … --dry-run   unified diff, writes nothing
       telescope_migrate_gen.py <record-key> <file.agda> … --apply     rewrite in place

⚑⚑ THIS TOOL USED TO WRITE BY DEFAULT, WITH `--dry` THE ONLY ESCAPE — exactly backwards from every
dry-by-default codemod beside it (`retire_mod_tip`, `rewire_fcr`, `drop_dead_renames`,
`collapse_carrier_nesting` all require `--apply` to write). It went UNDECLARED on top of that, so
the one flag standing between an operator and an in-place rewrite of an Agda file was invisible in
the usage line — and since the tool validated no argv, a typo'd `--dry-run` fell straight through
to the writing branch.

⚑ THE DEFAULT IS NOW GONE IN BOTH DIRECTIONS (⟡explicit-mutation, operator 2026-08-24). The prior
reading declined to invert it because *"flipping the default now would make every existing
invocation a no-op, which is its own hazard"* — a correct objection to INVERTING a default, and it
dissolves once there is no default to invert. Nothing becomes a silent no-op: an invocation stating
neither flag REFUSES, and `--dry` is caught by name as a near miss that prints `--dry → --dry-run`.
The cost is real and intended — a bare `telescope_migrate_gen.py <key> <file>` that used to write
now stops — which is the whole point on a tool whose write path is snapshot-guarded precisely
because this class of rewrite once left 33 files unrecoverable.
"""
import sys, re
import telescope_lib

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

# ── RESIDUE: record short-name → carrier specs (suffix, type_template with {v} for the binder var). ──
CONFIGS = {
    "LanguageWitness": [("Basis", "Set"), ("FreeCarrier", "Set")],
    "Brick":           [("Tag", "Set")],                       # homomorphism-tag : Set
    "Strict2Monoid":   [("M", "Set"), ("Eq", "M{v} → M{v} → Set")],
}

# ⟡tele-projection-tails: MOVED field name → its carrier suffix (the params record-edit created). A projection
# `Record.<field> v` of one of these becomes `<suffix>v`. (Field names ≡ suffixes for Language/Basis; differ
# for Brick's `homomorphism-tag`→`Tag` and Strict2Monoid's `_≈_`→`Eq`.)
MOVED_FIELDS = {
    "LanguageWitness": {"Basis": "Basis", "FreeCarrier": "FreeCarrier"},
    "Brick":           {"homomorphism-tag": "Tag"},
    "Strict2Monoid":   {"M": "M", "_≈_": "Eq"},
}


def project_tails(src, record, vars_seen, moved_fields):
    """Rewrite every surviving projection `Record.f v` of a MOVED field f (v ∈ the threaded binders) to the
    threaded carrier `<suffix>v` — non-import, non-comment lines only (the same regex also catches a value
    LIFTED into a type sig). Returns (new_src, n_rewrites, open_warn). An `open Record` makes UNQUALIFIED
    `f v` projections scope-ambiguous → open_warn=True (flag for HAND-CHECK, NOT auto-rewritten)."""
    lines = src.split("\n")
    end = telescope_lib.import_span(lines)
    n = 0
    for idx in range(end + 1, len(lines)):
        if lines[idx].lstrip().startswith("--"):
            continue
        for f, suf in moved_fields.items():
            for v in vars_seen:
                pat = r"(?<![^\\s(){}\\[\\];,])" + re.escape(record) + r"\." + re.escape(f) + r"\s+" + re.escape(v) + r"\b"
                new = re.sub(pat, f"{suf}{v}", lines[idx])
                if new != lines[idx]:
                    n += 1; lines[idx] = new
    open_warn = bool(re.search(r"\bopen\s+" + re.escape(record) + r"\b", src))
    return "\n".join(lines), n, open_warn


if __name__ == "__main__":
    # ⚑ DEMANDED BEFORE THE BRANCH IS COMPUTED, not inside the writing arm — the absent
    # flag WAS the writing arm here, so a guard placed after it could never see the case.
    # ⚑⚑⚑ AND IT NOW TAKES THE SNAPSHOT IN THE SAME ACT (Ⓐ49 ⟡split-8-unprotected).
    # `require_explicit_mutation` checks intent and NOTHING ELSE — it does not delegate to
    # `guard` — so this tool stated intent at entry while `_snapshot_once` sat two
    # conditions deep: under `else:` (i.e. not dry) AND past `if new == src: continue`.
    # A run that migrated nothing, or that ran dry, armed no snapshot; the tool read
    # COMPLIANT to `intent_census` and was UNPROTECTED in practice.
    # ⚑ `require_at_entry` IS THE BOUND FORM: it delegates to `require_explicit_mutation`
    # (the one authority — this is not a fourth body) and then, past the intent check,
    # to `guard`.  Stating `--apply` IS taking the snapshot.
    # ⚑ `paths` IS LOAD-BEARING: `snapshot()` covers TRACKED content whole-worktree, but
    # `_copy_untracked(paths)` is the ONLY reach to untracked files, and it iterates
    # `paths`.  The operands are hoisted above the guard so the targets are known to it.
    import edit_snapshot as _es
    _paths = [a for a in sys.argv[2:] if not a.startswith("--")]
    _es.require_at_entry("telescope_migrate_gen", paths=_paths)
    # ⚑ THE record-key VALIDATION MOVED BELOW THE GUARD (Ⓐ49).  It used to run FIRST, so
    # `telescope_migrate_gen.py <bad-key>` exited having never been asked for intent — the
    # guard was one dispatch short of entry, and `--unbound-snapshot` could not see it
    # because it classifies by SOURCE POSITION and the call sat inside `__main__` either
    # way.  An argument-validation bail is not a read-path exemption: under this contract
    # a tool that CAN mutate demands the statement at EVERY invocation.
    key = sys.argv[1] if len(sys.argv) > 1 else ""
    if key not in CONFIGS:
        sys.exit(f"unknown record-key {key!r}; known: {list(CONFIGS)}")
    dry = "--dry-run" in sys.argv
    for p in _paths:
        src = open(p).read()
        new, vars_seen = telescope_lib.thread_binders(src, key, CONFIGS[key])
        new, n_tails, open_warn = project_tails(new, key, vars_seen, MOVED_FIELDS.get(key, {}))
        if new == src:
            print(f"unchanged {p}"); continue
        if dry:
            import difflib
            sys.stdout.writelines(difflib.unified_diff(src.splitlines(True), new.splitlines(True),
                                                       fromfile=p, tofile=p + " (migrated)"))
        else:
            # ⚑ THE WRITE-SITE `_snapshot_once(p)` IS GONE, NOT MOVED (Ⓐ49).  It sat TWO
            # conditions deep — under `else:` (not dry) and past `if new == src:
            # continue` — so a run that migrated nothing armed nothing.  Entry-bound now.
            open(p, "w").write(new)
        print(f"{'DRY ' if dry else ''}migrated {p}  (binders: {vars_seen}, projection-tails: {n_tails})")
        if open_warn:
            print(f"# ⚠ HAND-CHECK: `open {key}` present — unqualified `f v` projections not auto-rewritten")
