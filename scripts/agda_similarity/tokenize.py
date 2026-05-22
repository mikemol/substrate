"""Agda-aware tokenizers at four scales: char3, token, line, block.

All scales operate on COMMENT-STRIPPED text so similarity isn't
dominated by commentary boilerplate. The Counter-returning forms
feed the cosine similarity pipeline; `units_at_scale` returns a flat
list, used by the template-extraction pipeline (which counts
file-membership, not within-file frequency).
"""

from __future__ import annotations

import re
from collections import Counter

# Agda-aware token split: identifiers (letters/digits/unicode chars),
# operators, punctuation. We treat each as a token unit.
TOKEN_RE = re.compile(
    r"[A-Za-z_][\w'-]*"          # identifier
    r"|[ℕ-℧⁰-⁹₀-₉ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψω]+"  # unicode names
    r"|->|→|⇒|=>|≡|≈|≠|≢|≤|≥|<|>|::|\.\.|"
    r"|[(){}\[\]:;,.=|]"
)

# Block separator: blank line, OR a comment rule (---- or more), OR
# a section heading line that's all dashes.
BLOCK_SEP_RE = re.compile(r"^\s*(?:--+\s*)?$|^-+\s*$")


def strip_comment_lines(text: str) -> str:
    """Drop full-line Agda comments (-- and {- ... -}) so similarity
    isn't dominated by commentary boilerplate. Keeps code structure."""
    out_lines = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if in_block:
            if "-}" in stripped:
                in_block = False
            continue
        if stripped.startswith("{-"):
            if "-}" not in stripped:
                in_block = True
            continue
        if stripped.startswith("--"):
            continue
        # Drop inline -- comments
        if " --" in line:
            line = line[: line.index(" --")]
        out_lines.append(line)
    return "\n".join(out_lines)


# ---------------------------------------------------------------------------
# Counter-returning views (feed cosine similarity).
# ---------------------------------------------------------------------------


def char_ngrams(text: str, n: int = 3) -> Counter[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return Counter(text[i : i + n] for i in range(len(text) - n + 1))


def tokens(text: str) -> Counter[str]:
    return Counter(TOKEN_RE.findall(text))


def lines(text: str) -> Counter[str]:
    return Counter(
        s for line in text.splitlines() if (s := line.strip())
    )


def blocks(text: str) -> Counter[str]:
    """Split on blank lines / ---- rules; normalize within each block."""
    out: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        if BLOCK_SEP_RE.match(line):
            if cur:
                out.append(" ".join(cur).strip())
                cur = []
        else:
            stripped = line.strip()
            if stripped:
                cur.append(stripped)
    if cur:
        out.append(" ".join(cur).strip())
    # Canonicalize each block: collapse whitespace, sort tokens.
    canonical = [
        " ".join(sorted(TOKEN_RE.findall(b))) for b in out if b
    ]
    return Counter(canonical)


# ---------------------------------------------------------------------------
# List-returning view (feeds template extraction; counts file-membership
# rather than within-file frequency).
# ---------------------------------------------------------------------------


def units_at_scale(text: str, scale: str) -> list[str]:
    """Extract a flat list of units at the given scale. Same
    tokenization/normalization as the Counter forms above."""
    body = strip_comment_lines(text)
    if scale == "char3":
        clean = re.sub(r"\s+", " ", body).strip()
        return [clean[i : i + 3] for i in range(len(clean) - 2)]
    if scale == "token":
        return TOKEN_RE.findall(body)
    if scale == "line":
        return [s for line in body.splitlines() if (s := line.strip())]
    if scale == "block":
        out: list[str] = []
        cur: list[str] = []
        for line in body.splitlines():
            if BLOCK_SEP_RE.match(line):
                if cur:
                    out.append(" ".join(cur).strip())
                    cur = []
            else:
                stripped = line.strip()
                if stripped:
                    cur.append(stripped)
        if cur:
            out.append(" ".join(cur).strip())
        return [" ".join(sorted(TOKEN_RE.findall(b))) for b in out if b]
    raise ValueError(f"unknown scale: {scale!r}")
