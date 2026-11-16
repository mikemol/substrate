# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run pandoc over a markdown document and hand back its headings.

⚑⚑⚑ FRONTMATTER IS PRESERVED FOR A MARKDOWN WRITER AND MUST NOT BE FOR ANY OTHER, and getting that
backwards blinded five modes for the whole life of the origin. A markdown→markdown round trip has
to re-attach the YAML head byte-for-byte or every normalisation round deletes the document's
metadata. Re-attaching it to JSON prepends `---` to the JSON, so the AST loader dies at character
zero — and the reader reports an empty document rather than a parse failure.

⚑⚑ SO THE RE-ATTACH IS A PREDICATE ON THE WRITER, spelled out rather than folded into the call. The
origin decided it with a `startswith` on a tuple inline at the return, which is correct and
invisible; a named predicate is a thing a case can drive directly, and this is the branch whose
wrong answer is silent.

⚑ THE DEFECT WAS DIAGNOSED BY A PEER, NOT HERE, AND THAT IS RECORDED BECAUSE IT IS THE MECHANISM
WORKING. gabion found it through summit, verified the one-condition fix by hand, and deliberately
did NOT apply it — their copy is a symlink and a local patch would fork the body silently. The
owner is the party who can fix it, and the owner could not see it from inside.

⚑⚑ AND A `+++` (TOML) DOCUMENT NEVER EXHIBITED THE BUG, which is the asymmetry the original report
could not explain. The splitter recognises a `---` fence only, so a TOML-fronted document never
splits, never gets a head re-attached, and the same mode succeeds on it. A defect that fires on one
metadata syntax and not another looks like a defect in the document until someone reads the
splitter.

⚑ A PANDOC FAILURE RAISES RATHER THAN RETURNING EMPTY. An empty return would reach the anchorer as
a document with no headings, which is exactly the silence this drain exists to remove — the reader
must be able to say UNREADABLE where it cannot say ANSWER.

⚑⚑ AND THE GATE REFUSED A SUPPRESSION FOR A RULE IT DOES NOT ENABLE. A first cut carried a `noqa`
for the subprocess-import warning, written from a guess about the configuration rather than from
the checker's own verdict — the same defect as reasoning from a rendering instead of reading the
binding, applied to a linter's rule set.
"""

from __future__ import annotations

import io
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

#: Writers for which the YAML head is CONTENT and must be re-attached after conversion.
#: ⚑ Everything else receives the body alone: for a non-markdown writer the head is not
#: preservation, it is corruption in a different language.
MD_WRITERS = ("markdown", "gfm", "commonmark")

#: The fence that opens a YAML frontmatter block, and the only one the splitter recognises.
FENCE = "---\n"


class PandocError(RuntimeError):
    """Pandoc could not convert the document.

    ⚑ A DISTINCT TYPE SO A CALLER CAN TELL A CONVERSION FAILURE FROM A DOCUMENT WITH NO HEADINGS.
    Collapsing the two is the defect this module is part of repairing, one layer up.
    """


def split_frontmatter(source: str) -> tuple[str, str]:
    """Return `(head, body)`, where `head` is the YAML frontmatter block including its fences.

    ⚑ ONLY A `---` FENCE SPLITS. A `+++` TOML head passes through as body, which is why the
    frontmatter defect never fired on TOML-fronted documents — worth stating because the asymmetry
    reads as a defect in the document rather than a bound on the splitter.
    """
    if not source.startswith(FENCE):
        return "", source
    end = source.find("\n---\n", len(FENCE) - 1)
    if end == -1:
        return "", source
    cut = end + len("\n---\n")
    return source[:cut], source[cut:]


def keeps_frontmatter(writer: str) -> bool:
    """Report whether `writer` should receive the document's YAML head back.

    ⚑ THE BRANCH WHOSE WRONG ANSWER IS SILENT, so it is a named predicate a case can drive rather
    than an expression at a return statement. Answering True for `json` is what prepended `---` to
    the AST input and blinded every structural mode.
    """
    return writer.startswith(MD_WRITERS)


def convert(source: str, to: str, frm: str = "markdown") -> str:
    """Return `source` converted by pandoc, re-attaching frontmatter only for markdown writers.

    ⚑ `to` MAY CARRY WRITER FLAGS after the format name, because `--columns` and `--wrap` decide
    idempotence for a table-dense document and must be reachable from the caller. Passing the whole
    string as one `-t` argument makes pandoc read `--columns=999` as an extension name and refuse.
    """
    head, body = split_frontmatter(source)
    parts = (to or "markdown").split()
    argv = ["pandoc", "-f", frm, "-t", parts[0], *parts[1:]]
    ran = subprocess.run(
        argv,
        input=body,
        capture_output=True,
        text=True,  # noqa: S603
        check=False,
    )
    if ran.returncode:
        raise PandocError(ran.stderr.strip()[:400])
    return head + ran.stdout if keeps_frontmatter(parts[0]) else ran.stdout


def headings(path: Path) -> list[tuple[int, str]]:
    """Return `(level, rendered_text)` for every heading in the document at `path`.

    ⚑⚑ THE TEXT IS PANDOC'S RENDERING, NOT THE SOURCE LINE, and that is the whole reason an
    anchorer is needed downstream. Inline markup is gone and smart punctuation is transformed, so
    what comes back here cannot be found in the file by string equality.

    ⚑ A `#` INSIDE A FENCED CODE BLOCK IS NOT A HEADING and a setext underline is one without a
    leading `#`, which is why this reads the AST rather than matching lines. That was the original
    argument for the AST path and it remains correct — the defect was never the parse.
    """
    import panflute  # noqa: PLC0415 - an optional heavy dependency, imported at the point of use

    doc = panflute.load(io.StringIO(convert(path.read_text(encoding="utf-8"), "json")))
    return [
        (el.level, panflute.stringify(el).strip())
        for el in doc.content
        if isinstance(el, panflute.Header)
    ]
