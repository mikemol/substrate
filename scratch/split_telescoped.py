#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Split a TELESCOPED ROOT into telescoped leaves — the generator `split_lemmas` declines.

⚑ FAMILY MAP (every sibling splitter/repair and the precondition that selects it):
    .claude/skills/agda-ban-decompose/telescope-family.md   (agda_imports.TELESCOPE_MAP)
This docstring already names `split_lemmas` and `hoist_telescope_imports` below, which
is the behaviour the standing rule wants; the map is the edge that reaches the SIBLINGS
those two do not mention (`split_inner_module`, `topup_leaves`, `prune_leaf_opens`,
`telescope_migrate*`, `recover_presplit`), none of which any tool named.

THE SHAPE.  `split_lemmas` refuses a parameterized module in writing (`:10-11`: *"a `module …
where` block (parameterized or named) plus its indented body — these CANNOT be split, the
telescope binds the whole block"*).  That refusal is correct for an INNER block treated as one
unit, but it left a whole class with NO generator at all: a file whose OWN module header carries
a telescope has perfectly splittable top-level definitions — they simply need the telescope
carried onto each leaf.

MEASURED: **5 telescoped roots / 19 telescoped leaves**, recursive (`Coxeter/Core` →
`Core/HigherArity` → its own leaves).  All 19 were split BY HAND, which is exactly why they
acquired the import-position defect `hoist_telescope_imports.py` repairs — there was no
generator to get it right.

THE GROUND TRUTH, read off the hand-split leaves rather than invented:

    root  Coxeter/Core.agda            9 parameters
    leaf  Core/NormalizeAppend/Left    7 — drops `ε-in` and `++-assoc`
                                           (verified 0 occurrences in its body)
    root re-opens each leaf APPLIED    `open import …NormalizeAppend  Word _++_ Canonical …`

So a leaf takes the MINIMAL SUBSET its body uses, and the root re-opens it applied to exactly
those arguments.  Both halves matter: a leaf that took the whole telescope would force every
consumer to supply parameters it does not need, and a root that did not re-apply would break
every downstream name.

⚑ SELECTION IS A CLOSURE, NOT A SCAN.  A parameter is needed if the body mentions it OR if an
already-needed parameter's TYPE mentions it — `Left` never writes `Word` in a term, but
`(Canonical : Word → Set)` does, so `Word` must come along.  Iterate to fixpoint.

⚑ AND AN OPERATOR HAS TWO SPELLINGS.  `_++_` is written `++` at an infix use site, so probing
only the declared spelling drops it: my first selection returned 6 of 7 parameters for `Left`,
missing exactly `_++_`.  That is the two-spelling hazard `rename_at_source` already documents.
Probing both spellings reproduces the hand-split telescope EXACTLY (7/7, in order).

    split_telescoped.py <file>              # report the plan
    split_telescoped.py <file> --apply      # write leaves + rewrite the root
"""
import re, os, sys

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import agda_lex                       # THE telescope / span authority; never re-derive
import split_lemmas as _sl            # THE unit scanner + name sanitiser
import split_inner_module as _sim     # THE inner-module unit reader (Ⓐ1)
import prune_imports as _pi           # THE keep-or-drop predicate (Ⓐ1¹²)

_SNAPPED = []


def _snapshot_once(path):
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        edit_snapshot.guard('split_telescoped', [path])
    except Exception as e:
        print(f"   ⚠ snapshot unavailable ({e}) — recover via git if needed")


def spellings(name):
    """Every way `name` can be written at a use site.

    `_++_` appears as `++` infix, `++_`/`_++` as sections.  Probing only the
    declared form is how the first selection lost `_++_` (6 of 7 parameters).
    """
    bare = name.strip("_")
    if not bare:
        return {name}
    return {name, bare, f"_{bare}_", f"{bare}_", f"_{bare}"}


def _mentions(text, names):
    return any(re.search(r"(?<![\w'-])" + re.escape(s) + r"(?![\w'-])", text)
               for n in names for s in spellings(n))


def needed_params(body, groups):
    """The MINIMAL subset of `groups` this body needs, closed over parameter types."""
    sel = set()
    changed = True
    while changed:
        changed = False
        probe = body + " " + " ".join(groups[j][1] for j in sorted(sel))
        for i, (names, _txt) in enumerate(groups):
            if i not in sel and _mentions(probe, names):
                sel.add(i)
                changed = True
    return [groups[i] for i in sorted(sel)]


def _balanced(text):
    """Are `()` `{}` balanced outside comments — the cheapest incoherence test.

    ⚑ DELIBERATELY SHALLOW. This is not a parser and must never be the reason a
    CORRECT split is refused; it exists only so that syntactically impossible
    output cannot be written while the tool reports `WROTE`. It catches the one
    defect measured live: a wrapped `using (…)` list truncated to its head, leaving
    an unclosed paren in all 22 leaves.
    """
    d = 0
    for ch in agda_lex.mask_comments(text):
        if ch in "({":
            d += 1
        elif ch in ")}":
            d -= 1
            if d < 0:
                return False
    return d == 0


def _emit_blockers(leaves, prelude=()):
    """Reasons NOT to write — checked BEFORE any file is created.

    ⚑ THE GATE THE LIVE APPLY DID NOT HAVE. It wrote 22 files, each with an
    unclosed paren, and printed `WROTE` twenty-two times. A generator that cannot
    detect impossible output is one whose success message carries no information —
    and the operator's standing rule is that the gate is the layer that can refuse,
    not the prose that describes the policy.

    ⚑ THE PRELUDE IS PART OF WHAT IS CHECKED, AND MY FIRST CUT OMITTED IT. The
    measured truncation lands in the INHERITED PRELUDE, not in any leaf's own
    block — so a gate reading only `blk` would have passed all 22 defective files.
    A gate that cannot see the defect it was built for is the census-green shape:
    check the text as ASSEMBLED, which is what actually reaches disk.
    """
    out = []
    pre = "\n".join(prelude)
    for leaf, _params, _defines, blk in leaves:
        if not _balanced(pre + "\n" + "\n".join(blk)):
            out.append(f"{leaf}: unbalanced delimiters in the emitted leaf")
    return out


def localize_variables(body_lines, blk, leaf):
    """Ⓡ8 — ([renamed variable decls], [rewritten blk]) with LEAF-LOCAL names.

    ⚑ THE COLLISION IS NAME-IDENTITY AND NOTHING ELSE. Two `variable n : ℕ`
    declarations in one scope are `[AmbiguousName]`; two differently-named ones are
    not. `AntiDiagSum` inherited four `m`s because four siblings each declared `m`
    — give each leaf its own spelling and the four are four distinct variables.

    ⚑ AND THE NAMES NEVER ESCAPE, which is why this is free at the boundary. A
    generalisable variable is elaborated away: `x-shift`'s exported type is
    `∀ {n} → Poly n → Poly (suc n)` whatever the source called it, so no consumer
    of any leaf can tell. The 16 importers of `Defs` see identical types.

    ⚑ WHY `module Over` IS NOT THE ANSWER, though the tree uses it. The existing
    shards (`Laws/Linear.agda:46`, `Conv.agda:52`) carry byte-identical blocks
    without colliding because each sits inside its own `module Over` — that does
    not AVOID the collision, it HIDES it in a scope nothing can see into. The
    opacity is the thing this arc removes; citing it as proof the problem is solved
    is using the black box to justify the black box.

    ⚑ BOTH HALVES OR NEITHER. The declaration and the leaf's signatures are
    rewritten together and returned together. Renaming one and not the other is the
    split-authority error this file has recorded five times.

    ⚑ A WRITTEN BINDER IS NOT TOUCHED, and this is the sharpest trap in the source.
    `Defs.agda:91-92` mixes mechanisms — `shift-to-suc-on-left : ∀ {n'} → …` binds
    `n'` explicitly while `m` comes from the block, and the body binds both
    positionally as `{m} {n'}`, which typechecks only because generalised variables
    insert to the LEFT of written ones. Renaming a written binder would keep the
    positional binding valid while silently swapping two ℕs — still typechecking if
    `+ℕ-comm`'s arguments swap too. Only block-derived names are renamed.
    """
    names = []
    decls = []
    for raw in body_lines:
        line = raw.strip()
        if line.startswith("private "):
            line = line[len("private "):].lstrip()
        if not line.startswith("variable"):
            continue
        decl = line[len("variable"):]
        if ":" not in decl:
            continue
        lhs, rhs = decl.split(":", 1)
        ns = [t for t in lhs.split() if t]
        names += ns
        decls.append("variable "
                     + " ".join(f"{n}-{leaf}" for n in ns)
                     + " :" + rhs.rstrip())
    if not names:
        return [], list(blk)
    out = []
    for line in blk:
        for n in names:
            line = agda_lex.word(n).sub(f"{n}-{leaf}", line)
        out.append(line)
    return decls, out


def variable_telescope(body_lines):
    """Ⓡ5ᵈ — a `variable` block as IMPLICIT TELESCOPE GROUPS, one per declaration.

    ⚑ SUPPRESSION CANNOT WORK, AND THE COMPILE PROVED IT. A generalisable variable
    declared in ANY leaf propagates through every sibling edge, and the sibling
    graph is not a tree: `AntiDiagSum` imports four leaves that each rightly
    declare `variable n m k : ℕ`, so it inherits FOUR `m`s. Suppressing its own
    copy changes nothing, and no assignment of leaf-local declarations avoids it.

    ⚑ THE TELESCOPE FORM DOES NOT PROPAGATE. `variable n m k : ℕ` generalises
    per-signature and travels with every `open`; `{n m k : ℕ}` is a module
    parameter the importer APPLIES, so N sibling edges bring zero copies. Same
    names, same type — a different binder form.

    ⚑ AND THIS IS A REWRITE, NOT AN INVENTION, which matters because I claimed
    three times that synthesising binders would breach the conservation guard.
    IT WOULD NOT: `_conserve` is called once, inside `body_units`, over the UNIT
    READ — `pycodemod --calls` confirms a single call site. It never sees emitted
    output. What constrains emission is `_emit_blockers`, which checks delimiter
    balance only. So the synthesis was unguarded all along; the honest response is
    to keep every emitted binder traceable to a source declaration, which this
    does — the names and type come from the line, only the brackets are ours.
    """
    out = []
    for raw in body_lines:
        line = raw.strip()
        if line.startswith("private "):
            line = line[len("private "):].lstrip()
        if not line.startswith("variable"):
            continue
        decl = line[len("variable"):].strip()
        if ":" not in decl:
            continue
        out.append("{" + decl + "}")
    return out


def variable_binders(body_lines, blk, sibling_carries=False):
    """Ⓑ6ᶜ²⁵ — `variable` declarations this leaf's names rely on.

    ⚑ A `variable` DECLARATION BINDS FOR THE WHOLE MODULE and is invisible to
    every other pass here. The conservation walk skips `private variable n m k : ℕ`
    because the line starts with `private` — right for a private BLOCK, whose body
    the units carry, and wrong for this: it introduces implicit binders that every
    leaf's signature uses. MEASURED: `[NotInScope] n` at `Defs/PlusP.agda:24`,
    signature `Poly n → Poly n`.

    ⚑ `private` IS STRIPPED ON THE WAY OUT. A leaf has no enclosing block to be
    private to, and the ban forbids `private` besides — the declaration is carried
    for its BINDING, not its visibility.

    ⚑ PER LEAF, like every other carry: a leaf that never names `n` does not get
    it. Carrying unconditionally would rebuild the unpruned-prelude debt this arc
    has spent two clusters removing.

    ⚑ SEVENTH SHAPE OF ONE PROBLEM — carrying the root's SCOPE into a leaf. The
    others: prelude imports, telescope groups, sibling args, residue binders, alias
    rewriting. Each was found by a compile, not by design, and each is kept as its
    own named patch so the list stays legible as a record of what a module scope
    turns out to contain.
    """
    # ⚑ Ⓡ5ᵃ — A SIBLING IMPORT ALREADY BRINGS THESE, AND TWO COPIES ARE AMBIGUOUS.
    # A `variable` is GENERALISABLE, not an ordinary binding: identical
    # declarations in one scope do not merge, they collide. A leaf that imports a
    # sibling carrying the same block therefore declares nothing itself.
    # MEASURED: `Outer` declared `variable n m k : ℕ` at :37 and imported sibling
    # `C` at :39 carrying the same — `[AmbiguousName] n` at `Outer.agda:40`.
    #
    # ⚑ SUPPRESSION, NOT SYNTHESIS. The alternative — emitting `∀ {n}` into each
    # signature — would make the generator WRITE source, which the conservation
    # guard refuses by design. Every emitted line still traces to a source line.
    if sibling_carries:
        return []
    body = agda_lex.mask_comments("\n".join(blk))
    out = []
    for raw in body_lines:
        line = raw.strip()
        if line.startswith("private "):
            line = line[len("private "):].lstrip()
        if not line.startswith("variable"):
            continue
        decl = line[len("variable"):].split(":", 1)[0]
        names = [t for t in decl.split() if t]
        if any(agda_lex.word(n).search(body) for n in names):
            out.append(line)
    return out


def residue_binders(residue, blk):
    """Ⓑ6ᶜ²‴ — residue lines that BIND names this leaf uses, so must travel with it.

    ⚑ A RESIDUE LINE IS NOT ALWAYS ROOT-ONLY, AND TREATING IT SO COST A COMPILE.
    The conservation pass files `open Base.Over 𝟘 public using (Poly; nth)` as
    residue — correctly: it DEFINES nothing, so no unit owns it — and `root_text`
    keeps it in the root. But it BINDS `Poly`/`nth`, and every leaf's signature
    reads `Poly n → Poly n → Poly n`. MEASURED: `[NotInScope] Poly` at
    `Graded/Defs/PlusP.agda:22`.

    ⚑ EXPORT vs BINDER IS THE WHOLE DISTINCTION, and why this never surfaced
    before. `FromCommRing`'s sixteen `open Pₙ.Over … public` are pure RE-EXPORTS —
    no leaf refers to them — so root-only was right there. An `open X …` whose
    names APPEAR IN A LEAF is a binder and belongs in that leaf too.

    ⚑ AND IT IS PER-LEAF, LIKE THE PRELUDE PRUNE. A leaf that never says `Poly`
    must not inherit the binder; carrying it unconditionally would re-create the
    unpruned-prelude debt this arc has spent two clusters removing.

    Keep-biased: an `open` whose bound names cannot be read (no `using` list) is
    carried whenever the leaf is non-trivial, since "cannot tell" must not decide
    a drop — the same rule `should_keep` states.
    """
    body = agda_lex.mask_comments("\n".join(blk))
    out = []
    for raw in residue:
        line = raw.strip()
        if not line.startswith("open ") or line.startswith("--"):
            continue
        m = re.search(r"\busing\s*\(([^)]*)\)", line)
        if m:
            names = [t for t in re.split(r"[;\s]+", m.group(1)) if t]
            # two-spelling, as everywhere here: `_∷_` is written `∷` at a use site
            if not any(agda_lex.word(s).search(body)
                       for n in names for s in spellings(n)):
                continue
        # ⚑ `public` IS STRIPPED ON THE CARRY. The leaf needs the names IN SCOPE;
        # re-exporting them makes every leaf a second provider of `Poly`, and the
        # root — which keeps its own copy — then sees eight of them:
        # `[ClashingDefinition] Multiple definitions of Poly` at `Defs.agda:68`.
        # A carry is for BINDING, not for publishing; the ban forbids the re-export
        # besides. Same reasoning as stripping `private` from a carried `variable`.
        out.append(re.sub(r"\s+public\b", "", line))
    return out


def _close_over_siblings(leaves, groups):
    """Ⓐ1′ — widen each leaf's telescope until it can APPLY its sibling imports.

    ⚑ THE THIRD TIME THE SEED WAS TOO SMALL, AND THE FIRST TIME IT SPANS LEAVES.
    `needed_params` closes a leaf over the telescope GROUPS its own text mentions;
    `emit` then turns a reference to a sibling's name into `open import <root>.<sib>
    <that sibling's args>`. Those two ran independently, so a leaf could reference a
    sibling whose arguments it does not bind. On the live `FromCommRing`, 15 of 22
    leaves selected ZERO parameters while being handed `open import ….R A CR` —
    `module ….Zero where` with an unresolvable applied import.

    ⚑ AND IT MUST BE A FIXPOINT OVER THE LEAF GRAPH, NOT ONE PASS. The live chain
    is `𝟘 = ε +M` → `+M = +-monoid SR` → `SR = semiring R` → `R = ring CR`: four
    hops. A single sibling read widens `𝟘` by `+M`'s params — which are themselves
    still too narrow at that moment. Iterate until nothing grows.

    This is the SAME closure `needed_params` already performs, lifted one level: a
    parameter is needed if the body mentions it, OR a needed parameter's type does,
    OR a referenced SIBLING needs it. Group order is preserved so a re-declared
    telescope stays in the root's declaration order (`emit` re-emits group text
    verbatim, and a reordered telescope would not match the re-open's arg order).
    """
    idx = {i: i for i in range(len(leaves))}
    home = {n: i for i, (_l, _p, dd, _b) in enumerate(leaves) for n in dd}
    bodies = [agda_lex.mask_comments("\n".join(b)) for _l, _p, _d, b in leaves]
    sel = [{groups.index(g) for g in prm} for _l, prm, _d, _b in leaves]
    changed = True
    while changed:
        changed = False
        for i, body in enumerate(bodies):
            for n, owner in home.items():
                # ⚑ Ⓡ4 — TWO-SPELLING, AGAIN, AND IN A SECOND PROBE. `home` is
                # keyed on the DECLARED name (`_·c_`) while the use site writes it
                # BARE (`a ·c q`), so `word("_·c_")` never matched and the sibling
                # edge was invisible HERE — even though the emitter's own sibling
                # detection was taught `spellings()` in Ⓠ7. Two probes, one
                # hazard, fixed once: the classic split-authority error.
                # MEASURED: `Outer` uses `·c` at :42, so its selection never
                # absorbed `C`'s `_*_`, and the emitted sibling import applied an
                # argument `Outer` does not bind — `[NoParseForApplication]` at
                # `Outer.agda:39`.
                if owner == i or not any(agda_lex.word(s).search(body)
                                         for s in spellings(n)):
                    continue
                if not sel[owner] <= sel[i]:
                    sel[i] |= sel[owner]
                    changed = True
    return [(l, [groups[j] for j in sorted(sel[i])], dd, b)
            for i, (l, _p, dd, b) in enumerate(leaves)]


def _inner_plan(path, src, want):
    """The INNER-MODULE variant: telescope and units from `module_scopes`.

    ⚑ WHY THIS IS A SEPARATE SOURCING PATH AND NOT A CHANGE TO `_sl.parse`.
    `parse` is 156 lines behind a conservation guard that has caught SEVEN silent
    deletions; teaching it about indented units risks every one of them. The three
    things the file-header path supplies — span, units, defined-names — each have a
    correct inner-module authority already: `module_scopes`, `split_inner_module.
    body_units` (whose tail-absorption defect was just fixed), and `_sl.defined_names`
    once the unit is DEDENTED.

    ⚑ THE DEDENT IS LOAD-BEARING, NOT COSMETIC. `_sl.defined_names` skips
    `l.startswith(" ")` by construction (it reads column-0 declarations). Handed
    indented inner units it returns the EMPTY SET for every leaf, so `emit`'s
    `home{}` map is empty and NO sibling imports are emitted — silently re-creating
    the `[NotInScope] _≉_` defect `emit` exists to prevent. A guard that degrades to
    measuring nothing is worse than a crash.
    """
    scopes = [(n, i, p, s, e) for n, i, p, s, e in agda_lex.module_scopes(src)
              if p and not (i == 0 and not p)]
    if want:
        scopes = [m for m in scopes if m[0] == want]
    else:                                   # only auto-pick when unambiguous
        scopes = [m for m in scopes if m[1] > 0]
        if len(scopes) != 1:
            return None
    if not scopes:
        return None
    name, indent, _params, b0, b1 = scopes[0]
    lines = src.split("\n")
    # the inner header's own line — `module_scopes` reports the BODY span, so the
    # header sits just above it. Walk back to the `module` keyword.
    hdr = b0 - 1
    while hdr > 0 and not lines[hdr].lstrip().startswith("module "):
        hdr -= 1
    # ⚑ `telescope_groups` slices `lines[s+1:e+1]`, so the span's FIRST line is the
    # head. A single-line inner header carries head AND params together, so start
    # one line earlier (pinned in agda_lex's own selftest).
    # ⚑ Ⓒ8′: THE INNER HEADER MAY SPAN MANY LINES, and `(hdr-1, hdr)` assumed ONE.
    # That held for `FromCommRing`'s `module Over {A : Set} (CR : …) where` and I
    # pinned it with a case asserting exactly that shape — encoding the one-line
    # assumption as the contract. `Graded/Defs.agda` continues for TWELVE lines:
    #     module Over {A : Set}
    #       (_+_ : A → A → A) (_*_ : A → A → A) (𝟘 𝟙 : A)
    #       … nine laws …
    #       where
    # so the hand-computed span read `{A : Set}` alone. MEASURED: the emitter
    # reported `1 parameter` where the module declares FOURTEEN, planned 8 leaves
    # each binding only `A`, and emitted re-opens with NO arguments — 8 files whose
    # bodies use `_+_`/`𝟘`/`Poly` and bind none of them. Caught by Ⓒ8 BEFORE the
    # apply; nothing was written.
    #
    # ⚑ REUSE `head_span`, DO NOT RE-DERIVE THE WALK. It runs a header to its
    # `where` with no arbitrary continuation bound — built against a measured 401
    # multi-line headers, 136 needing more than six continuations. It returns an
    # EXCLUSIVE end index; `telescope_groups` slices `[s+1:e+1]`, so the span
    # starts AT the header line and ends one before `head_span`'s result.
    #
    # ⚑ Ⓑ6ᶜ²″: AND THE SPAN STARTS ONE LINE **BEFORE** THE HEADER, ALWAYS. The
    # slice is `lines[s+1:e+1]`, so a span starting AT `hdr` skips the header line
    # — and `module Over {A : Set}` carries a binder group right there. Starting at
    # `hdr` read 13 of 14 groups on `Graded/Defs.agda`: every continuation line but
    # not the implicit, so leaves were emitted as `(_+_ : A → A → A)` with `A`
    # unbound. My first cut special-cased the single-line header with `(hdr-1, hdr)`
    # and used `(hdr, _hend)` for the multi-line one — two rules where the slice
    # semantics demand ONE. `_hend` is the header's LAST line either way.
    _hend = agda_lex.head_span(lines, hdr) - 1
    groups = agda_lex.telescope_groups(src, span=(hdr - 1, max(_hend, hdr)))
    units = _sim.body_units(lines, b0, b1, indent)
    out, used = [], set()
    # ⚑ Ⓐ1⁴ — STATEMENTS, NOT LINES. `IMP.match(l)` matches only a statement's
    # HEAD, so a wrapped `using (…)` list lost its tail and every leaf got an
    # unclosed paren (measured: all 22, and the tool said `WROTE`). `imports` must
    # therefore carry whole statements; `body_prelude` folds continuations via
    # `group_statements` and is the authority — feed it, do not re-derive it.
    _imports = []
    for _st in agda_lex.group_statements(lines[:hdr], _sl._opens):
        if _sl.IMP.match(_st[0]):
            _imports += [l.rstrip() for l in _st]
    prelude_txt = "\n".join(_imports)

    # ⚑ Ⓑ6ᶜ²⁴ — THE CONSERVATION PASS IS HOISTED ABOVE THE UNIT LOOP. It depends
    # only on `units` and `lines`, both already in hand, so this is a pure MOVE
    # rather than a restructure — and it has to happen first, because a residue
    # line that will TRAVEL WITH a leaf is part of that leaf's closure seed.
    # (The algorithm is `split_lemmas.parse`'s multiset difference; see the ⚑ at
    # `_residue`'s original site below for why it is reused rather than re-derived.)
    _emitted = [l for _u, _b, _p in units for l in _b if l.strip()]
    _residue = []
    for i in range(b0, min(b1 + 1, len(lines))):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("private"):
            continue
        if raw in _emitted:
            _emitted.remove(raw)          # multiset difference, as parse does
        else:
            _residue.append((i + 1, raw))

    # ⚑ AND A CARRIED RESIDUE LINE MUST BE REWRITTEN LIKE AN IMPORT. The root
    # reaches `Graded.Base` through `import … as Base`, so its residue says
    # `Base.Over`. `_bare()` correctly rewrites each leaf's IMPORTS to bare form,
    # which unbinds `Base` — and the carried line then failed `[NoSuchModule] No
    # module Base.Over in scope`. One rule (imports go bare) applied to the import
    # half and not the carried-text half: the SAME split-authority error as the
    # wrapped-import truncation and the telescope-half prune, now the fourth time.
    _alias_map = {}
    for _st in agda_lex.group_statements(lines[:hdr], _sl._opens):
        _m = re.match(r"^\s*(?:open\s+)?import\s+(\S+)\s+as\s+(\S+)", _st[0])
        if _m:
            _alias_map[_m.group(2)] = _m.group(1).rsplit(".", 1)[-1]
    def _debase(text):
        for _a, _tail in _alias_map.items():
            text = re.sub(r"(?<![\w.])" + re.escape(_a) + r"\.", "", text)
        return text
    # ⚑ THE ROOT AND THE LEAVES NEED DIFFERENT SPELLINGS OF THE SAME LINE, and
    # rewriting in place gave both the leaf's. The root RETAINS its aliased import
    # (`import … Graded.Base as Base`), so its own residue must keep `Base.Over`;
    # a leaf's imports are rewritten bare by `_bare()`, so its carried copy must
    # say `Over`. One de-aliased list served both and broke the root:
    # `[NoSuchModule] No module Over in scope` at `Defs.agda:79`.
    # Keep both forms — `body_residue` for the root, `body_residue_bare` for the
    # carry — rather than picking one and patching the other downstream.
    _residue_bare = [(ln, _debase(t)) for ln, t in _residue]
    _resid_txt = "\n".join(t for _ln, t in _residue_bare)

    # ⚑ Ⓑ6ᶜ²⁵ — `variable` declarations, collected from the WHOLE body. They are
    # not units (they define nothing) and not residue (the walk skips them for
    # starting with `private`), so no other pass can see them — yet every leaf's
    # signature may depend on the binders they introduce.
    _body_vars = [lines[i] for i in range(b0, min(b1 + 1, len(lines)))
                  if re.match(r"^\s*(?:private\s+)?variable\b", lines[i])]

    _pending = []
    for uname, blk, _priv in units:
        leaf = _sl.sanitize(uname, used)
        # ⚑ DEDENT BY THE UNIT'S OWN LEADING INDENT, NOT THE MODULE'S. A unit
        # lifted out of a `private` block sits TWO levels deep (4 spaces, not the
        # module's 2), so dedenting by the module indent leaves it indented — and
        # `defined_names`' `not l.startswith(" ")` test still fails, returning the
        # EMPTY SET. Measured: all three inner-leaf name cases failed with `set()`
        # while the dedent "ran". The unit's own first-line indent is the only
        # correct amount; relative structure inside the unit is preserved.
        _lead = min((len(l) - len(l.lstrip()) for l in blk if l.strip()),
                    default=indent)
        ded = [l[_lead:] if l.startswith(" " * _lead) else l.lstrip() for l in blk]
        # ⚑ Ⓑ6ᶜ²‴ — THE CARRIED RESIDUE IS PART OF THE SEED. A residue binder
        # travels with the leaf (see `residue_binders`), so its OWN text is demand:
        # `open Base.Over 𝟘 public using (Poly; nth)` applies `𝟘`, which `PlusP`'s
        # body never mentions. Seeding without it selected `A _+_` and emitted a
        # leaf whose carried binder referenced an unbound `𝟘`.
        # Seventh instance of the seed being too small — and the same fix each
        # time: whatever the leaf will CONTAIN must be in the closure's seed.
        params = needed_params("\n".join(blk) + "\n" + prelude_txt
                               + "\n" + _resid_txt, groups)
        out.append((leaf, params,
                    sorted(_sl.defined_names(ded) | _sl.field_names(ded)), ded))
    out = _close_over_siblings(out, groups)
    # ⚑ Ⓐ1⁵″ — THE CONSERVATION ALGORITHM IS `split_lemmas.parse`'s, NOT A NEW ONE.
    # WHAT BELONGS TO NO UNIT STILL BELONGS TO THE ROOT: the first apply dropped the
    # 16 `open Pₙ.Over … public` (barrel-not-unit, so no leaf carried them), leaving
    # a root that exported 22 coefficient names and none of the graded polynomial
    # ring — and it would have TYPECHECKED, failing only at its 36 consumers.
    #
    # ⚑ MY HAND-ROLLED REPLACEMENT SHIPPED TWO DEFECTS BEFORE THIS. A positional
    # cursor walk desynchronises on a MULTI-NAME SIGNATURE (`𝟘 𝟙 : A` declares two
    # names, so one source line feeds TWO units), duplicating `opOf`/`+-inverseʳ`
    # into both a leaf and the root. `parse` solves it with a MULTISET DIFFERENCE
    # over the EMITTED lines — order-free, and an imbalance surfaces instead of
    # silently mis-assigning. It has caught seven silent deletions; mine caught
    # none and caused two. Reuse the algorithm rather than re-derive it.
    #
    # ⚑ AND RESIDUE CARRIES PROVENANCE — `(1-based lineno, text)`, as `parse`
    # returns and `write_residue` consumes. A line you cannot look up in the
    # original is not recorded, it is merely retained.
    # (the pass itself is HOISTED above the unit loop — see Ⓑ6ᶜ²⁴ there. It must
    # run first so a carried residue line can seed each leaf's closure.)
    return {"root": _sl.parse(path)[0], "groups": groups, "leaves": out,
            "body_residue": _residue,            # root's form: alias retained
            "body_residue_bare": _residue_bare,  # leaf's form: alias stripped
            "body_vars": _body_vars,
            "imports": _imports,
            "span": (hdr - 1, max(_hend, hdr)),
            "opt": _sl.parse(path)[1], "src": src,
            # ⚑ `inner_hdr` is the header's LAST line, not its first: `root_text`
            # keeps `lines[:inner_hdr+1]`, so a multi-line telescope must be
            # inside that slice or the rewrite would truncate the header mid-way
            # and emit re-opens under a `module Over {A : Set}` with no `where`.
            "path": path, "inner": name, "inner_hdr": _hend,
            "inner_indent": indent}


def plan(path, module=None):
    """{root, groups, leaves:[(leaf, params, defines, block)]} — DECIDED, not applied.

    `module` — target an INNER `module M (…) where` instead of the file's own
    header. Pass the inner module's name; with no `module` and a bare file header,
    a single unambiguous inner telescoped module is picked automatically.
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    span = agda_lex.telescope_span(src)
    if span is None:
        # ⚑ NOT A REFUSAL ANY MORE — the file header being bare says nothing about
        # whether a telescope exists, only about WHERE. Ⓐ1: `FromCommRing`'s lives
        # on `module Over {A : Set} (CR : CommutativeRing A)`.
        return _inner_plan(path, src, module) if module else None
    if module:
        return _inner_plan(path, src, module)
    groups = agda_lex.telescope_groups(src)
    modname, opt, imports, units, fixities, residue = _sl.parse(path)
    # ⚑ THE UNIT'S TOKENS ARE NOT THE LEAF'S TOKENS — and `split_lemmas` already
    # says so, at `:807`, for its own version of this bug.  A leaf receives the
    # root's BODY PRELUDE verbatim, and that prelude can contain an APPLIED OPEN
    # whose arguments ARE telescope parameters:
    #
    #     open import …NormalizeIdem Word Canonical normalize normalize-canonical …
    #
    # Carried into a leaf that selected only `Word, normalize`, it references
    # `Canonical` — which that leaf deliberately does not bind.  MEASURED:
    # `[NotInScope] Canonical` at `Op.agda:18`.
    #
    # So the telescope selection and the inherited imports are COUPLED: seed the
    # closure with the block PLUS the prelude, and `needed_params`' existing
    # fixpoint pulls in every parameter either one mentions.  The closure was
    # right; the SEED was too small.
    _prelude_txt = "\n".join(imports)
    out, used = [], set()
    for name, blk in units:
        leaf = _sl.sanitize(name, used)
        params = needed_params("\n".join(blk) + "\n" + _prelude_txt, groups)
        out.append((leaf, params,
                    sorted(_sl.defined_names(blk) | _sl.field_names(blk)), blk))
    return {"root": modname, "groups": groups, "leaves": out,
            "imports": imports, "span": span, "opt": opt, "src": src,
            "path": path}


def body_prelude(p):
    """The root's BODY imports, as statement lines every leaf must also carry.

    ⚑ THE TELESCOPE HALF AND THE BODY HALF ARE DIFFERENT QUESTIONS, AND I USED
    ONE AUTHORITY FOR BOTH.  `imports_before(src, header)` answers *what does the
    TELESCOPE need* — positional, §31's rule — and it is the WRONG instrument for
    the body: `IdemInequality`'s `Eq.Neq`/`Eq.Trans`/`Eq.Sym` sit AFTER the module
    header, so the emitted leaves lost them and `Op.agda:21` failed
    `[NotInScope] ≢`.

    `split_lemmas.parse` already returns those statements as `imports`, and
    `group_statements` already folds a wrapped statement into one unit — so this
    reuses both rather than adding a second import selector (the worklist's own
    instruction, and the `agda_files()` lesson: a shared NAME is not a shared
    authority, but a second SELECTOR is worse).

    Deliberately UNFILTERED: `split_lemmas` narrows per-leaf via its `demand`
    evidence, which exists only where a `using` list declared it. This root's
    imports are BARE (⟡ban-decompose's target shape), so there is no demand map
    to narrow by, and dropping an import on a guess is the failure this section
    just repaired. `prune_imports` is the stage that removes what a leaf does not
    use — after the split, with the compiler as arbiter.

    ⚑ AND THE OPENER PREDICATE IS `split_lemmas._opens`, NOT `[]`.  My first cut
    passed an empty list; `group_statements(lines, opener)` takes a CALLABLE (its
    docstring: *"takes a caller's own opener predicate"*), and `[]` is falsy for
    every line — every statement would have been read as a continuation of the
    first.  Third time this session an authority's contract was inferred from a
    call site instead of read.
    """
    out = []
    for st in agda_lex.group_statements(p["imports"], _sl._opens):
        if _sl.IMP.match(st[0]):
            out += [l.rstrip() for l in st]
    return _bare(out)


def _needed(imports, blk, sibs_text=""):
    """Ⓐ1¹² — the subset of `imports` this leaf's body actually needs.

    ⚑ PRUNING AFTER EMISSION CANNOT PREVENT A COLLISION; ONLY PRUNING DURING IT
    CAN. Every leaf inherited the root's ENTIRE body prelude — `TimesComm` took 40
    imports to use ONE — and each unneeded bare import is a scope-widening that can
    clash. That is not merely wasteful: it is the collision GENERATOR.
    `TimesComm` defines `*-comm` and bare-imports `CommutativeRing`, whose FIELD is
    `*-comm` → `[ClashingDefinition]`. Running `prune_imports` afterwards cannot
    help, because by then the file is written and the pruner correctly KEEPS
    whatever the definition genuinely uses.

    ⚑ REUSE THE PREDICATE, DO NOT RE-DERIVE IT. `prune_imports.should_keep` is pure
    (no I/O), keep-biased ("every uncertain branch returns True: no evidence is
    never evidence of death"), and carries two REVERTED experiments in its
    docstring — the unique-provision test that broke 13 of 20 Enumerate leaves, and
    the fall-through that let the weakest signal overturn a no-evidence verdict.
    Re-deriving a keep-or-drop rule here would repeat both.

    ⚑ AND THE PREDICATE'S OWN NOTE NAMES THIS CALLER: *"The caller's SIBLING
    CLOSURE is what supplies the missing evidence."* The emitter knows each leaf's
    siblings, so the sibling import text joins the token probe — a name a leaf uses
    only through a sibling still counts as demand.
    """
    # ⚑ THE TOKEN SET IS MIXFIX-EXPANDED BEFORE THE CALL, and that is the caller's
    # job, not the predicate's — `prune.py:252` does it one line before invoking.
    # `_+_` appears as `+` at an infix use site; probing only the bare token loses
    # every operator, which is the two-spelling hazard this tree has now measured
    # in four separate tools. Read from the real call site, not inferred.
    toks = agda_lex.body_tokens("\n".join(blk) + "\n" + sibs_text,
                                _pi._mixfix_names())
    toks |= {f for t in list(toks) for f in ("_" + t + "_", t + "_", "_" + t)}
    # ⚑ `idx` IS `def_index()` — built by the CLI at `prune_imports.py:435` and
    # passed in, not constructed inside `prune`. Read from the call site; this is
    # the fourth contract in this file I first inferred and had to correct.
    idx = _pi.def_index()
    cache = {}
    out = []
    for st in agda_lex.group_statements(imports, _sl._opens):
        m = _pi.IMP.match(st[0])
        if not m:
            out += [l.rstrip() for l in st]
            continue
        # ⚑ `mod` IS `IMP.match(...).group(2)` — the predicate's own call site says
        # so. `agda_lex.statements(...).module` is a DIFFERENT authority and may
        # normalise differently; using it here would be a second spelling of the
        # same fact, which is how a census keyed on one spelling goes wrong.
        if _pi.should_keep(m.group(2), " ".join(st), toks, idx, cache, None, None):
            out += [l.rstrip() for l in st]
    return out


def _bare(statements):
    """Rewrite import STATEMENTS to their bare form — the ⟡ban-decompose shape.

    ⚑ THE GENERATOR WAS EMITTING BAN DEBT NOTHING DOWNSTREAM COULD CLEAR. The body
    prelude was copied VERBATIM, so every leaf inherited the root's
    `using (…)` lists and `as Pₙ` aliases — forms the import ban forbids. That was
    defensible only while `prune_imports` was the designated next stage, and it is
    NOT: the pruner "refuses renaming/as imports BY DESIGN". So the pipeline had no
    stage that could remove them, and `--qualified` counted them as fresh debt in
    22 brand-new files.

    ⚑ THE PRE-HEADER HALF ALREADY DID THIS and the body half did not — the same
    split-authority error as the wrapped-import truncation. `emit`'s prelude is
    rebuilt as bare `open import <mod>`, with its own comment noting that dropping
    `using`/`renaming` is "what ⟡ban-decompose wants anyway". One rule, applied in
    one place and not the other.

    A statement's continuations are consumed with it: `using (a;\\n  b)` is ONE
    statement, and keeping its tail after dropping its head is the unclosed-paren
    defect this file already measured.
    """
    out, seen = [], set()
    for st in agda_lex.group_statements(statements, _sl._opens):
        m = _sl.IMP.match(st[0])
        if not m:
            out += [l.rstrip() for l in st]
            continue
        _sts = list(agda_lex.statements(st))
        mod = _sts[0].module if _sts and _sts[0].module else None
        if not mod or mod in seen:
            continue                      # a duplicate bare import is dead weight
        seen.add(mod)
        out.append(f"open import {mod}")
    return out


def is_split_out(p):
    """Has this root ALREADY been split — i.e. does it hold only re-opens?

    ⚑ THE APPLY IS DESTRUCTIVE AND WAS NOT IDEMPOTENT, AND THE SECOND RUN PROVED
    IT.  After a successful apply the root retains its telescope and its
    `open import …Leaf … public` lines and NOTHING ELSE — so `plan()` finds ZERO
    units, and `emit(apply=True)` then deletes every leaf (none is in `keep`) and
    rewrites the root to a header with no re-opens.  A re-run therefore ERASES the
    work the first run did.

    MEASURED: the second invocation reported `0 leaf/leaves` and emptied the leaf
    directory; recovery came from the snapshot the run itself had just taken.
    *A tool whose second run destroys its first run's output is a tool that must
    REFUSE the second run* — the same reasoning as `prune_imports` refusing a
    body-less barrel rather than gutting it.
    """
    return bool(p["leaves"]) is False


def root_text(p, reopens):
    """The rewritten root: the shed leaves replaced by re-opens.

    ⚑ TRUNCATING AT THE HEADER IS CORRECT FOR A FILE-HEADER ROOT AND DESTRUCTIVE
    FOR AN INNER ONE. `lines[:hdr_end+1] + reopens` keeps everything up to the
    telescope's `where` — for a file-header root that IS the whole surviving root.
    For an inner module it would delete the file's own `module … where` and every
    import above it, since those sit ABOVE the inner header. The inner case keeps
    the file intact, replaces only the inner module's BODY, and INDENTS the
    re-opens to that module's body indent.
    """
    lines = p["src"].split("\n")
    if "inner_hdr" not in p:
        return "\n".join(lines[:p["span"][1] + 1] + [""] + reopens + [""])
    ind = " " * (p["inner_indent"] or 2)
    # ⚑ Ⓐ1⁵ — THE BODY'S NON-UNIT STATEMENTS MUST SURVIVE, AND THE FIRST APPLY
    # DROPPED THEM. `body_units` classifies `open … public` as barrel-not-unit
    # (correctly — it defines nothing), so `emit` never carried the 16
    # `open Pₙ.Over … public` and this rewrite rebuilt the root without them. The
    # root then exported 22 coefficient names and NONE of the graded polynomial
    # ring it gives 36 consumers — and it would have TYPECHECKED, failing only at
    # those consumers much later. A unit-shaped reader must still carry what is
    # not a unit.
    #
    # ⚑ THEY GO AFTER THE RE-OPENS BECAUSE THEY CONSUME THE SPLIT NAMES AS
    # ARGUMENTS (`open P0.Over _+_ _*_ 𝟘 𝟙 …`): every one of those arguments is
    # now supplied by a leaf re-opened above.
    return "\n".join(lines[:p["inner_hdr"] + 1] + [""]
                     + [ind + r for r in reopens] + [""]
                     + [t for _ln, t in p.get("body_residue", [])] + [""])


def _unlocalize(line, leaf):
    """Invert `localize_variables`' substitution on one emitted line.

    ⚑ THE RENAME IS ENUMERABLE, WHICH IS THE ONLY REASON A PROVENANCE CHECK IS
    POSSIBLE AT ALL. Ⓡ8 rewrites `n` → `n-<leaf>` by the `agda_lex.word`
    boundary; undoing it is a boundary-anchored substitution on the SAME
    authority. If a future transform rewrites emitted lines by some rule this
    cannot invert, `_emit_fidelity` will report those lines UNTRACED — which is
    the correct outcome (a guard that silently accepts an unknown rewrite is
    the false zero this whole class of bug lives in), and the fix is to teach
    the inverse here, never to loosen the comparison.
    """
    return re.sub(r"(?<![\w'-])([\w'-￿-]+?)-" + re.escape(leaf)
                  + r"(?![\w'-])", r"\1", line)


def _emit_fidelity(p, leaves_lines):
    """Ⓡ7 — every emitted BODY line traces to exactly one source body line.

    ⚑ `_conserve` GUARDS THE READ; NOTHING GUARDED THE WRITE, and I asserted the
    opposite three times (including in a committed docstring) — that synthesising
    content "would make the generator write source, which the conservation guard
    refuses by design". `pycodemod --calls _conserve` shows ONE call site, inside
    `body_units`, over the UNIT READ. It never sees emitted output. So the write
    path was unguarded the entire time the read path was being hardened, and the
    three unfaithfulness defects that shipped in one day were all found by READING
    EMITTED AGDA — the slowest possible instrument.

    ⚑ WHAT THIS CAN AND CANNOT CHECK, stated so it is not overread. This is
    CONSERVATION, not correctness — the same duty and the same limit `_conserve`
    records. It cannot say a leaf is well-formed, that its telescope is right, or
    that it typechecks. It says only: no emitted body line was INVENTED, and no
    source body line was LOST. Those are precisely the two failure modes that
    produce plausible-looking Agda, which is why they survived to be found by eye.

    ⚑ AND IT DELIBERATELY DOES NOT CHECK BYTE-EQUALITY, because the tool
    legitimately rewrites lines (Ⓡ8's leaf-local variables). A byte check would
    refuse the tool's own correct behaviour, so the invariant is PROVENANCE modulo
    the declared rename — inverted via `_unlocalize`, not waived.

    ⚑ SCOPE: BODY LINES ONLY. Headers, preludes, `variable` declarations, residue
    binders and sibling opens are CONSTRUCTED by design (`imports_before` returns
    module names, so the prelude is reconstructed and never copied). Demanding
    they trace to source would be a category error. The unit bodies are the half
    that must be carried verbatim, and they are the half that broke.

    ⚑⚑ IT CHECKS INVENTION ONLY, AND THE ASYMMETRY IS INHERITED, NOT INVENTED
    HERE. `_conserve` records it exactly: *"INVENTED is always a defect: a line
    in no source line means the reader FABRICATED content, and no downstream
    residue can absorb that. UNPLACED is returned as data for the caller to
    route."* A source body line reaching no leaf is NOT loss — imports, barrels
    (`open … public`), free-standing comments and the `private` marker
    legitimately belong to no unit, which is what residue is for.

    ⚑ AND MY FIRST CUT ADDED A `lost` ARM ANYWAY, firing on this tool's own
    fixtures — the same false refusal `_conserve`'s docstring says trains the
    caller to bypass the guard, re-derived one file away from where it is
    written down. The read guard learned this; the write guard did not inherit
    it because I wrote the write guard from the failure mode rather than from
    the sibling that already solved it. Loss at the WRITE boundary is already
    covered upstream: `_conserve` raises if the units do not reconstruct the
    body, so a line that reaches no unit never gets this far.
    """
    src_body = set()
    lines = p["src"].split("\n")
    b0 = p.get("inner_hdr", p["span"][1]) + 1
    for l in lines[b0:]:
        if l.strip():
            src_body.add(l.strip())
    invented = []
    for leaf, blk in leaves_lines:
        for l in blk:
            if not l.strip():
                continue
            # ⚑⚑ TRY THE LINE AS-IS *BEFORE* INVERTING THE RENAME — the inverse is
            # a heuristic and it FIRES ON NAMES THAT WERE NEVER RENAMED.
            # MEASURED on `Cyclic/Base.agda`: the leaf is named `HasOrderPerm` (it
            # defines `σ-HasOrderPerm`), and the source line
            #     σ-HasOrderPerm : HasOrderPerm σ (suc n)
            # unlocalizes to `σ : HasOrderPerm σ (suc n)` — because `-HasOrderPerm`
            # is a `-<leaf>` suffix by SPELLING, though Ⓡ8 never renamed anything
            # here (this root has no `variable` block at all). The guard then
            # reported three verbatim source lines as INVENTED and refused a
            # correct emit.
            #
            # ⚑ A LINE PRESENT VERBATIM IS CONSERVED, FULL STOP. The inverse exists
            # only to rescue lines Ⓡ8 legitimately rewrote, so it is a FALLBACK,
            # never the primary test. Ordering it first made a naming coincidence
            # between a leaf and a type it mentions into a refusal.
            if l.strip() in src_body:
                continue
            if _unlocalize(l, leaf).strip() not in src_body:
                invented.append((leaf, l.strip()))
    return invented


def emit(p, apply=False):
    """Write one file per leaf, each carrying ONLY the telescope it needs.

    ⚑ THE HALF THAT WAS MISSING, AND ITS ABSENCE IS WHY `IdemInequality/` BROKE.
    §34 built the planner, measured its population as ZERO over already-decomposed
    roots, and stopped — reasonable then.  §57 gave it a live population: R9 split
    a TELESCOPED root with `split_lemmas` (which declines that shape at `:10-11`),
    so the leaves were emitted WITHOUT the telescope and applied names they never
    bind (`[NotInScope] Word`).  Hand-writing the replacements is how the original
    damage happened (§31: *"the repair was unreviewable and un-rerunnable"*), and
    R7b-SWEEP says there are more.

    Three things every leaf needs, and each has a measured reason:

    1. **the selected telescope** — `needed_params`' CLOSURE, not a scan; probing a
       single spelling loses `_++_` (§34, pinned by a selftest).
    2. **its imports ABOVE the module header** — a telescope is scope-checked
       BEFORE anything in `where`, so a prelude emitted after the header leaves
       every `≡`-mentioning parameter unbound.  The restored root's own ⚑ records
       this and says *"MEASURED: 6 of the Core leaves"* inherited it.
       `agda_lex.imports_before` is the positional authority; nothing re-derives it.
    3. **the sibling imports it depends on** — a leaf using another leaf's name
       must import it, applied to the SAME arguments.

    The root becomes a re-opener: it keeps its telescope and re-opens each leaf
    applied to the parameters that leaf selected.

    ⚑ Ⓡ1 — THE RE-OPENS ARE NOT `public`, AND THIS SENTENCE USED TO SAY THEY WERE
    ("…so every existing consumer of the root's names still resolves"). That
    guarantee IS the re-export barrel the import ban forbids, and stating it as
    the tool's purpose is how the tool came to manufacture 30 of the tree's 150
    re-export sites from two splits. A generator emitting debt faster than a
    paydown can clear it cannot be fixed by a ratchet; it is fixed here.

    What replaces the guarantee: CONSUMERS IMPORT THE LEAVES. That is what the
    split is for, and it is the operator's ruling from the start of this arc —
    once bare imports carry individual symbols, the barrel becomes unnecessary
    rather than merely forbidden. The root still re-opens (without `public`) so
    its own carried residue still resolves; it simply no longer republishes.
    """
    src, path = p["src"], p["path"]
    hdr_end = p["span"][1]
    lines = src.split("\n")
    # ⚑ Ⓐ1⁶ — REFUSE BEFORE WRITING. Checked on every call (not just `--apply`) so
    # a dry run reports the same verdict the apply would, rather than looking clean
    # and failing at write time.
    _blk = _emit_blockers(p["leaves"], body_prelude(p) + [f"open import {m}" for m
                                                          in sorted(agda_lex.imports_before(
                                                              src, p["span"][0] + 1))])
    if _blk:
        raise ValueError("refusing to emit — incoherent leaf/leaves:\n  "
                         + "\n  ".join(_blk))
    # imports that sit ABOVE the module header travel with every leaf: they are
    # what the TELESCOPE itself needs (positional, via the homed authority).
    # ⚑ `imports_before` returns MODULE NAMES, not source lines — so the leaf's
    # prelude is RECONSTRUCTED as bare `open import <mod>`, never copied.  That is
    # the right shape twice over: it is the positional answer (what the TELESCOPE
    # can see), and re-emitting bare drops any `using`/`renaming` the root carried,
    # which is what ⟡ban-decompose wants anyway.
    pre = [f"open import {m}" for m in sorted(agda_lex.imports_before(
        src, p["span"][0] + 1))]
    # the root's BODY imports — a different question, a different authority
    body = body_prelude(p)
    root_mod = p["root"]
    root_dir = path[:-5]                       # …/IdemInequality
    leafdir = os.path.basename(root_dir)
    written, reopens = [], []
    # Ⓡ7 — (leaf, emitted body block) per leaf, checked for provenance below;
    # and the buffered (path, text) writes that check gates.
    _fid, _pending = [], []

    # name -> leaf that defines it, so a sibling reference becomes an import
    home = {}
    for leaf, _pr, defines, _blk in p["leaves"]:
        for d in defines:
            home[d] = leaf

    for leaf, params, defines, blk in p["leaves"]:
        names = [n for ns, _t in params for n in ns]
        # ⚑ THE GROUP TEXT IS ALREADY VERBATIM — DO NOT RE-WRAP IT.
        # `telescope_groups` documents this at `agda_lex.py:595`: *"Returns the
        # group VERBATIM (`(_++_ : Word → Word → Word)`) so a leaf can re-declare
        # it exactly"*.  My first cut emitted `f"({names} : {text})"`, producing
        # `(normalize : (normalize : Word → Word))` — a `[ParseError]` at the exact
        # column.  The authority's contract was in its docstring and I re-derived
        # it from the tuple's SHAPE instead of reading it.
        # ⚑ Ⓡ5ᵈ IS SUPERSEDED BY Ⓡ8 AND ITS INJECTION REMOVED. Putting the block
        # in the telescope destroyed per-signature generalisation: a module
        # parameter is fixed module-wide, so `pad-end`'s recursion (head at
        # `suc n'`, call at `n'`) failed `n₁ != suc n₁`. The block stays a
        # `variable` declaration in the body, with leaf-local names.
        tel = " ".join(t for _ns, t in params)
        # ⚑ AN IMPLICIT PARAMETER IS NOT A POSITIONAL ARGUMENT. `{A : Set}` is
        # solved by unification; passing it positionally gives
        # `[ModuleArityMismatch] the arguments … do not fit the telescope`, which
        # is what the whole 22-leaf apply hit at `SR.agda:85` on `R A CR`.
        # `telescope_groups` returns each group VERBATIM, so the brace is right
        # there — build the argument list from the group's DELIMITER, not from the
        # names alone. (An implicit can still be passed as `{A = A}`; positionally
        # it never can.)
        args = " ".join(n for ns, t in params if not t.lstrip().startswith("{")
                        for n in ns)
        # ⚑ SIBLING EDGES BY THE NAME-BOUNDARY AUTHORITY, NOT A `hasattr` HEDGE.
        # My first cut wrote `_sl.body_names(blk) if hasattr(...) else set()` —
        # and `body_names` DOES NOT EXIST, so the fallback would have emitted ZERO
        # sibling imports.  That is exactly the defect being repaired: the broken
        # `Idem.agda` references `_≉_` (defined in its sibling `Op`) with no import
        # of it.  A guard that degrades to measuring nothing is worse than a crash
        # (§52) — and here it would have RE-CREATED the bug.
        # `agda_lex.word` is THE Agda name boundary (`\b` misses 11.7% of names).
        _body = agda_lex.mask_comments("\n".join(blk))
        # ⚑ THE SIBLING PROBE MUST USE EVERY SPELLING — the two-spelling hazard,
        # for the third time in this file and the first in the SIBLING search.
        # `home` is keyed on the DECLARED name (`_+_`), while a use site writes the
        # operator BARE (`a + b`), so `word("_+_")` never matches and the sibling
        # edge is missed. MEASURED: `PlusComm`'s TYPE is `(a b : A) → a + b ≡ b + a`
        # — its only mention of `_+_` — so it imported `OpOf` and `R` but not
        # `Plus`, and failed `[NotInScope] +` at :32. `spellings()` is already the
        # authority here (it is what makes `needed_params` find `_++_`); the
        # sibling search simply never consulted it.
        sibs = sorted({home[n] for n in home
                       if home[n] != leaf
                       and any(agda_lex.word(s).search(_body)
                               for s in spellings(n))})
        # hoisted: BOTH prelude halves prune against the sibling closure, so it
        # must be bound before either `_needed` call.
        _sibtext = "\n".join(f"open import {root_mod}.{s}" for s in sibs)
        # ⚑ Ⓡ8 — LEAF-LOCAL VARIABLE NAMES. The block and this leaf's block are
        # rewritten TOGETHER, so a leaf importing four siblings sees four DISTINCT
        # variables instead of four `m`s. The names are elaborated away, so no
        # consumer of any leaf can tell. Done before the body is emitted, because
        # everything downstream (`blk`) must see the renamed form.
        _vdecls, blk = localize_variables(p.get("body_vars", []), blk, leaf)
        L = [
            "-" * 72,
            f"-- {root_mod}.{leaf}",
            "--",
            f"-- Defines: {', '.join(defines)}",
            "-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally",
            f"--   out of {root_mod}; telescope carried by split_telescoped).",
            "-" * 72,
            "",
            p["opt"] or "{-# OPTIONS --safe --without-K #-}",
            "",
            "-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES",
            "--   them: a parameter list is scope-checked before anything in `where`.",
        ]
        # ⚑ THE TELESCOPE PRELUDE IS PRUNED PER LEAF TOO. `pre` is built ONCE for
        # every leaf (it is the root's positional answer), so leaving it unpruned
        # left each `Graded.Laws.*` dead in all 22 — the census showed every one at
        # exactly 22, the tell that a whole class was untouched. Same split-
        # authority error as the truncation and the bare-form fix: one rule applied
        # to the body half and not the telescope half, three times now.
        # The TELESCOPE text joins the probe: a parameter's TYPE mentions names
        # these imports provide (`CommutativeRing` in `(CR : CommutativeRing A)`),
        # and those are demand even when the body never says them.
        # (the carried text joins this probe as well — the telescope half and the
        # body half are pruned separately, and a rule applied to one and not the
        # other is the split-authority error this file has now recorded five times)
        # ⚑ Ⓡ8: the RENAMED declarations, same as the body-half probe below. Both
        # halves must probe what is EMITTED, not its source — one probing the
        # pre-rename block and the other the post-rename one is the split-authority
        # error in its purest form.
        _carried_pre = "\n".join(
            _vdecls
            + residue_binders([t for _ln, t in p.get("body_residue_bare", [])], blk))
        L += _needed(pre, blk, _sibtext + "\n" + tel + "\n" + _carried_pre)
        L.append("")
        L.append(f"module {root_mod}.{leaf}{(' ' + tel) if tel else ''} where")
        L.append("")
        # ⚑ THE ROOT'S BODY IMPORTS BELONG HERE — AFTER the header, because they
        # are what the BODY needs, not what the telescope needs.  Omitting them
        # cost `[NotInScope] ≢` at `Op.agda:21`: `Eq.Neq`/`Eq.Trans`/`Eq.Sym` sit
        # after the root's `where`, so `imports_before` (the TELESCOPE authority)
        # cannot see them by construction.
        # ⚑ Ⓐ1¹² — PRUNE PER LEAF, DURING EMISSION. The body prelude is the ROOT's,
        # so most of it is dead in any single leaf (`TimesComm`: 40 imports, ONE
        # used) and every dead bare import is a scope-widening that can COLLIDE.
        # The sibling import text joins the probe, which is the "caller's SIBLING
        # CLOSURE" the predicate's docstring asks for.
        # ⚑ Ⓑ6ᶜ²⁵ — THE CARRIED TEXT IS PART OF THE IMPORT PROBE, TOO. A carried
        # `variable n m k : ℕ` needs `ℕ` in scope, and the leaf's body never says
        # `ℕ` — so the per-leaf prune dropped `Foundation.Nat.Nat` and the carried
        # declaration failed `[NotInScope] ℕ` at `PlusP:23`. Same shape as the
        # closure seed one line up: whatever the leaf will CONTAIN must be in the
        # probe, not just what its own block says.
        # ⚑ Ⓡ8: the probe must see the RENAMED declarations, which are what the
        # leaf actually contains. `_vdecls` carries `variable n-PlusP … : ℕ`, so
        # `ℕ` stays demand and the prune keeps `Foundation.Nat.Nat`. Probing the
        # pre-rename block would work by luck here (same type) and fail the moment
        # a rename touched the type — so probe what is emitted, not its source.
        _carried = "\n".join(_vdecls
                             + residue_binders(
                                 [t for _ln, t in p.get("body_residue_bare", [])], blk))
        L += _needed(body, blk, _sibtext + "\n" + _carried)
        if body:
            L.append("")
        # ⚑ Ⓑ6ᶜ²‴ — RESIDUE THAT BINDS TRAVELS WITH THE LEAF. A residue `open`
        # defines nothing (so no unit owns it) but may BIND names the leaves use:
        # `open Base.Over 𝟘 public using (Poly; nth)` is the whole reason every
        # `Graded.Defs` leaf says `Poly n → Poly n`. Root-only was right for
        # `FromCommRing`'s sixteen pure RE-EXPORTS and wrong here — export vs
        # binder is the distinction, and `residue_binders` decides it per leaf so
        # a leaf that never says `Poly` does not inherit the binder.
        _rb = residue_binders([t for _ln, t in p.get("body_residue_bare", [])], blk)
        if _rb:
            L += _rb
            L.append("")
        # ⚑ Ⓑ6ᶜ²⁵ — `variable` declarations the leaf's signature relies on. These
        # are invisible to every other carry: the conservation walk skips them for
        # starting with `private`, and they are neither imports nor units. Carried
        # with `private` STRIPPED — a leaf has no block to be private to.
        # ⚑ Ⓡ8 — the block is emitted with LEAF-LOCAL names (renamed above, in
        # lockstep with this leaf's own lines). Four siblings each declaring `m`
        # gave `AntiDiagSum` four ambiguous `m`s; four siblings declaring
        # `m-PadEnd`, `m-PlusP`, `m-ShiftToSucOnLeft`, `m-XShift` give it four
        # distinct variables. Per-signature generalisation is preserved — these
        # are still `variable` declarations, so `pad-end`'s recursion at `n` and
        # `suc n` still elaborates, which the telescope form (Ⓡ5ᵈ) destroyed.
        if _vdecls:
            L += _vdecls
            L.append("")
        # ⚑ A SIBLING IS APPLIED TO ITS **OWN** TELESCOPE, NOT THE IMPORTER'S.
        # This passed `args` — the IMPORTING leaf's argument list — to every
        # sibling. It only looks right while all leaves share one telescope. Once
        # the closure makes them differ, it breaks both ways: `OpOf` selects only
        # the IMPLICIT `A`, so it takes ZERO explicit arguments, and `Plus` handed
        # it `CR` → `[ModuleArityMismatch] … do not fit the telescope {A = A₁ :
        # Set}` at `Plus.agda:85`. The importee's own explicit selection is the
        # only correct argument list.
        _sibargs = {l: " ".join(n for ns, t in prm
                                if not t.lstrip().startswith("{") for n in ns)
                    for l, prm, _d, _b in p["leaves"]}
        for s in sibs:
            _sa = _sibargs.get(s, "")
            L.append(f"open import {root_mod}.{s}{(' ' + _sa) if _sa else ''}")
        L += blk
        L.append("")
        target = os.path.join(root_dir, leaf + ".agda")
        written.append(target)
        _fid.append((leaf, list(blk)))
        # ⚑ Ⓡ1 — NO `public`. This line made every split's root a RE-EXPORT BARREL,
        # the construct the import ban forbids and that this arc has deleted twice
        # (`Graded.Over`, `CommutativeRing`). It was written to keep the root's
        # consumers resolving — the same instinct the ban refuses — and it produced
        # 30 of the tree's 150 re-export sites from two splits alone.
        #
        # ⚑ THE ROOT STILL RE-OPENS, so its own body (the carried residue, e.g. the
        # sixteen `open Pₙ.Over …` in `FromCommRing`) still sees the names. What it
        # no longer does is REPUBLISH them: consumers import the leaves, which is
        # what the split exists to enable.
        reopens.append(f"open import {root_mod}.{leaf}"
                       f"{(' ' + args) if args else ''}")
        # ⚑ Ⓡ7 — THE TEXT IS BUFFERED, NOT WRITTEN HERE. The fidelity check below
        # is whole-plan (a source line "lost" by one leaf may be carried by
        # another), so it cannot run until every leaf is built — and a guard that
        # runs after the first leaves are already on disk is a post-mortem, not a
        # refusal. `_emit_blockers` is checked before the loop for the same reason.
        _pending.append((target, "\n".join(L)))

    # ⚑ Ⓡ7 EMIT-FIDELITY — REFUSE BEFORE WRITING. Same placement and same reason
    # as `_emit_blockers` above: a dry run reports the verdict the apply would.
    _inv = _emit_fidelity(p, _fid)
    if _inv:
        _msg = ["refusing to emit — emitted body line traces to no source line:"]
        _msg += [f"  INVENTED in {lf}: {t[:70]}" for lf, t in _inv[:12]]
        if len(_inv) > 12:
            _msg.append(f"  … {len(_inv) - 12} more")
        raise ValueError("\n".join(_msg))

    # the root keeps its telescope and re-opens the leaves it just shed
    root_new = root_text(p, reopens).split("\n")
    if apply:
        os.makedirs(root_dir, exist_ok=True)
        for _t, _txt in _pending:
            open(_t, "w", encoding="utf-8").write(_txt)
        # ⚑ DELETE the OLD split's leaves — they are the broken output, and
        # merging would leave both shapes on disk.  Only files NOT re-emitted.
        keep = {os.path.basename(w) for w in written}
        for f in sorted(os.listdir(root_dir)) if os.path.isdir(root_dir) else []:
            if f.endswith(".agda") and f not in keep:
                os.remove(os.path.join(root_dir, f))
        open(path, "w", encoding="utf-8").write("\n".join(root_new))
    return written, reopens


def _selftest():
    """Counted from len(cases). Cases run against the LIVE hand-split tree, because the
    ground truth for what a telescoped leaf should look like IS those 19 files."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    root = "agda/Substrate/Groups/Coxeter/Core.agda"
    leaf = "agda/Substrate/Groups/Coxeter/Core/NormalizeAppend/Left.agda"
    if not (os.path.exists(root) and os.path.exists(leaf)):
        print("split_telescoped selftest: 0/0 (witness files absent)")
        return True

    rsrc = open(root, encoding="utf-8").read()
    groups = agda_lex.telescope_groups(rsrc)
    check("the root's telescope parses into its 9 binder GROUPS (not flattened names)",
          len(groups), 9)

    # ⚑ `module_scopes` would return `a`,`b`,`c` here too — locals bound inside
    # `++-assoc`'s TYPE.  A generator using that list would emit `(a : ?)`.
    check("group names exclude locals bound inside a parameter's type",
          "a" in [n for ns, _ in groups for n in ns], False)

    lsrc = open(leaf, encoding="utf-8").read()
    body = "\n".join(agda_lex.mask_comments(lsrc).split("\n")
                     [agda_lex.telescope_span(lsrc)[1] + 1:])
    got = [n for ns, _ in needed_params(body, groups) for n in ns]
    want = [n for ns, _ in agda_lex.telescope_groups(lsrc) for n in ns]
    # ⚑ THE WHOLE POINT: reproduce the hand-split telescope exactly.
    check("selection reproduces the hand-split leaf's telescope", got, want)

    # ⚑ …and it fails WITHOUT two-spelling probing — `_++_` is written `++`.
    def one_spelling(body, groups):
        sel = set(); ch = True
        while ch:
            ch = False
            probe = body + " " + " ".join(groups[j][1] for j in sorted(sel))
            for i, (ns, _t) in enumerate(groups):
                if i not in sel and any(re.search(r"(?<![\w'-])" + re.escape(n) + r"(?![\w'-])", probe) for n in ns):
                    sel.add(i); ch = True
        return [n for i in sorted(sel) for n in groups[i][0]]
    check("without two-spelling probing the operator parameter is LOST",
          "_++_" in one_spelling(body, groups), False)

    # ── emit(): the half whose ABSENCE broke IdemInequality ────────────────
    # ⚑ EVERY CASE HERE IS A PROPERTY THE BROKEN LEAVES LACKED.  `Idem.agda` as
    # R9 emitted it: `module …Idem where` with NO telescope, applying `Word
    # Canonical normalize …` in its body (`[NotInScope] Word`), and referencing
    # its sibling's `_≉_` with no import.  A generator that reproduces any of
    # those is not a fix.
    import tempfile as _tf
    d = _tf.mkdtemp()
    rp = os.path.join(d, "Root.agda")
    open(rp, "w", encoding="utf-8").write(
        "{-# OPTIONS --safe #-}\n\n"
        "open import Sub.Eq\n\n"
        "module Sub.Root\n"
        "  (Word : Set)\n"
        "  (normalize : Word → Word)\n"
        "  (unused : Set)\n"
        "  where\n\n"
        "_≉_ : Word → Word → Set\n"
        "w₁ ≉ w₂ = normalize w₁ ≡ normalize w₂\n\n"
        "thm : (w : Word) → w ≉ w\n"
        "thm w = refl\n")
    pp = plan(rp)
    if pp:
        w, re_ = emit(pp, apply=False)
        check("emit plans one file per unit", len(w), 2)
        # rebuild the text the same way emit() would, to assert on content
        w2, re2 = emit(pp, apply=True)
        first = open(w2[0], encoding="utf-8").read()
        second = open(w2[1], encoding="utf-8").read()
        check("a leaf CARRIES ITS TELESCOPE (the broken split dropped it)",
              "(Word : Set)" in first, True)
        check("...and OMITS parameters it does not need",
              "unused" in first, False)
        # ⚑ THE GROUP TEXT IS VERBATIM — a re-wrap emits `(x : (x : T))`.
        # MEASURED: `[ParseError]` at `Op.agda:15.76`, invisible until the
        # compiler ran, because the plan's `params` list looked correct.
        check("a parameter's type is NOT double-wrapped",
              "(Word : (Word" in first or "(normalize : (normalize" in first,
              False)
        # ⚑ imports the TELESCOPE needs must precede the header — the restored
        # root's own ⚑ records 6 Core leaves that inherited this defect.
        check("telescope imports PRECEDE the module header",
              first.index("open import Sub.Eq") < first.index("module Sub.Root."),
              True)
        # ⚑ THE SIBLING EDGE, ON THE LIVE WITNESS — NOT THE FIXTURE.  My first
        # attempt asserted this against the synthetic root above and FAILED, and
        # the fixture was the defect: `thm w = refl` mentions `_≉_` only in its
        # TYPE, so it exercised nothing.  That is §22's trap (three of four new
        # fixtures were unrealistic and would have passed a broken helper), so the
        # case is re-pointed at `IdemInequality`, where `≉-idem`'s body genuinely
        # uses its sibling's `_≉_`.
        # ⚑ A CASE MUST NOT DEPEND ON TREE STATE THIS TOOL ITSELF MUTATES.
        # These cases originally read the live `IdemInequality.agda`, and every
        # successful `--apply` consumes it into re-opens — so the SAME suite
        # passed or failed depending on whether a split had just run, three times
        # in a row.  The witness's SHAPE is what matters, so it is reproduced here
        # verbatim (5-parameter telescope, `private` block, and the applied open
        # whose arguments are parameters — the coupling under test).
        wit = os.path.join(d, "Wit.agda")
        open(wit, "w", encoding="utf-8").write(
            "{-# OPTIONS --safe --without-K #-}\n\n"
            "open import Sub.Eq\n\n"
            "module Sub.Wit\n"
            "  (Word : Set)\n"
            "  (Canonical : Word → Set)\n"
            "  (normalize : Word → Word)\n"
            "  (normalize-canonical : (w : Word) → Canonical (normalize w))\n"
            "  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)\n"
            "  where\n\n"
            "open import Sub.NormalizeIdem\n"
            "  Word Canonical normalize normalize-canonical canonical-is-fixed\n"
            "open import Sub.Eq.Neq\n\n"
            "private\n"
            "  _≉_ : Word → Word → Set\n"
            "  w₁ ≉ w₂ = normalize w₁ ≢ normalize w₂\n\n"
            "≉-idem : (w₁ w₂ : Word) → w₁ ≉ w₂ → normalize w₁ ≉ normalize w₂\n"
            "≉-idem w₁ w₂ neq p = neq p\n")
        if os.path.exists(wit):
            wp = plan(wit)
            _w, wre = emit(wp, apply=False)
            defs = {l: set(d) for l, _p, d, _b in wp["leaves"]}
            check("the live witness splits into Op (defines _≉_) and Idem",
                  ("_≉_" in defs.get("Op", set())
                   and "≉-idem" in defs.get("Idem", set())), True)
            # ⚑ ASSERT THE RELATION, NOT A FROZEN ARGUMENT LIST.  This case read
            # `"Word normalize" in r`, which encoded the answer BEFORE the
            # coupling fix — so when leaves correctly began taking `Canonical`
            # too, the case failed on CORRECT output.  A case that hardcodes an
            # expected value cannot survive its own subject improving; assert
            # that each re-open is applied to exactly THAT leaf's selection.
            _sel = {l: [n for ns, _t in prm for n in ns]
                    for l, prm, _d, _b in wp["leaves"]}
            check("every re-open is APPLIED to that leaf's OWN selection",
                  all(any(r.startswith(f"open import Sub.Wit.{l} "
                                       + " ".join(ns)) for l, ns in _sel.items())
                      for r in wre), True)
            # ⚑ THE BODY IMPORTS ARE A SECOND, DIFFERENT QUESTION.  `Eq.Neq` sits
            # AFTER the root's `where`, so `imports_before` — the TELESCOPE
            # authority — cannot see it, and the leaves lost it:
            # `[NotInScope] ≢` at `Op.agda:21`.
            wbody = body_prelude(wp)
            check("the root's BODY imports are recovered (post-header)",
                  any("Eq.Neq" in l for l in wbody), True)
            # ⚑ A STATEMENT IS ITS HEAD **PLUS CONTINUATIONS** — my first form of
            # this case demanded every line start with `open import`, which is
            # false for a wrapped statement's second line by construction.  The
            # assertion, not the tool, was wrong: `group_statements` folds the
            # continuation in ON PURPOSE (the statement-span rule this arc fixed
            # in fifteen tools).  Assert the HEADS instead.
            check("...and they are STATEMENTS (heads are imports; "
                  "continuations ride along)",
                  bool(wbody) and wbody[0].lstrip().startswith(
                      ("open import", "import")), True)
            # ⚑ THE COUPLING: the inherited prelude holds an APPLIED OPEN whose
            # arguments are telescope parameters, so a leaf must take those too.
            # `Op`'s own body mentions only `Word`/`normalize`, but the prelude's
            # `…NormalizeIdem Word Canonical normalize normalize-canonical
            # canonical-is-fixed` drags in three more.  MEASURED before the fix:
            # `[NotInScope] Canonical` at `Op.agda:18`.
            wsel = {n for _l, prm, _d, _b in wp["leaves"]
                    for ns, _t in prm for n in ns}
            check("a leaf takes parameters used by its INHERITED PRELUDE, "
                  "not just its own body", "Canonical" in wsel, True)

    # ⚑ IDEMPOTENCE: A SECOND APPLY MUST REFUSE.  After a successful split the
    # root holds only its telescope and re-opens, so `plan()` sees ZERO units —
    # and the un-guarded `emit` then deleted every leaf (none in `keep`) and
    # blanked the re-opens.  MEASURED on the live witness; recovery came from the
    # snapshot the run had just taken.
    # ⚑ the fixture must match the SHAPE a real split leaves behind: a telescope
    # spanning to its own `where` line, then only re-opens.  My first version put
    # the telescope on the header line and `plan()` returned None — the fixture
    # was wrong, not the tool (§22's trap: a fixture that does not resemble real
    # input tests nothing).
    rp2 = os.path.join(d, "Done.agda")
    open(rp2, "w", encoding="utf-8").write(
        "{-# OPTIONS --safe #-}\n\n"
        "module Sub.Done\n"
        "  (Word : Set)\n"
        "  where\n\n"
        "open import Sub.Done.A Word public\n")
    p2 = plan(rp2)
    check("an ALREADY-SPLIT root plans zero units", len(p2["leaves"]) if p2 else -1, 0)
    check("...and `is_split_out` says so, so the CLI can refuse",
          is_split_out(p2) if p2 else None, True)

    # ── INNER-MODULE TARGETS (Ⓐ1) ──────────────────────────────────────────
    # ⚑ THE SHAPE THIS TOOL REFUSED, AND WHY THE REFUSAL WAS RIGHT.
    # `Graded/FromCommRing.agda`'s header is a bare `module … where`; its
    # telescope is on the INNER `module Over {A : Set} (CR : CommutativeRing A)`.
    # `telescope_span` skips any header indented or off column 0, so `plan`
    # returned None. The emitter was correct all along — only the SOURCE of the
    # span and the units was file-header-scoped.
    inr = os.path.join(d, "Inner.agda")
    open(inr, "w", encoding="utf-8").write(
        "{-# OPTIONS --safe --without-K #-}\n\n"
        "module Sub.Inner where\n\n"
        "open import Sub.Eq\n"
        # ⚑ A WRAPPED IMPORT, because that is the defect. The live root's
        # `Semiring using (Semiring; +-monoid; *-monoid;` wraps onto a second
        # line; a head-only line filter keeps the head and DROPS the tail,
        # emitting an unclosed paren into every leaf.
        "open import Sub.Semiring using (Semiring; plus-monoid;\n"
        "  distrib-left; absorb-left)\n"
        "open import Sub.Ring\n\n"
        "module Over {A : Set} (CR : CommutativeRing A) where\n"
        # ⚑ THE CHAIN IS FOUR HOPS ON PURPOSE — it mirrors the live
        # `FromCommRing` (`𝟘 = ε +M` → `+M = +-monoid SR` → `SR = semiring R` →
        # `R = ring CR`). A one-hop fixture would pass against a one-pass sibling
        # read and prove nothing; §22's trap is a fixture that does not resemble
        # real input.
        "  private\n"
        "    R = ring CR\n"
        "    SR = semiring R\n"
        "    +M = +-monoid SR\n"
        "  𝟘 : A\n"
        "  𝟘 = ε +M\n"
        "  neg : A → A\n"
        "  neg = inv +M\n"
        "  neg-𝟘 : neg 𝟘 ≡ 𝟘\n"
        "  neg-𝟘 = lemma 𝟘\n"
        # ⚑ THE BARREL, mirroring the live root's 16 `open Pₙ.Over … public`: it
        # defines nothing (so it is not a unit) and CONSUMES the split names as
        # arguments (so it must land after the re-opens).
        "  open G.Over 𝟘 neg public\n")
    check("⚑ the FILE-HEADER path still refuses an inner-telescoped file",
          plan(inr), None)
    ip = plan(inr, module="Over")
    check("an inner-module target PLANS (the Ⓐ1 gap closed)", ip is not None, True)
    if ip:
        check("the inner telescope is read as GROUPS, not the file header's",
              [n for ns, _t in ip["groups"] for n in ns], ["A", "CR"])
        # ⚑ SCAFFOLDING IS A LEAF, PER THE OPERATOR'S RULING — `private` is banned,
        # so `R` becomes an ordinary leaf every other leaf may import, rather than
        # being duplicated into each or left as a namespace-munging block.
        _defs = {l: set(dd) for l, _p, dd, _b in ip["leaves"]}
        check("the `private` scaffolding becomes an ORDINARY leaf",
              "R" in set().union(*_defs.values()) if _defs else False, True)
        check("each splittable name gets its own leaf",
              all(any(n in dd for dd in _defs.values())
                  for n in ("𝟘", "neg", "neg-𝟘")), True)
        # ⚑ THE DEFINED-NAMES AUTHORITY IS COLUMN-0-ORIENTED AND THESE UNITS ARE
        # INDENTED. `split_lemmas.defined_names` skips `l.startswith(" ")`, so on
        # inner units it returns NOTHING for every leaf — and `emit`'s `home{}`
        # map, which turns a sibling reference into an import, would be EMPTY.
        # That is silently zero sibling imports: exactly the `[NotInScope] _≉_`
        # defect `emit` was built to stop, re-created one level down.
        check("⚑ inner units are DEDENTED before the column-0 name authority runs",
              _defs.get("Neg", set()) or _defs.get("neg", set()), {"neg"})
        _w3, _re3 = emit(ip, apply=False)
        check("every inner leaf re-open is applied to its own selection",
              all(r.startswith("open import Sub.Inner.") for r in _re3), True)
        # ⚑ THE ROOT REWRITE CANNOT TRUNCATE AT THE HEADER. For a file-header root
        # `lines[:hdr_end+1]` IS the whole surviving root; for an inner module that
        # would DELETE the file's own header and imports above `module Over`.
        _rt = root_text(ip, _re3)
        check("the file's own header SURVIVES the inner rewrite",
              "module Sub.Inner where" in _rt, True)
        check("...and its imports above the inner module survive",
              "open import Sub.Ring" in _rt, True)
        check("...and the inner module header survives, re-opens INDENTED under it",
              "module Over {A : Set} (CR : CommutativeRing A) where" in _rt
              and all(l.startswith("  ") for l in _rt.split("\n")
                      if l.strip().startswith("open import Sub.Inner.")), True)

        # ── Ⓐ1′ SIBLING-ARG-CLOSURE ────────────────────────────────────────
        # ⚑ THE SEED WAS TOO SMALL A THIRD TIME, AND THE FIXTURE MUST BE
        # TRANSITIVE OR IT TESTS NOTHING. `needed_params` closes over telescope
        # GROUPS; here the chain runs through SIBLING DEFINITIONS. On the live
        # `FromCommRing`: `𝟘 = ε +M` → `+M = +-monoid SR` → `SR = semiring R` →
        # `R = ring CR` → `CR`. FOUR hops, so a one-pass sibling read still
        # under-selects — it must be a fixpoint over the leaf GRAPH.
        #
        # MEASURED before the fix: 15 of 22 live leaves selected ZERO parameters,
        # while `emit` would hand each an `open import ….R A CR` it cannot supply
        # — `module ….Zero where` with an unresolvable applied import. Same shape
        # as the inherited-prelude coupling `emit` documents (`[NotInScope]
        # Canonical`): the closure was right, the SEED was too small.
        _z = {l: [n for ns, _t in prm for n in ns] for l, prm, _d, _b in ip["leaves"]}
        check("⚑ a leaf reaching a param through a SIBLING selects it "
              "(𝟘 → R → CR, transitively)",
              set(_z.get("Zero", [])), {"A", "CR"})
        check("...and the sibling chain's MIDDLE links select it too",
              set(_z.get("Neg", [])), {"A", "CR"})
        # ⚑ THE PROPERTY, NOT A FROZEN LIST: every sibling import `emit` emits is
        # applied to args the importing leaf actually binds. This is what the
        # per-leaf assertion above generalises to, and it is the invariant that
        # would have caught the defect without knowing which leaves were wrong.
        _home = {n: l for l, _p, dd, _b in ip["leaves"] for n in dd}
        _ok = True
        for _l, _prm, _dd, _blk in ip["leaves"]:
            _mine = {n for ns, _t in _prm for n in ns}
            _body = agda_lex.mask_comments("\n".join(_blk))
            for _n, _owner in _home.items():
                if _owner != _l and agda_lex.word(_n).search(_body):
                    _need = {x for ns, _t in dict(
                        (ll, pp) for ll, pp, _d2, _b2 in ip["leaves"])[_owner]
                        for x in ns}
                    if not _need <= _mine:
                        _ok = False
        check("⚑ every sibling import is applied to args the importer BINDS",
              _ok, True)

        # ⚑ AN IMPLICIT PARAMETER IS NEVER A POSITIONAL ARGUMENT. The fixture's
        # telescope is `(A : Set)` — EXPLICIT — so it cannot exercise this; the
        # live root's is `{A : Set} (CR : …)`, and passing `R A CR` produced
        # `[ModuleArityMismatch] … do not fit the telescope {A = A₁ : Set}
        # (CR₁ : CommutativeRing A₁)` at `SR.agda:85` — the error that stopped the
        # fourth apply. Assert on a telescope that HAS an implicit.
        _imp = [(["A"], "{A : Set}"), (["CR"], "(CR : Ring A)")]
        # ⚑ Ⓡ7 — `src` NOW CARRIES THE LEAF BODIES. These fixtures decoupled the
        # two (a bare header, with leaf bodies from nowhere), which is exactly why
        # no fixture here could ever have caught a fidelity defect: the emitter was
        # free to invent because the fixture had nothing to invent AGAINST.
        _leaves = [("L", _imp, ["x"], ["x = 1"])]
        _w4, _re4 = emit({"src": "module M where\nmodule Over {A : Set} (CR : Ring A) where\n  x = 1\n",
                          "path": os.path.join(d, "M.agda"), "root": "M",
                          "groups": _imp, "leaves": _leaves, "imports": [],
                          "span": (0, 1), "opt": None, "inner": "Over",
                          "inner_hdr": 1, "inner_indent": 2,
                          "body_residue": []}, apply=False)
        # ⚑ this case is about the ARGUMENT LIST, not visibility — it froze
        # `public` into its expectation incidentally, and Ⓡ1 removing the
        # re-export made it fail on CORRECT output. Assert the arguments only.
        check("⚑ an implicit `{A : Set}` is NOT passed positionally",
              _re4, ["open import M.L CR"])

        # ⚑ Ⓑ6ᶜ²: AN IMPLICIT IS EXCLUDED FROM THE ARGUMENT LIST, NOT FROM THE
        # TELESCOPE. Ⓠ-era work taught `emit` to stop passing `{A : Set}`
        # positionally — correct — but the SELECTION must still carry it, because
        # a selected parameter's TYPE names it: `(_+_ : A → A → A)` is meaningless
        # without `A`. MEASURED on `Graded/Defs.agda`: leaf `PlusP` emitted
        # `module … .PlusP (_+_ : A → A → A) where` with `A` unbound —
        # `[NotInScope] A` at :16.
        # `needed_params` closes to fixpoint over group TEXT for exactly this
        # ("a needed parameter's TYPE may mention another"), so the closure is
        # right and the seed must include the implicit group.
        _gi = [(["A"], "{A : Set}"), (["_+_"], "(_+_ : A → A → A)")]
        _sel_i = [n for ns, _t in needed_params("x = a + b", _gi) for n in ns]
        check("⚑ selecting an operator also selects the IMPLICIT its type names",
              _sel_i, ["A", "_+_"])
        # ⚑ …AND THE SIBLING CLOSURE MUST NOT DROP IT ON THE REBUILD. The selection
        # above is correct; the emitted plan still read `params=1 ['_+_']`, so the
        # implicit is lost AFTER `needed_params`. `_close_over_siblings` rebuilds
        # each leaf's params through `groups.index(g)`, which is where a group can
        # silently fail to round-trip.
        _lv = [("L", needed_params("x = a + b", _gi), ["x"], ["x = a + b"])]
        _out_i = _close_over_siblings(_lv, _gi)
        check("⚑ Ⓑ6ᶜ²″: the sibling closure PRESERVES the implicit group",
              [n for ns, _t in _out_i[0][1] for n in ns], ["A", "_+_"])

        # ── Ⓑ6ᶜ²‴ RESIDUE THAT **BINDS** ───────────────────────────────────
        # ⚑ A RESIDUE LINE IS NOT ALWAYS ROOT-ONLY. The conservation pass files
        # `open Base.Over 𝟘 public using (Poly; nth)` as residue — correctly, it
        # DEFINES nothing, so no unit owns it — and `root_text` keeps it in the
        # root. But it BINDS `Poly`/`nth`, and every leaf's signature says
        # `Poly n → Poly n → Poly n`. MEASURED: `[NotInScope] Poly` at
        # `Defs/PlusP.agda:22`, with agda naming `Over.Poly` as the intended one.
        #
        # ⚑ EXPORT vs BINDER IS THE DISTINCTION. The 16 `open Pₙ.Over … public`
        # in `FromCommRing` are pure re-exports — nothing in a leaf refers to them,
        # so root-only was right there and this never surfaced. An `open X …`
        # whose names APPEAR IN THE LEAVES is a binder and must travel with them.
        # Sixth instance of the seed being too small (Ⓒ1).
        _resid = ["  open Base.Over 𝟘 public using (Poly; nth)"]
        check("⚑ Ⓑ6ᶜ²‴: a residue `open` whose names a leaf USES is carried",
              residue_binders(_resid, ["_+P_ : Poly n → Poly n"]),
              ["open Base.Over 𝟘 using (Poly; nth)"])
        # ⚑ …WITH `public` STRIPPED. Re-exporting makes every leaf a second
        # provider of `Poly`, and the root keeps its own copy — so it saw EIGHT
        # (`[ClashingDefinition] Multiple definitions of Poly`, `Defs.agda:68`).
        # A carry BINDS; it does not publish. Same reasoning as stripping
        # `private` from a carried `variable`, and the ban forbids re-exports.
        check("...and `public` is stripped, so a leaf is not a second provider",
              all("public" not in v
                  for v in residue_binders(_resid, ["_+P_ : Poly n"])), True)

        # ── Ⓡ1 THE ROOT DOES NOT RE-EXPORT ─────────────────────────────────
        # ⚑ THIS TOOL WAS MANUFACTURING THE BANNED CONSTRUCT ON EVERY SPLIT. Its
        # own docstring said the root "re-opens each leaf … so every existing
        # consumer of the root's names still resolves" — written to preserve the
        # consumers, which is exactly the instinct the import ban exists to refuse.
        # MEASURED: `--reexports` reports 150 sites in 80 modules tree-wide, and
        # THIRTY of them are mine — 22 from the `FromCommRing` split, 8 from
        # `Graded.Defs`. A generator that emits debt faster than a paydown can
        # clear it is the shape a ratchet cannot help with; the fix is at the
        # generator.
        #
        # ⚑ AND IT IS WHAT MADE THE `k` COLLISION LOOK LIKE A MISSING CARRY. Eight
        # leaves each correctly declared `variable n m k : ℕ`; the root's `public`
        # re-opens published all eight, so the root saw eight `k`s. The carry was
        # right — the re-export was the defect, and I nearly wrote a tenth carry
        # to work around it.
        #
        # ⚑ WHAT REPLACES THE GUARANTEE: the consumers import the LEAVES. That is
        # the point of splitting, and it is the operator's ruling from the start of
        # this arc — *once bare imports carry individual symbols, the filter (and
        # the barrel) becomes unnecessary rather than merely forbidden.*
        check("⚑ Ⓡ1: a root re-open is NOT `public` — the root is not a barrel",
              all("public" not in r for r in _re3), True)
        # ⚑ Ⓡ4: AN IMPORTER MUST BIND EVERY ARGUMENT IT PASSES A SIBLING. The
        # sibling is applied to ITS OWN telescope (correct — Ⓠ-era fix), so the
        # importer's selection must be a SUPERSET of the importee's. The closure
        # unions `sel[owner]` into `sel[i]` for exactly this, but only when the
        # importer's BODY names something the owner defines.
        # MEASURED: `Outer` selects `A _+_ 𝟘 𝟙` yet passes `_+_ _*_ 𝟘 𝟙` to `C` —
        # `[NoParseForApplication]` at `Outer.agda:39`, because `_*_` is not bound
        # there. The union either did not fire or fired on the wrong index.
        _g4 = [(["A"], "{A : Set}"), (["_+_"], "(_+_ : A → A)"),
               (["_*_"], "(_*_ : A → A)")]
        # ⚑ THE OWNER'S NAME IS AN OPERATOR AND THE USE SITE IS BARE — which is
        # what made this invisible. A fixture using a plain name (`o = c`) passes
        # against the BROKEN probe, because `word("c")` matches `c`. Only an
        # operator distinguishes the two spellings.
        _lv4 = [("C", [_g4[0], _g4[1], _g4[2]], ["_·c_"], ["_·c_ = f _*_"]),
                ("Outer", [_g4[0], _g4[1]], ["o"], ["o = a ·c q"])]
        _cl4 = _close_over_siblings(_lv4, _g4)
        check("⚑ Ⓡ4: an importer's selection SUPERSETS the sibling it applies",
              [n for ns, _t in dict((l, p) for l, p, _d, _b in _cl4)["Outer"]
               for n in ns], ["A", "_+_", "_*_"])
        check("...and it still applies the leaf's own arguments",
              any(r.startswith("open import Sub.Inner.Zero") for r in _re3), True)
        check("...but one the leaf never mentions is NOT (root-only, as before)",
              residue_binders(_resid, ["x = 1"]), [])
        # ⚑ a COMMENT in residue is never a binder, however it is punctuated
        check("a residue comment is never carried",
              residue_binders(["  -- Poly / nth come from Base"],
                              ["_+P_ : Poly n → Poly n"]), [])

        # ── Ⓑ6ᶜ²⁵ VARIABLE BLOCKS ──────────────────────────────────────────
        # ⚑ A `variable` DECLARATION BINDS FOR THE WHOLE MODULE, and the
        # conservation pass skips it because the line starts with `private`. That
        # skip is right for a private BLOCK — its body is carried by the units —
        # and wrong for `private variable n m k : ℕ`, which introduces implicit
        # binders every leaf's signature relies on. MEASURED: `[NotInScope] n` at
        # `Defs/PlusP.agda:24`, where the signature reads `Poly n → Poly n`.
        #
        # ⚑ SEVENTH SHAPE OF ONE PROBLEM — carrying the root's SCOPE into a leaf:
        # prelude imports, telescope groups, sibling args, residue binders, alias
        # rewriting, and now variable blocks. Kept as a named patch rather than
        # folded into a general rewrite, because the list IS the record of what a
        # module scope turns out to contain.
        _vb = ["  private variable n m k : ℕ", "  variable ℓ : Level"]
        check("⚑ Ⓑ6ᶜ²⁵: a `variable` binder a leaf USES is carried",
              variable_binders(_vb, ["_+P_ : Poly n → Poly n"]),
              ["variable n m k : ℕ"])
        check("...`private` is stripped — a leaf has no block to be private to",
              all(not v.startswith("private")
                  for v in variable_binders(_vb, ["x : Poly n"])), True)
        check("...a binder the leaf never names is NOT carried",
              variable_binders(_vb, ["x : Set"]), [])
        check("...and a NON-private `variable` is carried the same way",
              variable_binders(_vb, ["f : Set ℓ"]), ["variable ℓ : Level"])
        # ⚑ Ⓡ5ᵃ: A LEAF THAT IMPORTS A SIBLING ALREADY CARRYING THESE DOES NOT
        # DECLARE ITS OWN. A `variable` is GENERALISABLE, not an ordinary binding:
        # two identical declarations in one scope do not merge, they become
        # `[AmbiguousName]`. MEASURED: `Outer` declares `variable n m k : ℕ` at :37
        # and imports sibling `C` at :39, which carries the same — ambiguous `n` at
        # `Outer.agda:40`.
        # ⚑ THIS IS A MOVE, NOT A SYNTHESIS. The alternative — emitting `∀ {n}`
        # binders into each signature — would have the generator WRITE source, and
        # the conservation guard exists to refuse exactly that. Suppressing a
        # duplicate carry keeps every emitted line traceable to a source line.
        check("⚑ Ⓡ5ᵃ: a sibling already carrying the variables suppresses the copy",
              variable_binders(_vb, ["x : Poly n"], sibling_carries=True), [])
        check("...but with no such sibling the leaf still declares them",
              variable_binders(_vb, ["x : Poly n"], sibling_carries=False),
              ["variable n m k : ℕ"])

        # ── Ⓡ5ᵈ GENERALISE INTO THE TELESCOPE ──────────────────────────────
        # ⚑ SUPPRESSION CANNOT WORK, AND THE COMPILE PROVED IT. A generalisable
        # variable declared in ANY leaf propagates through every sibling edge, and
        # the sibling graph is not a tree: `AntiDiagSum` imports FOUR leaves
        # (`PadEnd`, `PlusP`, `ShiftToSucOnLeft`, `XShift`), none of which has a
        # sibling of its own, so each rightly declares `variable n m k : ℕ` — and
        # `AntiDiagSum` inherits FOUR copies of `m`. Suppressing its own changes
        # nothing. There is no assignment of leaf-local `variable` declarations
        # that avoids this.
        #
        # ⚑ SO THE BLOCK BECOMES TELESCOPE PARAMETERS, WHICH IS A MOVE AFTER ALL.
        # `variable n m k : ℕ` and `{n m k : ℕ}` bind the same names to the same
        # type; the first generalises per-signature, the second per-module. A
        # module telescope does NOT propagate through an import — the importer
        # applies it — so N sibling edges bring zero copies. The declaration is
        # rewritten, not invented: same names, same type, different binder form.
        check("⚑ Ⓡ5ᵈ: a `variable` block becomes an implicit telescope group",
              variable_telescope(["  private variable n m k : ℕ"]),
              ["{n m k : ℕ}"])
        check("...a non-private `variable` too",
              variable_telescope(["variable ℓ : Level"]), ["{ℓ : Level}"])
        check("...and a line that is not a `variable` yields nothing",
              variable_telescope(["  open X public"]), [])

        # ── Ⓡ8 LEAF-LOCAL VARIABLE NAMES ───────────────────────────────────
        # ⚑ THE COLLISION IS NAME-IDENTITY, AND NOTHING ELSE. Two `variable n : ℕ`
        # declarations in one scope are `[AmbiguousName]`; two DIFFERENTLY-NAMED
        # ones are not. The generalised names never escape — they are elaborated
        # away, so `x-shift`'s exported type is `∀ {n} → Poly n → Poly (suc n)`
        # whatever the source called it — which is exactly why renaming is free at
        # the boundary and sufficient inside it.
        #
        # ⚑ WHY THIS IS THE FIX AND `module Over` IS NOT. The tree's existing
        # shards (`Laws/Linear.agda:46`, `Conv.agda:52`) carry byte-identical
        # blocks without colliding because each sits inside its own `module Over`
        # — which does not AVOID the collision, it HIDES it in a scope nothing can
        # see into. That opacity is what this arc removes; citing it as proof the
        # problem is solved was using the black box to justify the black box.
        #
        # ⚑ BOTH HALVES OR NEITHER. The block and the leaf's SIGNATURES must be
        # renamed together; renaming one is the split-authority error this file has
        # recorded five times.
        _vsrc = ["  private variable n m k : ℕ"]
        _blk8 = ["_+P_ : Poly n → Poly n → Poly n",
                 "(x ∷ u) +P (y ∷ v) = (x + y) ∷ (u +P v)"]
        _vn, _rw = localize_variables(_vsrc, _blk8, "PlusP")
        check("⚑ Ⓡ8: the carried block gets LEAF-LOCAL names",
              _vn, ["variable n-PlusP m-PlusP k-PlusP : ℕ"])
        check("...and the leaf's signature is rewritten to match",
              _rw[0], "_+P_ : Poly n-PlusP → Poly n-PlusP → Poly n-PlusP")
        check("...while a clause mentioning no variable is untouched",
              _rw[1], "(x ∷ u) +P (y ∷ v) = (x + y) ∷ (u +P v)")
        # ⚑ WORD-BOUNDED, or `n` rewrites inside `nth`/`suc n'`/`anti-diag-sum`.
        check("⚑ the rename is word-bounded, not substring",
              localize_variables(_vsrc, ["f : Poly n → nth n k"], "X")[1][0],
              "f : Poly n-X → nth n-X k-X")
        # ⚑ THE POSITIONAL TRAP (`Defs.agda:91-92`). `shift-to-suc-on-left` mixes a
        # block-derived `m` with a WRITTEN `∀ {n'}`, and binds both positionally as
        # `{m} {n'}` — which works only because generalised variables insert to the
        # LEFT of written ones. A rename must touch the block-derived name and
        # leave the written binder alone, or the two ℕs silently swap and the body
        # still typechecks if `+ℕ-comm`'s arguments swap too.
        _trap = ["shift-to-suc-on-left : ∀ {n'} → Poly (m ℕ+ suc n') → Poly (suc n' ℕ+ m)",
                 "shift-to-suc-on-left {m} {n'} p = subst Poly (+ℕ-comm m (suc n')) p"]
        _t8 = localize_variables(_vsrc, _trap, "Sh")[1]
        check("⚑ Ⓡ8: a WRITTEN `∀ {n'}` binder is NOT renamed",
              "∀ {n'}" in _t8[0], True)
        check("...while the block-derived `m` IS, in both signature and body",
              ("m-Sh" in _t8[0]) and ("m-Sh" in _t8[1]), True)

        # ⚑ A SIBLING TAKES ITS OWN TELESCOPE, NOT THE IMPORTER'S. Two leaves with
        # DIFFERENT selections: `Narrow` binds only the implicit `A` (zero explicit
        # args), `Wide` binds `CR` and references `Narrow`'s name. Passing the
        # importer's list gave `Wide` → `open import …Narrow CR`, i.e.
        # `[ModuleArityMismatch] … do not fit the telescope {A = A₁ : Set}` at
        # `Plus.agda:85` — the fifth apply's failure. The bug is invisible while
        # every leaf shares one telescope, which is why the earlier fixture missed it.
        _g2 = [(["A"], "{A : Set}"), (["CR"], "(CR : Ring A)")]
        _two = [("Narrow", [_g2[0]], ["nn"], ["nn = 1"]),
                ("Wide", _g2, ["ww"], ["ww = nn"])]
        _w5, _re5 = emit({"src": "module M where\nmodule Over {A : Set} (CR : Ring A) where\n"
                                 "  nn = 1\n  ww = nn\n",
                          "path": os.path.join(d, "M2.agda"), "root": "M2",
                          "groups": _g2, "leaves": _two, "imports": [],
                          "span": (0, 1), "opt": None, "inner": "Over",
                          "inner_hdr": 1, "inner_indent": 2,
                          "body_residue": []}, apply=True)
        _wide = open(_w5[1], encoding="utf-8").read()
        check("⚑ a sibling import uses the SIBLING's telescope, not the importer's",
              "open import M2.Narrow\n" in _wide, True)

        # ⚑ THE SIBLING PROBE IS TWO-SPELLING. An operator is DECLARED `_+_` and
        # USED bare (`a + b`), so a probe on the declared form alone misses the
        # edge entirely. MEASURED: `PlusComm`'s only mention of `_+_` is in its
        # TYPE, `(a b : A) → a + b ≡ b + a`, so it was emitted without importing
        # its `Plus` sibling → `[NotInScope] +` at :32. Same hazard `spellings()`
        # already fixed for `needed_params`; the sibling search never used it.
        _g3 = [(["A"], "(A : Set)")]
        _ops = [("Plus", _g3, ["_+_"], ["_+_ = op"]),
                ("Comm", _g3, ["c"], ["c : (a b : A) → a + b ≡ b + a",
                                      "c = prf"])]
        _w6, _re6 = emit({"src": "module M where\nmodule Over (A : Set) where\n"
                                 "  _+_ = op\n"
                                 "  c : (a b : A) → a + b ≡ b + a\n  c = prf\n",
                          "path": os.path.join(d, "M3.agda"), "root": "M3",
                          "groups": _g3, "leaves": _ops, "imports": [],
                          "span": (0, 1), "opt": None, "inner": "Over",
                          "inner_hdr": 1, "inner_indent": 2,
                          "body_residue": []}, apply=True)
        _comm = open(_w6[1], encoding="utf-8").read()
        check("⚑ an operator used BARE in a TYPE still pulls its sibling import",
              "open import M3.Plus A" in _comm, True)

        # ── Ⓡ7 EMIT-FIDELITY ───────────────────────────────────────────────
        # ⚑ `_conserve` GUARDS THE READ; NOTHING GUARDED THE WRITE, and I claimed
        # the opposite three times including in a committed docstring. These cases
        # fail against the code as it stood before this guard existed.
        _fp = {"src": "module M where\nmodule Over (A : Set) where\n  x = 1\n",
               "path": os.path.join(d, "M4.agda"), "root": "M4",
               "groups": _g3, "imports": [], "span": (0, 1), "opt": None,
               "inner": "Over", "inner_hdr": 1, "inner_indent": 2,
               "body_residue": []}

        def _emits(leaves, src=None):
            q = dict(_fp, leaves=leaves)
            if src is not None:
                q["src"] = src
            try:
                emit(q, apply=False)
                return "emitted"
            except ValueError as e:
                return str(e).split("\n")[0]

        check("a leaf whose body IS the source body emits",
              _emits([("L", _g3, ["x"], ["  x = 1"])]), "emitted")
        # ⚑ THE FAILURE MODE THAT SHIPPED THREE TIMES IN ONE DAY, all found only by
        # reading emitted Agda — the slowest instrument available.
        check("⚑ Ⓡ7: an INVENTED body line is refused before any write",
              _emits([("L", _g3, ["x"], ["  x = 1", "  y = 2"])]),
              "refusing to emit — emitted body line traces to no source line:")
        # ⚑ AND THE GUARD MUST NOT REFUSE Ⓡ8's OWN RENAME. A byte-equality check
        # would reject the tool's correct behaviour here, which is why the
        # invariant is provenance-modulo-declared-rename, not equality.
        # ⚑⚑ THE INVERSE IS A FALLBACK, NOT THE PRIMARY TEST — it fires on names
        # that were never renamed. MEASURED on `Cyclic/Base.agda`: leaf
        # `HasOrderPerm` defines `σ-HasOrderPerm`, and the verbatim source line
        #     σ-HasOrderPerm : HasOrderPerm σ (suc n)
        # unlocalizes to `σ : HasOrderPerm σ (suc n)` because `-HasOrderPerm` LOOKS
        # like a `-<leaf>` suffix — though that root has no `variable` block, so Ⓡ8
        # renamed nothing. Three verbatim lines were reported INVENTED and a correct
        # emit refused. A line present verbatim is conserved, full stop.
        check("⚑⚑ a leaf named after a TYPE its body mentions is not 'invented'",
              _emits([("HasOrderPerm", _g3, ["σ-HasOrderPerm"],
                       ["  σ-HasOrderPerm : HasOrderPerm σ (suc n)"])],
                     src="module M where\nmodule Over (A : Set) where\n"
                         "  σ-HasOrderPerm : HasOrderPerm σ (suc n)\n"),
              "emitted")
        check("⚑ Ⓡ8's leaf-local rename still traces (the inverse is applied)",
              _emits([("L", _g3, ["x"], ["  x : Poly n-L", "  x = 1"])],
                     src="module M where\nmodule Over (A : Set) where\n"
                         "  x : Poly n\n  x = 1\n"),
              "emitted")
        # ⚑ …but the inverse must be BOUNDARY-ANCHORED, or it would strip a
        # legitimately-hyphenated name and launder an invention into a pass.
        check("⚑ the un-rename does not fire on an unrelated hyphen",
              _emits([("L", _g3, ["x"], ["  x = pad-end"])],
                     src="module M where\nmodule Over (A : Set) where\n"
                         "  x = pad-end\n"),
              "emitted")
        # ⚑ NOTHING IS ON DISK WHEN IT REFUSES, AND THIS MUST BE TESTED UNDER
        # `apply=True` OR IT TESTS NOTHING. My first cut asserted the empty
        # directory after an `apply=False` call, where no write was ever possible
        # — a case that passes whether or not the writes are buffered, which is
        # the tautological-green shape the guard above exists to reject. Under
        # apply, a leaf refused on the SECOND unit would leave the FIRST on disk
        # if the per-leaf write were not deferred past the whole-plan check.
        _mp = os.path.join(d, "M5")
        try:
            emit(dict(_fp, path=os.path.join(d, "M5.agda"), root="M5",
                      leaves=[("Good", _g3, ["x"], ["  x = 1"]),
                              ("Bad", _g3, ["y"], ["  y = 2"])]), apply=True)
            _disk = "emitted"
        except ValueError:
            _disk = sorted(os.listdir(_mp)) if os.path.isdir(_mp) else []
        check("⚑ a refused apply leaves NO leaf on disk (writes buffered past the check)",
              _disk, [])

        # ── Ⓐ1⁴ PRELUDE-STATEMENTS ─────────────────────────────────────────
        # ⚑ MEASURED ON THE LIVE APPLY, NOT HYPOTHESISED. The 22 emitted leaves
        # each carried `open import …Semiring using (Semiring; +-monoid; *-monoid;`
        # — the HEAD of a two-line statement, with `distrib-left; …)` dropped. An
        # unclosed paren: a parse error in every leaf, and the tool reported
        # SUCCESS. `body_prelude` reads STATEMENTS via `group_statements` and is
        # correct; `_inner_plan` bypassed it with an `IMP.match(l)` line filter,
        # which matches only heads. This is `agda-ban-decompose`'s named hazard —
        # *"any pass that treats an import as one line will orphan its tail"* —
        # re-committed in a tool whose sibling function already avoids it.
        _pre = body_prelude(ip)
        # ⚑ THE PRELUDE IS EMITTED BARE — the ban forbids `using`/`as`, and
        # `prune_imports` (the designated next stage) REFUSES those forms by
        # design, so anything the generator emits with them is debt no downstream
        # stage can clear. MEASURED: 672 unused imports across 21 fresh leaves,
        # every one carrying the root's `using (…)` lists and `as Pₙ` aliases.
        # The wrapped `using (Semiring; plus-monoid;\n  distrib-left; absorb-left)`
        # in this fixture must therefore come out as a BARE import — not truncated
        # (the earlier defect) and not carried whole (the ban violation).
        check("⚑ a `using (…)` import is emitted BARE, not carried or truncated",
              [l for l in _pre if "Semiring" in l],
              ["open import Sub.Semiring"])
        check("...so no emitted prelude line carries a ban-violating form",
              [l for l in _pre if " using " in l or " as " in l
               or " renaming " in l or " hiding " in l], [])

        # ── Ⓐ1¹² PRUNE-IN-EMITTER ──────────────────────────────────────────
        # ⚑ AN UNNEEDED IMPORT IS NOT MERELY WASTE — IT IS THE COLLISION
        # GENERATOR. Every leaf inherited the ROOT's whole prelude, so `TimesComm`
        # carried 40 imports to use ONE, and bare-importing `CommutativeRing`
        # (whose FIELD is `*-comm`) beside its own `*-comm` gave
        # `[ClashingDefinition]`. Pruning AFTER emission cannot prevent that: by
        # then the file is written, and the pruner correctly keeps what the
        # definition genuinely uses. So the prune belongs INSIDE the emitter.
        # ⚑ THE FIXTURE MUST USE REAL `Substrate` MODULES. `should_keep`'s FIRST
        # line is `if not (mod.startswith("Substrate") …): return True` — so a
        # `Sub.Eq` fixture exercises only the keep-everything branch and proves
        # nothing about pruning. My first version of this case did exactly that
        # and "passed" against a no-op. Probe against a module the def-index
        # actually knows, and a body that demands one of its names.
        _kept = _needed(["open import Substrate.Foundation.Eq",
                         "open import Substrate.Algebra.Magma"],
                        ["x = refl"])
        check("⚑ an import no body token demands is DROPPED during emission",
              _kept, ["open import Substrate.Foundation.Eq"])
        # ⚑ KEEP-BIASED: the predicate's own rule is *"every uncertain branch
        # returns True: no evidence is never evidence of death"*. A non-Substrate
        # module has no provision index here, so it must survive untouched.
        check("...but an unknown-provision import is KEPT, never guessed away",
              _needed(["open import Data.Nat"], ["x = 1"]), ["open import Data.Nat"])
        check("...and every emitted prelude has BALANCED delimiters",
              all(_balanced("\n".join(_pre)) for _ in [0]), True)

        # ── Ⓐ1⁶ EMIT-INSPECT-GATE ──────────────────────────────────────────
        # ⚑ THE TOOL WROTE 22 FILES WITH A PARSE ERROR IN EVERY ONE AND SAID
        # `WROTE`. A generator that cannot detect syntactically impossible output
        # is a generator whose success message means nothing — the same class as a
        # census reporting zero because it read the wrong attribute. The gate is
        # deliberately SHALLOW (delimiter balance, not a parse): it must never be
        # the reason a correct split is refused, only the reason an incoherent one
        # is not written.
        check("a leaf with unbalanced delimiters is REFUSED, not written",
              _emit_blockers([("Bad", [], ["x"],
                               ["open import M using (a;", "y = 1"])]),
              ["Bad: unbalanced delimiters in the emitted leaf"])
        check("a well-formed leaf is NOT refused",
              _emit_blockers([("Ok", [], ["y"], ["y = 1"])]), [])

        # ── Ⓐ1⁵ BARREL-CARRY ───────────────────────────────────────────────
        # ⚑ THE DEFECT A COMPILE WOULD NOT HAVE CAUGHT. `body_units` classifies
        # `open … public` as barrel-not-unit (right — it defines nothing), so the
        # first apply carried none of the live root's 16 `open Pₙ.Over … public`.
        # The rewritten root exported 22 coefficient names and NONE of the graded
        # polynomial ring its 36 consumers import — and it would have TYPECHECKED,
        # surfacing only at those consumers, in Ⓐ2, long after. Reading the output
        # found in minutes what the proposed verification step would have missed.
        check("⚑ a body `open … public` is RESIDUE, carried, not dropped",
              any("open G.Over" in t for _ln, t in ip.get("body_residue", [])), True)
        _rt2 = root_text(ip, _re3)
        check("...and it lands in the rewritten root, AFTER the re-opens",
              _rt2.index("open G.Over") > _rt2.index("Sub.Inner.Zero"), True)
        check("residue carries PROVENANCE — (1-based lineno, text), as parse returns",
              all(isinstance(ln, int) and ln > 0
                  for ln, _t in ip.get("body_residue", [])), True)
        # ⚑ CONSERVATION AS A PARTITION, COUNTED — and the WEAK form of this case
        # is why the second apply shipped. It compared STRIPPED STRINGS AGAINST A
        # SET, so a line appearing in BOTH a unit and the residue satisfied it:
        # the check could not observe double-counting, which was the entire defect
        # it was written to catch (`opOf`/`+-inverseʳ`/`𝟘 𝟙 : A` duplicated into a
        # leaf AND the root). A membership test cannot see a multiset error.
        # Assert the COUNT: every non-blank body line is accounted for exactly once.
        _body_lines = [l for l in ip["src"].split("\n")[ip["inner_hdr"] + 1:]
                       if l.strip() and not l.lstrip().startswith("private")]
        _acc = [l for _l, _p, _d, b in ip["leaves"] for l in b if l.strip()] \
            + [t for _ln, t in ip.get("body_residue", [])]
        check("⚑ conservation is a PARTITION: every body line accounted for ONCE",
              len(_acc), len(_body_lines))
        check("...and the multiset MATCHES, so nothing is duplicated or invented",
              sorted(l.strip() for l in _acc),
              sorted(l.strip() for l in _body_lines))

    ok = sum(1 for _n, g, _got, _w in cases if g)
    for n, g, got_, w in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got_!r} want {w!r}")
    print(f"split_telescoped selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        sys.exit(2)
    # ⚑ THE DISPATCH BRANCH IS THE HALF THAT GETS FORGOTTEN. `plan()` grew a
    # `module=` parameter and this entry point did not pass it — so the capability
    # existed and was unreachable from the CLI, which is the `rewire_only` defect
    # (`pycodemod --calls`: written, documented, ZERO callers) in the tool that
    # documents it.
    _mod = None
    if "--module" in sys.argv:
        _i = sys.argv.index("--module")
        _mod = sys.argv[_i + 1] if len(sys.argv) > _i + 1 else None
        args = [a for a in args if a != _mod]
    p = plan(args[0], module=_mod)
    if p is None:
        print(f"{args[0]} is not a telescoped root (its header ends in `where`)")
        print("   ⚑ its telescope may be on an INNER module — pass "
              "`--module <Name>` to target it\n"
              "     (`split_inner_module.py <file>` lists the candidates).")
        sys.exit(0)
    if "inner" in p:
        print(f"⚑ INNER-MODULE target: `module {p['inner']}` "
              f"(the file's own header is bare)")
    print(f"root {p['root']}  —  {len(p['groups'])} parameter(s), {len(p['leaves'])} leaf/leaves")
    for leaf, params, defines, _blk in p["leaves"]:
        names = [n for ns, _ in params for n in ns]
        print(f"   {leaf:<28} params={len(names):<2} {names}")
        print(f"   {'':<28} defines={defines}")
    # ⚑ THE DRY RUN WAS SILENT ON THE HALF THAT FAILED TWICE. Both reverted
    # applies were diagnosed by READING the written files — the preview reported
    # leaves and re-opens and nothing about the residue, which is where the barrel
    # went missing (apply 1) and where real definitions were duplicated (apply 2).
    # A preview that cannot show the failure mode is not a preview of the write.
    if p.get("body_residue"):
        print(f"\n   RESIDUE — {len(p['body_residue'])} body line(s) in no unit, "
              f"carried into the rewritten root:")
        for _ln, _t in p["body_residue"]:
            print(f"     {_ln:>5}  {_t.strip()[:80]}")
    elif "inner" in p:
        print("\n   RESIDUE — none (every body line landed in a unit)")
    ap = "--apply" in sys.argv
    # ⚑ REFUSE A SECOND APPLY.  Zero units means the root is already split out;
    # applying would delete every leaf and blank the root's re-opens.
    if not p["leaves"]:
        print(f"{p['root']}: 0 units — this root is ALREADY SPLIT "
              f"(it holds only its telescope and re-opens).")
        print("   REFUSING to apply: a second run would delete the leaves and "
              "erase the re-opens.\n"
              "   To re-do the split, restore the flat source first:\n"
              f"     python3 scratch/recover_presplit.py {p['root']} --restore=<ref>")
        sys.exit(0)
    # ⚑ SNAPSHOT: the apply DELETES the old split's leaves and REWRITES the root.
    # Those leaves are untracked, so `guard` (which copies them aside) is the only
    # instrument that can hold them — a tag cannot (§57).  That reasoning is intact
    # and is why `paths=` below is the root PLUS the existing leaf directory.
    # ⚑ ONE ACT, AND NO LONGER UNDER `if ap:`.  The guard was correct wherever it
    # ran, and it ran only once `ap` was already True (bound at :1989) — so the
    # UNSTATED case walked past it and printed "Dry run", which is precisely the
    # debt this ratchet counts. `require_at_entry` asks at the invocation and takes
    # the same snapshot on a stated `--apply`, so the two cannot drift apart again.
    import edit_snapshot
    _old = ([os.path.join(args[0][:-5], f)
             for f in os.listdir(args[0][:-5])
             if f.endswith(".agda")] if os.path.isdir(args[0][:-5]) else [])
    edit_snapshot.require_at_entry(f"split_telescoped {p['root']}",
                                   paths=[args[0]] + _old)
    written, reopens = emit(p, apply=ap)
    for w in written:
        print(f"   {'WROTE' if ap else 'would write'} {w}")
    for r in reopens:
        print(f"   root re-opens: {r}")
    if not ap:
        print("\nDry run — pass --apply to execute.")
