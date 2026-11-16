# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import re,sys,os
sys.path.insert(0,"scratch")
from agda_defs import def_index

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
        edit_snapshot.guard('narrow_leaf_imports', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



USAGE = """\
PREFIX=<Module> narrow_leaf_imports.py <file.agda>... --apply
                          # NARROW each file's `open import <PREFIX>` to the LEAF
                          # modules it actually uses, after <PREFIX> has been split.

⚑⚑⚑ THIS TOOL WRITES AND HAS NO DRY RUN. It rewrites every file named on the command line
in place. `edit_snapshot.guard` is armed on the first write — it RECORDS, it never restores;
recovery is `git checkout <snapshot> -- <path>`, manual and per-file.

⚑⚑ THE MODULE COMES FROM AN ENVIRONMENT VARIABLE, WHICH IS THE UNUSUAL PART AND WAS
UNDOCUMENTED. `PREFIX` names the module that was just split (e.g. `Substrate.Foundation.Fin`);
every `open import PREFIX…` in the given files is replaced by imports of the specific leaves
that file's body references, resolved through `agda_defs.def_index`. There is no default and
there cannot be a sensible one — a wrong PREFIX silently narrows the wrong imports.

⚑ IT CRASHED WITH `KeyError: 'PREFIX'` WHEN RUN BARE (⟡tools-cannot-self-describe,
2026-08-22), which is how the repo's standing instruction — *"run the tool bare and read its
mode list"* — met the tool the ⟡ban-decompose pipeline names at step 2. Five tools shared
that defect; this one is additionally the only one whose required input is invisible from the
command line.

⚑ `--apply` IS A CONFIRMATION, NOT HALF OF A DRY/APPLY PAIR. Nothing here can preview (the
narrowing is computed per-file from the def index and applied in the same pass), so the flag
exists to make the write STATED rather than implied by a file list.

  Pipeline context: `.claude/skills/agda-ban-decompose/SKILL.md` — run after
  `split_upstream.py <Module> --apply`. Note the SIBLING `narrow_leaf_opens.py` is a
  DIFFERENT tool; they are not spellings of one thing.
"""

if len(sys.argv) < 2 or "--apply" not in sys.argv or "PREFIX" not in os.environ:
    print(USAGE, file=sys.stderr)
    if "PREFIX" not in os.environ:
        print("REFUSED: PREFIX is unset — it names the module whose imports to narrow.",
              file=sys.stderr)
    elif "--apply" not in sys.argv:
        print("REFUSED: this tool has no dry run and rewrites in place. State --apply.",
              file=sys.stderr)
    sys.exit(2)

PREFIX=os.environ["PREFIX"]
# ⚑ ONE ACT: the contract consulted at the DECISION, with the snapshot bound to it.
# ⚑ THIS TOOL ALREADY REFUSED A BARE RUN (the `--apply` check above) — so what was
# missing is not the refusal but its ROUTING: the hand-rolled test states the same
# fact the contract states, and `_snapshot_once` then fired at the first write
# inside the loop, several decisions later. Consulting the authority here makes the
# two one act, and keeps the tool's own USAGE refusal, which says more (it names
# PREFIX) than the generic message can.
# ⚑ `paths=` IS THE WHOLE FILE LIST, NOT THE FIRST FILE. `_snapshot_once(f)` armed
# on file ONE and no-oped thereafter; that is right for the git-stash half (it is
# whole-worktree) and WRONG for `_copy_untracked`, which only ever saw one path —
# so an untracked leaf later in the list was unrecoverable. This is a live defect
# fixed by the move, not just a placement change.
_files=[a for a in sys.argv[1:] if not a.startswith("-")]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit_snapshot as _es
_es.require_at_entry("narrow_leaf_imports", paths=_files)
IMP=re.compile(r"^(open\s+import|import)\s+(\S+)")
idx=def_index(); cache={}
# ⚑ FILTER THE FLAG OUT OF THE FILE LIST. The loop consumed `sys.argv[1:]` verbatim, so
# adding `--apply` above would have made it `open("--apply")` and die PART-WAY THROUGH —
# after rewriting whatever files preceded it. That is the same half-processed failure
# `prune_imports` already exhibits (⟡tools-cannot-self-describe, defect 5), and it would
# have been introduced by the fix for defect 1.
for f in _files:
    L=open(f).read().split("\n")
    try: hdr=next(i for i,l in enumerate(L) if l.startswith("module "))
    except StopIteration: continue
    skip=set();k=hdr+1
    while k<len(L):
        if IMP.match(L[k]):
            # ⚑ span via agda_lex, not "every indented line" — that rule absorbs a
            # following parameterized `module M (a : A) … where` header (33 files
            # gutted; Coxeter/Core.agda 76 -> 3).  Here it would mark the header's
            # telescope as `skip`, dropping it from `body` and so making every name
            # it binds read as unused — a false DROP, the dangerous direction.
            e=_span_end(L,k)
            skip.update(range(k,e)); k=e
        else: k+=1
    body=" ".join(L[i] for i in range(hdr+1,len(L)) if i not in skip)
    for i in sorted(skip):
        m=IMP.match(L[i])
        if m: body+=" "+re.split(r"\b(using|renaming|hiding|public)\b",L[i][m.end():])[0]
    toks=set(re.findall(r"[^\s(){}\[\];,]+",body))
    out=[]
    for i,l in enumerate(L):
        m=IMP.match(l)
        # a `public` re-export is USED BY CONSUMERS, not by this file's body — the
        # token scan cannot see that, and dropping it empties the re-exporting module.
        if m and m.group(2).startswith(PREFIX+".") and "public" not in l:
            mod=m.group(2)
            if mod not in cache: cache[mod]={n for n,ms in idx.items() if mod in ms}
            p=cache[mod]
            if p and not (p & toks): continue
        out.append(l)
    # ⚑ THE SNAPSHOT MOVED TO ENTRY (see above).  `_snapshot_once` is retained,
    # not deleted: it is idempotent (a no-op once the run is armed), and it is the
    # residue of the placement this file used to have — kept so the next reader
    # sees the move rather than an absence.
    _snapshot_once(f)
    open(f,"w").write("\n".join(out))
