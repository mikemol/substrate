#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Structural questions about a Claude Code SESSION TRANSCRIPT (`.jsonl`).

⚑ WHY THIS IS A NEW TOOL AND NOT A MODE.  `.jsonl` is a distinct ARTIFACT KIND —
one JSON object per line, each a message envelope whose `.message.content` is
either a bare string or an array of typed blocks (`text` / `tool_use` /
`tool_result`).  No existing reader parses it, so per the struct-tools rule this
is the "new kind" case rather than the "new mode" case.

⚑ AND THE FILE IS ~1 GB, WHICH IS THE HARD CONSTRAINT.  `json.load` on the whole
file is not an option, and neither is the reflex `grep -n "phrase" session.jsonl`:
the text lives inside JSON-escaped strings, so a line-regex matches the ENCODED
form (`\\n`, `\\"`, `\\u2014`) and reports byte offsets in a 300 MB line rather
than a message identity.  A phrase the user typed with a smart quote or an em-dash
is simply invisible to a naive grep, and — the case that motivated this file — a
grep hit gives you no way to say WHO said it or WHICH turn it was, which is the
only thing a transcript is ever asked.

So every mode here STREAMS the file line by line, decodes each envelope, and
reports (turn index, role) with the match.  That is the identity a transcript
question needs; a byte offset is not.

    transcriptstruct.py <file> --messages [--role user] [--limit N]
                                  # enumerate: index, role, size, first line
    transcriptstruct.py <file> --grep-content <regex> [--role user] [--window N]
                                  # search the DECODED text; reports role + turn
                                  # index + a context window around each hit
    transcriptstruct.py <file> --human [--messages | --grep-content <regex>]
                                  # ⚑ A MODIFIER, NOT A MODE, and the load-bearing
                                  # one: `--role user` is NOT "what the human
                                  # said".  Tool results, `<system-reminder>`
                                  # injections and subagent `<task-notification>`
                                  # reports all carry role=user.  On this corpus
                                  # 189 envelopes have role=user and 13 carry
                                  # human prose.  `--human` is the predicate on
                                  # CONTENT that separates them.
    transcriptstruct.py <file> --extract <n> [<n> ...]
                                  # one message (or several), whole and verbatim
    transcriptstruct.py <file> --context <n> [--before N] [--after N]
                                  # a message with its neighbours, for citation
    transcriptstruct.py <file> --stats
                                  # how many envelopes, by role and block kind
    transcriptstruct.py <file> --prose [--since N] [--until N] [--role R]
                                  # every ACTOR-PROSE block, whole, in turn order

⚑ WHY `--prose` IS A MODE AND NOT A `--messages | cut`.  Hand-LABELLING a
transcript (which turn retracts which) needs the actor's prose COMPLETE and in
order, with tool traffic excluded — `--messages` truncates to a first line and
`--extract` needs the turn list you do not yet have.  Labelling from truncated
first lines is how a label set gets reduced to a count; that is `tmi-F6`.  The
denominator it prints is the population you must have read to claim exhaustive.

