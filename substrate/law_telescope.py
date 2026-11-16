# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Parse an Agda type telescope far enough to tell a law INSTANCE from a law APEX.

⚑⚑⚑ THIS IS THE DISCRIMINATOR THE WHOLE APEX GATE RESTS ON, AND IT HAD NO CASES. A law
INSTANCE has CONCRETE `F`, `s` — named top-level defs. A law APEX has them BOUND, as
parameters, with the law itself a hypothesis. `scripts/law_motif_apex.py`'s own header records
that this distinction is what "kills the false positives a flat regex produces" — and the
functions computing it sat in a file carrying ~90 ruff findings, so nothing could test them and
no repair could land beside them.

⚑⚑ THE ORIGIN IS A DRAIN TARGET FOR A MEASURED REASON, NOT FOR TIDINESS (gate-F65). Its body
runs at import with no `main`, and its tree walk accumulates every stripped Agda source into one
string by repeated concatenation — quadratic, ~22s of sys time. That string feeds only a token
counter, which feeds only the bare report's convergence line, and the `--check` branch reads
neither. The blocking gate therefore pays ~30s to build a counter it never uses. This module is
the first unit out: the parsing has no I/O at all, so it can be lifted and cased without
touching the walk that is the actual cost.

⚑ APPROXIMATE BY DESIGN, AND THE ORIGIN SAYS SO. A focused paren-aware parser, not full Agda;
it misses infix and `where`-bound laws. That is a DOCUMENTED LOWER BOUND rather than a defect —
reporting it as complete is what would turn a missing apex into a false green.

