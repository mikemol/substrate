#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Repair DEAD `fz`/`fs` references left by a deleted `renaming (zero to fz; suc to fs)`.

⟡public-policy.  Under the import ban a `renaming` is debt, not a fix — so the
Fin split provides UNAMBIGUOUS names AT SOURCE (`pattern fzero`/`fsuc` beside
Fin's constructors) and the consumers' alias references become dead names that
fail *silently* at the import and surface far away as `NotInScope`.

THE ONE HAZARD: a pattern synonym may not be PARTIALLY APPLIED.  `f ∘ fs` is
legal Agda today only because `fs` was a renamed constructor; rewritten to
`f ∘ fsuc` it does NOT compile.  So an unapplied occurrence is eta-expanded
(`(f ∘ fs)` → `(λ ix → f (fsuc ix))`) and any unapplied residue the rewrite
cannot see is REPORTED, never silently mangled.
"""
import os, re, sys

# `fz`/`fs` bound by whitespace/paren/brace — Agda names are not \w.
BOUND = r"(?<![\w₀-₉ⁿ'-])%s(?![\w₀-₉ⁿ'-])"
COMPOSE = re.compile(r"\(\s*([^()\s]+)\s+∘\s+fs\s*\)")
# an `fsuc` NOT followed by an argument: the partial-application hazard.
UNAPPLIED = re.compile(r"(?<![\w₀-₉ⁿ'-])fsuc\s*(?=[)\],;}]|$|∘|≡|,)")


FIN_IMPORT = re.compile(r"^open import Substrate\.Foundation\.Fin", re.M)


def repair(path, apply=False):
    src = open(path).read()
    if not (re.search(BOUND % "fz", src) or re.search(BOUND % "fs", src)):
        return False, "no dead alias"
    # THE DISCRIMINATOR: a dead Fin alias can only exist where Fin is imported.
    # Without it, `fs`/`fz` is a LOCAL VARIABLE that merely shares the spelling —
    # rewriting it renames a variable (semantically silent, and wrong).  Measured:
    # `consAll x (f ∷ fs)` (a list tail), `facets (cell fs)`, `x8a-ski-W fs v`
    # (a pair) all live in files with no Fin import at all.  A cheaper and
    # sharper guard than binder-position analysis, which cannot tell a pattern
    # VARIABLE from a constructor PATTERN (`fzero` on a LHS is a real match).
    if not FIN_IMPORT.search(src):
        return False, "no Fin import — `fz`/`fs` here is a LOCAL VARIABLE, not the deleted alias; REFUSING"
    # …AND the name must not be BOUND here.  The Fin-import test is necessary but
    # NOT sufficient: `prodFin-zero {suc k} f zero fz = …` binds `fz` as a PROOF
    # variable inside a file that does import Fin, and renaming it to `fzero`
    # shadows the pattern synonym (measured: LeibnizDetPerm, a
    # ConstructorPatternInWrongDatatype three build rounds later).  A dead alias
    # is never bound — so a binder occurrence settles it.  This check is sound
    # for `fz`/`fs` precisely because they name nothing in scope; it must NOT be
    # applied to `fzero`/`fsuc`, where a LHS occurrence is a constructor pattern.
    bound = set()
    for line in src.split("\n"):
        if line.lstrip().startswith("--"):
            continue
        lhs = re.split(r"(?<![-<>=≤≥≡≈])=(?![=>])", line, maxsplit=1)[0]
        for region in [lhs] + re.findall(r"λ\s*([^→]*)→", line) + re.findall(r"\(([^:()]+):", line):
            bound |= set(re.findall(r"[\w₀-₉ⁿ'-]+", region))
    local = bound & {"fz", "fs"}
    if local:
        return False, f"{sorted(local)} is BOUND here (a local variable) — REFUSING"
    n_eta = len(COMPOSE.findall(src))
    src = COMPOSE.sub(r"(λ ix → \1 (fsuc ix))", src)
    src = re.sub(BOUND % "fs", "fsuc", src)
    src = re.sub(BOUND % "fz", "fzero", src)
    warn = ""
    bad = [i + 1 for i, l in enumerate(src.split("\n"))
           if UNAPPLIED.search(l) and not l.lstrip().startswith("--")]
    if bad:
        warn = f"; ⚠ UNAPPLIED fsuc at line(s) {bad} — HAND-CHECK (a pattern synonym cannot be partially applied)"
    # `_∘_` may now be unreferenced; declining to import is ban-compliant.
    if "∘" not in re.sub(r"^open import .*$", "", src, flags=re.M):
        src = re.sub(r"^open import Substrate\.Foundation\.Function using \(_∘_\)\n", "", src, flags=re.M)
    # ⚑ THE WRITE IS NOW GATED ON THE STATED INTENT.  It used to be
    # UNCONDITIONAL — this tool had no `--dry-run` at all, so every invocation
    # wrote.  `require_at_entry` at `__main__` makes an unstated run REFUSE, but a
    # stated `--dry-run` would still have written here, which is a WORSE failure
    # than the unstated one: the caller states the safe intent and is disobeyed.
    if not apply:
        return True, f"WOULD eta-expand {n_eta} composition(s){warn}  (dry run)"
    open(path, "w").write(src)
    return True, f"eta-expanded {n_eta} composition(s){warn}"


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        print("usage: fix_dead_fin_alias.py <file.agda> ... (--apply | --dry-run)")
        sys.exit(2)
    # ⚑ ONE ACT: state the intent AND snapshot, before any write is decided. The
    # `guard` this replaces sat immediately above an unconditional `open(...,"w")`
    # deep in `repair` — correct where it ran, never consulted at the decision,
    # and there was no decision to consult it at until the `--dry-run` arm above.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("fix_dead_fin_alias", paths=args)
    apply = "--apply" in sys.argv
    for p in args:
        ok, msg = repair(p, apply)
        print(("FIXED " if ok else "skip  ") + p + "  " + msg)
