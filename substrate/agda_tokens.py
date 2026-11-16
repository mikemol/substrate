# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Read the tokens an Agda body mentions, and bound a name the way Agda names actually end.

⚑⚑⚑ THE FIFTH UNIT OUT OF THE `agda_lex` PROMOTION. That module is reached from 91 BARE import
sites across 63 files with ZERO dotted ones (`module_importers agda_lex`), so the tree's most
shared reader is unimportable from any packaged consumer. `mask_comments` came out as
`substrate.agda_mask`, naming as `substrate.agda_naming`, statement segmentation as
`substrate.agda_statements`, telescopes as `substrate.agda_telescope`; this is token reading.

⚑⚑⚑ EVERY RECOVERY HERE IS A MEASURED FALSE VERDICT IN THE DANGEROUS DIRECTION — a LIVE import
read as DEAD, which callers act on BY DELETING IT. That is why this cannot be rewritten from
memory, and why the recoveries are not defensive polish:

  * `\b` IS WRONG FOR AGDA, MEASURABLY. Python's `\b` is a `\w`/non-`\w` transition, but an
    Agda name may be entirely non-`\w`, may contain `-`, or may END in a non-`\w` character.
    Measured against the def index: **1269 of 10831 defined names (11.7%) are invisible to a
    `\b`-bounded regex** — and the sites using one are WRITE paths and a pre-commit gate, where
    a silent non-match is a silent no-op. Live witness: a rewrite tool failed to rewrite a name
    ending in a backtick.
  * A QUALIFIED HEAD IS EVIDENCE. `Magma._·_` yields `Magma`, and in this repo a RECORD is both
    a module and a definition, so that token IS the proof the import is live. Measured
    corpus-wide: removing this recovery takes the count 4088 → 4104, and ALL 16 extra are false
    positives with genuine qualified uses.
  * A STANDALONE PUNCTUATION RUN IS A REAL TOKEN. `,` is a delimiter, so an infix pair
    constructor produced NO token at all and its providing module read as dead — the import was
    dropped and the constructor went out of scope.
  * A BRACKET-DELIMITED MIXFIX IS BUILT FROM DELIMITERS, so the splitter shreds it and the
    whitespace form never matches when it is used applied or at line end. Measured: a split
    emitted a correct sibling edge and the prune then DELETED it, failing isolate-check.

⚑⚑ AND OMITTING THEM REPRODUCED THE BUG IN A SECOND TOOL THE SAME DAY. One tool carried all
three recoveries with their incidents written down; another was written without them and
immediately re-reported an infix constructor as UNUSED while it was used two lines later. *A
recovery whose incident is recorded in one file and absent in another is not documentation — it
is a defect waiting for the next reader.* One home, and these comments are the argument.

⚑ `mixfix` IS PASSED IN, NEVER COMPUTED HERE. The caller owns which name-set bounds the
verbatim scan, and reaching for a definition index from inside a lexer would invert the
dependency: this is the layer a def-index reads, not the reverse.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

#: The characters the body tokenizer splits on — and which some NAMES are built FROM.
#: ⚑ That collision is the whole reason this module exists; naming the set once is what keeps
#: the splitter and the mixfix recovery from disagreeing about which is which.
BODY_DELIMS = "(){}[];,"

_BODY_TOK = re.compile(r"[^\s(){}\[\];,]+")
_PUNCT_RUN = re.compile(r"(?<=\s)([(){}\[\];,]+)(?=\s)")


def _found(pattern: re.Pattern[str], text: str, group: int = 0) -> list[str]:
    """Return every match of `pattern` in `text`, as text.

    ⚑⚑ `finditer` RATHER THAN `findall`, AND THE CHECKER FORCED IT. `findall` is declared as
    returning `list[Any]`, and `Any` cannot be spelled in this tree — even a `str(...)` inside a
    comprehension over it is still an expression of type `Any`. `finditer` yields `Match[str]`,
    so the value is typed AT the seam rather than laundered one step past it.

    ⚑ AND THAT IS THE RIGHT PLACE ANYWAY: a caller DELETES imports based on what this module
    returns, so an unchecked value would otherwise sit in the most load-bearing position here.

    ⚑ `group` NAMES WHICH CAPTURE TO TAKE. `findall` silently returns group 1 when a pattern has
    one and group 0 when it does not — behaviour keyed on the pattern's shape rather than on the
    caller's intent, which is the kind of implicitness that hides a wrong answer.
    """
    return [m.group(group) for m in pattern.finditer(text)]


def word(name: str) -> re.Pattern[str]:
    r"""Return a regex matching the Agda name `name`, bounded as Agda names actually end.

    ⚑⚑ NOT `\b`, AND THE DIFFERENCE IS 11.7% OF THE CORPUS. A `\b`-bounded pattern is blind to
    1269 of 10831 defined names, because Agda names may be wholly non-word characters, may
    contain a hyphen, or may end in one. The sites using such a pattern are WRITE paths and a
    pre-commit gate, where a silent non-match is a silent no-op rather than an error.

    ⚑ AGDA NAMES ARE DELIMITED BY WHITESPACE AND BRACKETS, not by word characters, so that is
    exactly what the lookarounds assert.
    """
    return re.compile(r"(?<![^\s(){}\[\];,])" + re.escape(name) + r"(?![^\s(){}\[\];,])")


def mixfix_delims(names: Iterable[str]) -> set[str]:
    """Return the declared names whose SECTIONS ARE DELIMITERS.

    ⚑ AN `_` HOLE IS REQUIRED, because that is what makes a name mixfix. Without it the set
    picks up tokenizer artifacts whose verbatim presence in a body proves nothing — and since
    this set can only ADD tokens, an artifact would SUPPRESS a legitimate dead-name verdict,
    which is the dangerous direction.
    """
    return {n for n in names if "_" in n and any(c in BODY_DELIMS for c in n)}


def body_tokens(body: str, mixfix: Iterable[str] = ()) -> set[str]:
    """Return every token `body` mentions, WITH the recoveries a naive split loses.

    ⚑⚑⚑ EACH RECOVERY IS A MEASURED FALSE-DEAD VERDICT — see the module docstring. A caller
    acts on this set by DELETING what it does not name, so a missing token is not a smaller
    answer: it is a deleted import and a name that goes out of scope.

    ⚑ THE INPUT IS EXPECTED COMMENT-MASKED. `substrate.agda_mask.mask_comments` is the
    authority; a commented-out use is not a use, and masking here would re-mask text a caller
    has usually already masked.
    """
    toks: set[str] = set(_found(_BODY_TOK, body))
    # ⚑ THE QUALIFIED HEAD: a record is both a module and a definition here, so the head token
    # is the evidence the import is live.
    toks |= {t.split(".")[0] for t in list(toks) if "." in t}
    # ⚑ A STANDALONE PUNCTUATION RUN is a real token — an infix constructor otherwise yields
    # none at all. Group 1 is named explicitly: the pattern captures, and taking group 0 would
    # include the surrounding whitespace the lookarounds assert.
    toks |= set(_found(_PUNCT_RUN, body, 1))
    # ⚑ A BRACKET-DELIMITED MIXFIX is built FROM delimiters, so only a verbatim scan finds it.
    toks |= {nm for nm in mixfix if nm in body}
    return toks
