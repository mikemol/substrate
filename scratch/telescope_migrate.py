#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""telescope_migrate.py — UPArrow→UPArrowP telescope threading for one file. Shares the binder-rewrite +
variable-block SKELETON with the generalized scratch/telescope_migrate_gen.py via scratch/telescope_lib.py
(∩, lifted by the dedup machinery — jea_pysim found import_span identical + the thread core 81.4%-shared).

RESIDUE of THIS tool (the symmetric-difference half it keeps, NOT merged into the lib): the UPArrow-specific
import-retype (UPArrow→UPArrowP, trivial-UP→trivial-UPP), the Source/Target/Witness→P-shim projection renames,
and the defines-proj collision guard. Record fields (F : UPArrow → Set, L0-Source : UPArrow) and named-implicit
applications still need hand-fixes — run, then typecheck.

Usage: python3 scratch/telescope_migrate.py <file.agda> ...
"""
import re, sys
import telescope_lib

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
        edit_snapshot.guard('telescope_migrate', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



# UPArrow's carrier spec (the shared-core input): S,T : Set ; W : S{v} → T{v} → Set (dependent on earlier).
UP_CARRIERS = [("S", "Set"), ("T", "Set"), ("W", "S{v} → T{v} → Set")]


def migrate(path, apply=False):
    s = open(path).read()
    orig = s

    # does the file DEFINE its own Source/Target/Witness (collision) — then skip proj renames [RESIDUE]
    defines_proj = bool(re.search(r'^\s*(Source|Target|Witness)\s*:', s, re.M)) or \
        bool(re.search(r'field[\s\S]{0,400}?\b(Source|Target|Witness)\b\s*:', s))

    # ── SHARED SKELETON (telescope_lib): thread {v : UPArrow} → {v : UPArrowP Sv Tv Wv} + variable block ──
    s, _vars = telescope_lib.thread_binders(s, "UPArrow", UP_CARRIERS, new_record="UPArrowP")
    lines = s.split("\n")

    # ── RESIDUE: retype the UP import block (multi-line aware) ──
    i = 0
    while i < len(lines):
        if lines[i].startswith("open import Substrate.Category.UniversalProperty"):
            j = i
            while j + 1 < len(lines) and lines[j + 1][:1] in (" ", "\t") and lines[j + 1].strip():
                j += 1
            for k in range(i, j + 1):
                lines[k] = re.sub(r'\bUPArrow\b', 'UPArrowP', lines[k])
                lines[k] = re.sub(r'\btrivial-UP\b', 'trivial-UPP', lines[k])
                if not defines_proj:
                    lines[k] = re.sub(r'\bSource\b', 'SourceP', lines[k])
                    lines[k] = re.sub(r'\bTarget\b', 'TargetP', lines[k])
                    lines[k] = re.sub(r'\bWitness\b', 'WitnessP', lines[k])
            i = j + 1
        else:
            i += 1

    # ── RESIDUE: projection + trivial-UP renames in the BODY (non-import), if safe ──
    end = telescope_lib.import_span(lines)
    if not defines_proj:
        for idx in range(end + 1, len(lines)):
            if lines[idx].lstrip().startswith("--"):
                continue
            lines[idx] = re.sub(r'\bSource\b', 'SourceP', lines[idx])
            lines[idx] = re.sub(r'\bTarget\b', 'TargetP', lines[idx])
            lines[idx] = re.sub(r'\bWitness\b', 'WitnessP', lines[idx])
    for idx in range(end + 1, len(lines)):
        if lines[idx].lstrip().startswith("--"):
            continue
        lines[idx] = re.sub(r'\btrivial-UP\b', 'trivial-UPP', lines[idx])

    out = "\n".join(lines)
    if out != orig:
        # ⚑ THE WRITE IS NOW GATED ON THE STATED INTENT.  It used to be
        # unconditional — this tool took no flags at all, so every invocation
        # rewrote every file named on the command line.  Under the armed contract a
        # bare run now refuses; what would be WORSE is a stated `--dry-run` that
        # wrote anyway, which is what this branch did before the arm below existed.
        if not apply:
            return None, defines_proj
        _snapshot_once(path)
        open(path, "w").write(out)
        return True, defines_proj
    return False, defines_proj


if __name__ == "__main__":
    _files = [a for a in sys.argv[1:] if not a.startswith("-")]
    # ⚑ ONE ACT: state the intent AND snapshot, before any file is touched.
    # `_snapshot_once` sits under `if out != orig:` — the narrowest possible
    # condition — so a run over already-migrated files never snapshotted, and a run
    # that did changed the first file before recording anything about the rest.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("telescope_migrate", paths=_files)
    apply = "--apply" in sys.argv
    for p in _files:
        ch, coll = migrate(p, apply)
        tag = " [DEFINES-PROJ: proj-rename skipped, hand-check]" if coll else ""
        # ⚑ THREE OUTCOMES, NOT TWO — and collapsing the new one into `unchanged`
        # would be a lie in the dangerous direction: a dry run over a file that DOES
        # need migrating would report it as already done. `None` means "would have
        # changed, and did not".
        verb = "WOULD migrate " if ch is None else ("migrated " if ch else "unchanged ")
        print(verb + p + tag)
    if not apply:
        print("(dry run — pass --apply to write)")
