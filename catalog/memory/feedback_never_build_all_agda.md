---
name: feedback_never_build_all_agda
description: "NEVER typecheck Substrate.All — it OOMs the user's machine (dozens of GiB, exceeds RAM+swap); check modules standalone instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Do NOT run `agda` on `Substrate/All.agda` (the master build target). It
aggregates every top-level subtree and consumes **dozens of GiB of RAM —
more than the user's RAM + (large) swap combined**, paging the system hard
and OOMing. The user had to interrupt twice to make it stop.

**Why:** All.agda exists as an "if-this-builds-everything-builds" check,
but it is too heavy to run on the user's hardware. It is a CI/aspirational
target, not a local command.

**How to apply:**
- Typecheck modules **standalone**: `agda --safe --without-K
  Substrate/<Path>.agda` only pulls that module's own dependency cone
  (cheap). That is the correct verification for any single module.
- Do NOT add new modules to All.agda and then build it to "confirm wiring."
  Adding the import line is fine if requested; building All.agda is not.
- New arc modules (e.g. [[project_realizability_charter_arc]]) are
  intentionally kept OUT of All.agda; "wire into All.agda" is NOT an
  implied step of "land the module."
- If whole-graph verification is ever genuinely needed, ask first and let
  the user run it where the RAM exists — never kick it off locally,
  especially not in the background where it keeps growing unattended.
