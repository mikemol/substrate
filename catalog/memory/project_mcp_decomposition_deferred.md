---
name: project-mcp-decomposition-deferred
description: An MCP interface over the decomposition SQLite is designed but intentionally not built; resume from decomposition/mcp_decomposition_interface_design.md when querying becomes valuable.
metadata: 
  node_type: memory
  type: project
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

`decomposition/mcp_decomposition_interface_design.md` specifies an 8-tool MCP surface (A–H: list_sources, get_sections, query_triples, get_move_timeline, get_axis_transitions, get_move_themes, interpret_window, export_report) over the decomposition SQLite, with SQL templates and an evidence-anchored response envelope. Implementation is deferred.

**Why:** The decomposition artifacts already contain reusable structure worth preserving; the user chose to lock the contract in design form before context drift, rather than build prematurely.

**How to apply:**
- Do not propose implementing the MCP server unprompted. The design explicitly defers it.
- Resume trigger per the design doc: when interactive querying, tool integration, or external-agent access to decomposition results becomes valuable.
- On resume: build order is Tool A + C first, then D + E, then G; Tool H stays metadata-only until regeneration policy is settled. The doc also recommends a CLI mirror before MCP transport hardening.
- Related: [[project-retrospective-as-navigation-aid]] for what the database actually contains.