⚑⚑ HOMOMORPHISM IS DELIBERATELY NOT MATCHED, and the reason is carried rather than inferred:
the bare law has no clean parametric apex and the heuristic was unreliable. A motif that cannot
name its apex would report every instance as an APEX-CANDIDATE forever.
"""

from __future__ import annotations

import re

#: The bracket characters Agda telescopes nest with — ordinary, implicit, and instance.
OPEN = "({⦃"
CLOSE = ")}⦄"

#: A token that can name a def. ⚑ NEGATIVE: anything without structural punctuation, because
#: Agda identifiers admit almost every glyph (`≡-trans`, `∘`, `F₂-to-R`) and an allow-list would
#: silently drop the ones that matter most.
IDENT = re.compile(r"^[^\s()\[\]{}⦃⦄:;,]+$")

#: Tokens that match `IDENT` but are syntax, never names.
_NOT_NAMES = ("→", "≡", "∀", "λ")

#: The motif labels, spelled exactly as the origin renders them so a verdict is comparable.
INVOLUTION = "involution          f (f x) ≡ x"
RETRACTION = "retraction/section  f (g x) ≡ x"
IDEMPOTENT = "idempotent          f (f x) ≡ f x"


def depth_split(text: str, seps: list[str]) -> list[str]:
    """Split `text` on any separator in `seps`, at bracket depth 0.

    ⚑ DEPTH-AWARE BECAUSE A TELESCOPE NESTS. Splitting `(A → B) → C` on `→` textually yields
    three segments where the type has two, and every downstream judgement about which segment is
    the RESULT would then be about the wrong string.
    """
    parts: list[str] = []
    depth = 0
    cur = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char in OPEN:
            depth += 1
            cur += char
            i += 1
            continue
        if char in CLOSE:
            depth -= 1
            cur += char
            i += 1
            continue
        if depth == 0:
            hit = next((sep for sep in seps if text.startswith(sep, i)), None)
            if hit:
                parts.append(cur)
                cur = ""
                i += len(hit)
                continue
        cur += char
        i += 1
    parts.append(cur)
    return parts


def unwrap(text: str) -> str:
    """Peel fully-enclosing parentheses: `(g x)` becomes `g x`.

    ⚑ ONLY WHEN THEY ENCLOSE THE WHOLE STRING. `(f x) (g y)` opens and closes with parens and is
    NOT wrapped; stripping them would produce `f x) (g y` and every spine read off it would be
    nonsense. The depth walk is what tells the two apart.
    """
    got = text.strip()
    while len(got) >= 2 and got[0] == "(" and got[-1] == ")":  # noqa: PLR2004
        depth = 0
        whole = True
        for j, char in enumerate(got):
            if char in OPEN:
                depth += 1
            elif char in CLOSE:
                depth -= 1
                if depth == 0 and j != len(got) - 1:
                    whole = False
                    break
        if not whole:
            break
        got = got[1:-1].strip()
    return got


def spine(text: str) -> tuple[str, list[str]]:
    """Return the application spine: `f (g x) y` becomes `("f", ["(g x)", "y"])`.

    ⚑ LEFT-ASSOCIATIVE, as application is. The HEAD is what names the function a law is about,
    and the LAST argument is where the inner application sits — both are read positionally here
    rather than searched for, because a search would find the first match rather than the right one.
    """
    got = unwrap(text)
    parts = [p for p in depth_split(got, [" "]) if p.strip()]
    if not parts:
        return ("", [])
    return (parts[0].strip(), [p.strip() for p in parts[1:]])


def is_ident(text: str) -> bool:
    """Report whether `text` can name a definition rather than being syntax."""
    got = text.strip()
    return bool(IDENT.match(got)) and got not in _NOT_NAMES


def result_and_hyps(telescope: str) -> tuple[list[str], str]:
    """Split a telescope on top-level arrows: `(hypotheses, result)`.

    ⚑ THE RESULT IS THE LAST SEGMENT, and that is what a law INSTANCE is stated in. A reader
    taking the first would classify the hypotheses of an apex as its conclusion — exactly
    inverting the distinction this module exists to draw.
    """
    segs = [x.strip() for x in depth_split(telescope, ["→", "->"]) if x.strip()]
    return (segs[:-1], segs[-1]) if segs else ([], telescope)


def binder_groups(telescope: str) -> list[str]:
    """Return the contents of each TOP-LEVEL binder group.

    ⚑⚑ NOT ARROW-SEPARATED, WHICH IS THE WHOLE REASON THIS IS NOT A SPLIT. Agda JUXTAPOSES
    binders — `(F : A)(s : B)` has no arrow between them — so a reader that split on `→` would
    see one group where there are two and miss every name bound after the first.
    """
    groups: list[str] = []
    depth = 0
    cur = ""
    for char in telescope:
        if char in OPEN:
            if depth == 0:
                cur = ""
            else:
                cur += char
            depth += 1
        elif char in CLOSE:
            depth -= 1
            if depth == 0:
                groups.append(cur)
            else:
                cur += char
        elif depth >= 1:
            cur += char
    return groups


def bound_names(telescope: str) -> set[str]:
    """Return every name the telescope BINDS — `(F : …)`, `{a b : …}`.

    ⚑⚑⚑ THIS SET IS THE DISCRIMINATOR. A law over names in it is an APEX (parametric over the
    law); a law over names NOT in it, that are defined elsewhere, is an INSTANCE. Get this set
    wrong in either direction and the gate either demands an apex that exists or accepts a
    cluster that has none.
    """
    names: set[str] = set()
    for group in binder_groups(telescope):
        if " : " not in group:
            continue
        head = group.split(" : ", 1)[0].replace("{", " ").replace("}", " ")
        names.update(n for n in head.split() if is_ident(n))
    return names


def eq_sides(seg: str) -> tuple[str, str] | None:
    """Return `(lhs, rhs)` when `seg` is a top-level equation, else None.

    ⚑ EXACTLY TWO SIDES. A segment with several `≡` at depth 0 is not an equation this parser
    understands, and guessing which pair to take would be a judgement no case could pin.
    """
    parts = depth_split(seg, ["≡"])
    if len(parts) != 2:  # noqa: PLR2004
        return None
    return (parts[0].strip(), parts[1].strip())


def _law_over(head: str, inner: str, rh: str, rargs: list[str], x: str) -> str | None:
    """Return which motif `head`/`inner` states, or None.

    ⚑ SPLIT OUT SO `classify` STAYS ONE JOB. The origin's single function carried seven returns
    and the per-file gate flags that shape; the split is the gate's own reading of the grain.
    """
    # retraction / section: f (g x) ≡ x — the rhs is the bare variable.
    if not rargs and rh == x:
        return INVOLUTION if head == inner else RETRACTION
    # idempotent: f (f x) ≡ f x — the rhs re-applies the same function.
    if head == inner and rh == head and rargs and unwrap(rargs[-1]) == x:
        return IDEMPOTENT
    return None


def classify(seg: str) -> tuple[str, str, str, str] | None:
    """Match a result type against a law motif: `(motif, F, s, x)`, or None.

    ⚑ THE TRIPLE IS RETURNED, NOT JUST THE MOTIF, because the caller must then ask whether `F`
    and `s` are BOUND. A classifier returning only the motif would make the instance/apex split
    impossible downstream — which is the distinction the gate is built on.
    """
    eq = eq_sides(seg)
    if not eq:
        return None
    lhs, rhs = eq
    head, fargs = spine(lhs)
    rh, rargs = spine(rhs)
    if not is_ident(head) or not fargs:
        return None
    inner, sargs = spine(fargs[-1])
    if not is_ident(inner) or not sargs:
        # ⚑ HOMOMORPHISM `f (x ⊕ y) ≡ f x ⊗ f y` LANDS HERE AND IS DELIBERATELY UNMATCHED: the
        # bare law has no clean parametric apex, so matching it would report every instance as
        # a candidate forever.
        return None
    x = unwrap(sargs[-1])
    motif = _law_over(head, inner, rh, rargs, x)
    return None if motif is None else (motif, head, inner, x)