Every mode prints `n of m` — a bare list cannot distinguish *no matches* from
*no file read*, and on a 1 GB file that distinction is the whole question.
"""
import json
import os
import re
import sys


# ⚑ THE ROLE LIVES IN TWO PLACES AND THEY DISAGREE.  The envelope has a top-level
# `type` ("user"/"assistant"/"system"/"summary") AND the nested `message.role`.
# For tool-result envelopes the top-level type is "user" while the content holds
# no user prose at all — so a mode that filters on `type` alone reports the
# harness's tool plumbing as things the user said.  `is_human` below is the
# distinction that matters for "what did the USER actually say", and it is a
# PREDICATE ON CONTENT, not on the role label.
def envelope_role(obj):
    msg = obj.get("message")
    if isinstance(msg, dict) and msg.get("role"):
        return msg["role"]
    return obj.get("type") or "?"


def blocks(obj):
    """[(kind, text)] for every content block, decoded.

    A string `content` is one implicit `text` block; an array holds typed blocks.
    `tool_result` content is itself either a string or a nested block array, which
    is why this recurses one level rather than assuming a shape.
    """
    msg = obj.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if content is None:
        content = obj.get("content")
    out = []
    if isinstance(content, str):
        out.append(("text", content))
        return out
    if not isinstance(content, list):
        return out
    for b in content:
        if not isinstance(b, dict):
            out.append(("text", str(b)))
            continue
        k = b.get("type", "?")
        if k == "text":
            out.append(("text", b.get("text", "")))
        elif k == "thinking":
            out.append(("thinking", b.get("thinking", "")))
        elif k == "tool_use":
            out.append(("tool_use", json.dumps(b.get("input", {}))[:20000]))
        elif k == "tool_result":
            c = b.get("content")
            if isinstance(c, str):
                out.append(("tool_result", c))
            elif isinstance(c, list):
                for sub in c:
                    if isinstance(sub, dict) and sub.get("type") == "text":
                        out.append(("tool_result", sub.get("text", "")))
            else:
                out.append(("tool_result", json.dumps(c)[:20000]))
        else:
            out.append((k, json.dumps(b)[:4000]))
    return out


# ⚑ "WHAT THE USER SAID" IS NOT `role == "user"`.  Three envelope classes carry
# that role and are NOT the human: a tool_result being fed back, a
# `<system-reminder>` injection, and the harness's command wrappers
# (`<command-name>`, `<local-command-stdout>`).  A search for a user's design
# statement that admits these returns mostly plumbing, and the counts then read as
# "the user said this 400 times" when the user said it once.  This is the
# distinction the whole transcript question rests on.
_HARNESS_MARKERS = (
    "<system-reminder>", "<command-name>", "<local-command-stdout>",
    "<command-message>", "<command-args>",
)


def human_text(obj):
    """The prose the HUMAN typed in this envelope, or '' if it is not human.

    Returns the concatenated `text` blocks with harness-injected wrappers stripped;
    an envelope whose text is ENTIRELY harness plumbing yields ''.
    """
    if envelope_role(obj) != "user":
        return ""
    if obj.get("isMeta") or obj.get("isCompactSummary"):
        return ""
    parts = []
    for kind, txt in blocks(obj):
        if kind != "text":
            continue            # tool_result / tool_use are never human prose
        parts.append(txt)
    joined = "\n".join(parts)
    # strip the injected blocks, then ask whether anything is left
    stripped = re.sub(r"<system-reminder>.*?</system-reminder>", "", joined,
                      flags=re.S)
    stripped = re.sub(r"<(command-name|command-message|command-args|"
                      r"local-command-stdout|local-command-stderr)>.*?"
                      r"</\1>", "", stripped, flags=re.S)
    # ⚑ A TASK-NOTIFICATION IS THE HARNESS SPEAKING, AND IT IS THE LOUDEST FALSE
    # POSITIVE.  A completed subagent's REPORT is injected as a role=user text
    # block, so a search for a user's design statement returns the agent's own
    # prose back at you — measured on a live transcript, where a `--human` search
    # for "tier"/"drain"/"torsor" returned agent reports in the first two hits.
    # Worse, an agent's report often QUOTES the user's terms, so the hit looks
    # exactly like the thing being searched for.  These wrappers may be
    # unterminated in a truncated envelope, so the close tag is optional.
    stripped = re.sub(r"<task-notification>.*?(?:</task-notification>|\Z)", "",
                      stripped, flags=re.S)
    stripped = re.sub(r"<(task-id|tool-use-id|output-file|status|summary|note|"
                      r"result)>.*?</\1>", "", stripped, flags=re.S)
    return stripped if stripped.strip() else ""


def stream(path):
    """(index, obj) for every decodable envelope — line by line, never whole.

    ⚑ A MALFORMED LINE IS COUNTED, NOT CRASHED ON.  A 1 GB append-only log can end
    mid-write, and a tool that dies on the last line reports nothing about the
    first million.  Undecodable lines are yielded as `None` so callers can report
    them as a POPULATION rather than silently shrinking the corpus.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except Exception:
                yield i, None


def stats(path):
    """(n_lines, n_bad, {role: n}, {block_kind: n}, n_human)."""
    n = bad = human = 0
    roles, kinds = {}, {}
    for _i, obj in stream(path):
        n += 1
        if obj is None:
            bad += 1
            continue
        roles[envelope_role(obj)] = roles.get(envelope_role(obj), 0) + 1
        for k, _t in blocks(obj):
            kinds[k] = kinds.get(k, 0) + 1
        if human_text(obj):
            human += 1
    return n, bad, roles, kinds, human


