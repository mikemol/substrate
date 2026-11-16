#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The ONE place Agda import blocks are modified.

⟡import-topo: any tool that touches imports must (a) topologically order the
block — a parameterized import `open import M Arg` cannot precede whatever
binds `Arg` — and (b) verify it did not lose a line.  Both live HERE rather
than in a separate pass, because a separate pass can be skipped and this
session skipped it twice: once placing an import before its argument binder,
once burying an import inside a proof body.

⟡no-qualifiers: emits bare `open import` only — never using/renaming/hiding
or `as` aliasing.

SAFETY: every mutation asserts the result is a permutation of the input plus
exactly the lines intentionally added.  An earlier topo sorter mis-parsed the
block bounds and silently deleted 2094 lines of definitions; the assertion,
not the parser, is what makes that impossible."""
import re,sys,os,collections
# ⚑ `sys.path.insert(0,"scratch")` was cwd-DEPENDENT: run from anywhere but the repo
# root the sibling import failed (or, worse, found a different `scratch`).  Anchor on
# this file's own directory, which is correct from any cwd.
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from agda_defs import def_index
import agda_lex

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
        edit_snapshot.guard('agda_imports', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



IMP=re.compile(r"^(open\s+)?import\s+(\S+)(.*)$")

# ⚑ THE SPAN RULE IS NOT RE-DERIVED HERE.  The naive "head plus every indented line"
# test does not delimit an Agda statement: it absorbs the indented parameter telescope
# of a following `module M (a : A) … where` header, and a caller that MOVES or DELETES
# the span takes the header with it.  Measured: 33 files gutted in one arc,
# Coxeter/Core.agda 76 lines -> 3, found only by the build.  This module had FOUR
# copies of that rule; they now all route through `agda_lex`, which is depth-aware
# (a wrapped `using (…; module W)` continuation legitimately starts with a keyword)
# and carries the regression corpus (`python3 scratch/agda_lex.py`).
def _depth(text): return agda_lex._depth_after(agda_lex.mask_comments(text),0)

def importable(path, mod):
    """May `path` emit `open import mod`?  THE shared self-import predicate.

    ⚑ A MODULE MUST NEVER IMPORT ITSELF.  Agda reports it as
    [CyclicModuleDependency] ("X importing X") — a hard error that reads like a
    genuine dependency cycle and sends the reader hunting a structural problem.
    It arises MECHANICALLY: a rewire resolves a name to its definer, and when the
    file being rewired IS that definer the naive answer is itself.  Measured: 10
    Foundation.Bool.Properties leaves each emitted `open import <its own module>`;
    a guard added to `add_import` did not stop it, because a SECOND writer had its
    own copy — and 12 more tools emit import lines inline.

    Those tools cannot call `add_import`: they REWRITE an import in place, keeping
    its indentation, `public` tail and position, where `add_import` appends.  So the
    sharable unit is the PREDICATE, not the writer.  Call this before emitting.
    """
    own = _module_of(path)
    return not (own and mod == own)


def _module_of(path):
    """The module a file declares, read from its own `module … where` header.

    From the HEADER, not the path: a file's directory can disagree with its module
    (mid-collapse, mid-move), and the header is what Agda binds.
    """
    try:
        for l in open(path,encoding="utf-8"):
            m=re.match(r"^module\s+(\S+)",l)
            if m: return m.group(1)
    except OSError:
        pass
    return None

# ⚑ LIFTED TO `agda_lex.span_end` (2026-08-01).  This was a leading-underscore
# name — declared private — imported by SEVEN other files, i.e. public API wearing
# a private label.  The rule is LEXICAL (a wrapper over `_continues`/`_depth_after`,
# both defined in agda_lex) while THIS module's job is modifying import blocks, so
# a tool needing only "where does this statement end" had to import an import
# rewriter to ask.  The alias keeps all seven consumers working unchanged; new code
# takes `agda_lex.span_end`.
_span_end = agda_lex.span_end


def rename_pairs(stmt):
    """(source, target) for every `renaming (src to tgt; …)` pair in an import statement.

    ⚑ LIFTED FROM `scope_fix._rename_pairs` (2026-08-01).  Another leading-underscore
    name consumed across boundaries — by `drop_dead_renames`, `rewire_to_leaves`, and
    `scripts/check_import_shape` (a PRE-COMMIT GATE).  A CI gate reaching into a
    2000-line scope-fixing module to borrow a clause parser is the "would a third tool
    find it?" test failing outright, and the fourth adopter had to be told the parser
    existed after an agent reported it ABSENT tree-wide.

    Home is here because this is IMPORT-CLAUSE SYNTAX and this module declares itself
    "the ONE place Agda import blocks are modified".  `scope_fix._rename_pairs` stays
    as an alias; its own 3 internal call sites are untouched.
    """
    out = []
    for r in re.findall(r"renaming\s*\(([^)]*)\)", stmt, re.S):
        for pair in r.split(";"):
            parts = pair.split()
            if len(parts) == 3 and parts[1] == "to":
                out.append((parts[0], parts[2]))
    return out

# A col-0 `open M ...` (module open, NOT an import) is part of the block: it
# affects scope and must follow whatever binds M.  Treating it as a block
# TERMINATOR truncated the block and defeated the sort (V4Normal).
OPN=re.compile(r"^open\s+(?!import\b)(\S+)(.*)$")

def parse_block(lines):
    """The CONTIGUOUS leading import block: (start, end, stmts, trailing).
    A col-0 line that is not an import / continuation / comment / blank ENDS it."""
    start=None
    for i,l in enumerate(lines):
        if IMP.match(l): start=i; break
    if start is None: return None,None,[],[]
    stmts=[];cur=None;pending=[];i=start
    while i<len(lines):
        l=lines[i]
        if IMP.match(l):
            if cur: stmts.append(cur)
            m=IMP.match(l)
            cur={"pre":pending,"lines":[l],"mod":m.group(2),"tail":m.group(3)};pending=[]
        elif OPN.match(l):
            if cur: stmts.append(cur)
            m=OPN.match(l)
            cur={"pre":pending,"lines":[l],"mod":None,"tail":m.group(2),
                 "opens":m.group(1)};pending=[]
        elif cur is not None and agda_lex._continues(l,_depth("\n".join(cur["lines"]))):
            cur["lines"].append(l)
        elif l.strip()=="" or l.lstrip().startswith("--"):
            if cur: stmts.append(cur);cur=None
            pending.append(l)
        else: break
        i+=1
    if cur: stmts.append(cur)
    return start,i,stmts,pending

def _args(stmt):
    """REQUIRES: a parameterized import needs its module arguments; a module
    `open M` needs whatever binds M (usually an `import ... as M`)."""
    t=re.split(r"\b(using|renaming|hiding|public)\b",stmt["tail"])[0]
    args=[a for a in re.findall(r"[^\s(){}]+",t) if not a.isdigit()]
    if stmt.get("opens"): args.append(stmt["opens"])
    return args

def _order(stmts):
    idx=def_index()
    prov=[]
    for s in stmts:
        if s["mod"]:
            names={n for n,mods in idx.items() if s["mod"] in mods}
            # an `import X as A` binds the alias A
            m=re.search(r"\bas\s+(\S+)",s["tail"])
            if m: names.add(m.group(1))
        else:                       # `open M using (a; b)` binds a, b
            names=set(re.findall(r"[^\s;()]+",
                      (re.search(r"using\s*\(([^)]*)\)",s["tail"]) or
                       re.match(r"()",""))
                      .group(1) if re.search(r"using\s*\(",s["tail"]) else ""))
        prov.append(names)
    n=len(stmts);dep=[set() for _ in range(n)]
    for j,s in enumerate(stmts):
        need=set(_args(s))
        if not need: continue
        for k in range(n):
            if k!=j and (need & prov[k]): dep[j].add(k)
    order=[];placed=[False]*n
    for _ in range(n):
        for j in range(n):
            if not placed[j] and all(placed[k] for k in dep[j]):
                order.append(j);placed[j]=True;break
        else:
            for j in range(n):
                if not placed[j]: order.append(j);placed[j]=True
            break
    return order

def binding_sites(lines):
    """name -> the line index at which it becomes bound, over the WHOLE file.

    ⟡one-topo-sort: a module-header PARAMETER, a local DEFINITION, an
    import-provided NAME and an `import M as A` alias are FOUR spellings of
    one thing — a binding site — and every import / `open M` is a statement
    that must follow the sites it references.  Modelling only import
    ARGUMENTS is what produced two separate breakages: a parameterized
    import hoisted above its `module … where` header (params unbound), and
    an `open AbelianGroup` hoisted above the `record AbelianGroup` that
    binds it (259 files).  Neither is an exception to the sort; both are
    edges it was not being told about."""
    idx=def_index();site={}
    for i,l in enumerate(lines):
        # (1) module header: params are bound from the `where` line onward
        if re.match(r"^module\s+\S+",l):
            j=i
            while j<len(lines) and "where" not in lines[j]: j+=1
            for g in re.findall(r"[({]([^:(){}]+):",  "\n".join(lines[i:j+1])):
                for nm in g.split(): site.setdefault(nm,j)
            continue
        m=IMP.match(l) or OPN.match(l)
        if m:
            # A statement spans its indented continuations; its names become
            # bound at the END of the block.  Anchoring on the FIRST line let
            # a later insert land INSIDE a multi-line import's arguments.
            e=_span_end(lines,i)-1
            mi=IMP.match(l)
            if mi:                              # (3) import-provided names
                for n,mods in idx.items():
                    if mi.group(2) in mods: site.setdefault(n,e)
                a=re.search(r"\bas\s+(\S+)",mi.group(3))
                if a: site.setdefault(a.group(1),e)
            else:                               # `open M using (a; b)` binds a,b
                u=re.search(r"using\s*\(([^)]*)\)",m.group(2))
                if u:
                    for n in re.findall(r"[^\s;()]+",u.group(1)): site.setdefault(n,e)
            continue
        if not l or l[0] in " \t-{": continue    # (2) local definitions
        d=re.match(r"^(?:data|record|pattern)\s+([^\s({:]+)",l) or \
          (re.match(r"^([^\s:;{}()@]+)",l) if (":" in l or "=" in l) else None)
        if d:
            j=i+1
            while j<len(lines) and (not lines[j].strip() or lines[j][0] in " \t"): j+=1
            site[d.group(1)]=j-1                 # end of the definition block
    return site

def _refs(block):
    """Every name a statement REFERENCES: its module arguments, plus — for a
    col-0 `open M` — the opened module itself."""
    head=" ".join(block)
    t=re.split(r"\b(using|renaming|hiding|public)\b",head)[0]
    t=re.sub(r"^(open\s+import|import|open)\s+\S+","",t)
    refs={a for a in re.findall(r"[^\s(){};]+",t) if not a.isdigit()}
    m=OPN.match(block[0])
    if m: refs.add(m.group(1))
    # a QUALIFIED use `A.f` references the binder `A` (an `import … as A`),
    # not the dotted token; without the prefix the edge is invisible (S3).
    refs |= {r.split(".")[0] for r in list(refs) if "." in r}
    return refs

def order_file(path):
    """Move every import / `open M` below the binding sites it references.

    The file-wide form of the block sort: same edges, total rather than
    local.  Permutation-guarded like every other mutation here."""
    lines=open(path).read().split("\n")
    site=binding_sites(lines)
    stmts=[];i=0
    while i<len(lines):
        if IMP.match(lines[i]) or OPN.match(lines[i]):
            j=_span_end(lines,i)
            need=_refs(lines[i:j]) & site.keys()
            if need:
                anchor=max(site[n] for n in need)
                if anchor>=j: stmts.append((i,j,anchor))
            i=j
        else: i+=1
    if not stmts: return False,"already ordered"
    moved={};skip=set()
    for a,b,anc in stmts:
        moved.setdefault(anc,[]).extend(lines[a:b]);skip|=set(range(a,b))
    out=[]
    for i,l in enumerate(lines):
        if i not in skip: out.append(l)
        if i in moved: out.append("");out.extend(moved[i])
    if collections.Counter(out)!=collections.Counter(lines)+collections.Counter([""]*len(moved)):
        return False,"ABORT: not a permutation (refusing to write)"
    _snapshot_once(path)
    open(path,"w").write("\n".join(out))
    return True,f"moved {len(stmts)} statement(s) below their binding sites"

def _emit(path,lines,start,end,stmts,trailing,added):
    order=_order(stmts)
    out=lines[:start]
    for j in order: out.extend(stmts[j]["pre"]);out.extend(stmts[j]["lines"])
    out.extend(trailing);out.extend(lines[end:])
    want=collections.Counter(lines)+collections.Counter(added)
    if collections.Counter(out)!=want:
        return False,"ABORT: not a permutation of input+added (refusing to write)"
    open(path,"w").write("\n".join(out))
    moved=sum(1 for a,b in zip(order,range(len(order))) if a!=b)
    return True,(f"+{len(added)} import(s), {moved} reordered" if added
                 else f"reordered ({moved} moved)")

def hoist_imports(path):
    """POLICY: imports at the top, C89-declaration style.

    Agda permits a top-level import after definitions, and that freedom is
    what made this tool unsound: it manages a leading BLOCK while Agda's
    scope is the whole file in order, so an import inserted at the top could
    not be ordered against a binder further down (ExtrudeCoEmitGraded).
    Hoisting every import to the top makes the block and the file agree, so
    the topo sort is total rather than local.

    REFUSES to hoist an import whose module ARGUMENT is a locally defined
    name — hoisting it above its own binder would be wrong.  Reported, not
    guessed."""
    lines=open(path).read().split("\n")
    start,end,lead,trailing=parse_block(lines)
    if start is None: return False,"no imports"
    tail=lines[end:]
    late=[];keep=[];i=0
    while i<len(tail):
        l=tail[i]
        m=IMP.match(l) or OPN.match(l)
        if m and not l.startswith(" "):
            e=_span_end(tail,i)
            late.append(tail[i:e]);i=e;continue
        keep.append(l);i+=1
    if not late: return False,"already top"
    idx=def_index()
    body="\n".join(keep)
    local={m.group(1) for m in re.finditer(r"^([^\s:()@{}]+)\s*:(?!:)",body,re.M)}
    blocked=[]
    for blk in late:
        m=IMP.match(blk[0])
        if m:
            t=re.split(r"\b(using|renaming|hiding|public)\b",m.group(3))[0]
            if any(a in local for a in re.findall(r"[^\s(){}]+",t)):
                blocked.append(blk)
    if blocked:
        return False,f"ABORT: {len(blocked)} import(s) take a locally-defined argument"
    out=lines[:end]+[l for blk in late for l in blk]+keep
    if collections.Counter(out)!=collections.Counter(lines):
        return False,"ABORT: not a permutation"
    open(path,"w").write("\n".join(out))
    ok,msg=sort_imports(path)
    return True,f"hoisted {len(late)} import(s); "+msg

def sort_imports(path):
    lines=open(path).read().split("\n")
    start,end,stmts,trailing=parse_block(lines)
    if start is None or len(stmts)<2: return False,"trivial"
    if _order(stmts)==list(range(len(stmts))): return False,"already ordered"
    return _emit(path,lines,start,end,stmts,trailing,[])

def add_import(path,mod,args=""):
    line=f"open import {mod}"+(f" {args}" if args else "")
    lines=open(path).read().split("\n")
    if any(l.strip()==line for l in lines): return False,"present"
    # ⚑ A MODULE MUST NEVER IMPORT ITSELF.  Agda reports this as
    # [CyclicModuleDependency] ("X importing X") — a hard error that reads like a
    # genuine dependency cycle and sends the reader hunting a structural problem.
    # It arises mechanically: a rewire resolves a name to its definer, and when the
    # file BEING rewired IS that definer the naive answer is itself.  Measured: 10
    # Foundation.Bool.Properties leaves each emitted `open import <its own module>`.
    # The chokepoint is the only place this can be caught once for every caller.
    own=_module_of(path)
    if own and mod==own: return False,"self-import refused"
    start,end,stmts,trailing=parse_block(lines)
    if start is None:
        # ⚑ A PARAMETERIZED module header SPANS LINES:
        #     module M
        #       (Word : Set)
        #       (_++_ : Word → Word → Word)
        #       where
        # so `^module \S+ where` does not match and this returned "no module header",
        # silently declining to add an import the file needed.  MEASURED: the Coxeter
        # Core leaves lost `Foundation.Eq` and failed [NotInScope] ≡ — and because the
        # caller only logs the refusal, it read as "nothing to do" rather than "could
        # not place".  Find the header's `where` and insert after it; an import for a
        # parameterized module may also sit ABOVE the header (it can be needed BY the
        # telescope), which is where the split emits it, so prefer that slot when the
        # telescope itself references the module.
        hdr=next((i for i,l in enumerate(lines) if re.match(r"^module\s+\S+",l)),None)
        if hdr is None: return False,"no module header"
        end_hdr=hdr
        while end_hdr<len(lines) and not re.search(r"\bwhere\b",lines[end_hdr]):
            end_hdr+=1
        if end_hdr>=len(lines): return False,"module header has no `where`"
        if end_hdr>hdr:
            # multi-line header: the telescope may need the import, so place it ABOVE.
            lines.insert(hdr,line); lines.insert(hdr+1,"")
        else:
            lines.insert(end_hdr+1,line)
        open(path,"w",encoding="utf-8").write("\n".join(lines))
        return True,"+1 (no prior block)"
    m=IMP.match(line)
    stmts.append({"pre":[],"lines":[line],"mod":m.group(2),"tail":m.group(3)})
    return _emit(path,lines,start,end,stmts,trailing,[line])

def drop_import(path, mod):
    """Remove the top-level `open import <mod>` STATEMENT (and its span) from `path`.

    ⚑ THE INVERSE OF `add_import`, AND IT WAS MISSING WHILE THE FORWARD DIRECTION
    HAD THREE CALLERS.  A sweep that ADDS a guessed import has no way to retract
    one: `decompose_rewrite.drop_import` removes a module's import from EVERY file,
    which is a different question (retire a provider) from "cut this ONE edge".
    Measured 2026-08-24: 16 spurious imports appended by NotInScope repair created
    10 import SCCs, and no tool in the kit could remove a single named edge.

    ⚑ REFUSES A NON-BARE STATEMENT.  A line carrying `using`/`renaming`/`public`
    is load-bearing beyond the edge, and deleting it silently drops bindings the
    body may need — the caller must see that and decide.  Bare `open import M` is
    exactly the form the ban leaves behind, which is the form a guessed import takes.

    ⚑⚑ AND AN *APPLIED* IMPORT IS NOT BARE EITHER — this guard learned that by
    getting it wrong.  `open import M a b c` fills M's parameter telescope; it has
    no `using` keyword, so a keyword-only check passes it, and the first run of this
    tool deleted `open import …Coxeter.ListPresentation Gen Canonical-ex c-ε insert
    insert-canonical-ex` — a deliberate, commented, five-argument rewire — as if it
    were a guessed edge.  Recovered from the snapshot.  The tell is ARGUMENTS AFTER
    THE MODULE NAME, and a keyword census cannot see them.

    Permutation-guarded like every other mutation here: the result must be the
    input MINUS precisely the removed span.
    """
    lines = open(path, encoding="utf-8").read().split("\n")
    hits = []
    i = 0
    while i < len(lines):
        m = IMP.match(lines[i])
        if m and m.group(2) == mod:
            j = agda_lex.span_end(lines, i)
            hits.append((i, j))
            i = j
            continue
        i += 1
    if not hits:
        return False, f"no `import {mod}` statement"
    for a, b in hits:
        stmt = "\n".join(lines[a:b])
        if re.search(r"\b(using|renaming|hiding|public)\b", stmt):
            return False, "REFUSED: statement is not bare (using/renaming/hiding/public)"
        tail = IMP.match(lines[a]).group(3)
        rest = "\n".join(lines[a + 1:b])
        if tail.strip() or rest.strip():
            return False, ("REFUSED: APPLIED import (arguments fill a parameter "
                           f"telescope): `{tail.strip() or rest.strip()[:60]}`")
    cut = set()
    for a, b in hits:
        cut |= set(range(a, b))
    out = [l for i, l in enumerate(lines) if i not in cut]
    removed = [l for i, l in enumerate(lines) if i in cut]
    if collections.Counter(out) + collections.Counter(removed) != collections.Counter(lines):
        return False, "ABORT: not a permutation (refusing to write)"
    _snapshot_once(path)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return True, f"-{len(hits)} import(s) of {mod}"


if __name__=="__main__":
    cmd=sys.argv[1]
    # ⚑ ONE ACT: state the intent AND snapshot, at the DISPATCH — before any
    # subcommand runs, and after `cmd` is known so an unknown command still gets
    # its usage message rather than a mutation refusal.
    # ⚑⚑ THE GATE IS HERE AND NOT AT MODULE TOP BECAUSE THIS FILE IS A LIBRARY
    # FIRST.  `importable`, `_span_end` and `stage_warning` are imported by a dozen
    # sibling tools (`fix_stale_using`, `fix_orphan_using`, `narrow_leaf_imports`,
    # …); a module-top `require_at_entry` would refuse at IMPORT, taking down every
    # consumer that never intended to mutate anything. The write paths all run
    # through this dispatch, so this is the earliest point that is both after the
    # library/CLI split and before every write.
    # ⚑ ALL FOUR SUBCOMMANDS WRITE — this tool has no read mode and no `--apply`,
    # so a bare `agda_imports.py sort <file>` rewrote in place with nothing stated.
    # That is exactly the debt this ratchet counts.
    if cmd in ("sort", "order", "add", "drop"):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import edit_snapshot as _es
        _targets = ([sys.argv[2]] if cmd in ("add", "drop")
                    else [a for a in sys.argv[2:] if not a.startswith("-")])
        _es.require_at_entry(f"agda_imports {cmd}", paths=_targets)
        if "--apply" not in sys.argv:
            print(f"agda_imports {cmd}: WOULD rewrite {len(_targets)} file(s).  "
                  f"(dry run — pass --apply)")
            sys.exit(0)
    if cmd=="sort":
        for p in sys.argv[2:]: print(*sort_imports(p),p)
    elif cmd=="order":                 # the file-wide binding-site sort
        for p in sys.argv[2:]: print(*order_file(p),p)
    elif cmd=="add":
        print(*add_import(sys.argv[2],sys.argv[3]," ".join(sys.argv[4:])),sys.argv[2])
    elif cmd=="drop":
        print(*drop_import(sys.argv[2],sys.argv[3]),sys.argv[2])
    else:
        print(f"agda_imports.py: unknown command {cmd!r} — "
              "sort | order | add <file> <mod> [args] | drop <file> <mod>",
              file=sys.stderr)
        sys.exit(2)

# ── pipeline-stage discipline ──────────────────────────────────────────────
PIPELINE = "scratch/split_pipeline.py"

# ⚑ THE BACK-EDGE — ONE AUTHORITY, CITED BY EVERY TOOL IN THE SPLIT/TELESCOPE FAMILY.
# The operator's requirement (2026-08-26): *"always ensure the remaining tools point to
# a document that points back at all of them, so they're cross-discoverable"* — the
# remedy for a measured loop: *"some of the tools got built AFTER the LLMs forgot the
# pipeline existed. Honestly, that kept happening."*
#
# ⚑⚑ THE DOCUMENT IS NOT THE MECHANISM; THE REFUSAL THAT NAMES IT IS.  A document
# nobody is routed to loses to a refusal by construction — that argument already sank
# an earlier index proposal here, and it applies to this one.  So this is a CONSTANT a
# decline PRINTS, not a page a reader is expected to know about: `hook_structural_query`
# names the owning tool, `gate_census`'s ABSENT rows name `--init-absent --apply`,
# `vfs.listdir` names `--suffix`, and `split_lemmas`' telescoped-root decline names
# `split_telescoped`.  Every one of those is a refusal carrying its successor.
#
# ⚑ IT IS A PATH, NEVER A COPY OF THE ROSTER.  A second roster beside the document is
# the duplication this repo keeps paying for (SKILL.md:106).  The tools cite this
# string; the string names the page; the page holds the table.  Nothing here restates
# which tool handles which shape — that would be the frozen roster, one level in.
TELESCOPE_MAP = ".claude/skills/agda-ban-decompose/telescope-family.md"


def stage_warning(tool, why, pipeline_stage=None):
    """The banner a PIPELINE STAGE prints when it is invoked standalone.

    ⚑ WHY THIS EXISTS (user, 2026-08-01): *"the pipeline tools aren't MEANT to be
    run independently"* — and *"it would be nice if everyone stopped trying to
    run them independently; THAT needs correction."*

    A stage is written against the stages around it: `fix_stale_using` deletes a
    `public` conduit because `rewire_to_leaves` re-binds the consumers next;
    `rewire_to_leaves` errs WIDE because `prune_imports` cuts next.  Run alone,
    each looks like a bug — a risk audit of `fix_stale_using` scored "drops
    `public`" as an unrecoverable export-surface change, which is true standalone
    and false in the chain.  The tools could not say so, so every reader
    re-derived the same wrong conclusion.  Now they say it, at the moment of the
    standalone invocation, which is the only moment it lands.

    Returns the banner; callers print it rather than exiting — a standalone run
    is legitimate for inspection and repair, it just must not be MISTAKEN for the
    supported path.
    """
    head = f"⚠  {tool} is a PIPELINE STAGE, not a standalone tool."
    body = f"   {why}"
    seq = (f"   Supported path:  python3 {PIPELINE} <file> --apply"
           + (f"   (this runs as: {pipeline_stage})" if pipeline_stage else ""))
    tail = ("   Running it alone is fine for INSPECTION; if you repair with it,\n"
            "   the following stage's work is now yours to do by hand.")
    return "\n".join((head, body, seq, tail))

