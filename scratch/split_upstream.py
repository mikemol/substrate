# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import re,sys,os,subprocess,glob
sys.path.insert(0,"scratch")
import split_lemmas as SL
import agda_lex
import os as _os, sys as _sys
from agda_imports import importable as _importable  # THE self-import predicate (never re-derive)
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import _span_end   # THE statement-span authority (agda_lex-backed); never re-derive

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
        edit_snapshot.guard('split_upstream', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")


USAGE = """\
split_upstream.py <Module> --apply    # SPLIT an upstream module into definition-per-file
                                      # leaves AND REWIRE every consumer, in one pass.

⚑⚑⚑ THIS TOOL WRITES. It calls `split_lemmas.split(..., apply=True)` unconditionally and
then rewrites every importer of <Module>. There is NO dry run: the split and the rewire are
one act, and a preview would have to simulate the whole rewire to be honest about it.

⚑⚑ IT USED TO RUN FROM A BARE POSITIONAL AND CRASH WITH `IndexError` WHEN GIVEN NONE
(⟡tools-cannot-self-describe, 2026-08-22). That is the worst of both: the repo's standing
instruction is *"run the tool bare and read its mode list — THAT output is the authority"*,
and a bare run here produced a traceback, so the tool that rewires the whole tree was the
one a reader could not ask what it does. Four tools shared the defect; two of them,
including this one, write unconditionally.

⚑ `--apply` IS NOW REQUIRED, and it is not a dry-run/apply pair — it is a CONFIRMATION.
Nothing here can preview, so the flag exists to make the write STATED rather than implied by
a positional. Same reasoning as the mutation-intent contract everywhere else in this toolkit
(no default-dry, no default-apply — state one), applied to a tool that can only apply.

  RECOVERY IS MANUAL AND PER-FILE. `edit_snapshot.guard` is armed on the first write; it
  records, it never restores. `git checkout <snapshot> -- <path>`.

  Pipeline context: `.claude/skills/agda-ban-decompose/SKILL.md` step 1-2, and
  `narrow_leaf_imports.py` is its usual follow-on.
"""

if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
    print(USAGE, file=sys.stderr)
    sys.exit(2)
if "--apply" not in sys.argv:
    print(USAGE, file=sys.stderr)
    print("REFUSED: this tool has no dry run — it splits AND rewires. State --apply.",
          file=sys.stderr)
    sys.exit(2)

MOD=sys.argv[1]                      # e.g. Substrate.Foundation.Fin
path="agda/"+MOD.replace(".","/")+".agda"
# ⚑ ONE ACT: the contract consulted at the DECISION, with the snapshot bound to it.
# ⚑⚑⚑ AND THE SNAPSHOT WAS TAKEN TOO LATE BY A WHOLE STAGE.  `SL.split(path,
# apply=True)` on the next line DESTROYS THE MONOLITH — it is stage one of two —
# and `_snapshot_once` did not fire until the REWIRE loop below (:104), i.e. after
# the split had already landed. So the one file whose prior content this tool
# destroys first was the one file the snapshot could not recover. That is not a
# placement preference; it is the recorded incident's own shape (a monolith rewritten
# to something shorter, unrecoverably) reproduced in the tool that performs the split.
# ⚑⚑ AND `_snapshot_once` ARMED ON THE FIRST FILE ONLY.  That is right for the
# git-stash half (whole-worktree) and WRONG for `_copy_untracked`, which saw exactly
# one path — while this tool rewires EVERY consumer tree-wide and the tree currently
# carries 40+ untracked Agda leaves from an in-flight split. `paths=` below names the
# monolith plus every consumer, resolved before the split so the pre-split state is
# what gets copied.
# ⚑ THE TOOL ALREADY REFUSED A BARE RUN (the `--apply` check above), so nothing about
# the caller's obligation changes here — what changes is that the refusal now routes
# through the one authority instead of restating it, and drags the snapshot with it.
_consumers=[f for f in glob.glob("agda/Substrate/**/*.agda",recursive=True)
            if not f.startswith("agda/"+MOD.replace(".","/")+"/")]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit_snapshot as _es
_es.require_at_entry("split_upstream", paths=[path]+_consumers)
files,named=SL.split(path,apply=True)
leaves=[MOD+"."+fn for fn,_,_ in named]
print(f"{MOD} -> {len(leaves)} leaves")
# ⚑ allow LEADING WHITESPACE: an `open import` inside a module/private block is indented,
# and a col-0 anchor silently skipped it — leaving a consumer importing the module we just
# deleted (caught by gen_build_makefiles' unresolved-import guard, not by this tool).
IMPRE=re.compile(r"^(\s*)(open\s+import|import)\s+"+re.escape(MOD)+r"(?![\w.])")
n=0
# ⚑ THE SAME LIST THE SNAPSHOT COVERS, not a second glob. Re-globbing here would
# walk the tree AFTER `SL.split` created the leaf directory, so the set the
# snapshot recorded and the set this loop rewrites could differ — and the
# difference would be exactly the new leaves, which have no pre-state to recover.
for f in _consumers:
    L=open(f).read().split("\n"); out=[]; i=0; hit=False
    while i<len(L):
        if IMPRE.match(L[i]):
            j=i
            j = _span_end(L, j) - 1
            ind=IMPRE.match(L[i]).group(1)          # preserve the original indentation
            # ⚑ preserve `public`: the statement may be a RE-EXPORT, and emitting plain
            # imports silently empties the re-exporting module — its consumers then lose
            # the names far away (Category.ComposedReference.V4 -> ActionAlgebra).
            # ⚑ MASK COMMENTS FIRST.  `\bpublic\b` over raw text matches the word in a
            # trailing comment, and this site EMITS: a false positive writes ` public`
            # onto every generated leaf import, manufacturing re-export conduits that
            # never existed — the opposite of the loss this guard exists to prevent.
            # (88 import statements tree-wide trip the unmasked form; measured.)
            pub=(" public" if re.search(r"(?<![\w.'-])public(?![\w'-])",
                                        agda_lex.mask_comments(" ".join(L[i:j+1])))
                 else "")
            out+= [ind+"open import "+x+pub for x in leaves]
            i=j+1; hit=True
        else: out.append(L[i]); i+=1
    _snapshot_once(f)
    if hit: open(f,"w").write("\n".join(out)); n+=1
print(f"rewired {n} consumers")