def messages(path, role=None, human_only=False, limit=None, since=None,
             until=None):
    """[(index, role, nbytes, firstline)] — the enumeration.

    ⚑ `since`/`until` BOUND THE TURN RANGE, and that is not a convenience.  A
    transcript's questions are almost always about an ARC — a contiguous stretch
    where one model was being worked out — and the reflex without a range filter is
    to pipe the enumeration through `tail`, which is the output-manipulation the
    standing rule forbids.  The bound belongs in the tool.
    """
    out = []
    total = 0
    for i, obj in stream(path):
        if obj is None:
            continue
        total += 1
        if since is not None and i < since:
            continue
        if until is not None and i > until:
            break
        r = envelope_role(obj)
        if role and r != role:
            continue
        txt = human_text(obj) if human_only else "\n".join(
            t for _k, t in blocks(obj))
        if human_only and not txt:
            continue
        first = next((l for l in txt.splitlines() if l.strip()), "")
        out.append((i, r, len(txt), first))
        if limit and len(out) >= limit:
            break
    return out, total


def grep_content(path, pattern, role=None, human_only=False, kinds=None,
                 window=240, limit=None, since=None, until=None):
    """[(index, role, kind, snippet)] over the DECODED text.

    ⚑ THE REGEX RUNS ON DECODED TEXT, WHICH IS THE ENTIRE POINT.  In the raw file
    a newline is the two characters `\\n` and an em-dash may be `\\u2014`, so
    `grep 'tier must drain'` can miss a phrase that straddles a line break and
    `grep 'core \\* tier'` cannot see a unicode dash at all.  Here the pattern
    matches what the human read.
    """
    rx = re.compile(pattern, re.I | re.S)
    out = []
    total = 0
    for i, obj in stream(path):
        if obj is None:
            continue
        total += 1
        if since is not None and i < since:
            continue
        if until is not None and i > until:
            break
        r = envelope_role(obj)
        if role and r != role:
            continue
        if human_only:
            txt = human_text(obj)
            if not txt:
                continue
            src = [("human", txt)]
        else:
            src = [(k, t) for k, t in blocks(obj)
                   if kinds is None or k in kinds]
        for kind, txt in src:
            for m in rx.finditer(txt):
                a = max(0, m.start() - window)
                b = min(len(txt), m.end() + window)
                out.append((i, r, kind, txt[a:b]))
                break            # one hit per block; --extract gives the whole
        if limit and len(out) >= limit:
            break
    return out, total


def prose(path, role=None, since=None, until=None):
    """[(index, role, text)] — actor PROSE only, whole, in turn order.

    Excludes `tool_use` and `tool_result` (a JSON argument name is not prose —
    the census that read `description`/`command`/`file_path` as self-quotations
    is the recorded cost of blurring that line) and excludes harness plumbing on
    the user side by routing through `human_text`.
    """
    out = []
    total = 0
    for i, obj in stream(path):
        if obj is None:
            continue
        total += 1
        if since is not None and i < since:
            continue
        if until is not None and i > until:
            break
        r = envelope_role(obj)
        if role and r != role:
            continue
        if r == "user":
            t = human_text(obj)
            if t.strip():
                out.append((i, "human", t))
            continue
        txt = "\n".join(t for k, t in blocks(obj) if k == "text")
        if txt.strip():
            out.append((i, r, txt))
    return out, total


def extract(path, indices):
    """[(index, role, [(kind, text)])] — the named messages, whole."""
    want = set(indices)
    out = []
    total = 0
    for i, obj in stream(path):
        if obj is None:
            continue
        total += 1
        if i in want:
            out.append((i, envelope_role(obj), blocks(obj)))
            if len(out) == len(want):
                break
    return out, total


