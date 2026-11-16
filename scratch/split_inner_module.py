#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Split an INNER parameterized `module … where` into telescoped sibling leaves.

⚑ FAMILY MAP (every sibling splitter/repair and the precondition that selects it):
    .claude/skills/agda-ban-decompose/telescope-family.md   (agda_imports.TELESCOPE_MAP)
The two refusals quoted below are this family's SELECTION MECHANISM and must not be
merged away; the map records that, and reaches the repair tools no splitter names.

⚑ THE GAP BOTH EXISTING SPLITTERS DECLINE, EACH CORRECTLY.

  * `split_lemmas` refuses a parameterized block in writing (its `:10-11`: *"a
    `module … where` block (parameterized or named) plus its indented body —
    these CANNOT be split, the telescope binds the whole block"*).  Right, for a
    block treated as one unit — it reports `Over` as a single 49-line lemma.
  * `split_telescoped` handles a telescope on the FILE HEADER (`telescope_span`).
    `FromCommRing`'s header is bare `module … where`; the telescope is on the
    INNER `module Over {A : Set} (CR : CommutativeRing A) where`, so it refuses
    with *"not a telescoped root (its header ends in `where`)"*.

Neither refusal is wrong and the shape has no owner.  Measured: `FromCommRing.Over`
exposes 14 coefficient names to **36 consumers**, and any consumer that also opens
an `Algebra.F2.*` leaf gets [AmbiguousName] on `𝟘`/`𝟙`/`+-assoc`/… — three found
by compiling before `agda_defs --double-route` existed, 27 candidates after.

⚑ WHY SPLITTING IS THE FIX AND NOT DEDUPLICATION AT THE CONSUMER.  Dropping the
redundant leaf import per consumer works (done ×3) but ENTRENCHES the bundle: 27
modules keep taking 14 names to use one.  The operator's framing is that the
durable answer is upstream — *once bare imports carry individual symbols, `as`
becomes permissible for disambiguating*, because a one-name import names the
thing it disambiguates rather than munging a namespace.

⚑ THE LEAF CONTRACT, taken from `split_telescoped`'s measured ground truth rather
than invented: a leaf carries the MINIMAL telescope subset its body needs (closure
to fixpoint, since a needed parameter's TYPE may mention another), and the root
re-opens each leaf APPLIED to exactly those arguments so every downstream name
still resolves.  Both halves matter — a leaf taking the whole telescope forces
consumers to supply parameters they do not need.

⚑ AND THE `private` SCAFFOLDING IS THE REAL OBSTACLE, not the telescope.
`Over`'s body opens with `private R = ring CR; SR = semiring R; +M = +-monoid SR;
*M = *-monoid SR; opOf = …` — EVERY definition below depends on them.  A
one-definition-per-leaf split must either duplicate that scaffolding into each
leaf or promote it to a shared leaf.  `private` is banned here anyway, so the
promotion is the ban's remedy and the split's precondition at once.

    split_inner_module.py <file>                 # report the plan
    split_inner_module.py <file> --module <Name> # pick one of several inner modules
    split_inner_module.py --selftest             # fixture-driven; no live tree
    split_inner_module.py <file> --apply         # NOT IMPLEMENTED — see below

⚑⚑ THIS TOOL PLANS AND DOES NOT WRITE, DELIBERATELY.  The emit step needs
decisions this analysis cannot make alone (see the plan's OPEN QUESTIONS), and a
generator that guesses them would produce 14 leaves nobody vetted.  Planning is
the half that is mechanical; the scoping call is the operator's.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agda_lex


def inner_modules(src):
    """Every inner `module … where` with a telescope — the split candidates.

    Skips the file's own top-level module (indent 0 with no parameters is the
    header, and a parameterised top-level header is `split_telescoped`'s job).
    """
    out = []
    for name, indent, params, b0, b1 in agda_lex.module_scopes(src):
        if indent == 0 and not params:
            continue                       # the file header itself
        out.append((name, indent, params, b0, b1))
    return out


# ⚑ THE HEAD MAY CARRY ARGUMENTS: `f a = e` and `w₁ ≉ w₂ = e` are clauses of `f`
# and `_≉_`. The original `([^\s(){};]+)\s*(?::|=)` required the name to sit
# IMMEDIATELY before the `:`/`=`, so any clause with a pattern argument did not
# match at all — it fell through to the not-a-def-head branch and was ORPHANED from
# the signature above it (measured: `+-inverseʳ a = trans …` in residue while
# `+-inverseʳ : …` was in a unit, so the clause would have been DUPLICATED).
# The `:` form stays STRICT — a signature is `name : T`, and admitting arguments
# there would swallow a type-level application.
_DEF_HEAD = re.compile(r"^(\s*)(?!--)([^\s(){};]+)\s*:")
_DEF_CLAUSE = re.compile(r"^(\s*)(?!--)([^\s(){};]+)(?:\s+[^=]*?)?\s*=")


def body_units(lines, b0, b1, indent):
    """[(name, [lines], is_private)] — the inner module's own definitions.

    A unit is a definition head at the module's body indent plus everything
    indented deeper, which is the same rule `split_lemmas` uses one level up.
    `private` blocks are reported as such: they are the scaffolding every other
    unit depends on, and they cannot simply be dropped.
    """
    # ⚑ TWO DEFECTS IN THE FIRST CUT, both visible in its own output.
    #
    # (1) `private` NEVER RESET. It is an indented BLOCK, not a mode: everything
    #     under it is deeper than the `private` keyword's own indent, and the
    #     block ends when indentation returns. A sticky flag put all 25 units in
    #     the scaffolding and left SPLITTABLE empty — a census reporting nothing
    #     to split for a module that is 14 splittable names.
    #
    # (2) A SIGNATURE AND ITS CLAUSES ARE ONE UNIT. `+-comm : …` on one line and
    #     `+-comm = …` on the next are the same definition; keying each `name :`
    #     or `name =` as a new unit reported `+-comm`, `neg`, `+-inverseˡ` TWICE.
    #     Same name, consecutive → continue the open unit.
    # ⚑ (4) Ⓑ6ᶜ²′ — AN INFIX CLAUSE LEADS WITH ITS LEFT OPERAND. Ⓐ1⁹ taught this
    #     reader that `f a = e` continues `f`, because the NAME leads. An infix
    #     definition does not: `[] +P [] = []` leads with a PATTERN and
    #     `a ·c [] = []` with a BOUND VARIABLE, so each opened a bogus unit named
    #     `[]` / `a`, and `_+P_` kept only its signature. MEASURED on
    #     `Graded/Defs.agda`: 11 planned leaves, four defining NOTHING (fragments
    #     of `+P`/`·c`/`*P`), with real clauses and every `infixl` in residue.
    #     An operator's own name appears SECOND in its clauses; scan for it.
    _ops = set()
    for i in range(b0, min(b1 + 1, len(lines))):
        m = re.match(r"^\s*(?:infix[lr]?\s+\d+\s+)?(_\S+_)\s*(?::|$)", lines[i])
        if m:
            _ops.add(m.group(1))
    _bare_op = {o.strip("_"): o for o in _ops}

    units = []
    cur, name, priv = [], None, False
    priv_indent = None                 # set while inside a `private` block
    body_indent = None
    for i in range(b0, min(b1 + 1, len(lines))):
        raw = lines[i]
        if not raw.strip():
            if cur:
                cur.append(raw)
            continue
        ind = len(raw) - len(raw.lstrip())
        if raw.lstrip().startswith("private"):
            if cur:
                units.append((name, cur, priv))
                cur, name = [], None
            priv_indent = ind
            continue
        if priv_indent is not None and ind <= priv_indent:
            priv_indent = None         # dedented out of the private block
        if body_indent is None or (priv_indent is None and ind < body_indent):
            body_indent = ind
        if ind <= body_indent:
            # ⚑ Ⓑ6ᶜ²′ — resolve an INFIX line to the operator it belongs to,
            # BEFORE the name-leads matchers run. Three shapes, one owner:
            #   `infixl 6 _+P_`         a fixity declaration NAMES its operator
            #   `[] +P [] = []`         a clause whose SECOND token is the operator
            #   `a ·c (x ∷ p) = …`      ditto, with a bound variable leading
            _op = None
            _t = raw.split()
            if len(_t) >= 3 and _t[0] in ("infixl", "infixr", "infix") \
                    and _t[2] in _ops:
                _op = _t[2]
            elif "=" in raw and _bare_op:
                # ⚑ THE OPERATOR IS NOT ALWAYS THE SECOND TOKEN. `[] +P []` puts
                # it there, but `(x ∷ u) +P (y ∷ v)` leads with a PARENTHESISED
                # pattern, so `+P` sits at index 2 — and a longer pattern moves it
                # further. Scan the left-hand side (everything before the first
                # `=`) for a known operator instead of fixing its position.
                _lhs = raw.split("=", 1)[0].split()
                for _tok in _lhs[1:]:          # never the FIRST token: that is
                    if _tok in _bare_op:       # a pattern, and `f x = e` is
                        _op = _bare_op[_tok]   # already the name-leads case
                        break
            if _op is not None:
                if _op == name:
                    cur.append(raw)
                    continue
                if cur:
                    units.append((name, cur, priv))
                name, cur = _op, [raw]
                priv = priv_indent is not None
                continue
            m = _DEF_HEAD.match(raw) or _DEF_CLAUSE.match(raw)
            if m:
                nm = m.group(2)
                if nm == name:         # `f : T` then `f = e` / `f a = e` — one unit
                    cur.append(raw)
                    continue
                if cur:
                    units.append((name, cur, priv))
                name, cur = nm, [raw]
                priv = priv_indent is not None
                continue
            # ⚑ (3) TAIL-ABSORPTION. At BODY indent and not a definition head:
            #     an `open`/`import`/`--` comment belongs to NO definition. The
            #     fall-through below appended it to whatever unit was still open,
            #     so the LAST splittable unit swallowed the whole barrel —
            #     `+-inverseʳ` reported as 29 lines for a ONE-line definition.
            #     Close the unit instead. (Deeper-indented lines still fall
            #     through: those ARE the open unit's continuation clauses.)
            units.append((name, cur, priv))
            cur, name = [], None
            continue
        if cur:
            cur.append(raw)
    if cur:
        units.append((name, cur, priv))
    out = [(n, b, p) for n, b, p in units if n]
    # ⚑ THE UNPLACED LINES ARE RETURNED THROUGH A SIDE CHANNEL rather than in the
    # tuple, so the two existing callers keep their signature. `_conserve` RAISES on
    # invented content (never legitimate) and hands back what belongs to no unit,
    # which the emitter must route to residue and the reporter may show as barrels.
    body_units.unplaced = _conserve(lines, b0, b1, out)
    return out


def _conserve(lines, b0, b1, units):
    """Ⓐ1⁸ — REFUSE to return units that do not reconstruct the source body.

    ⚑ THIS FUNCTION WAS WRITTEN FOR REPORTING AND IS NOW LOAD-BEARING FOR EMISSION,
    and the difference is the whole reason this guard exists. A report tolerates an
    approximate unit; an EMITTER writes it to disk. Three distinct unfaithfulness
    defects shipped from here in one day — tail-absorption (the last unit swallowed
    16 barrel statements), the dedent (indented units returned no `defines`, so zero
    sibling imports), and the two below — each found only by reading emitted Agda.

    ⚑ WHAT IT ACTUALLY CATCHES, measured on `Graded/FromCommRing.agda`. Two shapes,
    and I mis-diagnosed BOTH from the residue before reading the code:

      * `𝟘 𝟙 : A` — `_DEF_HEAD` captures `𝟘` only (`𝟙` sits between the name and
        the `:`), so the unit is named `𝟘` and carries the shared signature whole.
        `𝟙 = ε *M` then opens a SEPARATE unit with a clause and NO signature. Not
        "a synthesized signature" as I first claimed — the line is carried, just
        attached to only one of the two names it declares.
      * `opOf M = …` at indent 4 inside `private`, while `body_indent` is 2: the
        `ind <= body_indent` test fails, so it rides the fall-through into whatever
        unit is open, and is ORPHANED when the private block ends.

    The guard is CONSERVATION, not correctness: it cannot say a unit is well-formed,
    only that the units TOGETHER account for every non-blank body line exactly once.
    That is the same duty `split_lemmas`' guard discharges — it has caught seven
    silent deletions — and the reason to reuse its shape rather than invent a third.
    Raising is right: a caller that emits unverified units writes broken Agda, and
    the reporting caller is better off failing loudly than printing a false census.
    """
    body = [l for l in lines[b0:min(b1 + 1, len(lines))]
            if l.strip() and not l.lstrip().startswith("private")]
    emitted = [l for _n, b, _p in units for l in b if l.strip()]
    pool = list(body)
    extra = []
    for l in emitted:
        if l in pool:
            pool.remove(l)                # multiset difference, as parse does
        else:
            extra.append(l)
    # ⚑ UNPLACED IS NOT AUTOMATICALLY A DEFECT — and my first cut refused on it,
    # firing on the tool's OWN fixture. A barrel line (`open … public`) and a
    # free-standing comment legitimately belong to no unit; that is what RESIDUE is
    # for, and `plan()` already reports barrels separately. A guard that cannot
    # tell "unplaced and recorded" from "unplaced and lost" refuses correct input,
    # which trains the caller to bypass it — worse than no guard.
    #
    # ⚑ SO THE ASYMMETRY IS THE WHOLE POINT. INVENTED is always a defect: a line in
    # no source line means the reader FABRICATED content, and no downstream residue
    # can absorb that. UNPLACED is returned as data for the caller to route.
    if extra:
        raise ValueError(
            "body_units INVENTED lines with no source — refusing to return units "
            "an emitter would write to disk:\n"
            + "".join(f"  INVENTED (in no source line) {l.strip()[:70]}\n"
                      for l in extra))
    return pool


def plan(path, want=None):
    src = open(path, encoding="utf-8", errors="replace").read()
    lines = src.split("\n")
    mods = inner_modules(src)
    if not mods:
        return None
    if want:
        mods = [m for m in mods if m[0] == want]
        if not mods:
            return None
    name, indent, params, b0, b1 = mods[0]
    units = body_units(lines, b0, b1, indent)
    # the `open … public` that forwards a bundle — the barrel inside the module
    barrels = [(i + 1, lines[i].strip()) for i in range(b0, min(b1 + 1, len(lines)))
               if lines[i].lstrip().startswith("open ")]
    return {"path": path, "module": name, "params": params,
            "body": (b0 + 1, b1 + 1), "units": units, "barrels": barrels,
            "all_modules": [m[0] for m in mods]}


def _selftest():
    """Counted from len(cases). Fixture-driven — no live tree.

    ⚑ EVERY CASE HERE IS A DEFECT THIS TOOL SHIPPED IN ITS FIRST RUN, and both
    were visible in its own output: `private` treated as a sticky mode put all 25
    units in the scaffolding and reported ZERO splittable, and a signature/clauses
    pair reported the same name twice. A census that reports nothing to split is
    the `census-green-is-a-fact-about-the-census` shape — it would have read as
    "this module does not decompose".
    """
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    import tempfile
    fixture = (
        "module Fx where\n"
        "module Over {A : Set} (CR : Ring A) where\n"
        "  private\n"
        "    R  = ring CR\n"
        "    op : A → A\n"
        "    op = id\n"
        "  𝟘 : A\n"
        "  𝟘 = ε R\n"
        "  f-comm : (a b : A) → a ≡ b\n"
        "  f-comm = trans\n"
        "  -- a body-indent comment belongs to NO definition\n"
        "  open G.Over 𝟘 public\n"
        "  open H.Over 𝟙 public\n")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "Fx.agda")
        open(p, "w", encoding="utf-8").write(fixture)
        pl = plan(p)
        names_priv = [n for n, _b, pv in pl["units"] if pv]
        names_pub = [n for n, _b, pv in pl["units"] if not pv]

        check("the inner telescope is read, not the file header",
              pl["params"], ["A", "CR"])
        # ⚑ the private BLOCK ends at dedent — not a mode that swallows the rest
        check("⚑ `private` ends at dedent, not at end-of-module",
              names_priv, ["R", "op"])
        check("⚑ post-private definitions are SPLITTABLE, not scaffolding",
              names_pub, ["𝟘", "f-comm"])
        # ⚑ a signature and its clauses are ONE unit
        check("⚑ `f : T` + `f = e` is one unit, not two",
              names_pub.count("f-comm"), 1)
        check("a private signature+clause pair is also one unit",
              names_priv.count("op"), 1)
        check("the body `open … public` is reported as a barrel",
              len(pl["barrels"]), 2)
        # ⚑ TAIL-ABSORPTION. An `open`/`import`/comment at body indent matches no
        # definition head, so the fall-through appended it to whatever unit was
        # still open — the LAST splittable unit swallowed the entire barrel. On
        # the live `FromCommRing` this reported `+-inverseʳ` as 29 lines when its
        # definition is ONE. Harmless in a report that lists barrels separately;
        # a silent-deletion hazard the moment anything EMITS these units, since
        # the leaf would carry 16 `open … public` it must not have.
        last = [b for n, b, pv in pl["units"] if n == "f-comm"][0]
        check("⚑ a trailing `open`/comment is NOT absorbed into the last unit",
              [l for l in last if l.strip()],
              ["  f-comm : (a b : A) → a ≡ b", "  f-comm = trans"])
        check("a file with no inner parameterized module plans nothing",
              plan(os.path.join(td, "Fx.agda"), want="NoSuchModule"), None)

        # ── Ⓐ1⁸ UNIT-READER-CONSERVE ───────────────────────────────────────
        # ⚑ THE GUARD MUST FIRE ON THE SHAPES THAT SHIPPED. Both are from the live
        # `Graded/FromCommRing.agda`, and both produced Agda that was written to
        # disk twice before being caught by READING it:
        #   `𝟘 𝟙 : A`  — one signature line declaring TWO names; `_DEF_HEAD`
        #                captures only the first, so the second name's unit gets a
        #                clause with no signature.
        #   `opOf M =` — a clause at indent 4 (inside `private`) while body_indent
        #                is 2, orphaned when the private block closes.
        multi = os.path.join(td, "Multi.agda")
        open(multi, "w", encoding="utf-8").write(
            "module Mx where\n"
            "module Over (A : Set) where\n"
            "  private\n"
            "    opOf : A → A\n"
            "    opOf M = M\n"
            "  𝟘 𝟙 : A\n"
            "  𝟘 = z\n"
            "  𝟙 = o\n")
        plan(multi)
        _unp = [l.strip() for l in body_units.unplaced]
        # ⚑ THE SIGNATURE LINE IS THE ONE THAT GOES MISSING. `𝟘 𝟙 : A` attaches to
        # the `𝟘` unit, `𝟙 = o` opens its own unit with a clause and NO signature —
        # so nothing is unplaced HERE, but `opOf M = M` (indent 4 while body_indent
        # is 2) is orphaned when the private block closes. That is the shape that
        # reached disk twice.
        # ⚑ THIS CASE ONCE ASSERTED THE DEFECT AS IF IT WERE THE CONTRACT. It
        # demanded `opOf M = M` be REPORTED UNPLACED, which was true of the old
        # reader and is exactly what Ⓐ1⁹ fixed — a clause with arguments now joins
        # its signature. A test that pins current behaviour rather than intended
        # behaviour fails when the bug is fixed, and reads as a regression.
        check("⚑ a private clause WITH ARGUMENTS joins its signature, not residue",
              "opOf M = M" in _unp, False)
        check("...and the private unit carries BOTH its lines",
              [len(b) for n, b, _p in plan(multi)["units"] if n == "opOf"], [2])

        # ── Ⓐ1⁹ ARGUMENT-BEARING CLAUSE ────────────────────────────────────
        # ⚑ `f : T` THEN `f a = e` IS ONE UNIT, and the existing join only handles
        # `f = e`. `_DEF_HEAD` is `([^\s(){};]+)\s*(?::|=)` — for `+-inverseʳ a = …`
        # the text before `=` is `+-inverseʳ a`, which CONTAINS A SPACE, so the
        # pattern does not match at all and the line falls through to the
        # not-a-def-head branch, CLOSING the unit and orphaning the clause from the
        # signature directly above it.
        # MEASURED on the live root: `+-inverseʳ a = trans …` landed in residue
        # while `+-inverseʳ : …` sat in a unit — the clause would have been
        # DUPLICATED into both the leaf and the rewritten root.
        argc = os.path.join(td, "ArgClause.agda")
        open(argc, "w", encoding="utf-8").write(
            "module Ax where\n"
            "module Over (A : Set) where\n"
            "  f : A → A\n"
            "  f a = a\n"
            "  g : A\n"
            "  g = z\n")
        pa = plan(argc)
        _names = [n for n, _b, _p in pa["units"]]
        check("⚑ `f : T` + `f a = e` is ONE unit (argument-bearing clause joins)",
              _names, ["f", "g"])
        check("...so nothing is left unplaced", list(body_units.unplaced), [])

        # ⚑ A COMMENT IS NOT A DEFINITION, AND WIDENING THE HEAD REGEX RE-BROKE
        # THIS. `split_lemmas.defined_names` documents the same false positive one
        # level up — a `----` banner parsed as a definition named `--`, which
        # blocked 3 of 79 files with `APPLIED import references file-local name(s)
        # ['--']`. My `_DEF_CLAUSE` matched a comment whose text contains `=`,
        # producing a live unit literally named `--` on `FromCommRing`. Reusing a
        # tool's ALGORITHM does not inherit the guards it learned; those are
        # separate knowledge and must be re-stated.
        cmt = os.path.join(td, "Cmt.agda")
        open(cmt, "w", encoding="utf-8").write(
            "module Cx where\n"
            "module Over (A : Set) where\n"
            "  -- a banner: x = y is prose, not a definition\n"
            "  ------------------------------------------\n"
            "  h : A\n"
            "  h = z\n")
        check("⚑ a `--` comment never becomes a unit, however it is punctuated",
              [n for n, _b, _p in plan(cmt)["units"]], ["h"])

        # ── Ⓑ6ᶜ²′ INFIX CLAUSE HEADS ───────────────────────────────────────
        # ⚑ AN INFIX CLAUSE LEADS WITH ITS LEFT OPERAND, NOT ITS NAME. Ⓐ1⁹ taught
        # this reader that `f a = e` belongs to `f` — the name leads. An INFIX
        # definition does not:
        #     infixl 6 _+P_
        #     _+P_ : Poly n → Poly n → Poly n
        #     []      +P []      = []
        #     (x ∷ u) +P (y ∷ v) = (x + y) ∷ (u +P v)
        # the clauses lead with `[]` and `(x ∷ u)`. So the reader opened a unit
        # named `[]`, and on `a ·c [] = []` a unit named `a` — the BOUND VARIABLE.
        # MEASURED on `Graded/Defs.agda`: 11 planned leaves, FOUR defining nothing
        # (`Op`, `A`, `P` — fragments of `+P`/`·c`/`*P` split at operator
        # boundaries), with `_+P_`'s own clause and all three `infixl` lines
        # pushed into RESIDUE. Applying that plan would have scattered one
        # definition across four files.
        # ⚑ THE CONSERVATION GUARD WOULD NOT HAVE CAUGHT IT: every line is a real
        # source line, merely mis-assigned. Ⓐ1⁸ catches INVENTED content, not
        # misfiled content — a distinction worth keeping straight.
        inf = os.path.join(td, "Infix.agda")
        open(inf, "w", encoding="utf-8").write(
            "module Ix where\n"
            "module Over (A : Set) where\n"
            "  infixl 6 _+P_\n"
            "  _+P_ : A → A → A\n"
            "  []      +P []      = []\n"
            "  (x ∷ u) +P (y ∷ v) = q\n"
            "  infixl 7 _·c_\n"
            "  _·c_ : A → A → A\n"
            "  a ·c [] = []\n"
            "  h : A\n"
            "  h = z\n")
        _iu = plan(inf)["units"]
        check("⚑ Ⓑ6ᶜ²′: an infix clause joins its OPERATOR, not its left operand",
              [n for n, _b, _p in _iu], ["_+P_", "_·c_", "h"])
        check("...so `_+P_` carries fixity + signature + BOTH clauses (4 lines)",
              [len(b) for n, b, _p in _iu if n == "_+P_"], [4])
        check("...and a clause leading with a BOUND VARIABLE joins too (`a ·c []`)",
              [len(b) for n, b, _p in _iu if n == "_·c_"], [3])
        check("...leaving nothing unplaced", list(body_units.unplaced), [])
        # ⚑ AND IT MUST NOT REFUSE CORRECT INPUT. A barrel line belongs to no unit
        # LEGITIMATELY — that is what residue is for — so unplaced is DATA, not an
        # error. My first cut raised on it and fired on this tool's own fixture.
        _ok_raised = None
        try:
            plan(p)
        except ValueError as e:
            _ok_raised = str(e)
        check("a legitimately-unplaced barrel line does NOT raise", _ok_raised, None)
        check("...and IS reported, so the emitter can route it to residue",
              any("open G.Over" in l for l in body_units.unplaced), True)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"split_inner_module selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def main():
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not argv:
        print(__doc__)
        return 2
    want = None
    if "--module" in sys.argv:
        i = sys.argv.index("--module")
        want = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
        argv = [a for a in argv if a != want]
    if "--apply" in sys.argv:
        print("⚑ --apply is NOT IMPLEMENTED. This tool plans only; the emit step\n"
              "  needs the scoping decisions the plan's OPEN QUESTIONS name, and a\n"
              "  generator that guesses them would write leaves nobody vetted.",
              file=sys.stderr)
        return 2

    p = plan(argv[0], want)
    if p is None:
        print(f"{argv[0]}: no inner parameterized `module … where` found")
        return 0

    print(f"file    : {p['path']}")
    print(f"module  : {p['module']}   telescope: {' '.join(p['params']) or '(none)'}")
    print(f"body    : lines {p['body'][0]}–{p['body'][1]}")
    if len(p["all_modules"]) > 1:
        print(f"⚑ {len(p['all_modules'])} inner modules; planning `{p['module']}` "
              f"(--module to pick another): {', '.join(p['all_modules'])}")

    priv = [u for u in p["units"] if u[2]]
    pub = [u for u in p["units"] if not u[2]]

    print(f"\n=== SCAFFOLDING ({len(priv)} unit(s), currently `private`) ===")
    for n, blk, _ in priv:
        print(f"   {n:<14} {len(blk)} line(s)")
    print("   ⚑ every leaf below depends on these; `private` is banned, so they")
    print("     must become a SHARED LEAF rather than be duplicated per-leaf.")

    print(f"\n=== SPLITTABLE ({len(pub)} unit(s) → one leaf each) ===")
    for n, blk, _ in pub:
        print(f"   {n:<14} {len(blk)} line(s)")

    print(f"\n=== BARREL ({len(p['barrels'])} `open` statement(s) in the body) ===")
    for ln, txt in p["barrels"]:
        print(f"   :{ln}  {txt[:88]}")

    print("\n⚑ OPEN QUESTIONS the plan cannot decide — these are why --apply is absent:")
    print("  1. The barrel consumes the splittable names AS ARGUMENTS. After the")
    print("     split it must import every leaf, which RECONSTITUTES the bundle for")
    print("     anyone opening it — so consumers only stop colliding if they switch")
    print("     to the leaves. Splitting alone does not dissolve the 27 candidates.")
    print("  2. Whether the scaffolding leaf is itself importable, or stays an")
    print("     implementation detail reachable only through the other leaves.")
    print("  3. 36 consumers apply `Over` with 1 argument today. A leaf-per-name")
    print("     split changes what they import but NOT the arity, so the telescope")
    print("     contract is preserved — verified by `agda_defs --telescope`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
