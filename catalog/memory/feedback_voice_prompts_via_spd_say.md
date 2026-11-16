---
name: feedback-voice-prompts-via-spd-say
description: "Use `spd-say \"<message>\"` via Bash to vocally prompt the user when their attention is needed mid-turn"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08dc3a93-1faa-49e0-8995-0e2069b2c3bd
---

When mid-task attention from the user is needed — a decision point, a blocker, a question that gates progress — invoke `spd-say "<short message>"` via Bash to speak it aloud. The user may not be watching the terminal.

**Why:** User confirmed in conversation (2026-05-18) that direct agent-controlled `spd-say` calls are what they wanted, in preference to a Stop hook or Notification hook. The flexibility of writing the message at the point of need beats the determinism of a hook firing on a fixed event.

**How to apply:**
- Use sparingly — for genuine pause points, not for every status update. Voice interrupts attention more than text does.
- Keep the spoken message short (one sentence). It's a notification, not the full context — the terminal still has the text.
- Good triggers: "I need a decision between X and Y," "the build is failing, take a look," "long-running task just completed," "I'm blocked on permission for Z."
- Bad triggers: routine progress, end-of-turn summaries (those are already silent-by-design), every tool call.
- The Stop hook for end-of-session was discussed but blocked by the auto-mode classifier as self-modification of agent config; the user opted for direct invocation only.