def _selftest():
    """Counted from len(cases)."""
    import tempfile
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.jsonl")
    rows = [
        {"type": "user", "message": {"role": "user",
         "content": "the tier must drain as it fills — always"}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "I think the tier fills first."},
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}},
        # ⚑ A TOOL RESULT CARRIES role "user" AND IS NOT THE HUMAN.  This row is
        # the one that makes `--role user` and `--human` different queries; without
        # it a search for what the user said returns the harness's plumbing.
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "content": "the tier must drain: 3 files"}]}},
        # ⚑ AND SO IS A SYSTEM-REMINDER INJECTION, which is a `text` block.
        {"type": "user", "message": {"role": "user",
         "content": "<system-reminder>the tier must drain</system-reminder>"}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "text", "text": "It's about core * tier,\nnot core alone."}]}},
        # ⚑ A SUBAGENT'S REPORT IS INJECTED AS A role=user TEXT BLOCK, and it
        # QUOTES the user's own vocabulary — so it is the false positive that
        # looks most like the thing being searched for.  Measured on a live
        # transcript: the first two `--human` hits for "tier"/"drain" were agent
        # reports, not the user.
        {"type": "user", "message": {"role": "user", "content":
         "<task-notification><status>completed</status><result>"
         "the tier must drain as it fills, per your model</result>"
         "</task-notification>"}},
        # ...and a TRUNCATED one, with no close tag, must strip too.
        {"type": "user", "message": {"role": "user", "content":
         "<task-notification><summary>the tier must drain"}},
    ]
    with open(p, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    # a torn final line — an append-only log can end mid-write
    with open(p, "a", encoding="utf-8") as fh:
        fh.write('{"type": "user", "mess')

    n, bad, roles, kinds, human = stats(p)
    check("every envelope is counted, including the torn one", n, 8)
    check("a torn line is reported as a POPULATION, not a crash", bad, 1)
    check("roles are counted from the nested message.role",
          (roles.get("user"), roles.get("assistant")), (6, 1))
    check("block kinds are enumerated across shapes",
          sorted(kinds), ["text", "tool_result", "tool_use"])
    # ⚑ THE LOAD-BEARING COUNT: 6 envelopes carry role "user"; TWO are human.
    check("only genuinely human envelopes count as human", human, 2)

    hits, total = grep_content(p, r"tier must drain")
    check("the phrase is found across ALL block kinds", len(hits), 5)
    check("...and every hit reports which turn it was in",
          sorted(i for i, _r, _k, _s in hits), [0, 2, 3, 5, 6])
    check("the scanned population is reported, not just the matches", total, 7)

    hhits, _t = grep_content(p, r"tier must drain", human_only=True)
    check("a --human search excludes tool_result and system-reminder",
          [i for i, _r, _k, _s in hhits], [0])
    # ⚑ THE CASE THAT FAILED BEFORE THE FIX: a subagent report quoting the user's
    # own words read as the user saying them.
    check("...and a task-notification agent report is NOT the human",
          [i for i, _r, _k, _s in hhits if i in (5, 6)], [])

    # ⚑ A NEWLINE INSIDE A MESSAGE IS A REAL NEWLINE HERE, NOT `\n`.  In the raw
    # file this phrase is split by the two-character escape, so a line-regex over
    # the bytes cannot match it — this case IS the reason the tool exists.
    span, _t = grep_content(p, r"core \* tier,\s*not core")
    check("a pattern spanning a newline matches the DECODED text",
          [i for i, _r, _k, _s in span], [4])
    raw = open(p, encoding="utf-8").read()
    check("...and the same pattern does NOT match the raw bytes",
          bool(re.search(r"core \* tier,\s*not core", raw)), False)

    check("a pattern matching nothing returns nothing (not everything)",
          grep_content(p, r"zzz-absent-zzz")[0], [])

    ms, mt = messages(p)
    check("--messages enumerates every decodable envelope", len(ms), 7)
    check("...and reports the corpus size alongside", mt, 7)
    check("--role filters to one role", len(messages(p, role="assistant")[0]), 1)
    check("--human filters to real human turns",
          [i for i, _r, _n, _f in messages(p, human_only=True)[0]], [0, 4])

    # ⚑ THE RANGE BOUND, PINNED.  Without it the reflex is `| tail`, which is the
    # output-manipulation the standing rule forbids — and a transcript question is
    # almost always about a contiguous ARC.
    check("--since bounds the enumeration below",
          [i for i, _r, _n, _f in messages(p, since=4)[0]], [4, 5, 6])
    check("--until bounds it above",
          [i for i, _r, _n, _f in messages(p, until=1)[0]], [0, 1])
    check("a range with no envelopes returns nothing (not everything)",
          messages(p, since=900)[0], [])
    check("--since applies to grep too",
          [i for i, _r, _k, _s in grep_content(p, r"tier must drain",
                                               since=3)[0]], [3, 5, 6])

    # ⚑ --prose MUST EXCLUDE TOOL TRAFFIC AND HARNESS PLUMBING.  Row 1 has both a
    # text block and a tool_use; only the text may appear.  Rows 2/3/5/6 are
    # tool_result / system-reminder / task-notification and must not appear at all.
    pr, ptot = prose(p)
    check("--prose returns only prose-bearing envelopes",
          [i for i, _r, _t in pr], [0, 1, 4])
    check("--prose excludes the tool_use payload of a mixed envelope",
          [t for i, _r, t in pr if i == 1], ["I think the tier fills first."])
    check("--prose reports the whole population as denominator", ptot, 7)
    check("--prose honours the range bound",
          [i for i, _r, _t in prose(p, since=2)[0]], [4])

    ex, _t = extract(p, [4])
    check("--extract returns the named message whole",
          ex[0][2], [("text", "It's about core * tier,\nnot core alone.")])
    check("--extract of an absent index returns nothing", extract(p, [999])[0], [])

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for nm, g, got, want in cases:
        if not g:
            print(f"  FAIL {nm}\n       got {got!r} want {want!r}")
    print(f"transcriptstruct selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def _arg(flag, default=None, cast=str):
    a = sys.argv[1:]
    for i, x in enumerate(a):
        if x == flag and i + 1 < len(a):
            return cast(a[i + 1])
        if x.startswith(flag + "="):
            return cast(x.split("=", 1)[1])
    return default


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    path = next((a for a in args if a.endswith(".jsonl")), None)
    if path is None or not os.path.exists(path):
        print(__doc__)
        if path:
            print(f"\n{path} does not exist")
        sys.exit(2)

    role = _arg("--role")
    human = "--human" in sys.argv
    limit = _arg("--limit", None, int)
    since = _arg("--since", None, int)
    until = _arg("--until", None, int)

    if "--stats" in sys.argv:
        n, bad, roles, kinds, hum = stats(path)
        print(f"{path}")
        print(f"  {n} envelope(s), {bad} undecodable")
        for r, c in sorted(roles.items(), key=lambda kv: -kv[1]):
            print(f"    role {r:<12} {c:>8}")
        for k, c in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print(f"    block {k:<11} {c:>8}")
        print(f"  {hum} envelope(s) carry genuine HUMAN prose "
              f"(of {roles.get('user', 0)} with role=user)")
        sys.exit(0)

    if "--messages" in sys.argv:
        rows, total = messages(path, role=role, human_only=human, limit=limit,
                               since=since, until=until)
        for i, r, nb, first in rows:
            print(f"  [{i:>7}] {r:<10} {nb:>8}B  {first[:120]}")
        scope = f"role={role}" if role else ("human" if human else "all")
        print(f"{len(rows)} of {total} envelope(s) ({scope})")
        sys.exit(0)

    if "--grep-content" in sys.argv:
        pat = _arg("--grep-content")
        if not pat:
            print("usage: --grep-content <regex>")
            sys.exit(2)
        win = _arg("--window", 240, int)
        hits, total = grep_content(path, pat, role=role, human_only=human,
                                   window=win, limit=limit, since=since,
                                   until=until)
        for i, r, k, snip in hits:
            print(f"\n  ── [{i}] {r} / {k} " + "─" * 40)
            print("     " + snip.replace("\n", "\n     "))
        scope = f"role={role}" if role else ("human" if human else "all")
        print(f"\n{len(hits)} of {total} envelope(s) match {pat!r} ({scope})")
        sys.exit(0)

    if "--prose" in sys.argv:
        rows, total = prose(path, role=role, since=since, until=until)
        for i, r, t in rows:
            print(f"\n══ [{i}] {r} " + "═" * 50)
            print(t)
        lo = since if since is not None else 0
        hi = until if until is not None else total - 1
        print(f"\n{len(rows)} of {total} envelope(s) carry prose "
              f"(range [{lo}..{hi}])")
        sys.exit(0)

    if "--extract" in sys.argv:
        idx = [int(a) for a in args if a.isdigit()]
        if not idx:
            print("usage: --extract <n> [<n> ...]")
            sys.exit(2)
        rows, total = extract(path, idx)
        for i, r, bs in rows:
            print(f"\n══ [{i}] {r} " + "═" * 50)
            for k, t in bs:
                print(f"  ── {k} ──")
                print(t)
        print(f"\n{len(rows)} of {total} envelope(s) extracted")
        sys.exit(0)

    if "--context" in sys.argv:
        n = _arg("--context", None, int)
        before = _arg("--before", 2, int)
        after = _arg("--after", 2, int)
        if n is None:
            print("usage: --context <n> [--before N] [--after N]")
            sys.exit(2)
        idx = list(range(max(0, n - before), n + after + 1))
        rows, total = extract(path, idx)
        for i, r, bs in rows:
            mark = "»»" if i == n else "  "
            print(f"\n{mark} [{i}] {r} " + "─" * 50)
            for k, t in bs:
                print(f"  ── {k} ── {t[:4000]}")
        print(f"\n{len(rows)} of {total} envelope(s) in window "
              f"[{idx[0]}..{idx[-1]}]")
        sys.exit(0)

    print(__doc__)
    sys.exit(2)
