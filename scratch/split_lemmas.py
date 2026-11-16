#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Split one Agda file HORIZONTALLY into a directory of lemma-per-file siblings.

⟡cap-128-forcing / ⟡no-barrels: an elaboration peak is per-MODULE, so the way
to get a fat file under the cap is to make each lemma its own elaboration unit.
The result is a DIRECTORY of siblings — never a barrel that re-exports them
(that would re-inflate every consumer's core and is banned).

UNITS.  A unit is either
  * a `module … where` block (parameterized or named) plus its indented body —
    these CANNOT be split, the telescope binds the whole block; or
  * a top-level definition: its leading comment block, its signature, and every
    following clause line until the next col-0 declaration.

IMPORTS.  Each sibling gets the original import block plus an `open import` of
every sibling whose defined names it references.  Redundant imports are
harmless; missing ones are not, so this errs wide and lets the typechecker
narrow.  Ordering across siblings is a DAG (a lemma may only use lemmas above
it in the original file), so it is acyclic by construction.

NAMES.  Agda module names are path segments, so an operator like `_⊑ᶠ_` cannot
be a filename.  Such units get a sanitized name and a header comment recording
what they actually define.
"""
import re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import agda_lex

DECL=re.compile(r"^([^\s:;{}()@|]+)\s*(?::|=)")
MODL=re.compile(r"^module\s+(\S+)")
IMP =re.compile(r"^(open\s+import|import)\s")
# A column-0 `open M …` that is NOT an import (`open Det NormPoly … using (Mat)`)
# is a FILE-SCOPED scope directive, exactly like an import: it binds names for
# the whole file.  Matching only IMP left it to the safety net, which made a
# `Preamble` unit that binds the names LOCALLY and re-exports NOTHING — so every
# sibling that used them was NotInScope (measured: `Mat`, `det` + 2 transitive in
# JacobianDetNative; `Poly`/`convCoeff`/`nth` in BezoutFold.Base, where the
# applied-import guard below could not even see the statement to refuse).
OPN =re.compile(r"^open\s+(?!import\b)")

# THE statement shape, single-sourced.  These two ran as FOUR byte-identical
# copies (twice inline in `parse`, plus `capture_demand` and `strip_using`,
# which were identical to each other).
#
# ⚑ COLUMN-0-ANCHORED ON PURPOSE — do NOT swap in `agda_lex.statements`, whose
# openers are `^\s*` (indent-tolerant).  There, an indented line CAN open a
# statement, which is right for a whole-file scan; here only a col-0 statement
# is file-scoped, and an indented one is BODY.  Widening the opener would hoist
# body lines into the shared import prelude of every leaf.  The GROUPING loop is
# the shared part (`agda_lex.group_statements`); the opener is the caller's.
def _opens(l): return bool(IMP.match(l) or OPN.match(l) or VAR.match(l))
def _continues(l):
    """Does `l` continue the col-0 statement above it?

    ⚑ DELIBERATELY the naive rule, and it is CORRECT HERE — this is the documented
    exception to "route every span through agda_lex".  It pairs with the col-0 opener
    `_opens` above: a statement here is file-scoped prelude, and EVERY indented line
    below one is its continuation, because an indented line cannot open a file-scoped
    statement.  `agda_lex._continues` additionally stops at a line opening a
    declaration, which is right for a whole-file scan and WRONG here — it releases
    indented body lines from the prelude and they become unplaced.
    MEASURED: swapping it in left 47 residue lines in Coxeter/Core.agda; the
    conservation guard caught it, which is what the guard is for.

    The general bug (an import above a parameterized `module M (a : A) … where`
    absorbing the telescope) cannot arise at this call site: the header is a col-0
    line, so `_opens` ends the prelude before `_continues` is consulted.
    """
    return l.startswith(" ") and bool(l.strip())
# A `private variable n m l : ℕ` block is a module-local GENERALISATION
# declaration: it is neither exported nor importable, so making it a unit
# ("Preamble") left every sibling that mentions `n` NotInScope no matter which
# leaf imported it.  It is preamble in the same sense an import is — hoist the
# statement into EVERY leaf.
VAR =re.compile(r"^(private\s+)?variable\b")
# ⚑ A col-0 `private` block is SCOPE, not a definition — the same class as the
# `private variable` block above, one shape over.  It was falling to the safety
# net, which glued it onto whichever unit happened to PRECEDE it: the helpers
# then landed in an arbitrary leaf (chosen by regex-miss, not by dependency) AND
# were invisible to `defined_names`, so no sibling edge was ever emitted and
# every OTHER leaf citing one went [NotInScope].  Measured over the corpus: 36
# such blocks swallowed onto NAMED units, 30 genuine cross-unit uses across 23
# files.  Give it its own unit and import it unconditionally (the `Preamble`
# treatment) — a private helper is module-local and cannot be re-exported, so
# copying the scope into every leaf is the only sound placement.
PRIV=re.compile(r"^private\b(?!\s+variable\b)")
SAFE=re.compile(r"[^A-Za-z0-9]")

# Agda names are mostly non-ASCII, and stripping to [A-Za-z0-9] turned `ℕ` and
# `_+_` into the same useless `Op`.  Transliterate the common symbols so a leaf
# module is named after what it defines.
# ORDER IS LOAD-BEARING: replacements run in sequence, so a MULTI-character
# pattern must precede any pattern that is its prefix.  `("+","Plus")` used to
# run before `("++","Append")`, so `_++_` came out `PlusPlus` and Append was
# dead.  Same for ⁻¹ before ¹.
TRANSLIT=[("++","Append"),("⁻¹","Inv"),
          ("ℕ","Nat"),("ℤ","Int"),("ℚ","Rat"),("𝟘","Zero"),("𝟙","One"),
          ("≟","Dec"),("≡","Eq"),("≈","Approx"),("≤","Le"),("≥","Ge"),
          ("<","Lt"),(">","Gt"),("∸","Monus"),("^","Pow"),("+","Plus"),
          ("*","Times"),("∷","Cons"),("⊔","Max"),("⊓","Min"),
          ("∘","Comp"),("×","Prod"),("⊎","Sum"),("→","To"),
          # Boolean / lattice / algebraic operator glyphs.  Without these a
          # whole family collapsed to one stem: ∧-comm and ∨-comm both
          # sanitized to `Comm`, so the leaf was named `Comm`/`Comm2` and the
          # operator — the load-bearing half of the name — was lost.
          ("∧","And"),("∨","Or"),("¬","Not"),("⇔","Iff"),("⊕","Oplus"),
          ("⊗","Otimes"),("∙","Dot"),("∣","Divides"),("⊑","Sqsub"),
          ("⊆","Subset"),("⊥","Bot"),("⊤","Top"),("≢","Neq"),
          # side/variant markers: these are what distinguish ˡ from ʳ forms.
          ("ˡ","L"),("ʳ","R"),("ᵇ","B"),("ᵗ","T"),("ᵈ","D"),("ᵍ","G"),
          ("ᶠ","F"),("ⁿ","N"),("ᴳ","G"),("²","2"),("³","3"),("₁","1"),
          ("₂","2"),("₃","3"),("₄","4")]

def sanitize(n,used):
    # `-` and `_` are WORD SEPARATORS in Agda names; stripping them ran the
    # segments together (`or-xor-and` -> `Orxorand`).  Split, transliterate and
    # capitalize each segment, then join — this reproduces the hand-chosen leaf
    # names (`ReconIsCons`, `VecUncons`, `PopcountOrAnd`, `AndDistribLOr`).
    out=[]
    for part in re.split(r"[-_]+", n):
        if not part: continue
        t=part
        for a,b in TRANSLIT: t=t.replace(a,b)
        t=SAFE.sub("",t)
        if t: out.append(t[0].upper()+t[1:])
    s="".join(out) or "Op"
    # A leaf name may not START with a digit (`0∸n` -> `0Monusn` is not a legal
    # module path segment).  Spell the leading digit.
    _D={"0":"Zero","1":"One","2":"Two","3":"Three","4":"Four",
        "5":"Five","6":"Six","7":"Seven","8":"Eight","9":"Nine"}
    if s[0].isdigit(): s=_D[s[0]]+s[1:]
    b=s;i=2
    while s in used: s=f"{b}{i}";i+=1
    used.add(s);return s

def parse(path):
    lines=open(path).read().split("\n")
    mi=next(i for i,l in enumerate(lines) if MODL.match(l))
    opt=next(l for l in lines if l.startswith("{-# OPTIONS"))
    modname=MODL.match(lines[mi]).group(1)
    # Collect imports STATEMENT-aware.  Taking heads only (`[l for l in lines
    # if IMP.match(l)]`) silently dropped every leading import's `renaming (…)`
    # continuation — the names bound by that clause then vanished from every
    # generated sibling.
    imports=[]
    # Body starts after the LEADING import block only.  Taking the last import
    # in the WHOLE file silently discarded everything above a mid-file import
    # (2096 of 2165 lines here) — an Agda import is file-scoped wherever it
    # sits, so mid-file ones hoist into the shared list and the rest is body.
    last=mi; i=mi+1
    while i<len(lines):
        l=lines[i]
        if IMP.match(l) or OPN.match(l) or VAR.match(l):
            # consume the WHOLE statement: a trailing `renaming (…)` continuation
            # of the last leading import otherwise lands in the body as an
            # orphan line with no owning unit.
            imports.append(lines[i]); i+=1
            while i<len(lines) and _continues(lines[i]):
                imports.append(lines[i]); i+=1
            last=i-1
        elif not l.strip() or l.lstrip().startswith("--"): i+=1
        else: break
    # A mid-file import statement spans its indented continuations; hoist the
    # WHOLE statement, or the orphaned `using (…)` tail lands in the body.
    # ⚑ An `open X` whose X is declared IN THIS FILE (a record/data/module
    # defined here) is NOT a prelude line — it is a BODY line that must stay
    # BELOW its declaration.  Hoisting it into the shared import block puts the
    # `open` above the `record`, and every leaf then fails scope-checking with
    # [NoSuchModule].  MEASURED on Substrate.Algebra.Q: `record ℚ` + `open ℚ
    # public` produced `Q/Denominator.agda` with `open ℚ public` at :18 and the
    # record's own leaf imported below it — isolate-check exit 42, "No module ℚ
    # in scope".  A file-scoped IMPORT can hoist; an open of a LOCAL name cannot.
    local_decls = set()
    for l in lines:
        mo = re.match(r"^(?:data|record|module)\s+([^\s({:]+)", l)
        if mo: local_decls.add(mo.group(1))
    def _hoistable_open(l):
        mo = OPN.match(l)
        if not mo: return False
        rest = l[mo.end():].strip().split()
        return not (rest and rest[0].split(".")[0] in local_decls)
    # ⚑ RECORD the true file line of each body line as it is appended. `body` is
    # NOT contiguous from `last+1`: a MID-FILE import and its indented
    # continuations are hoisted out into `imports`, so every later body index is
    # short by however many lines were hoisted, and any computed offset
    # (`last+2+i`) drifts by exactly that much. MEASURED: 15 of 151 barrels
    # mis-numbered — Z30JointGenViaProduct drifts 8 lines from its 7-line
    # mid-file import, reporting the residue text correctly under a line number
    # pointing at an import argument. Capstone has no mid-file import, which is
    # why validating on it alone showed nothing.
    body=[];bodyln=[];j=last+1
    while j<len(lines):
        if IMP.match(lines[j]) or _hoistable_open(lines[j]) or VAR.match(lines[j]):
            imports.append(lines[j]);j+=1
            while j<len(lines) and _continues(lines[j]):
                imports.append(lines[j]);j+=1
        else:
            body.append(lines[j]);bodyln.append(j+1);j+=1
    # The `private`-block rewrite (see PRIV below) is the ONE place a unit's
    # emitted text differs from the text it consumed, so the conservation guard
    # — a multiset difference over line TEXT — cannot see it.  Record both halves
    # of the rewrite so the guard can reconcile them explicitly rather than
    # reporting a correctly-placed block as unplaced residue.
    dropped_private=[]   # the `private` keyword lines, deliberately dropped
    dedented=[]          # the block bodies, emitted at a smaller indent
    units=[];fixities=[];i=0
    while i<len(body):
        l=body[i]
        if not l.strip() or l.lstrip().startswith("--"):
            # a comment block belongs to the unit that follows it
            j=i
            while j<len(body) and (not body[j].strip() or body[j].lstrip().startswith("--")): j+=1
            if j>=len(body):
                # a trailing comment block owns no following unit; it belongs
                # to the last one (dropping it is silent deletion)
                if units: units[-1][1].extend(body[i:j])
                break
            pre=body[i:j];i=j;l=body[i]
        else: pre=[]
        if l.startswith(" "):
            # a stray indented line continues the PREVIOUS unit; skipping it
            # deleted clause bodies whose head the scan had already consumed.
            # `pre` TOO: an INDENTED comment block (inside a `private`/`where`
            # block) is collected by the comment scanner above, and appending
            # only `l` dropped it — 19 lines in V4-Coxeter, caught by the
            # conservation guard.  Same silent-deletion shape the other
            # branches already carry a `pre` for.
            if units: units[-1][1].extend(pre+[l])
            i+=1; continue
        if PRIV.match(l):
            # consume the block: the `private` line plus its indented body
            j=i+1
            while j<len(body) and (not body[j].strip() or body[j].startswith(" ")): j+=1
            # trim trailing blanks back off the block
            while j-1>i and (not body[j-1].strip()): j-=1
            # ⚑ DROP the `private` keyword and DEDENT the body.  `private` is not
            # exportable across a module boundary, so a leaf that kept it would
            # emit a correct sibling edge and STILL fail [NotInScope] (measured
            # on TraceDescent/StepStrict: the edge was right, the name invisible).
            # The keyword was protecting the MONOLITH's namespace; once the block
            # is its own module the leaf IS the encapsulation, so the keyword has
            # nothing left to do.  Dedent by the block's own minimum indent so
            # nested `where`/data bodies keep their relative shape.
            # ⚑ The rewrite is INVISIBLE to the conservation guard, which compares
            # line TEXT as a multiset — so record the ORIGINAL lines in the unit's
            # ledger and the REWRITTEN ones for emission.  Dropping the keyword
            # without this would report the whole block as unplaced residue.
            blk=body[i+1:j]
            ind=min((len(x)-len(x.lstrip()) for x in blk if x.strip()),default=0)
            ded=[x[ind:] if x.strip() else x for x in blk]
            dropped_private.append(body[i])                    # the `private` line
            dedented+= [(x[ind:],x) for x in blk if x.strip()] # (emitted, original)
            # ⚑ A `private` BLOCK IS A CONTAINER, NOT A UNIT — and emitting it as one
            # leaf called `Private` REPRODUCES the very defect the split exists to
            # remove.  MEASURED: of 96 `private` blocks tree-wide, **61 hold 2+
            # definitions**, so `Private.agda` was a MULTI-DEFINITION leaf; and the
            # name says nothing about what is in it, so the 8 such leaves already on
            # disk collide in meaning across unrelated files.
            # The keyword is already dropped and the body dedented (above), which is
            # exactly the shape the ordinary top-level scanner expects — so RECURSE:
            # each definition inside becomes its own unit, named for ITSELF.
            # ⚑ `private` is a POLICY question, not just a shape one (user,
            # 2026-08-01): *"there should be no more requirement for private blocks,
            # since nothing should be 'public'"*.  `private` narrows an over-wide
            # module surface; under one-definition-per-file there is no surface to
            # narrow, so a hidden helper is simply a SECOND definition that wants its
            # own file.  `check_private_ratchet` censuses the debt (226 keys); THIS
            # is the codegen that pays it down.
            # Cut the dedented block the same way the top-level branches do: a
            # definition owns its signature line plus every following indented or
            # blank line, up to the next column-0 declaration.
            sub, k, first = [], 0, True
            while k < len(ded):
                if not ded[k].strip() or ded[k].startswith(" "):
                    if sub: sub[-1][1].append(ded[k])
                    elif ded[k].strip(): sub.append(["Private", [ded[k]]])
                    k += 1; continue
                nm = re.match(r"^(?:data|record)\s+([^\s({:]+)", ded[k]) or \
                     re.match(r"^([^\s:()]+)\s*:", ded[k])
                if nm:
                    sub.append([nm.group(1), (pre if first else []) + [ded[k]]])
                    first = False
                elif sub:
                    sub[-1][1].append(ded[k])          # a further clause of the same def
                else:
                    sub.append(["Private", (pre if first else []) + [ded[k]]]); first = False
                k += 1
            units.extend(sub if sub else [["Private", pre + ded]])
            i=j; continue
        m=MODL.match(l)
        if m:
            j=i+1
            while j<len(body) and (not body[j].strip() or body[j].startswith(" ")): j+=1
            units.append([m.group(1).strip("_") or "Anon",pre+body[i:j]]);i=j;continue
        r=re.match(r"^(?:data|record)\s+([^\s({:]+)",l)
        if r:
            # a data/record declaration + its indented constructors/fields.
            # The signature regex never matched these (`data X : Set where` has
            # `data` as its first token), so they were SILENTLY DROPPED — six of
            # them, until the conservation check below caught it.
            j=i+1
            while j<len(body) and (not body[j].strip() or body[j].startswith(" ")): j+=1
            while j-1>i and not body[j-1].strip(): j-=1
            units.append([r.group(1),pre+body[i:j]]);i=j;continue
        d=DECL.match(l)
        if d:
            name=d.group(1); j=i+1
            def cont(x):
                # a CLAUSE of the same definition: `f a b = …` / `f (suc n) = …`.
                # Matching only the signature regex here dropped every clause whose
                # LHS takes arguments, silently emptying one-line units.
                if not x.strip() or x.startswith(" "): return True
                t=x.split()
                if not t: return False
                if t[0]==name: return True
                # a COPATTERN clause leads with the FIELD, not the def:
                # `head (bar r) = …` belongs to `bar`.  Match that SHAPE only —
                # "any line mentioning the name" also swallowed the NEXT
                # definition's signature (which cited this def in its type),
                # separating that signature from its own clauses.
                return bool(re.match(r"^\S+\s+\(\s*"+re.escape(name)+r"[\s)]",x))
            while j<len(body) and cont(body[j]): j+=1
            # trim trailing blanks/comments back to the owning unit
            while j-1>i and (not body[j-1].strip()): j-=1
            units.append([name,pre+body[i:j]]);i=j;continue
        fx=re.match(r"^(infix[lr]?)\s+(\d+)\s+(.+)$",l)
        if fx:
            # H1: a fixity decl is a col-0 line DECL never matched, so it fell
            # into the PREVIOUS unit — declaring fixity for operators that leaf
            # does not define (Agda rejects that).  Park it; `split()` re-emits
            # one fixity line into each leaf that actually defines a named op.
            fixities.append((fx.group(1),fx.group(2),fx.group(3).split()))
            # its comment block still belongs to a unit — parking the fixity
            # without `pre` was itself a silent deletion (guard caught it)
            if pre:
                if units: units[-1][1].extend(pre)
                else: units.append(["Preamble",list(pre)])
            i+=1; continue
        # SAFETY NET: an unrecognised col-0 line continues the previous unit
        # rather than vanishing.  Every silent deletion so far came from this
        # `i+=1` fall-through.
        if units: units[-1][1].extend(pre+[l])   # `pre` too — dropping the
        else: units.append(["Preamble",pre+[l]]) # accumulated comment block
                                                 # was itself a silent deletion
        i+=1
    # APPLIED-IMPORT GUARD.  `split()` HOISTS every import to the top of EVERY
    # leaf.  That is sound for a plain import, but a PARAMETERIZED import whose
    # ARGUMENTS are names defined in this file —
    #   open import …Coxeter.ListPresentation Gen Canonical-V4 c-ε insert … public
    # — cannot be hoisted: in the leaf that defines `Gen` it lands ABOVE the
    # `data Gen`, and in every other leaf it references names that leaf does not
    # have.  Splitting V4-Coxeter this way produced a leaf whose own definition
    # was NotInScope.  The fix is not a hoist order but a restructure (the
    # application becomes its own leaf, ordered after its arguments — the
    # applied-open class), so REFUSE rather than emit a broken split.
    # ⚑ THE GUARD'S OWN HAZARD REQUIRES ≥2 LEAVES, AND IT WAS FIRING ON 1.
    # Its stated failure is "in the leaf that DEFINES `Gen` it lands ABOVE the
    # `data Gen`, and in every OTHER leaf it references names that leaf does not
    # have" — both halves presuppose a SPLIT.  A single-unit file emits one leaf
    # that is the whole file, so the application cannot be misplaced relative to
    # anything: there is no other leaf, and the ordering is unchanged.
    # MEASURED via the tool's own parser: **22 of the 76 blocked files are 1
    # unit** — the refusal was blocking a NO-OP, and those 22 need no
    # restructurer at all.  (405 units across the 76; 16 files carry 10+.)
    if len(units) < 2:
        local_defs = set()
    else:
        local_defs = set()
        for _n, _blk in units:
            local_defs |= defined_names(_blk)
    for _st in imports:
        _t = _st.split()
        if len(_t) < 3:
            continue
        # ARITY-AWARE.  `open import M a b` puts args at 3; a bare `open M a b`
        # (the OPN class) puts them at 2 — slicing at 3 unconditionally SKIPPED
        # the first argument, so an application whose first argument is
        # file-local slipped past this refusal.
        _args = _t[3:] if (_t[0] == "open" and _t[1] == "import") else _t[2:]
        _bad = [a for a in _args
                if a in local_defs and a not in ("using", "renaming", "hiding", "public", "as")]
        if _bad:
            raise SystemExit(
                f"REFUSING to split {path}: APPLIED import references file-local "
                f"name(s) {_bad} —\n    {_st.strip()}\n"
                "  Hoisting it into every leaf is unsound (it would precede the "
                "definition it applies).\n"
                "  Restructure the application into its own leaf first "
                "(the applied-open class).")

    # CONSERVATION: every non-blank body line must land in exactly one unit.
    # Without this the splitter DELETES whatever its regexes fail to match —
    # which it did, silently, to six `data`/`record` declarations.
    kept=[l for u in units for l in u[1] if l.strip()]
    kept+=[f'{k} {p} '+' '.join(ops) for k,p,ops in fixities]
    # Reconcile the `private`-block rewrite: the emitted block carries DEDENTED
    # lines, so restore the originals in the comparison set, and account for the
    # deliberately-dropped `private` keyword by re-adding it.  Both halves are
    # recorded at the rewrite site, so this reconciliation is exact — not a
    # blanket exemption that would let a real deletion through.
    if dropped_private:
        for emitted,original in dedented:
            if emitted in kept:
                kept.remove(emitted); kept.append(original)
        kept+=dropped_private
    orig=[l for l in body if l.strip()]
    residue=[]
    if sorted(kept)!=sorted(orig):
        # ⚑ "I cannot place these lines" is NOT a reason to refuse the split, and
        # NEVER a reason to drop them.  The guard exists so nothing vanishes
        # silently; it discharges that duty by RECORDING the unplaced lines with
        # their provenance (source module + original 1-based line number), not by
        # aborting.  A barrel is the pure case: zero definitions, so EVERY body
        # line is unplaceable prose — under the old refusal such a file could
        # never be split at all, which is exactly backwards (a barrel is the
        # module most in need of dissolving).
        # ⚑ The line number MUST be the one in the FILE, not the index within
        # `body` — `body` starts at `last+1` (after the leading import block), so
        # numbering it from 1 reports a line that does not exist at that number.
        # Provenance you cannot look up is not provenance: the whole point of the
        # residue file is that a reader can go back to the original and see the
        # lines in context.
        _kept=list(kept)
        for i,l in enumerate(body):
            if not l.strip(): continue
            if l in _kept: _kept.remove(l)          # multiset difference
            else: residue.append((bodyln[i], l))    # the RECORDED line, not a computed offset
    # ⚑ THE HEADER IS BODY TOO, WHEN THERE ARE NO LEAVES.  `parse` never puts the
    # pre-module header in `body`, so conservation cannot see it — fine for a file
    # WITH definitions (each leaf gets its own generated header, and the original
    # is legitimately superseded).  But a BARREL has zero units, so the header IS
    # the entire document: 55 lines of tower summary and gap-closure table on
    # Algebra.Module.Capstone, silently dropped by a deletion that reported
    # "6 unplaced lines" and preserved only the trailing comment.  When nothing
    # survives to carry it forward, the header is unplaced content like any other.
    if not units:
        for i,l in enumerate(lines[:mi]):
            if l.strip(): residue.append((i+1, l))
        # ⚑ COMMENTS INTERLEAVED BETWEEN IMPORTS are lost by BOTH collectors: the
        # leading-import loop skips them (`elif ... startswith("--"): i+=1`) and
        # the body loop never sees them, because they sit inside the import
        # region. In a file with definitions that is harmless (they annotate
        # imports the leaves inherit wholesale); in a BARREL they are the entire
        # documentation of what each conduit is FOR — e.g. AES.agda's "AI-8 —
        # GF(2⁸) is a field." labelling each re-export. MEASURED: 37 of 151
        # barrels carried such comments, all silently dropped.
        placed={ln for ln,_ in residue}
        impset={l for l in imports}
        for i,l in enumerate(lines[mi:], start=mi+1):
            if not l.strip() or i in placed: continue
            if l in impset or l.strip().startswith("module "): continue
            if l.lstrip().startswith("--"): residue.append((i, l))
        residue.sort()
    return modname,opt,imports,units,fixities,residue

def capture_demand(imports):
    """Record `module -> {names}` from the monolith's OWN `using` lists BEFORE
    they are stripped (F30).

    ⚑ THE MONOLITH KNOWS SOMETHING THE LEAVES CANNOT RECOVER. When two imports
    overlap — `Foundation.Vec using (Vec; []; _∷_; map; tabulate)` and
    `Foundation.List using (List; []; _∷_; _++_)` — the `using` lists say which
    module each shared name was wanted FROM. `strip_using` then deletes both
    filters (the ban forbids them), every leaf inherits both bare imports, and
    a List-only leaf is `[AmbiguousName]` on `_++_`.
    A token scan cannot repair this after the fact: `[]` is a real hit for both
    modules, and provision overlap is symmetric, so guessing drops the wrong one
    (measured, F29 — 13 of 20 leaves broke). The demand declaration is the only
    non-guessing evidence, and it exists ONLY at this moment. Capture it here.
    """
    demand={}
    for st in agda_lex.group_statements(imports, _opens):
        if not IMP.match(st[0]): continue
        txt=" ".join(x.strip() for x in st)
        # ⚑ IMP captures only the KEYWORD ("open import" / "import"), not the
        # module name — parse the name separately or every statement collapses
        # onto one bogus key.  A module name may contain `-` and `'`.
        mm=re.match(r"^\s*(?:open\s+import|import)\s+([\w.'-]+)", st[0])
        u=re.search(r"\busing\s*\(([^)]*)\)",txt)
        if not (mm and u): continue
        mod=mm.group(1)
        names={t for t in re.split(r"[;\s]+",u.group(1)) if t}
        if names: demand.setdefault(mod,set()).update(names)
    return demand


def strip_using(imports, _conduits=None):
    """Drop `using (…)` filters; dedupe.  ⟡public-policy: the ban forbids
    `using` on Substrate imports, and definition-per-file is the precondition
    that makes a bare import correct.  A stale `using` naming something its
    module no longer exports is only a WARNING — the name silently fails to
    bind and surfaces far away as NotInScope, which is exactly how the
    Axes/S4 breakage presented.  `renaming`/`as` are left alone: removing
    them requires rewriting use sites (the separate tree-wide sweep)."""
    out=[];seen=set()
    if _conduits is None: _conduits=[]
    for st in agda_lex.group_statements(imports, _opens):
        txt=" ".join(x.strip() for x in st)
        # ⚑ CAPTURE THE CONDUIT BEFORE EITHER STRIP.  The `using (…)` is removed
        # a few lines below and the `public` a few lines after that, so a capture
        # placed after them sees neither and reports every conduit as
        # whole-surface (`*`).  Read the statement while it is still intact.
        _pub_owner=_pub_names=None
        # ⚑ MASK COMMENTS BEFORE TESTING FOR `public`.  `\bpublic\b` over raw text
        # matches the word in a TRAILING COMMENT, and `group_statements` folds a
        # following comment line into the preceding statement — so a comment can even
        # leak ACROSS statements.  MEASURED: 88 import statements tree-wide are read as
        # re-export conduits purely because a nearby comment says "public"
        # (`S5/S5EEA.agda`: `open import …Foundation.Eq  -- the DivStr interface, re…`).
        # Each false positive makes this strip a `public` that was never there and
        # RECORD a conduit that does not exist, which the caller then reports as a
        # contagion site for consumers to rewire.
        #
        # ⚑ NO IMPORT-VS-LOCAL EXEMPTION (user, 2026-07-31).  This site used to require
        # `IMP.match`, exempting `open <LocalRecord> public` on the reasoning that
        # re-exporting a locally-declared record's field projections is "only what it
        # defines".  Two things retire that:
        #   * THE GATE ALREADY DISAGREES.  `check_public_ratchet`'s census counts BOTH
        #     kinds — 386 of its 557 keys are local-record re-exports.  So the exemption
        #     made this tool contradict the very gate it exists to serve.
        #   * IT IS NOT WORTH ITS COMPLEXITY.  The cost of dropping it is that a consumer
        #     writes a few more import lines; the cost of keeping it is a distinction
        #     every tool in the chain has to carry and can get wrong.
        # `is_public_open` makes no such distinction, which is now the point.  MEASURED:
        # 265 local statements join the 169 module conduits; 88 comment-only false
        # positives are excluded by the masking it does.
        if agda_lex.is_public_open(txt):
            _m=re.search(r"^\s*open\s+import\s+(\S+)",txt)
            _u=re.search(r"using\s*\(([^)]*)\)",txt)
            if _m:
                _pub_owner=_m.group(1)
                _pub_names=[t for t in re.split(r"[;\s]+",_u.group(1)) if t] if _u else None
        # ⟡public-policy bans `using` on an IMPORT, not on `open M` — and on an
        # applied `open M args using (…)` the filter is the only thing naming
        # what the application brings in.  Stripping it there is both outside
        # the ban and a silent scope change, so OPN statements are exempt.
        if (not OPN.match(st[0])) and "renaming" not in txt and "hiding" not in txt:
            txt=re.sub(r"\s*using\s*\([^)]*\)","",txt).rstrip()
        # ⚑ A `public` on an IMPORT is a RE-EXPORT CONDUIT: it makes this module
        # export names it does not define.  After a split there must be no
        # re-exports at all — a leaf holds ONE definition and re-exports exactly
        # what it defines, nothing more.  The parent's import prelude is copied
        # into EVERY leaf, so leaving `public` on it does not merely preserve the
        # conduit, it MULTIPLIES it: one conduit becomes N.  Strip it here.
        # ⚑ NOT the same as `open <LocalRecord> public` (an OPN statement, exempt
        # above): that re-exports the field projections of a record DECLARED in
        # this file — which IS "only what it defines".  The distinction is
        # import-vs-local, not the `public` keyword.
        # ⚑ AND RECORD IT.  Stripping the conduit is only half the move: the
        # parent PROVIDED those names to the rest of the tree, and every
        # consumer reaching one THROUGH the parent must be rewired to bind at
        # the owner (the P3 contagion).  Dropping the keyword silently leaves
        # those consumers pointing at a name nothing exports any more — Agda
        # reports that as a WARNING at the import and a far-away `[NotInScope]`
        # at the use site, so it surfaces long after the split, in a module the
        # splitter never touched, and gets hand-patched.
        # MEASURED: `GL3F2/GaugeGenerators.agda` re-exported `singer-Linear`
        # from `Algebra.F2.FanoPlane`; the split stripped it and two consumers
        # (`MultiRouteEquivariance/SingerInv`, `…/SingerGL`) broke.
        # So collect (owner, names) here and let the caller rewire them.
        if IMP.match(st[0]):
            if _pub_owner: _conduits.append((_pub_owner,_pub_names))
            txt=re.sub(r"\s+public\b","",txt).rstrip()
        if txt not in seen: seen.add(txt); out.append(txt)
    return out

# ⚑ MULTI-NAME CONSTRUCTOR SIGNATURES.  Agda lets several constructors share
# one signature — `_⊕E_ _⊗E_ _⊖E_ : Expr → Expr → Expr` (JacobianExpr) and
# `S K I : Tm` (the SKI/Trace family) — and capturing only the first token lost
# the rest, so a fixity naming the 2nd or 3rd was silently dropped.  MEASURED:
# after the DATAHDR fix this was the SOLE remaining cause, 9 drops over 7 files.
# `agda_defs.def_index:62` already solved exactly this shape for the tree-wide
# index; this is that pattern, not a third variant of it.
# ⚑ AND THE LEADING CHARACTER CLASS WAS ASCII-ONLY — the same class this arc
# retired in eight other regexes, surviving in the ONE place that decides what a
# leaf EXPORTS.  `[A-Za-z_]` rejects `𝟘`, `𝟙`, `ε`, `·-comm`, `0≢1`, `[]ᴾ` — so
# `defined_names` returned `{F₂}` for `data F₂ where 𝟘 𝟙`, `provides` never held
# the constructors, and no sibling edge to the carrier was ever computed.
# MEASURED LIVE: the F2 split emitted `OneNeqZero`/`ZeroNeqOne` (whose bodies are
# `𝟙≢𝟘 : 𝟙 ≡ 𝟘 → ⊥`) with NO import of their own carrier leaf — isolate-check
# [NotInScope] 𝟙.  MEASURED TREE-WIDE: **224 constructor/field names across 90
# files** are invisible to the old class, i.e. absent from every `-- Defines:`
# header and from every sibling-import decision that reads one.
# A leading `:` or `;` still cannot start a name, and the trailing class is
# unchanged, so multi-name signatures (`S K I : Tm`) parse exactly as before.
CTOR=re.compile(r"^\s+([^\s:;{}()@|]+(?:\s+[^\s:;{}()@|]+)*?)\s*:(?!:)")
CTORKW=re.compile(r"^\s+constructor\s+(\S+)")
# ⚑ The head's NAME stops at the first space, `(`, or `:` — a parameterized or
# explicitly-typed head is still a head.  This pattern used to be
# `^(?:data|record)\s+[^({:]+where\s*$`, whose character class EXCLUDED `(` and
# `:` and which required `where` to end the line, so it matched only the bare
# `data X where` shape.  MEASURED: 582 col-0 heads failed it across 427 files,
# hiding 1533 constructors and record fields — `data CharTerm (n : ℕ) : Set
# where` among them.  The consequences compound: the leaf's `-- Defines:`
# header omitted those names, so `rewire_to_leaves.leaf_map` could not map
# them; the sibling-edge scan emitted no import for a leaf using a sibling's
# constructor ([NotInScope] at isolate-check, F16's shape); and a fixity whose
# operator is a hidden constructor was dropped entirely (28 measured, silent —
# a dropped fixity does not error, it re-defaults to `infixl 20` and changes
# how existing expressions PARSE).
# ⚑ 197 of the 582 heads span multiple lines, so the flag must stay open until
# `where` is actually seen rather than being decided on the head line alone.
DATAHDR=re.compile(r"^(?:data|record)\s+[^\s({:]+")
def _hdr_open(l):
    """True iff L opens a data/record head whose `where` has not yet arrived.

    ⚑⚑ THE `where` TEST MUST IGNORE A TRAILING COMMENT, and not doing so made every
    constructor of one datatype invisible — MEASURED 2026-08-21 on
    `SKIShedDuality/Tm.agda:24`:

        data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧

    `re.search(r"\\bwhere\\s*$", l)` fails on that line because the comment follows `where`,
    so `pending_hdr` stayed True and `defined_names` skipped `S K I` and `_∙_` as "still in
    the head's telescope". The seed then emitted a leaf importing `Cost` and `Shed` and NOT
    `.Tm` — a leaf that had never typechecked, found only when a peer's rewire made it
    reachable and the build asked for it.

    ⚑ THE COMMENT IS A SHAPE HASH THIS ARC MINTS, which is what makes it not an edge case:
    `⟦shape:…⟧` is written onto `data`/`record` heads BY THIS TOOLCHAIN, so the annotation
    that records a declaration's identity was the thing that hid its constructors from the
    splitter. Every head carrying one has the same blindness.

    ⚑ AND THE DOCSTRING ABOVE `defined_names` CLAIMED THIS CLASS WAS FIXED. It was, for the
    indented-constructor half; this is the head-line half, and a probe showed `Shed.agda`
    (no trailing comment) returning `shed⟨_⟩` and `peeled` correctly while `Tm.agda` returned
    only `Tm`. Two files, one function, opposite results — the difference was a comment.
    """
    if not DATAHDR.match(l):
        return False
    # Mask a trailing `--` comment before asking where the line ENDS. Everything else in this
    # module masks comments first (`defined_names` skips comment lines outright); this
    # predicate did not, and it is the one that decides whether constructors are read.
    code = l.split("--", 1)[0] if "--" in l else l
    return not re.search(r"\bwhere\s*$", code)

def defined_names(block):
    # A `data X : Set where` / `record X : Set where` header is column-0; its
    # CONSTRUCTORS (and a `record`'s `constructor` line) are indented and were
    # invisible here (`l.startswith(" ")` skips every indented line), so the
    # "-- Defines:" header — and every consumer of it (rewire_to_leaves.py's
    # leaf-owner map) — never learned `true`/`false` belong to their `data Bool`
    # leaf.  Same class as the earlier agda_defs.py indented-head blind spot,
    # one layer down: the type name was visible, its inhabitants were not.
    ns=set()
    in_data=False
    pending_hdr=False   # inside a multi-line head, before its `where`
    for l in block:
        if not l.strip(): continue
        # ⚑ A COMMENT BANNER PARSED AS A DEFINITION.  `DECL` matched the leading
        # `--` of `------------------------------------------------------------`
        # (name `--`, "type" the rest), so `--` entered `local_defs` and the
        # applied-import guard REFUSED TO SPLIT over it.
        # MEASURED: `Algebra/F2/FromBool.agda` refused with
        # `APPLIED import references file-local name(s) ['--']` — a comment, not a
        # name. 3 of the 79 blocked files are this false positive; the other 76
        # cite real identifiers (`cap-Z₃`, `m-lo₄`, …) and are the genuine class.
        # Every other scanner in the tree masks comments first; this one did not.
        if l.lstrip().startswith("--"): continue
        if not l.startswith(" "):
            in_data=bool(DATAHDR.match(l))
            pending_hdr=_hdr_open(l)
            m=MODL.match(l)
            if m: ns.add(m.group(1)); continue
            d=DECL.match(l)
            if d: ns.add(d.group(1))
            r=re.match(r"^(?:data|record)\s+([^\s({:]+)",l)
            if r: ns.add(r.group(1))
            continue
        if pending_hdr:
            # Still in the head's own telescope/type — `(n : ℕ)` and `: Set`
            # are NOT constructors. Only once `where` lands does the indented
            # region become the constructor block.
            if re.search(r"\bwhere\s*$", l): pending_hdr=False
            continue
        if in_data:
            m=CTOR.match(l)
            if m:
                for nm in m.group(1).split(): ns.add(nm)
                continue
            m=CTORKW.match(l)
            if m: ns.add(m.group(1))
    return ns


FIELDKW = re.compile(r"^\s+field\b")


def field_names(block):
    """Record FIELD names — projections a consumer imports BY NAME.

    ⚑ MEASURED GAP, same class as the constructor one fixed above, one layer
    deeper.  `record _~_ … where` / `  field head~ : …` puts the field under an
    indented `field` KEYWORD, so `CTOR` (which expects the name at the data
    block's own indent) never saw it and `-- Defines:` listed only `_~_`.
    Consequence, observed live on the Bisim split: six consumers importing
    `head~` went **UNMAPPED** in `rewire_to_leaves`, because no leaf claimed to
    define it — yet `head~` is a projection of `_~_` and travels with it.
    Tree-wide only 12 of 686 `-- Defines:` headers mention any field.

    A field IS an exported name (`open Op` brings `head~` into scope), so it
    belongs in the header for the same reason constructors do.
    """
    ns, in_fields, depth = set(), False, 0
    for l in block:
        if not l.strip():
            continue
        ind = len(l) - len(l.lstrip())
        if FIELDKW.match(l):
            in_fields, depth = True, ind
            # `field x : A` on one line
            rest = l.split("field", 1)[1]
            m = re.match(r"\s+([^\s:;{}()@|]+(?:\s+[^\s:;{}()@|]+)*?)\s*:(?!:)", rest)
            if m:
                for nm in m.group(1).split(): ns.add(nm)
            continue
        if in_fields:
            # a field line is indented DEEPER than the `field` keyword
            if ind > depth:
                m = re.match(r"^\s+([^\s:;{}()@|]+(?:\s+[^\s:;{}()@|]+)*?)\s*:(?!:)", l)
                if m:
                    for nm in m.group(1).split(): ns.add(nm)
                continue
            in_fields = False
    return ns

def write_residue(outdir, path, modname, residue, apply):
    """Record body lines the splitter could not place in any leaf.

    ⚑ The conservation guard's duty is that NOTHING VANISHES SILENTLY — not
    that every line must be placeable.  Prose the parser cannot attach to a
    unit (a barrel's tower summary; a trailing closing comment with no
    following definition) is real content with no home; dropping it is a
    silent deletion, and REFUSING the split leaves the conduit standing.
    Write it out with provenance instead: source module + ORIGINAL 1-based
    line number, so a reader can put it back or re-home it deliberately."""
    if not residue: return None
    p = os.path.join(outdir, "RESIDUE.md")
    lines = [f"# Residue — {modname}",
             "",
             f"Lines the split of `{path}` could not place in any leaf.",
             "They are recorded, not discarded: each carries the line number it",
             "held in the original file. Re-home them deliberately, or delete",
             "them deliberately — but do it as a decision, not as a side effect.",
             ""]
    prev = None
    for ln, text in residue:
        if prev is not None and ln != prev + 1: lines.append("")
        lines.append(f"{ln:>5}  {text}")
        prev = ln
    lines.append("")
    out = "\n".join(lines)
    if apply:
        os.makedirs(outdir, exist_ok=True)
        with open(p, "w") as fh: fh.write(out)
    return p

def blockers(path):
    """Why this file cannot be split — [(kind, detail)], empty when it can.

    ⚑ THIS EXISTS BECAUSE EVERY CALLER WAS RE-DERIVING IT AND GETTING IT WRONG.
    The only way to ask "is this file blocked, and why" was to call `parse()`,
    catch `SystemExit`, and REGEX THE MESSAGE TEXT.  So a census of the blocked
    population is a hand-rolled reimplementation of `local_defs` — and mine
    disagreed with the tool on **50 of 79 files**, because it scanned column-0
    signatures while the tool unions `defined_names` over the parsed units.
    A module that refuses must be able to SAY WHY in data, or every consumer
    re-implements the predicate and drifts (user: *"don't hand-roll shit — the
    tooling is meant to be modular"*).

    Returns [] for a splittable file, so `if blockers(p): …` reads correctly.
    """
    try:
        parse(path)
        return []
    except SystemExit as e:
        msg = str(e)
        m = re.search(r"APPLIED import references file-local name\(s\) \[([^\]]*)\]", msg)
        if m:
            names = [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
            return [("applied-open", names)]
        return [("other", msg.splitlines()[0] if msg else "unknown")]


def split(path,outdir=None,apply=False):
    modname,opt,imports,units,fixities,residue=parse(path)
    # ⚑ THE DEMAND IS CAPTURED HERE, BEFORE `strip_using` DESTROYS IT.  The
    # monolith's `using` lists say which module each shared name was wanted
    # FROM (`_++_` from List, never from Vec); the ban forbids carrying those
    # filters into the leaves, so the ONLY way to keep the information is to
    # SPEND it here — decide each leaf's imports at split time, while the
    # declaration is still in hand.
    #
    # The post-hoc alternative (emit every leaf with the full prelude, then let
    # `prune_imports` infer liveness back from body tokens) is UNSOUND, and not
    # by a fixable margin: `perms zero = [] ∷ []` (Perms) and `concatMapL f [] =
    # []` (ConcatMapL) present the SAME token observable on the discriminating
    # names, yet Perms needs Vec KEPT and ConcatMapL needs it DROPPED.  No
    # function of the token set alone separates them — the distinguishing fact
    # is the elaborated TYPE of one occurrence.  Measured: 4 of 20 Enumerate
    # leaves lost a live import that way (Perms, WordsLength, PermsLength,
    # LengthAllPositions).
    demand=capture_demand(imports)
    _owners={}
    for _m,_ns in demand.items():
        for _n in _ns: _owners.setdefault(_n,set()).add(_m)
    shared={n for n,ms in _owners.items() if len(ms)>1}
    # The conduits this split DESTROYS.  `strip_using` removes each `public`
    # re-export (P2), which also removes a name the PARENT provided to the rest
    # of the tree — so every consumer reaching that name through the parent is a
    # P3 contagion site.  The splitter cannot rewire them (they are arbitrary
    # modules elsewhere), but it MUST report them, or they surface later as a
    # far-away `[NotInScope]` in a file the split never touched.
    conduits=[]
    imports=strip_using(imports, conduits)
    outdir=outdir or path[:-5]
    used=set();named=[]
    for n,blk in units: named.append((sanitize(n,used),n,blk))
    # ⚑ FIELDS TOO.  A record's projections are exported names a consumer imports
    # by name; omitting them made `rewire_to_leaves` report UNMAPPED for every
    # importer of `head~`/`tail~` after the Bisim split (measured, 6 files).
    provides={fn:defined_names(blk)|field_names(blk) for fn,_,blk in named}
    order=[fn for fn,_,_ in named]
    # Map each PRELUDE STATEMENT to the module it imports, so a leaf can decline
    # the ones it does not need.  A statement spans its indented continuations;
    # keying on the head line alone would strip a `renaming (…)` tail off the
    # line it belongs to.  Only plain IMPORT statements are filterable: an `open
    # M args` application and a `private variable` block are SCOPE, not a name
    # source, and every leaf keeps them unconditionally.
    pre_mod=[]
    for st in agda_lex.group_statements(imports, _opens):
        mm=re.match(r"^\s*(?:open\s+import|import)\s+([\w.'-]+)",st[0]) if IMP.match(st[0]) else None
        pre_mod.append((mm.group(1) if mm else None, st))
    files={};need={}
    for idx,(fn,orig,blk) in enumerate(named):
        # ⚑ THE UNIT'S TOKENS ARE NOT THE LEAF'S TOKENS.  Every leaf also receives the
        # UNCONDITIONAL prelude — the `private variable` blocks and `open M args`
        # applications kept as SCOPE (`mod is None` below).  Those lines are real code
        # in the emitted file and their names must be resolvable there, but they were
        # never added to `toks`, so the import that TYPES them was judged unneeded and
        # declined.
        #
        # MEASURED (Foundation.Eq): the monolith hoists `private variable a b c : Level`
        # and imports `Substrate.Foundation.Level using (Level; _⊔_)`.  Twelve of the
        # thirteen leaves carry that variable line, none writes the token `Level` in its
        # own block, so all twelve declined the import and failed [NotInScope] Level.
        # Only `EqReasoning` survived — because its unit text happens to say
        # `module ≡-Reasoning {a : Level} where` outright.
        #
        # The scope lines are part of the leaf, so they contribute demand like any other
        # line.  (They cannot recurse: `_scope_text` covers only statements with no
        # module of their own, which are exactly the ones never filtered.)
        _scope_text=" ".join(l for mod,st in pre_mod if mod is None for l in st)
        text=" ".join(blk)
        toks=set(re.findall(r"[^\s(){}\[\];,]+",text+" "+_scope_text))
        # a QUALIFIED use `M.f` references the sibling that defines the module
        # `M`; without the prefix the sibling-import edge is invisible.
        toks |= {t.split(".")[0] for t in list(toks) if "." in t}
        # H2: an INFIX use contributes the bare symbol (`+`), not `_+_`, so an
        # operator-mediated sibling edge was invisible (Times->Plus, Pow->Times,
        # Lt->Le, Le2->Le, Lt2->{Le2,Lt} were all silently missing).
        # ⚑ H2 covered only the INFIX section `_x_`.  A PREFIX operator (`¬_`,
        # used as `¬ A`) or a POSTFIX one (`_!`) contributes the same bare
        # symbol, so the same edge was still invisible one section over:
        # measured on Foundation.Negation, `Dec`'s `no : ¬ A → Dec A` never
        # imported its `Not` sibling and failed isolate-check [NotInScope] ¬.
        # Reconstruct all three sections, not just infix.
        toks |= {f for t in list(toks) for f in ("_"+t+"_", t+"_", "_"+t)}
        # ⚑ H2b: a BRACKET-DELIMITED mixfix (`[_,_]`, `⟨_⟩`, `⌊_⌋`) is shredded
        # by the tokenizer's OWN delimiter set — `[`, `]` and `,` are separators
        # above, so `[_,_]` can never appear as a token and the edge is invisible
        # BY CONSTRUCTION, no matter how the sections are reconstructed. H2 fixed
        # the symbolic operator (`_+_` used infix as `+`); this is the same defect
        # one section over, for names whose sections ARE delimiters.
        # MEASURED: Foundation.Sum split into Op (`[_,_]`) + Op2 (`[_,_]′`, whose
        # body is literally `[_,_]`); Op2 emitted no edge to Op and failed
        # isolate-check [NotInScope] `[_,_]`.
        # FIX: for each sibling name, scan the RAW block text for the name
        # VERBATIM. The negative lookahead stops `[_,_]` matching merely as the
        # prefix of `[_,_]′` — without it every primed variant would import its
        # unprimed sibling spuriously (and vice versa is already impossible,
        # since the longer name cannot occur inside the shorter).
        def _verbatim(nm):
            # scope lines included for the same reason `toks` includes them: they are
            # emitted into this leaf, so a name they mention is demanded by this leaf.
            return re.search(re.escape(nm) + r"(?![\w'′″-])",
                             text + " " + _scope_text) is not None
        sibs=[o for o in order[:idx]
              if (provides[o] & toks) or any(_verbatim(n) for n in provides[o])]
        # A `Preamble` leaf holds `private variable` blocks, whose bound names
        # (`ℓ`, `ℓ′`) `defined_names` cannot see — so `provides` is empty and no
        # sibling ever imported it, leaving every leaf that mentions `ℓ`
        # NotInScope.  It is scope, not a definition: import it unconditionally.
        if "Preamble" in order[:idx] and "Preamble" not in sibs:
            sibs=["Preamble"]+sibs
        # A `Private` leaf holds a col-0 `private` block.  Its names are
        # module-local, so `defined_names` cannot see them and no sibling edge is
        # ever computed — the same blindness `Preamble` has, for the same reason
        # (scope, not a definition).  Import it unconditionally.
        if "Private" in order[:idx] and "Private" not in sibs:
            sibs=["Private"]+sibs
        # ── the leaf's own import decision ────────────────────────────────
        # A module is NEEDED here if any name the monolith declared it wanted
        # FROM that module occurs in this unit's tokens, or if a sibling this
        # leaf imports needs it.  The sibling term is load-bearing and is what
        # the post-hoc prune could not see: `perms : (n : ℕ) → List (Perm n)`
        # never writes the token `Vec`, but it imports the sibling `Perm`,
        # whose body IS `Vec (Fin n) n`.  Because `sibs ⊆ order[:idx]`, every
        # sibling's need is already final — one forward pass, no fixpoint.
        #
        # An operator is `_∷_` in a using-list and bare `∷` at an infix use
        # site, so probe every section (the same reconstruction `toks` does).
        # ⚑ ONLY UNIQUELY-OWNED NAMES ARE DIRECT EVIDENCE.  `[]` and `_∷_` are
        # claimed by BOTH Vec and List in the monolith's own using-lists, so a
        # hit on them says nothing about which module THIS leaf meant — that is
        # the ambiguity the whole exercise is about.  Judge on the names exactly
        # one module claimed (`_++_` → List; `map`/`tabulate` → Vec).
        #
        # Subtracting shared names is safe HERE, and was not safe in the
        # post-hoc prune, because a leaf that needs a shared name reaches its
        # owner through the SIBLING term below rather than through this one.
        # Empty direct evidence is therefore not a death sentence, only silence.
        # ⚑ THE THIRD mixfix-reconstruction site (the other two are
        # `prune_imports` and `agda_defs`), hand-inlined here and subtly WRONG:
        # it emitted `""` for a name that strips to nothing (`__`), and the empty
        # string is a substring of every token, so a single such name in a
        # using-list made EVERY module read as needed.  `agda_lex.mixfix_forms`
        # carries the guard; use the authority rather than a fourth copy of it.
        direct={m for m,ns in demand.items()
                if any(p in toks
                       for n in ns - shared
                       for p in agda_lex.mixfix_forms(n))}
        need[fn]=direct.union(*(need[s] for s in sibs)) if sibs else direct
        # UNKNOWN PROVISION ⇒ KEEP.  A module the monolith imported BARE (no
        # `using`) declared nothing, so there is no evidence either way and the
        # only sound move is to keep it — absence of evidence is not evidence
        # of death.  That asymmetry is the whole reason this is emitted here
        # rather than inferred later.
        prelude=[l for mod,st in pre_mod
                 if mod is None or mod not in demand or mod in need[fn]
                 for l in st]
        defines=", ".join(sorted(provides[fn])) or orig
        hdr=["-"*72,
             f"-- {modname}.{fn}",
             "--",
             f"-- Defines: {defines}",
             "-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally",
             f"-- out of {modname}; no barrel re-exports these siblings).",
             "-"*72,"",opt,"",f"module {modname}.{fn} where",""]
        mine=[f"{k} {p} "+" ".join(o for o in ops if o in provides[fn])
              for k,p,ops in fixities if any(o in provides[fn] for o in ops)]
        body=hdr+prelude+[f"open import {modname}.{s}" for s in sibs]+[""]+mine+[""]+blk
        files[os.path.join(outdir,fn+".agda")]="\n".join(body).rstrip()+"\n"
    rp = write_residue(outdir, path, modname, residue, apply)
    if rp:
        print(f"# RESIDUE: {len(residue)} unplaced line(s) -> {rp}")
    # Report the DESTROYED conduits (see `conduits` above).  Machine-readable so
    # the pipeline can rewire the downstream consumers instead of waiting for a
    # far-away `[NotInScope]`: one `# CONDUIT: <owner> <name> …` line per
    # re-export the split removed.  A conduit with no `using` list re-exported
    # the owner's WHOLE surface, printed as `*`.
    for owner, names in conduits:
        print(f"# CONDUIT: {owner} " + (" ".join(names) if names else "*"))
    if apply:
        os.makedirs(outdir,exist_ok=True)
        for p,t in files.items(): open(p,"w").write(t)
        os.remove(path)
    return files,named

def _selftest():
    """Counted — a hardcoded total once hid an added case (prune_imports.py:332).

    End-to-end through `split()` on a temp file, because the defects this pins are
    EMISSION defects: they are invisible in any single helper and only appear in what
    the leaf file actually contains.
    """
    import tempfile, shutil
    cases=[]
    def check(name,got,want): cases.append((name,got==want,got,want))

    # ⚑ THE SCOPE-IMPORT REGRESSION.  A hoisted `private variable a b c : Level` is
    # copied into EVERY leaf, but the token scan read only the leaf's own unit block,
    # so no leaf "used" `Level` and all of them declined `Foundation.Level`.
    # MEASURED on the real Foundation.Eq: 12 of 13 leaves failed [NotInScope] Level;
    # only EqReasoning survived, because its unit text says `{a : Level}` outright.
    mono=("{-# OPTIONS --safe --without-K #-}\n\n"
          "module M where\n\n"
          "open import Substrate.Foundation.Level using (Level; _⊔_)\n"
          "open import Substrate.Foundation.Empty using (⊥)\n\n"
          "private variable a b c : Level\n\n"
          "sym : {A : Set a} {x y : A} → x ≡ y → y ≡ x\n"
          "sym refl = refl\n\n"
          "neq : {A : Set a} → A → A → Set a\n"
          "neq x y = x ≡ y → ⊥\n")
    d=tempfile.mkdtemp()
    try:
        p=os.path.join(d,"M.agda")
        open(p,"w",encoding="utf-8").write(mono)
        files,named=split(p,apply=False)
        by={os.path.basename(k):v for k,v in files.items()}
        # `sym` mentions neither Level (only via the variable block) nor ⊥.
        sym=next(v for k,v in by.items() if k.startswith("Sym"))
        check("a leaf carrying the hoisted `variable` block IMPORTS its type's module",
              "Substrate.Foundation.Level" in sym, True)
        # ...and the filter still WORKS: `sym` does not use ⊥, so it must not import it.
        check("an unrelated import is still declined (the filter is not disabled)",
              "Substrate.Foundation.Empty" in sym, False)
        # ...while the leaf that does use ⊥ keeps it.
        neq=next(v for k,v in by.items() if k.startswith("Neq"))
        check("a leaf that DOES use the name keeps that import",
              "Substrate.Foundation.Empty" in neq, True)
        check("every leaf gets the scope block itself",
              all("private variable" in v for v in by.values()), True)
    finally:
        shutil.rmtree(d,ignore_errors=True)

    # ⚑ NON-ASCII CONSTRUCTORS — the sibling edge to the CARRIER.  `CTOR`'s leading
    # class was `[A-Za-z_]`, so `𝟘`/`𝟙` were not in `defined_names`, so
    # `provides["F2"]` held only `F₂`, so a leaf whose ONLY mention of the carrier is
    # `𝟙 ≡ 𝟘` in its SIGNATURE computed no edge and emitted no import.
    # MEASURED LIVE on the real Substrate.Algebra.F2 split: `OneNeqZero.agda` and
    # `ZeroNeqOne.agda` failed isolate-check [NotInScope] 𝟙.  Tree-wide the old class
    # hid 224 constructor/field names across 90 files.
    # ⚑ The fixture uses the ABSURD-PATTERN shape on purpose: `𝟙≢𝟘 ()` mentions the
    # constructors in the type and NOWHERE in the body, so a body-token test passes it
    # while the real defect stands.  A case whose leaf also used them in a term would
    # have gone green against the broken class and proved nothing.
    mono2=("{-# OPTIONS --safe --without-K #-}\n\n"
           "module N where\n\n"
           "open import Substrate.Foundation.Empty using (⊥)\n\n"
           "data F₂ : Set where\n"
           "  𝟘 : F₂\n"
           "  𝟙 : F₂\n\n"
           "𝟙≢𝟘 : 𝟙 ≡ 𝟘 → ⊥\n"
           "𝟙≢𝟘 ()\n")
    d2=tempfile.mkdtemp()
    try:
        p2=os.path.join(d2,"N.agda")
        open(p2,"w",encoding="utf-8").write(mono2)
        files2,_=split(p2,apply=False)
        by2={os.path.basename(k):v for k,v in files2.items()}
        carrier=next((k[:-5] for k in by2 if "𝟘" in by2[k] and "data F₂" in by2[k]),None)
        check("a non-ASCII constructor is a DEFINED name of its carrier leaf",
              carrier is not None, True)
        leaf=next((v for k,v in by2.items() if "≢" in v and "data F₂" not in v),None)
        check("a leaf using constructors ONLY in its signature imports the carrier sibling",
              leaf is not None and ("import N." + (carrier or "?")) in leaf, True)
    finally:
        shutil.rmtree(d2,ignore_errors=True)

    # ⚑ A `private` BLOCK IS A CONTAINER, NOT A UNIT.  It was emitted as ONE leaf
    # called `Private`, which reproduced the defect the split exists to remove:
    # MEASURED, 61 of 96 `private` blocks tree-wide hold 2+ definitions, so
    # `Private.agda` was a MULTI-DEFINITION leaf — and the name says nothing about
    # its contents, so the 8 already on disk collide in meaning across unrelated
    # files.  Each definition now becomes its own unit, named for ITSELF.
    # The conservation guard is what makes this safe to change: it refuses unless
    # every non-blank line lands in exactly one unit, so a mis-cut block cannot
    # ship silently.
    mono3=("{-# OPTIONS --safe #-}\n\n"
           "module P where\n\n"
           "open import Substrate.Foundation.Eq\n\n"
           "private\n"
           "  helper-a : Set → Set\n"
           "  helper-a x = x\n\n"
           "  helper-b : Set → Set\n"
           "  helper-b x = x\n\n"
           "main-thing : Set → Set\n"
           "main-thing x = x\n")
    d3=tempfile.mkdtemp()
    try:
        p3=os.path.join(d3,"P.agda")
        open(p3,"w",encoding="utf-8").write(mono3)
        f3,_n3=split(p3,apply=False)
        base3={os.path.basename(k)[:-5] for k in f3}
        check("each def in a `private` block becomes its OWN leaf (not one `Private`)",
              ("Private" not in base3) and len(base3)>=3, True)
        check("...and the leaves are named for the DEFINITIONS",
              {b for b in base3 if b.lower().startswith("helper")} != set(), True)
        # the emitted leaf must NOT re-emit the keyword: `private` is not exportable
        # across a module boundary, so a leaf that kept it would fail [NotInScope].
        check("the `private` keyword is not re-emitted into any leaf",
              any("private" in v for v in f3.values()), False)
    finally:
        shutil.rmtree(d3,ignore_errors=True)

    # ⚑ THE COMMENT BANNER THAT PARSED AS A DEFINITION.  `DECL` matched the
    # leading `--` of a `-----…` separator (name `--`, "type" the rest), so `--`
    # entered `local_defs` and the applied-import guard REFUSED TO SPLIT over a
    # COMMENT.  MEASURED: `Algebra/F2/FromBool.agda` refused with
    # `file-local name(s) ['--']`; after the fix it splits into 7 leaves.
    check("a comment banner is not a definition",
          defined_names(["-"*60, "-- prose", "foo : Set"]), {"foo"})

    # ⚑ `blockers()` EXISTS SO NOBODY RE-DERIVES THE PREDICATE.  The only way to
    # ask "why is this blocked" was to catch SystemExit and regex the message —
    # so my census hand-rolled `local_defs` and disagreed with the tool on 50 of
    # 79 files.  A module that refuses must say why IN DATA.
    d4=tempfile.mkdtemp()
    try:
        okp=os.path.join(d4,"Ok.agda")
        open(okp,"w",encoding="utf-8").write(
            "{-# OPTIONS --safe #-}\n\nmodule Ok where\n\nfoo : Set → Set\nfoo x = x\n")
        check("blockers() returns [] for a splittable file", blockers(okp), [])
    finally:
        shutil.rmtree(d4,ignore_errors=True)

    # ⚑ THE TELESCOPED-ROOT DECLINE.  A parameterized root produced `0 lemma
    # file(s)` and exit 0 — INDISTINGUISHABLE from "already atomic".  Five such
    # roots (19 leaves) were therefore split BY HAND, which is how they acquired
    # the import-position defect `hoist_telescope_imports.py` repairs.  The
    # diagnosis lives in `__main__` (it is an operator-facing message), so what is
    # testable here is the PREDICATE it keys on: `agda_lex.telescope_span` must
    # separate a parameterized root from an ordinary one.  Stated plainly rather
    # than pretending the exit path itself is covered.
    import agda_lex
    check("a telescoped ROOT is detected (the decline's predicate)",
          agda_lex.telescope_span("{-# OPTIONS #-}\nmodule M (W : Set)\n  (_+_ : W → W → W)\n  where\nx = 1\n")
          is not None, True)
    check("a plain root is NOT mistaken for one",
          agda_lex.telescope_span("{-# OPTIONS #-}\nmodule M where\nx = 1\n"), None)
    # ⚑⚑ AND THE EXIT PATH IS NOW COVERED — the comment above admitted it was not,
    # and that gap is exactly what shipped. The decline was guarded on `not files`,
    # so it fired ONLY when the split produced zero units. A telescoped root is not
    # usually unsplittable: MEASURED on `Cyclic/Base.agda` (`module … (n : ℕ)`,
    # ten imports ABOVE the header), `split()` emitted 13 leaves and exited 0, and
    # the `Power` leaf failed `[NotInScope] ℕ` because neither the parameters nor
    # the above-header imports travelled. The predicate was right; the QUESTION was
    # "did we produce nothing?" when it should have been "is this our shape?".
    #
    # ⚑ A PREDICATE TEST IS NOT A DISPATCH TEST. Pinning `telescope_span` alone let
    # a correct predicate sit behind a wrong guard for five roots / 19 leaves.
    # ⚑ THE PARAMETER LIST SPANS LINES — `telescope_span` returns None for a
    # single-line `module M (n : ℕ) where`, which is a NARROWER predicate than the
    # decline needs and is worth knowing: `Cyclic/Base.agda`'s header IS one line
    # (`module Substrate.Groups.Coxeter.Cyclic.Base (n : ℕ) where`), so the guard
    # I just wrote would NOT have caught the very file that motivated it.
    _tel = ("{-# OPTIONS #-}\nopen import Substrate.Foundation.Nat.Nat\n"
            "module M (n : ℕ)\n  where\nx : ℕ\nx = n\ny : ℕ\ny = x\n")
    _td = tempfile.mkdtemp()
    _tp = os.path.join(_td, "M.agda")
    open(_tp, "w", encoding="utf-8").write(_tel)
    _tfiles, _ = split(_tp, apply=False)
    check("⚑⚑ a telescoped root PRODUCES units (so `not files` never fired)",
          len(_tfiles) > 0, True)
    check("...and is detected, so the decline must key on the SHAPE not the count",
          agda_lex.telescope_span(_tel) is not None, True)

    # ⚑⚑⚑ THE DECLINE'S ROUTING INFORMATION, PINNED AS TEXT — because the richer half
    # of this message was UNREACHABLE and no test noticed.  Until 2026-08-26 a SECOND
    # telescoped-root decline sat below the live one, guarded on `_span is not None`
    # under `if not files:` — which the live branch's `sys.exit(3)` had already made
    # impossible.  It was the ONLY place naming `hoist_telescope_imports` and R7b.
    # ⚑ SO THE REPO'S ONE WORKING REACHABILITY MECHANISM — a refusal that names its
    # successor (`hook_structural_query` names the owning tool; `gate_census`'s ABSENT
    # rows name `--init-absent --apply`) — was HALF DEAD in this family's only refusal.
    # ⚑ AND THE COMMENT ABOVE SAYS WHY IT SURVIVED: *"the diagnosis lives in `__main__`
    # … so what is testable here is the PREDICATE"*.  A predicate test cannot see a
    # dead print.  Pinning the STRINGS is what makes the successor-naming load-bearing;
    # the source is read rather than the branch executed, because the branch exits.
    _src = open(__file__, encoding="utf-8").read()
    for _needle in ("split_telescoped.py", "hoist_telescope_imports.py", "TELESCOPE_MAP"):
        check(f"the telescoped-root decline still NAMES `{_needle}`",
              _src.count(_needle) > 0, True)
    check("...and there is exactly ONE telescoped-root decline (no dead second copy)",
          # ⚑ the needle is BUILT, never written whole: a literal spelled here would
          # occur in this very file and make the census count its own test.
          _src.count('print("   ' + "⚠ TELESCOPED ROOT"), 1)

    ok=sum(1 for _,g,_,_ in cases if g)
    for name,good,got,want in cases:
        if not good: print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"split_lemmas selftest: {ok}/{len(cases)}")
    return 0 if ok==len(cases) else 1


if __name__=="__main__":
    if "--selftest" in sys.argv: sys.exit(_selftest())
    # ⚑ THE POPULATION IS A COMMAND, NOT A SNIPPET.  `blockers()` was built so a
    # census would stop re-deriving `local_defs` by hand (it disagreed with the tool
    # on 50 of 79 files), and then had NO CLI — so every later question about the
    # size of the applied-open class went back through a `python3 -c` loop over
    # `agda_files`.  A number quoted in a worklist ages; a command re-measures.
    # Grouped by KIND, because "54 files" is a size and "which shapes block them"
    # is the thing that decides whether a restructurer is one transform or several.
    if "--blocked" in sys.argv:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import agda_lex
        by_kind, nfiles = {}, 0
        for p in agda_lex.agda_files("agda"):
            b = blockers(p)
            if not b:
                continue
            nfiles += 1
            for kind, detail in b:
                by_kind.setdefault(kind, []).append((p, detail))
        for kind, rows in sorted(by_kind.items(), key=lambda kv: -len(kv[1])):
            print(f"{len(rows):>5}  {kind:<16} e.g. {rows[0][0]}  {rows[0][1]}")
        print(f"{nfiles} file(s) blocked; "
              f"{sum(len(v) for v in by_kind.values())} blocker(s) in "
              f"{len(by_kind)} kind(s)")
        sys.exit(0)
    src=sys.argv[1]; ap="--apply" in sys.argv
    if ap:
        # ⚑ Snapshot before the first write (edit_snapshot.py).  A split DELETES the
        # tip module, so an unrecoverable bad split loses the original outright.
        import edit_snapshot
        edit_snapshot.guard(f"split_lemmas {src}", [src])
    files,named=split(src,apply=ap)
    # ⚑ ZERO FILES IS TWO DIFFERENT ANSWERS AND THIS PRINTED THE SAME LINE FOR BOTH.
    # "nothing to split" (already atomic) and "this SHAPE is out of scope" both
    # exited 0 with `0 lemma file(s)`, so a caller — including split_pipeline and
    # every sweep built on it — could not tell a no-op from a decline.
    # MEASURED: `Groups/Coxeter/Core.agda` is a TELESCOPED ROOT (a parameterized
    # `module M (…) where` whose body is the whole file).  Its top-level defs are
    # perfectly splittable; they simply need the telescope carried onto each leaf
    # and the leaf re-applied at the root.  Nothing here does that, so the file
    # reported `0` and five such roots (19 leaves) were split BY HAND instead —
    # which is exactly how they acquired the import-position defect R7a repairs.
    # Say which case this is; a silent decline is how a whole shape stays invisible.
    # ⚑⚑ THE DECLINE WAS GUARDED ON `not files` AND THEREFORE ALMOST NEVER FIRED.
    # A telescoped root is not usually UNSPLITTABLE — `split()` happily carves it
    # into units and emits them WITHOUT the telescope's parameters or the imports
    # that sit ABOVE the module header. So the guard only caught the degenerate
    # case (zero units) and waved through every telescoped root that produced any.
    #
    # MEASURED on `Groups/Coxeter/Cyclic/Base.agda` — `module … Base (n : ℕ) where`
    # with ten imports ABOVE the header. It emitted 13 leaves and exited 0; the
    # `Power` leaf then failed `[NotInScope] ℕ`, and I diagnosed it three times as
    # a seed-too-small bug in the import filter before reading the parent and
    # finding the real shape. The tool KNEW this case (the message below spells it
    # out) and asked the wrong question about when to say so.
    #
    # ⚑ THE PREDICATE MUST PRECEDE THE SPLIT, NOT POST-MORTEM IT. `split_telescoped`
    # is the tool that models this shape; `split_lemmas` must DECLINE and name it,
    # which is the boundary between the two — previously undeclared, so each tool
    # grew its own import-seed computation and only one of them was right here.
    import agda_lex
    from agda_imports import TELESCOPE_MAP   # THE family back-edge; never restate the roster
    _span = agda_lex.telescope_span(open(src, encoding="utf-8", errors="replace").read())
    # ⚑⚑⚑ THE REFUSAL'S OWN ROUTING INFORMATION WAS UNREACHABLE, WHICH IS THIS
    # FAMILY'S DEFECT IN ITS OWN DECLINE MESSAGE.  Until 2026-08-26 the branch above
    # `sys.exit(3)`d, and a SECOND, STRICTLY MORE DETAILED telescoped-root decline sat
    # below under `if not files:` — guarded on `_span is not None`, which the exit had
    # already made impossible.  It was the only place that named `hoist_telescope_imports`
    # and R7b, so the two facts a reader most needs — WHY the hand-split is unsafe, and
    # WHICH tool repairs the damage if they do it anyway — were printed by nothing.
    # ⚑ A REFUSAL IS THIS REPO'S REACHABILITY MECHANISM (`hook_structural_query` names the
    # owning tool; `gate_census`'s ABSENT rows name `--init-absent --apply`), so a decline
    # whose successor-naming half is dead is a routing edge that silently does not exist.
    # The two messages are now ONE, printed on the live path.
    if _span is not None:
        print(f"{len(files)} lemma file(s) NOT written from {src}")
        print("   ⚠ TELESCOPED ROOT — refusing. Use `split_telescoped.py`, which")
        print("     models this shape; this tool would emit leaves missing both the")
        print("     parameters and the above-header imports the telescope needs.")
        print("     This file's module header carries a parameter list, so every leaf")
        print("     must RE-DECLARE the parameters it uses and the root must re-open")
        print("     each leaf applied to them.  That is not yet generated here (R7b);")
        print("     splitting it BY HAND is what produced the import-position defect")
        print("     `hoist_telescope_imports.py` exists to repair — so if you hand-split,")
        print("     run that tool afterwards.")
        print(f"   Family map: {TELESCOPE_MAP}")
        sys.exit(3)
    if not files:
        print(f"0 lemma file(s) from {src}   (already atomic — nothing to split)")
        sys.exit(0)
    print(f"{len(files)} lemma file(s) from {src}")
    # ⚑ THE TOOL KNEW THE PATHS AND THREW THEM AWAY.  `files` is keyed BY PATH, yet
    # `--apply` printed only a COUNT — so "which files did this run write?" had no
    # answer, and verifying R9 took FIVE reconstructions, each wrong in its own way:
    # `git status` A/?? (most leaves were already untracked), `git cat-file -e
    # pre-r9:` (a stash snapshot CANNOT hold untracked files, so it reported
    # 89 modified / 0 new for a run that wrote 589), a glob under the output dirs
    # (which also holds earlier splits' leaves), and finally file MTIMES.
    # Four of those produced a CONFIDENT WRONG VERDICT — one of them "88% failure,
    # serious regression" on a population that was mostly not this tool's output.
    # If the tooling cannot answer a question directly, the answer gets
    # reprocessed out of its side effects, and every consumer reprocesses it
    # differently (user, 2026-08-01).  `--manifest` prints the paths, one per line.
    if "--manifest" in sys.argv:
        for k in sorted(files): print(k)
    elif not ap:
        for fn,orig,blk in named[:20]: print(f"   {fn:28s} <- {orig}  ({len(blk)} lines)")
