---
name: feedback-substrate-memory-file-format
description: "Substrate memory files start with YAML frontmatter (name/description/metadata), NOT with a Markdown H1 heading. The MD041 lint warning (\"First line should be a top-level heading\") is intentional and should be ignored — all memory files follow this convention."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

When IDE diagnostics flag MD041/first-line-heading on a memory file:

**Don't fix it.** Just acknowledge and move on.

**Why:** The substrate's memory files follow a strict convention:
* First line: `---` (YAML frontmatter start).
* YAML frontmatter contains `name`, `description`, `metadata.type`.
* `---` (frontmatter end).
* Then the body.

This format is read by the auto-memory system. A leading H1 would
break the YAML parse. The lint warning is incompatible with this
convention.

**How to apply:** When MD041 fires on a memory file, ignore. When
OTHER lint warnings fire (MD032 lists, etc.), those are real and
should be fixed.

This applies to all files under
`/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/`.
